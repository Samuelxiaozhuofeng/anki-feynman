from aqt.qt import *
from PyQt6.QtCore import Qt, pyqtSignal
from ...config.language_levels import LANGUAGE_LEVELS
from aqt import mw

class LanguageSettingsPanel(QWidget):
    """语言和设置面板"""
    
    languageChanged = pyqtSignal(str)  # 语言变化信号
    levelChanged = pyqtSignal(str)     # 级别变化信号
    examplesCountChanged = pyqtSignal(int)  # 例句数量变化信号
    modelChanged = pyqtSignal(str)     # 模型变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_language_level = None
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 选择目标语言和级别
        language_layout = QHBoxLayout()
        
        # 目标语言选择
        self.languageLabel = QLabel("目标语言:")
        self.languageLabel.setStyleSheet("font-weight: 500;")
        self.languageComboBox = QComboBox()
        self.languageComboBox.addItems(list(LANGUAGE_LEVELS.keys()))
        self.languageComboBox.setMinimumWidth(100)
        self.languageComboBox.currentIndexChanged.connect(self.on_language_changed)
        language_layout.addWidget(self.languageLabel)
        language_layout.addWidget(self.languageComboBox)
        
        # 语言级别选择
        self.levelLabel = QLabel("级别:")
        self.levelLabel.setStyleSheet("font-weight: 500;")
        self.levelComboBox = QComboBox()
        self.levelComboBox.setMinimumWidth(100)
        # 默认填充第一个语言的级别选项
        self.levelComboBox.addItems(LANGUAGE_LEVELS["日语"])
        self.levelComboBox.currentIndexChanged.connect(self.on_level_changed)
        language_layout.addWidget(self.levelLabel)
        language_layout.addWidget(self.levelComboBox)
        
        language_layout.addStretch()
        
        # 牌组选择
        self.deckLabel = QLabel("选择牌组:")
        self.deckLabel.setStyleSheet("font-weight: 500;")
        self.deckComboBox = QComboBox()
        self.deckComboBox.setMinimumWidth(150)
        language_layout.addWidget(self.deckLabel)
        language_layout.addWidget(self.deckComboBox)
        
        main_layout.addLayout(language_layout)
        
        # 添加设置行，包含例句数量设置和模型选择
        settings_layout = QHBoxLayout()
        
        # 例句数量设置
        self.examplesCountLabel = QLabel("每个替换部分的例句数量:")
        self.examplesCountLabel.setStyleSheet("font-weight: 500;")
        settings_layout.addWidget(self.examplesCountLabel)
        
        self.examplesCountSpinner = QSpinBox()
        self.examplesCountSpinner.setMinimum(1)
        self.examplesCountSpinner.setMaximum(5)
        self.examplesCountSpinner.setValue(3)  # 默认3个例句
        self.examplesCountSpinner.setToolTip("设置为每个替换部分生成的例句数量，范围1-5")
        self.examplesCountSpinner.valueChanged.connect(self.on_examples_count_changed)
        settings_layout.addWidget(self.examplesCountSpinner)
        
        settings_layout.addStretch()
        
        # 添加模型选择
        self.modelLabel = QLabel("AI模型:")
        self.modelLabel.setStyleSheet("font-weight: 500;")
        self.modelComboBox = QComboBox()
        self.modelComboBox.addItem("默认模型", "")  # 默认模型选项
        self.modelComboBox.setMinimumWidth(150)
        self.modelComboBox.setToolTip("选择要使用的AI模型")
        self.modelComboBox.currentIndexChanged.connect(self.on_model_changed)
        settings_layout.addWidget(self.modelLabel)
        settings_layout.addWidget(self.modelComboBox)
        
        main_layout.addLayout(settings_layout)
        
        # 初始化加载模型列表
        self.load_models()
        
    def on_language_changed(self):
        """处理语言选择变化"""
        current_language = self.languageComboBox.currentText()
        
        # 更新级别下拉框
        self.levelComboBox.clear()
        if current_language in LANGUAGE_LEVELS:
            self.levelComboBox.addItems(LANGUAGE_LEVELS[current_language])
            # 默认选择第一个级别
            if self.levelComboBox.count() > 0:
                self.levelComboBox.setCurrentIndex(0)
                
        self.languageChanged.emit(current_language)
        
    def on_level_changed(self):
        """处理级别选择变化"""
        if self.levelComboBox.count() > 0:
            previous_level = self.current_language_level
            self.current_language_level = self.levelComboBox.currentText()
            self.levelChanged.emit(self.current_language_level)
            
    def on_examples_count_changed(self, value):
        """处理例句数量变化"""
        self.examplesCountChanged.emit(value)
        
    def on_model_changed(self):
        """处理模型选择变化"""
        current_model = self.modelComboBox.currentData()
        self.modelChanged.emit(current_model)
        
    def get_language(self):
        """获取当前语言"""
        return self.languageComboBox.currentText()
        
    def get_level(self):
        """获取当前级别"""
        return self.current_language_level
        
    def get_examples_count(self):
        """获取例句数量"""
        return self.examplesCountSpinner.value()
        
    def get_deck_name(self):
        """获取当前牌组名称"""
        return self.deckComboBox.currentText()
        
    def get_model(self):
        """获取当前选择的模型"""
        return self.modelComboBox.currentData()
        
    def load_decks(self, deck_names):
        """加载牌组列表"""
        self.deckComboBox.clear()
        self.deckComboBox.addItems(deck_names)
        
    def load_models(self):
        """加载模型列表到下拉框"""
        if not hasattr(self, 'modelComboBox'):
            return
            
        # 保留默认选项
        default_item = self.modelComboBox.itemText(0)
        self.modelComboBox.clear()
        self.modelComboBox.addItem(default_item, "")
        
        # 从配置中加载模型
        config = mw.addonManager.getConfig(__name__)
        models = config.get('models', [])
        
        for model in models:
            model_name = model.get('name', '')
            if model_name:
                self.modelComboBox.addItem(model_name, model_name) 