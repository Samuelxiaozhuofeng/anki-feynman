import os
import sys
import json

# 将vendor目录添加到Python路径
vendor_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor")
sys.path.insert(0, vendor_dir)

from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, qconnect
from .gui.input_window import show_input_dialog
from .gui.settings_window import SettingsDialog
from .gui.language_window import show_language_window
from .utils import ensure_note_types, setup_text_capture
from aqt.gui_hooks import profile_did_open
from .lang.messages import get_message, DEFAULT_LANG

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"ui": {"language": DEFAULT_LANG}}

def get_current_language():
    """获取当前语言设置"""
    config = load_config()
    return config.get("ui", {}).get("language", DEFAULT_LANG)

def show_settings():
    """显示设置对话框"""
    dialog = SettingsDialog(mw)
    dialog.exec()

def init_feynman():
    """初始化费曼学习插件"""
    if not mw.col:
        return
        
    # 确保笔记类型已创建
    ensure_note_types()
    
    # 设置文本捕获功能
    setup_text_capture()
    
    # 获取当前语言
    current_lang = get_current_language()
    
    # 创建菜单项
    feynman_menu = QMenu(get_message('menu_create', current_lang), mw)
    mw.form.menubar.addMenu(feynman_menu)

    # 添加菜单动作
    start_action = QAction(get_message('menu_create', current_lang), mw)
    language_action = QAction("语言学习练习", mw)
    settings_action = QAction(get_message('menu_settings', current_lang), mw)
    about_action = QAction('About', mw)

    feynman_menu.addAction(start_action)
    feynman_menu.addAction(language_action)
    feynman_menu.addAction(settings_action)
    feynman_menu.addAction(about_action)

    # 连接信号
    qconnect(start_action.triggered, show_input_dialog)
    qconnect(language_action.triggered, show_language_window)
    qconnect(settings_action.triggered, show_settings)
    qconnect(about_action.triggered, lambda: showInfo("Anki 费曼学习法插件 v0.1.0"))

# 在配置文件加载后初始化插件
profile_did_open.append(init_feynman)
