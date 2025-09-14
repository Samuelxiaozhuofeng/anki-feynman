from aqt.qt import *
from PyQt6.QtCore import Qt
from .language_example_item import LanguageExampleItem

class ExamplesDisplayPanel(QWidget):
    """例句展示面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存主窗口引用
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # 减少组件间的间距
        
        # 设置更合理的最小宽度，确保有足够空间显示内容
        self.setMinimumWidth(800)  # 增加最小宽度以适应70%的布局

        # 创建标题容器，使用更优雅的设计
        title_container = QWidget()
        title_container.setFixedHeight(70)  # 增加标题高度
        title_container.setObjectName("examplesTitleContainer")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(30, 0, 30, 0)  # 增加水平边距

        # 例句区域标题
        examples_title = QLabel("🎯 替换示例")
        examples_title.setObjectName("examplesTitle")
        examples_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        examples_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
                color: #1D1D1F;
                letter-spacing: 0.5px;
            }
        """)
        title_layout.addWidget(examples_title)

        # 添加装饰性元素
        title_layout.addStretch()

        # 添加到主布局
        layout.addWidget(title_container)

        # 创建更优雅的分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("examplesSeparator")
        separator.setStyleSheet("""
            QFrame {
                background: linear-gradient(to right, transparent, #007AFF, transparent);
                height: 2px;
                border: none;
                margin: 0 30px;
            }
        """)
        layout.addWidget(separator)
        
        # 例句滚动区域
        self.examples_scroll = QScrollArea()
        self.examples_scroll.setWidgetResizable(True)
        self.examples_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.examples_scroll.setObjectName("examplesScrollArea")
        self.examples_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.examples_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # 优化滚动区域样式
        self.examples_scroll.setStyleSheet("""
            QScrollArea {
                background-color: #F8F9FA;
                border: none;
                border-radius: 0 0 15px 15px;
            }
            QScrollBar:vertical {
                background-color: #F0F0F0;
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background-color: #C0C0C0;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

        self.examples_container = QWidget()
        self.examples_layout = QVBoxLayout(self.examples_container)
        self.examples_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.examples_layout.setSpacing(20)  # 增加间距以适应卡片设计
        self.examples_layout.setContentsMargins(30, 30, 30, 30)  # 增加内容区域边距
        
        self.examples_scroll.setWidget(self.examples_container)
        layout.addWidget(self.examples_scroll)
        
    def clear_examples(self):
        """清空例句区域"""
        # 清除所有现有的例句
        while self.examples_layout.count():
            item = self.examples_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
    def display_examples(self, examples, language, level, examples_count, specified_parts=None):
        """显示生成的例句"""
        self.clear_examples()
        
        # 获取当前模型信息
        model_info = self.parent.settings_panel.get_model() if hasattr(self.parent, 'settings_panel') else None
        model_display = f", 模型: {model_info if model_info else '默认模型'}"
        
        # 添加当前语言和级别信息 - 使用更好的信息卡片设计
        info_card = QWidget()
        info_card.setObjectName("examplesInfoCard")
        info_card.setStyleSheet("""
            QWidget#examplesInfoCard {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                border: none;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(25, 20, 25, 20)  # 增加边距
        info_layout.setSpacing(10)

        # 设置信息标题
        settings_title = QLabel("⚙️ 设置信息")
        settings_title.setObjectName("examplesInfoTitle")
        settings_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
        """)
        info_layout.addWidget(settings_title)

        # 设置信息内容
        settings_content = QLabel(f"{language} {level} (每部分{examples_count}个例句{model_display})")
        settings_content.setObjectName("examplesInfoContent")
        settings_content.setWordWrap(True)
        settings_content.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-weight: 500;
                line-height: 1.5;
            }
        """)
        info_layout.addWidget(settings_content)

        self.examples_layout.addWidget(info_card)
        
        # 如果用户指定了替换部分，显示提示信息
        if specified_parts:
            parts_text = ", ".join(specified_parts)
            
            note_card = QWidget()
            note_card.setObjectName("examplesNoteCard")
            note_card.setStyleSheet("""
                QWidget#examplesNoteCard {
                    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                    border-radius: 15px;
                    border: none;
                }
            """)
            note_layout = QVBoxLayout(note_card)
            note_layout.setContentsMargins(25, 20, 25, 20)  # 增加边距
            note_layout.setSpacing(10)

            note_title = QLabel("⚠️ 注意")
            note_title.setObjectName("examplesNoteTitle")
            note_title.setStyleSheet("""
                QLabel {
                    color: #8B4513;
                    font-size: 16px;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
            """)
            note_layout.addWidget(note_title)

            note_content = QLabel(f"根据您的要求，只替换了以下部分: {parts_text}")
            note_content.setObjectName("examplesNoteContent")
            note_content.setWordWrap(True)
            note_content.setStyleSheet("""
                QLabel {
                    color: #8B4513;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 1.5;
                }
            """)
            note_layout.addWidget(note_content)
            
            self.examples_layout.addWidget(note_card)
        
        # 按照替换部分对例句进行分组
        examples_by_part = {}
        for example in examples:
            part = example.get("replaced_part", "其他")
            if part not in examples_by_part:
                examples_by_part[part] = []
            examples_by_part[part].append(example)
        
        # 对每组例句添加一个分组标题，并显示该组的所有例句
        for part, part_examples in examples_by_part.items():
            # 创建分组标题容器
            group_header = QWidget()
            group_header.setObjectName("examplesGroupHeader")
            group_header.setStyleSheet("""
                QWidget#examplesGroupHeader {
                    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                    border-radius: 12px;
                    border: none;
                    margin: 10px 0;
                }
            """)
            group_layout = QHBoxLayout(group_header)
            group_layout.setContentsMargins(20, 15, 20, 15)  # 调整边距

            # 添加分组标题
            part_title = QLabel(f"🔄 【{part}】替换示例")
            part_title.setObjectName("examplesGroupTitle")
            part_title.setStyleSheet("""
                QLabel {
                    color: #2D3748;
                    font-size: 16px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }
            """)
            group_layout.addWidget(part_title)
            
            self.examples_layout.addWidget(group_header)
            
            # 添加该组的所有例句
            for example in part_examples:
                # 直接传递主窗口作为父组件，而不是self.parent()
                example_widget = LanguageExampleItem(example, self.main_window)
                self.examples_layout.addWidget(example_widget)
            
            # 添加组间分隔线
            if part != list(examples_by_part.keys())[-1]:  # 如果不是最后一组
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setFrameShadow(QFrame.Shadow.Sunken)
                separator.setObjectName("examplesGroupSeparator")
                separator.setFixedHeight(3)  # 设置分隔线高度
                separator.setStyleSheet("""
                    QFrame {
                        background: linear-gradient(to right, transparent, #E2E8F0, transparent);
                        border: none;
                        margin: 15px 20px;
                    }
                """)
                self.examples_layout.addWidget(separator)
        
        # 添加空白区域
        self.examples_layout.addStretch() 