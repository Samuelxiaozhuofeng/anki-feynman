"""
追加问题工作线程模块
负责处理追加提问请求并获取AI回答
"""
from aqt.qt import QObject, pyqtSignal


class FollowUpQuestionWorker(QObject):
    """追加问题处理工作线程类"""
    finished = pyqtSignal()
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_handler, context, followup_model=None):
        """
        初始化追加问题工作线程
        
        Args:
            ai_handler: AI处理器实例
            context (dict): 上下文信息，包含原始问题、用户回答、反馈等
            followup_model: 追加提问使用的模型，如果为None则使用默认模型
        """
        super().__init__()
        self.ai_handler = ai_handler
        self.context = context
        self.followup_model = followup_model

    def run(self):
        """运行工作线程，处理追加问题请求"""
        try:
            # 确保上下文中的关键字段存在，如果不存在则给默认值
            required_fields = ["original_question", "source_content", "user_answer", 
                              "ai_feedback", "follow_up_question", "history"]
            
            # 用默认值初始化上下文，确保所有必要字段都存在
            normalized_context = {
                "original_question": "",
                "source_content": "",
                "user_answer": "",
                "ai_feedback": "",
                "follow_up_question": "",
                "history": []
            }
            
            # 更新上下文，使用提供的值
            for field in required_fields:
                if field in self.context and self.context[field] is not None:
                    normalized_context[field] = self.context[field]
            
            # 确保follow_up_question字段有值
            if not normalized_context["follow_up_question"]:
                raise ValueError("追问内容不能为空")
                
            # 打印调试信息
            print(f"追问处理: 问题={normalized_context['follow_up_question']}, 原问题长度={len(normalized_context['original_question'])}")
            
            # 如果指定了追加提问模型，临时设置AI处理器使用该模型
            original_model = None
            if self.followup_model:
                # 先保存当前模型
                original_model = self.ai_handler.current_model_info
                # 设置为追加提问模型
                self.ai_handler.set_model(self.followup_model)
                
            try:
                # 调用AI处理器
                response = self.ai_handler.handle_follow_up_question(normalized_context)
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