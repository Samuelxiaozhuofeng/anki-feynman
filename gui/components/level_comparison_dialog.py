from aqt.qt import *
from ...utils.ai_handler import AIHandler

class LevelComparisonDialog(QDialog):
    """级别对比对话框"""
    
    def __init__(self, parent, sentence, language, level1, level2):
        super().__init__(parent)
        self.sentence = sentence
        self.language = language
        self.level1 = level1
        self.level2 = level2
        self.ai_handler = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"{self.language}级别对比 - {self.level1} vs {self.level2}")
        self.resize(900, 600)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        info_label = QLabel(f"<center><b>级别对比</b>: 以下展示同一句子在不同级别下的生成结果</center>")
        info_label.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # 添加原句显示
        sentence_label = QLabel(f"<b>原句</b>: {self.sentence}")
        sentence_label.setWordWrap(True)
        sentence_label.setStyleSheet("font-size: 13px; margin-bottom: 15px;")
        layout.addWidget(sentence_label)
        
        # 创建水平布局放置两个级别的结果
        compare_layout = QHBoxLayout()
        
        # 级别1的结果区域
        level1_widget = QWidget()
        level1_layout = QVBoxLayout(level1_widget)
        
        level1_title = QLabel(f"<center><b>{self.level1}</b> 级别</center>")
        level1_title.setStyleSheet("font-size: 14px; color: #007AFF;")
        level1_layout.addWidget(level1_title)
        
        self.level1_text = QTextEdit()
        self.level1_text.setReadOnly(True)
        self.level1_text.setPlaceholderText("正在生成中...")
        level1_layout.addWidget(self.level1_text)
        
        compare_layout.addWidget(level1_widget)
        
        # 级别2的结果区域
        level2_widget = QWidget()
        level2_layout = QVBoxLayout(level2_widget)
        
        level2_title = QLabel(f"<center><b>{self.level2}</b> 级别</center>")
        level2_title.setStyleSheet("font-size: 14px; color: #FF3B30;")
        level2_layout.addWidget(level2_title)
        
        self.level2_text = QTextEdit()
        self.level2_text.setReadOnly(True)
        self.level2_text.setPlaceholderText("正在生成中...")
        level2_layout.addWidget(self.level2_text)
        
        compare_layout.addWidget(level2_widget)
        
        layout.addLayout(compare_layout)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        # 初始化AI处理器（如果尚未初始化）
        if not self.ai_handler:
            self.ai_handler = AIHandler()
        
        # 生成两个不同级别的结果
        self._generate_comparison_result(self.level1, self.level1_text)
        self._generate_comparison_result(self.level2, self.level2_text)
    
    def _generate_comparison_result(self, level, text_widget):
        """生成特定级别的结果并显示到指定文本框"""
        try:
            # 使用当前设置的例句数量
            examples_count = 3  # 默认值
            
            # 直接调用AI处理器生成结果
            response = self.ai_handler.generate_language_pattern(
                self.sentence, 
                self.language, 
                None, 
                level, 
                examples_count
            )
            
            if 'analysis' in response:
                analysis = response['analysis']
                # 提取前面部分作为简要显示
                brief_analysis = analysis.split('\n\n')[0] if '\n\n' in analysis else analysis
                
                # 获取第一个例句作为示例
                example = ""
                if 'examples' in response and response['examples']:
                    first_example = response['examples'][0]
                    example = f"<b>示例</b>: {first_example.get('sentence', '')}<br><i>{first_example.get('translation', '')}</i>"
                
                # 组合显示
                result_text = f"<div style='margin-bottom:10px'>{brief_analysis}</div>"
                if example:
                    result_text += f"<div style='margin-top:15px'>{example}</div>"
                    # 添加说明：生成了多少个例句
                    examples_info = f"<div style='margin-top:10px; color:#666; font-size:12px;'>为每个替换部分生成了 {examples_count} 个例句</div>"
                    result_text += examples_info
                
                text_widget.setHtml(result_text)
            else:
                text_widget.setPlainText("未能获取有效分析结果")
                
        except Exception as e:
            text_widget.setPlainText(f"生成失败: {str(e)}") 