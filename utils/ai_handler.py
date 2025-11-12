import json
import requests
import time
try:
    import openai
except ImportError:
    # 如果直接导入失败，尝试从vendor目录导入
    import sys
    import os
    vendor_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vendor")
    if vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)
    import openai

from aqt import mw
from ..prompts.knowledge_card_prompts import get_prompt_config, format_prompt
from ..prompts.choice_prompts import get_choice_prompt
from ..prompts.essay_prompts import get_essay_prompt
from ..prompts.evaluation_prompts import get_essay_evaluation_prompt, get_choice_evaluation_messages
from ..prompts.followup_prompts import get_followup_messages
from ..prompts.language_prompts import format_language_pattern_messages  # 导入语言模式练习提示
from ..prompts.system_prompts import (
    get_choice_questions_prompt,
    get_knowledge_cards_prompt,
    get_cloze_conversion_prompt,
    get_essay_eval_system_prompt
)
from .response_handler import ResponseHandler
from .text_chunker import TextChunker
from .concurrent_processor import ConcurrentProcessor

class AIHandler:
    def __init__(self, config=None):
        self.config = config or mw.addonManager.getConfig(__name__)
        self.ai_config = self.config.get('ai_service', {})
        self.provider = self.ai_config.get('provider', 'openai')
        self.response_handler = ResponseHandler()
        
        # 当前选择的模型信息
        self.current_model_info = None
        
        # 加载额外设置
        advanced_config = self.config.get('advanced_settings', {})
        self.enable_concurrent = advanced_config.get('enable_concurrent_processing', False)
        self.max_concurrent = advanced_config.get('max_concurrent_requests', 3)
        self.enable_chunking = advanced_config.get('enable_text_chunking', False)
        
        # 保存默认设置（作为备份）
        self.default_max_concurrent = self.max_concurrent
        self.default_chunk_size = advanced_config.get('chunk_size', 2000)
        self.default_chunk_overlap = advanced_config.get('chunk_overlap', 200)
        self.default_chunk_strategy = advanced_config.get('chunk_strategy', 'smart')
        
        # 保存模型特定设置配置
        self.model_specific_settings = advanced_config.get('model_specific_settings', {})
        
        # 初始化文本分块器
        self.text_chunker = TextChunker(
            chunk_size=self.default_chunk_size,
            overlap=self.default_chunk_overlap,
            strategy=self.default_chunk_strategy
        )
        
        # 初始化并发处理器
        self.concurrent_processor = ConcurrentProcessor(max_workers=self.max_concurrent)
        
        # 进度回调（可由外部设置）
        self.progress_callback = None
        
        if self.provider == 'openai':
            self._setup_openai()
        else:
            self._setup_custom()

    def _setup_openai(self):
        """设置OpenAI客户端"""
        openai_config = self.ai_config.get('openai', {})
        api_key = openai_config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API Key未设置")
            
        # 设置OpenAI API密钥
        openai.api_key = api_key
        
        # 保存其他配置
        self.model = openai_config.get('model', 'gpt-3.5-turbo')
        self.max_tokens = openai_config.get('max_tokens', 2000)
        self.temperature = openai_config.get('temperature', 0.7)
        self.request_timeout = openai_config.get('request_timeout', 180)

    def _setup_custom(self):
        """设置自定义AI服务"""
        custom_config = self.ai_config.get('custom', {})
        self.api_url = custom_config.get('api_url')
        self.api_key = custom_config.get('api_key')
        self.model = custom_config.get('model')
        self.max_tokens = custom_config.get('max_tokens', 2000)
        self.temperature = custom_config.get('temperature', 0.7)
        self.request_timeout = custom_config.get('request_timeout', 180)

    def _call_ai_api(self, messages):
        """调用AI API"""
        try:
            if self.provider == 'openai':
                return self._call_openai(messages)
            else:
                return self._call_custom_api(messages)
        except Exception as e:
            # 添加更详细的错误信息
            error_msg = f"API调用失败：{str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\n响应状态码：{e.response.status_code}"
                error_msg += f"\n响应内容：{e.response.text}"
            raise Exception(error_msg)

    def _call_openai(self, messages):
        """调用OpenAI API"""
        if not openai.api_key:
            raise ValueError("OpenAI API Key未设置，请在设置中配置API密钥")
            
        try:
            try:
                # 尝试使用新版API
                client = openai.OpenAI(
                    api_key=openai.api_key,
                    timeout=self.request_timeout
                )
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content
            except (AttributeError, ImportError):
                # 如果新版API不可用，使用旧版API
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    request_timeout=self.request_timeout
                )
                return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"OpenAI API错误：{error_msg}\n状态码：{e.response.status_code}"
            raise Exception(error_msg)

    def _call_custom_api(self, messages):
        """调用自定义AI API"""
        # 确定API URL和API Key
        api_url = self.api_url
        api_key = self.api_key
        
        # 如果设置了当前模型并且模型有自定义API设置，则使用模型的API设置
        if self.current_model_info and 'api_url' in self.current_model_info and 'api_key' in self.current_model_info:
            api_url = self.current_model_info['api_url']
            api_key = self.current_model_info['api_key']
        
        if not api_url or not api_key:
            raise ValueError("自定义API的URL或密钥未设置")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 确定要使用的模型名称
        model_name = self.model
        if self.current_model_info:
            model_name = self.current_model_info.get('name', self.model)
        
        data = {
            "messages": messages,
            "model": model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # 针对不同模型调整请求格式和参数
        is_claude_model = "claude" in model_name.lower()
        if is_claude_model:
            # 为Claude模型调整请求，可能需要减小max_tokens和添加超时重试机制
            data["max_tokens"] = min(self.max_tokens, 4000)  # Claude对长请求可能更敏感
        
        # 添加重试机制，特别是针对连接重置错误
        max_retries = 3
        retry_count = 0
        retry_delay = 2  # 初始重试延迟（秒）
        
        while retry_count < max_retries:
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=self.request_timeout
                )
                response.raise_for_status()  # 检查HTTP错误
                result = response.json()
                
                if not isinstance(result, dict) or 'choices' not in result:
                    raise ValueError(f"API返回格式错误：{response.text}")
                    
                return result['choices'][0]['message']['content']
                
            except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
                # 特别处理连接错误和连接重置错误
                retry_count += 1
                if retry_count >= max_retries:
                    error_msg = f"API连接错误（已重试{max_retries}次）：{str(e)}"
                    if is_claude_model:
                        error_msg += "\n使用Claude模型时可能需要更长的超时时间或减小max_tokens值"
                    raise Exception(error_msg)
                
                print(f"连接错误，正在进行第{retry_count}次重试，等待{retry_delay}秒...")
                time.sleep(retry_delay)
                retry_delay *= 2  # 指数退避，增加重试间隔
                continue
                
            except requests.exceptions.RequestException as e:
                error_msg = f"API请求失败：{str(e)}"
                if hasattr(e, 'response') and e.response is not None:
                    error_msg += f"\n状态码：{e.response.status_code}"
                    error_msg += f"\n响应内容：{e.response.text}"
                raise Exception(error_msg)
                
            except (KeyError, IndexError, ValueError) as e:
                raise Exception(f"API响应解析失败：{str(e)}")

    def _should_chunk_text(self, content: str) -> bool:
        """
        判断文本是否需要分块
        
        Args:
            content: 文本内容
            
        Returns:
            是否需要分块
        """
        if not self.enable_chunking:
            return False
        return self.text_chunker.should_chunk(content)
    
    def _distribute_questions_across_chunks(self, num_chunks: int, total_questions: int) -> list:
        """
        将问题数量分配到各个分块
        
        Args:
            num_chunks: 分块数量
            total_questions: 总问题数
            
        Returns:
            每个分块应生成的问题数列表
        """
        if num_chunks <= 0:
            return []
        
        # 基础分配
        base_per_chunk = total_questions // num_chunks
        remainder = total_questions % num_chunks
        
        # 分配问题数（前面的分块多分配余数）
        distribution = []
        for i in range(num_chunks):
            if i < remainder:
                distribution.append(base_per_chunk + 1)
            else:
                distribution.append(base_per_chunk)
        
        return distribution
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """
        报告进度
        
        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        if self.progress_callback:
            try:
                self.progress_callback(current, total, message)
            except Exception as e:
                print(f"Progress callback error: {e}")

    def generate_questions(self, content, question_type, num_questions=3, language="中文"):
        """生成问题
        
        Args:
            content: 学习内容
            question_type: 问题类型
            num_questions: 问题数量
            language: 生成内容使用的语言
        """
        if question_type == "multiple_choice":
            return self._generate_choice_questions(content, num_questions, language)
        elif question_type == "knowledge_card":
            return self._generate_knowledge_cards(content, num_questions, language)
        elif question_type == "language_learning":
            return self._generate_language_learning_cards(content, num_questions, language)
        elif question_type == "custom":
            return self._generate_custom_questions(content, num_questions, language)
        else:
            return self._generate_essay_questions(content, num_questions, language)

    def _generate_choice_questions(self, content, num_questions, language="中文"):
        """生成选择题"""
        # 检查是否需要分块处理
        if self._should_chunk_text(content):
            print(f"文本长度 {len(content)}，启用分块处理")
            return self._generate_choice_questions_with_chunking(content, num_questions, language)
        
        # 原有的单次生成逻辑
        return self._generate_choice_questions_single(content, num_questions, language)
    
    def _generate_choice_questions_single(self, content, num_questions, language="中文"):
        """生成选择题（单次请求）"""
        prompt = get_choice_prompt(content, num_questions, language)
        max_retries = 3
        current_retry = 0
        
        # 检查当前使用的模型是否为Claude
        model_name = self.model
        if self.current_model_info:
            model_name = self.current_model_info.get('name', self.model)
        is_claude_model = "claude" in model_name.lower()
        
        # 如果题目数量较多，增加系统提示的强调
        system_prompt = get_choice_questions_prompt()
        
        # 为Claude模型添加更严格的格式要求
        if is_claude_model:
            system_prompt += """

