"""
知识卡片追问工作线程模块
处理知识卡片的AI追问请求
"""
from aqt.qt import QObject, pyqtSignal


class FollowUpQuestionWorker(QObject):
    """处理追问请求的工作线程"""
    finished = pyqtSignal()
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_handler, context, followup_model=None):
        """
        初始化追问工作线程
        
        Args:
            ai_handler: AI处理器实例
            context: 上下文信息字典
            followup_model: 追加提问使用的模型（可选）
        """
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

