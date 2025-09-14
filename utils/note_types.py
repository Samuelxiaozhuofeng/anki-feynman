from aqt import mw
from anki.models import NotetypeDict
import json

FEYNMAN_NOTE_TYPE = "费曼学习"
FEYNMAN_CLOZE_TYPE = "费曼学习填空"
KNOWLEDGE_CARD_TYPE = "知识卡"
KNOWLEDGE_CLOZE_TYPE = "知识卡填空"  # 新增知识卡填空类型
LANGUAGE_LEARNING_TYPE = "语言学习助手"  # 新增语言学习笔记类型

# 笔记字段定义
FIELDS = [
    "原始内容",      # 学习的原始文本
    "问题",         # 生成的问题
    "选择题选项",    # 选择题的选项
    "正确答案",     # 标准答案
    "我的回答",     # 用户的回答
    "AI评估"        # AI评估反馈
]

# 填空卡字段定义
CLOZE_FIELDS = [
    "原始内容",      # 学习的原始文本
    "填空内容",      # 包含填空的内容
    "解析"          # 答案解析
]

# 知识卡字段定义
KNOWLEDGE_FIELDS = [
    "问题",     # 问题内容
    "答案",     # 答案内容
    "上下文",   # 相关上下文
    "AI解析"    # AI的分析和解释
]

# 知识卡填空字段定义
KNOWLEDGE_CLOZE_FIELDS = [
    "问题",     # 问题内容
    "填空内容",  # 包含填空的内容
    "答案",     # 答案内容
    "上下文",   # 相关上下文
    "AI解析"    # AI的分析和解释
]

# 语言学习卡字段定义
LANGUAGE_FIELDS = [
    "例句",       # 原始句子
    "翻译",      # 句子翻译
    "语法知识点",  # 语法解释
    "原句",      # 原始句子备份 
    "标签"       # 自定义标签
]

# 卡片模板 - 正面
FRONT_TEMPLATE = """
<div class="question">
    {{问题}}
</div>

<div class="options">
    {{选择题选项}}
</div>
"""

# 卡片模板 - 背面
BACK_TEMPLATE = """
<div class="original-content">
    <div class="label">原始内容：</div>
    <div class="content">{{原始内容}}</div>
</div>

<hr>

<div class="answer">
    <div class="label">正确答案：</div>
    <div class="content">{{正确答案}}</div>
</div>

<hr>

<div class="my-answer">
    <div class="label">我的回答：</div>
    <div class="content">{{我的回答}}</div>
</div>

<hr>

<div class="ai-feedback">
    <div class="label">AI评估：</div>
    <div class="content">{{AI评估}}</div>
</div>
"""

# 知识卡模板 - 正面
KNOWLEDGE_FRONT_TEMPLATE = """
<div class="card-content">
    <div class="question-section">
        <div class="question-label">问题</div>
        <div class="question-content">{{问题}}</div>
    </div>
</div>
"""

# 知识卡模板 - 背面
KNOWLEDGE_BACK_TEMPLATE = """
<div class="card-content">
    <div class="question-section">
        <div class="question-label">问题</div>
        <div class="question-content">{{问题}}</div>
    </div>
    
    <hr class="divider">
    
    <div class="answer-section">
        <div class="answer-label">答案</div>
        <div class="answer-content">{{答案}}</div>
    </div>
    
    <hr class="divider">
    
    <div class="context-section">
        <div class="context-label">上下文</div>
        <div class="context-content">{{上下文}}</div>
    </div>
    
    <div class="ai-analysis-section">
        <div class="ai-label">AI解析</div>
        <div class="ai-content">{{AI解析}}</div>
    </div>
</div>
"""

# 知识卡填空模板
KNOWLEDGE_CLOZE_FRONT = """
<div class="card-content">
    <div class="question-section">
        <div class="question-label">问题</div>
        <div class="question-content">{{问题}}</div>
    </div>
    
    <div class="cloze-section">
        <div class="cloze-content">{{cloze:填空内容}}</div>
    </div>
</div>
"""

