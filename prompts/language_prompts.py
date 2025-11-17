"""语言学习提示配置文件"""

from .common import ROLE_FEYNMAN_ASSISTANT

# JSON格式要求（用于语言模式练习）
LANGUAGE_PATTERN_JSON_FORMAT = """
请确保输出的JSON格式正确，包含以下字段：
1. analysis: 句型分析内容
2. replaceable_parts: 可替换部分的说明
3. examples: 包含例句的数组，每个例句对象包含sentence(句子)、translation(翻译)、grammar_note(语法笔记，可选)和replaced_part(替换部分标识)字段
"""

def get_language_pattern_system_prompt(target_language="日语", language_level=None):
    """获取语言模式练习的系统提示
    
    Args:
        target_language: 目标语言，默认为"日语"
        language_level: 语言级别，如"N3"、"B2"等
    """
    # 根据目标语言和级别选择适当的系统提示
    
    # 设置语言级别描述
    level_description = ""
    if target_language == "日语":
        if language_level:
            if language_level == "N5" or language_level == "N4":
                level_description = f"用户的日语水平为{language_level}（初级），所以需要为所有汉字标注假名注音，使用简单词汇和基础语法。"
            elif language_level == "N3":
                level_description = f"用户的日语水平为{language_level}（中级偏初），所以需要为所有汉字标注假名注音，可以使用一些常见的中级词汇和语法。"
            elif language_level == "N2":
                level_description = f"用户的日语水平为{language_level}（中级），所以需要为大部分汉字标注假名注音，可以使用中级词汇和语法结构。"
            elif language_level == "N1":
                level_description = f"用户的日语水平为{language_level}（高级），可以使用较为高级的词汇和复杂语法结构，但常用汉字仍需标注假名。"
        else:
            level_description = "用户的日语水平为N3~N5，所以需要为所有汉字标注假名注音。"
    
    elif target_language in ["英语", "法语", "德语", "西班牙语"]:
        if language_level:
            if language_level in ["A1", "A2"]:
                level_description = f"用户的{target_language}水平为{language_level}（初级），需要使用基础词汇和简单语法结构。"
            elif language_level in ["B1", "B2"]:
                level_description = f"用户的{target_language}水平为{language_level}（中级），可以使用中级词汇和一定复杂度的语法结构。"
            elif language_level in ["C1", "C2"]:
                level_description = f"用户的{target_language}水平为{language_level}（高级），可以使用较为高级的词汇和复杂语法结构。"
        else:
            level_description = f"用户的{target_language}水平为中级水平，词汇量约3000-5000。"
    
    elif target_language == "韩语":
        if language_level and "初级" in language_level:
            level_description = f"用户的韩语水平为{language_level}，需要使用基础词汇和简单语法结构。"
        elif language_level and "中级" in language_level:
            level_description = f"用户的韩语水平为{language_level}，可以使用中级词汇和一定复杂度的语法结构。"
        elif language_level and "高级" in language_level:
            level_description = f"用户的韩语水平为{language_level}，可以使用较为高级的词汇和复杂语法结构。"
        else:
            level_description = "用户的韩语水平为TOPIK I到TOPIK II初级水平。"
    
    elif target_language == "俄语":
        if language_level == "初级":
            level_description = "用户的俄语水平为初级，需要使用基础词汇和简单语法结构。"
        elif language_level == "中级":
            level_description = "用户的俄语水平为中级，可以使用中级词汇和一定复杂度的语法结构。"
        elif language_level == "高级":
            level_description = "用户的俄语水平为高级，可以使用较为高级的词汇和复杂语法结构。"
        else:
            level_description = "用户的俄语水平为初级到中级水平。"
    
    # 根据目标语言构建基础系统提示
    if target_language == "日语":
        base_prompt = f"""你现在是一个帮助用户进行"句型替换练习"的语言学习助理。{level_description}

目标：
- 根据用户输入的句子，识别出其中的核心句型和可替换的部分
- 解释该句子的基本结构和用法
- 为每个可替换部分分别生成替换示例，每次只替换一个部分

对话格式：
当用户输入想练习的句子后，请按照以下格式回复：

1. **句型分析**：识别核心句型结构，解释基本用法和语法点。

2. **可替换部分**：
   - 明确指出句子中可以替换的不同部分（如形容词、名词、动词等）
   - 确保替换词汇难度符合用户的语言水平

3. **替换示例**：
   - 按照可替换部分分组提供例句
   - 对于每个可替换部分，提供2-3个替换示例
   - 每次只替换句子中的一个部分，保持其他部分完全不变
   - 所有汉字都必须标注假名
   - 提供每个句子的中文翻译

注意事项：
- 如果用户没有提供足够信息，请提问以获取更多上下文
- 所有示例必须符合用户语言水平
- 所有汉字都必须标注假名
- 重要语法点要配合简单的说明
- 教学语言使用中文
- 严格遵循每次只替换一个部分的原则，其他部分保持原样

{LANGUAGE_PATTERN_JSON_FORMAT}
"""
        return base_prompt
    else:
        # 其他语言使用通用模板，根据level_description调整难度
        base_prompt = f"""你现在是一个帮助用户进行"句型替换练习"的语言学习助理。{level_description}

目标：
- 根据用户输入的句子，识别出其中的核心句型和可替换的部分
- 解释该句子的基本结构和用法
- 为每个可替换部分分别生成替换示例，每次只替换一个部分

对话格式：
当用户输入想练习的句子后，请按照以下格式回复：

1. **句型分析**：识别核心句型结构，解释基本用法和语法点。

2. **可替换部分**：
   - 明确指出句子中可以替换的不同部分（如形容词、名词、动词等）
   - 确保替换词汇难度符合用户的语言水平

3. **替换示例**：
   - 按照可替换部分分组提供例句
   - 对于每个可替换部分，提供2-3个替换示例
   - 每次只替换句子中的一个部分，保持其他部分完全不变
   - 提供每个句子的中文翻译

注意事项：
- 如果用户没有提供足够信息，请提问以获取更多上下文
- 所有示例必须符合用户语言水平
- 重要语法点要配合简单的说明
- 教学语言使用中文
- 严格遵循每次只替换一个部分的原则，其他部分保持原样

{LANGUAGE_PATTERN_JSON_FORMAT}
"""
        return base_prompt

