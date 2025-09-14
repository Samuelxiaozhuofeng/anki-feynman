"""
问题显示组件
用于显示当前问题及其编号，支持选择题和问答题
"""
from aqt.qt import *
from ...lang.messages import get_message, get_default_lang


class QuestionView(QWidget):
    """问题显示组件"""
    
    def __init__(self, parent=None):
        """
        初始化问题显示组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.lang = get_default_lang()
        self.current_question = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 问题展示区域
        self.questionGroupBox = QGroupBox(get_message("question_group", self.lang))
        questionLayout = QVBoxLayout()
        self.questionLabel = QLabel()
        self.questionLabel.setWordWrap(True)
        self.questionLabel.setTextFormat(Qt.TextFormat.RichText)
        questionLayout.addWidget(self.questionLabel)
        self.questionGroupBox.setLayout(questionLayout)
        layout.addWidget(self.questionGroupBox)
    
    def set_question(self, question_text, current_index=None, total_questions=None):
        """
        设置问题内容
        
        Args:
            question_text (str): 问题文本内容
            current_index (int, optional): 当前问题索引(从1开始)
            total_questions (int, optional): 总问题数量
        """
        self.current_question = question_text
        
        # 如果提供了索引和总数，添加问题编号前缀
        if current_index is not None and total_questions is not None:
            # 检查问题文本中是否已经包含题号，如果包含则不重复添加
            question_number = get_message("question_number", self.lang).format(
                current=current_index,
                total=total_questions
            )
            
            # 如果问题文本开头没有题号，则添加
            if not question_text.strip().startswith(f"问题 {current_index}/{total_questions}"):
                question_text = f"{question_number}\n\n{question_text}"
        
        # 检查是否是选择题（通过查找选项标记）
        options_separator = get_message("options_separator", self.lang)
        if options_separator in question_text:
            # 分离问题和选项
            question_parts = question_text.split(options_separator)
            question_only = question_parts[0]
            
            # 设置问题文本（移除末尾的换行符）
            self.questionLabel.setText(question_only.strip())
            
            # 返回选项列表，供答案输入组件使用
            if len(question_parts) > 1:
                options = question_parts[1].strip().split("\n")
                return options
        else:
            # 问答题直接显示问题
            self.questionLabel.setText(question_text)
            return None
    
    def clear(self):
        """清除问题显示"""
        self.current_question = ""
        self.questionLabel.clear()
    
    def update_language(self):
        """更新语言"""
        self.lang = get_default_lang()
        self.questionGroupBox.setTitle(get_message("question_group", self.lang)) 