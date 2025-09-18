# data_ingestion.py
from typing import List, Dict, Optional
from pathlib import Path
import logging
import pickle
from datetime import datetime
import json

from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder
##from src.retrieval.indexer import VectorIndexer


class DataIngestion:
    """数据摄入类，支持多种文件格式和批量处理"""

    def __init__(self,
                 raw_data_dir: str = "data/raw",
                 processed_dir: str = "data/processed",
                 embeddings_dir: str = "data/embeddings",
                 supported_formats: tuple = ('.pdf', '.docx', '.txt', '.mp3', '.wav')):
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_dir)
        self.embeddings_dir = Path(embeddings_dir)
        self.supported_formats = supported_formats
        self.indexer = VectorIndexer()
        # 初始化处理器实例
        self.loader = DataLoader()
        self.preprocessor = Preprocessor()
        self.embedder = Embedder()

        # 创建必要的目录
        for dir_path in [self.processed_dir, self.embeddings_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # 设置日志
        self._setup_logging()

        # 记录处理状态
        self.process_stats = {
            'success_files': [],
            'failed_files': [],
            'processed_time': None
        }

    def _setup_logging(self):
        """配置日志"""
        logging.basicConfig(
            filename=f'logs/data_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

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
        """批量处理文件"""
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
                content = self.loader.load(file_path)
                logging.info(f"成功加载文件: {file_path}")

                # 2. 预处理文本
                cleaned_text = self.preprocessor.clean_text(content)
                sentences = self.preprocessor.split_sentences(cleaned_text)
                processed_text = '\n'.join(sentences)

                # 保存处理后的文本
                processed_file = self.processed_dir / f"{file_path.stem}_processed.txt"
                processed_file.write_text(processed_text, encoding='utf-8')

                # 3. 生成嵌入向量
                embeddings = self.embedder.encode([processed_text])  # 使用 Embedder 的 encode 方法

                # 保存嵌入向量
                embedding_file = self.embeddings_dir / f"{file_path.stem}_embeddings.pkl"
                with open(embedding_file, 'wb') as f:
                    pickle.dump(embeddings, f)

                # 4. 构建索引
                metadata = {
                    'file_name': file_path.name,
                    'file_path': str(file_path),
                    'processed_time': datetime.now().isoformat(),
                }
                self.indexer.add_embeddings(embeddings, metadata)

                processed_files.add(str(file_path))
                self.process_stats['success_files'].append(str(file_path))
                logging.info(f"成功处理文件: {file_path}")

            except Exception as e:
                self.process_stats['failed_files'].append(str(file_path))
                logging.error(f"处理文件 {file_path} 失败: {str(e)}")

        # 更新处理状态
        self._save_processed_files(processed_files)
        self.process_stats['processed_time'] = datetime.now() - start_time

        # 保存最终的索引
        self.indexer.save_index()

        return self.process_stats

    def get_processing_status(self) -> Dict:
        """获取处理状态"""
        return {
            'total_processed': len(self.process_stats['success_files']),
            'total_failed': len(self.process_stats['failed_files']),
            'success_files': self.process_stats['success_files'],
            'failed_files': self.process_stats['failed_files'],
            'processing_time': str(self.process_stats['processed_time'])
        }