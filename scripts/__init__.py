# scripts package
"""
⚠️ 注意: build_rag_system 和 data_ingestion 已废弃，移至 deprecated/ 目录
推荐使用: rag_cli.py 和 db_migrate.py

如需使用旧脚本，请从 deprecated 目录导入：
    from scripts.deprecated.build_rag_system import AcademicRAGBuilder
"""

from .paths import DATA_DIRS, ensure_data_dirs

# 为了向后兼容，可选择从 deprecated 导入（不推荐）
try:
    from .deprecated.build_rag_system import AcademicRAGBuilder
    from .deprecated.data_ingestion import DataIngestion
    __all__ = ["AcademicRAGBuilder", "DataIngestion", "DATA_DIRS", "ensure_data_dirs"]
except ImportError:
    # 如果导入失败，只导出路径配置
    __all__ = ["DATA_DIRS", "ensure_data_dirs"]