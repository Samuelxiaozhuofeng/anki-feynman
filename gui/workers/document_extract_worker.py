"""
文档提取工作线程

在后台线程中处理PDF文本提取，避免阻塞UI
"""
from aqt.qt import QObject, pyqtSignal
from ...utils.pdf_reader import extract_text_from_pages, PDFReaderError


class DocumentExtractWorker(QObject):
    """文档提取工作线程类"""
    
    finished = pyqtSignal()
    text_extracted = pyqtSignal(str)  # 提取的文本
    error_occurred = pyqtSignal(str)  # 错误信息
    progress_updated = pyqtSignal(str)  # 进度更新
    
    def __init__(self, pdf_path: str, start_page: int, end_page: int):
        """
        初始化文档提取工作线程
        
        Args:
            pdf_path: PDF文件路径
            start_page: 起始页码
            end_page: 结束页码
        """
        super().__init__()
        self.pdf_path = pdf_path
        self.start_page = start_page
        self.end_page = end_page
    
    def run(self):
        """运行工作线程，提取文档文本"""
        try:
            # 更新进度
            self.progress_updated.emit(f"正在提取第 {self.start_page}-{self.end_page} 页...")
            
            # 提取文本
            extracted_text = extract_text_from_pages(
                self.pdf_path, 
                self.start_page, 
                self.end_page
            )
            
            # 检查提取结果
            if not extracted_text or not extracted_text.strip():
                self.error_occurred.emit("未能从指定页面提取到任何文本内容")
                return
            
            # 更新进度
            self.progress_updated.emit("文本提取完成")
            
            # 发出提取成功信号
            self.text_extracted.emit(extracted_text)
            
        except PDFReaderError as e:
            self.error_occurred.emit(f"PDF读取错误: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"文本提取失败: {str(e)}")
        finally:
            self.finished.emit()
