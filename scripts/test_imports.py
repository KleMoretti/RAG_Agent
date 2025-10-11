#!/usr/bin/env python3
"""
测试脚本 - 验证导入和路径配置是否正确

⚠️ 注意: 旧脚本已移至 deprecated/ 目录，推荐使用新的 CLI 工具
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试导入...")
    
    try:
        from scripts.paths import DATA_DIRS, ensure_data_dirs
        print("✅ paths.py 导入成功")
        
        # 测试新的 CLI 工具（推荐）
        print("\n📝 新工具导入测试:")
        try:
            import importlib.util
            
            # 测试 rag_cli.py
            rag_cli_path = Path(__file__).parent / "rag_cli.py"
            if rag_cli_path.exists():
                print("✅ rag_cli.py 存在")
            else:
                print("❌ rag_cli.py 不存在")
            
            # 测试 db_migrate.py
            db_migrate_path = Path(__file__).parent / "db_migrate.py"
            if db_migrate_path.exists():
                print("✅ db_migrate.py 存在")
            else:
                print("❌ db_migrate.py 不存在")
        except Exception as e:
            print(f"⚠️  新工具检查失败: {e}")
        
        # 测试废弃脚本（仅用于向后兼容测试）
        print("\n📝 废弃脚本导入测试 (deprecated):")
        try:
            from scripts.deprecated.build_rag_system import AcademicRAGBuilder
            print("✅ deprecated/build_rag_system.py 导入成功")
        except ImportError:
            print("⚠️  deprecated/build_rag_system.py 导入失败（已废弃）")
        
        try:
            from scripts.deprecated.data_ingestion import DataIngestion
            print("✅ deprecated/data_ingestion.py 导入成功")
        except ImportError:
            print("⚠️  deprecated/data_ingestion.py 导入失败（已废弃）")
        
        from config.logging_config import setup_logging
        print("\n✅ logging_config 导入成功")
        
        from src.data_processing.loader import DataLoader
        from src.data_processing.preprocessor import Preprocessor
        from src.data_processing.embedder import Embedder
        print("✅ 数据处理模块导入成功")
        
        from src.retrieval.vector_store import VectorStore
        from src.retrieval.indexer import Indexer
        print("✅ 检索模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_paths():
    """测试路径配置"""
    print("\n🔍 测试路径配置...")
    
    try:
        from scripts.paths import DATA_DIRS, ensure_data_dirs
        
        # 确保目录存在
        ensure_data_dirs()
        
        print("✅ 数据目录配置:")
        for name, path in DATA_DIRS.items():
            exists = "✅" if path.exists() else "❌"
            print(f"   {name}: {path} {exists}")
        
        return True
        
    except Exception as e:
        print(f"❌ 路径配置失败: {e}")
        return False

def test_rag_builder():
    """测试RAG构建器初始化（使用新的 CLI 工具）"""
    print("\n🔍 测试RAG系统...")
    
    try:
        # 推荐使用新的 RAG CLI 工具
        print("📝 推荐使用: python scripts/rag_cli.py --help")
        
        # 测试旧的构建器（从 deprecated 导入）
        try:
            from scripts.deprecated.build_rag_system import AcademicRAGBuilder
            
            # 创建构建器实例
            builder = AcademicRAGBuilder()
            
            # 检查路径
            print(f"✅ 原始数据目录: {builder.raw_data_dir}")
            print(f"✅ 处理后目录: {builder.processed_dir}")
            print(f"✅ 嵌入目录: {builder.embeddings_dir}")
            
            # 检查系统信息
            info = builder.get_system_info()
            print(f"✅ 向量库大小: {info['vector_store_size']}")
            print(f"✅ 嵌入维度: {info['embedding_dimension']}")
            
            print("\n⚠️  注意: 此功能已废弃，请使用 rag_cli.py")
        except ImportError as e:
            print(f"⚠️  旧构建器不可用（已废弃）: {e}")
            print("   请使用: python scripts/rag_cli.py build")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试RAG系统配置...")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_imports,
        test_paths,
        test_rag_builder
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！RAG系统配置正确。")
        print("\n📝 下一步（推荐使用新的 CLI 工具）:")
        print("1. 将文档文件放入 data/raw/ 目录")
        print("2. 构建索引: python scripts/rag_cli.py build --rebuild")
        print("3. 搜索文档: python scripts/rag_cli.py search --interactive")
        print("4. 查看帮助: python scripts/rag_cli.py --help")
        print("\n⚠️  旧脚本已移至 scripts/deprecated/ 目录")
    else:
        print("❌ 部分测试失败，请检查配置。")

if __name__ == "__main__":
    main()
