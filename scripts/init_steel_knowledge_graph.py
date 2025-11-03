#!/usr/bin/env python3
"""
初始化钢铁领域知识图谱（基于标准本体）

从已上传的文档构建知识图谱，并自动加载钢铁行业标准本体作为基准。
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge_graph.builder import SteelKnowledgeGraphBuilder
from src.data_processing.loader import DataLoader
from config.logging_config import setup_logging


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting steel knowledge graph initialization with standard ontology")

    try:
        print("=" * 60)
        print("🚀 初始化知识图谱（基于标准本体）")
        print("=" * 60)
        
        # 1. 创建知识图谱构建器（自动加载标准本体）
        print("\n📚 加载钢铁行业标准本体...")
        builder = SteelKnowledgeGraphBuilder()
        logger.info("Standard ontology loaded successfully")
        
        # 2. 从文档构建知识图谱
        print("\n📄 从已上传的文档中提取实体和关系...")
        data_loader = DataLoader()
        raw_dir = Path("./data/raw")
        
        if not raw_dir.exists() or not list(raw_dir.glob("*")):
            print("⚠️  未找到已上传的文档，仅保存标准本体")
            logger.warning("No documents found in data/raw, only saving standard ontology")
        else:
            documents = []
            for file_path in raw_dir.glob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    try:
                        print(f"  - 处理文件: {file_path.name}")
                        text = data_loader.load(str(file_path))
                        if text:
                            documents.append({
                                'text': text,
                                'source': file_path.name
                            })
                    except Exception as e:
                        logger.warning(f"Skipped file {file_path.name}: {e}")
            
            if documents:
                print(f"\n✅ 成功加载 {len(documents)} 个文档")
                print("\n🔍 提取实体和关系...")
                builder.build_from_documents(documents)
                logger.info(f"Built knowledge graph from {len(documents)} documents")
        
        # 3. 保存知识图谱
        output_file = "./data/knowledge_graph.json"
        print(f"\n💾 保存知识图谱到: {output_file}")
        builder.save_to_file(output_file)
        logger.info(f"Knowledge graph saved to {output_file}")
        
        # 4. 显示统计信息
        stats = builder.get_statistics()
        print("\n" + "=" * 60)
        print("📊 知识图谱统计信息")
        print("=" * 60)
        print(f"总实体数: {stats['total_entities']}")
        print(f"总关系数: {stats['total_relations']}")
        print(f"平均置信度: {stats['average_confidence']:.2%}")
        
        print("\n实体类型分布:")
        for entity_type, count in sorted(
            stats['entity_type_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if count > 0:
                print(f"  - {entity_type}: {count}")
        
        print("\n关系类型分布:")
        for relation_type, count in sorted(
            stats['relation_type_counts'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if count > 0:
                print(f"  - {relation_type}: {count}")
        
        logger.info(f"Knowledge graph statistics: {stats}")
        
        print("\n" + "=" * 60)
        print("✅ 知识图谱构建完成！")
        print("=" * 60)
        print("\n📌 下一步:")
        print("  1. 访问 Web 界面: http://localhost:3000/dashboard/knowledge-graph")
        print("  2. 选择核心实体（如'碳素结构钢'）")
        print("  3. 切换到蛛网视图查看关联关系")
        print()
        
    except Exception as e:
        logger.error(f"Failed to build knowledge graph: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
