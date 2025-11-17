"""
问答题提示模板模块，包含生成问答题所需的提示模板。
"""

from typing import Dict, Any
from .common import (
    ROLE_FEYNMAN_ASSISTANT,
    JSON_FORMAT_DETAILED,
    format_with_language
)

# 问答题生成提示模板
ESSAY_QUESTION_PROMPT = """{role_description}请根据以下内容生成{num_questions}道问答题。
要求：
1. 问题应该促进深度思考和理解
2. 帮助学习者用自己的话解释概念
3. 对于每个问题，必须从原文中提取与该问题直接相关的段落
4. 必须严格按照以下JSON格式返回，不要添加任何其他标记：

{{{{
    "questions": [
        {{{{
            "question": "问题内容",
            "reference_answer": "参考答案",
            "key_points": [
                "关键点1",
                "关键点2",
                "关键点3"
            ],
            "source_content": "与该问题直接相关的原文段落（不要包含无关内容）"
        }}}}
    ]
}}}}

特别注意：
1. 每个问题至少包含3个关键点
2. 参考答案应该完整覆盖所有关键点
3. source_content必须是原文中与问题直接相关的段落，不要包含无关内容

{json_requirements}

内容：
{content}
"""

def get_essay_prompt(content: str, num_questions: int = 3, language: str = "中文") -> str:
    """
    格式化问答题提示模板

    Args:
        content: 输入的学习内容
        num_questions: 要生成的问答题数量
        language: 生成内容使用的语言

    Returns:
        格式化后的提示文本
    """
    # 使用公共函数添加语言指示和格式化
    prompt_template = ESSAY_QUESTION_PROMPT.format(
        role_description=ROLE_FEYNMAN_ASSISTANT + "。",
        json_requirements=JSON_FORMAT_DETAILED,
        content="{content}",
        num_questions="{num_questions}"
    )

    return format_with_language(
        prompt_template,
        language,
        "问题、参考答案、关键点和源内容",
        content=content,
        num_questions=num_questions
    )