"""AI响应处理工具"""
import json
import re
from typing import Dict, List, Any

class ResponseHandler:
    """处理AI响应的工具类"""
    
    @staticmethod
    def clean_response(response: str) -> str:
        """清理AI响应文本，移除代码块标记等"""
        cleaned = response.strip()
        
        # 移除代码块标记
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
            
        # 移除语言标识
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        
        return cleaned
    
    @staticmethod
    def fix_incomplete_json(json_str: str) -> str:
        """修复不完整的JSON字符串"""
        # 处理末尾不完整的情况
        if not json_str.endswith("}"):
            # 尝试找到最后一个完整的对象
            last_complete = json_str.rfind('        }')
            if last_complete != -1:
                json_str = json_str[:last_complete + 9] + "\n    ]\n}"
        return json_str
    
    @staticmethod
    def advanced_json_fix(json_str: str) -> str:
        """高级JSON修复，处理各种常见的JSON格式错误"""
        # 1. 尝试修复缺少逗号的问题
        # 查找可能缺少逗号的位置 - 通常是在对象或数组项之后
        pattern = r'(["}\]])\s*\n\s*(["{\[])'
        json_str = re.sub(pattern, r'\1,\n\2', json_str)
        
        # 特别处理题目列表中可能缺少的逗号
        # 例如："question": "问题内容"\n    "options": 之间缺少逗号
        pattern_question = r'("question":\s*"[^"]*")\s*\n\s*(")'
        json_str = re.sub(pattern_question, r'\1,\n    \2', json_str)
        
        # 处理选项之间缺少的逗号
        pattern_options = r'("options":\s*\[\s*(?:"[^"]*",\s*)*"[^"]*")\s*\n\s*(")'
        json_str = re.sub(pattern_options, r'\1,\n    \2', json_str)
        
        # 处理correct_answer后缺少的逗号
        pattern_correct = r'("correct_answer":\s*"[^"]*")\s*\n\s*(")'
        json_str = re.sub(pattern_correct, r'\1,\n    \2', json_str)
        
        # 处理explanation后缺少的逗号
        pattern_explanation = r'("explanation":\s*"[^"]*")\s*\n\s*(")'
        json_str = re.sub(pattern_explanation, r'\1,\n    \2', json_str)
        
        # 处理key_points后缺少的逗号
        pattern_key_points = r'("key_points":\s*\[[^\]]*\])\s*\n\s*(")'
        json_str = re.sub(pattern_key_points, r'\1,\n    \2', json_str)
        
        # 处理reference_answer后缺少的逗号
        pattern_reference = r'("reference_answer":\s*"[^"]*")\s*\n\s*(")'
        json_str = re.sub(pattern_reference, r'\1,\n    \2', json_str)
        
        # 2. 修复多余的逗号
        # 数组末尾多余的逗号
        json_str = re.sub(r',\s*\]', r']', json_str)
        # 对象末尾多余的逗号
        json_str = re.sub(r',\s*\}', r'}', json_str)
        
        # 3. 修复未闭合的引号
        # 这是一个简化的处理，实际上引号不匹配的问题很复杂
        # 计算引号数量，如果是奇数，尝试找到可能缺少引号的位置
        if json_str.count('"') % 2 != 0:
            lines = json_str.split('\n')
            for i, line in enumerate(lines):
                # 如果一行中有奇数个引号，可能是这行缺少引号
                if line.count('"') % 2 != 0:
                    # 检查是否是值的结尾缺少引号
                    if ':' in line and line.rstrip()[-1] not in ['"', '}', ']', ',']:
                        lines[i] = line + '"'
            json_str = '\n'.join(lines)
        
        # 4. 确保JSON对象和数组的完整性
        # 检查大括号是否匹配
        if json_str.count('{') > json_str.count('}'):
            json_str += '}'
        # 检查方括号是否匹配
        if json_str.count('[') > json_str.count(']'):
            json_str += ']'
        
        # 5. 处理特定位置的格式问题
        # 检查第13行附近是否缺少逗号（根据错误信息）
        lines = json_str.split('\n')
        if len(lines) >= 13:
            line12 = lines[12] if len(lines) > 12 else ""
            line13 = lines[13] if len(lines) > 13 else ""
            
            # 如果第12行结束没有逗号，且第13行开始是一个新的键
            if line12 and line13 and not line12.rstrip().endswith(',') and re.match(r'\s*"[^"]+"\s*:', line13):
                lines[12] = line12.rstrip() + ','
                json_str = '\n'.join(lines)
        
        return json_str
    
    @staticmethod
    def deep_json_fix(json_str: str) -> str:
        """深度JSON修复，处理更复杂的格式问题
        
        这个方法尝试通过更激进的方式修复JSON，适用于常规修复方法失败的情况
        """
        # 首先尝试识别JSON的基本结构
        # 大多数情况下，我们期望的是一个包含questions数组的对象
        
        # 1. 确保最外层是一个对象
        json_str = json_str.strip()
        if not json_str.startswith('{'):
            json_str = '{' + json_str
        if not json_str.endswith('}'):
            json_str = json_str + '}'
            
        # 2. 尝试识别和修复questions数组
        questions_match = re.search(r'"questions"\s*:\s*\[', json_str)
        if questions_match:
            # 找到questions数组的开始位置
            start_pos = questions_match.end()
            # 尝试找到数组的结束位置
            bracket_count = 1  # 已经遇到了一个[
            end_pos = len(json_str)
            
            for i in range(start_pos, len(json_str)):
                if json_str[i] == '[':
                    bracket_count += 1
                elif json_str[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end_pos = i + 1
                        break
            
            # 提取questions数组内容
            questions_content = json_str[start_pos:end_pos-1]  # 不包括最后的]
            
            # 分割成单独的问题对象
            question_objects = []
            object_start = 0
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(questions_content):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                elif not in_string:
                    if char == '{':
                        if bracket_count == 0:
                            object_start = i
                        bracket_count += 1
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            # 找到一个完整的问题对象
                            question_obj = questions_content[object_start:i+1]
                            # 尝试修复这个对象
                            fixed_obj = ResponseHandler.fix_question_object(question_obj)
                            question_objects.append(fixed_obj)
            
            # 重建questions数组
            fixed_questions = ',\n'.join(question_objects)
            fixed_json = json_str[:start_pos] + fixed_questions + json_str[end_pos-1:]
            
            return fixed_json
        
        return json_str
    
    @staticmethod
    def fix_question_object(question_obj: str) -> str:
        """修复单个问题对象的JSON格式"""
        # 确保对象的开始和结束
        question_obj = question_obj.strip()
        if not question_obj.startswith('{'):
            question_obj = '{' + question_obj
        if not question_obj.endswith('}'):
            question_obj = question_obj + '}'
            
        # 使用正则表达式找出所有键值对
        pairs = re.findall(r'"([^"]+)"\s*:\s*("(?:\\.|[^"\\])*"|[\[\{].*?[\]\}]|\d+|true|false|null)', question_obj, re.DOTALL)
        
        # 重建对象，确保键值对之间有逗号
        if pairs:
            fixed_obj = '{\n'
            for i, (key, value) in enumerate(pairs):
                fixed_obj += f'    "{key}": {value}'
                if i < len(pairs) - 1:
                    fixed_obj += ',\n'
                else:
                    fixed_obj += '\n'
            fixed_obj += '}'
            return fixed_obj
            
        return question_obj
        
    @staticmethod
    def try_multiple_fixes(response: str) -> str:
        """尝试多种方法修复JSON"""
        # 首先进行基本清理
        cleaned = ResponseHandler.clean_response(response)
        
        # 尝试直接解析
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            pass
        
        # 尝试基本的不完整JSON修复
        fixed = ResponseHandler.fix_incomplete_json(cleaned)
        try:
            json.loads(fixed)
            return fixed
        except json.JSONDecodeError:
            pass
        
        # 尝试高级修复
        advanced_fixed = ResponseHandler.advanced_json_fix(cleaned)
        try:
            json.loads(advanced_fixed)
            return advanced_fixed
        except json.JSONDecodeError:
            pass
            
        # 尝试深度修复
        deep_fixed = ResponseHandler.deep_json_fix(cleaned)
        try:
            json.loads(deep_fixed)
            return deep_fixed
        except json.JSONDecodeError:
            pass
        
        # 如果所有修复都失败，返回原始清理后的文本
        # 让json.loads抛出具体的错误信息
        return cleaned

    def validate_choice_question(self, data: Dict[str, Any]) -> None:
        """验证选择题格式"""
        if not isinstance(data, dict) or "questions" not in data:
            raise ValueError("返回的JSON格式不正确：缺少questions字段")
        
        for q in data["questions"]:
            if not all(key in q for key in ["question", "options", "correct_answer", "explanation", "source_content"]):
                raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
            if not isinstance(q["options"], list) or len(q["options"]) != 4:
                raise ValueError("返回的JSON格式不正确：选项数量不正确")
            if q["correct_answer"] not in ["A", "B", "C", "D"]:
                raise ValueError("返回的JSON格式不正确：正确答案必须是A、B、C、D之一")

    def validate_knowledge_card(self, data: Dict[str, Any]) -> None:
        """验证知识卡片格式"""
        if not isinstance(data, dict) or "cards" not in data:
            raise ValueError("返回的JSON格式不正确：缺少cards字段")
        
        for card in data["cards"]:
            if not all(key in card for key in ["question", "answer", "context"]):
                raise ValueError("返回的JSON格式不正确：卡片数据结构不完整")
            if not all(isinstance(card[key], str) for key in ["question", "answer", "context"]):
                raise ValueError("返回的JSON格式不正确：字段值必须是字符串")

    def validate_essay_evaluation(self, data: Dict[str, Any]) -> None:
        """验证问答评估格式"""
        required_fields = ["score", "feedback", "covered_points", "missing_points", "suggestions"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"AI返回的JSON缺少必要字段：{', '.join(missing_fields)}")
        
        if not isinstance(data["score"], (int, float)):
            raise ValueError("score必须是数字")
        if not isinstance(data["feedback"], str):
            raise ValueError("feedback必须是字符串")
        if not isinstance(data["covered_points"], list):
            raise ValueError("covered_points必须是数组")
        if not isinstance(data["missing_points"], list):
            raise ValueError("missing_points必须是数组")
        if not isinstance(data["suggestions"], list):
            raise ValueError("suggestions必须是数组")

    def validate_cloze_card(self, data: Dict[str, Any]) -> None:
        """验证填空卡片格式"""
        if not isinstance(data, dict) or "cards" not in data:
            raise ValueError("返回的JSON格式不正确：缺少cards字段")
        
        for card in data["cards"]:
            if not all(key in card for key in ["question", "answer", "context"]):
                raise ValueError("返回的JSON格式不正确：卡片数据结构不完整")
            if not all(isinstance(card[key], str) for key in ["question", "answer", "context"]):
                raise ValueError("返回的JSON格式不正确：字段值必须是字符串")
    
    def validate_essay_question(self, data: Dict[str, Any]) -> None:
        """验证问答题格式"""
        if not isinstance(data, dict) or "questions" not in data:
            raise ValueError("返回的JSON格式不正确：缺少questions字段")
        
        for q in data["questions"]:
            if not all(key in q for key in ["question", "reference_answer", "key_points", "source_content"]):
                raise ValueError("返回的JSON格式不正确：问题数据结构不完整")
            if not isinstance(q["key_points"], list) or len(q["key_points"]) < 3:
                raise ValueError("返回的JSON格式不正确：关键点数量不足")

    def parse_and_validate(self, response: str, schema_type: str) -> dict:
        """解析并验证JSON响应
        
        Args:
            response: AI的原始响应文本
            schema_type: 模式类型，可选值：choice_question, knowledge_card, essay_evaluation, cloze_card, essay_question
            
        Returns:
            解析后的JSON对象
            
        Raises:
            ValueError: 当JSON解析失败或验证失败时
        """
        # 添加调试信息
        debug_info = f"尝试解析{schema_type}类型的JSON..."
        
        try:
            # 尝试从文本中提取JSON部分（删除前导和尾随文本）
            json_text = response
            
            # 查找JSON的开始位置
            json_start = response.find('{')
            if json_start > 0:
                # 如果JSON不是从开头开始，则可能有前导文本
                debug_info += f"\n发现前导文本，JSON从位置{json_start}开始。"
                json_text = response[json_start:]
            
            # 查找JSON的结束位置（找到最后一个闭合的大括号）
            json_end = len(json_text)
            stack = []
            for i, char in enumerate(json_text):
                if char == '{':
                    stack.append(i)
                elif char == '}':
                    if stack:
                        stack.pop()
                        if not stack:  # 如果栈为空，意味着我们找到了最后匹配的闭合括号
                            json_end = i + 1
                            break
            
            if json_end < len(json_text):
                # 如果找到了闭合括号且不在文本末尾，可能有尾随文本
                debug_info += f"\n发现尾随文本，JSON在位置{json_end}结束。"
                json_text = json_text[:json_end]
            
            # 尝试多种方法修复JSON
            fixed = self.try_multiple_fixes(json_text)
            debug_info += "\n尝试修复JSON格式..."
            
            # 解析JSON
            try:
                data = json.loads(fixed)
                debug_info += "\nJSON解析成功!"
            except json.JSONDecodeError as e:
                debug_info += f"\nJSON解析失败: {str(e)}，尝试额外的修复方法..."
                
                # 尝试修复引号问题
                fixed = fixed.replace("'", '"')  # 将单引号替换为双引号
                
                # 尝试修复常见的问题，如尾部逗号
                fixed = re.sub(r',\s*}', '}', fixed)  # 删除对象结尾的逗号
                fixed = re.sub(r',\s*]', ']', fixed)  # 删除数组结尾的逗号
                
                # 如果是选择题，尝试修复options数组格式
                if schema_type == "choice_question":
                    # 查找并修复options数组中可能的格式问题
                    options_pattern = r'"options"\s*:\s*\[(.*?)\]'
                    for match in re.finditer(options_pattern, fixed, re.DOTALL):
                        options_content = match.group(1)
                        if ',' not in options_content:
                            # 可能缺少逗号，尝试添加
                            fixed_options = re.sub(r'("[^"]*")\s*("[^"]*")', r'\1, \2', options_content)
                            fixed = fixed.replace(options_content, fixed_options)
                
                data = json.loads(fixed)
                debug_info += "\n额外修复后JSON解析成功!"
            
            # 根据类型验证
            validator_map = {
                "choice_question": self.validate_choice_question,
                "knowledge_card": self.validate_knowledge_card,
                "essay_evaluation": self.validate_essay_evaluation,
                "cloze_card": self.validate_cloze_card,
                "essay_question": self.validate_essay_question
            }
            
            validator = validator_map.get(schema_type)
            if not validator:
                raise ValueError(f"未知的schema类型：{schema_type}")
            
            validator(data)
            return data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败：{str(e)}\n原始内容：{response[:200]}...\n调试信息：{debug_info}"
            print(error_msg)  # 打印错误信息以便调试
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"处理响应时出错：{str(e)}\n调试信息：{debug_info}"
            print(error_msg)  # 打印错误信息以便调试
            raise ValueError(error_msg) 