请注意，你正在使用Claude模型。必须特别注意以下几点：
1. 响应必须是严格的JSON格式，不得包含任何前导或尾随文本
2. 不要使用Markdown代码块，直接返回JSON
3. 所有字符串必须使用双引号
4. 每个属性后必须有逗号，除了最后一个属性
5. 确保生成的JSON可以被标准JSON解析器直接解析
6. 生成的JSON结构必须完全符合以下格式：

{
    "questions": [
        {
            "question": "问题内容",
            "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
            "correct_answer": "A/B/C/D其中之一",
            "explanation": "解释",
            "source_content": "相关段落"
        }
    ]
}"""
        elif num_questions > 5:
            system_prompt += "\n\n特别注意：你正在生成较多数量的题目，请特别注意JSON格式的正确性，确保每个问题对象之间有逗号分隔，所有属性名和字符串值都用双引号包围，每个属性后面都有逗号（除了最后一个）。"
        
        while current_retry < max_retries:
            try:
                # 打印当前重试次数，便于调试
                print(f"正在生成选择题，第{current_retry + 1}次尝试...")
                
                response = self._call_ai_api([{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": prompt
                }])
                
                # 输出原始响应前50个字符，便于调试
                print(f"获得原始响应（前50个字符）：{response[:50]}...")
                
                try:
                    result = self.response_handler.parse_and_validate(response, "choice_question")
                    
                    # 验证问题数量
                    if len(result["questions"]) < num_questions:
                        print(f"警告：请求生成{num_questions}个问题，但只生成了{len(result['questions'])}个")
                    
                    return result
                except ValueError as e:
                    # 如果是JSON解析错误，记录详细信息并重试
                    error_msg = str(e)
                    print(f"JSON解析错误：{error_msg}")
                    
                    # 对于Claude模型，尝试更激进的清理和修复
                    if is_claude_model:
                        try:
                            # 记录原始响应到日志（前200个字符）
                            print(f"Claude响应片段: {response[:200]}...")
                            
                            # 尝试找到JSON的开始位置（可能有前导文本）
                            json_start = response.find('{')
                            if json_start >= 0:
                                # 尝试清理并解析JSON部分
                                cleaned_json = response[json_start:]
                                
                                # 尝试找到JSON的结束位置（可能有尾随文本）
                                brace_count = 0
                                for i, char in enumerate(cleaned_json):
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            cleaned_json = cleaned_json[:i+1]
                                            break
                                
                                # 应用深度修复
                                cleaned_response = self.response_handler.clean_response(cleaned_json)
                                fixed_json = self.response_handler.deep_json_fix(cleaned_response)
                                result = json.loads(fixed_json)
                                
                                # 验证数据结构
                                if not isinstance(result, dict) or "questions" not in result:
                                    raise ValueError("返回的JSON格式不正确：缺少questions字段")
                                
                                # 验证每个问题的格式
                                for q in result["questions"]:
                                    if not all(key in q for key in ["question", "options", "correct_answer", "explanation", "source_content"]):
                                        raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
                                    if not isinstance(q["options"], list) or len(q["options"]) != 4:
                                        raise ValueError("返回的JSON格式不正确：选项数量不正确")
                                    if q["correct_answer"] not in ["A", "B", "C", "D"]:
                                        raise ValueError("返回的JSON格式不正确：正确答案必须是A、B、C、D之一")
                                
                                return result
                            else:
                                raise ValueError("Claude响应中未找到有效的JSON数据")
                        except Exception as claude_error:
                            print(f"Claude模型响应修复失败：{str(claude_error)}")
                            current_retry += 1
                            continue
                    elif "JSON解析失败" in error_msg:
                        # 尝试使用深度修复
                        try:
                            cleaned_response = self.response_handler.clean_response(response)
                            fixed_json = self.response_handler.deep_json_fix(cleaned_response)
                            result = json.loads(fixed_json)
                            
                            # 验证数据结构
                            if not isinstance(result, dict) or "questions" not in result:
                                raise ValueError("返回的JSON格式不正确：缺少questions字段")
                            
                            # 验证每个问题的格式
                            for q in result["questions"]:
                                if not all(key in q for key in ["question", "options", "correct_answer", "explanation", "source_content"]):
                                    raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
                                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                                    raise ValueError("返回的JSON格式不正确：选项数量不正确")
                                if q["correct_answer"] not in ["A", "B", "C", "D"]:
                                    raise ValueError("返回的JSON格式不正确：正确答案必须是A、B、C、D之一")
                            
                            return result
                        except Exception as inner_e:
                            print(f"深度修复失败：{str(inner_e)}")
                            current_retry += 1
                            continue
                    else:
                        current_retry += 1
                        continue
                
            except Exception as e:
                print(f"API调用错误：{str(e)}")
                current_retry += 1
                if current_retry >= max_retries:
                    raise Exception(f"生成选择题失败：{str(e)}")
                continue
        
        # 如果尝试次数用完，保存最后一次响应内容到临时文件以便调试
        try:
            with open("last_claude_response.txt", "w", encoding="utf-8") as f:
                f.write(f"模型: {model_name}\n\n")
                f.write(f"系统提示:\n{system_prompt}\n\n")
                f.write(f"用户提示:\n{prompt}\n\n")
                f.write(f"响应:\n{response}")
            print("已将最后一次响应保存到last_claude_response.txt")
        except:
            pass
            
        raise Exception("生成选择题失败：超过最大重试次数")

    def _generate_essay_questions(self, content, num_questions, language="中文"):
        """生成问答题"""
        # 检查是否需要分块处理
        if self._should_chunk_text(content):
            print(f"文本长度 {len(content)}，启用分块处理")
            return self._generate_essay_questions_with_chunking(content, num_questions, language)
        
        # 原有的单次生成逻辑
        return self._generate_essay_questions_single(content, num_questions, language)
    
    def _generate_essay_questions_single(self, content, num_questions, language="中文"):
        """生成问答题（单次请求）"""
        prompt = get_essay_prompt(content, num_questions, language)
        max_retries = 3
        current_retry = 0
        
        # 如果题目数量较多，增加系统提示的强调
        system_prompt = "你是一个教育助手，专门生成符合费曼学习法的问答题。你的回答必须是纯JSON格式，不要添加任何代码块标记。确保JSON格式正确，特别是逗号、引号等标点符号的使用。"
        if num_questions > 5:
            system_prompt += "\n\n特别注意：你正在生成较多数量的题目，请特别注意JSON格式的正确性，确保每个问题对象之间有逗号分隔，所有属性名和字符串值都用双引号包围，每个属性后面都有逗号（除了最后一个）。"
        
        while current_retry < max_retries:
            try:
                response = self._call_ai_api([{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": prompt
                }])
                
                # 记录原始响应（可以在调试时使用）
                # print(f"原始响应：{response}")
                
                # 使用ResponseHandler处理和验证JSON
                try:
                    result = self.response_handler.parse_and_validate(response, "essay_question")
                    
                    # 验证问题数量
                    if len(result["questions"]) < num_questions:
                        print(f"警告：请求生成{num_questions}个问题，但只生成了{len(result['questions'])}个")
                    
                    return result
                except ValueError as e:
                    # 如果是JSON解析错误，尝试手动解析和修复
                    error_msg = str(e)
                    print(f"JSON解析错误：{error_msg}")
                    
                    if "JSON解析失败" in error_msg:
                        # 尝试使用深度修复
                        try:
                            cleaned_response = self.response_handler.clean_response(response)
                            fixed_json = self.response_handler.deep_json_fix(cleaned_response)
                            result = json.loads(fixed_json)
                            
                            # 验证数据结构
                            if not isinstance(result, dict) or "questions" not in result:
                                raise ValueError("返回的JSON格式不正确：缺少questions字段")
                            
                            for q in result["questions"]:
                                if not all(key in q for key in ["question", "reference_answer", "key_points", "source_content"]):
                                    raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
                                if not isinstance(q["key_points"], list) or len(q["key_points"]) < 3:
                                    raise ValueError("返回的JSON格式不正确：关键点数量不足")
                            
                            return result
                        except Exception as inner_e:
                            print(f"深度修复失败：{str(inner_e)}")
                            current_retry += 1
                            continue
                    else:
                        # 如果是其他验证错误，继续重试
                        current_retry += 1
                        continue
                        
            except Exception as e:
                print(f"API调用错误：{str(e)}")
                current_retry += 1
                if current_retry >= max_retries:
                    raise Exception(f"生成问答题时出错：{str(e)}")
                continue
        
        raise Exception("生成问答题失败：超过最大重试次数")

    def _generate_knowledge_cards(self, content, num_cards=3, language="中文"):
        """生成知识卡片"""
        # 检查是否需要分块处理
        if self._should_chunk_text(content):
            print(f"文本长度 {len(content)}，启用分块处理")
            return self._generate_knowledge_cards_with_chunking(content, num_cards, language)
        
        # 原有的单次生成逻辑
        return self._generate_knowledge_cards_single(content, num_cards, language)
    
    def _generate_knowledge_cards_single(self, content, num_cards=3, language="中文"):
        """生成知识卡片（单次请求）"""
        prompt = format_prompt("basic", content, num_cards, language)
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                response = self._call_ai_api([{
                    "role": "system",
                    "content": get_knowledge_cards_prompt()
                }, {
                    "role": "user",
                    "content": prompt
                }])
                
                return self.response_handler.parse_and_validate(response, "knowledge_card")
                
            except Exception as e:
                current_retry += 1
                if current_retry >= max_retries:
                    raise e
                continue
        
        raise Exception("生成知识卡失败：超过最大重试次数")

    def _generate_language_learning_cards(self, content, num_cards=5, language="中文"):
        """生成语言学习知识卡片
        
        Args:
            content: 学习记录文本（包含原句、纠正、建议等）
            num_cards: 要生成的卡片数量
            language: 生成内容使用的语言
        
        Returns:
            包含cards数组的字典
        """
        # 检查是否需要分块处理
        if self._should_chunk_text(content):
            print(f"文本长度 {len(content)}，启用分块处理")
            return self._generate_language_learning_cards_with_chunking(content, num_cards, language)
        
        # 原有的单次生成逻辑
        return self._generate_language_learning_cards_single(content, num_cards, language)
    
    def _generate_language_learning_cards_single(self, content, num_cards=5, language="中文"):
        """生成语言学习知识卡片（单次请求）
        
        Args:
            content: 学习记录文本
            num_cards: 要生成的卡片数量
            language: 生成内容使用的语言
        
        Returns:
            包含cards数组的字典
        """
        from ..prompts.system_prompts import get_language_learning_cards_prompt
        
        prompt = format_prompt("language_learning", content, num_cards, language)
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                response = self._call_ai_api([{
                    "role": "system",
                    "content": get_language_learning_cards_prompt()
                }, {
                    "role": "user",
                    "content": prompt
                }])
                
                # 使用knowledge_card schema验证，因为格式相同
                return self.response_handler.parse_and_validate(response, "knowledge_card")
                
            except Exception as e:
                current_retry += 1
                if current_retry >= max_retries:
                    raise e
                continue
        
        raise Exception("生成语言学习知识卡失败：超过最大重试次数")

    def convert_to_cloze(self, card_data):
        """将知识卡转换为填空卡"""
        prompt = format_prompt("cloze", json.dumps(card_data, ensure_ascii=False))
        
        try:
            response = self._call_ai_api([{
                "role": "system",
                "content": get_cloze_conversion_prompt()
            }, {
                "role": "user",
                "content": prompt
            }])
            
            return self.response_handler.parse_and_validate(response, "cloze_card")
            
        except Exception as e:
            raise Exception(f"转换为填空卡失败：{str(e)}")

    def evaluate_answer(self, question_data, user_answer, language="中文"):
        """评估用户答案
        
        Args:
            question_data: 问题数据
            user_answer: 用户答案
            language: 评估使用的语言
        """
        if "options" in question_data:  # 选择题
            return self._evaluate_choice_answer(question_data, user_answer)
        else:  # 问答题
            return self._evaluate_essay_answer(question_data, user_answer, language)

    def _evaluate_choice_answer(self, question_data, user_answer):
        """评估选择题答案"""
        # 从用户答案中提取选项字母
        user_choice = user_answer.split('.')[0].strip().upper() if '.' in user_answer else user_answer.strip().upper()
        correct_choice = question_data["correct_answer"].upper()
        
        is_correct = user_choice == correct_choice
        
        if is_correct:
            feedback = f"✓ 回答正确！\n\n{question_data['explanation']}"
        else:
            # 找到正确答案的完整选项文本
            correct_option = next(opt for opt in question_data['options'] 
                                if opt.startswith(f"{correct_choice}."))
            feedback = f"✗ 回答错误。\n\n正确答案是：{correct_option}\n\n{question_data['explanation']}"
        
        return {
            "is_correct": is_correct,
            "feedback": feedback
        }

    def _evaluate_essay_answer(self, question_data, user_answer, language="中文"):
        """评估问答题答案"""
        prompt = get_essay_evaluation_prompt(
            question=question_data['question'],
            reference_answer=question_data['reference_answer'],
            key_points=question_data['key_points'],
            user_answer=user_answer,
            language=language
        )

        try:
            response = self._call_ai_api([{
                "role": "system",
                "content": get_essay_eval_system_prompt()
            }, {
                "role": "user",
                "content": prompt
            }])
            
            return self.response_handler.parse_and_validate(response, "essay_evaluation")
                
        except Exception as e:
            raise Exception(f"评估答案时出错：{str(e)}")

    def handle_follow_up_question(self, context, language="中文"):
        """处理追问
        
        Args:
            context: 上下文信息
            language: 回答使用的语言
        """
        messages = get_followup_messages(context, language)
        response = self._call_ai_api(messages)
        return response

    def generate_language_pattern(self, sentence, target_language, specified_parts=None, language_level=None, examples_count=3):
        """生成语言模式练习内容
        
        Args:
            sentence: 用户输入的句子
            target_language: 目标语言
            specified_parts: 用户指定的要替换的部分（可选）
            language_level: 语言级别（可选，例如"N3"、"B2"等）
            examples_count: 每个替换部分生成的例句数量（可选，默认为3）
        """
        messages = format_language_pattern_messages(sentence, target_language, specified_parts, language_level, examples_count)
        raw_response = self._call_ai_api(messages)
        
        try:
            # 尝试解析JSON响应
            response_text = raw_response.strip()
            if isinstance(response_text, str):
                # 找到JSON的开始和结束位置
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    pattern_data = json.loads(json_str)
                    
                    # 确保结果包含所需的字段
                    if not all(key in pattern_data for key in ['analysis', 'replaceable_parts', 'examples']):
                        raise ValueError("AI响应中缺少必需的字段")
                    
                    return pattern_data
                else:
                    # 如果未找到JSON，尝试使用文本格式
                    return self._parse_language_text_response(response_text)
            else:
                # 如果响应已经是字典形式
                return raw_response
        except Exception as e:
            raise ValueError(f"无法解析语言模式生成的响应: {str(e)}\n原始响应: {raw_response}")

    def _parse_language_text_response(self, text):
        """尝试从文本响应中解析语言模式练习内容"""
        result = {
            "analysis": "",
            "replaceable_parts": "",
            "examples": []
        }
        
        # 简单的分段解析
        sections = text.split("\n\n")
        current_section = None
        
        for section in sections:
            if "句型分析" in section:
                current_section = "analysis"
                result["analysis"] = section.replace("句型分析：", "").strip()
            elif "可替换部分" in section:
                current_section = "replaceable_parts"
                result["replaceable_parts"] = section.replace("可替换部分：", "").strip()
            elif "替换示例" in section or "例句" in section:
                current_section = "examples"
                # 解析例句
                examples = []
                example_blocks = section.split("\n-")
                
                for block in example_blocks[1:]:  # 跳过标题行
                    lines = block.strip().split("\n")
                    if len(lines) >= 2:
                        # 尝试识别替换部分信息
                        replaced_part = ""
                        for line in lines:
                            if "替换部分" in line or "替换了" in line:
                                replaced_part = line.replace("替换部分：", "").replace("替换了", "").strip()
                                break
                        
                        example = {
                            "sentence": lines[0].strip(),
                            "translation": lines[1].strip().replace("（", "").replace("）", ""),
                            "grammar_note": "",
                            "replaced_part": replaced_part
                        }
                        examples.append(example)
                
                result["examples"] = examples
        
        # 如果没有正确解析到例句，提供一个默认的说明
        if not result["examples"]:
            result["examples"] = [{
                "sentence": "未能正确解析例句，请重试",
                "translation": "解析失败",
                "grammar_note": "请重新生成练习",
                "replaced_part": ""
            }]
        
        return result

    def _format_history(self, history):
        """格式化对话历史"""
        formatted_history = []
        if not history:
            return "无历史对话"
            
        for item in history:
            formatted_history.append(f"问：{item['question']}")
            formatted_history.append(f"答：{item['answer']}")
            formatted_history.append("")
        
        return "\n".join(formatted_history).strip()

    def set_model(self, model_name):
        """设置当前使用的模型"""
        # 查找模型配置
        models = self.config.get('models', [])
        found_model = None
        
        for model in models:
            if model.get('name') == model_name:
                found_model = model
                break
                
        if found_model:
            self.current_model_info = found_model
            # 应用模型特定设置（如果有）
            self._apply_model_specific_settings(model_name)
            return True
        else:
            # 如果找不到模型，重置为默认设置
            self.current_model_info = None
            self._reset_to_default_settings()
            return False
    
    def _apply_model_specific_settings(self, model_name):
        """应用模型特定设置（如果存在）"""
        if model_name in self.model_specific_settings:
            settings = self.model_specific_settings[model_name]
            
            # 应用并发设置
            if 'max_concurrent_requests' in settings:
                self.max_concurrent = settings['max_concurrent_requests']
                self.concurrent_processor.set_max_workers(self.max_concurrent)
                print(f"为模型 {model_name} 应用特定并发设置: {self.max_concurrent}")
            
            # 应用分块设置
            if 'chunk_size' in settings:
                chunk_size = settings['chunk_size']
                self.text_chunker.chunk_size = chunk_size
                print(f"为模型 {model_name} 应用特定分块大小: {chunk_size}")
        else:
            # 没有特定设置，使用默认值
            self._reset_to_default_settings()
    
    def _reset_to_default_settings(self):
        """重置为默认设置"""
        self.max_concurrent = self.default_max_concurrent
        self.concurrent_processor.set_max_workers(self.max_concurrent)
        self.text_chunker.chunk_size = self.default_chunk_size

    def _generate_custom_questions(self, content, template_id, num_questions, language="中文"):
        """使用自定义模板生成选择题"""
        # 从配置中获取模板
        config = mw.addonManager.getConfig(__name__)
        templates = config.get('prompt_templates', [])
        template = next((t for t in templates if t.get('id', '') == template_id), None)
        
        if not template:
            raise ValueError("找不到指定的提示词模板")
            
        # 构建提示词，只替换content变量
        prompt = template['content'].format(
            content=content
        )
        
        # 在提示词末尾添加问题数量要求
        prompt += f"\n\n请生成{num_questions}道选择题。"
        
        # 添加系统提示，确保返回正确的JSON格式
        system_prompt = """你是一个基于费曼学习法的高级教学助手。请根据用户提供的提示词生成选择题。
