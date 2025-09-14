"""
答案评估工作线程模块
用于在后台线程中处理AI评估答案的过程
"""
from aqt.qt import QObject, pyqtSignal
from ...lang.messages import get_message, get_default_lang


class EvaluateAnswerWorker(QObject):
    """答案评估工作线程类"""
    finished = pyqtSignal()
    feedback_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_handler, question, answer):
        """
        初始化答案评估工作线程
        
        Args:
            ai_handler: AI处理器实例
            question (dict): 问题数据
            answer (str): 用户答案
        """
        super().__init__()
        self.ai_handler = ai_handler
        self.question = question
        self.answer = answer
        self.lang = get_default_lang()

    def run(self):
        """运行工作线程，处理答案评估请求"""
        try:
            # 验证数据
            if not self.ai_handler:
                raise ValueError("AI处理器未初始化")
            
            if not self.question:
                raise ValueError("问题数据为空")
            
            if not self.answer:
                raise ValueError("答案为空")
            
            # 调用AI处理器评估答案
            feedback = self.ai_handler.evaluate_answer(self.question, self.answer)
            
            if not feedback:
                raise ValueError("AI返回的评估为空")
            
            # 格式化反馈
            formatted_feedback = self._format_feedback(feedback)
                
            # 发送评估结果
            self.feedback_ready.emit(formatted_feedback)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()
    
    def _format_feedback(self, feedback):
        """
        格式化AI反馈
        
        Args:
            feedback: 反馈数据，可能是字符串或字典
            
        Returns:
            str: 格式化后的反馈文本
        """
        if isinstance(feedback, str):
            return feedback
        
        elif isinstance(feedback, dict):
            if "options" in self.question:  # 选择题
                return (
                    f"{get_message('correct_answer', self.lang) if feedback.get('is_correct') else get_message('wrong_answer', self.lang)}\n\n"
                    f"{feedback.get('feedback', '')}"
                )
            else:  # 问答题
                return (
                    f"{get_message('score_prefix', self.lang)}{feedback.get('score', '?')}\n\n"
                    f"{get_message('feedback_prefix', self.lang)}{feedback.get('feedback', '')}\n\n"
                    f"{get_message('covered_points', self.lang)}\n" + 
                    "\n".join([f"✓ {point}" for point in feedback.get('covered_points', [])]) + "\n\n"
                    f"{get_message('missing_points', self.lang)}\n" + 
                    "\n".join([f"• {point}" for point in feedback.get('missing_points', [])]) + "\n\n"
                    f"{get_message('suggestions', self.lang)}\n{feedback.get('suggestions', '')}"
                )
        else:
            # 未知类型，返回字符串表示
            return str(feedback) 