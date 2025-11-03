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
    # 知识库路径（系统知识库）
    'knowledge_base/raw': PROJECT_ROOT / 'data' / 'knowledge_base' / 'raw',
    'knowledge_base/processed': PROJECT_ROOT / 'data' / 'knowledge_base' / 'processed',
    
    # 用户上传路径
    'user_uploads/raw': PROJECT_ROOT / 'data' / 'user_uploads' / 'raw',
    'user_uploads/processed': PROJECT_ROOT / 'data' / 'user_uploads' / 'processed',
    
    # 向量索引路径
    'embeddings': PROJECT_ROOT / 'data' / 'embeddings',
    
    # 日志路径
    'logs': PROJECT_ROOT / 'logs',
    
    # 兼容性别名（推荐使用上面的完整路径）
    'raw': PROJECT_ROOT / 'data' / 'knowledge_base' / 'raw',  # 默认指向知识库
    'processed': PROJECT_ROOT / 'data' / 'knowledge_base' / 'processed',
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
    """获取数据目录路径
    
    Args:
        dir_name: 目录名称，支持:
            - 'knowledge_base/raw': 知识库原始文件
            - 'knowledge_base/processed': 知识库处理后文件
            - 'user_uploads/raw': 用户上传原始文件
            - 'user_uploads/processed': 用户上传处理后文件
            - 'embeddings': 向量索引
            - 'raw': (兼容) 默认知识库原始文件
            - 'processed': (兼容) 默认知识库处理后文件
    
    Returns:
        Path: 目录路径
    """
    if dir_name not in DATA_DIRS:
        raise ValueError(f"Unknown directory: {dir_name}. Available: {list(DATA_DIRS.keys())}")
    return DATA_DIRS[dir_name]

def ensure_data_dirs():
    """确保所有数据目录存在"""
    for dir_path in DATA_DIRS.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    return True

def get_file_source(file_path: Path) -> str:
    """判断文件来源
    
    Args:
        file_path: 文件路径
    
    Returns:
        str: 'knowledge_base' | 'user_uploads' | 'unknown'
    """
    file_str = str(file_path)
    if 'knowledge_base' in file_str:
        return 'knowledge_base'
    elif 'user_uploads' in file_str:
        return 'user_uploads'
    else:
        return 'unknown'

def get_processed_dir_for_file(file_path: Path) -> Path:
    """根据文件来源获取对应的处理后目录
    
    Args:
        file_path: 原始文件路径
    
    Returns:
        Path: 对应的处理后目录
    """
    source = get_file_source(file_path)
    if source == 'knowledge_base':
        return DATA_DIRS['knowledge_base/processed']
    elif source == 'user_uploads':
        return DATA_DIRS['user_uploads/processed']
    else:
        # 默认使用知识库
        return DATA_DIRS['knowledge_base/processed']
