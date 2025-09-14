from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.utils import tooltip
import os
import json

def capture_text(text):
    """
    捕获选中的文本并保存到例句库
    
    Args:
        text: 选中的文本
    """
    if not text or not text.strip():
        return
    
    # 保存句子到文件
    add_sentence_to_storage(text.strip())
    
    # 显示成功提示
    tooltip("句子已保存到例句库")

def add_sentence_to_storage(sentence):
    """将句子添加到存储中"""
    if not sentence:
        return False
        
    sentences_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "data", "sentences.json")
    
    # 确保数据目录存在
    os.makedirs(os.path.dirname(sentences_file), exist_ok=True)
    
    # 加载已有句子
    sentences = []
    try:
        if os.path.exists(sentences_file):
            with open(sentences_file, 'r', encoding='utf-8') as f:
                sentences = json.load(f)
    except Exception as e:
        print(f"加载句子出错: {str(e)}")
        sentences = []
    
    # 确保sentences是列表
    if not isinstance(sentences, list):
        sentences = []
    
    # 如果句子不重复，添加到列表中
    if sentence not in sentences:
        sentences.append(sentence)
        
        # 保存回文件
        try:
            with open(sentences_file, 'w', encoding='utf-8') as f:
                json.dump(sentences, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存句子出错: {str(e)}")
            return False
    
    return False
    
def add_context_menu_item(webview, menu):
    """
    向标准Anki webview添加右键菜单项
    
    Args:
        webview: Anki网页视图
        menu: 要添加菜单项的QMenu对象
    """
    selected_text = webview.selectedText()
    if not selected_text or not selected_text.strip():
        return
    
    # 创建捕获文本的动作
    action = menu.addAction("发送到语言学习助手")
    qconnect(action.triggered, lambda: capture_text(selected_text))

def add_editor_context_menu_item(editor, menu):
    """
    向编辑器添加右键菜单项
    
    Args:
        editor: Anki编辑器对象
        menu: 要添加菜单项的QMenu对象
    """
    # 获取编辑器中选中的文本
    selected_text = editor.web.selectedText()
    if not selected_text or not selected_text.strip():
        return
    
    # 创建捕获文本的动作
    action = menu.addAction("发送到语言学习助手")
    qconnect(action.triggered, lambda: capture_text(selected_text))

def add_browser_context_menu_item(browser, menu):
    """
    向浏览器添加右键菜单项
    
    Args:
        browser: Anki浏览器对象
        menu: 要添加菜单项的QMenu对象
    """
    # 获取浏览器中选中的文本
    if hasattr(browser, 'editor') and browser.editor:
        selected_text = browser.editor.web.selectedText()
        if not selected_text or not selected_text.strip():
            return
        
        # 创建捕获文本的动作
        action = menu.addAction("发送到语言学习助手")
        qconnect(action.triggered, lambda: capture_text(selected_text))

def add_reviewer_context_menu_item(reviewer, menu):
    """
    向复习界面添加右键菜单项
    
    Args:
        reviewer: Anki复习器对象
        menu: 要添加菜单项的QMenu对象
    """
    if not reviewer.card:
        return
    
    # 获取当前卡片上选中的文本
    selected_text = reviewer.web.selectedText()
    if not selected_text or not selected_text.strip():
        return
    
    # 创建捕获文本的动作
    action = menu.addAction("发送到语言学习助手")
    qconnect(action.triggered, lambda: capture_text(selected_text))

def inject_js(web_content, context):
    """
    向webview注入JavaScript以支持快捷键捕获文本
    
    Args:
        web_content: 网页内容对象
        context: 上下文信息
    """
    js_code = """
    (function() {
        // 添加快捷键支持
        document.addEventListener('keydown', function(e) {
            // Ctrl+Shift+L 捕获选中文本到语言学习助手
            if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                const selectedText = window.getSelection().toString().trim();
                if (selectedText) {
                    pycmd('anki_language_capture:' + selectedText);
                    e.preventDefault();
                }
            }
        });
    })();
    """
    
    web_content.body += f"<script>{js_code}</script>"

def handle_pycmd(handled, cmd, context):
    """
    处理从JavaScript发送的命令
    
    Args:
        handled: 是否已经处理的标志
        cmd: 命令字符串
        context: 上下文信息
    
    Returns:
        如果处理了命令，返回True；否则返回handled
    """
    if not cmd.startswith("anki_language_capture:"):
        return handled
    
    # 提取捕获的文本
    text = cmd.replace("anki_language_capture:", "")
    if text and text.strip():
        capture_text(text.strip())
    
    return True  # 命令已处理

def get_stored_sentences():
    """获取已存储的句子列表"""
    sentences_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "data", "sentences.json")
    
    sentences = []
    try:
        if os.path.exists(sentences_file):
            with open(sentences_file, 'r', encoding='utf-8') as f:
                sentences = json.load(f)
    except Exception as e:
        print(f"加载句子出错: {str(e)}")
        sentences = []
    
    # 确保sentences是列表
    if not isinstance(sentences, list):
        sentences = []
        
    return sentences

def setup_text_capture():
    """设置文本捕获功能"""
    # 注册各种环境的右键菜单钩子
    gui_hooks.webview_will_show_context_menu.append(add_context_menu_item)
    gui_hooks.editor_will_show_context_menu.append(add_editor_context_menu_item)
    gui_hooks.browser_will_show_context_menu.append(add_browser_context_menu_item)
    gui_hooks.reviewer_will_show_context_menu.append(add_reviewer_context_menu_item)
    
    # 注册JavaScript注入钩子
    gui_hooks.webview_will_set_content.append(inject_js)
    
    # 注册命令处理钩子
    gui_hooks.webview_did_receive_js_message.append(handle_pycmd) 