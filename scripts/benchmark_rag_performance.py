"""
RAG检索质量评估工具。

测试场景：
1. 检索准确性测试（相关度评分分析）
2. 检索召回率测试（期望文档是否被召回）
3. 文档覆盖率测试（知识库利用率）
4. 检索结果多样性测试
5. 分块质量评估（分块大小、重叠率）

使用方法：
    python scripts/benchmark_rag_performance.py

自定义测试查询：
    如果您的知识库专注于特定领域，请修改 RAGQualityEvaluator.__init__() 中的 test_queries 列表。
    
    示例（硅钢领域）：
        {
            "query": "取向硅钢的磁性能如何？",
            "expected_topics": ["取向硅钢", "磁性能", "铁损"],
            "min_relevance": 0.6,
            "category": "材料性能"
        }

注意事项：
    - 测试查询应与您的知识库内容匹配
    - 相关度阈值建议设置在 0.5-0.7 之间
    - 主题覆盖率为 0% 说明查询与文档内容不匹配，需要调整查询
"""
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
import statistics
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.retrieval.vector_store_fast import VectorStoreFast
from src.retrieval.searcher_fast import SearcherFast
from src.data_processing.embedder import Embedder
from config.settings import get_settings


class RAGQualityEvaluator:
    """RAG检索质量评估器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedder = Embedder("all-MiniLM-L6-v2")
        
        # 测试查询集（包含查询、预期主题、相关度阈值）
        # ✅ 已针对硅钢技术论文知识库优化！
        # 如果您的知识库内容不同，请修改查询以匹配
        self.test_queries = [
            {
                "query": "取向硅钢的磁性能如何？",
                "expected_topics": ["取向硅钢", "磁性能", "铁损", "磁感"],
                "min_relevance": 0.6,
                "category": "材料性能"
            },
            {
                "query": "终轧温度如何影响硅钢析出物？",
                "expected_topics": ["终轧温度", "析出物", "热轧", "组织"],
                "min_relevance": 0.5,
                "category": "工艺参数"
            },
            {
                "query": "无取向硅钢和取向硅钢的区别是什么？",
                "expected_topics": ["无取向", "取向", "织构", "晶粒"],
                "min_relevance": 0.6,
                "category": "材料对比"
            },
            {
                "query": "冷轧对硅钢织构演变的影响",
                "expected_topics": ["冷轧", "织构", "再结晶", "轧制"],
                "min_relevance": 0.5,
                "category": "工艺流程"
            },
            {
                "query": "如何提高硅钢的铁损性能？",
                "expected_topics": ["铁损", "磁畴", "退火", "晶粒"],
                "min_relevance": 0.5,
                "category": "性能优化"
            },
            {
                "query": "硅钢常化炉冷却工艺研究",
                "expected_topics": ["常化", "冷却", "热处理", "射流"],
                "min_relevance": 0.5,
                "category": "热处理工艺"
            },
            {
                "query": "热轧带钢的智能轧制技术",
                "expected_topics": ["热轧", "智能", "轧制", "板形"],
                "min_relevance": 0.5,
                "category": "智能制造"
            },
            {
                "query": "电磁钢板的铁心紧固性能",
                "expected_topics": ["电磁钢", "铁心", "紧固", "机械性能"],
                "min_relevance": 0.5,
                "category": "应用性能"
            },
        ]
        
    def load_searcher(self) -> SearcherFast | None:
        """加载检索器"""
        index_path = Path("data/embeddings/knowledge_base.faiss")
        meta_path = Path("data/embeddings/knowledge_base.meta.jsonl")
        
        if not index_path.exists():
            print("❌ 索引不存在，请先运行 python scripts/rag_cli.py build")
            return None
        
        print("📂 加载索引...")
        
        vector_store = VectorStoreFast(
            dim=384,
            index_path=index_path,
            metadata_path=meta_path,
            normalize=False,
            use_ivf=None,  # 自动判断
        )
        
        searcher = SearcherFast(
            self.embedder,
            vector_store,
            enable_cache=False,  # 禁用缓存以获得真实检索结果
            cache_size=0,
        )
        
        print(f"✅ 索引加载完成: {vector_store.size} 个向量")
        print(f"   索引类型: {vector_store.index_type}")
        print(f"   元数据路径: {meta_path}")
        
        return searcher
    
    def evaluate_retrieval_accuracy(self, searcher: SearcherFast) -> Dict[str, Any]:
        """评估检索准确性（相关度分析）"""
        print(f"\n{'='*60}")
        print(f"📊 测试 1: 检索准确性评估")
        print(f"{'='*60}")
        
        all_results = []
        category_scores = {}
        
        for i, test_case in enumerate(self.test_queries, 1):
            query = test_case["query"]
            expected_topics = test_case["expected_topics"]
            min_relevance = test_case["min_relevance"]
            category = test_case["category"]
            
            print(f"\n[{i}/{len(self.test_queries)}] 查询: {query}")
            print(f"   预期主题: {', '.join(expected_topics)}")
            print(f"   最低相关度: {min_relevance * 100:.0f}%")
            
            # 执行检索
            results = searcher.search(query, top_k=5)
            
            if not results:
                print("   ❌ 无检索结果")
                all_results.append({
                    "query": query,
                    "category": category,
                    "num_results": 0,
                    "avg_score": 0,
                    "max_score": 0,
                    "min_score": 0,
                    "topic_coverage": 0,
                    "meets_threshold": False,
                })
                continue
            
            # 分析结果
            scores = [r.get("score", 0) for r in results]
            avg_score = statistics.mean(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # 检查主题覆盖率（从完整分块内容中检查，而不是preview）
            top_result = results[0]
            content = top_result.get("content", "")
            
            # 如果 content 太短或为空，从文件系统读取完整内容
            if len(content) < 200:
                file_path = top_result.get("file", "")
                chunk_id = top_result.get("chunk_id", "")
                
                if file_path and chunk_id is not None:
                    try:
                        # 将 .pdf.txt 转换为 .pdf.chunks.jsonl
                        # 例如: data\...\xxx.pdf.txt → data\...\xxx.pdf.chunks.jsonl
                        chunks_file_path = file_path.replace(".txt", ".chunks.jsonl")
                        chunks_file = Path(chunks_file_path)
                        
                        # 读取对应的分块
                        if chunks_file.exists():
                            with open(chunks_file, "r", encoding="utf-8") as f:
                                for line in f:
                                    if line.strip():
                                        chunk_data = json.loads(line)
                                        if chunk_data.get("chunk_id") == chunk_id:
                                            content = chunk_data.get("content", "")
                                            break
                    except Exception as e:
                        pass  # 如果读取失败，使用原有的 content
            
            matched_topics = sum(1 for topic in expected_topics if topic in content)
            topic_coverage = matched_topics / len(expected_topics) if expected_topics else 0
            
            # 是否满足阈值
            meets_threshold = max_score >= min_relevance
            
            print(f"   ✅ 检索到 {len(results)} 个结果")
            print(f"   📊 相关度: 平均={avg_score*100:.1f}%, 最高={max_score*100:.1f}%, 最低={min_score*100:.1f}%")
            print(f"   🎯 主题覆盖: {matched_topics}/{len(expected_topics)} ({topic_coverage*100:.0f}%)")
            print(f"   {'✅' if meets_threshold else '❌'} 满足阈值: {meets_threshold}")
            
            if results:
                print(f"   📄 Top 1: {top_result.get('file', 'Unknown')} (相关度: {top_result.get('score', 0)*100:.1f}%)")
            
            # 记录结果
            result_data = {
                "query": query,
                "category": category,
                "num_results": len(results),
                "avg_score": avg_score,
                "max_score": max_score,
                "min_score": min_score,
                "topic_coverage": topic_coverage,
                "meets_threshold": meets_threshold,
                "top_file": top_result.get("file", "Unknown") if results else None,
            }
            all_results.append(result_data)
            
            # 按类别统计
            if category not in category_scores:
                category_scores[category] = []
            category_scores[category].append(max_score)
        
        # 汇总统计
        overall_avg = statistics.mean([r["avg_score"] for r in all_results])
        overall_max = statistics.mean([r["max_score"] for r in all_results])
        pass_rate = sum(1 for r in all_results if r["meets_threshold"]) / len(all_results)
        avg_coverage = statistics.mean([r["topic_coverage"] for r in all_results])
        
        return {
            "test_name": "检索准确性",
            "total_queries": len(all_results),
            "overall_avg_score": overall_avg,
            "overall_max_score": overall_max,
            "pass_rate": pass_rate,
            "avg_topic_coverage": avg_coverage,
            "category_scores": category_scores,
            "details": all_results,
        }
    
    def evaluate_document_coverage(self, searcher: SearcherFast) -> Dict[str, Any]:
        """评估文档覆盖率（知识库利用率）"""
        print(f"\n{'='*60}")
        print(f"📊 测试 2: 文档覆盖率评估")
        print(f"{'='*60}")
        
        # 收集所有被检索到的文档
        retrieved_files = set()
        file_frequency = {}
        
        for test_case in self.test_queries:
            query = test_case["query"]
            results = searcher.search(query, top_k=10)  # 扩大到top10
            
            for result in results:
                file_name = result.get("file", "Unknown")
                retrieved_files.add(file_name)
                file_frequency[file_name] = file_frequency.get(file_name, 0) + 1
        
        # 获取知识库总文档数（统计唯一文件数）
        all_files = set()
        try:
            # 访问私有属性 _store 和 _metadatas
            for meta in searcher._store._metadatas:
                file_name = meta.get("file", "Unknown")
                all_files.add(file_name)
            total_docs = len(all_files)
        except Exception as e:
            print(f"   ⚠️  无法获取总文档数: {e}")
            total_docs = searcher._store.size  # 降级使用向量总数
        
        coverage_rate = len(retrieved_files) / total_docs if total_docs > 0 else 0
        
        # 按频率排序
        sorted_files = sorted(file_frequency.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n📚 知识库统计:")
        print(f"   总文档数: {total_docs}")
        print(f"   被检索文档数: {len(retrieved_files)}")
        print(f"   文档覆盖率: {coverage_rate*100:.1f}%")
        
        print(f"\n🔥 高频文档 (Top 10):")
        for i, (file_name, count) in enumerate(sorted_files[:10], 1):
            print(f"   {i}. {file_name}: {count} 次")
        
        # 识别未被检索的文档（如果可以获取所有文档列表）
        unused_rate = 1 - coverage_rate
        
        return {
            "test_name": "文档覆盖率",
            "total_documents": total_docs,
            "retrieved_documents": len(retrieved_files),
            "coverage_rate": coverage_rate,
            "unused_rate": unused_rate,
            "file_frequency": file_frequency,
            "top_files": sorted_files[:10],
        }
    
    def evaluate_result_diversity(self, searcher: SearcherFast) -> Dict[str, Any]:
        """评估检索结果多样性"""
        print(f"\n{'='*60}")
        print(f"📊 测试 1: 检索结果多样性评估")
        print(f"{'='*60}")
        
        diversity_scores = []
        
        for test_case in self.test_queries:
            query = test_case["query"]
            results = searcher.search(query, top_k=5)
            
            if len(results) < 2:
                diversity_scores.append(0)
                continue
            
            # 计算文档多样性（不同文档的数量）
            unique_files = set(r.get("file", "") for r in results)
            file_diversity = len(unique_files) / len(results)
            
            # 计算相似度方差（越大说明结果越分散，多样性越高）
            scores = [r.get("score", 0) for r in results]
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            
            diversity_scores.append(file_diversity)
            
            print(f"\n📝 查询: {query}")
            print(f"   文档多样性: {len(unique_files)}/{len(results)} = {file_diversity*100:.0f}%")
            print(f"   相关度方差: {score_variance:.4f}")
        
        avg_diversity = statistics.mean(diversity_scores) if diversity_scores else 0
        
        print(f"\n📊 总体多样性: {avg_diversity*100:.1f}%")
        
        return {
            "test_name": "结果多样性",
            "avg_diversity": avg_diversity,
            "diversity_scores": diversity_scores,
        }
    
    def evaluate_chunk_quality(self, searcher: SearcherFast) -> Dict[str, Any]:
        """评估分块质量"""
        print(f"\n{'='*60}")
        print(f"📊 测试 2: 分块质量评估")
        print(f"{'='*60}")
        
        chunk_sizes = []
        
        # ✅ 优先从文件系统读取完整分块数据（更准确）
        print("   📁 从文件系统读取分块数据...")
        processed_dir = Path("data/knowledge_base/processed")
        
        if processed_dir.exists():
            # 支持多种扩展名（.pdf.chunks.jsonl, .txt.chunks.jsonl, .docx.chunks.jsonl）
            chunk_files = list(processed_dir.glob("*.chunks.jsonl"))[:20]  # 采样20个文件
            
            print(f"   📂 找到 {len(chunk_files)} 个分块文件")
            
            for chunk_file in chunk_files:
                try:
                    with open(chunk_file, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.strip():
                                chunk_data = json.loads(line)
                                content = chunk_data.get("content", "")
                                if content:
                                    chunk_sizes.append(len(content))
                except Exception as e:
                    print(f"   ⚠️  读取失败: {chunk_file.name} - {e}")
                    continue
            
            if chunk_sizes:
                print(f"   ✅ 成功读取 {len(chunk_sizes)} 个分块")
        
        # 备用方法：如果文件系统读取失败，从检索结果获取（不推荐，可能只有preview）
        if not chunk_sizes:
            print("   ⚠️  文件系统读取失败，尝试从检索结果获取...")
            sample_query = self.test_queries[0]["query"]
            results = searcher.search(sample_query, top_k=20)
            
            for result in results:
                # 尝试从完整的文件路径读取
                file_path = result.get("file", "")
                chunk_id = result.get("chunk_id", "")
                
                if file_path and chunk_id:
                    try:
                        chunks_file = Path(file_path)
                        if chunks_file.exists():
                            with open(chunks_file, "r", encoding="utf-8") as f:
                                for line in f:
                                    if line.strip():
                                        chunk_data = json.loads(line)
                                        if chunk_data.get("chunk_id") == chunk_id:
                                            content = chunk_data.get("content", "")
                                            if content:
                                                chunk_sizes.append(len(content))
                                            break
                    except Exception:
                        pass
        
        if not chunk_sizes or len(chunk_sizes) == 0:
            print("   ❌ 无法获取分块数据")
            print("   💡 可能原因：")
            print("      1. 检索结果不包含 content 字段")
            print("      2. data/knowledge_base/processed/ 目录中无分块文件")
            print("      3. 分块文件格式不正确")
            return {
                "test_name": "分块质量",
                "sample_count": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "coefficient_of_variation": 0,
            }
        
        avg_size = statistics.mean(chunk_sizes)
        min_size = min(chunk_sizes)
        max_size = max(chunk_sizes)
        std_size = statistics.stdev(chunk_sizes) if len(chunk_sizes) > 1 else 0
        coeff_var = std_size / avg_size if avg_size > 0 else 0  # 变异系数
        
        print(f"\n📏 分块大小统计 (采样 {len(chunk_sizes)} 个分块):")
        print(f"   平均大小: {avg_size:.0f} 字符")
        print(f"   最小大小: {min_size} 字符")
        print(f"   最大大小: {max_size} 字符")
        print(f"   标准差: {std_size:.0f} 字符")
        
        # 评估分块质量
        print(f"\n✅ 分块质量评价:")
        if 400 <= avg_size <= 800:
            print(f"   ✅ 平均分块大小合理 (推荐 400-800 字符)")
        else:
            print(f"   ⚠️  平均分块大小偏{'大' if avg_size > 800 else '小'} (推荐 400-800 字符)")
        
        # 变异系数评估
        if coeff_var < 0.5:
            print(f"   ✅ 分块大小一致性好 (变异系数 {coeff_var*100:.1f}%)")
        else:
            print(f"   ⚠️  分块大小差异较大 (变异系数 {coeff_var*100:.1f}%)")
        
        return {
            "test_name": "分块质量",
            "sample_count": len(chunk_sizes),
            "avg_chunk_size": avg_size,
            "min_chunk_size": min_size,
            "max_chunk_size": max_size,
            "std_chunk_size": std_size,
            "coefficient_of_variation": coeff_var,
        }
    
    def run_all_evaluations(self):
        """运行所有质量评估测试"""
        print("🚀 RAG检索质量评估测试")
        print("=" * 60)
        
        # 加载检索器
        searcher = self.load_searcher()
        if not searcher:
            return
        
        results = {}
        
        # 1. 检索准确性评估
        results["accuracy"] = self.evaluate_retrieval_accuracy(searcher)
        
        # 2. 文档覆盖率评估
        results["coverage"] = self.evaluate_document_coverage(searcher)
        
        # 3. 检索结果多样性评估
        results["diversity"] = self.evaluate_result_diversity(searcher)
        
        # 4. 分块质量评估
        results["chunk_quality"] = self.evaluate_chunk_quality(searcher)
        
        # 5. 生成总结报告
        self.print_summary(results)
        
        # 6. 保存详细结果到文件
        self.save_results(results)
    
    def print_summary(self, results: Dict[str, Any]):
        """打印质量评估总结"""
        print("\n" + "=" * 80)
        print("📊 RAG检索质量评估总结报告")
        print("=" * 80)
        
        # 数据说明
        print("\n" + "=" * 80)
        print("📖 数据说明")
        print("=" * 80)
        print("• 相关度: 查询向量与文档向量的余弦相似度 (0-100%)")
        print("• 通过率: 满足预期相关度阈值的查询比例")
        print("• 主题覆盖: 预期关键词在检索结果中出现的比例")
        print("• 文档覆盖率: 被检索到的文档占知识库总文档的比例")
        print("• 结果多样性: 检索结果来自不同文档的比例")
        print("• 分块质量: 文档分块大小的合理性（推荐 400-800 字符）")
        print("=" * 80)
        
        # 1. 检索准确性
        accuracy = results.get("accuracy", {})
        print(f"\n【1️⃣ 检索准确性】")
        print(f"   总查询数: {accuracy.get('total_queries', 0)}")
        print(f"   平均相关度: {accuracy.get('overall_avg_score', 0)*100:.1f}%")
        print(f"   最高相关度均值: {accuracy.get('overall_max_score', 0)*100:.1f}%")
        print(f"   通过率: {accuracy.get('pass_rate', 0)*100:.1f}% (满足预期阈值)")
        print(f"   主题覆盖度: {accuracy.get('avg_topic_coverage', 0)*100:.1f}%")
        
        # 按类别统计
        if "category_scores" in accuracy:
            print(f"\n   📋 各类别平均相关度:")
            for category, scores in accuracy["category_scores"].items():
                avg_score = statistics.mean(scores) if scores else 0
                print(f"      • {category}: {avg_score*100:.1f}%")
        
        # 2. 文档覆盖率
        coverage = results.get("coverage", {})
        print(f"\n【2️⃣ 文档覆盖率】")
        print(f"   知识库总文档数: {coverage.get('total_documents', 0)}")
        print(f"   被检索文档数: {coverage.get('retrieved_documents', 0)}")
        print(f"   文档覆盖率: {coverage.get('coverage_rate', 0)*100:.1f}%")
        print(f"   未使用文档率: {coverage.get('unused_rate', 0)*100:.1f}%")
        
        # 3. 结果多样性
        diversity = results.get("diversity", {})
        print(f"\n【1️⃣ 检索结果多样性】")
        print(f"   平均文档多样性: {diversity.get('avg_diversity', 0)*100:.1f}%")
        print(f"   说明: 多样性越高，说明检索结果来源越分散")
        
        # 4. 分块质量
        chunk = results.get("chunk_quality", {})
        print(f"\n【2️⃣ 分块质量】")
        print(f"   采样数量: {chunk.get('sample_count', 0)} 个分块")
        print(f"   平均大小: {chunk.get('avg_chunk_size', 0):.0f} 字符")
        print(f"   大小范围: {chunk.get('min_chunk_size', 0)} - {chunk.get('max_chunk_size', 0)} 字符")
        print(f"   标准差: {chunk.get('std_chunk_size', 0):.0f} 字符")
        print(f"   变异系数: {chunk.get('coefficient_of_variation', 0)*100:.1f}%")
        
        # 5. 综合评分
        print(f"\n【⭐ 综合评分】")
        accuracy_score = accuracy.get('pass_rate', 0) * 100
        coverage_score = min(coverage.get('coverage_rate', 0) * 2, 1.0) * 100  # 50%覆盖率=满分
        diversity_score = diversity.get('avg_diversity', 0) * 100
        
        # 分块质量评分 (400-800字符为最优)
        avg_chunk = chunk.get('avg_chunk_size', 0)
        if 400 <= avg_chunk <= 800:
            chunk_score = 100
        elif avg_chunk < 400:
            chunk_score = max(0, avg_chunk / 400 * 100)
        else:
            chunk_score = max(0, 100 - (avg_chunk - 800) / 10)
        
        overall_score = (accuracy_score + coverage_score + diversity_score + chunk_score) / 4
        
        print(f"   准确性得分: {accuracy_score:.1f}/100")
        print(f"   覆盖率得分: {coverage_score:.1f}/100")
        print(f"   多样性得分: {diversity_score:.1f}/100")
        print(f"   分块质量得分: {chunk_score:.1f}/100")
        print(f"   ━━━━━━━━━━━━━━━━━━━━")
        print(f"   综合得分: {overall_score:.1f}/100 {'🏆' if overall_score >= 80 else '✅' if overall_score >= 60 else '⚠️'}")
        
        # 6. 优化建议
        print(f"\n【💡 优化建议】")
        suggestions = []
        
        avg_topic_coverage = accuracy.get('avg_topic_coverage', 0)
        
        if avg_topic_coverage == 0:
            suggestions.append("• ⚠️  主题覆盖率为 0%！测试查询与知识库内容不匹配")
            suggestions.append("  → 请修改 test_queries 以匹配您的知识库领域")
            suggestions.append("  → 例如：如果知识库是硅钢论文，查询应该关于'取向硅钢'、'磁性能'等")
        
        if accuracy.get('pass_rate', 0) < 0.7:
            suggestions.append("• 检索准确性偏低，建议增加相关领域文档或优化分块策略")
        
        if coverage.get('coverage_rate', 0) < 0.3:
            suggestions.append("• 文档覆盖率低，部分文档可能质量较低或与查询不匹配")
        
        if diversity.get('avg_diversity', 0) < 0.5:
            suggestions.append("• 结果多样性不足，检索可能过于集中在少数文档")
        
        if avg_chunk < 400:
            suggestions.append("• 分块过小，可能导致上下文信息不足，建议增大chunk_size")
        elif avg_chunk > 800:
            suggestions.append("• 分块过大，可能包含无关信息，建议减小chunk_size")
        
        if chunk.get('coefficient_of_variation', 0) > 0.5:
            suggestions.append("• 分块大小不一致，建议检查文档预处理逻辑")
        
        if not suggestions:
            suggestions.append("• ✅ 系统整体表现良好，继续保持！")
        
        for suggestion in suggestions:
            print(f"   {suggestion}")
        
        print("\n" + "=" * 80)
        print("✅ 质量评估完成")
        print("=" * 80)
    
    def save_results(self, results: Dict[str, Any]):
        """保存评估结果到JSON文件"""
        output_dir = Path("data/evaluation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"rag_quality_report_{timestamp}.json"
        
        # 移除不可序列化的对象
        cleaned_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                cleaned_results[key] = {
                    k: v for k, v in value.items()
                    if not callable(v) and k != "details"  # 排除函数和详细列表
                }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(cleaned_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存: {output_file}")


if __name__ == "__main__":
    evaluator = RAGQualityEvaluator()
    try:
        evaluator.run_all_evaluations()
    except KeyboardInterrupt:
        print("\n\n❌ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

