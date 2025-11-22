# Anki 费曼学习插件 - 优化建议报告

**分析日期**: 2025-11-17  
**插件版本**: v0.1.0

---

## 📊 插件概述

这是一个功能丰富的 Anki 插件，使用 AI（OpenAI/自定义 API）帮助用户通过费曼学习法生成学习卡片。

**主要功能**：
- ✅ 选择题/问答题/知识卡片生成
- ✅ 语言学习练习
- ✅ PDF 导入和处理
- ✅ 并发处理和文本分块（已优化）
- ✅ 自定义提示词模板
- ✅ 提示词冗余优化（已完成）

**技术栈**：
- Python 3.7+
- PyQt6 (Anki UI)
- OpenAI API / 自定义 API
- 异步处理 (aiohttp, async-timeout)

---

## 🎯 优化建议（按优先级排序）

### 1. ⚠️ **测试覆盖率 - 高优先级**

**现状**：
- ❌ 代码库中**完全没有单元测试**
- ❌ 只有 vendor 依赖库中有测试文件
- ❌ 缺乏自动化测试导致重构和新功能开发风险高

**影响**：
- 代码质量无法保证
- 重构时容易引入 bug
- 难以验证复杂逻辑（如 JSON 修复、文本分块）

**建议**：

#### 1.1 创建测试基础设施

```
tests/
├── __init__.py
├── conftest.py                    # pytest 配置和 fixtures
├── test_ai_handler.py             # AI 处理器测试
├── test_text_chunker.py           # 文本分块测试
├── test_concurrent_processor.py   # 并发处理测试
├── test_response_handler.py       # 响应处理测试（重要！）
├── test_prompts/
│   ├── __init__.py
│   ├── test_choice_prompts.py
│   ├── test_essay_prompts.py
│   └── test_knowledge_card_prompts.py
├── test_utils/
│   ├── test_anki_operations.py
│   └── test_question_utils.py
└── fixtures/
    ├── sample_responses.json      # 模拟 AI 响应
    ├── sample_texts.txt           # 测试文本
    └── sample_pdfs/
```

#### 1.2 优先测试的模块

**高优先级**：
1. `utils/response_handler.py` - JSON 解析和修复逻辑复杂，容易出错
2. `utils/text_chunker.py` - 文本分块算法需要验证边界情况
3. `utils/concurrent_processor.py` - 并发逻辑需要测试竞态条件
4. `prompts/common.py` - 公共提示词组件

**中优先级**：
5. `utils/ai_handler.py` - 需要 mock API 调用
6. `utils/anki_operations.py` - 需要 mock Anki 数据库

#### 1.3 示例测试代码

