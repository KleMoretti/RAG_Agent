#!/usr/bin/env python3
"""
RAG系统使用示例
展示如何使用构建好的RAG系统进行文档检索和问答
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 现在可以直接导入
from scripts.build_rag_system import AcademicRAGBuilder
from config.logging_config import setup_logging
from scripts.paths import ensure_data_dirs


def demo_rag_usage():
    setup_logging(level="INFO")
    print("🔍 RAG系统使用示例")
    print("=" * 50)

    print("1. 加载RAG系统...")
    try:
        # 确保数据目录存在
        ensure_data_dirs()
        
        # 使用默认路径（相对于项目根目录）
        builder = AcademicRAGBuilder()
        info = builder.get_system_info()
        print(f"   ✅ 向量库大小: {info['vector_store_size']} 个块")
        print(f"   ✅ 嵌入维度: {info['embedding_dimension']}")
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        print("   请先运行: python scripts/build_rag_system.py")
        return

    # 若向量库为空，直接给出指引并退出，避免后续 WARNING
    if info.get("vector_store_size", 0) == 0:
        print("   ❌ 向量库为空，请先将文件放入 `data/raw` 并运行 `python scripts/build_rag_system.py` 构建。")
        return

    # 2. 示例查询...
    print("\n2. 示例查询...")
    test_queries = ["摘要", "研究方法", "实验结果", "结论", "机器学习", "深度学习"]
    for query in test_queries:
        print(f"\n🔍 查询: '{query}'")
        results = builder.search(query, top_k=3)
        if not results:
            print("   📭 未找到相关结果")
            continue
        for i, result in enumerate(results, 1):
            file_name = Path(result['file']).name
            print(f"   {i}. 📄 {file_name} (块 {result['chunk_id']})")
            print(f"      🎯 相似度: {result['score']:.4f}")
            print(f"      📝 预览: {result['preview']}...")
            print()
    
    # 3. 高级搜索示例
    print("\n3. 高级搜索示例...")
    
    # 搜索特定文件类型
    print("\n🔍 搜索PDF文件中的内容...")
    pdf_results = builder.search("算法", top_k=5)
    pdf_files = set()
    for result in pdf_results:
        if result['file'].endswith('.pdf'):
            pdf_files.add(Path(result['file']).name)
    
    if pdf_files:
        print(f"   找到 {len(pdf_files)} 个相关PDF文件:")
        for file in list(pdf_files)[:3]:  # 只显示前3个
            print(f"   - {file}")
    
    # 4. 元数据分析
    print("\n4. 元数据分析...")
    metadata_count = {}
    for meta in builder.store.iter_metadata():
        file_ext = Path(meta['file']).suffix.lower()
        metadata_count[file_ext] = metadata_count.get(file_ext, 0) + 1
    
    print("   文件类型分布:")
    for ext, count in metadata_count.items():
        print(f"   - {ext}: {count} 个块")
    
    # 5. 导出元数据（可选）
    print("\n5. 导出元数据...")
    try:
        export_file = builder.export_metadata("rag_metadata_export.json")
        print(f"   ✅ 元数据已导出到: {export_file}")
    except Exception as e:
        print(f"   ❌ 导出失败: {e}")


def interactive_search():
    """交互式搜索模式"""
    print("\n🎯 交互式搜索模式")
    print("输入查询词进行搜索，输入 'quit' 退出")
    print("-" * 50)
    
    try:
        # 确保数据目录存在
        ensure_data_dirs()
        
        # 使用默认路径（相对于项目根目录）
        builder = AcademicRAGBuilder()
        
        if builder.store.size == 0:
            print("❌ 向量库为空，请先构建RAG系统")
            return
            
    except Exception as e:
        print(f"❌ 加载RAG系统失败: {e}")
        return
    
    while True:
        try:
            query = input("\n🔍 请输入查询词: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 再见！")
                break
                
            if not query:
                continue
                
            print(f"\n搜索: '{query}'")
            results = builder.search(query, top_k=5)
            
            if not results:
                print("📭 未找到相关结果")
                continue
                
            print(f"找到 {len(results)} 个相关结果:")
            for i, result in enumerate(results, 1):
                file_name = Path(result['file']).name
                print(f"\n{i}. 📄 {file_name}")
                print(f"   🎯 相似度: {result['score']:.4f}")
                print(f"   📝 内容预览:")
                print(f"   {result['preview']}...")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 搜索出错: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG系统使用示例")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="启动交互式搜索模式")
    parser.add_argument("--demo", "-d", action="store_true", default=True,
                       help="运行演示模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_search()
    else:
        demo_rag_usage()


if __name__ == "__main__":
    main()
