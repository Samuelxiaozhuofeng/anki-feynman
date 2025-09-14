"""
追问处理提示模板模块，包含处理学习者追问所需的提示模板。
"""

from typing import Dict, Any

# 追问处理系统提示
FOLLOWUP_SYSTEM_PROMPT = """你是一个基于费曼学习法的AI助手，专注于通过简单、清晰的方式解释复杂概念。"""

# 追问处理提示模板
FOLLOWUP_PROMPT = """作为一个基于费曼学习法的AI助手，请根据以下信息回答用户的追问。

原始问题：{original_question}

相关内容：
{source_content}

原始答案：
{user_answer}

AI解析历史：
{ai_feedback}

对话历史：
{history}

用户追问：
{follow_up_question}

请提供详细、准确、易于理解的解答，运用费曼学习法的原则：
1. 使用简单、清晰的语言
2. 通过类比和实例来解释复杂概念
3. 确保解释逻辑连贯，层次分明
4. 指出与原始问题的关联
5. 如有必要，纠正可能的误解

回答格式要求：
1. 直接回答问题，无需重复问题内容
2. 分段落组织内容，确保易读性
3. 必要时使用列表或要点说明
4. 如果问题涉及多个方面，请分别说明
5. 结尾总结关键点"""

def format_history(history: list) -> str:
    """
    格式化对话历史

    Args:
        history: 对话历史列表，每个元素包含问题和答案

    Returns:
        格式化后的对话历史文本
    """
    if not history:
        return "无历史对话"
        
    formatted = ""
    for item in history:
        formatted += f"问：{item['question']}\n"
        formatted += f"答：{item['answer']}\n\n"
    return formatted.strip()

def get_followup_messages(context: Dict[str, Any]) -> list:
    """
    生成追问处理消息列表

    Args:
        context: 上下文信息，包含原始问题、相关内容、用户答案、AI反馈、对话历史和追问内容

    Returns:
        消息列表，包含系统提示和用户提示
    """
    # 格式化对话历史
    formatted_history = format_history(context.get('history', []))
    
    # 生成提示内容
    prompt = FOLLOWUP_PROMPT.format(
        original_question=context['original_question'],
        source_content=context['source_content'],
        user_answer=context['user_answer'],
        ai_feedback=context['ai_feedback'],
        history=formatted_history,
        follow_up_question=context['follow_up_question']
    )
    
    return [
        {
            "role": "system",
            "content": FOLLOWUP_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": prompt
        }
    ] 