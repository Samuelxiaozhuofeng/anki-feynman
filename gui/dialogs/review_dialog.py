"""
主复习对话框模块
用于提供主复习界面框架，集成和组织各个UI组件
"""
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning, askUser

from ..styles.anki_style import apply_anki_style
from ..components.question_view import QuestionView
from ..components.answer_input import AnswerInput
from ..components.feedback_view import FeedbackView
from ..components.followup_panel import FollowUpPanel
from ..controllers.review_controller import ReviewController
from ...utils import create_feynman_note
from ...utils.question_sets import add_question_set, update_question_set
from ...lang.messages import get_message, get_default_lang


class ReviewDialog(QDialog):
    """主复习对话框"""
    
    def __init__(self, questions=None, parent=None, ai_handler=None):
        """
        初始化复习对话框
        
        Args:
            questions (dict): 问题数据，包含questions列表
            parent: 父窗口
            ai_handler: AI处理器实例
        """
        super().__init__(parent)
        self.config = mw.addonManager.getConfig(__name__)
        self.lang = get_default_lang()
        self.ai_handler = ai_handler
        self.auto_save = False
        
        # 创建控制器
        self.controller = ReviewController(self, ai_handler)
        
        # 题目集ID，用于更新进度
        self.controller.question_set_id = None
        
        # 初始化UI
        self.setup_ui()
        self.load_config()
        self.setup_connections()
        
        # 设置问题
        if questions:
            self.controller.update_questions(questions)
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("review_window_title", self.lang))
        self.resize(900, 700)  # 增加窗口宽度以容纳右侧追加提问区域
        
        # 创建主水平布局
        mainLayout = QHBoxLayout(self)
        
        # 创建左侧垂直布局
        leftLayout = QVBoxLayout()
        
        # 创建组件
        self.questionView = QuestionView(self)
        leftLayout.addWidget(self.questionView)
        
        # 创建"添加到ANKI"和"制作填空卡"按钮，但不在这里添加到布局
        self.saveToAnkiButton = QPushButton(get_message("add_to_anki", self.lang))
        self.saveToAnkiButton.setEnabled(False)
        self.makeClozeButton = QPushButton(get_message("make_cloze", self.lang))
        self.makeClozeButton.setEnabled(False)
        
        # 在AnswerInput组件中已包含提交、下一题按钮，不需要在这里额外添加
        self.answerInput = AnswerInput(self)
        
        # 获取answerInput的按钮布局并添加保存到Anki和制作填空卡按钮
        if hasattr(self.answerInput, 'buttonLayout'):
            self.answerInput.buttonLayout.addWidget(self.saveToAnkiButton)
            self.answerInput.buttonLayout.addSpacing(10)
            self.answerInput.buttonLayout.addWidget(self.makeClozeButton)
        
        leftLayout.addWidget(self.answerInput)
        
        # 添加反馈区域
        self.feedbackView = FeedbackView(self)
        leftLayout.addWidget(self.feedbackView)
        
        # 创建右侧追加提问面板
        self.followupPanel = FollowUpPanel(self, ai_handler=self.ai_handler)
        
        # 设置左右布局的比例
        mainLayout.addLayout(leftLayout, 3)  # 左侧占3份
        mainLayout.addWidget(self.followupPanel, 2)  # 右侧占2份
        
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 应用样式
        apply_anki_style(self)
    
    def load_config(self):
        """加载配置"""
        # 检查并更新UI语言设置
        current_anki_lang = get_default_lang()
        if self.config.get('ui', {}).get('language') != current_anki_lang:
            if 'ui' not in self.config:
                self.config['ui'] = {}
            self.config['ui']['language'] = current_anki_lang
            mw.addonManager.writeConfig(__name__, self.config)
            self.lang = current_anki_lang
            self.update_ui_texts()
    
    def update_ui_texts(self):
        """更新UI文本"""
        self.setWindowTitle(get_message("review_window_title", self.lang))
        self.saveToAnkiButton.setText(get_message("add_to_anki", self.lang))
        self.makeClozeButton.setText(get_message("make_cloze", self.lang))
        
        # 更新子组件的语言
        self.questionView.update_language()
        self.answerInput.update_language()
        self.feedbackView.update_language()
    
    def setup_connections(self):
        """设置信号连接"""
        # 连接控制器信号
        self.controller.question_ready.connect(self.on_question_ready)
        self.controller.feedback_ready.connect(self.on_feedback_ready)
        
        # 连接UI信号
        self.answerInput.answer_submitted.connect(self.on_answer_submitted)
        self.saveToAnkiButton.clicked.connect(self.save_to_anki)
        self.makeClozeButton.clicked.connect(self.make_cloze)
    
    def on_question_ready(self, question_data):
        """
        处理问题准备好的信号
        
        Args:
            question_data (dict): 问题数据
        """
        # 设置问题显示
        options = self.questionView.set_question(
            question_data['text'],
            question_data['index'],
            question_data['total']
        )
        
        # 设置选项（如果是选择题）
        if options:
            self.answerInput.set_options(options)
        else:
            self.answerInput.set_options([])  # 清除选项，显示文本输入
        
        # 默认清空所有状态
        self.answerInput.clear()
        self.feedbackView.clear()
        self.followupPanel.clear()
        
        # 重要：设置上一题按钮状态
        # 如果问题索引大于1（从0开始，索引为1表示第二题），启用上一题按钮
        if question_data['index'] > 1:
            self.answerInput.prevButton.setEnabled(True)
        else:
            self.answerInput.prevButton.setEnabled(False)
        
        # 恢复历史答案和反馈（如果有）
        if question_data.get('has_history'):
            # 恢复答案
            if question_data.get('answer'):
                if options:  # 选择题
                    # 查找选择题答案对应的按钮并选中
                    for button in self.answerInput.optionButtonGroup.buttons():
                        if button.text() == question_data['answer']:
                            button.setChecked(True)
                            break
                else:  # 问答题
                    self.answerInput.answerEdit.setPlainText(question_data['answer'])
                
                # 设置内部状态
                self.answerInput.current_answer = question_data['answer']
                
            # 恢复反馈
            if question_data.get('feedback'):
                self.feedbackView.set_feedback(question_data['feedback'])
            
            # 启用下一题按钮，禁用提交按钮
            self.answerInput.submitButton.setEnabled(False)
            self.answerInput.nextButton.setEnabled(True)
            
            # 启用保存和填空卡按钮
            self.saveToAnkiButton.setEnabled(True)
            self.makeClozeButton.setEnabled(True)
            
            # 恢复追问历史（如果有）
            if hasattr(self.controller, 'question_history'):
                current_index = self.controller.current_question_index
                if current_index in self.controller.question_history:
                    followup_content = self.controller.question_history[current_index].get('followup_content')
                    if followup_content:
                        self.followupPanel.restore_followup_content(followup_content)
        
        # 如果是从题目集加载的，更新进度
        if hasattr(self.controller, 'question_set_id') and self.controller.question_set_id:
            update_question_set(self.controller.question_set_id, self.controller.current_question_index)
    
    def on_answer_submitted(self, answer):
        """
        处理答案提交信号
        
        Args:
            answer (str): 用户提交的答案
        """
        self.feedbackView.show_loading(50)
        self.controller.process_answer(answer)
    
    def on_feedback_ready(self, feedback):
        """
        处理反馈准备好的信号
        
        Args:
            feedback (str): 反馈内容
        """
        # 设置反馈显示
        mastery = self.feedbackView.set_feedback(feedback)
        self.feedbackView.hide_loading()
        
        # 启用保存和填空卡按钮
        self.saveToAnkiButton.setEnabled(True)
        self.makeClozeButton.setEnabled(True)
    
    def on_auto_save_changed(self, state):
        """
        自动保存选项改变事件
        
        Args:
            state: 复选框状态
        """
        self.auto_save = bool(state)
        self.saveToAnkiButton.setEnabled(
            not self.auto_save and 
            self.controller.current_feedback and 
            self.controller.current_answer
        )
    
    def on_next_question(self):
        """处理下一题按钮点击事件"""
        self.controller.next_question()
    
    def on_prev_question(self):
        """处理上一题按钮点击事件"""
        self.controller.previous_question()
    
    def save_to_anki(self):
        """保存当前问答到Anki"""
        if not hasattr(self.parent(), 'deckComboBox'):
            showWarning(get_message("no_deck_selected", self.lang))
            return
            
        deck_id = self.parent().deckComboBox.currentData()
        
        # 检查是否需要包含追加提问内容
        include_follow_up = self.followupPanel.has_followup_content()
        follow_up_content = ""
        
        if include_follow_up:
            follow_up_content = self.followupPanel.get_followup_content_text()
        
        # 保存到Anki
        success = self.controller.save_to_anki(
            deck_id=deck_id,
            include_follow_up=include_follow_up,
            follow_up_content=follow_up_content
        )
        
        if success:
            self.saveToAnkiButton.setEnabled(False)
    
    def make_cloze(self):
        """将当前问题转化为填空卡"""
        if not hasattr(self.parent(), 'deckComboBox'):
            showWarning(get_message("no_deck_selected", self.lang))
            return
            
        deck_id = self.parent().deckComboBox.currentData()
        
        # 检查是否需要包含追加提问内容
        include_follow_up = self.followupPanel.has_followup_content()
        follow_up_history = self.followupPanel.follow_up_history if include_follow_up else None
        
        # 创建填空卡
        self.controller.make_cloze(
            deck_id=deck_id,
            include_follow_up=include_follow_up,
            follow_up_history=follow_up_history
        )
    
    def update_questions(self, questions):
        """
        更新问题数据
        
        Args:
            questions (dict): 问题数据，包含questions列表
        """
        self.controller.update_questions(questions)
        
    def save_question_set(self, title=None):
        """
        保存当前题目集
        
        Args:
            title (str, optional): 题目集标题，如果未提供则弹出输入框
            
        Returns:
            bool: 是否保存成功
        """
        # 检查是否有问题
        if not hasattr(self.controller, 'current_questions') or not self.controller.current_questions:
            showWarning("没有题目可保存")
            return False
            
        # 如果未提供标题，弹出输入框
        if not title:
            title, ok = QInputDialog.getText(self, "保存题目集", "请输入题目集标题:")
            if not ok or not title:
                return False
                
        # 保存题目集
        return add_question_set(
            title=title,
            questions=self.controller.current_questions,
            current_index=self.controller.current_question_index
        )
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        
        Args:
            event: 关闭事件
        """
        # 检查是否有题目
        if (hasattr(self.controller, 'current_questions') and 
            self.controller.current_questions and 
            'questions' in self.controller.current_questions and
            len(self.controller.current_questions['questions']) > 0):
            
            # 计算题目进度
            total = len(self.controller.current_questions['questions'])
            current = self.controller.current_question_index
            
            # 如果已经有题目集ID，则更新进度
            if self.controller.question_set_id:
                update_question_set(self.controller.question_set_id, current)
            # 否则，如果答题未完成，询问是否保存
            elif current < total:
                # 确认是否保存题目集
                result = QMessageBox.question(
                    self,
                    "保存题目集",
                    f"您已完成{current}/{total}道题，是否要保存题目集以便稍后继续？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if result == QMessageBox.StandardButton.Yes:
                    self.save_question_set()
        
        # 处理原有的关闭逻辑
        super().closeEvent(event) 