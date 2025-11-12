"""
文本分块工具模块

提供智能和简单两种文本分块策略，用于处理长文本。
"""

import re
from typing import List, Tuple


class TextChunker:
    """文本分块工具类"""
    
    def __init__(self, chunk_size: int = 2000, overlap: int = 200, strategy: str = "smart"):
        """
        初始化文本分块器
        
        Args:
            chunk_size: 每块的字符数
            overlap: 分块之间的重叠字符数
            strategy: 分块策略 ("simple" 或 "smart")
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy
        
    def chunk_text(self, text: str) -> List[Tuple[str, int, int]]:
        """
        将文本分块
        
        Args:
            text: 要分块的文本
            
        Returns:
            分块列表，每个元素为 (chunk_text, start_pos, end_pos)
        """
        if not text or len(text) <= self.chunk_size:
            # 文本太短，不需要分块
            return [(text, 0, len(text))]
        
        if self.strategy == "smart":
            return self._smart_chunk(text)
        else:
            return self._simple_chunk(text)
    
    def _simple_chunk(self, text: str) -> List[Tuple[str, int, int]]:
        """
        简单分块：按固定字符数分块
        
        Args:
            text: 要分块的文本
            
        Returns:
            分块列表
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # 计算当前块的结束位置
            end = min(start + self.chunk_size, text_len)
            chunk = text[start:end]
            chunks.append((chunk, start, end))
            
            # 下一块的起始位置（考虑重叠）
            start = end - self.overlap if end < text_len else text_len
            
        return chunks
    
    def _smart_chunk(self, text: str) -> List[Tuple[str, int, int]]:
        """
        智能分块：在自然边界处分块（段落、句子）
        
        Args:
            text: 要分块的文本
            
        Returns:
            分块列表
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            # 计算理想的结束位置
            ideal_end = min(start + self.chunk_size, text_len)
            
            if ideal_end >= text_len:
                # 已到文本末尾
                chunks.append((text[start:text_len], start, text_len))
                break
            
            # 寻找自然断点
            actual_end = self._find_natural_break(text, start, ideal_end, text_len)
            chunk = text[start:actual_end]
            chunks.append((chunk, start, actual_end))
            
            # 计算下一块的起始位置（考虑重叠）
            if actual_end < text_len:
                # 向前查找重叠区域的起始点
                overlap_start = max(start, actual_end - self.overlap)
                # 尝试在重叠区域找到段落或句子边界
                next_start = self._find_overlap_start(text, overlap_start, actual_end)
                start = next_start
            else:
                start = text_len
                
        return chunks
    
    def _find_natural_break(self, text: str, start: int, ideal_end: int, text_len: int) -> int:
        """
        寻找自然断点
        
        Args:
            text: 文本
            start: 起始位置
            ideal_end: 理想结束位置
            text_len: 文本总长度
            
        Returns:
            实际结束位置
        """
        # 如果理想结束位置就是文本末尾，直接返回
        if ideal_end >= text_len:
            return text_len
        
        # 定义搜索窗口（在理想位置前后各搜索一定范围）
        search_window = min(200, self.chunk_size // 4)
        search_start = max(start, ideal_end - search_window)
        search_end = min(text_len, ideal_end + search_window)
        search_text = text[search_start:search_end]
        
        # 1. 优先查找段落边界（双换行符）
        paragraph_breaks = [m.end() for m in re.finditer(r'\n\s*\n', search_text)]
        if paragraph_breaks:
            # 找到最接近理想位置的段落边界
            closest = min(paragraph_breaks, 
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 2. 查找单换行符
        newline_breaks = [m.end() for m in re.finditer(r'\n', search_text)]
        if newline_breaks:
            closest = min(newline_breaks,
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 3. 查找句子边界（句号、问号、感叹号后跟空格或换行）
        sentence_breaks = [m.end() for m in re.finditer(r'[。！？.!?]\s+', search_text)]
        if sentence_breaks:
            closest = min(sentence_breaks,
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 4. 查找中文句号
        chinese_sentence_breaks = [m.end() for m in re.finditer(r'[。！？]', search_text)]
        if chinese_sentence_breaks:
            closest = min(chinese_sentence_breaks,
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 5. 查找逗号、分号等标点
        punctuation_breaks = [m.end() for m in re.finditer(r'[，,;；]\s*', search_text)]
        if punctuation_breaks:
            closest = min(punctuation_breaks,
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 6. 查找空格
        space_breaks = [m.end() for m in re.finditer(r'\s+', search_text)]
        if space_breaks:
            closest = min(space_breaks,
                         key=lambda x: abs((search_start + x) - ideal_end))
            return search_start + closest
        
        # 7. 如果都找不到，直接在理想位置分割
        return ideal_end
    
    def _find_overlap_start(self, text: str, overlap_start: int, chunk_end: int) -> int:
        """
        寻找重叠区域的起始点，尽量在自然边界处
        
        Args:
            text: 文本
            overlap_start: 重叠区域的理想起始位置
            chunk_end: 上一块的结束位置
            
        Returns:
            重叠区域的实际起始位置
        """
        search_text = text[overlap_start:chunk_end]
        
        # 1. 查找段落开始
        paragraph_starts = [m.start() for m in re.finditer(r'\n\s*\n\s*', search_text)]
        if paragraph_starts:
            # 使用最后一个段落开始
            return overlap_start + paragraph_starts[-1] + len(re.search(r'\n\s*\n\s*', search_text[paragraph_starts[-1]:]).group())
        
        # 2. 查找换行符
        newline_starts = [m.start() for m in re.finditer(r'\n', search_text)]
        if newline_starts:
            return overlap_start + newline_starts[-1] + 1
        
        # 3. 查找句子开始（标点后的位置）
        sentence_starts = [m.end() for m in re.finditer(r'[。！？.!?]\s+', search_text)]
        if sentence_starts:
            return overlap_start + sentence_starts[-1]
        
        # 4. 如果都找不到，使用理想起始位置
        return overlap_start
    
    def merge_results(self, chunk_results: List[dict], result_type: str = "questions") -> dict:
        """
        合并多个分块的生成结果
        
        Args:
            chunk_results: 各分块的生成结果列表
            result_type: 结果类型 ("questions" 或 "cards")
            
        Returns:
            合并后的结果
        """
        if not chunk_results:
            return {"questions": []} if result_type == "questions" else {"cards": []}
        
        if result_type == "questions":
            merged = {"questions": []}
            for result in chunk_results:
                if isinstance(result, dict) and "questions" in result:
                    merged["questions"].extend(result["questions"])
            return merged
        elif result_type == "cards":
            merged = {"cards": []}
            for result in chunk_results:
                if isinstance(result, dict) and "cards" in result:
                    merged["cards"].extend(result["cards"])
            return merged
        else:
            # 对于其他类型，简单地返回第一个结果
            return chunk_results[0] if chunk_results else {}
    
    def should_chunk(self, text: str, threshold_multiplier: float = 1.5) -> bool:
        """
        判断文本是否需要分块
        
        Args:
            text: 要判断的文本
            threshold_multiplier: 阈值倍数，文本长度超过 chunk_size * threshold_multiplier 时才分块
            
        Returns:
            是否需要分块
        """
        return len(text) > self.chunk_size * threshold_multiplier
    
    def get_chunk_count(self, text: str) -> int:
        """
        计算文本会被分成多少块
        
        Args:
            text: 文本
            
        Returns:
            分块数量
        """
        if not self.should_chunk(text):
            return 1
        
        # 粗略估算
        text_len = len(text)
        if text_len <= self.chunk_size:
            return 1
        
        # 考虑重叠的分块数估算
        effective_chunk_size = self.chunk_size - self.overlap
        if effective_chunk_size <= 0:
            return 1
        
        chunks_needed = 1 + (text_len - self.chunk_size + effective_chunk_size - 1) // effective_chunk_size
        return max(1, chunks_needed)

