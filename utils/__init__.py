# 导出笔记类型相关函数
from .note_types import create_feynman_note, create_feynman_cloze_type, ensure_note_types
from .text_capture import setup_text_capture
# PDF相关功能延迟导入，避免在模块加载时就导入pypdf