请严格按照以下JSON格式返回，确保格式完整：

{
    "questions": [
        {
            "question": "问题内容",
            "options": [
                "A. 选项1",
                "B. 选项2",
                "C. 选项3",
                "D. 选项4"
            ],
            "correct_answer": "A/B/C/D其中之一",
            "explanation": "解释为什么这是正确答案",
            "source_content": "与该问题直接相关的原文段落"
        }
    ]
}

JSON格式要求：
1. 不要添加任何代码块标记（如```json）
2. 选项必须包含A、B、C、D前缀
3. source_content必须是原文中与问题直接相关的段落
4. 特别注意JSON格式中的逗号、引号等标点符号的正确使用
5. 确保每个JSON对象和数组的开始和结束都有正确的括号
6. 每个属性后面都必须有逗号，除了最后一个属性
7. 所有字符串必须用双引号包围，不能用单引号
8. 当生成多个问题时，每个问题对象之间必须用逗号分隔
9. 检查生成的JSON是否完整，特别是在生成大量题目时
10. 确保每个问题对象的所有字段都正确闭合"""
        
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                response = self._call_ai_api([{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": prompt
                }])
                
                try:
                    result = self.response_handler.parse_and_validate(response, "choice_question")
                    
                    # 验证问题数量
                    if len(result["questions"]) < num_questions:
                        print(f"警告：请求生成{num_questions}个问题，但只生成了{len(result['questions'])}个")
                    
                    return result
                except ValueError as e:
                    # 如果是JSON解析错误，记录详细信息并重试
                    error_msg = str(e)
                    print(f"JSON解析错误：{error_msg}")
                    
                    if "JSON解析失败" in error_msg:
                        # 尝试使用深度修复
                        try:
                            cleaned_response = self.response_handler.clean_response(response)
                            fixed_json = self.response_handler.deep_json_fix(cleaned_response)
                            result = json.loads(fixed_json)
                            
                            # 验证数据结构
                            if not isinstance(result, dict) or "questions" not in result:
                                raise ValueError("返回的JSON格式不正确：缺少questions字段")
                            
                            # 验证每个问题的格式
                            for q in result["questions"]:
                                if not all(key in q for key in ["question", "options", "correct_answer", "explanation", "source_content"]):
                                    raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
                                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                                    raise ValueError("返回的JSON格式不正确：选项数量不正确")
                                if q["correct_answer"] not in ["A", "B", "C", "D"]:
                                    raise ValueError("返回的JSON格式不正确：正确答案必须是A、B、C、D之一")
                            
                            return result
                        except Exception as inner_e:
                            print(f"深度修复失败：{str(inner_e)}")
                            current_retry += 1
                            continue
                    else:
                        current_retry += 1
                        continue
                
            except Exception as e:
                print(f"API调用错误：{str(e)}")
                current_retry += 1
                continue
                
        raise Exception("生成问题失败，请检查提示词模板是否正确")

    def generate_custom_questions(self, content, template_id, num_questions=3, language="中文"):
        """生成自定义问题的公共方法"""
        return self._generate_custom_questions(content, template_id, num_questions, language)
    
    def _generate_choice_questions_with_chunking(self, content, num_questions, language="中文"):
        """
        使用分块处理生成选择题
        
        Args:
            content: 文本内容
            num_questions: 总问题数
            language: 生成内容使用的语言
            
        Returns:
            合并后的问题结果
        """
        try:
            # 分块
            chunks = self.text_chunker.chunk_text(content)
            num_chunks = len(chunks)
            print(f"文本已分为 {num_chunks} 块")
            
            # 分配问题数
            question_distribution = self._distribute_questions_across_chunks(num_chunks, num_questions)
            
            # 准备任务列表
            tasks = []
            for i, (chunk_text, start, end) in enumerate(chunks):
                num_q = question_distribution[i]
                if num_q > 0:  # 只处理需要生成问题的分块
                    tasks.append((chunk_text, num_q))
            
            # 检查是否启用并发
            if self.enable_concurrent and len(tasks) > 1:
                print(f"使用并发处理，最大并发数: {self.max_concurrent}")
                
                # 并发处理
                def progress_callback(completed, total):
                    self._report_progress(completed, total, f"正在处理分块 {completed}/{total}")
                
                results = self.concurrent_processor.process_batch(
                    tasks,
                    lambda chunk_text, num_q: self._generate_choice_questions_single(chunk_text, num_q, language),
                    progress_callback=progress_callback
                )
            else:
                # 顺序处理
                print("顺序处理各个分块")
                results = []
                for i, (chunk_text, num_q) in enumerate(tasks):
                    print(f"处理分块 {i+1}/{len(tasks)}")
                    self._report_progress(i+1, len(tasks), f"正在处理分块 {i+1}/{len(tasks)}")
                    result = self._generate_choice_questions_single(chunk_text, num_q, language)
                    results.append(result)
            
            # 合并结果
            merged = self.text_chunker.merge_results(results, "questions")
            print(f"已合并 {len(merged.get('questions', []))} 个问题")
            
            return merged
            
        except Exception as e:
            print(f"分块处理失败: {str(e)}，回退到单次处理")
            # 回退到单次处理
            return self._generate_choice_questions_single(content, num_questions)
    
    def _generate_essay_questions_with_chunking(self, content, num_questions, language="中文"):
        """
        使用分块处理生成问答题
        
        Args:
            content: 文本内容
            num_questions: 总问题数
            language: 生成内容使用的语言
            
        Returns:
            合并后的问题结果
        """
        try:
            chunks = self.text_chunker.chunk_text(content)
            num_chunks = len(chunks)
            print(f"文本已分为 {num_chunks} 块")
            
            question_distribution = self._distribute_questions_across_chunks(num_chunks, num_questions)
            
            tasks = []
            for i, (chunk_text, start, end) in enumerate(chunks):
                num_q = question_distribution[i]
                if num_q > 0:
                    tasks.append((chunk_text, num_q))
            
            if self.enable_concurrent and len(tasks) > 1:
                print(f"使用并发处理，最大并发数: {self.max_concurrent}")
                
                def progress_callback(completed, total):
                    self._report_progress(completed, total, f"正在处理分块 {completed}/{total}")
                
                results = self.concurrent_processor.process_batch(
                    tasks,
                    lambda chunk_text, num_q: self._generate_essay_questions_single(chunk_text, num_q, language),
                    progress_callback=progress_callback
                )
            else:
                print("顺序处理各个分块")
                results = []
                for i, (chunk_text, num_q) in enumerate(tasks):
                    print(f"处理分块 {i+1}/{len(tasks)}")
                    self._report_progress(i+1, len(tasks), f"正在处理分块 {i+1}/{len(tasks)}")
                    result = self._generate_essay_questions_single(chunk_text, num_q, language)
                    results.append(result)
            
            merged = self.text_chunker.merge_results(results, "questions")
            print(f"已合并 {len(merged.get('questions', []))} 个问题")
            
            return merged
            
        except Exception as e:
            print(f"分块处理失败: {str(e)}，回退到单次处理")
            return self._generate_essay_questions_single(content, num_questions)
    
    def _generate_knowledge_cards_with_chunking(self, content, num_cards, language="中文"):
        """
        使用分块处理生成知识卡
        
        Args:
            content: 文本内容
            num_cards: 总卡片数
            language: 生成内容使用的语言
            
        Returns:
            合并后的卡片结果
        """
        try:
            chunks = self.text_chunker.chunk_text(content)
            num_chunks = len(chunks)
            print(f"文本已分为 {num_chunks} 块")
            
            card_distribution = self._distribute_questions_across_chunks(num_chunks, num_cards)
            
            tasks = []
            for i, (chunk_text, start, end) in enumerate(chunks):
                num_c = card_distribution[i]
                if num_c > 0:
                    tasks.append((chunk_text, num_c))
            
            if self.enable_concurrent and len(tasks) > 1:
                print(f"使用并发处理，最大并发数: {self.max_concurrent}")
                
                def progress_callback(completed, total):
                    self._report_progress(completed, total, f"正在处理分块 {completed}/{total}")
                
                results = self.concurrent_processor.process_batch(
                    tasks,
                    lambda chunk_text, num_c: self._generate_knowledge_cards_single(chunk_text, num_c, language),
                    progress_callback=progress_callback
                )
            else:
                print("顺序处理各个分块")
                results = []
                for i, (chunk_text, num_c) in enumerate(tasks):
                    print(f"处理分块 {i+1}/{len(tasks)}")
                    self._report_progress(i+1, len(tasks), f"正在处理分块 {i+1}/{len(tasks)}")
                    result = self._generate_knowledge_cards_single(chunk_text, num_c, language)
                    results.append(result)
            
            merged = self.text_chunker.merge_results(results, "cards")
            print(f"已合并 {len(merged.get('cards', []))} 张卡片")
            
            return merged
            
        except Exception as e:
            print(f"分块处理失败: {str(e)}，回退到单次处理")
            return self._generate_knowledge_cards_single(content, num_cards)
    
    def _generate_language_learning_cards_with_chunking(self, content, num_cards, language="中文"):
        """
        使用分块处理生成语言学习知识卡
        
        Args:
            content: 文本内容
            num_cards: 总卡片数
            language: 生成内容使用的语言
            
        Returns:
            合并后的卡片结果
        """
        try:
            chunks = self.text_chunker.chunk_text(content)
            num_chunks = len(chunks)
            print(f"文本已分为 {num_chunks} 块")
            
            card_distribution = self._distribute_questions_across_chunks(num_chunks, num_cards)
            
            tasks = []
            for i, (chunk_text, start, end) in enumerate(chunks):
                num_c = card_distribution[i]
                if num_c > 0:
                    tasks.append((chunk_text, num_c))
            
            if self.enable_concurrent and len(tasks) > 1:
                print(f"使用并发处理，最大并发数: {self.max_concurrent}")
                
                def progress_callback(completed, total):
                    self._report_progress(completed, total, f"正在处理分块 {completed}/{total}")
                
                results = self.concurrent_processor.process_batch(
                    tasks,
                    lambda chunk_text, num_c: self._generate_language_learning_cards_single(chunk_text, num_c, language),
                    progress_callback=progress_callback
                )
            else:
                print("顺序处理各个分块")
                results = []
                for i, (chunk_text, num_c) in enumerate(tasks):
                    print(f"处理分块 {i+1}/{len(tasks)}")
                    self._report_progress(i+1, len(tasks), f"正在处理分块 {i+1}/{len(tasks)}")
                    result = self._generate_language_learning_cards_single(chunk_text, num_c, language)
                    results.append(result)
            
            merged = self.text_chunker.merge_results(results, "cards")
            print(f"已合并 {len(merged.get('cards', []))} 张语言学习卡片")
            
            return merged
            
        except Exception as e:
            print(f"分块处理失败: {str(e)}，回退到单次处理")
            return self._generate_language_learning_cards_single(content, num_cards)
            