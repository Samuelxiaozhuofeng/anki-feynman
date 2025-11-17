"""
选择题提示模板模块，包含生成选择题所需的提示模板。
"""

from typing import Dict, Any
from .common import (
    ROLE_LEARNING_STRATEGIST,
    ROLE_FEYNMAN_ASSISTANT,
    JSON_FORMAT_DETAILED,
    format_with_language
)

# 选择题生成提示模板
CHOICE_QUESTION_PROMPT = """## 核心目标 (Core Goal)
{role_description}请根据以下学习材料生成 {{num_questions}} 道选择题，旨在深入测试学习者对概念的理解和应用能力。你的问题不应纠结于文本的表面信息，而应聚焦于以下两点：

**模式提炼 (Pattern Extraction)**: 引导用户思考文本背后隐藏的、可复用的思维模型、框架或普遍规律。  
**实践应用 (Practical Application)**: 引导用户思考如何将文本的核心观点应用于解决真实世界的问题。  

## 核心工作流 (Core Workflow) 

**第一步：内部思考与分析** (请在内心完成，不要在输出中显示)
1. 提炼核心模型：通读全文后，首先用一句话总结："这篇文章最核心的、可以被迁移到其他领域的思维模型或通用法则是什么？"  
2. 构思应用场景：思考："这个核心模型最适合用来解决什么类型的实际问题？如果我要把它教给别人，我会举一个什么新的例子？"  

**第二步：题目与选项设计**
基于上述思考，开始设计题目。遵循以下原则： 

**问题围绕"模型"与"应用"：**
- 模式提炼型问题：题干应询问关于文本核心框架、原则或其逻辑重点。 
- 实践应用型问题：题干应创造一个全新的、未在文中出现的具体情景，要求用户运用文本的观点来做出判断。

**设计高质量的选项：**
- 正确选项：必须是基于你第一步思考得出的、对核心模型或其应用的精准概括。  
- 干扰选项：必须设计得"巧妙"，通常包括：
  - 表面化解读：看起来正确，但只是对文本某个例子的字面概括，缺乏深度。  
  - 合理的误用：将文本的观点用在了错误的前提或场景下，看似相关，实则偏离。  
  - 事实正确但偏离核心：选项本身是一个正确的陈述，但并非作者在文中最想强调的核心规律或应用。

## 输出格式要求

请严格按照以下JSON格式返回，确保格式完整：

{{{{
    "questions": [
        {{{{
            "question": "问题内容",
            "options": [
                "A. 选项1",
                "B. 选项2",
                "C. 选项3",
                "D. 选项4"
            ],
            "correct_answer": "A/B/C/D其中之一",
            "explanation": "解释为什么这是正确答案",
            "source_content": "与该问题直接相关的原文段落（不要包含无关内容）"
        }}}}
    ]
}}}}

特别注意：
1. 选项必须包含A、B、C、D前缀
2. source_content必须是原文中与问题直接相关的段落

{json_requirements}

内容：
{content}
"""

def get_choice_prompt(content: str, num_questions: int = 3, language: str = "中文") -> str:
    """
    格式化选择题提示模板

    Args:
        content: 输入的学习内容
        num_questions: 要生成的选择题数量
        language: 生成内容使用的语言

    Returns:
        格式化后的提示文本
    """
    # 使用公共函数添加语言指示和格式化
    role_desc = f"{ROLE_LEARNING_STRATEGIST}。{ROLE_FEYNMAN_ASSISTANT}。"
    prompt_template = CHOICE_QUESTION_PROMPT.format(
        role_description=role_desc,
        json_requirements=JSON_FORMAT_DETAILED,
        content="{content}",
        num_questions="{num_questions}"
    )

    return format_with_language(
        prompt_template,
        language,
        "问题、选项、解释和答案",
        content=content,
        num_questions=num_questions
    )