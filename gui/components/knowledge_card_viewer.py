"""
知识卡片查看组件
显示卡片的问题、答案和上下文
"""
from aqt.qt import QWidget, QVBoxLayout, QGroupBox, QTextEdit
from ...lang.messages import get_message, get_default_lang


class KnowledgeCardViewer(QWidget):
    """知识卡片查看组件"""
    
    def __init__(self, parent=None):
        """
        初始化卡片查看组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.lang = get_default_lang()
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 问题区域
        question_group = QGroupBox(get_message("question_field", self.lang))
        question_layout = QVBoxLayout()
        self.question_text = QTextEdit()
        self.question_text.setReadOnly(True)
        question_layout.addWidget(self.question_text)
        question_group.setLayout(question_layout)
        layout.addWidget(question_group)
        
        # 答案区域
        answer_group = QGroupBox(get_message("answer_field", self.lang))
        answer_layout = QVBoxLayout()
        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        answer_layout.addWidget(self.answer_text)
        answer_group.setLayout(answer_layout)
        layout.addWidget(answer_group)
        
        # 上下文区域
        context_group = QGroupBox(get_message("context_field", self.lang))
        context_layout = QVBoxLayout()
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        context_layout.addWidget(self.context_text)
        context_group.setLayout(context_layout)
        layout.addWidget(context_group)
        
    def display_card(self, card_data):
        """
        显示卡片内容
        
        Args:
            card_data: 卡片数据字典，包含 question, answer, context 等字段
        """
        if not card_data:
            self.clear()
            return
            
        self.question_text.setText(card_data.get('question', ''))
        self.answer_text.setText(card_data.get('answer', ''))
        self.context_text.setText(card_data.get('context', ''))
        
    def clear(self):
        """清空显示内容"""
        self.question_text.clear()
        self.answer_text.clear()
        self.context_text.clear()
        
    def get_current_card_text(self):
        """
        获取当前显示的卡片文本（用于预览等功能）
        
        Returns:
            dict: 包含 question, answer, context 的字典
        """
        return {
            'question': self.question_text.toPlainText(),
            'answer': self.answer_text.toPlainText(),
            'context': self.context_text.toPlainText()
        }

