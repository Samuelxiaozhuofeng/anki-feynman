from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning
from ..lang.messages import get_message, get_default_lang
from ..utils.note_types import (
    KNOWLEDGE_CARD_TYPE, 
    KNOWLEDGE_CLOZE_TYPE,
    create_knowledge_card_type,
    create_knowledge_cloze_type
)
from PyQt6.QtCore import Qt

class ClozeDialog(QDialog):
    # 自定义信号
    saveRequested = pyqtSignal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.lang = get_default_lang()
        self.cloze_count = 1
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(get_message("cloze_dialog_title", self.lang))
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 说明文本
        instructions = QLabel(get_message("cloze_instructions", self.lang))
        layout.addWidget(instructions)
        
        # 编辑区域
        self.edit_area = QTextEdit()
        self.edit_area.setText(self.text)
        layout.addWidget(self.edit_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_cloze_btn = QPushButton(get_message("add_cloze_marker", self.lang))
        self.save_btn = QPushButton(get_message("save_cloze", self.lang))
        
        button_layout.addWidget(self.add_cloze_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.add_cloze_btn.clicked.connect(self.add_cloze)
        self.save_btn.clicked.connect(self.on_save_clicked)
        
    def add_cloze(self):
        cursor = self.edit_area.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            showWarning(get_message("select_cloze_text", self.lang))
            return
            
        # 添加填空标记，使用双大括号来转义
        cloze_text = f"{{{{c{self.cloze_count}::{selected_text}}}}}"
        cursor.insertText(cloze_text)
        self.cloze_count += 1

    def on_save_clicked(self):
        """处理保存按钮点击事件"""
        # 发出保存请求信号，不关闭对话框
        self.saveRequested.emit()

class KnowledgeCardWindow(QDialog):
    """知识卡片窗口"""
    def __init__(self, cards, parent=None):
        super().__init__(parent)
        self.cards = cards
        self.current_index = 0
        self.lang = get_default_lang()
        self.parent_dialog = parent
        self.follow_up_history = []
        self.followup_model = None  # 添加追加提问模型字段
        self.ai_handler = None  # AI处理器实例
        self.setup_ui()
        self.show_current_card()

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("knowledge_window_title", self.lang))
        self.resize(800, 800)  # 增加窗口高度以容纳追问区域
        
        layout = QVBoxLayout(self)
        
        # 卡片导航区域
        nav_layout = QHBoxLayout()
        
        # 卡片计数标签
        self.card_count_label = QLabel()
        nav_layout.addWidget(self.card_count_label)
        
        nav_layout.addStretch()
        
        # 导航按钮
        self.prev_button = QPushButton(get_message("prev_card", self.lang))
        self.next_button = QPushButton(get_message("next_card", self.lang))
        self.preview_button = QPushButton(get_message("preview_card", self.lang))
        
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.preview_button)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)
        
        # 卡片内容区域
        card_layout = QVBoxLayout()
        
        # 问题区域
        question_group = QGroupBox(get_message("question_field", self.lang))
        question_layout = QVBoxLayout()
        self.question_text = QTextEdit()
        self.question_text.setReadOnly(True)
        question_layout.addWidget(self.question_text)
        question_group.setLayout(question_layout)
        card_layout.addWidget(question_group)
        
        # 答案区域
        answer_group = QGroupBox(get_message("answer_field", self.lang))
        answer_layout = QVBoxLayout()
        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        answer_layout.addWidget(self.answer_text)
        answer_group.setLayout(answer_layout)
        card_layout.addWidget(answer_group)
        
        # 上下文区域
        context_group = QGroupBox(get_message("context_field", self.lang))
        context_layout = QVBoxLayout()
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        context_layout.addWidget(self.context_text)
        context_group.setLayout(context_layout)
        card_layout.addWidget(context_group)
        
        layout.addLayout(card_layout)
        
        # 添加追问区域
        followup_group = QGroupBox(get_message("followup_area", self.lang))
        followup_layout = QVBoxLayout()
        
        # 追问历史显示区域
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(100)
        followup_layout.addWidget(self.history_text)
        
        # 追问输入区域
        input_layout = QHBoxLayout()
        self.followup_input = QLineEdit()
        self.followup_input.setPlaceholderText(get_message("followup_placeholder", self.lang))
        self.send_button = QPushButton(get_message("send_followup", self.lang))
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        input_layout.addWidget(self.followup_input)
        input_layout.addWidget(self.send_button)
        followup_layout.addLayout(input_layout)
        followup_layout.addWidget(self.progress_bar)
        
        followup_group.setLayout(followup_layout)
        layout.addWidget(followup_group)
        
        # 功能按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.add_button = QPushButton(get_message("add_to_anki_btn", self.lang))
        self.cloze_button = QPushButton(get_message("make_cloze_btn", self.lang))
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cloze_button)
        
        layout.addLayout(button_layout)
        
        # 设置按钮连接
        self.prev_button.clicked.connect(self.show_prev_card)
        self.next_button.clicked.connect(self.show_next_card)
        self.preview_button.clicked.connect(self.preview_card)
        self.add_button.clicked.connect(self.add_to_anki)
        self.cloze_button.clicked.connect(self.convert_to_cloze)
        self.send_button.clicked.connect(self.handle_followup_question)
        self.followup_input.returnPressed.connect(self.handle_followup_question)
        
        # 设置历史区域的右键菜单
        self.history_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_text.customContextMenuRequested.connect(self.show_history_context_menu)
        
        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.apply_anki_style()

    def show_current_card(self):
        """显示当前卡片"""
        if not self.cards or not self.cards.get('cards'):
            return
            
        current_card = self.cards['cards'][self.current_index]
        total_cards = len(self.cards['cards'])
        
        # 更新卡片计数
        self.card_count_label.setText(
            get_message("card_number", self.lang).format(
                current=self.current_index + 1,
                total=total_cards
            )
        )
        
        # 更新卡片内容
        self.question_text.setText(current_card.get('question', ''))
        self.answer_text.setText(current_card.get('answer', ''))
        self.context_text.setText(current_card.get('context', ''))
        
        # 更新导航按钮状态
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < total_cards - 1)

    def show_prev_card(self):
        """显示上一张卡片"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_card()

    def show_next_card(self):
        """显示下一张卡片"""
        if self.current_index < len(self.cards['cards']) - 1:
            self.current_index += 1
            self.show_current_card()

    def preview_card(self):
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

    def add_to_anki(self):
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
            note['AI解析'] = ''  # 预留AI解析字段，后续可以添加
            
            # 添加标签
            note.tags = ['knowledge_card']
            
            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()
            
            showInfo(get_message("knowledge_card_added", self.lang))
            
        except Exception as e:
            showWarning(f"{get_message('knowledge_card_add_error', self.lang)}{str(e)}")

    def convert_to_cloze(self):
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
        dialog = ClozeDialog(card_text, self)

        # 连接保存请求信号
        dialog.saveRequested.connect(lambda: self._handle_convert_to_cloze_save(dialog, current_card))

        # 显示对话框（非阻塞模式）
        dialog.show()

    def _handle_convert_to_cloze_save(self, dialog, current_card):
        """
        处理转换为填空卡的保存请求

        Args:
            dialog: ClozeDialog实例
            current_card: 当前卡片数据
        """
        try:
            # 获取填空内容
            cloze_text = dialog.edit_area.toPlainText()

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
            note['AI解析'] = ''  # 预留AI解析字段

            # 添加标签
            note.tags = ['knowledge_card', 'cloze']

            # 添加到Anki
            mw.col.add_note(note, did)
            mw.col.save()

            showInfo(get_message("cloze_create_success", self.lang))

        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")

    def apply_anki_style(self):
        """应用Anki样式"""
        # 检测Anki是否处于夜间模式
        night_mode = False
        try:
            from aqt.theme import theme_manager
            night_mode = theme_manager.night_mode
        except:
            try:
                night_mode = mw.pm.meta.get("night_mode", False)
            except:
                pass
        
        # 根据夜间模式设置不同的样式
        if night_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 0.5em;
                }
                QGroupBox::title {
                    color: #64b5f6;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QTextEdit {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #383838;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #555555;
                }
                QLabel {
                    color: #e0e0e0;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 0.5em;
                }
                QGroupBox::title {
                    color: #2196F3;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QTextEdit {
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                }
            """)

    def show_history_context_menu(self, pos):
        """显示历史记录的右键菜单"""
        menu = QMenu(self)
        make_qa_action = menu.addAction(get_message("make_qa_card", self.lang))
        make_cloze_action = menu.addAction(get_message("make_cloze_card", self.lang))
        
        # 获取选中的文本
        cursor = self.history_text.textCursor()
        selected_text = cursor.selectedText()
        
        # 只有在有选中文本时才启用菜单项
        make_qa_action.setEnabled(bool(selected_text))
        make_cloze_action.setEnabled(bool(selected_text))
        
        # 连接动作信号
        make_qa_action.triggered.connect(lambda: self.make_qa_card_from_history(selected_text))
        make_cloze_action.triggered.connect(lambda: self.make_cloze_card_from_history(selected_text))
        
        # 显示菜单
        menu.exec(self.history_text.mapToGlobal(pos))

    def handle_followup_question(self):
        """处理追问"""
        question = self.followup_input.text().strip()
        if not question:
            return
            
        # 确保有AI处理器
        if not self.ai_handler and hasattr(self.parent(), 'ai_handler'):
            self.ai_handler = self.parent().ai_handler
        elif not self.ai_handler:
            from ..utils.ai_handler import AIHandler
            self.ai_handler = AIHandler()
            
        # 禁用输入和按钮
        self.followup_input.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式
        
        # 获取当前卡片
        current_card = self.cards['cards'][self.current_index]
        
        # 构建上下文
        context = {
            "original_question": current_card.get('question', ''),
            "source_content": current_card.get('context', ''),
            "user_answer": "", # 知识卡片没有用户答案
            "ai_feedback": current_card.get('AI解析', ''),
            "follow_up_question": question,
            "history": self.follow_up_history
        }
        
        # 创建工作线程
        self.thread = QThread()
        self.worker = FollowUpQuestionWorker(
            self.ai_handler,
            context,
            self.followup_model  # 传递追加提问模型
        )
        
        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.response_ready.connect(self.handle_ai_response)
        self.worker.error_occurred.connect(self.handle_ai_error)
        
        # 保存当前问题
        self.current_followup_question = question
        
        # 启动线程
        self.thread.start()

    def handle_ai_response(self, response):
        """处理AI响应"""
        # 添加到历史记录
        self.follow_up_history.append({
            "question": self.current_followup_question,
            "answer": response
        })
        
        # 更新显示
        self.update_history_display()
        
        # 清空输入框并恢复界面
        self.followup_input.clear()
        self.followup_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 更新卡片的AI解析字段
        current_card = self.cards['cards'][self.current_index]
        current_card['AI解析'] = self._format_history_for_card()
        
    def handle_ai_error(self, error_msg):
        """处理AI错误"""
        from aqt.utils import showWarning
        showWarning(error_msg)
        
        # 恢复界面
        self.followup_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def update_history_display(self):
        """更新历史记录显示"""
        history_text = ""
        for item in self.follow_up_history:
            history_text += f"Q: {item['question']}\n"
            history_text += f"A: {item['answer']}\n\n"
        self.history_text.setText(history_text)
        
    def _format_history_for_card(self):
        """格式化历史记录用于保存到卡片"""
        formatted = "AI解析与追问记录：\n\n"
        for item in self.follow_up_history:
            formatted += f"问：{item['question']}\n"
            formatted += f"答：{item['answer']}\n\n"
        return formatted
        
    def make_qa_card_from_history(self, selected_text):
        """从历史记录创建问答卡片"""
        if not selected_text:
            return
            
        # 获取当前卡片作为上下文
        current_card = self.cards['cards'][self.current_index]
        
        # 创建新的笔记
        deck_name = self.parent_dialog.deckComboBox.currentText()
        did = mw.col.decks.id_for_name(deck_name)
        if not did:
            did = mw.col.decks.add_normal_deck_with_name(deck_name)
            
        # 获取或创建知识卡笔记类型
        from ..utils.note_types import create_knowledge_card_type
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
        
        from aqt.utils import showInfo
        showInfo(get_message("card_created", self.lang))
        
    def make_cloze_card_from_history(self, selected_text):
        """从历史记录创建填空卡片"""
        if not selected_text:
            return
            
        # 打开填空编辑对话框
        dialog = ClozeDialog(selected_text, self)

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
            dialog: ClozeDialog实例
            current_card: 当前卡片数据
        """
        try:
            cloze_text = dialog.edit_area.toPlainText()

            # 直接使用父窗口选择的牌组
            deck_name = self.parent_dialog.deckComboBox.currentText()
            did = mw.col.decks.id_for_name(deck_name)
            if not did:
                did = mw.col.decks.add_normal_deck_with_name(deck_name)

            # 获取或创建填空卡笔记类型
            from ..utils.note_types import create_knowledge_cloze_type
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

            from aqt.utils import showInfo
            showInfo(get_message("card_created", self.lang))

        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")

    def update_cards(self, cards):
        """更新卡片内容并重置当前状态"""
        self.cards = cards
        self.current_index = 0
        self.follow_up_history = []  # 重置追问历史
        
        # 清空历史区域
        if hasattr(self, 'history_text'):
            self.history_text.clear()
            
        # 显示新的卡片
        self.show_current_card()

class FollowUpQuestionWorker(QObject):
    """处理追问请求的工作线程"""
    finished = pyqtSignal()
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_handler, context, followup_model=None):
        super().__init__()
        self.ai_handler = ai_handler
        self.context = context
        self.followup_model = followup_model
        
    def run(self):
        """运行AI请求"""
        try:
            # 如果指定了追加提问模型，临时设置AI处理器使用该模型
            original_model = None
            if self.followup_model:
                # 先保存当前模型
                original_model = self.ai_handler.current_model_info
                # 设置为追加提问模型
                self.ai_handler.set_model(self.followup_model)
                
            try:
                # 调用AI处理器
                response = self.ai_handler.handle_follow_up_question(self.context)
                if not response:
                    raise ValueError("AI返回的响应为空")
                    
                self.response_ready.emit(response)
            finally:
                # 如果之前切换了模型，恢复原始模型设置
                if self.followup_model and original_model:
                    self.ai_handler.current_model_info = original_model
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit() 