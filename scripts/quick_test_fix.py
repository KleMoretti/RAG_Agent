#!/usr/bin/env python3
"""
快速测试修复效果

测试RAG检索是否能正确获取完整chunk内容
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder
from src.retrieval.vector_store import VectorStore


def test_retrieval():
    """测试检索功能"""
    print("=" * 60)
    print("RAG修复效果测试")
    print("=" * 60)
    
    # 初始化组件
    print("\n[1] 初始化组件...")
    preprocessor = Preprocessor()
    embedder = Embedder(model_name="all-MiniLM-L6-v2")
    store = VectorStore(
        dim=embedder.dim,
        index_path=Path("data/embeddings/knowledge_base.faiss"),
        metadata_path=Path("data/embeddings/knowledge_base.meta.jsonl"),
        normalize=False
    )
    
    try:
        store.load()
        print(f"   ✅ 向量库已加载: {store.size} 个向量")
    except Exception as e:
        print(f"   ❌ 向量库加载失败: {e}")
        return False
    
    # 测试查询
    print("\n[2] 执行测试查询...")
    test_query = "硅钢生产工艺"
    
    cleaned_query = preprocessor.clean_text(test_query)
    query_vec = embedder.encode([cleaned_query], normalize=True)[0]
    hits = store.search(query_vec, top_k=3, include_metadata=True)
    
    if not hits:
        print("   ⚠️  未找到相关结果")
        return False
    
    print(f"   找到 {len(hits)} 个相关结果\n")
    
    # 检查metadata格式
    print("[3] 检查metadata格式...")
    has_file_id = 0
    has_full_content = 0
    
    for i, hit in enumerate(hits, 1):
        print(f"\n   结果 {i}:")
        print(f"   - file_id: {'✅ ' + hit.get('file_id', 'N/A') if 'file_id' in hit else '❌ 缺失'}")
        print(f"   - file_name: {'✅ ' + hit.get('file_name', 'N/A') if 'file_name' in hit else '❌ 缺失'}")
        print(f"   - chunk_id: {hit.get('chunk_id', 'N/A')}")
        print(f"   - score: {hit.get('score', 0):.4f}")
        
        preview = hit.get('preview', '')
        print(f"   - preview长度: {len(preview)} 字符")
        print(f"   - preview内容: {preview[:100]}...")
        
        if 'file_id' in hit:
            has_file_id += 1
        
        if len(preview) > 50:
            has_full_content += 1
    
    # 评估结果
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    
    all_success = True
    
    if has_file_id == len(hits):
        print("✅ 所有结果都包含file_id字段")
    else:
        print(f"⚠️  只有 {has_file_id}/{len(hits)} 个结果包含file_id字段")
        print("   建议：运行 python scripts/clear_rag_data.py 清理后重新上传")
        all_success = False
    
    if has_full_content == len(hits):
        print("✅ 所有结果都有完整内容（>50字符）")
    else:
        print(f"⚠️  只有 {has_full_content}/{len(hits)} 个结果有完整内容")
        all_success = False
    
    if all_success:
        print("\n🎉 修复成功！系统可以正常工作")
    else:
        print("\n⚠️  仍存在问题，建议重新索引")
    
    return all_success


def main():
    try:
        success = test_retrieval()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

