"""
复习控制器模块
用于管理复习过程中的状态，协调各组件间的数据流，处理卡片保存逻辑
"""
from aqt import mw
from aqt.utils import showInfo, showWarning
from aqt.qt import QObject, pyqtSignal, QThread, QDialog

from ...utils import create_feynman_note, create_feynman_cloze_type
from ...utils.question_sets import update_question_set
from ...lang.messages import get_message, get_default_lang
from ..dialogs.cloze_dialog import ClozeDialog


class ReviewController(QObject):
    """复习控制器类"""
    
    # 自定义信号
    feedback_ready = pyqtSignal(str)     # 反馈准备好的信号
    question_ready = pyqtSignal(dict)    # 问题准备好的信号
    
    def __init__(self, parent=None, ai_handler=None):
        """
        初始化复习控制器
        
        Args:
            parent: 父窗口
            ai_handler: AI处理器实例
        """
        super().__init__(parent)
        self.parent = parent
        self.ai_handler = ai_handler
        self.lang = get_default_lang()
        
        # 状态数据
        self.current_questions = None
        self.current_question_index = 0
        self.current_question = ""
        self.current_answer = ""
        self.current_feedback = ""
        self.current_mastery = ""
        self.current_source_content = None
        
        # 存储每个问题的答案和反馈的字典
        self.question_history = {}
        
        # 题目集ID，用于更新进度
        self.question_set_id = None
        
        # 工作线程
        self.thread = None
        self.worker = None
    
    def update_questions(self, questions):
        """
        更新问题数据，重置状态
        
        Args:
            questions (dict): 问题数据，包含questions列表
        """
        # 重置所有状态
        self.current_questions = questions
        self.current_question_index = 0
        self.current_question = None
        self.current_answer = None
        self.current_feedback = None
        self.current_mastery = None
        self.current_source_content = None
        
        # 重要：清除历史记录，避免旧的答题历史干扰新问题
        self.question_history = {}
        
        self.show_current_question()
    
    def show_current_question(self):
        """显示当前问题"""
        if not self.current_questions or 'questions' not in self.current_questions:
            showWarning(get_message("no_questions", self.lang))
            return
        
        questions = self.current_questions['questions']
        if self.current_question_index >= len(questions):
            showInfo(get_message("all_questions_done", self.lang))
            return
        
        current_question = questions[self.current_question_index]
        self.current_source_content = current_question.get('source_content', '')
        
        # 准备问题文本，不添加问题编号，由UI组件处理
        if "options" in current_question:  # 选择题
            question_text = (
                f"{current_question['question']}\n\n"
                f"{get_message('options_separator', self.lang)}" + 
                "\n".join(current_question['options'])
            )
        else:  # 问答题
            question_text = current_question['question']
        
        self.current_question = question_text
        print(f"已设置当前问题: {len(question_text)}字符")
        
        # 检查是否有历史答案和反馈
        if self.current_question_index in self.question_history:
            history = self.question_history[self.current_question_index]
            self.current_answer = history.get('answer', '')
            self.current_feedback = history.get('feedback', '')
            self.current_mastery = history.get('mastery', '')
        else:
            self.current_answer = ""
            self.current_feedback = ""
            self.current_mastery = ""
        
        # 通知UI组件显示问题
        question_data = {
            'text': question_text,
            'index': self.current_question_index + 1,
            'total': len(questions),
            'is_multiple_choice': "options" in current_question,
            'options': current_question.get('options', []) if "options" in current_question else None,
            'has_history': self.current_question_index in self.question_history,
            'answer': self.current_answer,
            'feedback': self.current_feedback
        }
        self.question_ready.emit(question_data)
    
    def process_answer(self, answer):
        """
        处理用户提交的答案
        
        Args:
            answer (str): 用户提交的答案
        """
        if not answer:
            showWarning(get_message("enter_answer_warning", self.lang))
            return
        
        # 设置当前答案
        self.current_answer = answer
        print(f"已设置当前答案: {answer}")
        
        # 获取当前问题
        if not self.current_questions or 'questions' not in self.current_questions:
            showWarning(get_message("no_questions", self.lang))
            return
        
        questions = self.current_questions['questions']
        if self.current_question_index >= len(questions):
            showWarning(get_message("question_index_error", self.lang))
            return
        
        current_question = questions[self.current_question_index]
        
        # 准备评估答案
        try:
            if hasattr(self.ai_handler, 'evaluate_answer'):
                # 使用单独线程评估答案，避免UI冻结
                self._evaluate_answer_in_thread(current_question, answer)
            else:
                showWarning(get_message("ai_handler_error", self.lang))
        except Exception as e:
            showWarning(f"{get_message('answer_eval_error', self.lang)}{str(e)}")
    
    def _evaluate_answer_in_thread(self, question, answer):
        """
        在单独线程中评估答案
        
        Args:
            question (dict): 问题数据
            answer (str): 用户答案
        """
        from ..workers.evaluate_answer_worker import EvaluateAnswerWorker
        
        # 创建工作线程
        self.thread = QThread()
        self.worker = EvaluateAnswerWorker(
            self.ai_handler, 
            question, 
            answer
        )
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.feedback_ready.connect(self.on_feedback_received)
        self.worker.error_occurred.connect(self.on_evaluate_error)
        
        # 启动线程
        self.thread.start()
    
    def on_feedback_received(self, feedback):
        """
        处理接收到的AI反馈
        
        Args:
            feedback (str): AI反馈内容
        """
        # 确保我们有有效的问题和答案
        if not self.current_question:
            print("警告：接收到反馈但current_question为空")
            return
            
        if not self.current_answer:
            print("警告：接收到反馈但current_answer为空")
            return
        
        # 设置反馈和掌握程度
        self.current_feedback = feedback
        
        # 从反馈中提取掌握程度
        if "得分：" in feedback:
            score_text = feedback.split("得分：")[1].split("\n")[0].strip()
            self.current_mastery = score_text
        elif "✓ 回答正确" in feedback:
            self.current_mastery = "100%"
        else:
            self.current_mastery = get_message("needs_review", self.lang) or "需要复习"
        
        print(f"已设置反馈和掌握程度：反馈长度={len(feedback)}, 掌握程度={self.current_mastery}")
        
        # 保存当前问题的答案和反馈到历史记录
        self.question_history[self.current_question_index] = {
            'answer': self.current_answer,
            'feedback': self.current_feedback,
            'mastery': self.current_mastery
        }
        
        # 发送反馈信号
        self.feedback_ready.emit(feedback)
    
    def on_evaluate_error(self, error_message):
        """
        处理评估过程中的错误
        
        Args:
            error_message (str): 错误信息
        """
        showWarning(f"{get_message('answer_eval_error', self.lang)}{error_message}")
        self.feedback_ready.emit(get_message("feedback_error", self.lang))
    
    def next_question(self):
        """处理进入下一题"""
        # 保存当前问题的followup面板内容
        self._save_current_followup_content()
        
        # 切换到下一题
        self.current_question_index += 1
        self.show_current_question()
        
        # 更新进度
        if self.question_set_id:
            update_question_set(self.question_set_id, self.current_question_index)
    
    def previous_question(self):
        """处理返回上一题"""
        # 保存当前问题的followup面板内容
        self._save_current_followup_content()
        
        # 切换到上一题
        self.current_question_index -= 1
        # 确保索引不小于0
        if self.current_question_index < 0:
            self.current_question_index = 0
        
        self.show_current_question()
        
        # 更新进度
        if self.question_set_id:
            update_question_set(self.question_set_id, self.current_question_index)
    
    def _save_current_followup_content(self):
        """保存当前问题的追加提问内容"""
        if hasattr(self.parent, 'followupPanel'):
            followup_content = self.parent.followupPanel.get_followup_content()
            if followup_content:  # 只有在有内容时才保存
                # 确保当前索引在历史记录中
                if self.current_question_index not in self.question_history:
                    self.question_history[self.current_question_index] = {
                        'answer': self.current_answer,
                        'feedback': self.current_feedback,
                        'mastery': self.current_mastery
                    }
                # 保存追问内容
                self.question_history[self.current_question_index]['followup_content'] = followup_content
    
    def save_to_anki(self, deck_id, include_follow_up=False, follow_up_content=""):
        """
        保存当前问答到Anki
        
        Args:
            deck_id: 牌组ID
            include_follow_up (bool): 是否包含追加提问内容
            follow_up_content (str): 追加提问内容
            
        Returns:
            bool: 是否保存成功
        """
        # 输出状态变量的值，用于调试
        print(f"当前问题: {bool(self.current_question)}")
        print(f"当前答案: {bool(self.current_answer)}")
        print(f"当前反馈: {bool(self.current_feedback)}")
        print(f"当前掌握度: {bool(self.current_mastery)}")
        
        if not all([self.current_question, self.current_answer, 
                   self.current_feedback, self.current_mastery]):
            showWarning(get_message("no_content_warning", self.lang))
            return False
            
        try:
            # 获取源内容
            source_content = self.current_source_content or ""
            
            if not source_content and hasattr(self.parent, 'contentEdit'):
                source_content = self.parent.contentEdit.toPlainText().strip()
            
            # 获取当前完整的问题文本，包括题号
            if self.current_questions and 'questions' in self.current_questions and self.current_question_index < len(self.current_questions['questions']):
                # 获取完整问题，包括题号
                question_number = get_message("question_number", self.lang).format(
                    current=self.current_question_index + 1,
                    total=len(self.current_questions['questions'])
                )
                # 拼接完整问题文本
                formatted_question = f"{question_number}\n\n{self.current_question}"
            else:
                # 使用当前问题文本
                formatted_question = self.current_question
            
            # 处理选择题格式
            if "选项：\n" in formatted_question:
                question_parts = formatted_question.split("选项：\n")
                question_text = question_parts[0].strip()
                options = question_parts[1].strip().split("\n")
                
                formatted_options = "<br><div style='margin-left: 20px;'>"
                for option in options:
                    if option.strip():
                        formatted_options += f"• {option.strip()}<br>"
                formatted_options += "</div>"
                
                formatted_question = f"{question_text}<br>{formatted_options}"
            
            # 获取标签
            config = mw.addonManager.getConfig(__name__)
            tags = config.get('deck', {}).get('tags', ['feynman-learning'])
            
            # 处理追加提问内容
            ai_feedback = self.current_feedback
            if include_follow_up and follow_up_content:
                ai_feedback += follow_up_content
            
            # 创建笔记
            note = create_feynman_note(
                deck_id=deck_id,
                content=source_content,
                question=formatted_question,
                correct_answer="",
                my_answer=self.current_answer,
                ai_feedback=ai_feedback,
                mastery=self.current_mastery,
                tags=tags
            )
            
            showInfo(get_message("save_success", self.lang))
            return True
            
        except Exception as e:
            showWarning(f"{get_message('save_error', self.lang)}{str(e)}")
            return False
    
    def make_cloze(self, deck_id, include_follow_up=False, follow_up_history=None):
        """
        将当前问题转化为填空卡
        
        Args:
            deck_id: 牌组ID
            include_follow_up (bool): 是否包含追加提问内容
            follow_up_history (list): 追加提问历史记录
            
        Returns:
            bool: 是否操作成功
        """
        # 获取当前问题的原文段落
        source_content = self.current_source_content or ""
        
        if not source_content and hasattr(self.parent, 'contentEdit'):
            source_content = self.parent.contentEdit.toPlainText().strip()
        
        dialog = ClozeDialog(
            self.parent,
            content=source_content,
            question=self.current_question,
            answer=self.current_answer,
            feedback=self.current_feedback
        )

        # 连接保存请求信号
        dialog.saveRequested.connect(lambda: self._handle_cloze_save_request(
            dialog, deck_id, include_follow_up, follow_up_history
        ))

        # 显示对话框（非阻塞模式）
        dialog.show()
        return True

    def _handle_cloze_save_request(self, dialog, deck_id, include_follow_up, follow_up_history):
        """
        处理填空卡保存请求

        Args:
            dialog: ClozeDialog实例
            deck_id: 牌组ID
            include_follow_up (bool): 是否包含追加提问内容
            follow_up_history (list): 追加提问历史记录
        """
        try:
            # 调用对话框的保存方法
            success = dialog.save_cloze_card(
                deck_id,
                include_follow_up=include_follow_up,
                follow_up_history=follow_up_history
            )

            if success:
                # 保存成功，但不关闭对话框，用户可以继续编辑
                pass

        except Exception as e:
            showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")