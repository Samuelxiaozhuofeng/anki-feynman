"""
输入事件处理控制器模块
"""
from aqt.qt import QThread
from aqt.utils import showWarning, showInfo
from ...lang.messages import get_message
from ...utils.ai_handler import AIHandler
from ..workers.generate_questions_worker import GenerateQuestionsWorker
from ..workers.document_extract_worker import DocumentExtractWorker
from ..dialogs.pdf_import_dialog import PDFImportDialog
from ..dialogs.pdf_library_dialog import PDFLibraryDialog

class InputEventsController:
    """输入事件处理控制器，负责处理用户交互事件"""
    
    def __init__(self, dialog, question_controller):
        """
        初始化控制器
        
        参数:
        dialog -- 持有对话框的引用
        question_controller -- 问题控制器的引用
        """
        self.dialog = dialog
        self.question_controller = question_controller
        self.ai_handler = None
        self.thread = None
        self.worker = None
        self.extract_thread = None
        self.extract_worker = None
        
    def setup_connections(self):
        """设置信号连接"""
        if not hasattr(self.dialog.ui, 'generateButton') or not hasattr(self.dialog.ui, 'contentEdit'):
            return

        self.dialog.ui.generateButton.clicked.connect(self.on_generate_clicked)
        self.dialog.ui.contentEdit.textChanged.connect(self.on_content_changed)

        # 添加问题类型变更事件
        if hasattr(self.dialog.ui, 'questionTypeComboBox'):
            self.dialog.ui.questionTypeComboBox.currentIndexChanged.connect(self.on_question_type_changed)
            self.dialog.ui.questionTypeComboBox.currentIndexChanged.connect(self.on_selection_changed)

        # 添加管理模板按钮点击事件
        if hasattr(self.dialog.ui, 'manageTemplateButton'):
            self.dialog.ui.manageTemplateButton.clicked.connect(self.on_manage_templates_clicked)

        # 添加选择变更事件监听，用于自动保存用户选择
        if hasattr(self.dialog.ui, 'deckComboBox'):
            self.dialog.ui.deckComboBox.currentIndexChanged.connect(self.on_selection_changed)

        if hasattr(self.dialog.ui, 'templateComboBox'):
            self.dialog.ui.templateComboBox.currentIndexChanged.connect(self.on_selection_changed)

        if hasattr(self.dialog.ui, 'numQuestionsSpinBox'):
            self.dialog.ui.numQuestionsSpinBox.valueChanged.connect(self.on_selection_changed)

        if hasattr(self.dialog.ui, 'modelComboBox'):
            self.dialog.ui.modelComboBox.currentIndexChanged.connect(self.on_selection_changed)

        if hasattr(self.dialog.ui, 'followUpModelComboBox'):
            self.dialog.ui.followUpModelComboBox.currentIndexChanged.connect(self.on_selection_changed)

        # 添加PDF相关按钮事件
        if hasattr(self.dialog.ui, 'pdfImportButton'):
            self.dialog.ui.pdfImportButton.clicked.connect(self.on_pdf_import_clicked)

        if hasattr(self.dialog.ui, 'pdfLibraryButton'):
            self.dialog.ui.pdfLibraryButton.clicked.connect(self.on_pdf_library_clicked)

        # 注意：题集按钮的点击事件已在InputDialogUI的setup_ui方法中连接，不需要在这里重复连接
        
    def on_generate_clicked(self):
        """生成问题按钮点击事件"""
        content = self.dialog.ui.contentEdit.toPlainText().strip()
        if not content:
            showWarning(get_message("input_content_warning", self.dialog.lang))
            return

        # 获取选择的问题类型和数量
        question_type = self.dialog.ui.questionTypeComboBox.currentText()
        # 将界面显示的文本转换为实际的问题类型
        if question_type == get_message("question_type_choice", self.dialog.lang):
            actual_type = "multiple_choice"
        elif question_type == get_message("question_type_knowledge", self.dialog.lang):
            actual_type = "knowledge_card"
        elif question_type == get_message("question_type_custom", self.dialog.lang):
            actual_type = "custom"
        else:
            actual_type = "qa"
        num_questions = self.dialog.ui.numQuestionsSpinBox.value()
        
        # 获取选择的模型
        selected_model = self.dialog.ui.modelComboBox.currentData()
        # 获取选择的追加提问模型
        selected_followup_model = self.dialog.ui.followUpModelComboBox.currentData()
        
        # 获取选择的模板ID
        template_id = None
        if actual_type == "custom":
            template_id = self.dialog.ui.templateComboBox.currentData()
            if not template_id:
                # 如果没有选择模板，显示创建模板对话框
                from ..template_manager import PromptTemplateEditor
                editor = PromptTemplateEditor(parent=self.dialog)
                if editor.exec():
                    # 如果创建了新模板，重新加载模板并选择新创建的模板
                    template_id = editor.template_id
                    self.dialog.model_controller.load_templates()
                    # 选择新创建的模板
                    index = self.dialog.ui.templateComboBox.findData(template_id)
                    if index >= 0:
                        self.dialog.ui.templateComboBox.setCurrentIndex(index)
                else:
                    # 如果取消创建模板，不继续生成
                    return

        # 禁用生成按钮
        self.dialog.ui.generateButton.setEnabled(False)
        # 显示进度条
        self.dialog.ui.progressBar.show()

        try:
            # 初始化AI处理器
            if not self.ai_handler:
                self.ai_handler = AIHandler()

            # 创建新线程
            self.thread = QThread()
            self.worker = GenerateQuestionsWorker(
                self.ai_handler,
                content,
                actual_type,  # 使用转换后的类型
                num_questions,
                selected_model,  # 传递选择的模型
                template_id,  # 传递模板ID
                selected_followup_model  # 传递追加提问模型
            )
            self.worker.moveToThread(self.thread)

            # 连接信号
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.questions_ready.connect(self.question_controller.on_questions_generated)
            self.worker.error_occurred.connect(self.question_controller.on_generation_error)

            # 启动线程
            self.thread.start()

        except Exception as e:
            self.question_controller.on_generation_error(str(e))
            
    def on_content_changed(self):
        """内容变化事件"""
        has_content = bool(self.dialog.ui.contentEdit.toPlainText().strip())
        self.dialog.ui.generateButton.setEnabled(has_content)
        
    def on_question_type_changed(self):
        """问题类型变更事件处理"""
        question_type = self.dialog.ui.questionTypeComboBox.currentText()
        
        # 如果选择自定义选项，显示模板选择框
        is_custom = question_type == get_message("question_type_custom", self.dialog.lang)
        self.dialog.ui.templateContainer.setVisible(is_custom)
        
        # 如果是自定义选项，加载模板
        if is_custom:
            self.dialog.model_controller.load_templates()

    def on_selection_changed(self):
        """选择变更事件处理，自动保存用户的选择"""
        # 延迟保存，避免在初始化时触发
        if hasattr(self.dialog, 'save_current_selections'):
            self.dialog.save_current_selections()
            
    def on_manage_templates_clicked(self):
        """管理模板按钮点击事件"""
        from ..template_manager import PromptTemplateManager
        dialog = PromptTemplateManager(parent=self.dialog)
        if dialog.exec():
            # 如果对话框关闭时返回接受，重新加载模板
            self.dialog.model_controller.load_templates()

    def on_pdf_import_clicked(self):
        """PDF导入按钮点击事件"""
        dialog = PDFImportDialog(parent=self.dialog)
        dialog.pdf_imported.connect(self.on_pdf_imported)
        dialog.exec()

    def on_pdf_library_clicked(self):
        """PDF库按钮点击事件"""
        dialog = PDFLibraryDialog(parent=self.dialog)
        dialog.pdf_selected.connect(self.on_pdf_selected)
        dialog.exec()

    def on_pdf_imported(self, pdf_record):
        """PDF导入成功回调"""
        # 可以在这里添加额外的处理逻辑
        pass

    def on_pdf_selected(self, pdf_path, start_page, end_page):
        """PDF选择回调，开始提取文本并生成题目"""
        try:
            # 创建文档提取线程
            self.extract_thread = QThread()
            self.extract_worker = DocumentExtractWorker(pdf_path, start_page, end_page)
            self.extract_worker.moveToThread(self.extract_thread)

            # 连接信号
            self.extract_thread.started.connect(self.extract_worker.run)
            self.extract_worker.finished.connect(self.extract_thread.quit)
            self.extract_worker.finished.connect(self.extract_worker.deleteLater)
            self.extract_thread.finished.connect(self.extract_thread.deleteLater)
            self.extract_worker.text_extracted.connect(self.on_pdf_text_extracted)
            self.extract_worker.error_occurred.connect(self.on_pdf_extraction_error)
            self.extract_worker.progress_updated.connect(self.on_pdf_extraction_progress)

            # 显示进度状态
            if hasattr(self.dialog.ui, 'progressBar'):
                self.dialog.ui.progressBar.setVisible(True)
                self.dialog.ui.progressBar.setRange(0, 0)  # 不确定进度

            # 禁用生成按钮
            self.dialog.ui.generateButton.setEnabled(False)

            # 启动线程
            self.extract_thread.start()

        except Exception as e:
            showWarning(f"{get_message('pdf_extraction_failed', self.dialog.lang)}: {str(e)}")

    def on_pdf_text_extracted(self, extracted_text):
        """PDF文本提取完成回调"""
        try:
            # 隐藏进度条
            if hasattr(self.dialog.ui, 'progressBar'):
                self.dialog.ui.progressBar.setVisible(False)

            # 直接使用提取的文本生成题目，不经过contentEdit
            self.generate_questions_from_text(extracted_text)

        except Exception as e:
            showWarning(f"{get_message('unexpected_error', self.dialog.lang)}: {str(e)}")

    def on_pdf_extraction_error(self, error_message):
        """PDF文本提取错误回调"""
        # 隐藏进度条
        if hasattr(self.dialog.ui, 'progressBar'):
            self.dialog.ui.progressBar.setVisible(False)

        # 重新启用生成按钮
        self.dialog.ui.generateButton.setEnabled(True)

        showWarning(f"{get_message('pdf_extraction_failed', self.dialog.lang)}: {error_message}")

    def on_pdf_extraction_progress(self, progress_message):
        """PDF文本提取进度更新回调"""
        # 可以在这里更新状态栏或进度信息
        pass

    def generate_questions_from_text(self, content):
        """从给定文本直接生成题目（不经过contentEdit）"""
        if not content or not content.strip():
            showWarning(get_message("input_content_warning", self.dialog.lang))
            return

        # 获取选择的问题类型和数量
        question_type = self.dialog.ui.questionTypeComboBox.currentText()
        # 将界面显示的文本转换为实际的问题类型
        if question_type == get_message("question_type_choice", self.dialog.lang):
            actual_type = "multiple_choice"
        elif question_type == get_message("question_type_knowledge", self.dialog.lang):
            actual_type = "knowledge_card"
        elif question_type == get_message("question_type_custom", self.dialog.lang):
            actual_type = "custom"
        else:
            actual_type = "qa"
        num_questions = self.dialog.ui.numQuestionsSpinBox.value()

        # 获取选择的模型
        selected_model = self.dialog.ui.modelComboBox.currentData()
        # 获取选择的追加提问模型
        selected_followup_model = self.dialog.ui.followUpModelComboBox.currentData()

        # 获取选择的模板ID
        template_id = None
        if actual_type == "custom":
            template_id = self.dialog.ui.templateComboBox.currentData()
            if not template_id:
                # 如果没有选择模板，显示创建模板对话框
                from ..template_manager import PromptTemplateEditor
                editor = PromptTemplateEditor(parent=self.dialog)
                if editor.exec():
                    # 如果创建了新模板，重新加载模板并选择新创建的模板
                    template_id = editor.template_id
                    self.dialog.model_controller.load_templates()
                    # 选择新创建的模板
                    index = self.dialog.ui.templateComboBox.findData(template_id)
                    if index >= 0:
                        self.dialog.ui.templateComboBox.setCurrentIndex(index)
                else:
                    # 如果取消创建模板，不继续生成
                    return

        # 显示进度条
        if hasattr(self.dialog.ui, 'progressBar'):
            self.dialog.ui.progressBar.setVisible(True)
            self.dialog.ui.progressBar.setRange(0, 0)

        try:
            # 初始化AI处理器
            if not self.ai_handler:
                self.ai_handler = AIHandler()

            # 创建新线程
            self.thread = QThread()
            self.worker = GenerateQuestionsWorker(
                self.ai_handler,
                content,
                actual_type,  # 使用转换后的类型
                num_questions,
                selected_model,  # 传递选择的模型
                template_id,  # 传递模板ID
                selected_followup_model  # 传递追加提问模型
            )
            self.worker.moveToThread(self.thread)

            # 连接信号
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.questions_ready.connect(self.question_controller.on_questions_generated)
            self.worker.error_occurred.connect(self.question_controller.on_generation_error)

            # 启动线程
            self.thread.start()

        except Exception as e:
            self.question_controller.on_generation_error(str(e))