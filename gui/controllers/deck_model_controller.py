"""
牌组和模型控制器模块
"""
from aqt import mw
from ...lang.messages import get_message

class DeckModelController:
    """牌组和模型控制器，负责加载牌组、模型和模板数据"""
    
    def __init__(self, dialog):
        """
        初始化控制器
        
        参数:
        dialog -- 持有对话框的引用
        """
        self.dialog = dialog
        self.config = mw.addonManager.getConfig(__name__)
        
    def load_decks(self):
        """加载所有牌组到下拉框"""
        if not hasattr(self.dialog.ui, 'deckComboBox'):
            return
            
        self.dialog.ui.deckComboBox.clear()
        for deck in mw.col.decks.all_names_and_ids():
            self.dialog.ui.deckComboBox.addItem(deck.name, deck.id)
        
        # 加载模型列表
        self.load_models()
        
    def load_models(self):
        """加载模型列表到下拉框"""
        if not hasattr(self.dialog.ui, 'modelComboBox') or not hasattr(self.dialog.ui, 'followUpModelComboBox'):
            return
            
        # 保留默认选项
        default_item = self.dialog.ui.modelComboBox.itemText(0)
        self.dialog.ui.modelComboBox.clear()
        self.dialog.ui.modelComboBox.addItem(default_item, "")
        
        # 同样为追加提问模型保留默认选项
        default_followup_item = self.dialog.ui.followUpModelComboBox.itemText(0)
        self.dialog.ui.followUpModelComboBox.clear()
        self.dialog.ui.followUpModelComboBox.addItem(default_followup_item, "")
        
        # 从配置中加载模型
        config = mw.addonManager.getConfig(__name__)
        models = config.get('models', [])
        
        for model in models:
            model_name = model.get('name', '')
            if model_name:
                self.dialog.ui.modelComboBox.addItem(model_name, model_name)
                self.dialog.ui.followUpModelComboBox.addItem(model_name, model_name)
                
    def load_templates(self):
        """加载提示词模板"""
        if not hasattr(self.dialog.ui, 'templateComboBox'):
            return
            
        self.dialog.ui.templateComboBox.clear()
        
        # 从配置中加载模板
        config = mw.addonManager.getConfig(__name__)
        templates = config.get('prompt_templates', [])
        
        if not templates:
            # 如果没有模板，添加默认示例
            self.dialog.ui.templateComboBox.addItem(
                get_message("no_templates", self.dialog.lang), 
                ""
            )
        else:
            for template in templates:
                template_name = template.get('name', '')
                if template_name:
                    self.dialog.ui.templateComboBox.addItem(
                        template_name, 
                        template.get('id', '')
                    ) 