KNOWLEDGE_CLOZE_BACK = """
<div class="card-content">
    <div class="question-section">
        <div class="question-label">问题</div>
        <div class="question-content">{{问题}}</div>
    </div>
    
    <div class="cloze-section">
        <div class="cloze-content">{{cloze:填空内容}}</div>
    </div>
    
    <hr class="divider">
    
    <div class="answer-section">
        <div class="answer-label">答案</div>
        <div class="answer-content">{{答案}}</div>
    </div>
    
    <div class="context-section">
        <div class="context-label">上下文</div>
        <div class="context-content">{{上下文}}</div>
    </div>
    
    <div class="ai-analysis-section">
        <div class="ai-label">AI解析</div>
        <div class="ai-content">{{AI解析}}</div>
    </div>
</div>
"""

# 卡片样式
CARD_STYLING = """
.card {
    font-family: "Microsoft YaHei", Arial, sans-serif;
    font-size: 16px;
    text-align: left;
    color: #333;
    line-height: 1.5;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    background-color: #fff;
}

.question {
    font-size: 18px;
    color: #2196F3;
    margin-bottom: 20px;
    padding: 15px;
    border-left: 4px solid #2196F3;
    background-color: #E3F2FD;
}

.options {
    margin: 15px 0;
}

.option-group {
    margin: 10px 0;
    padding: 8px 15px;
    background-color: #F5F5F5;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.option-group:hover {
    background-color: #E3F2FD;
}

.label {
    font-weight: bold;
    color: #1976D2;
    margin-bottom: 5px;
}

.content {
    white-space: pre-wrap;
    padding: 5px 0;
}

.original-content {
    background-color: #F5F5F5;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
}

.answer, .my-answer {
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
}

.answer {
    background-color: #E8F5E9;
}

.my-answer {
    background-color: #FFF3E0;
}

.ai-feedback {
    background-color: #F3E5F5;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
}

hr {
    border: none;
    border-top: 1px solid #E0E0E0;
    margin: 15px 0;
}
"""

# 知识卡样式
KNOWLEDGE_CARD_STYLING = """
.card {
    font-family: "Microsoft YaHei", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #2c3e50;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    background-color: #ffffff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-content {
    padding: 15px;
}

.question-section,
.answer-section,
.context-section,
.ai-analysis-section {
    margin-bottom: 20px;
    padding: 15px;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.question-label,
.answer-label,
.context-label,
.ai-label {
    font-weight: bold;
    color: #1a73e8;
    margin-bottom: 8px;
    font-size: 1.1em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.question-content {
    font-size: 1.2em;
    color: #202124;
    padding: 10px;
    background-color: #e8f0fe;
    border-radius: 6px;
}

.answer-content {
    padding: 10px;
    background-color: #e6f4ea;
    border-radius: 6px;
}

.context-content {
    padding: 10px;
    background-color: #fef7e0;
    border-radius: 6px;
    font-size: 0.95em;
}

.ai-content {
    padding: 10px;
    background-color: #f3e8fd;
    border-radius: 6px;
    font-style: italic;
}

.divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #e0e0e0, transparent);
    margin: 20px 0;
}

/* 夜间模式适配 */
.nightMode .card {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

.nightMode .question-section,
.nightMode .answer-section,
.nightMode .context-section,
.nightMode .ai-analysis-section {
    background-color: #383838;
}

.nightMode .question-content {
    background-color: #3c4043;
}

.nightMode .answer-content {
    background-color: #2e3b2f;
}

.nightMode .context-content {
    background-color: #3c3831;
}

.nightMode .ai-content {
    background-color: #3a3045;
}
"""