def get_language_pattern_prompt(sentence, target_language, specified_parts=None, examples_count=3):
    """生成语言模式练习的提示
    
    Args:
        sentence: 用户输入的句子
        target_language: 目标语言
        specified_parts: 用户指定的要替换的部分（可选）
        examples_count: 每个替换部分生成的例句数量（默认为3）
    """
    
    # 添加调试输出
    print(f"生成语言模式提示 - 目标语言: '{target_language}', 例句数量: {examples_count}")
    
    # 根据目标语言调整提示
    language_specific_instructions = {
        "日语": f"""
- 请为所有汉字标注假名读音，格式为：漢字（かんじ）
- 所有例句使用日语书写，并提供中文翻译
- 难度应在JLPT N3~N5水平范围内
- 每次只替换一个部分，例如：
  1. 如果原句是"一度（いちど）だけ見（み）たことがある"
  2. 替换动词部分时，保持"一度だけ"和"ことがある"不变
  3. 替换副词部分时，保持"見た"和"ことがある"不变
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "英语": f"""
- 所有例句使用英语书写，并提供中文翻译
- 难度应在中级水平范围内，词汇量3000-5000
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "法语": f"""
- 所有例句使用法语书写，并提供中文翻译
- 请标注重要的发音变化和连读
- 难度应在DELF A2-B1水平范围内
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "德语": f"""
- 所有例句使用德语书写，并提供中文翻译
- 请特别注意标记名词的性别
- 难度应在歌德学院A2-B1水平范围内
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "西班牙语": f"""
- 所有例句使用西班牙语书写，并提供中文翻译
- 请标注重要的发音和重音
- 难度应在DELE A2-B1水平范围内
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "韩语": f"""
- 所有例句使用韩语书写，并提供中文翻译
- 难度应在TOPIK I到TOPIK II初级水平范围内
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """,
        "俄语": f"""
- 所有例句使用俄语书写，并提供中文翻译
- 请标注重音位置和发音变化
- 难度应在初级到中级水平范围内
- 每次只替换一个部分，保持句子结构完全相同
- 对于每个可替换部分，请提供{examples_count}个例句
        """
    }
    
    # 获取特定语言的指导
    specific_instructions = language_specific_instructions.get(target_language, "")
    
    # 如果没有找到匹配的语言指令，记录错误并尝试使用默认值
    if not specific_instructions:
        print(f"警告：未找到目标语言 '{target_language}' 的特定指令，尝试使用默认指令")
        # 尝试使用第一个可用的语言指令作为默认值
        if language_specific_instructions:
            default_language = list(language_specific_instructions.keys())[0]
            specific_instructions = language_specific_instructions[default_language]
            print(f"使用默认语言 '{default_language}' 的指令")
    else:
        print(f"成功找到目标语言 '{target_language}' 的特定指令")
    
    # 添加用户指定的替换部分说明（如果有）
    if specified_parts and len(specified_parts) > 0:
        specific_instructions += f"\n\n用户指定要替换的部分：{', '.join(specified_parts)}\n- 请只针对用户指定的这些部分生成替换示例，每个部分生成{examples_count}个例句"
    
    prompt = f"""请帮我分析以下{target_language}句子，并生成句型练习：

"{sentence}"

{specific_instructions}

请按以下格式返回JSON结果：
{{
  "analysis": "句型分析内容",
  "replaceable_parts": "可替换部分的说明",
  "examples": [
    {{
      "sentence": "例句1（替换了第一个可替换部分）",
      "translation": "例句1的中文翻译",
      "grammar_note": "相关语法解释（可选）",
      "replaced_part": "说明替换了哪个部分（如：动词、副词等）"
    }},
    {{
      "sentence": "例句2（替换了第一个可替换部分的另一种情况）",
      "translation": "例句2的中文翻译",
      "grammar_note": "相关语法解释（可选）",
      "replaced_part": "说明替换了哪个部分（如：动词、副词等）"
    }}
    // 更多例句...
  ]
}}

确保输出为有效的JSON格式，以便程序可以正确解析。
对于每个可替换部分，请生成{examples_count}个例句，总共例句数量将取决于可替换部分的数量。
每次只替换一个部分，保持其他部分不变。

例如，对于日语句子"一度（いちど）だけ見（み）たことがある"：
1. 如果识别出"見た"和"一度だけ"是可替换部分
2. 则应分别提供{examples_count}个替换"見た"的例句（保持"一度だけ"和"ことがある"不变）
3. 和{examples_count}个替换"一度だけ"的例句（保持"見た"和"ことがある"不变）
4. 而不是同时替换多个部分"""
    return prompt

def format_language_pattern_messages(sentence, target_language, specified_parts=None, language_level=None, examples_count=3):
    """格式化语言模式练习的消息
    
    Args:
        sentence: 用户输入的句子
        target_language: 目标语言
        specified_parts: 用户指定的要替换的部分（可选）
        language_level: 语言级别（可选，例如"N3"、"B2"等）
        examples_count: 每个替换部分生成的例句数量（可选，默认为3）
    """
    system_prompt = get_language_pattern_system_prompt(target_language, language_level)
    user_prompt = get_language_pattern_prompt(sentence, target_language, specified_parts, examples_count)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return messages 