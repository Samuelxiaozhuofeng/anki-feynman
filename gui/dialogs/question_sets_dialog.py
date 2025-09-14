"""
题目集管理对话框模块
用于显示和管理已保存的题目集
"""
from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning, askUser

from ..styles.anki_style import apply_anki_style
from ...utils.question_sets import (
    load_question_sets, delete_question_set, get_question_set_by_id
)
from ...lang.messages import get_message, get_default_lang
from ..review_window import show_review_dialog


class QuestionSetsDialog(QDialog):
    """题目集管理对话框"""
    
    def __init__(self, parent=None):
        """
        初始化题目集管理对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.parent = parent
        self.lang = get_default_lang()
        self.selected_set_id = None
        
        self.setup_ui()
        self.setup_connections()
        self.load_question_sets()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("题目集管理")
        self.resize(800, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建上部分的题目集列表
        self.sets_group = QGroupBox("已保存的题目集")
        sets_layout = QVBoxLayout()
        
        # 创建表格显示题目集
        self.sets_table = QTableWidget()
        self.sets_table.setColumnCount(5)
        self.sets_table.setHorizontalHeaderLabels(["标题", "创建时间", "更新时间", "进度", "操作"])
        self.sets_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.sets_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.sets_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        sets_layout.addWidget(self.sets_table)
        
        self.sets_group.setLayout(sets_layout)
        layout.addWidget(self.sets_group)
        
        # 创建下部分的详情区域
        self.details_group = QGroupBox("题目集详情")
        details_layout = QVBoxLayout()
        
        # 题目集信息显示
        self.details_label = QLabel("选择一个题目集以查看详细信息")
        details_layout.addWidget(self.details_label)
        
        # 题目预览区域
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("题目预览将显示在这里")
        details_layout.addWidget(self.preview_text)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        self.continue_button = QPushButton("继续答题")
        self.continue_button.setEnabled(False)
        buttons_layout.addWidget(self.continue_button)
        
        self.restart_button = QPushButton("从头开始")
        self.restart_button.setEnabled(False)
        buttons_layout.addWidget(self.restart_button)
        
        self.delete_button = QPushButton("删除题目集")
        self.delete_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_button)
        
        self.close_button = QPushButton("关闭")
        buttons_layout.addWidget(self.close_button)
        
        details_layout.addLayout(buttons_layout)
        self.details_group.setLayout(details_layout)
        layout.addWidget(self.details_group)
        
        # 应用样式
        apply_anki_style(self)
    
    def setup_connections(self):
        """设置信号连接"""
        self.sets_table.cellClicked.connect(self.on_set_selected)
        self.continue_button.clicked.connect(self.on_continue_clicked)
        self.restart_button.clicked.connect(self.on_restart_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.close_button.clicked.connect(self.accept)
    
    def load_question_sets(self):
        """加载题目集列表"""
        # 清空表格
        self.sets_table.setRowCount(0)
        
        # 加载题目集
        question_sets = load_question_sets()
        
        if not question_sets:
            # 如果没有题目集，显示一个空行
            self.sets_table.setRowCount(1)
            empty_item = QTableWidgetItem("没有保存的题目集")
            empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sets_table.setSpan(0, 0, 1, 5)
            self.sets_table.setItem(0, 0, empty_item)
            return
        
        # 填充表格
        self.sets_table.setRowCount(len(question_sets))
        
        for row, question_set in enumerate(question_sets):
            # 标题
            title_item = QTableWidgetItem(question_set.get("title", "未命名"))
            self.sets_table.setItem(row, 0, title_item)
            
            # 创建时间
            created_at_item = QTableWidgetItem(question_set.get("created_at", ""))
            self.sets_table.setItem(row, 1, created_at_item)
            
            # 更新时间
            updated_at_item = QTableWidgetItem(question_set.get("updated_at", ""))
            self.sets_table.setItem(row, 2, updated_at_item)
            
            # 进度
            questions = question_set.get("questions", {}).get("questions", [])
            current_index = question_set.get("current_index", 0)
            progress_text = f"{current_index}/{len(questions)}"
            progress_item = QTableWidgetItem(progress_text)
            self.sets_table.setItem(row, 3, progress_item)
            
            # 操作单元格
            operation_widget = QWidget()
            operation_layout = QHBoxLayout(operation_widget)
            operation_layout.setContentsMargins(0, 0, 0, 0)
            
            # 点击事件由表格的cellClicked处理，此处只做展示
            view_button = QPushButton("查看")
            view_button.setProperty("set_id", question_set.get("id"))
            operation_layout.addWidget(view_button)
            
            self.sets_table.setCellWidget(row, 4, operation_widget)
            
            # 存储ID到第一列的item中，方便后续操作
            title_item.setData(Qt.ItemDataRole.UserRole, question_set.get("id"))
    
    def on_set_selected(self, row, column):
        """
        选择题目集事件
        
        Args:
            row (int): 行索引
            column (int): 列索引
        """
        # 获取选中行的第一列
        title_item = self.sets_table.item(row, 0)
        if not title_item:
            return
            
        # 获取题目集ID
        set_id = title_item.data(Qt.ItemDataRole.UserRole)
        if not set_id:
            return
            
        self.selected_set_id = set_id
        
        # 获取题目集详情
        question_set = get_question_set_by_id(set_id)
        if not question_set:
            showWarning("无法加载题目集详情")
            return
            
        # 更新详情显示
        self.update_details(question_set)
        
        # 启用按钮
        self.continue_button.setEnabled(True)
        self.restart_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def update_details(self, question_set):
        """
        更新题目集详情显示
        
        Args:
            question_set (dict): 题目集数据
        """
        # 更新题目集信息
        title = question_set.get("title", "未命名")
        created_at = question_set.get("created_at", "")
        current_index = question_set.get("current_index", 0)
        questions = question_set.get("questions", {}).get("questions", [])
        
        info_text = f"<b>题目集:</b> {title}<br>"
        info_text += f"<b>创建时间:</b> {created_at}<br>"
        info_text += f"<b>题目数量:</b> {len(questions)}<br>"
        info_text += f"<b>当前进度:</b> {current_index}/{len(questions)}<br>"
        
        self.details_label.setText(info_text)
        
        # 更新题目预览
        preview_text = ""
        
        for i, question in enumerate(questions):
            # 只预览前3道题，避免过多
            if i >= 3:
                preview_text += f"\n...(共{len(questions)}道题)\n"
                break
                
            question_text = question.get("question", "")
            
            # 格式化显示
            if i == current_index:
                preview_text += f"[当前] 问题 {i+1}/{len(questions)}: {question_text}\n\n"
            else:
                preview_text += f"问题 {i+1}/{len(questions)}: {question_text}\n\n"
        
        self.preview_text.setPlainText(preview_text)
    
    def on_continue_clicked(self):
        """继续答题按钮点击事件"""
        if not self.selected_set_id:
            return
            
        # 获取题目集
        question_set = get_question_set_by_id(self.selected_set_id)
        if not question_set:
            showWarning("无法加载题目集")
            return
            
        # 显示复习对话框，从当前进度继续
        questions = question_set.get("questions", {})
        current_index = question_set.get("current_index", 0)
        
        # 关闭当前对话框
        self.accept()
        
        # 打开复习对话框，并传入题目集ID以便更新进度
        dialog = show_review_dialog(questions=questions, parent=self.parent)
        
        # 设置当前索引
        if hasattr(dialog, 'controller'):
            # 设置当前题目集ID
            dialog.controller.question_set_id = self.selected_set_id
            # 设置当前索引
            dialog.controller.current_question_index = current_index
            # 显示对应的问题
            dialog.controller.show_current_question()
    
    def on_restart_clicked(self):
        """从头开始按钮点击事件"""
        if not self.selected_set_id:
            return
            
        # 获取题目集
        question_set = get_question_set_by_id(self.selected_set_id)
        if not question_set:
            showWarning("无法加载题目集")
            return
            
        # 显示复习对话框，从头开始
        questions = question_set.get("questions", {})
        
        # 关闭当前对话框
        self.accept()
        
        # 打开复习对话框，并传入题目集ID以便更新进度
        dialog = show_review_dialog(questions=questions, parent=self.parent)
        
        # 设置当前索引为0
        if hasattr(dialog, 'controller'):
            dialog.controller.current_question_index = 0
            dialog.controller.question_set_id = self.selected_set_id
            dialog.controller.show_current_question()
    
    def on_delete_clicked(self):
        """删除题目集按钮点击事件"""
        if not self.selected_set_id:
            return
            
        # 确认是否删除
        from aqt import qt
        result = qt.QMessageBox.question(
            self,
            "确认删除", 
            "确定要删除选中的题目集吗？此操作无法恢复。",
            qt.QMessageBox.StandardButton.Yes | qt.QMessageBox.StandardButton.No,
            qt.QMessageBox.StandardButton.No
        )
            
        if result != qt.QMessageBox.StandardButton.Yes:
            return
            
        # 删除题目集
        if delete_question_set(self.selected_set_id):
            showInfo("题目集已删除")
            
            # 重新加载题目集列表
            self.load_question_sets()
            
            # 清空详情显示
            self.details_label.setText("选择一个题目集以查看详细信息")
            self.preview_text.clear()
            
            # 禁用按钮
            self.continue_button.setEnabled(False)
            self.restart_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            
            # 清除选择
            self.selected_set_id = None
        else:
            showWarning("删除题目集失败")


def show_question_sets_dialog(parent=None):
    """
    显示题目集管理对话框
    
    Args:
        parent: 父窗口
        
    Returns:
        QuestionSetsDialog: 创建的对话框实例
    """
    dialog = QuestionSetsDialog(parent)
    dialog.show()
    return dialog 