# 知识卡填空样式
KNOWLEDGE_CLOZE_STYLING = """
.card {
    font-family: "Microsoft YaHei", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #2c3e50;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    background-color: #ffffff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.card-content {
    padding: 15px;
}

.question-section,
.cloze-section,
.answer-section,
.context-section,
.ai-analysis-section {
    margin-bottom: 20px;
    padding: 15px;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.question-label,
.answer-label,
.context-label,
.ai-label {
    font-weight: bold;
    color: #1a73e8;
    margin-bottom: 8px;
    font-size: 1.1em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.question-content {
    font-size: 1.2em;
    color: #202124;
    padding: 10px;
    background-color: #e8f0fe;
    border-radius: 6px;
}

.cloze-section {
    background-color: #e3f2fd;
    border-left: 4px solid #2196F3;
}

.cloze-content {
    font-size: 1.1em;
    padding: 10px;
}

.cloze {
    font-weight: bold;
    color: #1976D2;
    padding: 2px 4px;
    border-bottom: 2px solid #1976D2;
}

.answer-content {
    padding: 10px;
    background-color: #e6f4ea;
    border-radius: 6px;
}

.context-content {
    padding: 10px;
    background-color: #fef7e0;
    border-radius: 6px;
    font-size: 0.95em;
}

.ai-content {
    padding: 10px;
    background-color: #f3e8fd;
    border-radius: 6px;
    font-style: italic;
}

.divider {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #e0e0e0, transparent);
    margin: 20px 0;
}

/* 夜间模式适配 */
.nightMode .card {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

.nightMode .question-section,
.nightMode .cloze-section,
.nightMode .answer-section,
.nightMode .context-section,
.nightMode .ai-analysis-section {
    background-color: #383838;
}

.nightMode .question-content {
    background-color: #3c4043;
}

.nightMode .cloze-section {
    background-color: #1a3f5f;
    border-left-color: #64b5f6;
}

.nightMode .cloze {
    color: #64b5f6;
    border-bottom-color: #64b5f6;
}

.nightMode .answer-content {
    background-color: #2e3b2f;
}

.nightMode .context-content {
    background-color: #3c3831;
}

.nightMode .ai-content {
    background-color: #3a3045;
}
"""

# 语言学习卡模板 - 正面
LANGUAGE_FRONT_TEMPLATE = """
<div class="sentence">
    {{例句}}
</div>
"""

# 语言学习卡模板 - 背面
LANGUAGE_BACK_TEMPLATE = """
<div class="sentence">
    {{例句}}
</div>

<hr>
<div class="translation">
    <div class="label">翻译：</div>
    <div class="content">{{翻译}}</div>
</div>

<hr>
<div class="grammar">
    <div class="label">语法知识点：</div>
    <div class="content">{{语法知识点}}</div>
</div>

<hr>
<div class="original">
    <div class="label">原句：</div>
    <div class="content">{{原句}}</div>
</div>
"""

# 语言学习卡样式
LANGUAGE_CARD_STYLING = """
.card {
    font-family: "Microsoft YaHei", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #2c3e50;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    background-color: #ffffff;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sentence {
    font-size: 1.2em;
    color: #202124;
    padding: 15px;
    background-color: #e8f0fe;
    border-radius: 6px;
    margin-bottom: 15px;
}

.translation,
.grammar,
.original {
    margin-bottom: 20px;
    padding: 15px;
    border-radius: 8px;
    background-color: #f8f9fa;
}

.label {
    font-weight: bold;
    color: #1a73e8;
    margin-bottom: 8px;
}

.content {
    color: #202124;
}

hr {
    border: none;
    border-top: 1px solid #e0e0e0;
    margin: 20px 0;
}
"""

def create_feynman_note_type() -> NotetypeDict:
    """创建费曼学习笔记类型"""
    # 检查是否已存在
    existing = mw.col.models.by_name(FEYNMAN_NOTE_TYPE)
    if existing:
        return existing

    # 创建新的笔记类型
    model = mw.col.models.new(FEYNMAN_NOTE_TYPE)
    
    # 添加字段
    for field in FIELDS:
        template = mw.col.models.new_field(field)
        mw.col.models.add_field(model, template)

    # 添加卡片模板
    template = mw.col.models.new_template("费曼学习卡片")
    template['qfmt'] = FRONT_TEMPLATE  # 问题面
    template['afmt'] = BACK_TEMPLATE   # 答案面
    mw.col.models.add_template(model, template)

    # 添加样式
    model['css'] = CARD_STYLING

    # 保存模型
    mw.col.models.add(model)
    mw.col.models.save(model)
    
    return model

