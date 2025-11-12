"""
知识卡片窗口模块（重构版）
提供知识卡片的查看、导航、追问和保存功能
"""
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
from PyQt6.QtCore import Qt
from aqt import mw
from aqt.utils import showInfo, showWarning

from ..lang.messages import get_message, get_default_lang
from ..utils.note_types import (
    create_knowledge_card_type,
    create_knowledge_cloze_type
)
from .components.knowledge_card_navigation import KnowledgeCardNavigation
from .components.knowledge_card_viewer import KnowledgeCardViewer
from .components.knowledge_followup_panel import KnowledgeFollowUpPanel
from .dialogs.knowledge_cloze_dialog import KnowledgeClozeDialog
from .styles.knowledge_window_style import apply_knowledge_window_style

class KnowledgeCardWindow(QDialog):
    """知识卡片窗口（重构版）"""

    def __init__(self, cards, parent=None):
        """
        初始化知识卡片窗口

        Args:
            cards: 卡片数据字典，包含 'cards' 列表
            parent: 父窗口
        """
        super().__init__(parent)
        self.cards = cards
        self.current_index = 0
        self.lang = get_default_lang()
        self.parent_dialog = parent
        self.followup_model = None
        self.ai_handler = None

        self._setup_ui()
        self._setup_connections()
        self._show_current_card()

    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("knowledge_window_title", self.lang))
        self.resize(800, 800)

        layout = QVBoxLayout(self)

        # 创建导航组件
        self.navigation = KnowledgeCardNavigation(self)
        layout.addWidget(self.navigation)

        # 创建卡片查看组件
        self.card_viewer = KnowledgeCardViewer(self)
        layout.addWidget(self.card_viewer)

        # 创建追问面板组件
        self.followup_panel = KnowledgeFollowUpPanel(self)
        layout.addWidget(self.followup_panel)

        # 功能按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_button = QPushButton(get_message("add_to_anki_btn", self.lang))
        self.cloze_button = QPushButton(get_message("make_cloze_btn", self.lang))

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cloze_button)

        layout.addLayout(button_layout)

        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)

        # 应用样式
        apply_knowledge_window_style(self)

    def _setup_connections(self):
        """设置信号连接"""
        # 导航信号
        self.navigation.prev_clicked.connect(self._show_prev_card)
        self.navigation.next_clicked.connect(self._show_next_card)
        self.navigation.preview_clicked.connect(self._preview_card)

        # 功能按钮信号
        self.add_button.clicked.connect(self._add_to_anki)
        self.cloze_button.clicked.connect(self._convert_to_cloze)

        # 追问面板信号
        self.followup_panel.create_qa_card.connect(self._make_qa_card_from_history)
        self.followup_panel.create_cloze_card.connect(self._make_cloze_card_from_history)
        self.followup_panel.history_updated.connect(self._on_history_updated)

    def _show_current_card(self):
        """显示当前卡片"""
        if not self.cards or not self.cards.get('cards'):
            return

        current_card = self.cards['cards'][self.current_index]
        total_cards = len(self.cards['cards'])

        # 更新导航组件
        self.navigation.update_navigation(self.current_index, total_cards)

        # 更新卡片查看组件
        self.card_viewer.display_card(current_card)

    def _show_prev_card(self):
        """显示上一张卡片"""
        if self.current_index > 0:
            self.current_index -= 1
            self._show_current_card()

    def _show_next_card(self):
        """显示下一张卡片"""
        if self.current_index < len(self.cards['cards']) - 1:
            self.current_index += 1
            self._show_current_card()

    def _preview_card(self):
        """预览当前卡片"""
        if not self.cards or not self.cards.get('cards'):
            return

        current_card = self.cards['cards'][self.current_index]
        preview_text = (
            f"{get_message('question_field', self.lang)}:\n"
            f"{current_card.get('question', '')}\n\n"
            f"{get_message('answer_field', self.lang)}:\n"
            f"{current_card.get('answer', '')}\n\n"
            f"{get_message('context_field', self.lang)}:\n"
            f"{current_card.get('context', '')}"
        )

        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle(get_message("preview_card", self.lang))
        preview_dialog.resize(600, 400)

        layout = QVBoxLayout(preview_dialog)
        preview_text_edit = QTextEdit()
        preview_text_edit.setReadOnly(True)
        preview_text_edit.setText(preview_text)
        layout.addWidget(preview_text_edit)

        preview_dialog.exec()

    def _add_to_anki(self):
        """添加当前卡片到Anki"""
        if not self.cards or not self.cards.get('cards'):
            return

        try:
            current_card = self.cards['cards'][self.current_index]

            # 获取选中的牌组名称
            deck_name = self.parent_dialog.deckComboBox.currentText()

            # 确保牌组存在
            did = mw.col.decks.id_for_name(deck_name)
            if not did:
                did = mw.col.decks.add_normal_deck_with_name(deck_name)

            # 获取或创建知识卡笔记类型
            knowledge_model = create_knowledge_card_type()

            # 创建新笔记
            note = mw.col.new_note(knowledge_model)
            note['问题'] = current_card.get('question', '')
            note['答案'] = current_card.get('answer', '')
            note['上下文'] = current_card.get('context', '')

            # 如果有追问历史，添加到AI解析字段
            ai_analysis = self.followup_panel.format_history_for_card() if self.followup_panel.get_history() else ''
            note['AI解析'] = ai_analysis

            # 添加标签
            note.tags = ['knowledge_card']

            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()

            showInfo(get_message("knowledge_card_added", self.lang))

        except Exception as e:
            showWarning(f"{get_message('knowledge_card_add_error', self.lang)}{str(e)}")

    def _convert_to_cloze(self):
        """将当前卡片转换为填空题"""
        if not self.cards or not self.cards.get('cards'):
            return

        current_card = self.cards['cards'][self.current_index]

        # 组合卡片内容
        card_text = (
            f"{current_card.get('answer', '')}\n\n"
            f"{current_card.get('context', '')}"
        )

        # 创建填空对话框
        dialog = KnowledgeClozeDialog(card_text, self)

        # 连接保存请求信号
        dialog.saveRequested.connect(lambda: self._handle_convert_to_cloze_save(dialog, current_card))

        # 显示对话框（非阻塞模式）
        dialog.show()

    def _handle_convert_to_cloze_save(self, dialog, current_card):
        """
        处理转换为填空卡的保存请求

        Args:
            dialog: KnowledgeClozeDialog实例
            current_card: 当前卡片数据
        """
        try:
            # 获取填空内容
            cloze_text = dialog.get_cloze_text()

            # 直接使用父窗口选择的牌组
            deck_name = self.parent_dialog.deckComboBox.currentText()

            # 确保牌组存在
            did = mw.col.decks.id_for_name(deck_name)
            if not did:
                did = mw.col.decks.add_normal_deck_with_name(deck_name)

            # 获取或创建知识卡填空类型
            cloze_model = create_knowledge_cloze_type()

            # 创建填空卡片
            note = mw.col.new_note(cloze_model)
            note['问题'] = current_card.get('question', '')
            note['填空内容'] = cloze_text
            note['答案'] = current_card.get('answer', '')
            note['上下文'] = current_card.get('context', '')

            # 如果有追问历史，添加到AI解析字段
            ai_analysis = self.followup_panel.format_history_for_card() if self.followup_panel.get_history() else ''
            note['AI解析'] = ai_analysis

            # 添加标签
            note.tags = ['knowledge_card', 'cloze']

            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()

            showInfo(get_message("cloze_create_success", self.lang))

        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")
    def _on_history_updated(self, history):
        """
        处理追问历史更新

        Args:
            history: 更新后的历史记录列表
        """
        # 更新当前卡片的AI解析字段
        if self.cards and self.cards.get('cards'):
            current_card = self.cards['cards'][self.current_index]
            current_card['AI解析'] = self.followup_panel.format_history_for_card()

    def _make_qa_card_from_history(self, selected_text):
        """从历史记录创建问答卡片"""
        if not selected_text:
            return

        try:
            # 获取当前卡片作为上下文
            current_card = self.cards['cards'][self.current_index]

            # 创建新的笔记
            deck_name = self.parent_dialog.deckComboBox.currentText()
            did = mw.col.decks.id_for_name(deck_name)
            if not did:
                did = mw.col.decks.add_normal_deck_with_name(deck_name)

            # 获取或创建知识卡笔记类型
            knowledge_model = create_knowledge_card_type()

            # 创建新笔记
            note = mw.col.new_note(knowledge_model)
            note['问题'] = selected_text
            note['答案'] = ''  # 用户需要自己填写答案
            note['上下文'] = current_card.get('context', '')
            note['AI解析'] = f"从卡片追问记录创建。原始卡片问题：{current_card.get('question', '')}"

            # 添加标签
            note.tags = ['knowledge_card', 'from_followup']

            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()

            showInfo(get_message("card_created", self.lang))

        except Exception as e:
            showWarning(f"{get_message('qa_create_error', self.lang)}{str(e)}")

    def _make_cloze_card_from_history(self, selected_text):
        """从历史记录创建填空卡片"""
        if not selected_text:
            return

        # 打开填空编辑对话框
        dialog = KnowledgeClozeDialog(selected_text, self)

        # 获取当前卡片作为上下文
        current_card = self.cards['cards'][self.current_index]

        # 连接保存请求信号
        dialog.saveRequested.connect(lambda: self._handle_history_cloze_save(dialog, current_card))

        # 显示对话框（非阻塞模式）
        dialog.show()

    def _handle_history_cloze_save(self, dialog, current_card):
        """
        处理从历史记录创建填空卡的保存请求

        Args:
            dialog: KnowledgeClozeDialog实例
            current_card: 当前卡片数据
        """
        try:
            cloze_text = dialog.get_cloze_text()

            # 直接使用父窗口选择的牌组
            deck_name = self.parent_dialog.deckComboBox.currentText()
            did = mw.col.decks.id_for_name(deck_name)
            if not did:
                did = mw.col.decks.add_normal_deck_with_name(deck_name)

            # 获取或创建填空卡笔记类型
            cloze_model = create_knowledge_cloze_type()

            # 创建新笔记
            note = mw.col.new_note(cloze_model)
            note['问题'] = current_card.get('question', '')
            note['填空内容'] = cloze_text
            note['答案'] = current_card.get('answer', '')
            note['上下文'] = current_card.get('context', '')
            note['AI解析'] = f"从卡片追问记录创建。原始卡片问题：{current_card.get('question', '')}"

            # 添加标签
            note.tags = ['knowledge_card', 'cloze', 'from_followup']

            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()

            showInfo(get_message("card_created", self.lang))

        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")

    def _setup_followup_handler(self):
        """设置追问处理器（由父窗口调用）"""
        # 确保有AI处理器
        if not self.ai_handler and hasattr(self.parent_dialog, 'ai_handler'):
            self.ai_handler = self.parent_dialog.ai_handler
        elif not self.ai_handler:
            from ..utils.ai_handler import AIHandler
            self.ai_handler = AIHandler()

        # 设置追问面板的AI处理器
        self.followup_panel.set_ai_handler(self.ai_handler)

        # 定义发送请求的方法
        def send_with_context(question):
            # 获取当前卡片
            if not self.cards or not self.cards.get('cards'):
                return

            current_card = self.cards['cards'][self.current_index]

            # 构建上下文
            context = {
                "original_question": current_card.get('question', ''),
                "source_content": current_card.get('context', ''),
                "user_answer": "",  # 知识卡片没有用户答案
                "ai_feedback": current_card.get('AI解析', ''),
                "follow_up_question": question,
                "history": self.followup_panel.get_history()
            }

            # 使用上下文发送请求
            self.followup_panel.send_followup_with_context(context)

        # 动态添加方法到追问面板实例
        self.followup_panel._send_followup_request = send_with_context

    def update_cards(self, cards):
        """更新卡片内容并重置当前状态"""
        self.cards = cards
        self.current_index = 0

        # 清空追问历史
        self.followup_panel.clear_history()

        # 显示新的卡片
        self._show_current_card()

    # 保留旧的apply_anki_style方法以防其他地方调用（已废弃）
    def apply_anki_style(self):
        """应用Anki样式（已废弃，使用样式模块）"""
        apply_knowledge_window_style(self)