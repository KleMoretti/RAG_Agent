#!/usr/bin/env python3
"""重建知识库向量索引（从已处理的文件）"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processing.embedder import Embedder
from src.retrieval.vector_store_fast import VectorStoreFast
from config.settings import get_settings
import hashlib

def rebuild_index():
    print("=" * 80)
    print("🔨 重建知识库向量索引")
    print("=" * 80)
    
    settings = get_settings()
    kb_processed_dir = Path(settings.knowledge_base_processed_dir)
    kb_index_path = Path(settings.knowledge_base_index_path)
    kb_meta_path = kb_index_path.with_suffix('.meta.jsonl')
    
    # 1. 删除旧索引
    print("\n1️⃣ 删除旧索引文件...")
    if kb_index_path.exists():
        kb_index_path.unlink()
        print(f"   ✅ 已删除: {kb_index_path}")
    if kb_meta_path.exists():
        kb_meta_path.unlink()
        print(f"   ✅ 已删除: {kb_meta_path}")
    
    # 删除配置文件
    kb_config_path = kb_index_path.with_suffix('.config.json')
    if kb_config_path.exists():
        kb_config_path.unlink()
        print(f"   ✅ 已删除: {kb_config_path}")
    
    # 2. 扫描已处理的文件
    print(f"\n2️⃣ 扫描知识库处理文件: {kb_processed_dir}")
    chunks_files = list(kb_processed_dir.glob("*.chunks.jsonl"))
    print(f"   找到 {len(chunks_files)} 个文件")
    
    if not chunks_files:
        print("\n❌ 没有找到已处理的文件！请先上传文档。")
        return
    
    # 3. 加载所有分块
    print("\n3️⃣ 加载分块数据...")
    all_chunks = []
    all_metadatas = []
    
    for chunks_file in chunks_files:
        try:
            with chunks_file.open('r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        chunk_data = json.loads(line)
                        content = chunk_data.get('content', '')
                        if not content:
                            continue
                        
                        # 提取元数据
                        file_id = chunk_data.get('file_id', '')
                        file_name = chunk_data.get('file_name', '')
                        chunk_id = chunk_data.get('chunk_id', 0)
                        
                        all_chunks.append(content)
                        all_metadatas.append({
                            'file': str(kb_processed_dir / f"{file_id}.txt"),  # 必需字段
                            'file_id': file_id,
                            'file_name': file_name,
                            'chunk_id': chunk_id,
                            'hash': hashlib.md5(content.encode('utf-8')).hexdigest(),
                            'preview': content[:100],
                            'upload_type': 'knowledge_base',
                        })
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"   ⚠️ 读取文件失败: {chunks_file.name} - {e}")
            continue
    
    print(f"   ✅ 加载了 {len(all_chunks)} 个分块")
    
    if not all_chunks:
        print("\n❌ 没有有效的分块数据！")
        return
    
    # 4. 生成向量
    print("\n4️⃣ 生成向量嵌入...")
    emb = Embedder()
    vectors = emb.encode(all_chunks, normalize=True)
    print(f"   ✅ 生成了 {len(vectors)} 个向量")
    
    # 5. 创建新索引
    print("\n5️⃣ 创建向量索引...")
    vector_store = VectorStoreFast(
        dim=emb.dim,
        index_path=str(kb_index_path),
        normalize=False,
        use_ivf=None,  # 自动选择
    )
    
    # 6. 添加向量
    print("\n6️⃣ 添加向量到索引...")
    ids = vector_store.add(vectors, all_metadatas)
    print(f"   ✅ 已添加 {len(ids)} 个向量")
    
    # 7. 保存索引
    print("\n7️⃣ 保存索引到磁盘...")
    vector_store.save()
    print(f"   ✅ 已保存: {kb_index_path}")
    
    # 8. 验证
    print("\n8️⃣ 验证索引...")
    vector_store_verify = VectorStoreFast(
        dim=emb.dim,
        index_path=str(kb_index_path),
    )
    vector_store_verify.load()
    print(f"   ✅ 索引大小: {vector_store_verify.size}")
    
    # 检查元数据
    if kb_meta_path.exists():
        meta_lines = [l for l in kb_meta_path.read_text(encoding='utf-8').split('\n') if l.strip()]
        print(f"   ✅ 元数据记录: {len(meta_lines)}")
        
        if len(meta_lines) == vector_store_verify.size:
            print(f"\n✅ 索引重建成功！向量和元数据已同步。")
        else:
            print(f"\n⚠️ 向量({vector_store_verify.size})和元数据({len(meta_lines)})仍不同步")
    
    print("\n" + "=" * 80)
    print("✅ 重建完成！现在可以正常使用RAG检索功能。")
    print("=" * 80)

if __name__ == "__main__":
    rebuild_index()

