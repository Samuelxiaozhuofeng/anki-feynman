"""
追加提问面板组件
提供追加提问功能，显示历史对话，支持右键菜单操作
"""
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning, tooltip
import re

from ..styles.anki_style import apply_anki_style
from ..dialogs.cloze_dialog import ClozeDialog
from ...utils import create_feynman_note
from ...lang.messages import get_message, get_default_lang
from ..workers.followup_worker import FollowUpQuestionWorker

# 导入markdown处理
MARKDOWN_AVAILABLE = False
markdown2 = None
markdown = None

try:
    import markdown2
    MARKDOWN_AVAILABLE = True
except (ImportError, PermissionError, OSError) as e:
    try:
        import markdown
        MARKDOWN_AVAILABLE = True
    except (ImportError, PermissionError, OSError) as e:
        MARKDOWN_AVAILABLE = False


class MarkdownRenderer:
    """Markdown渲染器，将Markdown文本转换为HTML"""

    @staticmethod
    def markdown_to_html(text):
        """将Markdown文本转换为HTML"""
        if not MARKDOWN_AVAILABLE or not text:
            return MarkdownRenderer.simple_markdown_to_html(text)

        try:
            # 尝试使用markdown2
            if markdown2 is not None:
                html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
            elif markdown is not None:
                # 使用markdown
                md = markdown.Markdown(extensions=['extra', 'codehilite'])
                html = md.convert(text)
            else:
                return MarkdownRenderer.simple_markdown_to_html(text)

            # 添加基本样式
            styled_html = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        font-size: 14px; line-height: 1.6; color: #333;">
                {html}
            </div>
            """
            return styled_html

        except Exception as e:
            print(f"Markdown渲染失败: {e}")
            return MarkdownRenderer.simple_markdown_to_html(text)

    @staticmethod
    def simple_markdown_to_html(text):
        """简单的Markdown到HTML转换（备用方案）"""
        if not text:
            return ""

        html = text

        # 处理粗体 **text** 或 __text__
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)

        # 处理斜体 *text* 或 _text_
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)

        # 处理代码 `code`
        html = re.sub(r'`(.*?)`', r'<code style="background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px;">\1</code>', html)

        # 处理标题
        html = re.sub(r'^### (.*?)$', r'<h3 style="margin: 15px 0 10px 0; color: #2c3e50;">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2 style="margin: 20px 0 15px 0; color: #2c3e50;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1 style="margin: 25px 0 20px 0; color: #2c3e50;">\1</h1>', html, flags=re.MULTILINE)

        # 处理列表项 - 开头的
        lines = html.split('\n')
        in_list = False
        result_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    result_lines.append('<ul style="margin: 10px 0; padding-left: 20px;">')
                    in_list = True
                content = stripped[2:].strip()
                result_lines.append(f'<li style="margin: 5px 0;">{content}</li>')
            elif stripped.startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
                if not in_list:
                    result_lines.append('<ol style="margin: 10px 0; padding-left: 20px;">')
                    in_list = True
                content = re.sub(r'^\d+\.\s*', '', stripped)
                result_lines.append(f'<li style="margin: 5px 0;">{content}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>' if any(l.strip().startswith(('-', '*')) for l in lines if l.strip()) else '</ol>')
                    in_list = False
                if stripped:
                    result_lines.append(f'<p style="margin: 8px 0;">{line}</p>')
                else:
                    result_lines.append('<br>')

        if in_list:
            result_lines.append('</ul>')

        html = '\n'.join(result_lines)

        # 处理分隔线
        html = re.sub(r'^---+$', '<hr style="margin: 15px 0; border: none; border-top: 1px solid #ddd;">', html, flags=re.MULTILINE)

        # 添加基本样式容器
        styled_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    font-size: 14px; line-height: 1.6; color: #333;">
            {html}
        </div>
        """

        return styled_html


