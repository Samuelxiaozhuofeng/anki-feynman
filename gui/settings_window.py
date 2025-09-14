from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showWarning
import json
import requests
from ..utils.ai_handler import AIHandler
from ..lang.messages import get_message, get_default_lang

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = mw.addonManager.getConfig(__name__)
        self.lang = get_default_lang()  # 使用Anki语言设置初始化
        self.setup_ui()
        self.load_config()
        self.setup_connections()

    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(get_message("settings_window_title", self.lang))
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tabWidget = QTabWidget()
        
        # 创建基本设置标签页
        self.basicTab = QWidget()
        self.setupBasicTab()
        self.tabWidget.addTab(self.basicTab, get_message("basic_settings", self.lang))
        
        # 创建模型管理标签页
        self.modelsTab = QWidget()
        self.setupModelsTab()
        self.tabWidget.addTab(self.modelsTab, get_message("model_management", self.lang))
        
        layout.addWidget(self.tabWidget)
        
        # 按钮区域
        buttonLayout = QHBoxLayout()
        self.saveButton = QPushButton(get_message("btn_save", self.lang))
        self.cancelButton = QPushButton(get_message("btn_cancel", self.lang))
        
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonLayout)
        
        # 设置为非模态窗口，允许用户同时刷卡
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 应用Anki样式
        self.apply_anki_style()

    def setupBasicTab(self):
        """设置基本设置标签页"""
        layout = QVBoxLayout(self.basicTab)
        
        # AI服务提供商选择
        providerGroup = QGroupBox(get_message("ai_provider", self.lang))
        providerLayout = QVBoxLayout()
        
        self.openaiRadio = QRadioButton("OpenAI")
        self.customRadio = QRadioButton(get_message("custom_ai", self.lang))
        providerLayout.addWidget(self.openaiRadio)
        providerLayout.addWidget(self.customRadio)
        providerGroup.setLayout(providerLayout)
        layout.addWidget(providerGroup)
        
        # OpenAI设置
        self.openaiGroup = QGroupBox(get_message("openai_settings", self.lang))
        openaiLayout = QFormLayout()
        
        self.openaiKeyEdit = QLineEdit()
        self.openaiKeyEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openaiModelCombo = QComboBox()
        self.openaiModelCombo.addItems(["gpt-3.5-turbo", "gpt-4"])
        
        openaiLayout.addRow("API Key:", self.openaiKeyEdit)
        openaiLayout.addRow(f"{get_message('model', self.lang)}:", self.openaiModelCombo)
        self.openaiGroup.setLayout(openaiLayout)
        layout.addWidget(self.openaiGroup)
        
        # 自定义AI设置
        self.customGroup = QGroupBox(get_message("custom_settings", self.lang))
        customLayout = QFormLayout()
        
        self.customUrlEdit = QLineEdit()
        self.customKeyEdit = QLineEdit()
        self.customKeyEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.customModelEdit = QLineEdit()
        
        customLayout.addRow("API URL:", self.customUrlEdit)
        customLayout.addRow("API Key:", self.customKeyEdit)
        customLayout.addRow(f"{get_message('model_name', self.lang)}:", self.customModelEdit)
        self.customGroup.setLayout(customLayout)
        layout.addWidget(self.customGroup)
        
        # 通用AI设置
        commonGroup = QGroupBox(get_message("common_settings", self.lang))
        commonLayout = QFormLayout()
        
        self.maxTokensSpinBox = QSpinBox()
        self.maxTokensSpinBox.setRange(100, 999999)
        self.maxTokensSpinBox.setValue(8000)
        
        self.temperatureSpinBox = QDoubleSpinBox()
        self.temperatureSpinBox.setRange(0.0, 1.0)
        self.temperatureSpinBox.setSingleStep(0.1)
        self.temperatureSpinBox.setValue(0.7)
        
        commonLayout.addRow(f"{get_message('max_tokens', self.lang)}:", self.maxTokensSpinBox)
        commonLayout.addRow(f"{get_message('temperature', self.lang)}:", self.temperatureSpinBox)
        commonGroup.setLayout(commonLayout)
        layout.addWidget(commonGroup)
        
        # 测试连接按钮
        self.testButton = QPushButton(get_message("test_connection", self.lang))
        layout.addWidget(self.testButton)

    def setupModelsTab(self):
        """设置模型管理标签页"""
        layout = QVBoxLayout(self.modelsTab)
        
        # 提示信息
        infoLabel = QLabel(get_message("model_management_info", self.lang))
        infoLabel.setWordWrap(True)
        layout.addWidget(infoLabel)
        
        # 模型列表
        self.modelListGroup = QGroupBox(get_message("model_list", self.lang))
        modelListLayout = QVBoxLayout()
        
        # 模型列表表格
        self.modelTable = QTableWidget()
        self.modelTable.setColumnCount(2)
        self.modelTable.setHorizontalHeaderLabels([
            get_message("model_name", self.lang),
            get_message("status", self.lang)
        ])
        self.modelTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.modelTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        modelListLayout.addWidget(self.modelTable)
        
        # 按钮区域
        buttonLayout = QHBoxLayout()
        self.addModelButton = QPushButton(get_message("add_model", self.lang))
        self.editModelButton = QPushButton(get_message("edit_model", self.lang))
        self.deleteModelButton = QPushButton(get_message("delete_model", self.lang))
        self.testModelButton = QPushButton(get_message("test_model", self.lang))
        
        buttonLayout.addWidget(self.addModelButton)
        buttonLayout.addWidget(self.editModelButton)
        buttonLayout.addWidget(self.deleteModelButton)
        buttonLayout.addWidget(self.testModelButton)
        
        modelListLayout.addLayout(buttonLayout)
        self.modelListGroup.setLayout(modelListLayout)
        layout.addWidget(self.modelListGroup)
        
        # 模型编辑区域
        self.modelEditGroup = QGroupBox(get_message("model_edit", self.lang))
        modelEditLayout = QFormLayout()
        
        self.modelNameEdit = QLineEdit()
        modelEditLayout.addRow(get_message("model_name", self.lang) + ":", self.modelNameEdit)
        
        # 添加API设置区域
        # API设置选项
        self.apiSettingsGroup = QGroupBox(get_message("api_settings", self.lang))
        apiSettingsLayout = QVBoxLayout()
        
        # 使用默认API设置选项
        self.useDefaultApiCheck = QCheckBox(get_message("use_default_api", self.lang))
        self.useDefaultApiCheck.setChecked(True)
        apiSettingsLayout.addWidget(self.useDefaultApiCheck)
        
        # 自定义API设置
        self.customApiGroup = QGroupBox(get_message("custom_api_settings", self.lang))
        customApiLayout = QFormLayout()
        
        self.modelApiUrlEdit = QLineEdit()
        self.modelApiKeyEdit = QLineEdit()
        self.modelApiKeyEdit.setEchoMode(QLineEdit.EchoMode.Password)
        
        customApiLayout.addRow("API URL:", self.modelApiUrlEdit)
        customApiLayout.addRow("API Key:", self.modelApiKeyEdit)
        
        self.customApiGroup.setLayout(customApiLayout)
        apiSettingsLayout.addWidget(self.customApiGroup)
        
        self.apiSettingsGroup.setLayout(apiSettingsLayout)
        modelEditLayout.addRow("", self.apiSettingsGroup)
        
        # 保存和取消按钮
        editButtonLayout = QHBoxLayout()
        self.saveModelButton = QPushButton(get_message("save_model", self.lang))
        self.cancelModelButton = QPushButton(get_message("cancel", self.lang))
        
        editButtonLayout.addStretch()
        editButtonLayout.addWidget(self.saveModelButton)
        editButtonLayout.addWidget(self.cancelModelButton)
        
        modelEditLayout.addRow("", editButtonLayout)
        self.modelEditGroup.setLayout(modelEditLayout)
        layout.addWidget(self.modelEditGroup)
        
        # 初始状态
        self.modelEditGroup.setVisible(False)
        
        # 连接API设置选择信号
        self.useDefaultApiCheck.toggled.connect(self.on_api_setting_changed)

    def on_api_setting_changed(self):
        """处理API设置选择变更"""
        use_default = self.useDefaultApiCheck.isChecked()
        self.customApiGroup.setEnabled(not use_default)

    def setup_connections(self):
        """设置信号连接"""
        # 基本设置标签页
        self.openaiRadio.toggled.connect(self.on_provider_changed)
        self.customRadio.toggled.connect(self.on_provider_changed)
        self.testButton.clicked.connect(self.test_connection)
        
        # 模型管理标签页
        self.addModelButton.clicked.connect(self.add_model)
        self.editModelButton.clicked.connect(self.edit_model)
        self.deleteModelButton.clicked.connect(self.delete_model)
        self.testModelButton.clicked.connect(self.test_model)
        self.saveModelButton.clicked.connect(self.save_model)
        self.cancelModelButton.clicked.connect(self.cancel_model_edit)
        self.useDefaultApiCheck.toggled.connect(self.on_api_setting_changed)
        
        # 全局按钮
        self.saveButton.clicked.connect(self.save_config)
        self.cancelButton.clicked.connect(self.reject)

    def load_config(self):
        """加载配置"""
        # 检查并更新UI语言设置
        current_anki_lang = get_default_lang()
        if self.config.get('ui', {}).get('language') != current_anki_lang:
            if 'ui' not in self.config:
                self.config['ui'] = {}
            self.config['ui']['language'] = current_anki_lang
            mw.addonManager.writeConfig(__name__, self.config)
            self.lang = current_anki_lang

        ai_config = self.config.get('ai_service', {})
        provider = ai_config.get('provider', 'openai')
        
        # 设置服务提供商
        if provider == 'openai':
            self.openaiRadio.setChecked(True)
        else:
            self.customRadio.setChecked(True)
        
        # 加载OpenAI设置
        openai_config = ai_config.get('openai', {})
        self.openaiKeyEdit.setText(openai_config.get('api_key', ''))
        self.openaiModelCombo.setCurrentText(openai_config.get('model', 'gpt-3.5-turbo'))
        
        # 加载自定义AI设置
        custom_config = ai_config.get('custom', {})
        self.customUrlEdit.setText(custom_config.get('api_url', ''))
        self.customKeyEdit.setText(custom_config.get('api_key', ''))
        self.customModelEdit.setText(custom_config.get('model', ''))
        
        # 加载通用设置
        self.maxTokensSpinBox.setValue(openai_config.get('max_tokens', 2000))
        self.temperatureSpinBox.setValue(openai_config.get('temperature', 0.7))
        
        # 加载模型列表
        self.load_models()

    def load_models(self):
        """加载模型列表"""
        models = self.config.get('models', [])
        self.modelTable.setRowCount(len(models))
        
        for i, model in enumerate(models):
            self.modelTable.setItem(i, 0, QTableWidgetItem(model.get('name', '')))
            self.modelTable.setItem(i, 1, QTableWidgetItem(get_message("not_tested", self.lang)))

    def save_config(self):
        """保存配置"""
        config = self.config.copy()
        
        # 更新AI服务配置
        config['ai_service'] = {
            'provider': 'openai' if self.openaiRadio.isChecked() else 'custom',
            'openai': {
                'api_key': self.openaiKeyEdit.text(),
                'model': self.openaiModelCombo.currentText(),
                'max_tokens': self.maxTokensSpinBox.value(),
                'temperature': self.temperatureSpinBox.value(),
                'request_timeout': 180
            },
            'custom': {
                'api_url': self.customUrlEdit.text(),
                'api_key': self.customKeyEdit.text(),
                'model': self.customModelEdit.text(),
                'max_tokens': self.maxTokensSpinBox.value(),
                'temperature': self.temperatureSpinBox.value(),
                'request_timeout': 300  # 增加自定义API的超时时间，特别是为了支持Claude模型
            }
        }
        
        # 确保模型列表被保存
        if 'models' not in config:
            config['models'] = []
            
        # 为Claude模型配置特殊设置
        for model in config['models']:
            if 'name' in model and 'claude' in model['name'].lower():
                # 为Claude模型设置更长的超时时间
                model['request_timeout'] = 300
        
        # 保存配置
        mw.addonManager.writeConfig(__name__, config)
        
        # 如果InputWindow已经打开，更新其模型列表
        self.update_input_window_models()
        
        showInfo(get_message("settings_saved", self.lang))
        self.accept()

    def test_connection(self):
        """测试AI服务连接"""
        try:
            if self.openaiRadio.isChecked():
                self._test_openai_connection()
            else:
                self._test_custom_connection()
        except Exception as e:
            showWarning(f"{get_message('connection_failed', self.lang)}{str(e)}")

    def _test_openai_connection(self):
        """测试OpenAI连接"""
        api_key = self.openaiKeyEdit.text()
        if not api_key:
            showWarning(get_message("enter_api_key", self.lang))
            return
        
        # 创建临时配置
        temp_config = {
            'ai_service': {
                'provider': 'openai',
                'openai': {
                    'api_key': api_key,
                    'model': self.openaiModelCombo.currentText(),
                    'max_tokens': self.maxTokensSpinBox.value(),
                    'temperature': self.temperatureSpinBox.value()
                }
            }
        }
        
        try:
            # 创建临时AIHandler实例进行测试
            handler = AIHandler(temp_config)
            # 尝试一个简单的API调用
            response = handler._call_ai_api([{"role": "user", "content": "测试连接"}])
            if response:
                showInfo(get_message("openai_success", self.lang))
        except Exception as e:
            raise Exception(f"{get_message('openai_failed', self.lang)}{str(e)}")

    def _test_custom_connection(self):
        """测试自定义AI服务连接"""
        api_url = self.customUrlEdit.text()
        api_key = self.customKeyEdit.text()
        
        if not api_url or not api_key:
            showWarning(get_message("enter_api_info", self.lang))
            return
        
        try:
            # 发送测试请求
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            response = requests.post(
                api_url,
                headers=headers,
                json={
                    "messages": [{"role": "user", "content": "测试连接"}],
                    "model": self.customModelEdit.text(),
                    "max_tokens": 10
                },
                timeout=30
            )
            response.raise_for_status()
            showInfo(get_message("custom_success", self.lang))
        except Exception as e:
            raise Exception(f"{get_message('custom_failed', self.lang)}{str(e)}")

    def on_provider_changed(self):
        """处理服务提供商切换"""
        is_openai = self.openaiRadio.isChecked()
        self.openaiGroup.setEnabled(is_openai)
        self.customGroup.setEnabled(not is_openai)

    # 模型管理相关方法
    def add_model(self):
        """添加新模型"""
        self.current_edit_index = -1
        self.modelNameEdit.clear()
        self.useDefaultApiCheck.setChecked(True)
        self.modelApiUrlEdit.clear()
        self.modelApiKeyEdit.clear()
        self.modelEditGroup.setVisible(True)
        self.on_api_setting_changed()

    def edit_model(self):
        """编辑选中的模型"""
        selected_rows = self.modelTable.selectedIndexes()
        if not selected_rows:
            showWarning(get_message("select_model", self.lang))
            return
        
        row = selected_rows[0].row()
        self.current_edit_index = row
        
        models = self.config.get('models', [])
        if row < len(models):
            model = models[row]
            self.modelNameEdit.setText(model.get('name', ''))
            
            # 加载API设置
            has_custom_api = 'api_url' in model and 'api_key' in model
            self.useDefaultApiCheck.setChecked(not has_custom_api)
            
            if has_custom_api:
                self.modelApiUrlEdit.setText(model.get('api_url', ''))
                self.modelApiKeyEdit.setText(model.get('api_key', ''))
            else:
                self.modelApiUrlEdit.clear()
                self.modelApiKeyEdit.clear()
                
            self.on_api_setting_changed()
            self.modelEditGroup.setVisible(True)

    def delete_model(self):
        """删除选中的模型"""
        selected_rows = self.modelTable.selectedIndexes()
        if not selected_rows:
            showWarning(get_message("select_model", self.lang))
            return
        
        row = selected_rows[0].row()
        models = self.config.get('models', [])
        
        if row < len(models):
            del models[row]
            self.config['models'] = models
            self.load_models()

    def save_model(self):
        """保存模型设置"""
        model_name = self.modelNameEdit.text().strip()
        if not model_name:
            showWarning(get_message("enter_model_name", self.lang))
            return
            
        # 创建模型配置
        model_config = {
            'name': model_name,
        }
        
        # 如果是Claude模型，添加特殊设置
        is_claude_model = "claude" in model_name.lower()
        
        # 如果不使用默认API设置，添加自定义API设置
        if not self.useDefaultApiCheck.isChecked():
            api_url = self.modelApiUrlEdit.text()
            api_key = self.modelApiKeyEdit.text()
            
            if not api_url or not api_key:
                showWarning(get_message("enter_api_info", self.lang))
                return
                
            model_config['api_url'] = api_url
            model_config['api_key'] = api_key
            
        # 为Claude模型设置特殊参数
        if is_claude_model:
            model_config['request_timeout'] = 300  # 增加超时时间
            model_config['max_tokens'] = 4000     # 限制最大token数
            
        # 获取现有模型列表
        models = self.config.get('models', [])
        
        if self.current_edit_index >= 0 and self.current_edit_index < len(models):
            # 更新现有模型
            models[self.current_edit_index] = model_config
        else:
            # 添加新模型
            models.append(model_config)
            
        # 更新配置
        self.config['models'] = models
        
        # 刷新表格
        self.load_models()
        
        # 隐藏编辑区域
        self.modelEditGroup.setVisible(False)
        
        # 如果是Claude模型，显示提示
        if is_claude_model:
            showInfo(get_message("claude_model_notice", self.lang) or 
                    "已为Claude模型设置特殊参数：增加超时时间和限制Token数量，这有助于提高连接稳定性。")

    def update_input_window_models(self):
        """更新已打开的InputWindow和LanguageWindow的模型列表"""
        # 查找所有打开的窗口
        for window in QApplication.topLevelWidgets():
            # 更新InputWindow
            if window.__class__.__name__ == 'FeynmanInputDialog':
                if hasattr(window, 'update_models'):
                    window.update_models()
            
            # 更新LanguageWindow
            if window.__class__.__name__ == 'LanguageWindow':
                if hasattr(window, 'settings_panel') and hasattr(window.settings_panel, 'load_models'):
                    window.settings_panel.load_models()

    def cancel_model_edit(self):
        """取消模型编辑"""
        self.modelEditGroup.setVisible(False)

    def test_model(self):
        """测试选中的模型连接"""
        selected_rows = self.modelTable.selectedIndexes()
        if not selected_rows:
            showWarning(get_message("select_model", self.lang))
            return
        
        row = selected_rows[0].row()
        models = self.config.get('models', [])
        
        if row < len(models):
            model = models[row]
            try:
                self._test_model_connection(model)
                # 更新状态
                self.modelTable.setItem(row, 1, QTableWidgetItem(get_message("connection_success", self.lang)))
            except Exception as e:
                self.modelTable.setItem(row, 1, QTableWidgetItem(get_message("connection_failed", self.lang)))
                showWarning(str(e))

    def _test_model_connection(self, model):
        """测试模型连接"""
        # 检查模型是否有自定义API设置
        if 'api_url' in model and 'api_key' in model:
            api_url = model['api_url']
            api_key = model['api_key']
        else:
            # 使用基本设置页面中的自定义API信息
            api_url = self.customUrlEdit.text()
            api_key = self.customKeyEdit.text()
        
        if not api_url or not api_key:
            raise ValueError(get_message("missing_api_info", self.lang))
        
        try:
            # 发送测试请求
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # 使用模型名称
            data = {
                "messages": [{"role": "user", "content": "测试连接"}],
                "model": model.get('name', ''),
                "max_tokens": 10
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            showInfo(f"{model.get('name')} {get_message('connection_success', self.lang)}")
        except Exception as e:
            raise Exception(f"{model.get('name')} {get_message('connection_failed', self.lang)}: {str(e)}")

    def apply_anki_style(self):
        """应用Anki样式"""
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
            self.setStyleSheet("""
                QDialog {
                    background-color: #2d2d2d;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #64b5f6;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px;
                }
                QRadioButton {
                    color: #e0e0e0;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QTableWidget {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QHeaderView::section {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #2d2d2d;
                }
                QTabBar::tab {
                    background-color: #383838;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    border-bottom-color: #555555;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #1976D2;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    margin-top: 1em;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    color: #2196F3;
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px 0 3px;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
                QTableWidget {
                    border: 1px solid #cccccc;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-bottom-color: #cccccc;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 8ex;
                    padding: 5px;
                }
                QTabBar::tab:selected {
                    background-color: #2196F3;
                    color: white;
                }
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
            """) 