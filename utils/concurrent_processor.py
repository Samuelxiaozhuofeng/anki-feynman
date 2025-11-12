"""
并发处理器模块

提供并发处理API请求的功能，支持进度回调和错误处理。
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any, Optional, Tuple
import time
import threading


class ConcurrentProcessor:
    """并发处理器类"""
    
    def __init__(self, max_workers: int = 3):
        """
        初始化并发处理器
        
        Args:
            max_workers: 最大并发工作线程数
        """
        self.max_workers = max(1, min(max_workers, 10))  # 限制在1-10之间
        self._cancel_flag = threading.Event()
        
    def process_batch(
        self,
        tasks: List[Tuple[Any, ...]],
        task_func: Callable,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        error_callback: Optional[Callable[[Exception, int], None]] = None
    ) -> List[Any]:
        """
        批量并发处理任务
        
        Args:
            tasks: 任务列表，每个任务是一个参数元组
            task_func: 处理单个任务的函数
            progress_callback: 进度回调函数 (completed, total)
            error_callback: 错误回调函数 (error, task_index)
            
        Returns:
            结果列表，与任务列表顺序对应
            
        Raises:
            Exception: 如果所有任务都失败
        """
        if not tasks:
            return []
        
        # 重置取消标志
        self._cancel_flag.clear()
        
        total = len(tasks)
        results = [None] * total
        task_indices = {}
        failed_tasks = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_index = {}
            for i, task_args in enumerate(tasks):
                if self._cancel_flag.is_set():
                    break
                future = executor.submit(task_func, *task_args)
                future_to_index[future] = i
                task_indices[i] = task_args
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_index):
                if self._cancel_flag.is_set():
                    # 取消所有未完成的任务
                    for f in future_to_index:
                        f.cancel()
                    break
                
                task_index = future_to_index[future]
                
                try:
                    result = future.result()
                    results[task_index] = result
                    completed += 1
                    
                    # 调用进度回调
                    if progress_callback:
                        try:
                            progress_callback(completed, total)
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                            
                except Exception as e:
                    failed_tasks.append((task_index, e))
                    print(f"Task {task_index} failed: {str(e)}")
                    
                    # 调用错误回调
                    if error_callback:
                        try:
                            error_callback(e, task_index)
                        except Exception as callback_error:
                            print(f"Error callback error: {callback_error}")
        
        # 检查是否所有任务都失败了
        if len(failed_tasks) == total:
            raise Exception(f"所有任务都失败了。第一个错误: {failed_tasks[0][1]}")
        
        # 过滤掉None结果（失败的任务）
        valid_results = [r for r in results if r is not None]
        
        return valid_results
    
    def process_with_rate_limit(
        self,
        tasks: List[Tuple[Any, ...]],
        task_func: Callable,
        rate_limit: float = 0.5,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        error_callback: Optional[Callable[[Exception, int], None]] = None
    ) -> List[Any]:
        """
        带速率限制的并发处理
        
        Args:
            tasks: 任务列表
            task_func: 处理函数
            rate_limit: 每个任务之间的最小间隔时间（秒）
            progress_callback: 进度回调
            error_callback: 错误回调
            
        Returns:
            结果列表
        """
        if not tasks:
            return []
        
        # 重置取消标志
        self._cancel_flag.clear()
        
        total = len(tasks)
        results = [None] * total
        failed_tasks = []
        
        # 使用锁来控制速率
        rate_lock = threading.Lock()
        last_submit_time = [0]  # 使用列表以便在闭包中修改
        
        def rate_limited_func(*args):
            """带速率限制的任务函数包装"""
            with rate_lock:
                # 计算需要等待的时间
                elapsed = time.time() - last_submit_time[0]
                if elapsed < rate_limit:
                    time.sleep(rate_limit - elapsed)
                last_submit_time[0] = time.time()
            
            # 执行实际任务
            return task_func(*args)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {}
            
            # 提交所有任务（速率限制会在执行时生效）
            for i, task_args in enumerate(tasks):
                if self._cancel_flag.is_set():
                    break
                future = executor.submit(rate_limited_func, *task_args)
                future_to_index[future] = i
            
            # 收集结果
            completed = 0
            for future in as_completed(future_to_index):
                if self._cancel_flag.is_set():
                    for f in future_to_index:
                        f.cancel()
                    break
                
                task_index = future_to_index[future]
                
                try:
                    result = future.result()
                    results[task_index] = result
                    completed += 1
                    
                    if progress_callback:
                        try:
                            progress_callback(completed, total)
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                            
                except Exception as e:
                    failed_tasks.append((task_index, e))
                    print(f"Task {task_index} failed: {str(e)}")
                    
                    if error_callback:
                        try:
                            error_callback(e, task_index)
                        except Exception as callback_error:
                            print(f"Error callback error: {callback_error}")
        
        if len(failed_tasks) == total:
            raise Exception(f"所有任务都失败了。第一个错误: {failed_tasks[0][1]}")
        
        valid_results = [r for r in results if r is not None]
        return valid_results
    
    def cancel(self):
        """取消所有正在进行的任务"""
        self._cancel_flag.set()
    
    def is_cancelled(self) -> bool:
        """检查是否已取消"""
        return self._cancel_flag.is_set()
    
    def set_max_workers(self, max_workers: int):
        """
        设置最大工作线程数
        
        Args:
            max_workers: 新的最大工作线程数
        """
        self.max_workers = max(1, min(max_workers, 10))