class FollowUpPanel(QWidget):
    """追加提问面板"""
    
    def __init__(self, parent=None, ai_handler=None, followup_model=None):
        """
        初始化追加提问面板
        
        Args:
            parent: 父窗口
            ai_handler: AI处理器实例
            followup_model: 追加提问使用的模型，如果为None则使用默认模型
        """
        super().__init__(parent)
        self.parent = parent
        self.ai_handler = ai_handler
        self.followup_model = followup_model
        self.lang = get_default_lang()
        self.follow_up_history = []
        self.current_follow_up_question = ""
        self.thread = None
        self.worker = None
        
        self.setup_ui()
        self.setup_connections()
        self.setup_context_menu()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置面板
        self.followUpGroupBox = QGroupBox(get_message("follow_up_group", self.lang))
        self.followUpGroupBox.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        followUpLayout = QVBoxLayout()
        
        # 历史记录显示区域 - 使用QTextBrowser支持HTML渲染
        self.historyArea = QTextBrowser()
        self.historyArea.setReadOnly(True)
        self.historyArea.setPlaceholderText(get_message("follow_up_history_placeholder", self.lang))
        self.historyArea.setMinimumHeight(400)
        self.historyArea.setOpenExternalLinks(False)  # 禁用外部链接
        self.historyArea.setOpenLinks(False)  # 禁用所有链接
        followUpLayout.addWidget(self.historyArea)
        
        # 包含到卡片的选项
        self.includeFollowUpCheckBox = QCheckBox(get_message("include_followup_in_card", self.lang) or "将追加提问内容包含到卡片中")
        self.includeFollowUpCheckBox.setChecked(True)  # 默认选中
        followUpLayout.addWidget(self.includeFollowUpCheckBox)
        
        # 输入区域
        inputLayout = QHBoxLayout()
        self.followUpEdit = QLineEdit()
        self.followUpEdit.setPlaceholderText(get_message("follow_up_input_placeholder", self.lang))
        self.askButton = QPushButton(get_message("ask_question", self.lang))
        self.askButton.setEnabled(False)
        inputLayout.addWidget(self.followUpEdit)
        inputLayout.addWidget(self.askButton)
        followUpLayout.addLayout(inputLayout)
        
        self.followUpGroupBox.setLayout(followUpLayout)
        layout.addWidget(self.followUpGroupBox)
        
        # 进度条
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.hide()
        layout.addWidget(self.progressBar)
    
    def setup_connections(self):
        """设置信号连接"""
        self.askButton.clicked.connect(self.on_ask_clicked)
        self.followUpEdit.returnPressed.connect(self.on_ask_clicked)  # 支持回车提交
        self.followUpEdit.textChanged.connect(self.on_follow_up_changed)
    
    def setup_context_menu(self):
        """设置右键菜单"""
        self.history_context_menu = QMenu(self)
        
        make_qa_action = QAction(get_message("make_qa", self.lang), self)
        make_qa_action.triggered.connect(self.make_qa_card)
        self.history_context_menu.addAction(make_qa_action)
        
        make_cloze_action = QAction(get_message("make_cloze_from_selection", self.lang), self)
        make_cloze_action.triggered.connect(self.make_cloze_from_selection)
        self.history_context_menu.addAction(make_cloze_action)
        
        self.historyArea.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.historyArea.customContextMenuRequested.connect(self.show_context_menu)
    
    def on_follow_up_changed(self):
        """追加问题输入变化事件"""
        # 只有当有内容输入时才启用提问按钮
        self.askButton.setEnabled(bool(self.followUpEdit.text().strip()))
    
    def on_ask_clicked(self):
        """处理追加提问"""
        question = self.followUpEdit.text().strip()
        if not question:
            return
            
        try:
            # 显示进度条并禁用界面
            self.progressBar.show()
            self.askButton.setEnabled(False)
            self.followUpEdit.setEnabled(False)

            # 获取当前问题的相关信息
            context = self._get_context_info(question)

            # 创建新线程处理提问
            self.thread = QThread()
            self.worker = FollowUpQuestionWorker(
                self.ai_handler,
                context,
                self.followup_model
            )
            self.worker.moveToThread(self.thread)

            # 连接信号
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.response_ready.connect(self.on_response_received)
            self.worker.error_occurred.connect(self.on_ask_error)

            # 保存当前问题以供后续使用
            self.current_follow_up_question = question

            # 启动线程
            self.thread.start()

        except Exception as e:
            self.on_ask_error(str(e))
    
    def _get_context_info(self, question):
        """获取上下文信息"""
        # 从父组件获取当前问题的信息
        source_content = ""
        original_question = ""
        user_answer = ""
        ai_feedback = ""
        
        # 检查父组件是否有controller属性，然后从controller获取信息
        if hasattr(self.parent, 'controller'):
            controller = self.parent.controller
            
            # 获取source_content
            if hasattr(controller, 'current_questions') and hasattr(controller, 'current_question_index'):
                if controller.current_questions and 'questions' in controller.current_questions:
                    questions = controller.current_questions['questions']
                    if 0 <= controller.current_question_index < len(questions):
                        current_question = questions[controller.current_question_index]
                        source_content = current_question.get('source_content', '')
            
            # 获取其他属性
            if hasattr(controller, 'current_question'):
                original_question = controller.current_question
                
            if hasattr(controller, 'current_answer'):
                user_answer = controller.current_answer
                
            if hasattr(controller, 'current_feedback'):
                ai_feedback = controller.current_feedback
        
        # 调试输出，查看获取到的信息
        print(f"追问上下文: 问题长度={len(original_question)}，内容长度={len(source_content)}，答案长度={len(user_answer)}，反馈长度={len(ai_feedback)}")
        
        return {
            "original_question": original_question,
            "source_content": source_content,
            "user_answer": user_answer,
            "ai_feedback": ai_feedback,
            "follow_up_question": question,
            "history": self.follow_up_history
        }
    
    def on_response_received(self, response):
        """处理AI回答"""
        try:
            # 添加到对话历史
            self.follow_up_history.append({
                "question": self.current_follow_up_question,
                "answer": response
            })
            
            # 更新显示
            self.update_history_display()
            
            # 清空输入框
            self.followUpEdit.clear()
            
        finally:
            # 恢复界面状态
            self.progressBar.hide()
            self.askButton.setEnabled(True)
            self.followUpEdit.setEnabled(True)
    
    def on_ask_error(self, error_message):
        """处理提问错误"""
        showWarning(f"{get_message('follow_up_error', self.lang)}{error_message}")
        self.progressBar.hide()
        self.askButton.setEnabled(True)
        self.followUpEdit.setEnabled(True)
    
    def update_history_display(self):
        """更新对话历史显示"""
        if not self.follow_up_history:
            self.historyArea.clear()
            return

        history_html = ""
        for i, item in enumerate(self.follow_up_history):
            # 问题部分
            question_prefix = get_message('question_prefix', self.lang)
            question_html = f"""
            <div style="margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px;">
                <div style="font-weight: bold; color: #007bff; margin-bottom: 8px;">{question_prefix}</div>
                <div style="color: #495057;">{item['question']}</div>
            </div>
            """

            # 答案部分 - 使用Markdown渲染
            answer_prefix = get_message('answer_prefix_qa', self.lang)
            answer_content = MarkdownRenderer.markdown_to_html(item['answer'])
            answer_html = f"""
            <div style="margin-bottom: 20px; padding: 15px; background-color: #ffffff; border: 1px solid #e9ecef; border-radius: 4px;">
                <div style="font-weight: bold; color: #28a745; margin-bottom: 10px;">{answer_prefix}</div>
                <div>{answer_content}</div>
            </div>
            """

            history_html += question_html + answer_html

            # 添加分隔线（除了最后一个）
            if i < len(self.follow_up_history) - 1:
                history_html += '<hr style="margin: 20px 0; border: none; border-top: 1px solid #dee2e6;">'

        # 设置HTML内容
        self.historyArea.setHtml(history_html)

        # 滚动到底部
        self.historyArea.verticalScrollBar().setValue(
            self.historyArea.verticalScrollBar().maximum()
        )
    
    def clear(self):
        """清空追加提问区域"""
        self.followUpEdit.clear()
        self.historyArea.clear()
        self.follow_up_history = []
        self.askButton.setEnabled(False)
        self.current_follow_up_question = ""
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        # 只有在有选中文本时才显示菜单
        cursor = self.historyArea.textCursor()
        if cursor.hasSelection():
            self.history_context_menu.exec(self.historyArea.mapToGlobal(position))
    
    def make_qa_card(self):
        """从选中文本制作问答题"""
        cursor = self.historyArea.textCursor()
        selected_text = cursor.selectedText().strip()
        if not selected_text:
            return

        # 清理HTML标签（如果有的话）
        import re
        selected_text = re.sub(r'<[^>]+>', '', selected_text)
            
        try:
            # 获取当前牌组
            deck_id = None
            if hasattr(self.parent, 'parent') and hasattr(self.parent.parent(), 'deckComboBox'):
                deck_id = self.parent.parent().deckComboBox.currentData()
            else:
                showWarning(get_message("no_deck_selected", self.lang))
                return
                
            config = mw.addonManager.getConfig(__name__)
            tags = config.get('deck', {}).get('tags', ['feynman-learning'])
            
            note = create_feynman_note(
                deck_id=deck_id,
                content=selected_text,
                question=f"{get_message('please_explain', self.lang)}{selected_text}",
                correct_answer="",
                my_answer="",
                ai_feedback="",
                mastery=get_message("needs_review", self.lang),
                tags=tags
            )
            
            showInfo(get_message("qa_create_success", self.lang))
            
        except Exception as e:
            showWarning(f"{get_message('qa_create_error', self.lang)}{str(e)}")
    
    def make_cloze_from_selection(self):
        """从选中文本制作填空卡"""
        cursor = self.historyArea.textCursor()
        selected_text = cursor.selectedText().strip()
        if not selected_text:
            return

        # 清理HTML标签（如果有的话）
        import re
        selected_text = re.sub(r'<[^>]+>', '', selected_text)
            
        dialog = ClozeDialog(
            self,
            content=selected_text,
            question="",
            answer="",
            feedback=""
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                # 获取当前牌组
                deck_id = None
                if hasattr(self.parent, 'parent') and hasattr(self.parent.parent(), 'deckComboBox'):
                    deck_id = self.parent.parent().deckComboBox.currentData()
                else:
                    showWarning(get_message("no_deck_selected", self.lang))
                    return
                
                # 保存填空卡
                dialog.save_cloze_card(deck_id, 
                                       include_follow_up=self.includeFollowUpCheckBox.isChecked(),
                                       follow_up_history=self.follow_up_history)
                
            except Exception as e:
                showWarning(f"{get_message('cloze_create_error', self.lang)}{str(e)}")
    
    def get_followup_content_html(self):
        """
        获取格式化的追加提问内容HTML

        Returns:
            str: 格式化的HTML内容，如果没有历史记录则返回空字符串
        """
        if not self.follow_up_history or not self.includeFollowUpCheckBox.isChecked():
            return ""

        followup_content = f'<div style="border-top: 1px solid #ccc; margin-top: 15px; padding-top: 15px;">'
        followup_content += f'<div style="font-weight: bold; color: #2196F3; margin-bottom: 10px;">{get_message("followup_content_header", self.lang)}</div>'

        for item in self.follow_up_history:
            followup_content += '<div style="margin-bottom: 15px;">'
            followup_content += f'<div style="color: #666; margin-bottom: 5px; font-weight: bold;">{get_message("question_prefix", self.lang)}{item["question"]}</div>'
            # 对答案内容进行Markdown渲染
            answer_html = MarkdownRenderer.markdown_to_html(item["answer"])
            followup_content += f'<div style="margin-left: 20px; color: #333;">{get_message("answer_prefix_qa", self.lang)}<div style="margin-top: 5px;">{answer_html}</div></div>'
            followup_content += '</div>'

        followup_content += '</div>'
        return followup_content
    
    def get_followup_content_text(self):
        """
        获取格式化的追加提问内容文本
        
        Returns:
            str: 格式化的文本内容，如果没有历史记录则返回空字符串
        """
        if not self.follow_up_history or not self.includeFollowUpCheckBox.isChecked():
            return ""
            
        followup_content = f"\n\n{get_message('followup_content_header', self.lang)}\n"
        for item in self.follow_up_history:
            followup_content += f"\n{get_message('question_prefix', self.lang)}{item['question']}\n"
            followup_content += f"{get_message('answer_prefix_qa', self.lang)}{item['answer']}\n"
            
        return followup_content
    
    def has_followup_content(self):
        """
        检查是否有追加提问内容需要包含
        
        Returns:
            bool: 是否有需要包含的内容
        """
        return bool(self.follow_up_history) and self.includeFollowUpCheckBox.isChecked()

    def get_followup_content(self):
        """
        获取完整的追问历史记录，用于保存和恢复状态
        
        Returns:
            dict: 包含历史记录和设置的字典
        """
        if not self.follow_up_history:
            return None
        
        return {
            'history': self.follow_up_history,
            'include_checked': self.includeFollowUpCheckBox.isChecked()
        }

    def restore_followup_content(self, followup_content):
        """
        恢复追问历史记录和设置
        
        Args:
            followup_content (dict): 包含历史记录和设置的字典
        """
        # 先清空当前的历史记录
        self.clear()
        
        if not followup_content:
            return
        
        self.follow_up_history = followup_content.get('history', [])
        self.includeFollowUpCheckBox.setChecked(followup_content.get('include_checked', True))
        
        # 更新历史显示
        if self.follow_up_history:
            self.update_history_display()