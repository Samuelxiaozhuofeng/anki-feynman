"""
Feynman输入对话框模块

该模块提供Feynman方法学习插件的主输入界面
"""
from aqt.qt import *
from aqt import mw
import os
from ..lang.messages import get_message, get_default_lang
from .components.input_dialog_ui import InputDialogUI
from .controllers.deck_model_controller import DeckModelController
from .controllers.input_events_controller import InputEventsController
from .controllers.question_controller import QuestionController

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class FeynmanInputDialog(QDialog):
    """Feynman方法学习的输入对话框类"""
    
    def __init__(self, parent=None):
        """
        初始化对话框

        参数:
        parent -- 父窗口
        """
        super().__init__(parent)
        self.config = mw.addonManager.getConfig(__name__)
        self.lang = get_default_lang()  # 使用Anki语言设置初始化

        # 初始化标志，防止在初始化过程中触发保存
        self._initializing = True

        # 使用组合模式创建各个组件
        self.ui = InputDialogUI(self, self.lang)
        self.question_controller = QuestionController(self)
        self.model_controller = DeckModelController(self)
        self.events_controller = InputEventsController(self, self.question_controller)

        # 初始化
        self.model_controller.load_decks()
        self.events_controller.setup_connections()

        # 加载上次的选择
        self.load_last_selections()

        # 初始化完成
        self._initializing = False
        
    def showEvent(self, event):
        """窗口显示事件，确保加载最新的模型列表"""
        super().showEvent(event)
        # 设置初始化标志，防止在重新加载时触发保存
        self._initializing = True

        # 重新加载配置和模型列表
        self.config = mw.addonManager.getConfig(__name__)
        self.model_controller.load_models()
        # 重新加载上次的选择
        self.load_last_selections()

        # 重新加载完成
        self._initializing = False
        
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
            self.ui.update_ui_texts(self.lang)  # 更新UI文本
    
    def update_models(self):
        """更新模型列表"""
        self.model_controller.load_models()
        
    # 为了兼容性，添加属性代理方法
    
    @property
    def current_questions(self):
        """为了兼容性，代理到question_controller的current_questions属性"""
        return self.question_controller.current_questions

    def load_last_selections(self):
        """加载上次的选择"""
        try:
            config = mw.addonManager.getConfig(__name__)
            last_selections = config.get('last_selections', {})

            # 恢复牌组选择
            last_deck = last_selections.get('deck', '')
            if last_deck and hasattr(self.ui, 'deckComboBox'):
                deck_index = self.ui.deckComboBox.findText(last_deck)
                if deck_index >= 0:
                    self.ui.deckComboBox.setCurrentIndex(deck_index)

            # 恢复问题类型选择
            last_question_type = last_selections.get('question_type', '')
            if last_question_type and hasattr(self.ui, 'questionTypeComboBox'):
                type_index = self.ui.questionTypeComboBox.findText(last_question_type)
                if type_index >= 0:
                    self.ui.questionTypeComboBox.setCurrentIndex(type_index)

            # 恢复模板选择
            last_template = last_selections.get('template', '')
            if last_template and hasattr(self.ui, 'templateComboBox'):
                template_index = self.ui.templateComboBox.findText(last_template)
                if template_index >= 0:
                    self.ui.templateComboBox.setCurrentIndex(template_index)

            # 恢复问题数量
            last_num_questions = last_selections.get('num_questions', 5)
            if hasattr(self.ui, 'numQuestionsSpinBox'):
                self.ui.numQuestionsSpinBox.setValue(last_num_questions)

            # 恢复模型选择
            last_model = last_selections.get('model', '')
            if last_model and hasattr(self.ui, 'modelComboBox'):
                model_index = self.ui.modelComboBox.findText(last_model)
                if model_index >= 0:
                    self.ui.modelComboBox.setCurrentIndex(model_index)

            # 恢复追问模型选择
            last_followup_model = last_selections.get('followup_model', '')
            if last_followup_model and hasattr(self.ui, 'followUpModelComboBox'):
                followup_index = self.ui.followUpModelComboBox.findText(last_followup_model)
                if followup_index >= 0:
                    self.ui.followUpModelComboBox.setCurrentIndex(followup_index)

        except Exception as e:
            print(f"加载上次选择失败: {str(e)}")

    def save_current_selections(self):
        """保存当前的选择"""
        # 如果正在初始化，不保存选择
        if getattr(self, '_initializing', False):
            return

        try:
            config = mw.addonManager.getConfig(__name__)
            if 'last_selections' not in config:
                config['last_selections'] = {}

            # 保存牌组选择
            if hasattr(self.ui, 'deckComboBox'):
                config['last_selections']['deck'] = self.ui.deckComboBox.currentText()

            # 保存问题类型选择
            if hasattr(self.ui, 'questionTypeComboBox'):
                config['last_selections']['question_type'] = self.ui.questionTypeComboBox.currentText()

            # 保存模板选择
            if hasattr(self.ui, 'templateComboBox'):
                config['last_selections']['template'] = self.ui.templateComboBox.currentText()

            # 保存问题数量
            if hasattr(self.ui, 'numQuestionsSpinBox'):
                config['last_selections']['num_questions'] = self.ui.numQuestionsSpinBox.value()

            # 保存模型选择
            if hasattr(self.ui, 'modelComboBox'):
                config['last_selections']['model'] = self.ui.modelComboBox.currentText()

            # 保存追问模型选择
            if hasattr(self.ui, 'followUpModelComboBox'):
                config['last_selections']['followup_model'] = self.ui.followUpModelComboBox.currentText()

            # 写入配置文件
            mw.addonManager.writeConfig(__name__, config)

        except Exception as e:
            print(f"保存当前选择失败: {str(e)}")
        
    @property
    def current_question_index(self):
        """为了兼容性，代理到question_controller的current_question_index属性"""
        return self.question_controller.current_question_index
        
    @property
    def deckComboBox(self):
        """为了兼容性，代理到ui的deckComboBox属性"""
        return self.ui.deckComboBox
        
    @property
    def contentEdit(self):
        """为了兼容性，代理到ui的contentEdit属性"""
        return self.ui.contentEdit
        
    @property
    def review_dialog(self):
        """为了兼容性，代理到question_controller的review_dialog属性"""
        return self.question_controller.review_dialog
        
    @property
    def ai_handler(self):
        """为了兼容性，代理到question_controller的ai_handler属性"""
        return self.question_controller.ai_handler
        
    def on_next_question(self):
        """为了兼容性，代理到question_controller的on_next_question方法"""
        self.question_controller.on_next_question()
        
    def show_current_question(self):
        """为了兼容性，代理到question_controller的show_current_question方法"""
        self.question_controller.show_current_question()

def show_input_dialog():
    """显示输入对话框，返回对话框实例而不是执行结果，以允许非模态使用"""
    dialog = FeynmanInputDialog(mw)
    dialog.show()  # 使用show()而不是exec()，使对话框非模态
    return dialog  # 返回对话框实例 