"""
Anki样式模块，提供与Anki一致的界面样式
"""
from aqt import mw

def is_night_mode():
    """
    检测Anki是否处于夜间模式
    
    Returns:
        bool: 是否为夜间模式
    """
    night_mode = False
    try:
        from aqt.theme import theme_manager
        night_mode = theme_manager.night_mode
    except:
        try:
            night_mode = mw.pm.meta.get("night_mode", False)
        except:
            pass
    return night_mode

def get_anki_style(night_mode=None):
    """
    获取与Anki一致的样式表
    
    Args:
        night_mode (bool, optional): 是否为夜间模式。如果为None，则自动检测。
        
    Returns:
        str: 样式表字符串
    """
    if night_mode is None:
        night_mode = is_night_mode()
        
    if night_mode:
        return """
            QDialog {
                background-color: #2d2d2d;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
                font-size: 15px;
            }
            QGroupBox::title {
                color: #64b5f6;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                font-size: 16px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2196F3;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #555555;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #1976D2;
            }
            QRadioButton {
                color: #e0e0e0;
                padding: 5px;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                background-color: #1976D2;
                border: 2px solid #555555;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #555555;
                border-radius: 8px;
            }
            QPlainTextEdit, QTextEdit {
                font-size: 14px;
                line-height: 1.5;
                padding: 5px;
                background-color: #383838;
                color: #e0e0e0;
                border: 1px solid #555555;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                background-color: #383838;
                color: #e0e0e0;
                border: 1px solid #555555;
            }
            QComboBox {
                font-size: 14px;
                padding: 5px;
                background-color: #383838;
                color: #e0e0e0;
                border: 1px solid #555555;
            }
            QCheckBox {
                font-size: 14px;
                color: #e0e0e0;
            }
        """
    else:
        return """
            QDialog {
                background-color: white;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 1em;
                padding-top: 10px;
                font-size: 15px;
            }
            QGroupBox::title {
                color: #2196F3;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
                font-size: 16px;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 80px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
            QRadioButton {
                color: #333333;
                padding: 5px;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
            }
            QPlainTextEdit, QTextEdit {
                font-size: 14px;
                line-height: 1.5;
                padding: 5px;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
            }
            QComboBox {
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox {
                font-size: 14px;
            }
        """

def apply_anki_style(widget):
    """
    应用Anki样式到指定组件
    
    Args:
        widget (QWidget): 需要应用样式的组件
    """
    widget.setStyleSheet(get_anki_style()) 