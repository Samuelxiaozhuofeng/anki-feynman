"""
评估答案提示模板模块，包含评估学习者答案所需的提示模板。
"""

from typing import Dict, Any
from .common import ROLE_EVALUATOR, format_with_language

# 问答题评估提示模板
ESSAY_EVALUATION_PROMPT = """{role_description}请评估以下答案的质量，并以JSON格式返回评估结果。

问题：{{question}}
参考答案：{{reference_answer}}
关键点：{{key_points}}

用户答案：{{user_answer}}

请严格按照以下JSON格式返回评估结果，注意score必须是0-100之间的整数（不要添加任何其他内容）：
{{{{
    "score": 整数分数（0-100，不要加引号）,
    "feedback": "总体评价",
    "covered_points": ["已覆盖的关键点1", "已覆盖的关键点2", ...],
    "missing_points": ["未覆盖的关键点1", "未覆盖的关键点2", ...],
    "suggestions": ["改进建议1", "改进建议2", ...]
}}}}
"""

# 选择题评估系统提示
CHOICE_EVALUATION_SYSTEM_PROMPT = f"""{ROLE_EVALUATOR}，负责评估选择题答案。你需要：
1. 准确判断答案是否正确
2. 提供清晰的解释
3. 指出正确答案（如果答错）
4. 给出有助于理解的反馈"""

def get_essay_evaluation_prompt(
    question: str,
    reference_answer: str,
    key_points: list,
    user_answer: str,
    language: str = "中文"
) -> str:
    """
    格式化问答题评估提示模板

    Args:
        question: 问题内容
        reference_answer: 参考答案
        key_points: 关键点列表
        user_answer: 用户答案
        language: 评估使用的语言

    Returns:
        格式化后的提示文本
    """
    # 使用公共函数添加语言指示和格式化
    prompt_template = ESSAY_EVALUATION_PROMPT.format(
        role_description=ROLE_EVALUATOR + "。"
    )

    return format_with_language(
        prompt_template,
        language,
        "评估结果、反馈和建议",
        question=question,
        reference_answer=reference_answer,
        key_points=", ".join(key_points),
        user_answer=user_answer
    )

def get_choice_evaluation_messages(question_data: Dict[str, Any], user_answer: str) -> list:
    """
    生成选择题评估消息列表

    Args:
        question_data: 问题数据，包含问题、选项、正确答案和解释
        user_answer: 用户答案

    Returns:
        消息列表，包含系统提示和用户提示
    """
    return [
        {
            "role": "system",
            "content": CHOICE_EVALUATION_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""请评估以下选择题答案：

问题：{question_data['question']}
选项：
{chr(10).join(question_data['options'])}

正确答案：{question_data['correct_answer']}
答案解释：{question_data['explanation']}

用户答案：{user_answer}"""
        }
    ] 