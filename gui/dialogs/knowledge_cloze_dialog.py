"""
知识卡片填空对话框模块
专门用于知识卡片的填空卡制作
"""
from aqt.qt import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton, pyqtSignal
from aqt.utils import showWarning
from ...lang.messages import get_message, get_default_lang


class KnowledgeClozeDialog(QDialog):
    """知识卡片填空对话框（简化版）"""
    
    # 自定义信号
    saveRequested = pyqtSignal()

    def __init__(self, text, parent=None):
        """
        初始化填空对话框
        
        Args:
            text: 要编辑的文本内容
            parent: 父窗口
        """
        super().__init__(parent)
        self.text = text
        self.lang = get_default_lang()
        self.cloze_count = 1
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("cloze_dialog_title", self.lang))
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 说明文本
        instructions = QLabel(get_message("cloze_instructions", self.lang))
        layout.addWidget(instructions)
        
        # 编辑区域
        self.edit_area = QTextEdit()
        self.edit_area.setText(self.text)
        layout.addWidget(self.edit_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_cloze_btn = QPushButton(get_message("add_cloze_marker", self.lang))
        self.save_btn = QPushButton(get_message("save_cloze", self.lang))
        
        button_layout.addWidget(self.add_cloze_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.add_cloze_btn.clicked.connect(self._add_cloze)
        self.save_btn.clicked.connect(self._on_save_clicked)
        
    def _add_cloze(self):
        """添加填空标记"""
        cursor = self.edit_area.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            showWarning(get_message("select_cloze_text", self.lang))
            return
            
        # 添加填空标记，使用双大括号来转义
        cloze_text = f"{{{{c{self.cloze_count}::{selected_text}}}}}"
        cursor.insertText(cloze_text)
        self.cloze_count += 1

    def _on_save_clicked(self):
        """处理保存按钮点击事件"""
        # 发出保存请求信号，不关闭对话框
        self.saveRequested.emit()
        
    def get_cloze_text(self):
        """
        获取编辑后的填空文本
        
        Returns:
            str: 填空文本内容
        """
        return self.edit_area.toPlainText()