def create_feynman_cloze_type() -> NotetypeDict:
    """创建费曼学习填空卡类型"""
    # 检查是否已存在
    existing = mw.col.models.by_name(FEYNMAN_CLOZE_TYPE)
    if existing:
        return existing

    # 创建新的笔记类型
    model = mw.col.models.new(FEYNMAN_CLOZE_TYPE)
    
    # 设置为填空类型
    model['type'] = 1  # 1 表示填空类型
    
    # 添加字段
    for field in CLOZE_FIELDS:
        template = mw.col.models.new_field(field)
        mw.col.models.add_field(model, template)

    # 添加卡片模板
    template = mw.col.models.new_template("费曼学习填空卡片")
    template['qfmt'] = """
<div class="sentence">
    {{cloze:填空内容}}
</div>
"""
    template['afmt'] = """
<div class="sentence">
    {{cloze:填空内容}}
</div>

<hr>
<div class="original">
    <div class="label">原始内容：</div>
    <div class="content">{{原始内容}}</div>
</div>

<hr>
<div class="explanation">
    <div class="label">解析：</div>
    <div class="content">{{解析}}</div>
</div>
"""
    # 添加模板到模型
    mw.col.models.add_template(model, template)

    # 添加样式
    model['css'] = """
/* Neon Tech Style */

/* Base Card Style */
.card {
  font-family: 'Roboto Mono', monospace;
  font-size: 15px;
  line-height: 1.5;
  padding: 30px;
  max-width: 750px;
  margin: 30px auto;
  background-color: #0f0f1a;
  color: #d8d8f0;
  border-radius: 2px;
  box-shadow: 0 0 20px rgba(114, 137, 218, 0.2);
  border: 1px solid #2a2a40;
  position: relative;
  overflow: hidden;
}


.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, #ff2a6d, #05d9e8);
}

/* Original Text Section */
.original {
  background: #171727;
  color: #a9a9c9;
  font-size: 15px;
  padding: 18px;
  border-radius: 2px;
  margin-bottom: 22px;
  border-left: 2px solid #05d9e8;
}


.sentence {
  font-weight: 600;
  padding: 10px;
  color: #00e5ff;

}


.cloze {
  font-weight: 600;
  padding: 2px 4px;
  font-size: 15px;
  color: #00e5ff;
  background-color: rgba(0, 229, 255, 0.08);
  display: inline-block;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 100% {
    text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.25);
  }
  50% {
    text-shadow: 0 0 16px rgba(0, 229, 255, 0.9);
    box-shadow: 0 0 24px rgba(0, 229, 255, 0.5);
  }
}





/* Explanation Section */
.explanation {
  background: #171727;
  border-left: 2px solid #05d9e8;
  padding: 18px;
  border-radius: 2px;
  margin: 22px 0;
}

.explanation .label {
  font-weight: 600;
  color: #05d9e8;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 10px;
  text-shadow: 0 0 8px rgba(5, 217, 232, 0.4);
}

.explanation .content {
  padding: 5px 0;
  line-height: 1.6;
}

/* Divider */
hr {
  border: none;
  height: 1px;
  background: linear-gradient(to right, #ff2a6d, #05d9e8);
  margin: 22px 0;
  box-shadow: 0 0 8px rgba(114, 137, 218, 0.4);
}
"""

    # 保存模型
    mw.col.models.add(model)
    mw.col.models.save(model)
    
    return model

