"""
反馈显示组件
用于显示AI反馈内容，格式化反馈信息，提取掌握程度
"""
from aqt.qt import *
from ...lang.messages import get_message, get_default_lang


class FeedbackView(QWidget):
    """反馈显示组件"""
    
    def __init__(self, parent=None):
        """
        初始化反馈显示组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.lang = get_default_lang()
        self.current_feedback = ""
        self.current_mastery = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # AI反馈区域
        self.feedbackGroupBox = QGroupBox(get_message("ai_feedback_group", self.lang))
        feedbackLayout = QVBoxLayout()
        self.feedbackLabel = QLabel()
        self.feedbackLabel.setWordWrap(True)
        self.feedbackLabel.setTextFormat(Qt.TextFormat.RichText)
        feedbackLayout.addWidget(self.feedbackLabel)
        self.feedbackGroupBox.setLayout(feedbackLayout)
        layout.addWidget(self.feedbackGroupBox)
        
        # 进度条
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setTextVisible(False)
        self.progressBar.hide()
        layout.addWidget(self.progressBar)
    
    def set_feedback(self, feedback_text):
        """
        设置AI反馈内容
        
        Args:
            feedback_text (str): 反馈文本
            
        Returns:
            str: 提取的掌握程度
        """
        self.current_feedback = feedback_text
        self.feedbackLabel.setText(feedback_text)
        
        # 从反馈中提取掌握程度
        mastery = self._extract_mastery(feedback_text)
        self.current_mastery = mastery
        
        # 返回掌握程度，便于上层组件使用
        return mastery
    
    def _extract_mastery(self, feedback_text):
        """
        从反馈中提取掌握程度
        
        Args:
            feedback_text (str): 反馈文本
            
        Returns:
            str: 掌握程度文本
        """
        if "得分：" in feedback_text:
            score_text = feedback_text.split("得分：")[1].split("\n")[0].strip()
            return score_text
        elif "✓ 回答正确" in feedback_text:
            return "100%"
        else:
            return get_message("needs_review", self.lang) or "需要复习"
    
    def show_loading(self, value=50):
        """
        显示加载进度条
        
        Args:
            value (int): 进度值，0-100
        """
        if value == 0:
            # 显示不确定进度条
            self.progressBar.setMaximum(0)
        else:
            # 显示确定进度条
            self.progressBar.setMaximum(100)
            self.progressBar.setValue(value)
        
        self.progressBar.show()
    
    def hide_loading(self):
        """隐藏加载进度条"""
        self.progressBar.hide()
        self.progressBar.setValue(0)
    
    def clear(self):
        """清除反馈显示"""
        self.current_feedback = ""
        self.current_mastery = ""
        self.feedbackLabel.clear()
        self.hide_loading()
    
    def get_feedback(self):
        """
        获取当前反馈文本
        
        Returns:
            str: 当前反馈文本
        """
        return self.current_feedback
    
    def get_mastery(self):
        """
        获取当前掌握程度
        
        Returns:
            str: 当前掌握程度
        """
        return self.current_mastery
    
    def update_language(self):
        """更新语言"""
        self.lang = get_default_lang()
        self.feedbackGroupBox.setTitle(get_message("ai_feedback_group", self.lang)) 