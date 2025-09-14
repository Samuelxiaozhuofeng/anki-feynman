"""
知识卡提示模板模块，包含生成知识卡所需的各种提示模板。
"""

from typing import Dict, Any

# SuperMemo制卡原则
SUPERMEMO_PRINCIPLES = """
1. 信息最小化原则：
   - 每张卡片只包含一个基本概念
   - 避免复杂的、多重的问题
   - 确保问题的独立性和完整性
   - 答案应该只包含一个关键的事实/名称/概念/术语

2. 语言表达原则：
   - 使用清晰简洁的语言
   - 避免使用模糊或歧义的词语
   - 问题必须具体且不含糊
   - 优先使用简单直接的表达方式

3. 内容处理原则：
   - 将复杂内容分解为独立的知识点
   - 对超过15个字的内容进行拆分和概括
   - 保持概念的完整性
   - 确保知识点的逻辑连贯性

4. 制卡流程原则：
   - 第一步：使用简单的语言改写原内容
   - 第二步：将内容分成独立的知识点
   - 第三步：基于知识点生成抽认卡
   - 第四步：检查并优化卡片质量
"""

# 基础问答卡提示模板
BASIC_CARD_PROMPT = """
你是一个专业的知识卡制作助手。请基于以下制卡原则，将输入的文本转换为高质量的知识卡：

{supermemo_principles}

制卡步骤：
1. 内容改写
   - 使用简单的中文改写原文
   - 保持原意不变
   - 确保语言清晰易懂

2. 内容拆分
   - 将内容分成独立的知识点
   - 每个知识点聚焦一个核心概念
   - 对较长的知识点进行拆分和概括

3. 卡片生成
   - 基于知识点生成问答对
   - 确保问题具体明确
   - 答案简洁且只包含一个要点
   - 生成{num_cards}张卡片

4. 格式要求：
   - 输出格式为JSON
   - 包含cards数组
   - 每个card对象包含：
     * question：具体明确的问题
     * answer：简洁的单一答案
     * context：必要的背景信息

输入文本：
{input_text}

请生成符合要求的知识卡JSON。
"""

# 填空卡提示模板
CLOZE_CARD_PROMPT = """
你是一个专业的填空卡制作助手。请基于以下SuperMemo制卡原则，将输入的文本转换为高质量的填空卡：

{supermemo_principles}

要求：
1. 每张卡片必须包含三个字段：问题（包含填空标记）、答案和上下文
2. 填空部分应该是关键概念、重要术语或核心事实
3. 每个填空必须有足够的上下文线索来推断答案
4. 答案应该是明确且唯一的
5. 上下文应该提供理解填空内容所需的必要背景信息
6. 生成的卡片数量应该是{num_cards}张
7. 输出格式必须是JSON，包含cards数组，每个card对象包含question、answer和context字段

输入文本：
{input_text}

请生成符合要求的填空卡JSON。
"""

def get_prompt_config(prompt_type: str = "basic") -> Dict[str, Any]:
    """
    获取指定类型的提示模板配置

    Args:
        prompt_type: 提示模板类型，可选值：basic（基础问答卡）或cloze（填空卡）

    Returns:
        包含提示模板和相关配置的字典
    """
    base_config = {
        "temperature": 0.7,
        "max_tokens": 2000,
        "supermemo_principles": SUPERMEMO_PRINCIPLES,
    }

    if prompt_type == "basic":
        return {
            **base_config,
            "template": BASIC_CARD_PROMPT,
            "type": "basic",
            "description": "基础问答卡生成器"
        }
    elif prompt_type == "cloze":
        return {
            **base_config,
            "template": CLOZE_CARD_PROMPT,
            "type": "cloze",
            "description": "填空卡生成器"
        }
    else:
        raise ValueError(f"不支持的提示模板类型：{prompt_type}")

def format_prompt(prompt_type: str, input_text: str, num_cards: int = 3) -> str:
    """
    格式化提示模板

    Args:
        prompt_type: 提示模板类型
        input_text: 输入文本
        num_cards: 要生成的卡片数量

    Returns:
        格式化后的提示文本
    """
    config = get_prompt_config(prompt_type)
    return config["template"].format(
        supermemo_principles=SUPERMEMO_PRINCIPLES,
        input_text=input_text,
        num_cards=num_cards
    ) 