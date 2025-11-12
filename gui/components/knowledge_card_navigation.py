"""
知识卡片导航组件
提供卡片切换、计数显示等导航功能
"""
from aqt.qt import QWidget, QHBoxLayout, QLabel, QPushButton, pyqtSignal
from ...lang.messages import get_message, get_default_lang


class KnowledgeCardNavigation(QWidget):
    """知识卡片导航组件"""
    
    # 信号定义
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    preview_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        初始化导航组件
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.lang = get_default_lang()
        self.current_index = 0
        self.total_cards = 0
        self._setup_ui()
        
    def _setup_ui(self):
        """设置UI界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 卡片计数标签
        self.card_count_label = QLabel()
        layout.addWidget(self.card_count_label)
        
        layout.addStretch()
        
        # 导航按钮
        self.prev_button = QPushButton(get_message("prev_card", self.lang))
        self.next_button = QPushButton(get_message("next_card", self.lang))
        self.preview_button = QPushButton(get_message("preview_card", self.lang))
        
        layout.addWidget(self.prev_button)
        layout.addWidget(self.preview_button)
        layout.addWidget(self.next_button)
        
        # 连接信号
        self.prev_button.clicked.connect(self.prev_clicked.emit)
        self.next_button.clicked.connect(self.next_clicked.emit)
        self.preview_button.clicked.connect(self.preview_clicked.emit)
        
    def update_navigation(self, current_index, total_cards):
        """
        更新导航状态
        
        Args:
            current_index: 当前卡片索引（从0开始）
            total_cards: 总卡片数
        """
        self.current_index = current_index
        self.total_cards = total_cards
        
        # 更新卡片计数显示
        self.card_count_label.setText(
            get_message("card_number", self.lang).format(
                current=current_index + 1,
                total=total_cards
            )
        )
        
        # 更新按钮状态
        self.prev_button.setEnabled(current_index > 0)
        self.next_button.setEnabled(current_index < total_cards - 1)
        
    def reset(self):
        """重置导航状态"""
        self.update_navigation(0, 0)

