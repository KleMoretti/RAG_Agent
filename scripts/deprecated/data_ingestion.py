# data_ingestion.py
"""
⚠️ DEPRECATED: 此脚本已废弃，请使用新的统一 CLI 工具

推荐使用: python scripts/rag_cli.py build
"""
from typing import List, Dict, Optional, Callable
from pathlib import Path
import logging
import hashlib
from datetime import datetime
import json
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder
from src.retrieval.indexer import Indexer
from src.retrieval.vector_store import VectorStore
from scripts.paths import DATA_DIRS, ensure_data_dirs


class DataIngestion:
    """数据摄入类，支持多种文件格式和批量处理，符合AGENTS.md元数据规范"""

    def __init__(self,
                 raw_data_dir: str = None,
                 processed_dir: str = None,
                 embeddings_dir: str = None,
                 supported_formats: tuple = ('.pdf', '.docx', '.txt', '.mp3', '.wav'),
                 chunk_size: int = 600,
                 chunk_overlap: int = 100):
        # 使用默认路径（相对于项目根目录）
        self.raw_data_dir = Path(raw_data_dir) if raw_data_dir else DATA_DIRS['raw']
        self.processed_dir = Path(processed_dir) if processed_dir else DATA_DIRS['processed']
        self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else DATA_DIRS['embeddings']
        self.supported_formats = supported_formats
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化处理器实例
        self.loader = DataLoader()
        self.preprocessor = Preprocessor(min_chars=10, keep_spaces=True, keep_numbers=True)
        self.embedder = Embedder()
        
        # 创建向量存储和索引器
        self.store = VectorStore(
            dim=self.embedder.dim,
            index_path=self.embeddings_dir / "index.faiss",
            metadata_path=self.embeddings_dir / "index.meta.jsonl",
            normalize=False  # 外部归一化
        )
        
        # 创建分块函数
        self.chunker = self._create_chunker()
        
        # 创建索引器
        self.indexer = Indexer(
            embedder=self.embedder,
            store=self.store,
            chunker=self.chunker,
            preprocessor=self._preprocess_text
        )

        # 确保所有目录存在
        ensure_data_dirs()

        # 设置日志
        self._setup_logging()

        # 记录处理状态
        self.process_stats = {
            'success_files': [],
            'failed_files': [],
            'total_chunks': 0,
            'processed_time': None
        }

    def _setup_logging(self):
        """配置日志"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=logs_dir / f'data_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        return self.preprocessor.clean_text(text)

    def _create_chunker(self) -> Callable[[str], List[str]]:
        """创建智能分块函数，适合中文学术论文"""
        def chunk_text(text: str) -> List[str]:
            """智能分块：先分句，再按长度合并成语义完整的块"""
            if not text.strip():
                return []
            
            # 先分句
            sentences = self.preprocessor.split_sentences(text)
            if not sentences:
                return []
            
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # 如果当前块加上新句子会超过chunk_size，先保存当前块
                if current_length + len(sentence) > self.chunk_size and current_chunk:
                    chunk_text = ''.join(current_chunk)
                    if len(chunk_text.strip()) >= 50:  # 最小块长度
                        chunks.append(chunk_text.strip())
                    
                    # 保留重叠部分
                    overlap_text = ''.join(current_chunk[-self.chunk_overlap:]) if self.chunk_overlap > 0 else ""
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text)
                
                current_chunk.append(sentence)
                current_length += len(sentence)
            
            # 处理最后一个块
            if current_chunk:
                chunk_text = ''.join(current_chunk)
                if len(chunk_text.strip()) >= 50:
                    chunks.append(chunk_text.strip())
            
            return chunks
        
        return chunk_text

    def _get_processed_files(self) -> set:
        """获取已处理的文件列表"""
        try:
            with open(self.processed_dir / 'processed_files.json', 'r') as f:
                return set(json.load(f))
        except FileNotFoundError:
            return set()

    def _save_processed_files(self, processed_files: set):
        """保存已处理文件列表"""
        with open(self.processed_dir / 'processed_files.json', 'w') as f:
            json.dump(list(processed_files), f)

    def process_files(self) -> Dict:
        """批量处理文件，使用分块策略和标准元数据"""
        processed_files = self._get_processed_files()
        start_time = datetime.now()

        for file_path in self.raw_data_dir.rglob('*'):
            if file_path.suffix.lower() not in self.supported_formats:
                continue

            if str(file_path) in processed_files:
                logging.info(f"跳过已处理文件: {file_path}")
                continue

            try:
                # 1. 加载文件
                content = self.loader.load(str(file_path))
                logging.info(f"成功加载文件: {file_path}")

                # 跳过空内容并给出 OCR 提示
                if not content or not content.strip():
                    self.process_stats['failed_files'].append(str(file_path))
                    hint = "空内容或无法提取文本，已跳过"
                    if file_path.suffix.lower() == '.pdf':
                        hint += "（可能为扫描版或不可选文本PDF，建议使用OCR识别后再导入）"
                    logging.warning(f"跳过空内容文件: {file_path} - {hint}")
                    continue

                # 2. 预处理文本
                cleaned_text = self.preprocessor.clean_text(content)
                if not cleaned_text.strip():
                    self.process_stats['failed_files'].append(str(file_path))
                    hint = "清洗后仍为空，已跳过"
                    if file_path.suffix.lower() == '.pdf':
                        hint += "（可能为不可选文本PDF，建议进行OCR）"
                    logging.warning(f"跳过清洗后仍为空的文件: {file_path} - {hint}")
                    continue

                # 保存处理后的文本（覆盖写入）
                processed_file = self.processed_dir / f"{file_path.stem}.txt"
                processed_file.write_text(cleaned_text, encoding='utf-8')

                # 3. 使用Indexer进行分块、嵌入和索引
                chunk_ids = self.indexer.index_file(processed_file, file_id=str(file_path))
                
                # 更新统计
                chunk_count = len(chunk_ids)
                self.process_stats['total_chunks'] += chunk_count
                self.process_stats['success_files'].append(str(file_path))
                processed_files.add(str(file_path))
                
                logging.info(f"成功处理文件: {file_path}, 生成 {chunk_count} 个块")

            except Exception as e:
                self.process_stats['failed_files'].append(str(file_path))
                logging.error(f"处理文件 {file_path} 失败: {str(e)}")

        # 更新处理状态
        self._save_processed_files(processed_files)
        self.process_stats['processed_time'] = datetime.now() - start_time

        # 保存最终的索引
        self.store.save()

        return self.process_stats

    def get_processing_status(self) -> Dict:
        """获取处理状态"""
        return {
            'total_processed': len(self.process_stats['success_files']),
            'total_failed': len(self.process_stats['failed_files']),
            'total_chunks': self.process_stats['total_chunks'],
            'success_files': self.process_stats['success_files'],
            'failed_files': self.process_stats['failed_files'],
            'processing_time': str(self.process_stats['processed_time']),
            'vector_store_size': self.store.size
        }

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关文档块"""
        # 对查询进行预处理和嵌入
        query_processed = self._preprocess_text(query)
        query_vector = self.embedder.encode([query_processed], normalize=True)[0]
        
        # 在向量库中搜索
        results = self.store.search(query_vector, top_k=top_k, include_metadata=True)
        return results


