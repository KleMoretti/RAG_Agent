#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 此脚本已废弃，请使用新的统一 CLI 工具

推荐使用: python scripts/rag_cli.py build --help

RAG系统构建脚本 - 专为学术论文RAG设计
符合AGENTS.md元数据规范，支持中文学术论文的智能分块和检索

使用方法:
    python scripts/build_rag_system.py --help
    python scripts/build_rag_system.py --input data/raw --output data/embeddings
    python scripts/build_rag_system.py --rebuild --chunk-size 800
    
新方式:
    python scripts/rag_cli.py build --help
    python scripts/rag_cli.py build --rebuild --chunk-size 800
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder
from src.retrieval.vector_store import VectorStore
from src.retrieval.indexer import Indexer
from config.logging_config import setup_logging
from scripts.paths import DATA_DIRS, ensure_data_dirs


class AcademicRAGBuilder:
    """学术论文RAG系统构建器"""
    
    def __init__(
        self,
        raw_data_dir: str = None,
        processed_dir: str = None,
        embeddings_dir: str = None,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50,
        embedding_model: str = "all-MiniLM-L6-v2",
        supported_formats: tuple = None
    ):
        # 使用默认路径（相对于项目根目录）
        self.raw_data_dir = Path(raw_data_dir) if raw_data_dir else DATA_DIRS['raw']
        self.processed_dir = Path(processed_dir) if processed_dir else DATA_DIRS['processed']
        self.embeddings_dir = Path(embeddings_dir) if embeddings_dir else DATA_DIRS['embeddings']
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.supported_formats = supported_formats or ('.pdf', '.docx', '.txt', '.md')
        
        # 确保所有目录存在
        ensure_data_dirs()
        
        # 初始化组件
        self.loader = DataLoader()
        self.preprocessor = Preprocessor(
            min_chars=10,
            keep_spaces=True,
            keep_numbers=True
        )
        self.embedder = Embedder(model_name=embedding_model)
        
        # 创建向量存储
        self.store = VectorStore(
            dim=self.embedder.dim,
            index_path=self.embeddings_dir / "index.faiss",
            metadata_path=self.embeddings_dir / "index.meta.jsonl",
            normalize=False
        )
        
        # 创建分块函数
        self.chunker = self._create_academic_chunker()
        
        # 创建索引器
        self.indexer = Indexer(
            embedder=self.embedder,
            store=self.store,
            chunker=self.chunker,
            preprocessor=self._preprocess_text
        )
        
        # 统计信息
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'start_time': None,
            'end_time': None,
            'failed_file_details': []
        }

    def _create_academic_chunker(self):
        """创建适合学术论文的智能分块函数"""
        def chunk_academic_text(text: str) -> List[str]:
            """
            学术论文智能分块策略：
            1. 按段落分割（双换行）
            2. 按句子分割（中文标点）
            3. 按长度合并，保持语义完整
            4. 处理标题、摘要、正文等不同部分
            """
            if not text.strip():
                return []
            
            # 预处理：标准化换行和空格
            text = self.preprocessor.clean_text(text)
            
            # 按段落分割
            paragraphs = self._split_paragraphs(text)
            chunks = []
            
            for para in paragraphs:
                if len(para.strip()) < self.min_chunk_size:
                    continue
                
                # 如果段落太长，进一步分句
                if len(para) > self.chunk_size:
                    para_chunks = self._split_long_paragraph(para)
                    chunks.extend(para_chunks)
                else:
                    chunks.append(para.strip())
            
            return [chunk for chunk in chunks if len(chunk.strip()) >= self.min_chunk_size]
        
        return chunk_academic_text

    def _split_paragraphs(self, text: str) -> List[str]:
        """按段落分割文本"""
        # 按双换行分割段落
        paragraphs = text.split('\n\n')
        result = []
        
        for para in paragraphs:
            para = para.strip()
            if para and len(para) >= self.min_chunk_size:
                result.append(para)
        
        return result

    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割过长的段落"""
        # 先分句
        sentences = self.preprocessor.split_sentences(paragraph)
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 如果加上当前句子会超过chunk_size，先保存当前块
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                chunk_text = ''.join(current_chunk)
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    chunks.append(chunk_text.strip())
                
                # 保留重叠部分
                if self.chunk_overlap > 0:
                    overlap_text = ''.join(current_chunk[-2:])  # 保留最后2个句子作为重叠
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(sentence)
        
        # 处理最后一个块
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunks.append(chunk_text.strip())
        
        return chunks

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        return self.preprocessor.clean_text(text)

    def _get_processed_files(self) -> set:
        """获取已处理的文件列表"""
        processed_file = self.processed_dir / 'processed_files.json'
        if processed_file.exists():
            with open(processed_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()

    def _save_processed_files(self, processed_files: set):
        """保存已处理文件列表"""
        processed_file = self.processed_dir / 'processed_files.json'
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(list(processed_files), f, ensure_ascii=False, indent=2)

    def build_rag_system(self, rebuild: bool = False) -> Dict[str, Any]:
        """构建RAG系统"""
        self.stats['start_time'] = datetime.now()
        
        # 如果重建，清空现有索引
        if rebuild:
            logging.info("重建模式：清空现有索引")
            self.store = VectorStore(
                dim=self.embedder.dim,
                index_path=self.embeddings_dir / "index.faiss",
                metadata_path=self.embeddings_dir / "index.meta.jsonl",
                normalize=False
            )
            self.indexer = Indexer(
                embedder=self.embedder,
                store=self.store,
                chunker=self.chunker,
                preprocessor=self._preprocess_text
            )
        
        processed_files = self._get_processed_files()
        
        # 扫描文件
        all_files = list(self.raw_data_dir.rglob('*'))
        pdf_files = [f for f in all_files if f.suffix.lower() in self.supported_formats]
        self.stats['total_files'] = len(pdf_files)
        
        logging.info(f"发现 {self.stats['total_files']} 个支持的文件")
        
        # 处理文件
        for file_path in pdf_files:
            if not rebuild and str(file_path) in processed_files:
                logging.info(f"跳过已处理文件: {file_path}")
                continue
            
            try:
                ok = self._process_single_file(file_path)
                if ok:
                    self.stats['processed_files'] += 1
                    processed_files.add(str(file_path))
                else:
                    # 空内容/无法提取文本，跳过但不计为异常
                    self.stats['failed_files'] += 1
                    hint = '空内容或无法提取文本，已跳过'
                    if file_path.suffix.lower() == '.pdf':
                        hint += '（可能为扫描版或不可选文本PDF，建议使用OCR识别后再导入）'
                    self.stats['failed_file_details'].append({
                        'file': str(file_path),
                        'error': hint,
                        'timestamp': datetime.now().isoformat()
                    })
                    logging.warning(f"跳过空内容文件: {file_path} - {hint}")

            except Exception as e:
                self.stats['failed_files'] += 1
                error_info = {
                    'file': str(file_path),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.stats['failed_file_details'].append(error_info)
                logging.error(f"处理文件失败 {file_path}: {e}")
        
        # 保存索引和状态
        self.store.save()
        self._save_processed_files(processed_files)
        
        self.stats['end_time'] = datetime.now()
        self.stats['total_chunks'] = self.store.size
        
        return self.stats

    def _process_single_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        logging.info(f"开始处理文件: {file_path}")
        
        # 1. 加载文件
        content = self.loader.load(str(file_path))
        if not content or not content.strip():
            # 允许跳过空内容文件
            return False
        
        # 2. 预处理文本
        cleaned_text = self.preprocessor.clean_text(content)
        if not cleaned_text.strip():
            return False

        # 3. 保存处理后的文本
        processed_file = self.processed_dir / f"{file_path.stem}.txt"
        # 若文件已存在：覆盖写入，避免旧内容干扰
        processed_file.write_text(cleaned_text, encoding='utf-8')
        
        # 4. 使用Indexer进行分块、嵌入和索引
        chunk_ids = self.indexer.index_file(processed_file, file_id=str(file_path))
        
        logging.info(f"文件 {file_path.name} 处理完成，生成 {len(chunk_ids)} 个块")
        return True

    def search(self, query: str, top_k: int = 5, include_metadata: bool = True) -> List[Dict[str, Any]]:
        """搜索相关文档块"""
        if self.store.size == 0:
            logging.warning("向量库为空，无法搜索")
            return []
        
        # 预处理查询
        query_processed = self._preprocess_text(query)
        query_vector = self.embedder.encode([query_processed], normalize=True)[0]
        
        # 搜索
        results = self.store.search(
            query_vector, 
            top_k=top_k, 
            include_metadata=include_metadata
        )
        
        return results

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            'vector_store_size': self.store.size,
            'embedding_dimension': self.embedder.dim,
            'embedding_model': self.embedder.model.get_sentence_embedding_dimension(),
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'supported_formats': self.supported_formats,
            'stats': self.stats
        }

    def export_metadata(self, output_file: str = "metadata_export.json"):
        """导出元数据用于分析"""
        metadata_list = []
        for meta in self.store.iter_metadata():
            metadata_list.append(meta)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_chunks': len(metadata_list),
            'system_info': self.get_system_info(),
            'metadata': metadata_list
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"元数据已导出到: {output_path}")
        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="构建学术论文RAG系统")
    parser.add_argument("--input", "-i", default="data/raw", 
                       help="输入目录路径 (默认: data/raw)")
    parser.add_argument("--output", "-o", default="data/embeddings",
                       help="输出目录路径 (默认: data/embeddings)")
    parser.add_argument("--processed", "-p", default="data/processed",
                       help="处理后文本目录 (默认: data/processed)")
    parser.add_argument("--chunk-size", "-c", type=int, default=600,
                       help="分块大小 (默认: 600)")
    parser.add_argument("--chunk-overlap", type=int, default=100,
                       help="分块重叠大小 (默认: 100)")
    parser.add_argument("--min-chunk-size", type=int, default=50,
                       help="最小分块大小 (默认: 50)")
    parser.add_argument("--model", "-m", default="all-MiniLM-L6-v2",
                       help="嵌入模型名称 (默认: all-MiniLM-L6-v2)")
    parser.add_argument("--rebuild", action="store_true",
                       help="重建索引（清空现有数据）")
    parser.add_argument("--test-query", "-q", 
                       help="构建完成后测试查询")
    parser.add_argument("--export-metadata", action="store_true",
                       help="导出元数据到JSON文件")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    # 创建构建器
    builder = AcademicRAGBuilder(
        raw_data_dir=args.input,
        processed_dir=args.processed,
        embeddings_dir=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_size=args.min_chunk_size,
        embedding_model=args.model
    )
    
    # 构建RAG系统
    print("🚀 开始构建学术论文RAG系统...")
    stats = builder.build_rag_system(rebuild=args.rebuild)
    
    # 输出结果
    print(f"\n✅ 构建完成！")
    print(f"📁 总文件数: {stats['total_files']}")
    print(f"✅ 成功处理: {stats['processed_files']}")
    print(f"❌ 失败文件: {stats['failed_files']}")
    print(f"📄 总块数: {stats['total_chunks']}")
    print(f"⏱️  处理时间: {stats['end_time'] - stats['start_time']}")
    
    if stats['failed_file_details']:
        print(f"\n❌ 失败文件详情:")
        for detail in stats['failed_file_details']:
            print(f"  - {detail['file']}: {detail['error']}")
    
    # 测试查询
    if args.test_query:
        print(f"\n🔍 测试查询: '{args.test_query}'")
        results = builder.search(args.test_query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. 文件: {Path(result['file']).name}")
            print(f"     块ID: {result['chunk_id']}")
            print(f"     相似度: {result['score']:.4f}")
            print(f"     预览: {result['preview']}...")
            print()
    
    # 导出元数据
    if args.export_metadata:
        export_file = builder.export_metadata()
        print(f"📊 元数据已导出到: {export_file}")
    
    # 显示系统信息
    info = builder.get_system_info()
    print(f"\n📊 系统信息:")
    print(f"  向量库大小: {info['vector_store_size']}")
    print(f"  嵌入维度: {info['embedding_dimension']}")
    print(f"  分块大小: {info['chunk_size']}")
    print(f"  分块重叠: {info['chunk_overlap']}")


if __name__ == "__main__":
    main()
