#!/usr/bin/env python3
"""
初始化钢铁领域知识图谱

从已处理的文档中构建钢铁领域知识图谱。
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge_graph.manager import SteelKnowledgeGraphManager
from config.logging_config import setup_logging


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting steel knowledge graph initialization")

    try:
        # 创建知识图谱管理器
        kg_manager = SteelKnowledgeGraphManager()

        # 从已处理的文件中构建知识图谱
        logger.info("Building knowledge graph from processed files")
        kg = kg_manager.build_from_processed_files()

        # 获取统计信息
        stats = kg_manager.get_statistics()
        logger.info(f"Knowledge graph statistics: {stats}")

        # 测试查询功能
        logger.info("Testing knowledge graph queries")

        # 搜索钢种
        steel_grades = kg_manager.search_entities("Q235", entity_types=["steel_grade"])
        logger.info(f"Found {len(steel_grades['entities'])} steel grades matching 'Q235'")

        # 搜索性能
        properties = kg_manager.search_entities("抗拉强度", entity_types=["material_property"])
        logger.info(f"Found {len(properties['entities'])} properties matching '抗拉强度'")

        # 搜索工艺
        processes = kg_manager.search_entities("热轧", entity_types=["process"])
        logger.info(f"Found {len(processes['entities'])} processes matching '热轧'")

        logger.info("Steel knowledge graph initialization completed successfully")

    except Exception as e:
        logger.error(f"Error initializing steel knowledge graph: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
