from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, tooltip
import os
import json

class SentencesStorageWindow(QDialog):
    """句子存储窗口，用于显示和管理收集的外语句子"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_dialog = parent
        self.sentences = []
        self.sentences_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         "data", "sentences.json")
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(self.sentences_file), exist_ok=True)
        
        # 加载已保存的句子
        self.load_sentences()
        
        # 创建UI组件
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("语言学习例句库")
        self.resize(800, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 添加顶部标题
        title_label = QLabel("语言学习例句库")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加说明文本
        description_label = QLabel("这里存储了你在学习过程中收集的外语句子。你可以查看、编辑、删除这些句子，也可以将它们添加到学习中。")
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索句子...")
        self.search_edit.textChanged.connect(self.filter_sentences)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        main_layout.addLayout(search_layout)
        
        # 句子列表
        self.sentences_list = QListWidget()
        self.sentences_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.sentences_list.itemSelectionChanged.connect(self.on_sentence_selected)
        self.sentences_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sentences_list.customContextMenuRequested.connect(self.show_sentence_list_context_menu)
        main_layout.addWidget(self.sentences_list)
        
        # 句子详情
        details_group = QGroupBox("句子详情")
        details_layout = QVBoxLayout(details_group)
        
        self.sentence_text = QTextEdit()
        self.sentence_text.setReadOnly(False)
        self.sentence_text.setPlaceholderText("选择一个句子查看详情...")
        details_layout.addWidget(self.sentence_text)
        
        self.edit_buttons_layout = QHBoxLayout()
        self.save_edit_button = QPushButton("保存修改")
        self.save_edit_button.clicked.connect(self.save_sentence_edit)
        self.delete_button = QPushButton("删除句子")
        self.delete_button.clicked.connect(self.delete_sentence)
        self.send_to_language_window_button = QPushButton("发送到语言学习窗口")
        self.send_to_language_window_button.clicked.connect(self.send_to_language_window)
        
        self.edit_buttons_layout.addWidget(self.save_edit_button)
        self.edit_buttons_layout.addWidget(self.delete_button)
        self.edit_buttons_layout.addWidget(self.send_to_language_window_button)
        details_layout.addLayout(self.edit_buttons_layout)
        
        main_layout.addWidget(details_group)
        
        # 更新句子列表
        self.update_sentences_list()

    def load_sentences(self):
        """从文件加载保存的句子"""
        try:
            if os.path.exists(self.sentences_file):
                with open(self.sentences_file, 'r', encoding='utf-8') as f:
                    self.sentences = json.load(f)
            else:
                self.sentences = []
        except Exception as e:
            showInfo(f"加载句子时出错: {str(e)}")
            self.sentences = []
    
    def save_sentences(self):
        """保存句子到文件"""
        try:
            with open(self.sentences_file, 'w', encoding='utf-8') as f:
                json.dump(self.sentences, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            showInfo(f"保存句子时出错: {str(e)}")
            return False
    
    def update_sentences_list(self):
        """更新句子列表显示"""
        self.sentences_list.clear()
        for sentence in self.sentences:
            # 创建项目
            item = QListWidgetItem(sentence[:50] + ("..." if len(sentence) > 50 else ""))
            item.setData(Qt.ItemDataRole.UserRole, sentence)
            self.sentences_list.addItem(item)
            
    def filter_sentences(self):
        """根据搜索文本过滤句子列表"""
        search_text = self.search_edit.text().lower()
        self.sentences_list.clear()
        
        for sentence in self.sentences:
            if search_text in sentence.lower():
                item = QListWidgetItem(sentence[:50] + ("..." if len(sentence) > 50 else ""))
                item.setData(Qt.ItemDataRole.UserRole, sentence)
                self.sentences_list.addItem(item)
                
    def on_sentence_selected(self):
        """当选择列表中的句子时显示详情"""
        selected_items = self.sentences_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            full_sentence = item.data(Qt.ItemDataRole.UserRole)
            self.sentence_text.setText(full_sentence)
            
    def save_sentence_edit(self):
        """保存对句子的编辑"""
        selected_items = self.sentences_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        old_sentence = item.data(Qt.ItemDataRole.UserRole)
        new_sentence = self.sentence_text.toPlainText()
        
        # 更新列表中的句子
        if old_sentence in self.sentences:
            index = self.sentences.index(old_sentence)
            self.sentences[index] = new_sentence
            self.save_sentences()
            
            # 更新列表项显示
            item.setText(new_sentence[:50] + ("..." if len(new_sentence) > 50 else ""))
            item.setData(Qt.ItemDataRole.UserRole, new_sentence)
            
            tooltip("句子已更新")
        
    def delete_sentence(self):
        """删除选中的句子"""
        selected_items = self.sentences_list.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        sentence = item.data(Qt.ItemDataRole.UserRole)
        
        # 确认删除
        confirm = QMessageBox.question(self, "确认删除", 
                                       "确定要删除这个句子吗？此操作不可撤销。",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            # 从列表中删除句子
            if sentence in self.sentences:
                self.sentences.remove(sentence)
                self.save_sentences()
                
                # 从列表控件中删除
                row = self.sentences_list.row(item)
                self.sentences_list.takeItem(row)
                
                # 清空详情区域
                self.sentence_text.clear()
                
                tooltip("句子已删除")
                
    def add_sentence(self, sentence):
        """添加新句子到列表"""
        if sentence and sentence not in self.sentences:
            self.sentences.append(sentence)
            self.save_sentences()
            self.update_sentences_list()
            tooltip("句子已添加到例句库")
            return True
        elif sentence in self.sentences:
            tooltip("句子已存在于例句库中")
            return False
        return False
    
    def send_to_language_window(self):
        """将选中的句子发送到语言学习窗口进行分析"""
        selected_items = self.sentences_list.selectedItems()
        if not selected_items:
            return
            
        sentence = selected_items[0].data(Qt.ItemDataRole.UserRole)
        from .language_window import show_language_window
        
        # 打开语言学习窗口并设置句子
        language_window = show_language_window(sentence)
        if language_window:
            self.close()  # 可选：关闭当前窗口
    
    def show_sentence_list_context_menu(self, position):
        """显示句子列表的右键菜单"""
        menu = QMenu()
        selected_items = self.sentences_list.selectedItems()
        
        if selected_items:
            send_action = menu.addAction("发送到语言学习窗口")
            send_action.triggered.connect(self.send_to_language_window)
            
            delete_action = menu.addAction("删除句子")
            delete_action.triggered.connect(self.delete_sentence)
            
            menu.exec(self.sentences_list.mapToGlobal(position))

def show_sentences_storage_window(sentence=None):
    """显示句子存储窗口，可选参数为要添加的新句子"""
    storage_dialog = SentencesStorageWindow(mw)
    
    # 如果提供了句子，添加到列表
    if sentence:
        storage_dialog.add_sentence(sentence)
    
    storage_dialog.show()
    return storage_dialog 