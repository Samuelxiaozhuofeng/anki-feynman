from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning, tooltip
from ..lang.messages import get_message, get_default_lang
from ..utils.note_types import ensure_language_learning_type
from ..utils.ai_handler import AIHandler
from PyQt6.QtCore import Qt, QThread
from .components.language_example_item import LanguageExampleItem
from .workers.language_pattern_worker import LanguagePatternWorker
from .styles.apple_style import apply_apple_style
from ..config.language_levels import LANGUAGE_LEVELS
from .components.language_settings_panel import LanguageSettingsPanel
from .components.sentence_input_panel import SentenceInputPanel
from .components.analysis_result_panel import AnalysisResultPanel
from .components.examples_display_panel import ExamplesDisplayPanel
from .controllers.language_controller import LanguageController

class LanguageWindow(QDialog):
    """语言模式练习窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lang = get_default_lang()
        self.parent_dialog = parent
        self.ai_handler = None  # AI处理器实例
        self.pattern_examples = []  # 存储生成的例句
        self.current_language_level = None  # 当前选择的语言级别
        self.examples_count = 3  # 默认例句数量为每个替换部分3个
        
        # 创建UI组件
        self.setup_ui()
        
        # 初始化控制器
        self.controller = LanguageController(self)

        # 加载牌组列表
        self.load_decks()

        # 设置默认目标语言
        self.settings_panel.languageComboBox.setCurrentIndex(0)  # 设置第一个选项为默认值
        
        # 应用样式
        apply_apple_style(self)
        
        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("语言模式练习")
        self.resize(1200, 800)
        
        # 主布局为水平布局，左侧为输入和分析，右侧为示例
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧布局（输入和分析区域）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 创建语言设置面板
        self.settings_panel = LanguageSettingsPanel()
        left_layout.addWidget(self.settings_panel)
        
        # 创建输入面板
        self.input_panel = SentenceInputPanel()
        left_layout.addWidget(self.input_panel)
        
        # 创建分析结果面板
        self.result_panel = AnalysisResultPanel()
        left_layout.addWidget(self.result_panel)
        
        # 状态指示器
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.status_label)
        
        # 添加左侧面板到主布局
        main_layout.addWidget(left_panel, 1)  # 左侧占比30%

        # 创建例句展示面板
        self.examples_panel = ExamplesDisplayPanel(self)

        # 添加右侧面板到主布局
        main_layout.addWidget(self.examples_panel, 7)  # 右侧占比70%

    def load_decks(self):
        """加载可用的牌组列表"""
        if not mw.col:
            return
            
        deck_names = [d['name'] for d in mw.col.decks.all()]
        self.settings_panel.load_decks(deck_names)
        

        

        






    def showEvent(self, event):
        """窗口显示事件，确保加载最新的模型列表"""
        super().showEvent(event)
        # 重新加载模型列表
        self.settings_panel.load_models()

def show_language_window(sentence=None):
    """
    显示语言模式练习窗口
    
    Args:
        sentence: 可选参数，如果提供则自动填入句子输入框
        
    Returns:
        LanguageWindow: 创建的窗口实例
    """
    dialog = LanguageWindow(mw)
    
    # 如果提供了句子，自动填入输入框
    if sentence:
        dialog.input_panel.sentence_edit.setPlainText(sentence)
    
    dialog.show()
    return dialog 