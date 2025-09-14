"""
PDF导入对话框模块

提供PDF文件选择和导入功能
"""
from aqt.qt import *
from aqt.utils import showWarning, showInfo, tooltip
from ...lang.messages import get_message, get_default_lang
from ...utils.pdf_reader import PDFReaderError, check_pypdf_availability


class PDFImportDialog(QDialog):
    """PDF导入对话框"""
    
    pdf_imported = pyqtSignal(dict)  # PDF导入成功信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_default_lang()
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(get_message("pdf_import_title", self.lang))
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # 检查pypdf可用性
        if not check_pypdf_availability():
            warning_label = QLabel(get_message("pypdf_not_available", self.lang))
            warning_label.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(warning_label)
            
            close_button = QPushButton(get_message("close", self.lang))
            close_button.clicked.connect(self.reject)
            layout.addWidget(close_button)
            return
        
        # 说明文本
        info_label = QLabel(get_message("pdf_import_info", self.lang))
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 文件选择区域
        file_group = QGroupBox(get_message("select_pdf_file", self.lang))
        file_layout = QVBoxLayout(file_group)
        
        # 文件路径显示
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText(get_message("no_file_selected", self.lang))
        
        self.browse_button = QPushButton(get_message("browse", self.lang))
        self.browse_button.clicked.connect(self.browse_file)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        file_layout.addLayout(path_layout)
        
        layout.addWidget(file_group)
        
        # PDF信息显示区域
        self.info_group = QGroupBox(get_message("pdf_info", self.lang))
        self.info_group.setVisible(False)
        info_layout = QFormLayout(self.info_group)
        
        self.title_label = QLabel()
        self.pages_label = QLabel()
        self.size_label = QLabel()
        
        info_layout.addRow(get_message("pdf_title", self.lang), self.title_label)
        info_layout.addRow(get_message("pdf_pages", self.lang), self.pages_label)
        info_layout.addRow(get_message("pdf_size", self.lang), self.size_label)
        
        layout.addWidget(self.info_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.import_button = QPushButton(get_message("import_pdf", self.lang))
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_pdf)
        
        cancel_button = QPushButton(get_message("cancel", self.lang))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # 状态栏
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            get_message("select_pdf_file", self.lang),
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
            self.load_pdf_info(file_path)
    
    def load_pdf_info(self, pdf_path: str):
        """加载PDF信息"""
        try:
            from ...utils.pdf_reader import get_pdf_info
            
            self.status_label.setText(get_message("loading_pdf_info", self.lang))
            
            pdf_info = get_pdf_info(pdf_path)
            
            # 显示PDF信息
            self.title_label.setText(pdf_info['title'])
            self.pages_label.setText(str(pdf_info['page_count']))
            
            # 格式化文件大小
            size_mb = pdf_info['file_size'] / (1024 * 1024)
            if size_mb < 1:
                size_text = f"{pdf_info['file_size'] / 1024:.1f} KB"
            else:
                size_text = f"{size_mb:.1f} MB"
            self.size_label.setText(size_text)
            
            self.info_group.setVisible(True)
            self.import_button.setEnabled(True)
            self.status_label.setText(get_message("pdf_info_loaded", self.lang))
            
        except PDFReaderError as e:
            showWarning(f"{get_message('pdf_load_error', self.lang)}: {str(e)}")
            self.info_group.setVisible(False)
            self.import_button.setEnabled(False)
            self.status_label.setText(get_message("pdf_load_failed", self.lang))
        except Exception as e:
            showWarning(f"{get_message('unexpected_error', self.lang)}: {str(e)}")
            self.info_group.setVisible(False)
            self.import_button.setEnabled(False)
            self.status_label.setText(get_message("pdf_load_failed", self.lang))
    
    def import_pdf(self):
        """导入PDF"""
        pdf_path = self.path_edit.text()
        if not pdf_path:
            showWarning(get_message("no_file_selected", self.lang))
            return
        
        try:
            self.status_label.setText(get_message("importing_pdf", self.lang))
            self.import_button.setEnabled(False)
            
            # 添加到PDF库
            from ...utils.pdf_storage import pdf_storage
            pdf_record = pdf_storage.add_pdf(pdf_path)
            
            self.status_label.setText(get_message("pdf_imported_success", self.lang))
            
            # 发出导入成功信号
            self.pdf_imported.emit(pdf_record)
            
            # 显示成功消息
            showInfo(get_message("pdf_added_to_library", self.lang))
            
            # 关闭对话框
            self.accept()
            
        except PDFReaderError as e:
            showWarning(f"{get_message('pdf_import_error', self.lang)}: {str(e)}")
            self.status_label.setText(get_message("pdf_import_failed", self.lang))
            self.import_button.setEnabled(True)
        except Exception as e:
            showWarning(f"{get_message('unexpected_error', self.lang)}: {str(e)}")
            self.status_label.setText(get_message("pdf_import_failed", self.lang))
            self.import_button.setEnabled(True)