def main():
    """主函数：运行数据摄入流程"""
    print("开始构建RAG向量数据库...")
    
    # 确保数据目录存在
    ensure_data_dirs()
    
    # 创建数据摄入实例（使用默认路径）
    ingestion = DataIngestion(
        chunk_size=600,
        chunk_overlap=100
    )
    
    # 处理文件
    stats = ingestion.process_files()
    
    # 输出结果
    print(f"\n处理完成！")
    print(f"成功处理文件: {stats['total_processed']}")
    print(f"失败文件: {stats['total_failed']}")
    print(f"总块数: {stats['total_chunks']}")
    print(f"向量库大小: {stats['vector_store_size']}")
    print(f"处理时间: {stats['processing_time']}")
    
    if stats['failed_files']:
        print(f"\n失败的文件:")
        for file in stats['failed_files']:
            print(f"  - {file}")
    
    # 测试搜索功能
    if stats['total_chunks'] > 0:
        print(f"\n测试搜索功能...")
        test_query = "摘要"
        results = ingestion.search(test_query, top_k=3)
        print(f"搜索 '{test_query}' 的结果:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. 文件: {result['file']}")
            print(f"     块ID: {result['chunk_id']}")
            print(f"     相似度: {result['score']:.4f}")
            print(f"     预览: {result['preview']}...")
            print()


if __name__ == "__main__":
    main()