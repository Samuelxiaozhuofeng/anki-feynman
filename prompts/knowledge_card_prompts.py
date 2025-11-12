"""
知识卡提示模板模块，包含生成知识卡所需的各种提示模板。
"""

from typing import Dict, Any

# 语言学习知识卡提示模板
LANGUAGE_LEARNING_CARD_PROMPT = """
你是一个专业的语言学习卡片制作助手。请分析用户的语言学习材料，智能识别材料类型，并从中提取重要的学习要点，制作成知识卡片。

## 第一步：识别材料类型

用户的学习材料可能是以下类型之一或混合：

### 类型A：纠错材料
- 包含原句和纠正信息（如Correction、错误标注、语法改正等）
- 可能包含表达建议（Expression suggestion）
- 重点：错误点、正确用法对比

### 类型B：纯学习材料
- 课文、对话、例句、语法说明等
- 没有明显的纠错信息
- 重点：语法知识点、词汇用法、表达方式、句型结构

### 类型C：混合材料
- 既包含纠错，也包含学习内容
- 需要分别提取

## 第二步：智能提取知识点

**如果是纠错材料**：
- 识别错误类型（语法、词汇、拼写、表达方式等）
- 提取"错误→正确"的对比
- 说明错误原因和正确用法规则
- 每个错误点制作一张卡片

**如果是学习材料**：
- 提取重要的语法结构和规则
- 识别关键词汇的用法和搭配
- 总结句型模式
- 提取表达方式和习惯用法
- 每个独立的知识点制作一张卡片

## 第三步：制作卡片

**卡片结构**：
- **问题（question）**：用疑问句形式，清晰地提出学习重点
  - 纠错类："XXX的正确用法是什么？"、"为什么不能用XXX？"
  - 学习类："XXX语法结构如何使用？"、"XXX词汇在什么情境下使用？"
  
- **答案（answer）**：简洁明了的解释和正确用法
  - 突出关键点
  - 必要时给出规则说明
  
- **上下文（context）**：提供完整背景信息
  - 纠错类：原句、纠正句、错误原因、正确规则
  - 学习类：例句、用法场景、相关说明

## 输出格式

输出为JSON格式，包含cards数组：
```json
{{
  "cards": [
    {{
      "question": "清晰的问题",
      "answer": "简洁的答案和解释",
      "context": "相关上下文和例句"
    }}
  ]
}}
```

## 示例

**纠错材料示例**：
输入："costaba mucho tiempo → 应该用gastaba mucho tiempo"
卡片：
- 问题："表达'花费时间'时应该用costar还是gastar？"
- 答案："应该用gastar tiempo，而不是costar tiempo。Costar表示'花费金钱/代价'，gastar表示'花费时间/金钱'"
- 上下文："错误：costaba mucho tiempo\n正确：gastaba mucho tiempo\n说明：costar和gastar的区别"

**学习材料示例**：
输入："虚拟式现在时用于表达愿望、怀疑、否定等情绪。例如：Espero que vengas mañana."
卡片：
- 问题："西班牙语虚拟式现在时主要用于哪些情况？"
- 答案："虚拟式现在时用于表达愿望（esperar que）、怀疑（dudar que）、否定（no creer que）等主观情绪和非事实内容"
- 上下文："例句：Espero que vengas mañana (我希望你明天来)\n特点：que引导的从句中使用虚拟式"

---

输入文本：
{input_text}

请先识别材料类型，然后生成约{num_cards}张知识卡片（根据实际学习要点数量灵活调整）。
确保每张卡片聚焦一个明确的知识点，问题清晰，答案实用。
"""

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
        prompt_type: 提示模板类型，可选值：basic（基础问答卡）、cloze（填空卡）或language_learning（语言学习知识卡）

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
    elif prompt_type == "language_learning":
        return {
            **base_config,
            "template": LANGUAGE_LEARNING_CARD_PROMPT,
            "type": "language_learning",
            "description": "语言学习知识卡生成器"
        }
    else:
        raise ValueError(f"不支持的提示模板类型：{prompt_type}")

def format_prompt(prompt_type: str, input_text: str, num_cards: int = 3, language: str = "中文") -> str:
    """
    格式化提示模板

    Args:
        prompt_type: 提示模板类型
        input_text: 输入文本
        num_cards: 要生成的卡片数量
        language: 生成内容使用的语言

    Returns:
        格式化后的提示文本
    """
    # 添加语言指示
    language_instruction = f"请使用{language}生成所有知识卡的问题、答案和上下文。\n\n"
    
    config = get_prompt_config(prompt_type)
    
    # 对于语言学习类型，不需要supermemo_principles
    if prompt_type == "language_learning":
        return language_instruction + config["template"].format(
            input_text=input_text,
            num_cards=num_cards
        )
    else:
        return language_instruction + config["template"].format(
            supermemo_principles=SUPERMEMO_PRINCIPLES,
            input_text=input_text,
            num_cards=num_cards
        ) 