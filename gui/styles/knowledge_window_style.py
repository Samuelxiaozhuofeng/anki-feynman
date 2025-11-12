"""
知识卡片窗口样式管理模块
提供日间/夜间模式的样式定义
"""
from aqt import mw


def get_knowledge_window_style(night_mode=None):
    """
    获取知识卡片窗口的样式表
    
    Args:
        night_mode: 是否为夜间模式，None则自动检测
        
    Returns:
        str: CSS样式表字符串
    """
    if night_mode is None:
        night_mode = _detect_night_mode()
    
    if night_mode:
        return _get_night_mode_style()
    else:
        return _get_day_mode_style()


def _detect_night_mode():
    """检测Anki是否处于夜间模式"""
    try:
        from aqt.theme import theme_manager
        return theme_manager.night_mode
    except:
        try:
            return mw.pm.meta.get("night_mode", False)
        except:
            return False


def _get_night_mode_style():
    """获取夜间模式样式"""
    return """
        QDialog {
            background-color: #2d2d2d;
        }
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 4px;
            margin-top: 1em;
            padding-top: 0.5em;
        }
        QGroupBox::title {
            color: #64b5f6;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QTextEdit {
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            background-color: #383838;
            color: #e0e0e0;
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
        QPushButton:disabled {
            background-color: #555555;
        }
        QLabel {
            color: #e0e0e0;
        }
        QLineEdit {
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            background-color: #383838;
            color: #e0e0e0;
        }
    """


def _get_day_mode_style():
    """获取日间模式样式"""
    return """
        QDialog {
            background-color: white;
        }
        QGroupBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            margin-top: 1em;
            padding-top: 0.5em;
        }
        QGroupBox::title {
            color: #2196F3;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QTextEdit {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 5px;
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
        QPushButton:disabled {
            background-color: #BDBDBD;
        }
        QLineEdit {
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            padding: 5px;
        }
    """


def apply_knowledge_window_style(widget):
    """
    应用知识卡片窗口样式到指定widget
    
    Args:
        widget: 要应用样式的Qt widget
    """
    style = get_knowledge_window_style()
    widget.setStyleSheet(style)

