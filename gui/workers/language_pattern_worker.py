from PyQt6.QtCore import QObject, pyqtSignal

class LanguagePatternWorker(QObject):
    """处理语言模式练习请求的工作线程"""
    finished = pyqtSignal()
    response_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_handler, sentence, target_language, specified_parts=None, language_level=None, examples_count=3):
        super().__init__()
        self.ai_handler = ai_handler
        self.sentence = sentence
        self.target_language = target_language
        self.specified_parts = specified_parts
        self.language_level = language_level
        self.examples_count = examples_count
        
    def run(self):
        try:
            # 调用AI处理器生成语言练习内容
            print(f"使用目标语言: {self.target_language} ({self.language_level})")  # 添加调试信息
            response = self.ai_handler.generate_language_pattern(
                self.sentence, 
                self.target_language, 
                self.specified_parts, 
                self.language_level, 
                self.examples_count
            )
            self.response_ready.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit() 