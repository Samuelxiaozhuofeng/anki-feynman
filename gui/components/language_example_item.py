from aqt.qt import *
from aqt import mw
from aqt.utils import tooltip, showWarning
from ...utils.note_types import ensure_language_learning_type
from ...utils.anki_operations import add_language_note
import traceback

class LanguageExampleItem(QWidget):
    """语言例句项目组件"""
    
    def __init__(self, example_data, parent=None):
        super().__init__(parent)
        self.example_data = example_data
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距以适应卡片设计
        main_layout.setSpacing(18)  # 增加组件间的间距

        # 设置最小宽度保证内容正常显示
        self.setMinimumWidth(700)  # 增加宽度以适应70%的布局

        self.setObjectName("languageExampleItem")
        # 设置卡片样式
        self.setStyleSheet("""
            QWidget#languageExampleItem {
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border-radius: 16px;
                border: 1px solid #e9ecef;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                margin: 5px;
            }
            QWidget#languageExampleItem:hover {
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
                transform: translateY(-2px);
            }
        """)
        
        # 内容区域
        content_area = QWidget()
        content_area.setObjectName("exampleContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)  # 增加组件间距
        
        # 显示替换了哪个部分（如果有）
        if self.example_data.get("replaced_part"):
            replaced_part_container = QWidget()
            replaced_part_container.setObjectName("replacedPartContainer")
            replaced_part_container.setStyleSheet("""
                QWidget#replacedPartContainer {
                    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                    border-radius: 10px;
                    border: 1px solid #bbdefb;
                    padding: 8px 12px;
                }
            """)
            replaced_part_layout = QHBoxLayout(replaced_part_container)
            replaced_part_layout.setContentsMargins(12, 8, 12, 8)

            # 图标更改为标签样式
            replaced_part_icon = QLabel("🔄")
            replaced_part_icon.setFixedWidth(25)  # 固定图标宽度
            replaced_part_icon.setStyleSheet("font-size: 16px;")
            replaced_part_layout.addWidget(replaced_part_icon)

            self.replaced_part_label = QLabel(f"替换部分：{self.example_data.get('replaced_part', '')}")
            self.replaced_part_label.setObjectName("replacedPartLabel")
            self.replaced_part_label.setWordWrap(True)
            self.replaced_part_label.setStyleSheet("""
                QLabel {
                    color: #1976d2;
                    font-size: 14px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                }
            """)
            replaced_part_layout.addWidget(self.replaced_part_label, 1)  # 设置拉伸比例

            content_layout.addWidget(replaced_part_container)
        
        # 原始句子容器
        sentence_container = QWidget()
        sentence_container.setObjectName("sentenceContainer")
        sentence_container.setStyleSheet("""
            QWidget#sentenceContainer {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e9ecef;
                padding: 15px;
            }
        """)
        sentence_layout = QVBoxLayout(sentence_container)
        sentence_layout.setContentsMargins(15, 15, 15, 15)
        sentence_layout.setSpacing(8)  # 增加标签和内容间的间距
        
        # 标签与内容
        sentence_header = QWidget()
        sentence_header_layout = QHBoxLayout(sentence_header)
        sentence_header_layout.setContentsMargins(0, 0, 0, 0)
        
        sentence_label = QLabel("📝 示例句子")
        sentence_label.setObjectName("exampleSectionLabel")
        sentence_label.setStyleSheet("""
            QLabel {
                color: #495057;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.3px;
                text-transform: uppercase;
            }
        """)
        sentence_header_layout.addWidget(sentence_label)
        
        sentence_header_layout.addStretch()  # 添加弹性空间
        
        # 添加发音按钮（如果支持）
        is_japanese = self.example_data.get("language", "").lower() in ["日语", "japanese", "日本語"]
        if is_japanese:
            sound_button = QPushButton("发音")
            sound_button.setObjectName("soundButton")
            sound_button.setFixedSize(50, 24)  # 设置按钮大小
            sound_button.setToolTip("播放句子发音")
            sentence_header_layout.addWidget(sound_button)
        
        sentence_layout.addWidget(sentence_header)
        
        # 使用HTML格式增强换行显示效果，为日语添加特殊类
        sentence_text = self.example_data.get("sentence", "")
        html_class = "jp-text" if is_japanese else ""
        
        self.original_text = QLabel()
        self.original_text.setObjectName("exampleSentence")
        self.original_text.setWordWrap(True)
        self.original_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # 允许选择文本
        # 设置文本格式策略，确保长文本正确换行
        self.original_text.setTextFormat(Qt.TextFormat.RichText)
        self.original_text.setStyleSheet("""
            QLabel {
                color: #212529;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.6;
                padding: 12px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dee2e6;
            }
        """)
        # 添加日语特殊样式类
        self.original_text.setText(f"<div class='{html_class}' style='white-space: pre-wrap; word-wrap: break-word;'>{sentence_text}</div>")
        sentence_layout.addWidget(self.original_text)
        
        content_layout.addWidget(sentence_container)
        
        # 翻译容器
        translation_container = QWidget()
        translation_container.setObjectName("translationContainer")
        translation_container.setStyleSheet("""
            QWidget#translationContainer {
                background-color: #e8f5e9;
                border-radius: 10px;
                border: 1px solid #c8e6c9;
                padding: 15px;
            }
        """)
        translation_layout = QVBoxLayout(translation_container)
        translation_layout.setContentsMargins(15, 15, 15, 15)
        translation_layout.setSpacing(8)  # 增加标签和内容间的间距

        translation_label = QLabel("🌐 译文")
        translation_label.setObjectName("exampleSectionLabel")
        translation_label.setStyleSheet("""
            QLabel {
                color: #2e7d32;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.3px;
                text-transform: uppercase;
            }
        """)
        translation_layout.addWidget(translation_label)
        
        self.translation = QLabel(self.example_data.get("translation", ""))
        self.translation.setObjectName("exampleTranslation")
        self.translation.setWordWrap(True)
        self.translation.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # 允许选择文本
        # 设置文本格式策略，确保长文本正确换行
        self.translation.setTextFormat(Qt.TextFormat.RichText)
        self.translation.setStyleSheet("""
            QLabel {
                color: #1b5e20;
                font-size: 15px;
                font-weight: 500;
                line-height: 1.6;
                padding: 12px;
                background-color: white;
                border-radius: 8px;
                border: 1px solid #a5d6a7;
            }
        """)
        # 使用HTML格式增强换行显示效果
        translation_text = self.example_data.get("translation", "")
        self.translation.setText(f"<div style='white-space: pre-wrap; word-wrap: break-word;'>{translation_text}</div>")
        translation_layout.addWidget(self.translation)
        
        content_layout.addWidget(translation_container)
        
        # 语法注解（如果有）
        if self.example_data.get("grammar_note"):
            grammar_container = QWidget()
            grammar_container.setObjectName("grammarContainer")
            grammar_container.setStyleSheet("""
                QWidget#grammarContainer {
                    background-color: #fff3e0;
                    border-radius: 10px;
                    border: 1px solid #ffcc02;
                    padding: 15px;
                }
            """)
            grammar_layout = QVBoxLayout(grammar_container)
            grammar_layout.setContentsMargins(15, 15, 15, 15)
            grammar_layout.setSpacing(8)  # 增加标签和内容间的间距

            grammar_label = QLabel("📚 语法注解")
            grammar_label.setObjectName("exampleSectionLabel")
            grammar_label.setStyleSheet("""
                QLabel {
                    color: #e65100;
                    font-size: 14px;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                    text-transform: uppercase;
                }
            """)
            grammar_layout.addWidget(grammar_label)
            
            self.grammar_note = QLabel(self.example_data.get("grammar_note", ""))
            self.grammar_note.setObjectName("exampleGrammarNote")
            self.grammar_note.setWordWrap(True)
            self.grammar_note.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)  # 允许选择文本
            # 设置文本格式策略，确保长文本正确换行
            self.grammar_note.setTextFormat(Qt.TextFormat.RichText)
            self.grammar_note.setStyleSheet("""
                QLabel {
                    color: #bf360c;
                    font-size: 14px;
                    font-weight: 500;
                    line-height: 1.6;
                    padding: 12px;
                    background-color: white;
                    border-radius: 8px;
                    border: 1px solid #ffb74d;
                }
            """)
            # 使用HTML格式增强换行显示效果
            grammar_text = self.example_data.get("grammar_note", "")
            self.grammar_note.setText(f"<div style='white-space: pre-wrap; word-wrap: break-word;'>{grammar_text}</div>")
            grammar_layout.addWidget(self.grammar_note)
            
            content_layout.addWidget(grammar_container)
        
        main_layout.addWidget(content_area)
        
        # 按钮区域 - 更改为右对齐
        button_area = QWidget()
        button_area.setObjectName("exampleButtonArea")
        button_layout = QHBoxLayout(button_area)
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.addStretch()  # 添加弹性空间，使按钮靠右

        # 添加到Anki按钮 - 更小巧
        self.add_button = QPushButton("📚 添加到Anki")
        self.add_button.setObjectName("addToAnkiButton")
        self.add_button.setMinimumHeight(36)  # 稍微增加按钮高度
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 18px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #4e5bc6 0%, #5e377e 100%);
                transform: translateY(0px);
            }
        """)
        self.add_button.clicked.connect(self.add_to_anki)
        button_layout.addWidget(self.add_button)
        
        main_layout.addWidget(button_area)

    def add_to_anki(self):
        """添加到Anki牌组"""
        try:
            # 获取主窗口及相关信息
            main_window = self.get_main_window()
            if main_window and hasattr(main_window, 'settings_panel'):
                # 从settings_panel获取当前选择的牌组
                deck_name = main_window.settings_panel.get_deck_name()
                if not deck_name:
                    showWarning("未选择牌组，请先在主界面选择一个牌组")
                    return
                
                print(f"添加到牌组: {deck_name}")
                
                # 确保语言学习的笔记类型存在
                ensure_language_learning_type()
                
                # 创建笔记
                note = {
                    "original": self.example_data.get("sentence", ""),
                    "translation": self.example_data.get("translation", ""),
                    "grammar_note": self.example_data.get("grammar_note", "")
                }
                
                # 使用Anki API添加笔记
                add_language_note(note, deck_name)
                tooltip("已添加到牌组")
            else:
                showWarning("无法获取主窗口或设置面板，添加失败")
        except Exception as e:
            error_msg = str(e) + "\n" + traceback.format_exc()
            print(f"添加到Anki时出错: {error_msg}")
            showWarning(f"添加到Anki时出错: {str(e)}")
    
    def get_main_window(self):
        """获取主窗口实例"""
        # 直接使用传入的父窗口
        parent = self.parent()
        while parent:
            # 检查是否是主窗口
            if hasattr(parent, 'settings_panel'):
                return parent
            parent = parent.parent()
        return None 