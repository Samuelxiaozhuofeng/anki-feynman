from aqt.qt import *
from aqt.utils import showInfo, showWarning, tooltip
from PyQt6.QtCore import QThread
from ...utils.ai_handler import AIHandler
from ..workers.language_pattern_worker import LanguagePatternWorker
from ...config.language_levels import LANGUAGE_LEVELS

class LanguageController:
    """语言学习控制器"""
    
    def __init__(self, window):
        self.window = window
        self.ai_handler = None
        self.pattern_examples = []
        self.thread = None
        self.worker = None
        self.selected_model = None  # 存储当前选择的模型
        self.setup_connections()
        
    def setup_connections(self):
        """设置信号连接"""
        # 连接UI组件的信号到控制器方法
        self.window.settings_panel.languageChanged.connect(self.on_language_changed)
        self.window.settings_panel.levelChanged.connect(self.on_level_changed)
        self.window.settings_panel.examplesCountChanged.connect(self.on_examples_count_changed)
        self.window.settings_panel.modelChanged.connect(self.on_model_changed)
        
        self.window.input_panel.generateClicked.connect(self.on_generate_clicked)
        self.window.result_panel.addReplacementRequested.connect(self.add_more_replacements)
        
    def on_language_changed(self, language):
        """处理语言变化"""
        print(f"语言已更改为: {language}")
        # 可能的更多处理...
        
    def on_level_changed(self, level):
        """处理级别变化"""
        print(f"级别已更改为: {level}")
        # 如果已经有结果显示，添加提示
        if self.window.result_panel.analysis_text.toPlainText():
            self.window.status_label.setText(f"级别已更改为 {level}，再次点击生成按钮以应用新级别")
            self.window.status_label.setStyleSheet("color: #FF9500; font-weight: bold;")
        else:
            tooltip(f"{self.window.settings_panel.get_language()}级别已设置为 {level}")
            
    def on_examples_count_changed(self, value):
        """处理例句数量变化"""
        print(f"例句数量已更改为: {value}")
        # 如果已经有结果显示，添加提示
        if self.window.result_panel.analysis_text.toPlainText():
            self.window.status_label.setText(f"例句数量已设置为 {value}，再次点击生成按钮以应用新设置")
            self.window.status_label.setStyleSheet("color: #FF9500; font-weight: bold;")
            
    def on_model_changed(self, model):
        """处理模型变化"""
        self.selected_model = model
        print(f"AI模型已更改为: {model if model else '默认模型'}")
        # 如果已经有结果显示，添加提示
        if self.window.result_panel.analysis_text.toPlainText():
            model_name = model if model else '默认模型'
            self.window.status_label.setText(f"AI模型已更改为 {model_name}，再次点击生成按钮以应用新模型")
            self.window.status_label.setStyleSheet("color: #FF9500; font-weight: bold;")
        else:
            model_name = model if model else '默认模型'
            tooltip(f"AI模型已设置为 {model_name}")
            
    def on_generate_clicked(self):
        """处理生成按钮点击"""
        # 获取当前句子
        sentence = self.window.input_panel.get_sentence()
        if not sentence:
            showWarning("请输入一个句子")
            return
            
        # 获取当前设置
        target_language = self.window.settings_panel.get_language()
        language_level = self.window.settings_panel.get_level()
        examples_count = self.window.settings_panel.get_examples_count()
        
        # 获取用户指定的替换部分
        specified_parts = self.window.input_panel.get_specified_parts()
        
        # 获取当前所选模型
        selected_model = self.window.settings_panel.get_model()
        
        print(f"正在生成 {target_language} ({language_level}) 的语言模式练习，每个部分 {examples_count} 个例句，使用模型: {selected_model if selected_model else '默认模型'}")
        
        # 清空之前的结果
        self.window.result_panel.clear()
        self.window.examples_panel.clear_examples()
        
        # 显示加载状态
        self.window.status_label.setText("正在处理...")
        self.window.input_panel.generate_button.setEnabled(False)
        
        # 初始化AI处理器
        if not self.ai_handler:
            self.ai_handler = AIHandler()
            
        # 如果选择了特定模型，设置AI处理器使用该模型
        if selected_model:
            self.ai_handler.set_model(selected_model)
            
        # 创建工作线程
        self.worker = LanguagePatternWorker(
            self.ai_handler, 
            sentence, 
            target_language, 
            specified_parts, 
            language_level, 
            examples_count
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.response_ready.connect(self.on_pattern_generated)
        self.worker.error_occurred.connect(self.on_generation_error)
        
        # 启动线程
        self.thread.start()
        
    def on_pattern_generated(self, response):
        """处理生成的语言模式练习内容"""
        self.window.status_label.setText("")
        self.window.input_panel.generate_button.setEnabled(True)
        
        # 获取当前语言和级别信息
        current_language = self.window.settings_panel.get_language()
        current_level = self.window.settings_panel.get_level()
        
        # 显示句型分析和可替换部分（合并显示）
        analysis_text = response.get('analysis', '')
        replaceable_parts = response.get('replaceable_parts', '')
        self.window.result_panel.set_analysis(current_language, current_level, analysis_text, replaceable_parts)
            
        # 显示替换示例
        if 'examples' in response:
            self.pattern_examples = response['examples']
            examples_count = self.window.settings_panel.get_examples_count()
            specified_parts = self.window.input_panel.get_specified_parts()
            self.window.examples_panel.display_examples(
                self.pattern_examples, 
                current_language, 
                current_level, 
                examples_count,
                specified_parts
            )
            
    def on_generation_error(self, error_message):
        """处理生成过程中发生的错误"""
        self.window.status_label.setText("")
        self.window.input_panel.generate_button.setEnabled(True)
        showWarning(f"生成失败: {error_message}")
        
    def add_more_replacements(self, new_part):
        """处理添加更多替换部分"""
        if not new_part:
            showWarning("请输入要替换的部分")
            return
        
        # 获取当前句子
        sentence = self.window.input_panel.get_sentence()
        if not sentence:
            showWarning("请先输入句子")
            return
        
        # 获取目标语言和级别
        target_language = self.window.settings_panel.get_language()
        language_level = self.window.settings_panel.get_level()
        examples_count = self.window.settings_panel.get_examples_count()
        
        # 获取当前所选模型
        selected_model = self.window.settings_panel.get_model()
        
        print(f"追加替换使用语言: {target_language}, 级别: {language_level}, 例句数量: {examples_count}, 模型: {selected_model if selected_model else '默认模型'}")
        
        # 显示加载状态
        self.window.status_label.setText("正在处理新的替换部分...")
        self.window.result_panel.enable_add_button(False)
        
        # 初始化AI处理器
        if not self.ai_handler:
            self.ai_handler = AIHandler()
            
        # 如果选择了特定模型，设置AI处理器使用该模型
        if selected_model:
            self.ai_handler.set_model(selected_model)
        
        # 创建工作线程
        self.worker = LanguagePatternWorker(
            self.ai_handler, 
            sentence, 
            target_language, 
            [new_part], 
            language_level, 
            examples_count
        )
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        
        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # 设置响应处理
        self.worker.response_ready.connect(self.on_additional_examples_generated)
        self.worker.error_occurred.connect(self.on_additional_generation_error)
        
        # 启动线程
        self.thread.start()
        
    def on_additional_examples_generated(self, response):
        """处理生成的追加替换例句"""
        self.window.status_label.setText("")
        self.window.result_panel.enable_add_button(True)
        
        # 添加新的例句到已有例句列表
        if 'examples' in response:
            # 将新例句添加到现有例句中
            self.pattern_examples.extend(response['examples'])
            
            # 重新显示所有例句
            current_language = self.window.settings_panel.get_language()
            current_level = self.window.settings_panel.get_level()
            examples_count = self.window.settings_panel.get_examples_count()
            
            # 更新指定替换部分列表
            if self.window.input_panel.get_specified_parts():
                parts = self.window.input_panel.get_specified_parts()
            else:
                parts = []
                
            # 添加新的替换部分
            new_part_from_response = response['examples'][0].get("replaced_part", "") if response['examples'] else ""
            if new_part_from_response and new_part_from_response not in parts:
                parts.append(new_part_from_response)
                
            # 重新显示例句
            self.window.examples_panel.display_examples(
                self.pattern_examples, 
                current_language, 
                current_level, 
                examples_count,
                parts
            )
            
            # 将新替换部分添加到输入面板的替换部分
            if parts:
                self.window.input_panel.specify_checkbox.setChecked(True)
                self.window.input_panel.parts_to_replace_edit.setText(", ".join(parts))
    
    def on_additional_generation_error(self, error_message):
        """处理生成追加例句过程中发生的错误"""
        self.window.status_label.setText("")
        self.window.result_panel.enable_add_button(True)
        showWarning(f"生成追加例句失败: {error_message}") 