```python
# tests/test_response_handler.py
import pytest
from utils.response_handler import ResponseHandler

class TestResponseHandler:
    def test_clean_response_removes_code_blocks(self):
        handler = ResponseHandler()
        response = "```json\n{\"key\": \"value\"}\n```"
        cleaned = handler.clean_response(response)
        assert cleaned == '{"key": "value"}'
    
    def test_fix_incomplete_json(self):
        handler = ResponseHandler()
        incomplete = '{"questions": [{"q": "test"'
        fixed = handler.fix_incomplete_json(incomplete)
        # 验证修复后的 JSON 可以解析
        import json
        json.loads(fixed)
    
    @pytest.mark.parametrize("input,expected", [
        ('{"a": "b"\n"c": "d"}', '{"a": "b",\n"c": "d"}'),
        ('{"arr": ["a" "b"]}', '{"arr": ["a", "b"]}'),
    ])
    def test_advanced_json_fix(self, input, expected):
        handler = ResponseHandler()
        fixed = handler.advanced_json_fix(input)
        assert fixed == expected
```

#### 1.4 测试工具推荐

```bash
# requirements-dev.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
```

**预期收益**：
- ✅ 提高代码质量和可靠性
- ✅ 重构时有信心
- ✅ 快速发现回归问题
- ✅ 文档化预期行为

---

### 2. ⚠️ **错误处理和日志 - 高优先级**

**现状**：
- ⚠️ 使用通用 `Exception`，不够精细
- ⚠️ 使用 `print()` 而非结构化日志
- ⚠️ 错误消息对用户不够友好
- ⚠️ 缺少错误追踪和调试信息

**问题示例**：

```python
# utils/ai_handler.py:102-108
except Exception as e:
    error_msg = f"API调用失败：{str(e)}"
    if hasattr(e, 'response') and e.response is not None:
        error_msg += f"\n响应状态码：{e.response.status_code}"
        error_msg += f"\n响应内容：{e.response.text}"
    raise Exception(error_msg)  # ❌ 通用异常
```

**建议**：

#### 2.1 创建自定义异常类

```python
# utils/exceptions.py
class FeynmanPluginError(Exception):
    """插件基础异常"""
    pass

class APIError(FeynmanPluginError):
    """API 调用相关错误"""
    def __init__(self, message, status_code=None, response_text=None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)

class APIKeyMissingError(APIError):
    """API Key 未配置"""
    pass

class APIRateLimitError(APIError):
    """API 速率限制"""
    pass

class JSONParseError(FeynmanPluginError):
    """JSON 解析错误"""
    def __init__(self, message, raw_response=None):
        self.raw_response = raw_response
        super().__init__(message)

class TextChunkingError(FeynmanPluginError):
    """文本分块错误"""
    pass

class ConcurrentProcessingError(FeynmanPluginError):
    """并发处理错误"""
    pass
```

#### 2.2 实现结构化日志

```python
# utils/logger.py
import logging
import os
from datetime import datetime

def setup_logger(name='anki_feynman'):
    """设置插件日志"""
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # 控制台 handler（仅显示 WARNING 及以上）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # 文件 handler（记录所有级别）
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'feynman_{datetime.now():%Y%m%d}.log')

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 使用示例
logger = setup_logger()
```

#### 2.3 改进错误处理示例

```python
# utils/ai_handler.py (改进后)
from .exceptions import APIError, APIKeyMissingError, APIRateLimitError, JSONParseError
from .logger import setup_logger

logger = setup_logger()

def _call_ai_api(self, messages):
    """调用AI API"""
    try:
        logger.debug(f"调用 AI API，provider={self.provider}, model={self.model}")

        if self.provider == 'openai':
            return self._call_openai(messages)
        else:
            return self._call_custom_api(messages)

    except APIKeyMissingError:
        logger.error("API Key 未配置")
        raise  # 重新抛出，让 UI 层处理
    except APIRateLimitError as e:
        logger.warning(f"API 速率限制：{e}")
        raise
    except APIError as e:
        logger.error(f"API 调用失败：{e}", exc_info=True)
        raise
    except Exception as e:
        logger.exception(f"未预期的错误：{e}")
        raise APIError(f"API 调用失败：{str(e)}")

def _call_openai(self, messages):
    """调用OpenAI API"""
    if not openai.api_key:
        raise APIKeyMissingError("OpenAI API Key未设置，请在设置中配置API密钥")

    try:
        # ... API 调用代码 ...
        logger.info(f"OpenAI API 调用成功，model={self.model}")
        return response.choices[0].message.content

    except openai.error.RateLimitError as e:
        raise APIRateLimitError("API 速率限制，请稍后重试", status_code=429)
    except openai.error.AuthenticationError as e:
        raise APIKeyMissingError("API Key 无效，请检查配置")
    except Exception as e:
        logger.error(f"OpenAI API 调用失败：{e}", exc_info=True)
        raise APIError(f"OpenAI API 调用失败：{str(e)}")
