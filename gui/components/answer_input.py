"""
答案输入组件
用于提供答案输入界面，支持选择题选项和问答题文本输入
"""
from aqt.qt import *
from aqt.utils import showWarning
from ...lang.messages import get_message, get_default_lang


class AnswerInput(QWidget):
    """答案输入组件"""
    
    # 自定义信号
    answer_submitted = pyqtSignal(str)  # 提交答案信号
    answer_changed = pyqtSignal()       # 答案变化信号
    
    def __init__(self, parent=None):
        """
        初始化答案输入组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.lang = get_default_lang()
        self.current_answer = ""
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 答案输入区域
        self.answerGroupBox = QGroupBox(get_message("your_answer_group", self.lang))
        answerLayout = QVBoxLayout()
        
        # 选择题答案选择
        self.optionButtonGroup = QButtonGroup(self)
        self.optionLayout = QVBoxLayout()
        answerLayout.addLayout(self.optionLayout)
        
        # 问答题答案输入
        self.answerEdit = QPlainTextEdit()
        self.answerEdit.setPlaceholderText(get_message("enter_answer_placeholder", self.lang))
        answerLayout.addWidget(self.answerEdit)
        
        self.answerGroupBox.setLayout(answerLayout)
        layout.addWidget(self.answerGroupBox)
        
        # 按钮区域 - 修改布局使按钮居中显示
        self.buttonLayout = QHBoxLayout()
        self.submitButton = QPushButton(get_message("submit_answer", self.lang))
        self.submitButton.setMinimumWidth(120)  # 设置最小宽度
        self.prevButton = QPushButton(get_message("prev_question", self.lang))
        self.prevButton.setMinimumWidth(120)  # 设置最小宽度
        self.prevButton.setEnabled(False)  # 初始时禁用上一题按钮
        self.nextButton = QPushButton(get_message("next_question", self.lang))
        self.nextButton.setMinimumWidth(120)  # 设置最小宽度
        self.nextButton.setEnabled(False)
        
        # 调整布局，将提交答案和上一题、下一题按钮放到左侧
        self.buttonLayout.addWidget(self.submitButton)
        self.buttonLayout.addSpacing(10)  # 按钮之间添加间距
        self.buttonLayout.addWidget(self.prevButton)
        self.buttonLayout.addSpacing(10)  # 按钮之间添加间距
        self.buttonLayout.addWidget(self.nextButton)
        self.buttonLayout.addStretch(1)  # 右侧添加弹性空间
        
        layout.addLayout(self.buttonLayout)
    
    def setup_connections(self):
        """设置信号连接"""
        self.submitButton.clicked.connect(self.on_submit_clicked)
        self.prevButton.clicked.connect(self.on_prev_clicked)
        self.nextButton.clicked.connect(self.on_next_clicked)
        self.answerEdit.textChanged.connect(self.on_answer_changed)
    
    def set_options(self, options):
        """
        设置选择题选项
        
        Args:
            options (list): 选项列表
        """
        # 清除现有选项
        self._clear_option_buttons()
        
        # 如果提供了有效的选项列表，显示选项按钮并隐藏文本输入
        if options and isinstance(options, list) and len(options) > 0:
            for option in options:
                if option.strip():
                    radio = QRadioButton(option)
                    self.optionButtonGroup.addButton(radio)
                    self.optionLayout.addWidget(radio)
            
            # 显示选项，隐藏文本输入
            self.answerEdit.hide()
            return True
        else:
            # 无有效选项，显示文本输入
            self.answerEdit.show()
            return False
    
    def _clear_option_buttons(self):
        """清除选择题选项按钮"""
        for button in self.optionButtonGroup.buttons():
            self.optionButtonGroup.removeButton(button)
            self.optionLayout.removeWidget(button)
            button.deleteLater()
    
    def on_answer_changed(self):
        """答案输入变化事件"""
        self.answer_changed.emit()
    
    def on_submit_clicked(self):
        """提交答案按钮点击事件"""
        answer = self.get_answer()
        
        if not answer:
            showWarning(get_message("enter_answer_warning", self.lang))
            return
        
        self.current_answer = answer
        self.answer_submitted.emit(answer)
        
        # 禁用提交按钮，启用下一题按钮
        self.submitButton.setEnabled(False)
        self.nextButton.setEnabled(True)
        
        # 设置上一题按钮状态（根据当前题目索引）
        if hasattr(self.parent, 'controller') and hasattr(self.parent.controller, 'current_question_index'):
            # 索引从0开始，所以大于0表示不是第一题
            if self.parent.controller.current_question_index > 0:
                self.prevButton.setEnabled(True)
            else:
                self.prevButton.setEnabled(False)
    
    def on_prev_clicked(self):
        """上一题按钮点击事件"""
        # 通知父组件处理上一题，由父组件控制状态恢复
        if hasattr(self.parent, 'on_prev_question'):
            self.parent.on_prev_question()
    
    def on_next_clicked(self):
        """下一题按钮点击事件"""
        # 通知父组件处理下一题，由父组件控制状态恢复
        if hasattr(self.parent, 'on_next_question'):
            self.parent.on_next_question()
    
    def get_answer(self):
        """
        获取当前答案
        
        Returns:
            str: 当前答案文本
        """
        if self.answerEdit.isVisible():
            # 问答题
            return self.answerEdit.toPlainText().strip()
        else:
            # 选择题
            selected_button = self.optionButtonGroup.checkedButton()
            if selected_button:
                return selected_button.text()
            else:
                return ""
    
    def clear(self):
        """清除答案"""
        self.answerEdit.clear()
        for button in self.optionButtonGroup.buttons():
            button.setChecked(False)
        self.submitButton.setEnabled(True)
        self.nextButton.setEnabled(False)
        
        # 只在第一题时禁用上一题按钮
        # 注意：current_question_index从0开始，0表示第一题
        if hasattr(self.parent, 'controller') and hasattr(self.parent.controller, 'current_question_index'):
            if self.parent.controller.current_question_index == 0:
                self.prevButton.setEnabled(False)
            else:
                self.prevButton.setEnabled(True)
        else:
            # 如果没有控制器或者控制器没有current_question_index属性，默认禁用上一题按钮
            self.prevButton.setEnabled(False)
            
        self.current_answer = ""
    
    def enable_next_button(self, enable_prev=True):
        """
        启用下一题按钮
        
        Args:
            enable_prev (bool): 是否同时启用上一题按钮，默认为True
        """
        self.nextButton.setEnabled(True)
        if enable_prev:
            self.prevButton.setEnabled(True)
        self.submitButton.setEnabled(False)
    
    def update_language(self):
        """更新语言"""
        self.lang = get_default_lang()
        self.answerGroupBox.setTitle(get_message("your_answer_group", self.lang))
        self.answerEdit.setPlaceholderText(get_message("enter_answer_placeholder", self.lang))
        self.submitButton.setText(get_message("submit_answer", self.lang))
        self.prevButton.setText(get_message("prev_question", self.lang))
        self.nextButton.setText(get_message("next_question", self.lang)) 