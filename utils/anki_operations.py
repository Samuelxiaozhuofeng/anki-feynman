from aqt import mw
from ..utils.note_types import LANGUAGE_LEARNING_TYPE, ensure_language_learning_type

def add_language_note(note_data, deck_name):
    """添加语言学习笔记到Anki"""
    # 确保笔记类型存在
    ensure_language_learning_type()
    
    # 获取目标牌组
    did = mw.col.decks.id(deck_name)
    
    # 创建笔记
    note = mw.col.new_note(notetype=mw.col.models.by_name(LANGUAGE_LEARNING_TYPE))
    
    # 填充字段
    original_text = note_data.get("original", "")
    note["原句"] = original_text
    note["例句"] = original_text  # 确保例句字段也有同样的内容
    note["翻译"] = note_data.get("translation", "")
    note["语法知识点"] = note_data.get("grammar_note", "")
    
    # 添加到集合中
    mw.col.add_note(note, did)
    
    # 保存更改
    mw.col.save() 