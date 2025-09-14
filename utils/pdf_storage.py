"""
PDF存储管理模块

管理PDF文档的存储、检索和元数据
"""
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from aqt import mw
# 延迟导入pdf_reader，避免在模块加载时就导入pypdf


class PDFStorage:
    """PDF存储管理器"""
    
    def __init__(self):
        self.config_key = "pdf_library"
    
    def get_config(self) -> dict:
        """获取PDF库配置"""
        config = mw.addonManager.getConfig(__name__)
        return config.get(self.config_key, {
            "pdfs": [],
            "storage_path": "",
            "max_cache_size_mb": 100
        })
    
    def save_config(self, pdf_config: dict):
        """保存PDF库配置"""
        config = mw.addonManager.getConfig(__name__)
        config[self.config_key] = pdf_config
        mw.addonManager.writeConfig(__name__, config)
    
    def add_pdf(self, pdf_path: str) -> dict:
        """
        添加PDF到库中
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            PDF信息字典
            
        Raises:
            PDFReaderError: PDF读取失败时抛出
        """
        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            from .pdf_reader import PDFReaderError
            raise PDFReaderError(f"PDF文件不存在: {pdf_path}")

        # 获取PDF信息
        from .pdf_reader import get_pdf_info
        pdf_info = get_pdf_info(pdf_path)
        
        # 检查是否已存在
        pdf_config = self.get_config()
        existing_pdf = self.find_pdf_by_path(pdf_path)
        if existing_pdf:
            # 更新现有记录
            existing_pdf.update({
                'title': pdf_info['title'],
                'page_count': pdf_info['page_count'],
                'file_size': pdf_info['file_size'],
                'last_accessed': datetime.now().isoformat()
            })
            self.save_config(pdf_config)
            return existing_pdf
        
        # 创建新记录
        pdf_record = {
            'id': str(uuid.uuid4()),
            'path': pdf_path,
            'title': pdf_info['title'],
            'file_name': pdf_info['file_name'],
            'page_count': pdf_info['page_count'],
            'file_size': pdf_info['file_size'],
            'added_date': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'access_count': 0
        }
        
        pdf_config['pdfs'].append(pdf_record)
        self.save_config(pdf_config)
        
        return pdf_record
    
    def get_all_pdfs(self) -> List[dict]:
        """获取所有PDF记录"""
        pdf_config = self.get_config()
        return pdf_config.get('pdfs', [])
    
    def find_pdf_by_id(self, pdf_id: str) -> Optional[dict]:
        """根据ID查找PDF"""
        pdfs = self.get_all_pdfs()
        for pdf in pdfs:
            if pdf.get('id') == pdf_id:
                return pdf
        return None
    
    def find_pdf_by_path(self, pdf_path: str) -> Optional[dict]:
        """根据路径查找PDF"""
        pdfs = self.get_all_pdfs()
        for pdf in pdfs:
            if pdf.get('path') == pdf_path:
                return pdf
        return None
    
    def remove_pdf(self, pdf_id: str) -> bool:
        """
        从库中移除PDF
        
        Args:
            pdf_id: PDF ID
            
        Returns:
            是否成功移除
        """
        pdf_config = self.get_config()
        pdfs = pdf_config.get('pdfs', [])
        
        for i, pdf in enumerate(pdfs):
            if pdf.get('id') == pdf_id:
                pdfs.pop(i)
                self.save_config(pdf_config)
                return True
        
        return False
    
    def update_access_info(self, pdf_id: str):
        """更新PDF访问信息"""
        pdf_config = self.get_config()
        pdfs = pdf_config.get('pdfs', [])
        
        for pdf in pdfs:
            if pdf.get('id') == pdf_id:
                pdf['last_accessed'] = datetime.now().isoformat()
                pdf['access_count'] = pdf.get('access_count', 0) + 1
                self.save_config(pdf_config)
                break
    
    def validate_pdf_paths(self) -> List[str]:
        """
        验证所有PDF路径是否有效，返回无效的PDF ID列表
        
        Returns:
            无效PDF的ID列表
        """
        invalid_ids = []
        pdfs = self.get_all_pdfs()
        
        for pdf in pdfs:
            if not os.path.exists(pdf.get('path', '')):
                invalid_ids.append(pdf.get('id'))
        
        return invalid_ids
    
    def cleanup_invalid_pdfs(self) -> int:
        """
        清理无效的PDF记录
        
        Returns:
            清理的记录数量
        """
        invalid_ids = self.validate_pdf_paths()
        
        if not invalid_ids:
            return 0
        
        pdf_config = self.get_config()
        pdfs = pdf_config.get('pdfs', [])
        
        # 过滤掉无效记录
        valid_pdfs = [pdf for pdf in pdfs if pdf.get('id') not in invalid_ids]
        
        pdf_config['pdfs'] = valid_pdfs
        self.save_config(pdf_config)
        
        return len(invalid_ids)
    
    def get_recent_pdfs(self, limit: int = 5) -> List[dict]:
        """
        获取最近访问的PDF
        
        Args:
            limit: 返回数量限制
            
        Returns:
            按最近访问时间排序的PDF列表
        """
        pdfs = self.get_all_pdfs()
        
        # 按最近访问时间排序
        sorted_pdfs = sorted(
            pdfs,
            key=lambda x: x.get('last_accessed', ''),
            reverse=True
        )
        
        return sorted_pdfs[:limit]
    
    def search_pdfs(self, keyword: str) -> List[dict]:
        """
        搜索PDF
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的PDF列表
        """
        if not keyword:
            return self.get_all_pdfs()
        
        keyword = keyword.lower()
        pdfs = self.get_all_pdfs()
        
        matching_pdfs = []
        for pdf in pdfs:
            title = pdf.get('title', '').lower()
            file_name = pdf.get('file_name', '').lower()
            
            if keyword in title or keyword in file_name:
                matching_pdfs.append(pdf)
        
        return matching_pdfs


# 全局实例
pdf_storage = PDFStorage()
