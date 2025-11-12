"""
问答题提示模板模块，包含生成问答题所需的提示模板。
"""

from typing import Dict, Any

# 问答题生成提示模板
ESSAY_QUESTION_PROMPT = """你是一个基于费曼学习法的教学助手。请根据以下内容生成{num_questions}道问答题。
要求：
1. 问题应该促进深度思考和理解
2. 帮助学习者用自己的话解释概念
3. 对于每个问题，必须从原文中提取与该问题直接相关的段落
4. 必须严格按照以下JSON格式返回，不要添加任何其他标记：

{{
    "questions": [
        {{
            "question": "问题内容",
            "reference_answer": "参考答案",
            "key_points": [
                "关键点1",
                "关键点2",
                "关键点3"
            ],
            "source_content": "与该问题直接相关的原文段落（不要包含无关内容）"
        }}
    ]
}}

JSON格式要求（非常重要）：
1. 返回的必须是合法的JSON格式
2. 不要添加任何代码块标记（如```json）
3. 每个问题至少包含3个关键点
4. 参考答案应该完整覆盖所有关键点
5. source_content必须是原文中与问题直接相关的段落，不要包含无关内容
6. 特别注意JSON格式中的逗号、引号等标点符号的正确使用
7. 确保每个JSON对象和数组的开始和结束都有正确的括号
8. 每个属性后面都必须有逗号，除了最后一个属性
9. 所有字符串必须用双引号包围，不能用单引号
10. 当生成多个问题时，每个问题对象之间必须用逗号分隔
11. 检查生成的JSON是否完整，特别是在生成大量题目时
12. 确保每个问题对象的所有字段都正确闭合

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
    # 添加语言指示
    language_instruction = f"请使用{language}生成所有问题、参考答案、关键点和源内容。\n\n"
    
    return language_instruction + ESSAY_QUESTION_PROMPT.format(
        content=content,
        num_questions=num_questions
    ) 