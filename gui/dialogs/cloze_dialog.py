"""
填空卡制作对话框模块
提供创建填空卡的界面和功能
"""
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning, tooltip

from ..styles.anki_style import apply_anki_style
from ...utils import create_feynman_cloze_type
from ...lang.messages import get_message, get_default_lang


class ClozeDialog(QDialog):
    """填空卡制作对话框"""

    # 为了兼容性添加静态属性
    Accepted = QDialog.DialogCode.Accepted
    Rejected = QDialog.DialogCode.Rejected

    # 自定义信号
    saveRequested = pyqtSignal()
    
    def __init__(self, parent=None, content="", question="", answer="", feedback=""):
        """
        初始化填空卡对话框
        
        Args:
            parent: 父窗口
            content (str): 原始内容
            question (str): 问题内容
            answer (str): 答案内容
            feedback (str): 反馈内容
        """
        super().__init__(parent)
        self.content = content
        self.question = question
        self.answer = answer
        self.feedback = feedback
        self.lang = get_default_lang()
        
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("make_cloze_title", self.lang))
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 原始内容（只读）
        originalGroup = QGroupBox(get_message("original_content", self.lang))
        originalLayout = QVBoxLayout()
        self.originalEdit = QPlainTextEdit()
        self.originalEdit.setPlainText(self.content)
        self.originalEdit.setReadOnly(True)
        originalLayout.addWidget(self.originalEdit)
        originalGroup.setLayout(originalLayout)
        layout.addWidget(originalGroup)
        
        # 填空内容编辑
        clozeGroup = QGroupBox(get_message("cloze_content", self.lang))
        clozeLayout = QVBoxLayout()
        self.clozeEdit = QPlainTextEdit()
        self.clozeEdit.setPlainText(self.question)
        clozeLayout.addWidget(self.clozeEdit)
        
        # 添加填空按钮
        buttonLayout = QHBoxLayout()
        self.addClozeButton = QPushButton(get_message("add_cloze", self.lang))
        self.addClozeButton.clicked.connect(self.add_cloze)
        buttonLayout.addWidget(self.addClozeButton)
        buttonLayout.addStretch()
        clozeLayout.addLayout(buttonLayout)
        
        clozeGroup.setLayout(clozeLayout)
        layout.addWidget(clozeGroup)
        
        # 解析编辑
        explanationGroup = QGroupBox(get_message("explanation", self.lang))
        explanationLayout = QVBoxLayout()
        self.explanationEdit = QPlainTextEdit()
        default_explanation = f"{get_message('answer_prefix', self.lang)}{self.answer}\n\n{get_message('ai_feedback_prefix', self.lang)}{self.feedback}"
        self.explanationEdit.setPlainText(default_explanation)
        explanationLayout.addWidget(self.explanationEdit)
        explanationGroup.setLayout(explanationLayout)
        layout.addWidget(explanationGroup)
        
        # 按钮区域
        buttonLayout = QHBoxLayout()
        self.saveButton = QPushButton(get_message("btn_save", self.lang))
        self.cancelButton = QPushButton(get_message("btn_cancel", self.lang))
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        
        # 应用样式
        apply_anki_style(self)

    def setup_connections(self):
        """设置信号连接"""
        self.saveButton.clicked.connect(self.on_save_clicked)
        self.cancelButton.clicked.connect(self.reject)

    def add_cloze(self):
        """添加填空标记"""
        cursor = self.clozeEdit.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            tooltip(get_message("select_text_warning", self.lang))
            return
            
        # 获取当前填空数量
        text = self.clozeEdit.toPlainText()
        cloze_count = len([m for m in text.split("{{c") if "::" in m]) + 1
        
        # 插入填空
        cursor.insertText(f"{{{{c{cloze_count}::{selected_text}}}}}")

    def on_save_clicked(self):
        """处理保存按钮点击事件"""
        # 发出保存请求信号，不关闭对话框
        self.saveRequested.emit()

    def save_cloze_card(self, deck_id, include_follow_up=False, follow_up_history=None):
        """
        保存填空卡片
        
        Args:
            deck_id: 牌组ID
            include_follow_up (bool): 是否包含追加提问内容
            follow_up_history (list): 追加提问历史记录
            
        Returns:
            bool: 是否保存成功
        """
        try:
            cloze_content = self.clozeEdit.toPlainText().strip()
            explanation = self.explanationEdit.toPlainText().strip()
            original_content = self.originalEdit.toPlainText().strip()
            
            # 检查是否包含填空标记
            if "{{c" not in cloze_content or "::" not in cloze_content:
                showWarning(get_message("cloze_validation", self.lang))
                return False
            
            # 如果用户选择了包含追加提问内容，将其添加到解析字段
            if include_follow_up and follow_up_history:
                # 使用HTML格式化追加提问内容
                followup_content = f'<div style="border-top: 1px solid #ccc; margin-top: 15px; padding-top: 15px;">'
                followup_content += f'<div style="font-weight: bold; color: #2196F3; margin-bottom: 10px;">{get_message("followup_content_header", self.lang)}</div>'
                
                for item in follow_up_history:
                    followup_content += '<div style="margin-bottom: 10px;">'
                    followup_content += f'<div style="color: #666; margin-bottom: 5px;">{get_message("question_prefix", self.lang)}{item["question"]}</div>'
                    followup_content += f'<div style="margin-left: 20px; color: #333;">{get_message("answer_prefix_qa", self.lang)}{item["answer"]}</div>'
                    followup_content += '</div>'
                
                followup_content += '</div>'
                explanation += followup_content
            
            # 创建填空笔记
            note = mw.col.new_note(create_feynman_cloze_type())
            
            # 设置字段内容
            note['原始内容'] = original_content
            note['填空内容'] = cloze_content
            note['解析'] = explanation
            
            # 获取标签
            config = mw.addonManager.getConfig(__name__)
            tags = config.get('deck', {}).get('tags', ['feynman-learning'])
            note.tags = tags
            
            # 添加到牌组
            mw.col.add_note(note, deck_id)
            
            # 保存更改
            mw.col.save()
            
            showInfo(get_message("cloze_create_success", self.lang))
            return True
            
        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")
            return False 