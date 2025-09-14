"""
复习窗口模块
作为导入和组装各组件的入口点，负责初始化和配置组件
"""
from aqt.qt import QDialog
from aqt.utils import showWarning

from .dialogs.review_dialog import ReviewDialog
from ..utils.ai_handler import AIHandler

# 明确指定导出的函数
__all__ = ['show_review_dialog']


def show_review_dialog(questions=None, parent=None, ai_handler=None):
    """
    显示复习对话框
    
    Args:
        questions (dict): 问题数据，包含questions列表
        parent: 父窗口
        ai_handler: AI处理器实例
        
    Returns:
        ReviewDialog: 创建的对话框实例
    """
    # 如果没有提供AI处理器，创建一个新的
    if not ai_handler:
        try:
            ai_handler = AIHandler()
        except Exception as e:
            showWarning(f"初始化AI处理器失败: {str(e)}")
            return None
    
    # 如果传入的questions不包含questions键，则将其包装
    if questions and not isinstance(questions, dict):
        questions = {"questions": questions}
    elif questions and "questions" not in questions:
        questions = {"questions": [questions]}
    
    # 创建和显示对话框
    dialog = ReviewDialog(questions, parent, ai_handler)
    dialog.show()
    return dialog
