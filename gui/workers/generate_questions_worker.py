"""
问题生成工作线程
"""
from aqt.qt import QObject, pyqtSignal

class GenerateQuestionsWorker(QObject):
    """生成问题的工作线程类"""
    finished = pyqtSignal()
    questions_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_handler, content, question_type, num_questions, model_name=None, template_id=None, followup_model=None):
        """
        初始化问题生成工作线程
        
        参数:
        ai_handler -- AI处理器实例
        content -- 输入内容
        question_type -- 问题类型
        num_questions -- 问题数量
        model_name -- 模型名称（可选）
        template_id -- 模板ID（可选，自定义类型需要）
        followup_model -- 追加提问模型（可选）
        """
        super().__init__()
        self.ai_handler = ai_handler
        self.content = content
        self.question_type = question_type
        self.num_questions = num_questions
        self.model_name = model_name
        self.template_id = template_id
        self.followup_model = followup_model

    def run(self):
        """运行工作线程，生成问题"""
        try:
            # 如果设置了模型名称，先设置模型
            if self.model_name:
                self.ai_handler.set_model(self.model_name)
                
            # 生成问题
            if self.question_type == "custom" and self.template_id:
                questions = self.ai_handler.generate_custom_questions(
                    self.content, 
                    self.template_id, 
                    self.num_questions
                )
            else:
                questions = self.ai_handler.generate_questions(
                    self.content, 
                    self.question_type, 
                    self.num_questions
                )
                
            # 将追加提问模型信息添加到结果中
            if self.followup_model:
                if isinstance(questions, dict):
                    questions['followup_model'] = self.followup_model
                
            self.questions_ready.emit(questions)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit() 