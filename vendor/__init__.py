import os
import sys
from typing import List, Dict

def init_vendor():
    """初始化vendor目录，确保所有依赖都可以正确导入"""
    # 将vendor目录添加到Python路径
    vendor_dir = os.path.dirname(os.path.abspath(__file__))
    if vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)

    # 需要检查的包列表
    required_packages: Dict[str, List[str]] = {
        'vendor': [  # 需要从vendor目录导入的包
            'openai',
            'httpx',
            'anyio',
            'tqdm',
            'httpcore',
            'certifi',
            'sniffio',
            'typing_extensions',
            'distro'
        ],
        'anki': [    # Anki提供的包
            'aqt',
            'anki',
            'PyQt6'
        ]
    }

    # 检查所有必需的包
    missing_packages = []
    
    # 检查vendor包
    for package in required_packages['vendor']:
        try:
            __import__(package)
        except ImportError as e:
            missing_packages.append(f"{package} (vendor): {str(e)}")
    
    # 检查Anki包
    for package in required_packages['anki']:
        try:
            __import__(package)
        except ImportError as e:
            missing_packages.append(f"{package} (anki): {str(e)}")

    if missing_packages:
        error_msg = "以下依赖包导入失败：\n" + "\n".join(missing_packages)
        raise ImportError(error_msg)

    return True

# 初始化vendor
try:
    init_vendor()
except ImportError as e:
    print(f"Error initializing vendor packages: {e}")
    raise 