```

**预期收益**：
- ✅ 更精确的错误诊断
- ✅ 更好的用户体验（友好的错误消息）
- ✅ 便于调试和问题追踪
- ✅ 生产环境问题排查

---

### 3. 🔧 **性能优化 - 中优先级**

**现状**：
- ✅ 已实现并发处理和文本分块（很好！）
- ⚠️ 但仍有优化空间

#### 3.1 缓存机制

**问题**：相同的文本重复调用 API 会浪费成本和时间

**建议**：实现简单的缓存

```python
# utils/cache.py
import hashlib
import json
import os
from datetime import datetime, timedelta

class ResponseCache:
    """AI 响应缓存"""

    def __init__(self, cache_dir=None, ttl_hours=24):
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(__file__), '..', 'cache'
        )
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_key(self, text, question_type, num_questions, model):
        """生成缓存键"""
        content = f"{text}|{question_type}|{num_questions}|{model}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text, question_type, num_questions, model):
        """获取缓存"""
        key = self._get_cache_key(text, question_type, num_questions, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查是否过期
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                os.remove(cache_file)
                return None

            return data['response']
        except Exception:
            return None

    def set(self, text, question_type, num_questions, model, response):
        """设置缓存"""
        key = self._get_cache_key(text, question_type, num_questions, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")

        data = {
            'timestamp': datetime.now().isoformat(),
            'response': response
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear_expired(self):
        """清理过期缓存"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    cached_time = datetime.fromisoformat(data['timestamp'])
                    if datetime.now() - cached_time > self.ttl:
                        os.remove(filepath)
                except Exception:
                    pass
```

#### 3.2 批量处理优化

**当前问题**：`concurrent_processor.py` 已经很好，但可以添加自适应并发数

```python
# utils/concurrent_processor.py (增强版)
class ConcurrentProcessor:
    def __init__(self, max_workers: int = 3):
        self.max_workers = max(1, min(max_workers, 10))
        self._cancel_flag = threading.Event()
        self._adaptive_mode = True  # 新增：自适应模式
        self._success_rate = 1.0    # 新增：成功率追踪

    def _adjust_workers(self, success_rate):
        """根据成功率自适应调整并发数"""
        if not self._adaptive_mode:
            return

        if success_rate < 0.7:  # 成功率低于70%
            # 降低并发数
            self.max_workers = max(1, self.max_workers - 1)
            logger.warning(f"降低并发数至 {self.max_workers}（成功率：{success_rate:.1%}）")
        elif success_rate > 0.95 and self.max_workers < 10:
            # 成功率高，可以尝试提高并发数
            self.max_workers = min(10, self.max_workers + 1)
            logger.info(f"提高并发数至 {self.max_workers}（成功率：{success_rate:.1%}）")
```

#### 3.3 内存优化

**问题**：大文本处理时可能占用大量内存

**建议**：

```python
# utils/text_chunker.py (改进)
class TextChunker:
    def chunk_text_generator(self, text: str):
        """生成器版本，节省内存"""
        if not text or len(text) <= self.chunk_size:
            yield (text, 0, len(text))
            return

        start = 0
        text_len = len(text)

        while start < text_len:
            ideal_end = min(start + self.chunk_size, text_len)

            if ideal_end >= text_len:
                yield (text[start:text_len], start, text_len)
                break

            actual_end = self._find_natural_break(text, start, ideal_end, text_len)
            yield (text[start:actual_end], start, actual_end)

            if actual_end < text_len:
                start = actual_end - self.overlap
            else:
                break
```

**预期收益**：
- ✅ 减少重复 API 调用，节省成本
- ✅ 提高响应速度
- ✅ 更好的资源利用
- ✅ 处理大文本时更稳定

---

### 4. 🔒 **安全性改进 - 中优先级**

#### 4.1 API Key 安全

**现状**：
- ✅ 打包时自动清除 API keys（很好！）
- ⚠️ 但运行时 API key 存储在明文配置文件中

**建议**：

```python
# utils/secure_config.py
import base64
import os
from cryptography.fernet import Fernet

class SecureConfig:
    """安全配置管理"""

    def __init__(self):
        # 使用机器特定的密钥
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)

    def _get_or_create_key(self):
        """获取或创建加密密钥"""
        key_file = os.path.join(os.path.dirname(__file__), '..', '.key')

        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_api_key(self, api_key: str) -> str:
        """加密 API key"""
        if not api_key:
            return ""
        encrypted = self.cipher.encrypt(api_key.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """解密 API key"""
        if not encrypted_key:
            return ""
        try:
            encrypted = base64.b64decode(encrypted_key.encode())
            return self.cipher.decrypt(encrypted).decode()
        except Exception:
            return ""  # 解密失败返回空字符串
```

#### 4.2 输入验证

**问题**：缺少对用户输入的验证

**建议**：

```python
# utils/validators.py
import re

class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_text_length(text: str, min_len=10, max_len=50000):
        """验证文本长度"""
        if not text or not text.strip():
            raise ValueError("文本不能为空")

        text_len = len(text.strip())
        if text_len < min_len:
            raise ValueError(f"文本太短（至少需要 {min_len} 个字符）")
        if text_len > max_len:
            raise ValueError(f"文本太长（最多 {max_len} 个字符）")

        return True

    @staticmethod
    def validate_num_questions(num: int, min_num=1, max_num=50):
        """验证题目数量"""
        if not isinstance(num, int):
            raise ValueError("题目数量必须是整数")
        if num < min_num or num > max_num:
            raise ValueError(f"题目数量必须在 {min_num}-{max_num} 之间")
        return True

    @staticmethod
    def sanitize_deck_name(name: str):
        """清理牌组名称"""
        # 移除不安全字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        return sanitized.strip()
```

**预期收益**：
- ✅ 保护用户 API key
- ✅ 防止无效输入导致的错误
- ✅ 提高插件安全性

---

### 5. 📚 **代码质量改进 - 中优先级**

#### 5.1 类型注解

**现状**：部分代码有类型注解，但不完整

**建议**：添加完整的类型注解

```python
# utils/ai_handler.py (改进示例)
from typing import Dict, List, Optional, Tuple, Any

class AIHandler:
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or mw.addonManager.getConfig(__name__)
        # ...

    def generate_choice_questions(
        self,
        text: str,
        num_questions: int,
        template_name: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        生成选择题

        Args:
            text: 学习材料文本
            num_questions: 题目数量
            template_name: 模板名称
            custom_prompt: 自定义提示词

        Returns:
            包含题目列表的字典

        Raises:
            APIError: API 调用失败
            JSONParseError: JSON 解析失败
        """
        # ...
```

#### 5.2 代码复杂度降低

**问题**：`utils/ai_handler.py` 文件过大（1331 行），职责过多

**建议**：拆分为多个文件

```
utils/
├── ai/
│   ├── __init__.py
│   ├── base_handler.py          # 基础 AI 处理器
│   ├── openai_handler.py        # OpenAI 专用
│   ├── custom_api_handler.py    # 自定义 API
│   ├── question_generator.py    # 题目生成
│   ├── card_generator.py        # 卡片生成
│   └── evaluator.py             # 评估功能
```

#### 5.3 配置管理改进

**问题**：配置散落在多处

**建议**：统一配置管理

```python
# config/config_manager.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class AIServiceConfig:
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2000
    temperature: float = 0.7
    request_timeout: int = 180

@dataclass
class AdvancedSettings:
    enable_concurrent_processing: bool = False
    max_concurrent_requests: int = 3
    enable_text_chunking: bool = False
    chunk_size: int = 2000
    chunk_overlap: int = 200
    chunk_strategy: str = "smart"

@dataclass
class PluginConfig:
    ai_service: AIServiceConfig = field(default_factory=AIServiceConfig)
    advanced_settings: AdvancedSettings = field(default_factory=AdvancedSettings)

    @classmethod
    def from_dict(cls, data: Dict) -> 'PluginConfig':
        """从字典创建配置"""
        # ...

    def to_dict(self) -> Dict:
        """转换为字典"""
        # ...
```

**预期收益**：
- ✅ 更好的 IDE 支持（自动补全、类型检查）
- ✅ 更易维护的代码
- ✅ 更清晰的代码结构

---

### 6. 📖 **文档改进 - 低优先级**

**现状**：
- ✅ 有打包文档（很好！）
- ✅ 有功能说明文档
- ⚠️ 缺少开发者文档
- ⚠️ 缺少 API 文档

**建议**：

#### 6.1 添加开发者文档

```markdown
# docs/DEVELOPMENT.md

## 开发环境设置

### 1. 克隆仓库
\`\`\`bash
git clone <repo-url>
cd anki_feynman
\`\`\`

### 2. 安装开发依赖
\`\`\`bash
pip install -r requirements-dev.txt
\`\`\`

### 3. 运行测试
\`\`\`bash
pytest tests/
\`\`\`

## 代码结构

- `gui/` - UI 组件
- `utils/` - 工具函数
- `prompts/` - AI 提示词
- `config/` - 配置管理

## 贡献指南

1. 创建功能分支
2. 编写测试
3. 确保测试通过
4. 提交 PR
```

#### 6.2 添加 API 文档

使用 Sphinx 或 MkDocs 生成 API 文档

**预期收益**：
- ✅ 降低新开发者上手难度
- ✅ 便于团队协作
- ✅ 提高代码可维护性

---

## 📊 优化优先级总结

| 优先级 | 优化项 | 预计工作量 | 预期收益 |
|--------|--------|-----------|---------|
| 🔴 高 | 1. 测试覆盖率 | 3-5 天 | 代码质量↑↑↑ |
| 🔴 高 | 2. 错误处理和日志 | 2-3 天 | 可维护性↑↑ |
| 🟡 中 | 3. 性能优化（缓存） | 1-2 天 | 用户体验↑↑ |
| 🟡 中 | 4. 安全性改进 | 1-2 天 | 安全性↑↑ |
| 🟡 中 | 5. 代码质量 | 3-4 天 | 可维护性↑ |
| 🟢 低 | 6. 文档改进 | 1-2 天 | 协作效率↑ |

---

## 🎯 建议实施路线图

### 第一阶段（1-2 周）
1. ✅ 设置测试基础设施
2. ✅ 为核心模块编写测试（response_handler, text_chunker）
3. ✅ 实现自定义异常类
4. ✅ 添加结构化日志

### 第二阶段（1-2 周）
5. ✅ 实现缓存机制
6. ✅ 改进错误处理
7. ✅ 添加输入验证

### 第三阶段（1-2 周）
8. ✅ 重构大文件（ai_handler.py）
9. ✅ 添加完整类型注解
10. ✅ 编写开发者文档

---

## 💡 额外建议

### 1. 依赖管理
- 考虑使用 `poetry` 或 `pipenv` 替代 `requirements.txt`
- 定期更新依赖，特别是安全补丁

### 2. CI/CD
- 设置 GitHub Actions 自动运行测试
- 自动化打包流程

### 3. 用户反馈
- 添加错误报告功能
- 收集使用统计（匿名）以改进功能

### 4. 国际化
- 当前已有多语言支持，继续完善
- 考虑添加更多语言

---

## 📝 总结

这个插件已经有很好的基础：
- ✅ 功能丰富
- ✅ 已完成提示词优化
- ✅ 已实现并发处理
- ✅ 有完善的打包流程

主要改进方向：
1. **测试** - 最重要，确保代码质量
2. **错误处理** - 提高用户体验和可维护性
3. **性能** - 通过缓存进一步优化
4. **安全** - 保护用户数据

建议优先实施高优先级项目，它们能带来最大的收益。

---

**报告生成时间**: 2025-11-17
**分析工具**: Augment Agent

