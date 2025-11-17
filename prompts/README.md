# Prompts 模块使用指南

## 📁 模块结构

```
prompts/
├── common.py                    # 公共常量和工具函数
├── system_prompts.py           # 系统级提示词
├── choice_prompts.py           # 选择题生成提示词
├── essay_prompts.py            # 问答题生成提示词
├── evaluation_prompts.py       # 评估相关提示词
├── knowledge_card_prompts.py   # 知识卡片生成提示词
├── language_prompts.py         # 语言学习提示词
└── followup_prompts.py         # 追问处理提示词
```

## 🔧 公共模块 (common.py)

### 常量

#### JSON格式要求
- `JSON_FORMAT_BASIC` - 基础JSON格式要求
- `JSON_FORMAT_DETAILED` - 详细JSON格式要求（包含示例）
- `JSON_COMPLIANCE_SHORT` - 简短合规性说明
- `JSON_COMPLIANCE_FULL` - 完整合规性说明

#### 角色定义
- `ROLE_FEYNMAN_ASSISTANT` - 费曼学习法助手
- `ROLE_EDUCATOR` - 教育内容开发者
- `ROLE_EVALUATOR` - 评估专家
- `ROLE_LANGUAGE_EXPERT` - 语言学习专家
- `ROLE_LEARNING_STRATEGIST` - 学习策略专家

#### 原则说明
- `FEYNMAN_PRINCIPLES_BRIEF` - 费曼学习法简要原则
- `SUPERMEMO_PRINCIPLES` - SuperMemo制卡原则

### 工具函数

#### `add_language_instruction(language, content_type)`
生成语言指示文本。

**参数：**
- `language` (str): 目标语言，如"中文"、"英语"
- `content_type` (str): 内容类型描述，如"问题和答案"

**返回：**
- str: 格式化的语言指示

**示例：**
```python
from prompts.common import add_language_instruction

instruction = add_language_instruction("中文", "问题和答案")
# 输出: "请使用中文生成所有问题和答案。\n\n"
```

#### `format_with_language(template, language, content_type, **kwargs)`
为模板添加语言指示并格式化。

**参数：**
- `template` (str): 提示词模板
- `language` (str): 目标语言
- `content_type` (str): 内容类型描述
- `**kwargs`: 模板中的占位符参数

**返回：**
- str: 格式化后的完整提示词

**示例：**
```python
from prompts.common import format_with_language

template = "请分析以下内容：{content}"
result = format_with_language(
    template,
    "中文",
    "分析结果",
    content="这是要分析的内容"
)
```

## 📝 使用示例

### 1. 生成选择题

```python
from prompts.choice_prompts import get_choice_prompt

prompt = get_choice_prompt(
    content="量子力学的基本原理...",
    num_questions=5,
    language="中文"
)
```

### 2. 生成问答题

```python
from prompts.essay_prompts import get_essay_prompt

prompt = get_essay_prompt(
    content="机器学习的基本概念...",
    num_questions=3,
    language="中文"
)
```

### 3. 生成知识卡片

```python
from prompts.knowledge_card_prompts import format_prompt

# 基础问答卡
prompt = format_prompt(
    prompt_type="basic",
    input_text="深度学习是...",
    num_cards=5,
    language="中文"
)

# 填空卡
prompt = format_prompt(
    prompt_type="cloze",
    input_text="神经网络包含...",
    num_cards=3,
    language="中文"
)

# 语言学习卡
prompt = format_prompt(
    prompt_type="language_learning",
    input_text="Je suis étudiant...",
    num_cards=4,
    language="中文"
)
```

### 4. 评估答案

```python
from prompts.evaluation_prompts import get_essay_evaluation_prompt

prompt = get_essay_evaluation_prompt(
    question="什么是机器学习？",
    reference_answer="机器学习是...",
    key_points=["监督学习", "无监督学习", "强化学习"],
    user_answer="机器学习就是...",
    language="中文"
)
```

## 🎯 最佳实践

### 1. 复用公共常量

在创建新的提示词时，优先使用`common.py`中的常量：

```python
from prompts.common import ROLE_EDUCATOR, JSON_FORMAT_DETAILED

MY_PROMPT = f"""{ROLE_EDUCATOR}请完成以下任务...

{JSON_FORMAT_DETAILED}
"""
```

### 2. 使用工具函数

使用`format_with_language()`统一处理语言指示：

```python
from prompts.common import format_with_language

def my_prompt_function(content, language="中文"):
    template = "分析：{content}"
    return format_with_language(
        template,
        language,
        "分析结果",
        content=content
    )
```

### 3. 模板格式化注意事项

当模板需要两层格式化时，注意大括号的转义：

```python
# 第一层：替换角色和常量
TEMPLATE = """{role_description}
生成{num_items}个项目：
{content}
"""

# 第二层：在函数中替换实际值
def format_template(content, num_items):
    template = TEMPLATE.format(
        role_description=ROLE_EDUCATOR,
        content="{content}",      # 保留占位符
        num_items="{num_items}"   # 保留占位符
    )
    return template.format(
        content=content,
        num_items=num_items
    )
```

## 🔄 维护指南

### 添加新常量

如果发现多处使用相同的文本，应该将其提取到`common.py`：

1. 在`common.py`中定义常量
2. 在需要使用的文件中导入
3. 替换原有的重复文本

### 添加新提示词文件

1. 导入需要的公共常量和函数
2. 定义特定的提示词模板
3. 提供格式化函数
4. 使用`format_with_language()`处理语言指示

## 📚 相关文档

- [REFACTORING_SUMMARY.md](../REFACTORING_SUMMARY.md) - 重构总结报告

