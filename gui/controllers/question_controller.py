"""
问题处理控制器模块
"""
from aqt.qt import QPoint
from aqt.utils import showInfo, showWarning
from ...lang.messages import get_message
from ..dialogs.review_dialog import ReviewDialog
from ..knowledge_window import KnowledgeCardWindow
from ...utils.ai_handler import AIHandler

class QuestionController:
    """问题处理控制器，负责处理问题生成、显示和评估"""
    
    def __init__(self, dialog):
        """
        初始化控制器
        
        参数:
        dialog -- 持有对话框的引用
        """
        self.dialog = dialog
        self.current_questions = None
        self.current_question_index = 0
        self.review_dialog = None
        self.knowledge_dialog = None
        self.ai_handler = AIHandler()
        
    def on_questions_generated(self, questions):
        """
        问题生成完成的回调
        
        参数:
        questions -- 生成的问题数据
        """
        self.current_questions = questions
        self.current_question_index = 0
        
        # 获取选择的追加提问模型
        selected_followup_model = self.dialog.ui.followUpModelComboBox.currentData()

        # 根据问题类型创建不同的窗口
        question_type = self.dialog.ui.questionTypeComboBox.currentText()
        if question_type == get_message("question_type_knowledge", self.dialog.lang) or \
           question_type == get_message("question_type_language_learning", self.dialog.lang):
            # 创建或更新知识卡窗口（知识卡和语言学习知识卡都使用同一个窗口）
            if not hasattr(self, 'knowledge_dialog') or self.knowledge_dialog is None:
                self.knowledge_dialog = KnowledgeCardWindow(questions, parent=self.dialog)
                # 传递追加提问模型和AI处理器
                self.knowledge_dialog.followup_model = selected_followup_model
                self.knowledge_dialog.followup_panel.set_followup_model(selected_followup_model)
                # 设置追问处理器
                self.knowledge_dialog._setup_followup_handler()
            else:
                # 更新现有窗口的内容和追加提问模型
                self.knowledge_dialog.update_cards(questions)
                self.knowledge_dialog.followup_model = selected_followup_model
                self.knowledge_dialog.followup_panel.set_followup_model(selected_followup_model)
            self.knowledge_dialog.show()
            
            # 将窗口移动到输入窗口旁边
            input_pos = self.dialog.pos()
            input_size = self.dialog.size()
            knowledge_pos = QPoint(input_pos.x() + input_size.width() + 10, input_pos.y())
            self.knowledge_dialog.move(knowledge_pos)
        else:
            # 创建或更新答题窗口
            if not hasattr(self, 'review_dialog') or self.review_dialog is None:
                self.review_dialog = ReviewDialog(questions=self.current_questions, parent=self.dialog, ai_handler=self.ai_handler)
            else:
                # 更新现有窗口的内容
                self.review_dialog.update_questions(self.current_questions)

            # 显示窗口
            self.review_dialog.show()
            
            # 将窗口移动到输入窗口旁边
            input_pos = self.dialog.pos()
            input_size = self.dialog.size()
            review_pos = QPoint(input_pos.x() + input_size.width() + 10, input_pos.y())
            self.review_dialog.move(review_pos)

        # 恢复界面状态
        self.dialog.ui.progressBar.hide()
        self.dialog.ui.generateButton.setEnabled(True)
        
    def on_generation_error(self, error_message):
        """
        处理生成过程中的错误
        
        参数:
        error_message -- 错误信息
        """
        showWarning(f"{get_message('generation_error', self.dialog.lang)}{error_message}")
        self.dialog.ui.progressBar.hide()
        self.dialog.ui.generateButton.setEnabled(True)
        
    def show_current_question(self):
        """显示当前问题 - 已由ReviewDialog内部处理，此方法保留但不再需要实现具体逻辑"""
        if not self.current_questions or 'questions' not in self.current_questions:
            showWarning(get_message("no_questions", self.dialog.lang))
            return

        # 新的ReviewDialog会自己处理问题的显示，这里只需检查是否有问题
        questions = self.current_questions['questions']
        if self.current_question_index >= len(questions):
            showInfo(get_message("all_questions_done", self.dialog.lang))
            return
            
    def on_answer_submitted(self, answer):
        """
        处理用户提交的答案 - 已由ReviewDialog内部控制器处理，此方法保留但不再需要实现具体逻辑
        
        参数:
        answer -- 用户提交的答案
        """
        # 新的ReviewDialog使用内部控制器处理答案评估，此方法保留仅作为接口兼容
        pass
            
    def on_next_question(self):
        """显示下一个问题 - 已由ReviewDialog内部处理，此方法保留但不再需要复杂实现"""
        if not self.current_questions or 'questions' not in self.current_questions:
            return

        questions = self.current_questions['questions']
        self.current_question_index += 1
        
        if self.current_question_index >= len(questions):
            showInfo(get_message("all_questions_done", self.dialog.lang))
            if self.review_dialog:
                self.review_dialog.close()
            return
            
        # 如果使用新的ReviewDialog，则这一步已经由内部处理
        
    @property
    def ai_handler(self):
        """获取AI处理器实例"""
        if not hasattr(self, '_ai_handler') or self._ai_handler is None:
            self._ai_handler = AIHandler()
        return self._ai_handler
        
    @ai_handler.setter
    def ai_handler(self, handler):
        """设置AI处理器实例"""
        self._ai_handler = handler 