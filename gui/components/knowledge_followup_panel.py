"""
知识卡片追问面板组件
提供AI追问功能和历史记录显示
"""
from aqt.qt import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                     QTextEdit, QLineEdit, QPushButton, QProgressBar,
                     QMenu, QThread, pyqtSignal)
from PyQt6.QtCore import Qt
from aqt import mw
from aqt.utils import showInfo, showWarning

from ...lang.messages import get_message, get_default_lang
from ..workers.knowledge_followup_worker import FollowUpQuestionWorker


class KnowledgeFollowUpPanel(QWidget):
    """知识卡片追问面板组件"""
    
    # 信号定义
    history_updated = pyqtSignal(list)  # 历史记录更新信号
    create_qa_card = pyqtSignal(str)  # 创建问答卡信号
    create_cloze_card = pyqtSignal(str)  # 创建填空卡信号
    
    def __init__(self, parent=None):
        """
        初始化追问面板
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.lang = get_default_lang()
        self.follow_up_history = []
        self.ai_handler = None
        self.followup_model = None
        self.current_followup_question = ""
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 追问区域组
        followup_group = QGroupBox(get_message("followup_area", self.lang))
        followup_layout = QVBoxLayout()
        
        # 追问历史显示区域
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(100)
        followup_layout.addWidget(self.history_text)
        
        # 追问输入区域
        input_layout = QHBoxLayout()
        self.followup_input = QLineEdit()
        self.followup_input.setPlaceholderText(get_message("followup_placeholder", self.lang))
        self.send_button = QPushButton(get_message("send_followup", self.lang))
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        input_layout.addWidget(self.followup_input)
        input_layout.addWidget(self.send_button)
        followup_layout.addLayout(input_layout)
        followup_layout.addWidget(self.progress_bar)
        
        followup_group.setLayout(followup_layout)
        layout.addWidget(followup_group)
        
        # 连接信号
        self.send_button.clicked.connect(self._handle_followup_question)
        self.followup_input.returnPressed.connect(self._handle_followup_question)
        
        # 设置历史区域的右键菜单
        self.history_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_text.customContextMenuRequested.connect(self._show_history_context_menu)
        
    def set_ai_handler(self, ai_handler):
        """
        设置AI处理器
        
        Args:
            ai_handler: AI处理器实例
        """
        self.ai_handler = ai_handler
        
    def set_followup_model(self, followup_model):
        """
        设置追问使用的模型
        
        Args:
            followup_model: 模型信息
        """
        self.followup_model = followup_model
        
    def _handle_followup_question(self):
        """处理追问请求"""
        question = self.followup_input.text().strip()
        if not question:
            return

        # 确保有AI处理器
        if not self.ai_handler:
            showWarning(get_message("ai_handler_not_set", self.lang))
            return

        # 禁用输入和按钮
        self.followup_input.setEnabled(False)
        self.send_button.setEnabled(False)

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 设置为不确定模式

        # 保存当前问题
        self.current_followup_question = question

        # 调用可重写的方法来发送请求（由父窗口重写以提供上下文）
        if hasattr(self, '_send_followup_request') and callable(self._send_followup_request):
            self._send_followup_request(question)
        else:
            # 默认行为：显示警告
            showWarning("追问功能未正确初始化，请联系开发者")
            self.followup_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.progress_bar.setVisible(False)
        
    def send_followup_with_context(self, context):
        """
        使用给定的上下文发送追问请求

        Args:
            context: 上下文信息字典
        """
        # 创建工作线程
        self.thread = QThread()
        self.worker = FollowUpQuestionWorker(
            self.ai_handler,
            context,
            self.followup_model
        )

        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.response_ready.connect(self._handle_ai_response)
        self.worker.error_occurred.connect(self._handle_ai_error)

        # 启动线程
        self.thread.start()

    def _handle_ai_response(self, response):
        """处理AI响应"""
        # 添加到历史记录
        self.follow_up_history.append({
            "question": self.current_followup_question,
            "answer": response
        })

        # 更新显示
        self._update_history_display()

        # 清空输入框并恢复界面
        self.followup_input.clear()
        self.followup_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)

        # 发出历史更新信号
        self.history_updated.emit(self.follow_up_history)

    def _handle_ai_error(self, error_msg):
        """处理AI错误"""
        showWarning(error_msg)

        # 恢复界面
        self.followup_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def _update_history_display(self):
        """更新历史记录显示"""
        history_text = ""
        for item in self.follow_up_history:
            history_text += f"Q: {item['question']}\n"
            history_text += f"A: {item['answer']}\n\n"
        self.history_text.setText(history_text)

    def _show_history_context_menu(self, pos):
        """显示历史记录的右键菜单"""
        menu = QMenu(self)
        make_qa_action = menu.addAction(get_message("make_qa_card", self.lang))
        make_cloze_action = menu.addAction(get_message("make_cloze_card", self.lang))

        # 获取选中的文本
        cursor = self.history_text.textCursor()
        selected_text = cursor.selectedText()

        # 只有在有选中文本时才启用菜单项
        make_qa_action.setEnabled(bool(selected_text))
        make_cloze_action.setEnabled(bool(selected_text))

        # 连接动作信号
        make_qa_action.triggered.connect(lambda: self.create_qa_card.emit(selected_text))
        make_cloze_action.triggered.connect(lambda: self.create_cloze_card.emit(selected_text))

        # 显示菜单
        menu.exec(self.history_text.mapToGlobal(pos))

    def clear_history(self):
        """清空历史记录"""
        self.follow_up_history = []
        self.history_text.clear()

    def get_history(self):
        """
        获取追问历史记录

        Returns:
            list: 历史记录列表
        """
        return self.follow_up_history

    def format_history_for_card(self):
        """
        格式化历史记录用于保存到卡片

        Returns:
            str: 格式化后的历史记录文本
        """
        formatted = "AI解析与追问记录：\n\n"
        for item in self.follow_up_history:
            formatted += f"问：{item['question']}\n"
            formatted += f"答：{item['answer']}\n\n"
        return formatted

