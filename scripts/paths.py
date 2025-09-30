#!/usr/bin/env python3
"""
统一路径配置
确保所有脚本都使用相对于项目根目录的路径
"""

from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录路径（相对于项目根目录）
DATA_DIRS = {
    'raw': PROJECT_ROOT / 'data' / 'raw',
    'processed': PROJECT_ROOT / 'data' / 'processed', 
    'embeddings': PROJECT_ROOT / 'data' / 'embeddings',
    'logs': PROJECT_ROOT / 'logs'
}

# 确保所有目录存在
for dir_path in DATA_DIRS.values():
    dir_path.mkdir(parents=True, exist_ok=True)

# 导出路径字符串（用于向后兼容）
RAW_DATA_DIR = str(DATA_DIRS['raw'])
PROCESSED_DIR = str(DATA_DIRS['processed'])
EMBEDDINGS_DIR = str(DATA_DIRS['embeddings'])
LOGS_DIR = str(DATA_DIRS['logs'])

# 支持的文件格式
SUPPORTED_FORMATS = ('.pdf', '.docx', '.txt', '.md', '.mp3', '.wav')

def get_data_dir(dir_name: str) -> Path:
    """获取数据目录路径"""
    if dir_name not in DATA_DIRS:
        raise ValueError(f"Unknown directory: {dir_name}. Available: {list(DATA_DIRS.keys())}")
    return DATA_DIRS[dir_name]

def ensure_data_dirs():
    """确保所有数据目录存在"""
    for dir_path in DATA_DIRS.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return True
