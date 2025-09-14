from aqt.qt import *
from PyQt6.QtCore import Qt, pyqtSignal
from ...utils.text_capture import get_stored_sentences

class SentenceInputPanel(QGroupBox):
    """句子输入区域面板"""
    
    sentenceChanged = pyqtSignal(str)  # 句子变化信号
    partsChanged = pyqtSignal(list)    # 替换部分变化信号
    generateClicked = pyqtSignal()     # 生成按钮点击信号
    
    def __init__(self, parent=None):
        super().__init__("输入句子", parent)
        self.setStyleSheet("font-weight: 500;")
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        input_layout = QVBoxLayout(self)
        input_layout.setContentsMargins(15, 25, 15, 15)
        input_layout.setSpacing(15)
        
        # 添加句子输入与例句库按钮的水平布局
        sentence_area_layout = QHBoxLayout()
        
        # 添加句子输入区
        self.sentence_edit = QPlainTextEdit()
        self.sentence_edit.setPlaceholderText("请输入你想练习的句子...")
        self.sentence_edit.setMinimumHeight(100)
        self.sentence_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sentence_edit.customContextMenuRequested.connect(self.show_sentence_context_menu)
        self.sentence_edit.textChanged.connect(self.on_sentence_changed)
        sentence_area_layout.addWidget(self.sentence_edit, 5)  # 分配比例 5
        
        # 添加例句库按钮和操作区域
        examples_layout = QVBoxLayout()
        examples_layout.setContentsMargins(10, 0, 0, 0)
        
        self.examples_button = QPushButton("从例句库选择")
        self.examples_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.examples_button.clicked.connect(self.show_examples_list)
        examples_layout.addWidget(self.examples_button)
        
        # 添加例句数量显示
        self.examples_count_label = QLabel("例句库: 0 个句子")
        examples_layout.addWidget(self.examples_count_label)
        
        # 更新例句数量
        self.update_examples_count()
        
        # 添加刷新按钮
        self.refresh_button = QPushButton("刷新例句库")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.clicked.connect(self.update_examples_count)
        examples_layout.addWidget(self.refresh_button)
        
        # 添加垂直间隔
        examples_layout.addStretch()
        
        sentence_area_layout.addLayout(examples_layout, 1)  # 分配比例 1
        
        input_layout.addLayout(sentence_area_layout)
        
        # 添加用户指定替换部分的选项
        specify_layout = QHBoxLayout()
        
        self.specify_checkbox = QCheckBox("指定替换部分")
        self.specify_checkbox.toggled.connect(self.toggle_specify_parts)
        specify_layout.addWidget(self.specify_checkbox)
        
        self.parts_to_replace_edit = QLineEdit()
        self.parts_to_replace_edit.setPlaceholderText("输入要替换的部分，多个部分用逗号分隔")
        self.parts_to_replace_edit.setEnabled(False)
        self.parts_to_replace_edit.textChanged.connect(self.on_parts_changed)
        specify_layout.addWidget(self.parts_to_replace_edit)
        
        input_layout.addLayout(specify_layout)
        
        # 生成按钮
        self.generate_button = QPushButton("生成练习")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.clicked.connect(self.on_generate_clicked)
        input_layout.addWidget(self.generate_button)
        
    def on_sentence_changed(self):
        """句子变化处理"""
        self.sentenceChanged.emit(self.sentence_edit.toPlainText().strip())
        
    def on_parts_changed(self):
        """替换部分变化处理"""
        parts_text = self.parts_to_replace_edit.text().strip()
        parts = [part.strip() for part in parts_text.split(',') if part.strip()]
        self.partsChanged.emit(parts)
        
    def on_generate_clicked(self):
        """生成按钮点击处理"""
        self.generateClicked.emit()
    
    def toggle_specify_parts(self):
        """处理用户选择指定替换部分"""
        if self.specify_checkbox.isChecked():
            self.parts_to_replace_edit.setEnabled(True)
        else:
            self.parts_to_replace_edit.setEnabled(False)
    
    def show_sentence_context_menu(self, position):
        """显示句子编辑区域的右键菜单"""
        menu = self.sentence_edit.createStandardContextMenu()
        
        # 获取选中的文本
        cursor = self.sentence_edit.textCursor()
        selected_text = cursor.selectedText()
        
        # 如果有选中文本，添加"添加到替换部分"的菜单项
        if selected_text:
            menu.addSeparator()
            add_to_replace_action = menu.addAction("添加到替换部分")
            add_to_replace_action.triggered.connect(lambda: self.add_to_replace_parts(selected_text))
        
        menu.exec(self.sentence_edit.mapToGlobal(position))

    def add_to_replace_parts(self, text):
        """将选中的文本添加到替换部分"""
        self.specify_checkbox.setChecked(True)  # 自动勾选"指定替换部分"
        
        current_text = self.parts_to_replace_edit.text()
        if current_text:
            # 如果已经有内容，检查是否重复
            parts = [part.strip() for part in current_text.split(',')]
            if text not in parts:
                self.parts_to_replace_edit.setText(f"{current_text}, {text}")
        else:
            self.parts_to_replace_edit.setText(text)
            
    def get_sentence(self):
        """获取当前句子"""
        return self.sentence_edit.toPlainText().strip()
    
    def get_specified_parts(self):
        """获取用户指定的替换部分"""
        if not self.specify_checkbox.isChecked():
            return None
            
        parts_text = self.parts_to_replace_edit.text().strip()
        if not parts_text:
            return None
            
        return [part.strip() for part in parts_text.split(',') if part.strip()]
        
    def update_examples_count(self):
        """更新例句数量显示"""
        sentences = get_stored_sentences()
        count = len(sentences)
        self.examples_count_label.setText(f"例句库: {count} 个句子")
        
    def show_examples_list(self):
        """显示例句库列表对话框"""
        sentences = get_stored_sentences()
        if not sentences:
            from aqt.utils import showInfo
            showInfo("例句库中暂无句子，请先通过右键菜单添加例句。")
            return
            
        # 创建例句选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择例句")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 添加说明标签
        label = QLabel("请从例句库中选择一个句子导入到输入框：")
        layout.addWidget(label)
        
        # 添加搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_edit = QLineEdit()
        search_edit.setPlaceholderText("输入关键词搜索...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_edit)
        layout.addLayout(search_layout)
        
        # 添加例句列表
        sentences_list = QListWidget()
        sentences_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        sentences_list.setWordWrap(True)
        layout.addWidget(sentences_list)
        
        # 添加"选择后删除"选项
        delete_after_select_checkbox = QCheckBox("选择后从例句库中删除")
        delete_after_select_checkbox.setToolTip("勾选此项后，选择的句子将在导入到输入框后从例句库中删除")
        layout.addWidget(delete_after_select_checkbox)
        
        # 添加按钮
        buttons_layout = QHBoxLayout()
        select_button = QPushButton("选择")
        select_button.setDefault(True)
        cancel_button = QPushButton("取消")
        delete_button = QPushButton("删除句子")
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(select_button)
        layout.addLayout(buttons_layout)
        
        # 更新列表显示
        def update_list(filter_text=""):
            sentences_list.clear()
            for sentence in sentences:
                if filter_text.lower() in sentence.lower():
                    sentences_list.addItem(sentence)
        
        # 初始化列表
        update_list()
        
        # 连接搜索信号
        search_edit.textChanged.connect(update_list)
        
        # 连接按钮信号
        select_button.clicked.connect(lambda: self.select_example(
            sentences_list.currentItem(), 
            dialog, 
            sentences_list, 
            sentences, 
            delete_after_select_checkbox.isChecked()
        ))
        cancel_button.clicked.connect(dialog.reject)
        delete_button.clicked.connect(lambda: self.delete_example(sentences_list.currentItem(), sentences_list, sentences))
        
        # 双击选择
        sentences_list.itemDoubleClicked.connect(lambda item: self.select_example(
            item, 
            dialog, 
            sentences_list, 
            sentences, 
            delete_after_select_checkbox.isChecked()
        ))
        
        # 显示对话框
        dialog.exec()
        
    def select_example(self, item, dialog, list_widget=None, sentences=None, delete_after_select=False):
        """从例句库选择一个句子"""
        if not item:
            from aqt.utils import showInfo
            showInfo("请先选择一个句子")
            return
            
        sentence_text = item.text()
        self.sentence_edit.setPlainText(sentence_text)
        
        # 如果需要选择后删除，且提供了必要的参数
        if delete_after_select and list_widget and sentences is not None:
            if sentence_text in sentences:
                sentences.remove(sentence_text)
                
                # 保存回文件
                import os
                import json
                sentences_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                           "data", "sentences.json")
                
                try:
                    with open(sentences_file, 'w', encoding='utf-8') as f:
                        json.dump(sentences, f, ensure_ascii=False, indent=4)
                    
                    # 更新计数
                    self.update_examples_count()
                    
                    from aqt.utils import tooltip
                    tooltip("句子已选择并从例句库中删除")
                except Exception as e:
                    from aqt.utils import showWarning
                    showWarning(f"删除失败: {str(e)}")
        
        dialog.accept()
        
    def delete_example(self, item, list_widget, sentences):
        """从例句库删除一个句子"""
        if not item:
            from aqt.utils import showInfo
            showInfo("请先选择一个句子")
            return
            
        from aqt.utils import showWarning, tooltip
        
        # 确认删除
        confirm = QMessageBox.question(self, "确认删除", 
                                       "确定要删除这个句子吗？此操作不可撤销。",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            sentence_text = item.text()
            
            # 从列表和存储中删除
            if sentence_text in sentences:
                sentences.remove(sentence_text)
                
                # 保存回文件
                import os
                import json
                sentences_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                           "data", "sentences.json")
                
                try:
                    with open(sentences_file, 'w', encoding='utf-8') as f:
                        json.dump(sentences, f, ensure_ascii=False, indent=4)
                        
                    # 从列表控件中删除
                    row = list_widget.row(item)
                    list_widget.takeItem(row)
                    
                    # 更新计数
                    self.update_examples_count()
                    
                    tooltip("句子已删除")
                except Exception as e:
                    showWarning(f"删除失败: {str(e)}") 