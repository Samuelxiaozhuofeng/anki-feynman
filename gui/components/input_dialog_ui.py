"""
输入对话框UI组件
"""
from aqt.qt import *
from aqt import mw
from ...lang.messages import get_message

class InputDialogUI:
    """输入对话框UI组件类，负责构建UI和设置样式"""
    
    def __init__(self, dialog, lang):
        """
        初始化UI组件
        
        参数:
        dialog -- 持有对话框的引用
        lang -- 当前语言
        """
        self.dialog = dialog
        self.lang = lang
        
        # UI元素引用
        self.titleLabel = None
        self.contentEdit = None
        self.deckLabel = None
        self.deckComboBox = None
        self.questionTypeLabel = None
        self.questionTypeComboBox = None
        self.templateContainer = None
        self.templateLabel = None
        self.templateComboBox = None
        self.manageTemplateButton = None
        self.languageLabel = None
        self.languageComboBox = None
        self.numQuestionsLabel = None
        self.numQuestionsSpinBox = None
        self.modelLabel = None
        self.modelComboBox = None
        self.followUpModelLabel = None
        self.followUpModelComboBox = None
        self.generateButton = None
        self.progressBar = None
        self.questionSetsButton = None
        
        # 窗口引用
        self.question_sets_dialog = None
        
        # 设置UI
        self.setup_ui()
        
    def setup_ui(self):
        """设置对话框UI"""
        # 创建基本UI元素
        self.dialog.setWindowTitle(get_message("input_window_title", self.lang))
        self.dialog.resize(800, 600)
        
        layout = QVBoxLayout(self.dialog)
        
        # 创建顶部工具栏
        toolbarLayout = QHBoxLayout()
        
        # 添加题集按钮
        self.questionSetsButton = QPushButton("题集")
        toolbarLayout.addWidget(self.questionSetsButton)

        # 添加PDF导入按钮
        self.pdfImportButton = QPushButton(get_message("pdf_import", self.lang))
        toolbarLayout.addWidget(self.pdfImportButton)

        # 添加PDF库按钮
        self.pdfLibraryButton = QPushButton(get_message("pdf_library", self.lang))
        toolbarLayout.addWidget(self.pdfLibraryButton)

        # 右侧添加填充空间
        toolbarLayout.addStretch()
        
        # 将工具栏添加到主布局
        layout.addLayout(toolbarLayout)
        
        # 标题
        self.titleLabel = QLabel(get_message("input_title", self.lang))
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.titleLabel.font()
        font.setPointSize(12)
        font.setBold(True)
        self.titleLabel.setFont(font)
        layout.addWidget(self.titleLabel)
        
        # 文本输入区域
        self.contentEdit = QPlainTextEdit()
        self.contentEdit.setPlaceholderText(get_message("input_placeholder", self.lang))
        layout.addWidget(self.contentEdit)
        
        # 牌组选择和问题类型
        optionsLayout = QHBoxLayout()
        
        self.deckLabel = QLabel(get_message("select_deck", self.lang))
        self.deckComboBox = QComboBox()
        optionsLayout.addWidget(self.deckLabel)
        optionsLayout.addWidget(self.deckComboBox)
        
        optionsLayout.addStretch()
        
        self.questionTypeLabel = QLabel(get_message("question_type", self.lang))
        self.questionTypeComboBox = QComboBox()
        self.questionTypeComboBox.addItems([
            get_message("question_type_choice", self.lang),
            get_message("question_type_qa", self.lang),
            get_message("question_type_knowledge", self.lang),
            get_message("question_type_language_learning", self.lang),
            get_message("question_type_custom", self.lang)  # 添加自定义选项
        ])
        optionsLayout.addWidget(self.questionTypeLabel)
        optionsLayout.addWidget(self.questionTypeComboBox)
        
        layout.addLayout(optionsLayout)
        
        # 添加模板选择框，默认隐藏
        self.templateContainer = QWidget()
        templateLayout = QHBoxLayout(self.templateContainer)
        templateLayout.setContentsMargins(0, 0, 0, 0)
        
        self.templateLabel = QLabel(get_message("select_template", self.lang))
        self.templateComboBox = QComboBox()
        self.manageTemplateButton = QPushButton(get_message("manage_templates", self.lang))
        
        templateLayout.addWidget(self.templateLabel)
        templateLayout.addWidget(self.templateComboBox)
        templateLayout.addWidget(self.manageTemplateButton)
        
        layout.addWidget(self.templateContainer)
        self.templateContainer.hide()  # 初始隐藏
        
        # 语言选择
        languageLayout = QHBoxLayout()
        
        self.languageLabel = QLabel(get_message("select_language", self.lang))
        self.languageComboBox = QComboBox()
        self.languageComboBox.addItems([
            get_message("language_chinese", self.lang),
            get_message("language_spanish", self.lang),
            get_message("language_japanese", self.lang),
            get_message("language_custom", self.lang)
        ])
        
        languageLayout.addWidget(self.languageLabel)
        languageLayout.addWidget(self.languageComboBox)
        languageLayout.addStretch()
        
        layout.addLayout(languageLayout)
        
        # 高级选项
        advancedLayout = QHBoxLayout()
        
        self.numQuestionsLabel = QLabel(get_message("num_questions", self.lang))
        self.numQuestionsSpinBox = QSpinBox()
        self.numQuestionsSpinBox.setMinimum(1)
        self.numQuestionsSpinBox.setMaximum(100)
        self.numQuestionsSpinBox.setValue(5)
        advancedLayout.addWidget(self.numQuestionsLabel)
        advancedLayout.addWidget(self.numQuestionsSpinBox)
        
        advancedLayout.addStretch()
        
        self.modelLabel = QLabel(get_message("select_model", self.lang))
        self.modelComboBox = QComboBox()
        # 添加默认模型选项
        self.modelComboBox.addItem(get_message("default_model", self.lang) or "默认模型", "")
        advancedLayout.addWidget(self.modelLabel)
        advancedLayout.addWidget(self.modelComboBox)
        
        layout.addLayout(advancedLayout)
        
        # 追加提问模型选择
        followUpLayout = QHBoxLayout()
        
        followUpLayout.addStretch()
        
        self.followUpModelLabel = QLabel(get_message("select_followup_model", self.lang))
        self.followUpModelComboBox = QComboBox()
        # 添加默认追加提问模型选项
        self.followUpModelComboBox.addItem(get_message("default_model", self.lang) or "默认模型", "")
        followUpLayout.addWidget(self.followUpModelLabel)
        followUpLayout.addWidget(self.followUpModelComboBox)
        
        layout.addLayout(followUpLayout)
        
        # 生成按钮和进度条
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        
        self.generateButton = QPushButton(get_message("generate_button", self.lang))
        self.generateButton.setMinimumWidth(120)
        buttonLayout.addWidget(self.generateButton)
        
        buttonLayout.addStretch()
        
        layout.addLayout(buttonLayout)
        
        # 进度条
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(0)
        self.progressBar.hide()
        layout.addWidget(self.progressBar)
        
        # 设置题集按钮的事件处理
        self.questionSetsButton.clicked.connect(self.on_question_sets_clicked)
        
        # 设置语言选择的事件处理
        self.languageComboBox.currentIndexChanged.connect(self.on_language_changed)
        
        # 将窗口设置为非模态，允许用户同时刷卡
        self.dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.dialog.setWindowFlags(Qt.WindowType.Window)
        
        self.apply_anki_style()
        
    def apply_anki_style(self):
        """应用Anki样式表"""
        # 检测Anki是否处于夜间模式
        night_mode = False
        try:
            from aqt.theme import theme_manager
            night_mode = theme_manager.night_mode
        except:
            try:
                night_mode = mw.pm.meta.get("night_mode", False)
            except:
                pass
        
        # 根据夜间模式设置不同的样式
        if night_mode:
            self.dialog.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                }
                QLabel {
                    color: #64b5f6;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QProgressBar {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    height: 8px;
                    margin: 0px;
                    background-color: #383838;
                }
                QProgressBar::chunk {
                    background-color: #1976D2;
                    width: 20px;
                    margin: 0px;
                }
                QPlainTextEdit, QTextEdit {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QComboBox {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QSpinBox {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
            """)
        else:
            self.dialog.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QLabel {
                    color: #2196F3;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QProgressBar {
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    height: 8px;
                    margin: 0px;
                    background-color: white;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                    width: 20px;
                    margin: 0px;
                }
            """)
            
    def on_question_sets_clicked(self):
        """题集按钮点击事件"""
        # 如果窗口已存在且可见，则激活它而不是创建新的
        if self.question_sets_dialog and self.question_sets_dialog.isVisible():
            self.question_sets_dialog.activateWindow()
            return
            
        # 导入模块（此处放在方法内导入，避免循环导入问题）
        from ..dialogs.question_sets_dialog import show_question_sets_dialog
        
        # 显示题目集管理对话框
        self.question_sets_dialog = show_question_sets_dialog(self.dialog)
        
        # 连接关闭信号，在窗口关闭时清空引用
        self.question_sets_dialog.finished.connect(self.on_question_sets_dialog_closed)
    
    def on_question_sets_dialog_closed(self):
        """处理题集管理对话框关闭事件"""
        # 清空窗口引用
        self.question_sets_dialog = None
    
    def on_language_changed(self, index):
        """处理语言选择变更事件"""
        # 获取选择的语言文本
        selected_text = self.languageComboBox.currentText()
        
        # 检查是否选择了"自定义..."选项
        custom_language_text = get_message("language_custom", self.lang)
        if custom_language_text in selected_text:
            # 弹出输入对话框
            from aqt.qt import QInputDialog
            custom_lang, ok = QInputDialog.getText(
                self.dialog,
                get_message("custom_language_title", self.lang),
                get_message("custom_language_prompt", self.lang)
            )
            
            if ok and custom_lang.strip():
                # 用户输入了自定义语言，保存到ComboBox
                # 移除"自定义..."选项，添加新的自定义语言选项
                self.languageComboBox.blockSignals(True)  # 暂时阻止信号，避免递归
                self.languageComboBox.removeItem(index)
                self.languageComboBox.insertItem(index, custom_lang.strip())
                self.languageComboBox.setCurrentIndex(index)
                # 重新添加"自定义..."选项
                self.languageComboBox.addItem(get_message("language_custom", self.lang))
                self.languageComboBox.blockSignals(False)  # 恢复信号
            else:
                # 用户取消或未输入，恢复到默认选项
                self.languageComboBox.blockSignals(True)
                self.languageComboBox.setCurrentIndex(0)  # 默认选择中文
                self.languageComboBox.blockSignals(False)
        
    def update_ui_texts(self, lang):
        """更新UI文本"""
        self.lang = lang
        self.dialog.setWindowTitle(get_message("input_window_title", self.lang))
        self.titleLabel.setText(get_message("input_title", self.lang))
        self.contentEdit.setPlaceholderText(get_message("input_placeholder", self.lang))
        self.deckLabel.setText(get_message("select_deck", self.lang))
        self.questionTypeLabel.setText(get_message("question_type", self.lang))
        
        # 更新下拉框选项
        current_index = self.questionTypeComboBox.currentIndex()
        self.questionTypeComboBox.clear()
        self.questionTypeComboBox.addItems([
            get_message("question_type_choice", self.lang),
            get_message("question_type_qa", self.lang),
            get_message("question_type_knowledge", self.lang),
            get_message("question_type_language_learning", self.lang),
            get_message("question_type_custom", self.lang)
        ])
        self.questionTypeComboBox.setCurrentIndex(current_index)
        
        self.templateLabel.setText(get_message("select_template", self.lang))
        self.manageTemplateButton.setText(get_message("manage_templates", self.lang))
        self.languageLabel.setText(get_message("select_language", self.lang))
        
        # 更新语言选择下拉框选项
        current_lang_index = self.languageComboBox.currentIndex()
        self.languageComboBox.clear()
        self.languageComboBox.addItems([
            get_message("language_chinese", self.lang),
            get_message("language_spanish", self.lang),
            get_message("language_japanese", self.lang),
            get_message("language_custom", self.lang)
        ])
        if current_lang_index >= 0:
            self.languageComboBox.setCurrentIndex(current_lang_index)
        
        self.numQuestionsLabel.setText(get_message("num_questions", self.lang))
        self.modelLabel.setText(get_message("select_model", self.lang))
        self.followUpModelLabel.setText(get_message("select_followup_model", self.lang))
        self.generateButton.setText(get_message("generate_button", self.lang))
        self.questionSetsButton.setText("题集") 