"""
题目集管理模块
处理题目集的保存、加载和管理功能
"""
import json
import os
import time
from typing import List, Dict, Any, Optional

# 确保data目录存在
def ensure_data_dir():
    """确保data目录存在"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

# 题目集文件路径
def question_sets_file_path():
    """获取题目集文件路径"""
    data_dir = ensure_data_dir()
    return os.path.join(data_dir, "question_sets.json")

# 加载题目集列表
def load_question_sets() -> List[Dict[str, Any]]:
    """
    加载所有保存的题目集
    
    Returns:
        List[Dict[str, Any]]: 题目集列表
    """
    try:
        file_path = question_sets_file_path()
        if not os.path.exists(file_path):
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"加载题目集失败: {str(e)}")
        return []

# 保存题目集列表
def save_question_sets(question_sets: List[Dict[str, Any]]) -> bool:
    """
    保存题目集列表
    
    Args:
        question_sets (List[Dict[str, Any]]): 题目集列表
        
    Returns:
        bool: 是否保存成功
    """
    try:
        file_path = question_sets_file_path()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(question_sets, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存题目集失败: {str(e)}")
        return False

# 添加新题目集
def add_question_set(title: str, questions: Dict[str, Any], current_index: int = 0) -> bool:
    """
    添加新题目集
    
    Args:
        title (str): 题目集标题
        questions (Dict[str, Any]): 题目数据
        current_index (int): 当前回答到的问题索引
        
    Returns:
        bool: 是否添加成功
    """
    try:
        # 加载现有题目集
        question_sets = load_question_sets()
        
        # 创建新题目集
        new_set = {
            "id": str(int(time.time())),  # 使用时间戳作为ID
            "title": title,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_index": current_index,
            "questions": questions
        }
        
        # 添加到列表
        question_sets.append(new_set)
        
        # 保存到文件
        return save_question_sets(question_sets)
    except Exception as e:
        print(f"添加题目集失败: {str(e)}")
        return False

# 更新题目集
def update_question_set(question_set_id: str, current_index: int) -> bool:
    """
    更新题目集进度
    
    Args:
        question_set_id (str): 题目集ID
        current_index (int): 当前回答到的问题索引
        
    Returns:
        bool: 是否更新成功
    """
    try:
        # 加载现有题目集
        question_sets = load_question_sets()
        
        # 查找指定题目集
        for question_set in question_sets:
            if question_set.get("id") == question_set_id:
                question_set["current_index"] = current_index
                question_set["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                break
        else:
            # 未找到指定题目集
            return False
        
        # 保存到文件
        return save_question_sets(question_sets)
    except Exception as e:
        print(f"更新题目集失败: {str(e)}")
        return False

# 删除题目集
def delete_question_set(question_set_id: str) -> bool:
    """
    删除题目集
    
    Args:
        question_set_id (str): 题目集ID
        
    Returns:
        bool: 是否删除成功
    """
    try:
        # 加载现有题目集
        question_sets = load_question_sets()
        
        # 过滤掉要删除的题目集
        updated_sets = [qs for qs in question_sets if qs.get("id") != question_set_id]
        
        # 如果列表长度没变，说明没找到指定题目集
        if len(updated_sets) == len(question_sets):
            return False
        
        # 保存到文件
        return save_question_sets(updated_sets)
    except Exception as e:
        print(f"删除题目集失败: {str(e)}")
        return False

# 根据ID获取题目集
def get_question_set_by_id(question_set_id: str) -> Optional[Dict[str, Any]]:
    """
    根据ID获取题目集
    
    Args:
        question_set_id (str): 题目集ID
        
    Returns:
        Optional[Dict[str, Any]]: 题目集数据，如果未找到则返回None
    """
    try:
        # 加载现有题目集
        question_sets = load_question_sets()
        
        # 查找指定题目集
        for question_set in question_sets:
            if question_set.get("id") == question_set_id:
                return question_set
                
        # 未找到
        return None
    except Exception as e:
        print(f"获取题目集失败: {str(e)}")
        return None 