from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning
import json
import uuid
from ..lang.messages import get_message, get_default_lang

class PromptTemplateManager(QDialog):
    """提示词模板管理窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_default_lang()
        self.setWindowTitle(get_message("template_manager_title", self.lang))
        self.resize(800, 500)
        self.setup_ui()
        self.load_templates()
        
        # 初始状态
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.template_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel(get_message("template_manager_title", self.lang))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # 说明文本
        description = QLabel(get_message("template_manager_description", self.lang))
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 模板列表
        self.template_list = QListWidget()
        layout.addWidget(self.template_list)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton(get_message("add_template", self.lang))
        self.edit_button = QPushButton(get_message("edit_template", self.lang))
        self.delete_button = QPushButton(get_message("delete_template", self.lang))
        self.close_button = QPushButton(get_message("close", self.lang))
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.add_button.clicked.connect(self.on_add_template)
        self.edit_button.clicked.connect(self.on_edit_template)
        self.delete_button.clicked.connect(self.on_delete_template)
        self.close_button.clicked.connect(self.accept)
        self.template_list.itemDoubleClicked.connect(self.on_edit_template)
        
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        
        config = mw.addonManager.getConfig(__name__)
        templates = config.get('prompt_templates', [])
        
        if not templates:
            # 如果没有模板，添加默认的占位符
            item = QListWidgetItem(get_message("no_templates_placeholder", self.lang))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.template_list.addItem(item)
        else:
            for template in templates:
                template_name = template.get('name', '')
                if template_name:
                    item = QListWidgetItem(template_name)
                    item.setData(Qt.ItemDataRole.UserRole, template.get('id', ''))
                    self.template_list.addItem(item)
                    
    def on_selection_changed(self):
        """选择变更事件处理"""
        selected_items = self.template_list.selectedItems()
        has_selection = len(selected_items) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def on_add_template(self):
        """添加模板"""
        editor = PromptTemplateEditor(parent=self)
        if editor.exec():
            self.load_templates()
            
    def on_edit_template(self):
        """编辑模板"""
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            return
            
        template_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        editor = PromptTemplateEditor(template_id=template_id, parent=self)
        if editor.exec():
            self.load_templates()
            
    def on_delete_template(self):
        """删除模板"""
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            return
            
        template_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        template_name = selected_items[0].text()
        
        # 确认删除
        confirm = QMessageBox.question(
            self,
            get_message("confirm_delete_title", self.lang),
            get_message("confirm_delete_template", self.lang).format(template_name=template_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # 删除模板
            config = mw.addonManager.getConfig(__name__)
            templates = config.get('prompt_templates', [])
            templates = [t for t in templates if t.get('id', '') != template_id]
            config['prompt_templates'] = templates
            mw.addonManager.writeConfig(__name__, config)
            self.load_templates()


class PromptTemplateEditor(QDialog):
    """提示词模板编辑器"""
    
    def __init__(self, template_id=None, parent=None):
        super().__init__(parent)
        self.lang = get_default_lang()
        self.template_id = template_id
        
        if template_id:
            self.setWindowTitle(get_message("edit_template_title", self.lang))
        else:
            self.setWindowTitle(get_message("add_template_title", self.lang))
            
        self.resize(800, 600)
        self.setup_ui()
        
        if template_id:
            self.load_template(template_id)
        else:
            self.load_default_template()
            
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        
        # 模板名称
        name_layout = QHBoxLayout()
        name_label = QLabel(get_message("template_name", self.lang))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(get_message("template_name_placeholder", self.lang))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 说明文本
        description = QLabel(get_message("template_editor_description", self.lang))
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # 模板内容
        content_label = QLabel(get_message("template_content", self.lang))
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText(get_message("template_content_placeholder", self.lang))
        layout.addWidget(content_label)
        layout.addWidget(self.content_edit)
        
        # 选项卡：示例和说明
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # 示例选项卡
        example_widget = QWidget()
        example_layout = QVBoxLayout(example_widget)
        example_text = QLabel(get_message("template_example_description", self.lang))
        example_text.setWordWrap(True)
        example_layout.addWidget(example_text)
        
        self.example_content = QPlainTextEdit()
        self.example_content.setReadOnly(True)
        example_layout.addWidget(self.example_content)
        
        tabs.addTab(example_widget, get_message("example_tab", self.lang))
        
        # 说明选项卡
        help_widget = QWidget()
        help_layout = QVBoxLayout(help_widget)
        help_text = QLabel(get_message("template_help_description", self.lang))
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        tips_text = QTextEdit()
        tips_text.setReadOnly(True)
        tips_text.setHtml(get_message("template_help_tips", self.lang))
        help_layout.addWidget(tips_text)
        
        tabs.addTab(help_widget, get_message("help_tab", self.lang))
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.save_button = QPushButton(get_message("save_template", self.lang))
        self.cancel_button = QPushButton(get_message("cancel", self.lang))
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.save_button.clicked.connect(self.on_save)
        self.cancel_button.clicked.connect(self.reject)
        
        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
    def load_default_template(self):
        """加载默认模板"""
        self.example_content.setPlainText("""请基于以下内容设计5道关于量子力学的选择题，确保每个题目覆盖不同的概念，
选项要有足够的干扰性，使学生必须真正理解概念才能选对。
每个题目都应包含一个简短的解释，说明为什么正确答案是正确的，以及其他选项为什么不正确。
避免太简单的记忆性问题，我想要能测试深层理解的问题。""")
        
    def load_template(self, template_id):
        """加载现有模板"""
        config = mw.addonManager.getConfig(__name__)
        templates = config.get('prompt_templates', [])
        
        template = next((t for t in templates if t.get('id', '') == template_id), None)
        if template:
            self.name_edit.setText(template.get('name', ''))
            self.content_edit.setPlainText(template.get('content', ''))
        
    def on_save(self):
        """保存模板"""
        name = self.name_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not name:
            showWarning(get_message("template_name_required", self.lang))
            return
            
        if not content:
            showWarning(get_message("template_content_required", self.lang))
            return
            
        config = mw.addonManager.getConfig(__name__)
        templates = config.get('prompt_templates', [])
        
        if self.template_id:
            # 更新现有模板
            template = next((t for t in templates if t.get('id', '') == self.template_id), None)
            if template:
                template['name'] = name
                template['content'] = content
        else:
            # 创建新模板
            self.template_id = str(uuid.uuid4())
            templates.append({
                'id': self.template_id,
                'name': name,
                'content': content,
                'type': 'choice'  # 目前仅支持选择题类型
            })
            
        config['prompt_templates'] = templates
        mw.addonManager.writeConfig(__name__, config)
        self.accept() 