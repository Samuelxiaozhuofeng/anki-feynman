"""
PDF库管理对话框模块

提供PDF库浏览、选择和页码范围输入功能
"""
from aqt.qt import *
from aqt.utils import showWarning, showInfo, askUser
from ...lang.messages import get_message, get_default_lang
from ...utils.pdf_reader import validate_page_range, get_page_preview, get_page_range_preview


class PDFLibraryDialog(QDialog):
    """PDF库对话框"""
    
    pdf_selected = pyqtSignal(str, int, int)  # PDF路径, 起始页, 结束页
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_default_lang()
        self.current_pdf = None
        self.setup_ui()
        self.load_pdf_list()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(get_message("pdf_library_title", self.lang))
        self.setModal(True)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton(get_message("refresh", self.lang))
        self.refresh_button.clicked.connect(self.load_pdf_list)
        
        self.cleanup_button = QPushButton(get_message("cleanup_invalid", self.lang))
        self.cleanup_button.clicked.connect(self.cleanup_invalid_pdfs)
        
        toolbar_layout.addWidget(self.refresh_button)
        toolbar_layout.addWidget(self.cleanup_button)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel(get_message("search", self.lang))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(get_message("search_pdf_placeholder", self.lang))
        self.search_edit.textChanged.connect(self.filter_pdf_list)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # PDF列表
        self.pdf_list = QListWidget()
        self.pdf_list.itemSelectionChanged.connect(self.on_pdf_selected)
        layout.addWidget(self.pdf_list)
        
        # PDF详情和页码选择区域
        details_group = QGroupBox(get_message("pdf_details_and_pages", self.lang))
        details_layout = QVBoxLayout(details_group)
        
        # PDF详情
        self.details_label = QLabel(get_message("select_pdf_first", self.lang))
        self.details_label.setWordWrap(True)
        details_layout.addWidget(self.details_label)
        
        # 页码选择
        pages_layout = QHBoxLayout()
        
        pages_layout.addWidget(QLabel(get_message("start_page", self.lang)))
        self.start_page_spin = QSpinBox()
        self.start_page_spin.setMinimum(1)
        self.start_page_spin.valueChanged.connect(self.validate_page_range)
        pages_layout.addWidget(self.start_page_spin)
        
        pages_layout.addWidget(QLabel(get_message("end_page", self.lang)))
        self.end_page_spin = QSpinBox()
        self.end_page_spin.setMinimum(1)
        self.end_page_spin.valueChanged.connect(self.validate_page_range)
        pages_layout.addWidget(self.end_page_spin)
        
        pages_layout.addStretch()
        
        self.preview_button = QPushButton(get_message("preview_range", self.lang))
        self.preview_button.clicked.connect(self.preview_page_range)
        self.preview_button.setEnabled(False)
        pages_layout.addWidget(self.preview_button)
        
        details_layout.addLayout(pages_layout)
        
        # 页码验证状态
        self.page_status_label = QLabel()
        details_layout.addWidget(self.page_status_label)
        
        layout.addWidget(details_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.generate_button = QPushButton(get_message("generate_questions", self.lang))
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self.generate_questions)
        
        cancel_button = QPushButton(get_message("cancel", self.lang))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def load_pdf_list(self):
        """加载PDF列表"""
        self.pdf_list.clear()

        from ...utils.pdf_storage import pdf_storage
        pdfs = pdf_storage.get_all_pdfs()
        
        if not pdfs:
            item = QListWidgetItem(get_message("no_pdfs_in_library", self.lang))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.pdf_list.addItem(item)
            return
        
        for pdf in pdfs:
            item_text = f"{pdf['title']} ({pdf['page_count']} {get_message('pages', self.lang)})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, pdf)
            self.pdf_list.addItem(item)
    
    def filter_pdf_list(self):
        """过滤PDF列表"""
        keyword = self.search_edit.text()
        from ...utils.pdf_storage import pdf_storage
        matching_pdfs = pdf_storage.search_pdfs(keyword)
        
        self.pdf_list.clear()
        
        if not matching_pdfs:
            item = QListWidgetItem(get_message("no_matching_pdfs", self.lang))
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.pdf_list.addItem(item)
            return
        
        for pdf in matching_pdfs:
            item_text = f"{pdf['title']} ({pdf['page_count']} {get_message('pages', self.lang)})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, pdf)
            self.pdf_list.addItem(item)
    
    def on_pdf_selected(self):
        """PDF选择事件"""
        current_item = self.pdf_list.currentItem()
        if not current_item:
            return
        
        pdf_data = current_item.data(Qt.ItemDataRole.UserRole)
        if not pdf_data:
            return
        
        self.current_pdf = pdf_data
        
        # 更新详情显示
        details_text = f"""
{get_message('title', self.lang)}: {pdf_data['title']}
{get_message('file_name', self.lang)}: {pdf_data['file_name']}
{get_message('pages', self.lang)}: {pdf_data['page_count']}
{get_message('file_size', self.lang)}: {self.format_file_size(pdf_data['file_size'])}
{get_message('added_date', self.lang)}: {pdf_data['added_date'][:10]}
        """.strip()
        
        self.details_label.setText(details_text)
        
        # 设置页码范围
        self.start_page_spin.setMaximum(pdf_data['page_count'])
        self.end_page_spin.setMaximum(pdf_data['page_count'])
        self.start_page_spin.setValue(1)
        self.end_page_spin.setValue(min(10, pdf_data['page_count']))  # 默认前10页
        
        self.preview_button.setEnabled(True)
        self.validate_page_range()
    
    def validate_page_range(self):
        """验证页码范围"""
        if not self.current_pdf:
            return
        
        start_page = self.start_page_spin.value()
        end_page = self.end_page_spin.value()
        
        is_valid, message = validate_page_range(
            self.current_pdf['path'], 
            start_page, 
            end_page
        )
        
        if is_valid:
            self.page_status_label.setText(
                f"{get_message('valid_page_range', self.lang)}: {start_page}-{end_page}"
            )
            self.page_status_label.setStyleSheet("color: green;")
            self.generate_button.setEnabled(True)
        else:
            self.page_status_label.setText(f"{get_message('invalid_page_range', self.lang)}: {message}")
            self.page_status_label.setStyleSheet("color: red;")
            self.generate_button.setEnabled(False)
    
    def preview_page_range(self):
        """预览页码范围"""
        if not self.current_pdf:
            return

        start_page = self.start_page_spin.value()
        end_page = self.end_page_spin.value()

        try:
            # 获取页码范围预览
            preview_data = get_page_range_preview(self.current_pdf['path'], start_page, end_page)

            if preview_data['error']:
                showWarning(f"{get_message('preview_error', self.lang)}: {preview_data['error']}")
                return

            # 显示预览对话框
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle(f"{get_message('page_range_preview', self.lang)} - {get_message('pages', self.lang)} {start_page}-{end_page}")
            preview_dialog.resize(700, 500)

            layout = QVBoxLayout(preview_dialog)

            # 添加说明标签
            info_label = QLabel(get_message("preview_range_info", self.lang))
            info_label.setWordWrap(True)
            info_label.setStyleSheet("font-weight: bold; color: #666; margin-bottom: 10px;")
            layout.addWidget(info_label)

            # 创建分割器
            splitter = QSplitter(Qt.Orientation.Vertical)

            # 起始页预览
            start_group = QGroupBox(f"{get_message('start_page', self.lang)} {start_page} - {get_message('beginning_text', self.lang)}")
            start_layout = QVBoxLayout(start_group)

            start_text_edit = QTextEdit()
            start_text_edit.setPlainText(preview_data['start_preview'])
            start_text_edit.setReadOnly(True)
            start_text_edit.setMaximumHeight(200)
            start_layout.addWidget(start_text_edit)

            splitter.addWidget(start_group)

            # 结束页预览（如果不是同一页）
            if start_page != end_page:
                end_group = QGroupBox(f"{get_message('end_page', self.lang)} {end_page} - {get_message('ending_text', self.lang)}")
                end_layout = QVBoxLayout(end_group)

                end_text_edit = QTextEdit()
                end_text_edit.setPlainText(preview_data['end_preview'])
                end_text_edit.setReadOnly(True)
                end_text_edit.setMaximumHeight(200)
                end_layout.addWidget(end_text_edit)

                splitter.addWidget(end_group)
            else:
                # 同一页的情况，显示页面结尾
                same_page_group = QGroupBox(f"{get_message('same_page_ending', self.lang)} {start_page}")
                same_page_layout = QVBoxLayout(same_page_group)

                same_page_text_edit = QTextEdit()
                same_page_text_edit.setPlainText(preview_data['end_preview'])
                same_page_text_edit.setReadOnly(True)
                same_page_text_edit.setMaximumHeight(200)
                same_page_layout.addWidget(same_page_text_edit)

                splitter.addWidget(same_page_group)

            layout.addWidget(splitter)

            # 统计信息
            stats_label = QLabel(f"{get_message('total_pages_in_range', self.lang)}: {end_page - start_page + 1}")
            stats_label.setStyleSheet("color: #666; font-size: 12px;")
            layout.addWidget(stats_label)

            # 按钮
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            close_button = QPushButton(get_message("close", self.lang))
            close_button.clicked.connect(preview_dialog.accept)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            preview_dialog.exec()

        except Exception as e:
            showWarning(f"{get_message('preview_error', self.lang)}: {str(e)}")
    
    def generate_questions(self):
        """生成题目"""
        if not self.current_pdf:
            return
        
        start_page = self.start_page_spin.value()
        end_page = self.end_page_spin.value()
        
        # 更新访问信息
        from ...utils.pdf_storage import pdf_storage
        pdf_storage.update_access_info(self.current_pdf['id'])
        
        # 发出选择信号
        self.pdf_selected.emit(self.current_pdf['path'], start_page, end_page)
        
        # 关闭对话框
        self.accept()
    
    def cleanup_invalid_pdfs(self):
        """清理无效PDF"""
        if askUser(get_message("confirm_cleanup_invalid", self.lang)):
            from ...utils.pdf_storage import pdf_storage
            count = pdf_storage.cleanup_invalid_pdfs()
            if count > 0:
                showInfo(f"{get_message('cleanup_completed', self.lang)}: {count}")
                self.load_pdf_list()
            else:
                showInfo(get_message("no_invalid_pdfs", self.lang))
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
