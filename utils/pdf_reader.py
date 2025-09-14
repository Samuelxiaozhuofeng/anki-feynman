"""
PDF文档读取工具模块

使用pypdf库提取PDF文档的文本内容
"""
import os
from typing import Optional, Tuple, List

# 延迟导入pypdf，避免在模块加载时就导入
def _get_pypdf():
    """获取pypdf模块，延迟导入"""
    try:
        from pypdf import PdfReader
        return PdfReader, True
    except ImportError:
        return None, False


class PDFReaderError(Exception):
    """PDF读取相关错误"""
    pass


def check_pypdf_availability():
    """检查pypdf是否可用"""
    _, available = _get_pypdf()
    return available


def get_pdf_info(pdf_path: str) -> dict:
    """
    获取PDF文档基本信息

    Args:
        pdf_path: PDF文件路径

    Returns:
        包含PDF信息的字典：{
            'title': str,
            'page_count': int,
            'file_size': int,
            'file_name': str
        }

    Raises:
        PDFReaderError: PDF读取失败时抛出
    """
    PdfReader, available = _get_pypdf()
    if not available:
        raise PDFReaderError("pypdf库未安装，无法读取PDF文件")
    
    if not os.path.exists(pdf_path):
        raise PDFReaderError(f"PDF文件不存在: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            
            # 获取文档信息
            metadata = reader.metadata
            title = ""
            if metadata and metadata.title:
                title = metadata.title
            
            # 如果没有标题，使用文件名
            if not title:
                title = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # 获取文件大小
            file_size = os.path.getsize(pdf_path)
            
            return {
                'title': title,
                'page_count': len(reader.pages),
                'file_size': file_size,
                'file_name': os.path.basename(pdf_path)
            }
            
    except Exception as e:
        raise PDFReaderError(f"读取PDF信息失败: {str(e)}")


def extract_text_from_pages(pdf_path: str, start_page: int, end_page: int) -> str:
    """
    从PDF指定页码范围提取文本

    Args:
        pdf_path: PDF文件路径
        start_page: 起始页码（从1开始）
        end_page: 结束页码（包含，从1开始）

    Returns:
        提取的文本内容

    Raises:
        PDFReaderError: PDF读取失败时抛出
    """
    PdfReader, available = _get_pypdf()
    if not available:
        raise PDFReaderError("pypdf库未安装，无法读取PDF文件")
    
    if not os.path.exists(pdf_path):
        raise PDFReaderError(f"PDF文件不存在: {pdf_path}")
    
    if start_page < 1 or end_page < start_page:
        raise PDFReaderError("页码范围无效")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            
            if start_page > total_pages:
                raise PDFReaderError(f"起始页码 {start_page} 超出文档总页数 {total_pages}")
            
            # 调整结束页码，不超过总页数
            actual_end_page = min(end_page, total_pages)
            
            extracted_text = []
            
            # 提取指定范围的页面文本（pypdf使用0基索引）
            for page_num in range(start_page - 1, actual_end_page):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():  # 只添加非空文本
                        extracted_text.append(f"=== 第 {page_num + 1} 页 ===\n{text.strip()}")
                except Exception as e:
                    print(f"警告：提取第 {page_num + 1} 页时出错: {str(e)}")
                    continue
            
            if not extracted_text:
                raise PDFReaderError(f"从页码 {start_page}-{actual_end_page} 未能提取到任何文本")
            
            return "\n\n".join(extracted_text)
            
    except PDFReaderError:
        raise
    except Exception as e:
        raise PDFReaderError(f"提取PDF文本失败: {str(e)}")


def validate_page_range(pdf_path: str, start_page: int, end_page: int) -> Tuple[bool, str]:
    """
    验证页码范围是否有效
    
    Args:
        pdf_path: PDF文件路径
        start_page: 起始页码
        end_page: 结束页码
        
    Returns:
        (是否有效, 错误信息)
    """
    try:
        if start_page < 1:
            return False, "起始页码必须大于0"
        
        if end_page < start_page:
            return False, "结束页码不能小于起始页码"
        
        pdf_info = get_pdf_info(pdf_path)
        total_pages = pdf_info['page_count']
        
        if start_page > total_pages:
            return False, f"起始页码 {start_page} 超出文档总页数 {total_pages}"
        
        if end_page > total_pages:
            return False, f"结束页码 {end_page} 超出文档总页数 {total_pages}，将自动调整为 {total_pages}"
        
        return True, ""
        
    except PDFReaderError as e:
        return False, str(e)


def get_page_preview(pdf_path: str, page_num: int, max_chars: int = 200) -> str:
    """
    获取指定页面的文本预览

    Args:
        pdf_path: PDF文件路径
        page_num: 页码（从1开始）
        max_chars: 最大字符数

    Returns:
        页面文本预览
    """
    try:
        text = extract_text_from_pages(pdf_path, page_num, page_num)
        # 移除页面标题行
        lines = text.split('\n')
        content_lines = [line for line in lines if not line.startswith('=== 第')]
        content = '\n'.join(content_lines).strip()

        if len(content) > max_chars:
            return content[:max_chars] + "..."
        return content

    except PDFReaderError:
        return "无法预览此页面"


def get_page_range_preview(pdf_path: str, start_page: int, end_page: int, max_chars_per_section: int = 300) -> dict:
    """
    获取页码范围的预览，显示起始页开头和结束页结尾的文本

    Args:
        pdf_path: PDF文件路径
        start_page: 起始页码（从1开始）
        end_page: 结束页码（从1开始）
        max_chars_per_section: 每个部分的最大字符数

    Returns:
        包含预览信息的字典：{
            'start_preview': str,  # 起始页开头文本
            'end_preview': str,    # 结束页结尾文本
            'start_page': int,     # 起始页码
            'end_page': int,       # 结束页码
            'total_pages': int,    # 总页数
            'error': str           # 错误信息（如果有）
        }
    """
    PdfReader, available = _get_pypdf()
    if not available:
        return {
            'start_preview': '',
            'end_preview': '',
            'start_page': start_page,
            'end_page': end_page,
            'total_pages': 0,
            'error': 'pypdf库未安装，无法预览PDF文件'
        }

    if not os.path.exists(pdf_path):
        return {
            'start_preview': '',
            'end_preview': '',
            'start_page': start_page,
            'end_page': end_page,
            'total_pages': 0,
            'error': f'PDF文件不存在: {pdf_path}'
        }

    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)

            if start_page < 1 or start_page > total_pages:
                return {
                    'start_preview': '',
                    'end_preview': '',
                    'start_page': start_page,
                    'end_page': end_page,
                    'total_pages': total_pages,
                    'error': f'起始页码 {start_page} 超出范围 (1-{total_pages})'
                }

            if end_page < start_page or end_page > total_pages:
                end_page = min(end_page, total_pages)

            # 获取起始页的开头文本
            start_preview = ""
            try:
                start_page_obj = reader.pages[start_page - 1]
                start_text = start_page_obj.extract_text().strip()
                if start_text:
                    # 取前几行作为开头预览
                    start_lines = start_text.split('\n')[:5]  # 取前5行
                    start_preview = '\n'.join(line.strip() for line in start_lines if line.strip())
                    if len(start_preview) > max_chars_per_section:
                        start_preview = start_preview[:max_chars_per_section] + "..."
                else:
                    start_preview = "（此页面无文本内容）"
            except Exception as e:
                start_preview = f"（无法读取第 {start_page} 页：{str(e)}）"

            # 获取结束页的结尾文本
            end_preview = ""
            if end_page == start_page:
                # 如果起始页和结束页是同一页，显示该页的结尾部分
                try:
                    if start_text:
                        end_lines = start_text.split('\n')[-5:]  # 取后5行
                        end_preview = '\n'.join(line.strip() for line in end_lines if line.strip())
                        if len(end_preview) > max_chars_per_section:
                            end_preview = "..." + end_preview[-max_chars_per_section:]
                    else:
                        end_preview = "（此页面无文本内容）"
                except Exception as e:
                    end_preview = f"（无法读取第 {end_page} 页：{str(e)}）"
            else:
                # 获取结束页的文本
                try:
                    end_page_obj = reader.pages[end_page - 1]
                    end_text = end_page_obj.extract_text().strip()
                    if end_text:
                        # 取后几行作为结尾预览
                        end_lines = end_text.split('\n')[-5:]  # 取后5行
                        end_preview = '\n'.join(line.strip() for line in end_lines if line.strip())
                        if len(end_preview) > max_chars_per_section:
                            end_preview = "..." + end_preview[-max_chars_per_section:]
                    else:
                        end_preview = "（此页面无文本内容）"
                except Exception as e:
                    end_preview = f"（无法读取第 {end_page} 页：{str(e)}）"

            return {
                'start_preview': start_preview,
                'end_preview': end_preview,
                'start_page': start_page,
                'end_page': end_page,
                'total_pages': total_pages,
                'error': ''
            }

    except Exception as e:
        return {
            'start_preview': '',
            'end_preview': '',
            'start_page': start_page,
            'end_page': end_page,
            'total_pages': 0,
            'error': f'读取PDF文件失败: {str(e)}'
        }
