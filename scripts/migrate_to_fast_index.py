"""
将现有FAISS索引迁移到优化的快速索引。

使用方法：
    python scripts/migrate_to_fast_index.py

功能：
1. 读取现有的Flat索引
2. 自动判断是否需要升级为IVF索引
3. 迁移所有向量和元数据
4. 备份原索引
5. 性能对比测试
"""
import sys
from pathlib import Path
import time
import shutil

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retrieval.vector_store import VectorStore
from src.retrieval.vector_store_fast import VectorStoreFast
from src.data_processing.embedder import Embedder
from config.settings import get_settings


def migrate_index():
    """迁移索引到快速版本"""
    settings = get_settings()
    
    # 路径配置
    old_index_path = Path("data/embeddings/index.faiss")
    old_meta_path = Path("data/embeddings/index.meta.jsonl")
    new_index_path = Path("data/embeddings/index_fast.faiss")
    new_meta_path = Path("data/embeddings/index_fast.meta.jsonl")
    backup_dir = Path("data/embeddings/backup")
    
    print("=" * 60)
    print("🚀 FAISS索引迁移工具 - 升级到快速索引")
    print("=" * 60)
    
    # 1. 检查旧索引是否存在
    if not old_index_path.exists():
        print(f"❌ 未找到旧索引: {old_index_path}")
        print("   请先运行 scripts/build_rag_system.py 构建索引")
        return
    
    print(f"\n📂 旧索引路径: {old_index_path}")
    print(f"📂 新索引路径: {new_index_path}")
    
    # 2. 加载旧索引
    print("\n⏳ 加载旧索引...")
    start = time.time()
    old_store = VectorStore(
        dim=384,  # all-MiniLM-L6-v2的维度
        index_path=old_index_path,
        metadata_path=old_meta_path,
        normalize=False,
    )
    load_time = time.time() - start
    print(f"✅ 加载完成，耗时 {load_time:.2f}s")
    print(f"   向量数量: {old_store.size}")
    print(f"   索引类型: IndexFlatIP (暴力检索)")
    
    if old_store.size == 0:
        print("❌ 索引为空，无需迁移")
        return
    
    # 3. 创建快速索引
    print("\n⏳ 创建快速索引...")
    start = time.time()
    new_store = VectorStoreFast(
        dim=384,
        index_path=new_index_path,
        metadata_path=new_meta_path,
        normalize=False,
        use_ivf=None,  # 自动判断
        nlist=100,  # IVF聚类数
        m=8,  # PQ子向量数
        nbits=8,  # 每个子向量8位
    )
    
    # 4. 迁移所有向量和元数据
    print(f"\n⏳ 迁移 {old_store.size} 个向量...")
    
    # 从旧索引提取所有向量
    import faiss
    import numpy as np
    vectors = faiss.rev_swig_ptr(old_store._index.get_xb(), old_store.size * 384)
    vectors = vectors.reshape(old_store.size, 384).astype(np.float32)
    
    # 提取所有元数据
    metadatas = list(old_store.iter_metadata())
    
    # 添加到新索引（会自动触发IVF升级）
    batch_size = 1000
    for i in range(0, len(vectors), batch_size):
        end = min(i + batch_size, len(vectors))
        batch_vectors = vectors[i:end]
        batch_meta = metadatas[i:end]
        new_store.add(batch_vectors, batch_meta)
        print(f"   进度: {end}/{len(vectors)} ({end/len(vectors)*100:.1f}%)")
    
    migrate_time = time.time() - start
    print(f"✅ 迁移完成，耗时 {migrate_time:.2f}s")
    print(f"   新索引类型: {new_store.index_type}")
    
    # 5. 保存新索引
    print("\n⏳ 保存新索引...")
    start = time.time()
    new_store.save()
    save_time = time.time() - start
    print(f"✅ 保存完成，耗时 {save_time:.2f}s")
    
    # 6. 性能对比测试
    print("\n" + "=" * 60)
    print("📊 性能对比测试")
    print("=" * 60)
    
    embedder = Embedder("all-MiniLM-L6-v2")
    test_queries = [
        "钢铁生产流程",
        "高炉温度控制",
        "环保排放标准",
        "设备故障诊断",
        "市场价格分析",
    ]
    
    print("\n测试查询:")
    for i, q in enumerate(test_queries, 1):
        print(f"  {i}. {q}")
    
    # 测试旧索引
    print(f"\n⏱️  旧索引 (Flat) 性能测试...")
    old_times = []
    for query in test_queries:
        vec = embedder.encode([query], normalize=True)[0]
        start = time.perf_counter()
        old_store.search(vec, top_k=5)
        elapsed = (time.perf_counter() - start) * 1000
        old_times.append(elapsed)
    
    avg_old = sum(old_times) / len(old_times)
    print(f"   平均耗时: {avg_old:.2f}ms")
    print(f"   详细: {[f'{t:.2f}ms' for t in old_times]}")
    
    # 测试新索引
    print(f"\n⏱️  新索引 ({new_store.index_type}) 性能测试...")
    new_times = []
    for query in test_queries:
        vec = embedder.encode([query], normalize=True)[0]
        start = time.perf_counter()
        new_store.search(vec, top_k=5, nprobe=10)
        elapsed = (time.perf_counter() - start) * 1000
        new_times.append(elapsed)
    
    avg_new = sum(new_times) / len(new_times)
    print(f"   平均耗时: {avg_new:.2f}ms")
    print(f"   详细: {[f'{t:.2f}ms' for t in new_times]}")
    
    # 对比
    speedup = avg_old / avg_new if avg_new > 0 else 1.0
    improvement = ((avg_old - avg_new) / avg_old * 100) if avg_old > 0 else 0
    
    print(f"\n🎉 性能提升:")
    print(f"   加速比: {speedup:.2f}x")
    print(f"   时间减少: {improvement:.1f}%")
    
    # 7. 备份建议
    print("\n" + "=" * 60)
    print("📦 后续步骤")
    print("=" * 60)
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n✅ 迁移成功！新索引已保存到: {new_index_path}")
    print(f"\n💡 建议:")
    print(f"   1. 备份旧索引:")
    print(f"      mv {old_index_path} {backup_dir}/")
    print(f"      mv {old_meta_path} {backup_dir}/")
    print(f"   2. 使用新索引:")
    print(f"      mv {new_index_path} {old_index_path}")
    print(f"      mv {new_meta_path} {old_meta_path}")
    print(f"   3. 更新代码使用 VectorStoreFast 和 SearcherFast")
    
    print("\n" + "=" * 60)


def auto_migrate():
    """自动迁移（包含备份和替换）"""
    settings = get_settings()
    
    old_index_path = Path("data/embeddings/index.faiss")
    old_meta_path = Path("data/embeddings/index.meta.jsonl")
    backup_dir = Path("data/embeddings/backup")
    
    print("🔄 自动迁移模式（包含备份和替换）")
    
    # 备份
    if old_index_path.exists():
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_index = backup_dir / f"index_{timestamp}.faiss"
        backup_meta = backup_dir / f"index_{timestamp}.meta.jsonl"
        
        print(f"📦 备份旧索引到: {backup_dir}/")
        shutil.copy2(old_index_path, backup_index)
        shutil.copy2(old_meta_path, backup_meta)
        print("✅ 备份完成")
    
    # 执行迁移
    migrate_index()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="迁移FAISS索引到快速版本")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="自动模式：自动备份、迁移和替换",
    )
    
    args = parser.parse_args()
    
    try:
        if args.auto:
            auto_migrate()
        else:
            migrate_index()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

