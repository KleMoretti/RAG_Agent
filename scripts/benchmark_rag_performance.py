"""
RAG检索性能基准测试工具。

测试场景：
1. 单次查询性能（冷启动 vs 热启动）
2. 批量查询性能
3. 并发查询性能
4. 缓存命中率
5. 不同索引类型对比（Flat vs IVF）
"""
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import statistics

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retrieval.vector_store import VectorStore
from src.retrieval.vector_store_fast import VectorStoreFast
from src.retrieval.searcher import Searcher
from src.retrieval.searcher_fast import SearcherFast
from src.data_processing.embedder import Embedder
from config.settings import get_settings


class RAGBenchmark:
    """RAG性能基准测试"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedder = Embedder("all-MiniLM-L6-v2")
        
        # 测试查询集
        self.test_queries = [
            "钢铁生产流程",
            "高炉温度控制方法",
            "环保排放标准要求",
            "设备故障诊断步骤",
            "市场价格分析报告",
            "质量检测标准",
            "原料采购策略",
            "生产成本优化",
            "安全操作规程",
            "技术创新方案",
        ]
        
    def load_stores(self):
        """加载不同类型的索引"""
        index_path = Path("data/embeddings/index.faiss")
        meta_path = Path("data/embeddings/index.meta.jsonl")
        
        if not index_path.exists():
            print("❌ 索引不存在，请先运行 scripts/build_rag_system.py")
            return None, None
        
        print("📂 加载索引...")
        
        # 原始Flat索引
        print("   - 加载 Flat 索引...")
        flat_store = VectorStore(
            dim=384,
            index_path=index_path,
            metadata_path=meta_path,
            normalize=False,
        )
        flat_searcher = Searcher(self.embedder, flat_store)
        
        # 快速索引（直接使用现有的 VectorStoreFast）
        print("   - 使用现有索引作为 Fast 索引...")
        fast_store = VectorStoreFast(
            dim=384,
            index_path=index_path,
            metadata_path=meta_path,
            normalize=False,
            use_ivf=None,  # 自动判断
        )
        fast_searcher = SearcherFast(
            self.embedder,
            fast_store,
            enable_cache=True,
            cache_size=1000,
        )
        
        print(f"✅ 索引加载完成")
        print(f"   Flat索引: {flat_store.size} 个向量")
        print(f"   Fast索引: {fast_store.size} 个向量, 类型={fast_store.index_type}")
        
        return flat_searcher, fast_searcher
    
    def benchmark_single_query(
        self,
        searcher: Searcher | SearcherFast,
        name: str,
        iterations: int = 10,
    ) -> Dict[str, Any]:
        """单次查询性能测试"""
        print(f"\n{'='*60}")
        print(f"📊 {name} - 单次查询性能测试")
        print(f"{'='*60}")
        
        times = []
        query = self.test_queries[0]
        
        # 冷启动
        print(f"\n⏱️  冷启动测试 (查询: '{query}')")
        start = time.perf_counter()
        results = searcher.search(query, top_k=5)
        cold_time = (time.perf_counter() - start) * 1000
        print(f"   耗时: {cold_time:.2f}ms")
        print(f"   结果数: {len(results)}")
        
        # 热启动（重复查询，测试缓存）
        print(f"\n⏱️  热启动测试 (重复 {iterations} 次)")
        for i in range(iterations):
            start = time.perf_counter()
            searcher.search(query, top_k=5)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        
        print(f"   平均: {avg_time:.2f}ms")
        print(f"   中位数: {median_time:.2f}ms")
        print(f"   最小: {min_time:.2f}ms")
        print(f"   最大: {max_time:.2f}ms")
        print(f"   标准差: {std_time:.2f}ms")
        
        return {
            "name": name,
            "cold_time_ms": cold_time,
            "avg_time_ms": avg_time,
            "median_time_ms": median_time,
            "min_time_ms": min_time,
            "max_time_ms": max_time,
            "std_time_ms": std_time,
        }
    
    def benchmark_batch_query(
        self,
        searcher: Searcher | SearcherFast,
        name: str,
    ) -> Dict[str, Any]:
        """批量查询性能测试"""
        print(f"\n{'='*60}")
        print(f"📊 {name} - 批量查询性能测试")
        print(f"{'='*60}")
        
        print(f"\n⏱️  批量查询 {len(self.test_queries)} 个问题")
        
        start = time.perf_counter()
        results = searcher.batch_search(self.test_queries, top_k=5)
        total_time = (time.perf_counter() - start) * 1000
        
        avg_per_query = total_time / len(self.test_queries)
        
        print(f"   总耗时: {total_time:.2f}ms")
        print(f"   平均每查询: {avg_per_query:.2f}ms")
        print(f"   查询数: {len(results)}")
        
        return {
            "name": name,
            "total_time_ms": total_time,
            "avg_per_query_ms": avg_per_query,
            "num_queries": len(self.test_queries),
        }
    
    def benchmark_cache_effectiveness(
        self,
        searcher: SearcherFast,
        name: str,
    ) -> Dict[str, Any]:
        """缓存有效性测试"""
        print(f"\n{'='*60}")
        print(f"📊 {name} - 缓存有效性测试")
        print(f"{'='*60}")
        
        # 清空缓存
        searcher.clear_cache()
        
        # 第一轮：所有查询（无缓存）
        print("\n⏱️  第一轮：无缓存")
        start = time.perf_counter()
        for q in self.test_queries:
            searcher.search(q, top_k=5)
        round1_time = (time.perf_counter() - start) * 1000
        print(f"   耗时: {round1_time:.2f}ms")
        
        # 第二轮：重复查询（全缓存）
        print("\n⏱️  第二轮：全缓存命中")
        start = time.perf_counter()
        for q in self.test_queries:
            searcher.search(q, top_k=5)
        round2_time = (time.perf_counter() - start) * 1000
        print(f"   耗时: {round2_time:.2f}ms")
        
        # 第三轮：混合查询（50%缓存命中）
        print("\n⏱️  第三轮：50%缓存命中")
        mixed_queries = self.test_queries + [q + "的详细信息" for q in self.test_queries[:5]]
        start = time.perf_counter()
        for q in mixed_queries:
            searcher.search(q, top_k=5)
        round3_time = (time.perf_counter() - start) * 1000
        print(f"   耗时: {round3_time:.2f}ms")
        
        # 统计
        stats = searcher.get_stats()
        print(f"\n📈 缓存统计:")
        print(f"   总查询数: {stats['total_queries']}")
        print(f"   缓存命中: {stats['cache_hits']}")
        print(f"   命中率: {stats['cache_hit_rate']}")
        
        speedup = round1_time / round2_time if round2_time > 0 else 1.0
        print(f"\n🎉 缓存加速比: {speedup:.2f}x")
        
        return {
            "name": name,
            "no_cache_ms": round1_time,
            "full_cache_ms": round2_time,
            "mixed_cache_ms": round3_time,
            "speedup": speedup,
            "stats": stats,
        }
    
    def run_all_benchmarks(self):
        """运行所有基准测试"""
        print("🚀 RAG检索性能基准测试")
        print("=" * 60)
        
        # 加载索引
        flat_searcher, fast_searcher = self.load_stores()
        if not flat_searcher or not fast_searcher:
            return
        
        results = {}
        
        # 1. 单次查询性能
        results["flat_single"] = self.benchmark_single_query(
            flat_searcher,
            "Flat索引",
            iterations=10,
        )
        
        results["fast_single"] = self.benchmark_single_query(
            fast_searcher,
            "Fast索引+缓存",
            iterations=10,
        )
        
        # 2. 批量查询性能
        results["flat_batch"] = self.benchmark_batch_query(
            flat_searcher,
            "Flat索引",
        )
        
        results["fast_batch"] = self.benchmark_batch_query(
            fast_searcher,
            "Fast索引+缓存",
        )
        
        # 3. 缓存有效性（仅Fast）
        if isinstance(fast_searcher, SearcherFast):
            results["cache"] = self.benchmark_cache_effectiveness(
                fast_searcher,
                "Fast索引",
            )
        
        # 4. 总结对比
        self.print_summary(results)
    
    def print_summary(self, results: Dict[str, Any]):
        """打印性能对比总结"""
        print("\n" + "=" * 60)
        print("📊 性能对比总结")
        print("=" * 60)
        
        # 单次查询对比
        flat_avg = results["flat_single"]["avg_time_ms"]
        fast_avg = results["fast_single"]["avg_time_ms"]
        single_speedup = flat_avg / fast_avg if fast_avg > 0 else 1.0
        
        print(f"\n🔍 单次查询性能:")
        print(f"   Flat索引: {flat_avg:.2f}ms")
        print(f"   Fast索引: {fast_avg:.2f}ms")
        print(f"   加速比: {single_speedup:.2f}x")
        print(f"   提升: {(flat_avg - fast_avg) / flat_avg * 100:.1f}%")
        
        # 批量查询对比
        flat_batch = results["flat_batch"]["avg_per_query_ms"]
        fast_batch = results["fast_batch"]["avg_per_query_ms"]
        batch_speedup = flat_batch / fast_batch if fast_batch > 0 else 1.0
        
        print(f"\n📦 批量查询性能:")
        print(f"   Flat索引: {flat_batch:.2f}ms/查询")
        print(f"   Fast索引: {fast_batch:.2f}ms/查询")
        print(f"   加速比: {batch_speedup:.2f}x")
        print(f"   提升: {(flat_batch - fast_batch) / flat_batch * 100:.1f}%")
        
        # 缓存效果
        if "cache" in results:
            cache_speedup = results["cache"]["speedup"]
            print(f"\n💾 缓存效果:")
            print(f"   无缓存: {results['cache']['no_cache_ms']:.2f}ms")
            print(f"   全缓存: {results['cache']['full_cache_ms']:.2f}ms")
            print(f"   缓存加速比: {cache_speedup:.2f}x")
        
        print("\n" + "=" * 60)
        print("✅ 基准测试完成")
        print("=" * 60)


if __name__ == "__main__":
    benchmark = RAGBenchmark()
    try:
        benchmark.run_all_benchmarks()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

