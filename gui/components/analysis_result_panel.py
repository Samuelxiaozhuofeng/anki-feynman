from aqt.qt import *
from PyQt6.QtCore import Qt, pyqtSignal

class AnalysisResultPanel(QGroupBox):
    """分析结果区域面板"""
    
    addReplacementRequested = pyqtSignal(str)  # 添加替换请求信号
    
    def __init__(self, parent=None):
        super().__init__("分析结果", parent)
        self.setStyleSheet("font-weight: 500;")
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        result_layout = QVBoxLayout(self)
        result_layout.setContentsMargins(15, 25, 15, 15)
        result_layout.setSpacing(15)

        # 句型分析（合并可替换部分内容）
        self.analysis_label = QLabel("句型分析与可替换部分:")
        self.analysis_label.setStyleSheet("font-weight: 600; font-size: 15px; color: #007AFF;")
        result_layout.addWidget(self.analysis_label)

        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setMinimumHeight(250)  # 增加高度以容纳更多内容
        # 优化字体和排版，提升阅读体验
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
                font-size: 15px;
                line-height: 1.8;
                padding: 20px;
                border: 1px solid #D1D1D6;
                border-radius: 10px;
                background-color: #FFFFFF;
                selection-background-color: #007AFF;
                selection-color: white;
            }
            QTextEdit:focus {
                border-color: #007AFF;
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
            }
        """)
        result_layout.addWidget(self.analysis_text)

        # 添加"追加替换"功能
        add_replace_layout = QHBoxLayout()
        add_replace_layout.setContentsMargins(0, 10, 0, 0)

        self.add_replace_label = QLabel("新增替换部分:")
        self.add_replace_label.setStyleSheet("font-weight: 500; color: #666666;")
        add_replace_layout.addWidget(self.add_replace_label)

        self.add_replace_edit = QLineEdit()
        self.add_replace_edit.setPlaceholderText("输入要新增替换的部分")
        self.add_replace_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #D1D1D6;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007AFF;
            }
        """)
        add_replace_layout.addWidget(self.add_replace_edit)

        self.add_replace_button = QPushButton("追加生成")
        self.add_replace_button.clicked.connect(self.on_add_replace_clicked)
        self.add_replace_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        add_replace_layout.addWidget(self.add_replace_button)

        result_layout.addLayout(add_replace_layout)
        
    def on_add_replace_clicked(self):
        """添加替换按钮点击处理"""
        new_part = self.add_replace_edit.text().strip()
        if new_part:
            self.addReplacementRequested.emit(new_part)
            self.add_replace_edit.clear()
            
    def set_analysis(self, language, level, analysis_text, replaceable_parts=None):
        """设置分析结果，合并可替换部分内容"""
        # 构建完整的分析内容
        content_parts = []

        # 添加级别信息
        level_info = f"""
        <div style='background: linear-gradient(135deg, #E8F4FD 0%, #F0F8FF 100%);
                    padding: 16px 20px;
                    border-radius: 10px;
                    margin-bottom: 25px;
                    border-left: 5px solid #007AFF;
                    box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);'>
            <span style='color: #007AFF; font-weight: 600; font-size: 15px; letter-spacing: 0.5px;'>🎯 当前设置</span>
            <span style='color: #333333; font-size: 15px; margin-left: 8px;'>{language} ({level})</span>
        </div>
        """
        content_parts.append(level_info)

        # 添加句型分析
        if analysis_text:
            analysis_section = f"""
            <div style='margin-bottom: 25px;'>
                <h3 style='color: #1D1D1F;
                          font-size: 18px;
                          font-weight: 600;
                          margin-bottom: 15px;
                          border-bottom: 3px solid #007AFF;
                          padding-bottom: 8px;
                          letter-spacing: 0.3px;'>📝 句型分析</h3>
                <div style='background-color: #FAFBFC;
                          padding: 20px;
                          border-radius: 10px;
                          border: 1px solid #E5E7EB;
                          line-height: 2.0;
                          color: #374151;
                          font-size: 15px;
                          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);'>
                    {analysis_text}
                </div>
            </div>
            """
            content_parts.append(analysis_section)

        # 添加可替换部分
        if replaceable_parts:
            replaceable_section = f"""
            <div style='margin-bottom: 25px;'>
                <h3 style='color: #1D1D1F;
                          font-size: 18px;
                          font-weight: 600;
                          margin-bottom: 15px;
                          border-bottom: 3px solid #34C759;
                          padding-bottom: 8px;
                          letter-spacing: 0.3px;'>🔄 可替换部分</h3>
                <div style='background: linear-gradient(135deg, #F0FDF4 0%, #F7FEF9 100%);
                          padding: 20px;
                          border-radius: 10px;
                          border-left: 5px solid #34C759;
                          box-shadow: 0 2px 8px rgba(52, 199, 89, 0.1);'>
                    <div style='line-height: 2.0;
                              color: #374151;
                              font-size: 15px;
                              white-space: pre-wrap;
                              font-weight: 500;'>
                        {replaceable_parts}
                    </div>
                </div>
            </div>
            """
            content_parts.append(replaceable_section)

        # 设置完整内容
        full_content = "".join(content_parts)
        self.analysis_text.setHtml(full_content)

    def set_replaceable_parts(self, replaceable_parts):
        """设置可替换部分（保持向后兼容）"""
        # 这个方法现在只是为了向后兼容，实际内容会在set_analysis中处理
        self.replaceable_parts = replaceable_parts

    def clear(self):
        """清空分析结果"""
        self.analysis_text.setText("")
        self.replaceable_parts = None
        
    def enable_add_button(self, enabled=True):
        """启用或禁用追加生成按钮"""
        self.add_replace_button.setEnabled(enabled) 