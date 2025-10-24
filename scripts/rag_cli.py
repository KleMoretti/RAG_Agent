#!/usr/bin/env python3
"""
统一的 RAG 系统管理 CLI 工具

功能：
1. 构建 RAG 系统（build）- 数据加载、分块、嵌入、索引
2. 搜索测试（search）- 交互式或命令行搜索
3. 性能基准测试（benchmark）- 测试检索性能
4. 索引迁移（migrate）- 升级到快速索引
5. 系统信息（info）- 查看 RAG 系统状态
6. 导出数据（export）- 导出元数据用于分析

使用方法:
    python scripts/rag_cli.py build --help
    python scripts/rag_cli.py search "钢铁生产"
    python scripts/rag_cli.py benchmark
    python scripts/rag_cli.py migrate --auto
    python scripts/rag_cli.py info
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_processing.loader import DataLoader
from src.data_processing.preprocessor import Preprocessor
from src.data_processing.embedder import Embedder
from src.retrieval.vector_store_fast import VectorStoreFast
from src.retrieval.indexer import Indexer
from config.logging_config import setup_logging
from scripts.paths import DATA_DIRS, ensure_data_dirs
from src.api.db import get_db, db_context
from src.api.models import Agent, User, SystemPrompt


class RAGSystemManager:
    """RAG 系统统一管理器"""
    
    def __init__(
        self,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50,
        embedding_model: str = "all-MiniLM-L6-v2",
        verbose: bool = False
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.embedding_model = embedding_model
        
        # 设置日志
        log_level = logging.DEBUG if verbose else logging.INFO
        setup_logging(level=log_level)
        
        # 确保数据目录存在
        ensure_data_dirs()
        
        # 初始化组件
        self._init_components()
        
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
    
    def _init_components(self):
        """初始化 RAG 组件"""
        self.loader = DataLoader()
        self.preprocessor = Preprocessor(
            min_chars=10,
            keep_spaces=True,
            keep_numbers=True
        )
        self.embedder = Embedder(model_name=self.embedding_model)
        
        # 创建快速向量存储（自动选择索引类型）
        self.store = VectorStoreFast(
            dim=self.embedder.dim,
            index_path=DATA_DIRS['embeddings'] / "index.faiss",
            metadata_path=DATA_DIRS['embeddings'] / "index.meta.jsonl",
            normalize=False,
            use_ivf=None,  # 自动判断：<10k用Flat，>=10k自动升级IVF
            nlist=100,
            m=8,
            nbits=8,
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
    
    def _create_chunker(self):
        """创建智能分块函数"""
        def chunk_text(text: str) -> List[str]:
            if not text.strip():
                return []
            
            # 预处理
            text = self.preprocessor.clean_text(text)
            
            # 按段落分割
            paragraphs = text.split('\n\n')
            chunks = []
            
            for para in paragraphs:
                para = para.strip()
                if len(para) < self.min_chunk_size:
                    continue
                
                # 长段落分句
                if len(para) > self.chunk_size:
                    para_chunks = self._split_long_paragraph(para)
                    chunks.extend(para_chunks)
                else:
                    chunks.append(para)
            
            return [c for c in chunks if len(c.strip()) >= self.min_chunk_size]
        
        return chunk_text
    
    def _split_long_paragraph(self, paragraph: str) -> List[str]:
        """分割长段落"""
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
            
            if current_length + len(sentence) > self.chunk_size and current_chunk:
                chunk_text = ''.join(current_chunk)
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    chunks.append(chunk_text.strip())
                
                # 重叠
                if self.chunk_overlap > 0:
                    overlap_text = ''.join(current_chunk[-2:])
                    current_chunk = [overlap_text] if overlap_text else []
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(sentence)
            current_length += len(sentence)
        
        # 最后一个块
        if current_chunk:
            chunk_text = ''.join(current_chunk)
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunks.append(chunk_text.strip())
        
        return chunks
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        return self.preprocessor.clean_text(text)
    
    def _get_processed_files(self) -> set:
        """获取已处理文件列表"""
        processed_file = DATA_DIRS['processed'] / 'processed_files.json'
        if processed_file.exists():
            with open(processed_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()
    
    def _save_processed_files(self, processed_files: set):
        """保存已处理文件列表"""
        processed_file = DATA_DIRS['processed'] / 'processed_files.json'
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(list(processed_files), f, ensure_ascii=False, indent=2)
    
    def build(self, rebuild: bool = False, supported_formats: tuple = None) -> Dict[str, Any]:
        """构建 RAG 系统"""
        self.stats['start_time'] = datetime.now()
        supported_formats = supported_formats or ('.pdf', '.docx', '.txt', '.md')
        
        print("🚀 开始构建 RAG 系统...")
        print("=" * 60)
        
        # 重建模式：清空现有索引
        if rebuild:
            logging.info("重建模式：清空现有索引")
            self.store = VectorStoreFast(
                dim=self.embedder.dim,
                index_path=DATA_DIRS['embeddings'] / "index.faiss",
                metadata_path=DATA_DIRS['embeddings'] / "index.meta.jsonl",
                normalize=False,
                use_ivf=None,  # 自动判断：<10k用Flat，>=10k自动升级IVF
                nlist=100,
                m=8,
                nbits=8
            )
            self.indexer = Indexer(
                embedder=self.embedder,
                store=self.store,
                chunker=self.chunker,
                preprocessor=self._preprocess_text
            )
        
        processed_files = self._get_processed_files()
        
        # 扫描文件
        all_files = list(DATA_DIRS['raw'].rglob('*'))
        target_files = [f for f in all_files if f.suffix.lower() in supported_formats]
        self.stats['total_files'] = len(target_files)
        
        print(f"📁 发现 {self.stats['total_files']} 个支持的文件")
        
        # 处理文件
        for file_path in target_files:
            if not rebuild and str(file_path) in processed_files:
                logging.info(f"跳过已处理文件: {file_path}")
                continue
            
            try:
                ok = self._process_single_file(file_path)
                if ok:
                    self.stats['processed_files'] += 1
                    processed_files.add(str(file_path))
                    print(f"✅ {file_path.name}")
                else:
                    self.stats['failed_files'] += 1
                    hint = '空内容或无法提取文本'
                    if file_path.suffix.lower() == '.pdf':
                        hint += '（可能需要 OCR）'
                    self.stats['failed_file_details'].append({
                        'file': str(file_path),
                        'error': hint,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"⚠️  {file_path.name} - {hint}")
            
            except Exception as e:
                self.stats['failed_files'] += 1
                error_info = {
                    'file': str(file_path),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.stats['failed_file_details'].append(error_info)
                logging.error(f"处理失败 {file_path}: {e}")
                print(f"❌ {file_path.name} - {e}")
        
        # 保存索引
        self.store.save()
        self._save_processed_files(processed_files)
        
        self.stats['end_time'] = datetime.now()
        self.stats['total_chunks'] = self.store.size
        
        # 输出结果
        print("\n" + "=" * 60)
        print("✅ 构建完成！")
        print(f"📁 总文件数: {self.stats['total_files']}")
        print(f"✅ 成功处理: {self.stats['processed_files']}")
        print(f"❌ 失败文件: {self.stats['failed_files']}")
        print(f"📄 总块数: {self.stats['total_chunks']}")
        print(f"⏱️  处理时间: {self.stats['end_time'] - self.stats['start_time']}")
        
        if self.stats['failed_file_details']:
            print(f"\n❌ 失败文件详情:")
            for detail in self.stats['failed_file_details']:
                print(f"  - {Path(detail['file']).name}: {detail['error']}")
        
        return self.stats
    
    def _process_single_file(self, file_path: Path) -> bool:
        """处理单个文件"""
        logging.info(f"开始处理文件: {file_path}")
        
        # 加载文件
        content = self.loader.load(str(file_path))
        if not content or not content.strip():
            return False
        
        # 预处理
        cleaned_text = self.preprocessor.clean_text(content)
        if not cleaned_text.strip():
            return False
        
        # 保存处理后的文本
        processed_file = DATA_DIRS['processed'] / f"{file_path.stem}.txt"
        processed_file.write_text(cleaned_text, encoding='utf-8')
        
        # 分块、嵌入和索引
        chunk_ids = self.indexer.index_file(processed_file, file_id=str(file_path))
        
        logging.info(f"文件 {file_path.name} 处理完成，生成 {len(chunk_ids)} 个块")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        if self.store.size == 0:
            logging.warning("向量库为空")
            return []
        
        query_processed = self._preprocess_text(query)
        query_vector = self.embedder.encode([query_processed], normalize=True)[0]
        results = self.store.search(query_vector, top_k=top_k, include_metadata=True)
        
        return results
    
    def interactive_search(self):
        """交互式搜索"""
        print("\n🎯 交互式搜索模式")
        print("输入查询词进行搜索，输入 'quit' 退出")
        print("-" * 60)
        
        if self.store.size == 0:
            print("❌ 向量库为空，请先构建 RAG 系统")
            return
        
        while True:
            try:
                query = input("\n🔍 请输入查询词: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 再见！")
                    break
                
                if not query:
                    continue
                
                results = self.search(query, top_k=5)
                
                if not results:
                    print("📭 未找到相关结果")
                    continue
                
                print(f"\n找到 {len(results)} 个相关结果:")
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
    
    def get_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        info = {
            'vector_store_size': self.store.size,
            'embedding_dimension': self.embedder.dim,
            'embedding_model': self.embedding_model,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'min_chunk_size': self.min_chunk_size,
            'index_path': str(DATA_DIRS['embeddings'] / "index.faiss"),
            'metadata_path': str(DATA_DIRS['embeddings'] / "index.meta.jsonl"),
        }
        
        # 统计文件类型分布
        if self.store.size > 0:
            file_types = {}
            for meta in self.store.iter_metadata():
                ext = Path(meta['file']).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            info['file_type_distribution'] = file_types
        
        return info
    
    def print_info(self):
        """打印系统信息"""
        info = self.get_info()
        
        print("\n📊 RAG 系统信息")
        print("=" * 60)
        print(f"向量库大小: {info['vector_store_size']} 个块")
        print(f"嵌入模型: {info['embedding_model']}")
        print(f"嵌入维度: {info['embedding_dimension']}")
        print(f"分块大小: {info['chunk_size']}")
        print(f"分块重叠: {info['chunk_overlap']}")
        print(f"最小块长: {info['min_chunk_size']}")
        print(f"索引路径: {info['index_path']}")
        
        if 'file_type_distribution' in info:
            print("\n文件类型分布:")
            for ext, count in info['file_type_distribution'].items():
                print(f"  {ext}: {count} 个块")
    
    def export_metadata(self, output_file: str = "rag_metadata_export.json") -> Path:
        """导出元数据"""
        metadata_list = list(self.store.iter_metadata())
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_chunks': len(metadata_list),
            'system_info': self.get_info(),
            'metadata': metadata_list
        }
        
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"📊 元数据已导出到: {output_path}")
        return output_path


def cmd_build(args):
    """构建命令"""
    manager = RAGSystemManager(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        min_chunk_size=args.min_chunk_size,
        embedding_model=args.model,
        verbose=args.verbose
    )
    
    stats = manager.build(rebuild=args.rebuild)
    
    # 测试查询
    if args.test_query:
        print(f"\n🔍 测试查询: '{args.test_query}'")
        results = manager.search(args.test_query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"  {i}. 文件: {Path(result['file']).name}")
            print(f"     相似度: {result['score']:.4f}")
            print(f"     预览: {result['preview']}...")
    
    # 导出元数据
    if args.export_metadata:
        manager.export_metadata()


def cmd_search(args):
    """搜索命令"""
    manager = RAGSystemManager(verbose=args.verbose)
    
    if args.interactive:
        manager.interactive_search()
    elif args.query:
        results = manager.search(args.query, top_k=args.top_k)
        
        if not results:
            print("📭 未找到相关结果")
            return
        
        print(f"\n🔍 搜索: '{args.query}'")
        print(f"找到 {len(results)} 个相关结果:")
        
        for i, result in enumerate(results, 1):
            file_name = Path(result['file']).name
            print(f"\n{i}. 📄 {file_name}")
            print(f"   块ID: {result['chunk_id']}")
            print(f"   🎯 相似度: {result['score']:.4f}")
            print(f"   📝 内容预览:")
            print(f"   {result['preview']}...")
    else:
        print("❌ 请指定查询词或使用 --interactive 模式")


def cmd_info(args):
    """信息命令"""
    manager = RAGSystemManager(verbose=args.verbose)
    manager.print_info()


def cmd_export(args):
    """导出命令"""
    manager = RAGSystemManager(verbose=args.verbose)
    manager.export_metadata(args.output)


def cmd_benchmark(args):
    """基准测试命令"""
    print("🚀 启动性能基准测试...")
    print("请使用: python scripts/benchmark_rag_performance.py")
    print("或者运行: python -m scripts.benchmark_rag_performance")


def cmd_migrate(args):
    """迁移命令"""
    print("🔄 启动索引迁移...")
    print("请使用: python scripts/migrate_to_fast_index.py")
    if args.auto:
        print("       python scripts/migrate_to_fast_index.py --auto")


def cmd_check(args):
    """检查数据库对象状态"""
    with db_context() as db:
        print("\n📊 数据库状态检查")
        print("=" * 60)

        agent_count = db.query(Agent).count()
        user_count = db.query(User).count()
        prompt_count = db.query(SystemPrompt).count()

        print(f"🧠 Agent 数量: {agent_count}")
        if args.verbose and agent_count:
            for agent in db.query(Agent).order_by(Agent.id):
                print(f"  - ID: {agent.id}, 名称: {agent.name}, 展示名: {agent.display_name}, 类型: {agent.agent_type}")

        print(f"👤 用户数量: {user_count}")
        if args.verbose and user_count:
            for user in db.query(User).order_by(User.id):
                print(f"  - ID: {user.id}, 用户名: {user.username}, 角色: {user.role}")

        print(f"🗂️  Prompt 数量: {prompt_count}")
        if args.verbose and prompt_count:
            for prompt in db.query(SystemPrompt).order_by(SystemPrompt.id):
                print(f"  - ID: {prompt.id}, 名称: {prompt.name}, 状态: {prompt.status}, 语言: {prompt.language}, 默认: {prompt.is_default}")

        print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG 系统统一管理 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 构建 RAG 系统
  python scripts/rag_cli.py build --rebuild
  
  # 搜索文档
  python scripts/rag_cli.py search "钢铁生产流程" --top-k 5
  
  # 交互式搜索
  python scripts/rag_cli.py search --interactive
  
  # 查看系统信息
  python scripts/rag_cli.py info
  
  # 导出元数据
  python scripts/rag_cli.py export --output metadata.json
  
  # 性能测试
  python scripts/rag_cli.py benchmark
  
  # 索引迁移
  python scripts/rag_cli.py migrate --auto
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # build 子命令
    build_parser = subparsers.add_parser('build', help='构建 RAG 系统')
    build_parser.add_argument('--rebuild', action='store_true',
                             help='重建索引（清空现有数据）')
    build_parser.add_argument('--chunk-size', '-c', type=int, default=600,
                             help='分块大小 (默认: 600)')
    build_parser.add_argument('--chunk-overlap', type=int, default=100,
                             help='分块重叠 (默认: 100)')
    build_parser.add_argument('--min-chunk-size', type=int, default=50,
                             help='最小分块 (默认: 50)')
    build_parser.add_argument('--model', '-m', default='all-MiniLM-L6-v2',
                             help='嵌入模型 (默认: all-MiniLM-L6-v2)')
    build_parser.add_argument('--test-query', '-q',
                             help='构建后测试查询')
    build_parser.add_argument('--export-metadata', action='store_true',
                             help='导出元数据')
    
    # search 子命令
    search_parser = subparsers.add_parser('search', help='搜索文档')
    search_parser.add_argument('query', nargs='?', help='查询词')
    search_parser.add_argument('--top-k', '-k', type=int, default=5,
                              help='返回结果数 (默认: 5)')
    search_parser.add_argument('--interactive', '-i', action='store_true',
                              help='交互式搜索模式')
    
    # info 子命令
    info_parser = subparsers.add_parser('info', help='查看系统信息')
    
    # export 子命令
    export_parser = subparsers.add_parser('export', help='导出元数据')
    export_parser.add_argument('--output', '-o', default='rag_metadata_export.json',
                              help='输出文件 (默认: rag_metadata_export.json)')
    
    # benchmark 子命令
    benchmark_parser = subparsers.add_parser('benchmark', help='性能基准测试')
    
    # migrate 子命令
    migrate_parser = subparsers.add_parser('migrate', help='索引迁移')
    migrate_parser.add_argument('--auto', action='store_true',
                               help='自动模式（备份+迁移+替换）')
    
    check_parser = subparsers.add_parser('check', help='检查数据库状态（Agent、用户、Prompt）')
    check_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细列表')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 执行对应的命令
    command_handlers = {
        'build': cmd_build,
        'search': cmd_search,
        'info': cmd_info,
        'export': cmd_export,
        'benchmark': cmd_benchmark,
        'migrate': cmd_migrate,
        'check': cmd_check,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except Exception as e:
            logging.error(f"命令执行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