def create_knowledge_card_type() -> NotetypeDict:
    """创建知识卡笔记类型"""
    # 检查是否已存在
    existing = mw.col.models.by_name(KNOWLEDGE_CARD_TYPE)
    if existing:
        return existing

    # 创建新的笔记类型
    model = mw.col.models.new(KNOWLEDGE_CARD_TYPE)
    
    # 添加字段
    for field in KNOWLEDGE_FIELDS:
        template = mw.col.models.new_field(field)
        mw.col.models.add_field(model, template)

    # 添加卡片模板
    template = mw.col.models.new_template("知识卡")
    template['qfmt'] = KNOWLEDGE_FRONT_TEMPLATE
    template['afmt'] = KNOWLEDGE_BACK_TEMPLATE
    mw.col.models.add_template(model, template)

    # 添加样式
    model['css'] = KNOWLEDGE_CARD_STYLING

    # 保存模型
    mw.col.models.add(model)
    mw.col.models.save(model)
    
    return model

def create_knowledge_cloze_type() -> NotetypeDict:
    """创建知识卡填空类型"""
    # 检查是否已存在
    existing = mw.col.models.by_name(KNOWLEDGE_CLOZE_TYPE)
    if existing:
        return existing

    # 创建新的笔记类型
    model = mw.col.models.new(KNOWLEDGE_CLOZE_TYPE)
    
    # 设置为填空类型
    model['type'] = 1  # 1 表示填空类型
    
    # 添加字段
    for field in KNOWLEDGE_CLOZE_FIELDS:
        template = mw.col.models.new_field(field)
        mw.col.models.add_field(model, template)

    # 添加卡片模板
    template = mw.col.models.new_template("知识卡填空")
    template['qfmt'] = KNOWLEDGE_CLOZE_FRONT
    template['afmt'] = KNOWLEDGE_CLOZE_BACK
    mw.col.models.add_template(model, template)

    # 添加样式
    model['css'] = KNOWLEDGE_CLOZE_STYLING

    # 保存模型
    mw.col.models.add(model)
    mw.col.models.save(model)
    
    return model

def create_language_learning_type() -> NotetypeDict:
    """创建语言学习笔记类型"""
    # 检查是否已存在
    existing = mw.col.models.by_name(LANGUAGE_LEARNING_TYPE)
    if existing:
        return existing

    # 创建新的笔记类型
    model = mw.col.models.new(LANGUAGE_LEARNING_TYPE)
    
    # 添加字段
    for field in LANGUAGE_FIELDS:
        template = mw.col.models.new_field(field)
        mw.col.models.add_field(model, template)

    # 添加卡片模板
    template = mw.col.models.new_template("语言学习")
    template['qfmt'] = LANGUAGE_FRONT_TEMPLATE
    template['afmt'] = LANGUAGE_BACK_TEMPLATE
    mw.col.models.add_template(model, template)

    # 添加样式
    model['css'] = LANGUAGE_CARD_STYLING

    # 保存模型
    mw.col.models.add(model)
    mw.col.models.save(model)
    
    return model

def ensure_note_types():
    """确保所有笔记类型都已创建"""
    if not mw.col:
        return
        
    create_feynman_note_type()
    create_feynman_cloze_type()
    create_knowledge_card_type()
    create_knowledge_cloze_type()  # 添加知识卡填空类型的创建
    create_language_learning_type()  # 添加语言学习类型的创建

def create_feynman_note(deck_id: int, content: str, question: str, 
                       correct_answer: str, my_answer: str, 
                       ai_feedback: str, mastery: str, tags: list[str] = None):
    """创建一个新的费曼学习笔记"""
    if not mw.col:
        raise Exception("Anki集合未加载")
        
    # 确保笔记类型存在
    ensure_note_types()
    model = create_feynman_note_type()
    note = mw.col.new_note(model)
    
    # 设置字段值
    note['原始内容'] = content
    note['问题'] = question
    note['正确答案'] = correct_answer
    note['我的回答'] = my_answer
    note['AI评估'] = ai_feedback
    
    # 添加标签
    if tags:
        note.tags = tags
    
    # 添加到牌组
    mw.col.add_note(note, deck_id)
    
    return note

def ensure_language_learning_type():
    """确保语言学习笔记类型已创建"""
    if not mw.col:
        return None
    return create_language_learning_type() 