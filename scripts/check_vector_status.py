#!/usr/bin/env python3
"""检查向量索引状态"""
import sys
from pathlib import Path
import json

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import get_dual_vector_store

def main():
    print("=" * 60)
    print("📊 向量索引状态检查")
    print("=" * 60)
    
    # 1. 检查向量存储
    dual_store = get_dual_vector_store()
    print(f"\n✅ 知识库向量数: {dual_store.kb_store.size}")
    print(f"✅ 用户上传向量数: {dual_store.user_store.size}")
    print(f"✅ 总向量数: {dual_store.kb_store.size + dual_store.user_store.size}")
    
    # 2. 检查元数据
    kb_meta = Path('data/embeddings/knowledge_base.meta.jsonl')
    if kb_meta.exists():
        lines = [l for l in kb_meta.read_text(encoding='utf-8').strip().split('\n') if l.strip()]
        print(f"\n✅ 知识库元数据记录数: {len(lines)}")
        
        if lines:
            sample = json.loads(lines[0])
            print(f"✅ 元数据字段: {list(sample.keys())}")
            print(f"✅ file_id 示例: {sample.get('file_id', 'N/A')[:80]}")
            print(f"✅ file_name 示例: {sample.get('file_name', 'N/A')}")
            print(f"✅ upload_type: {sample.get('upload_type', 'N/A')}")
            
            # 检查是否同步
            if len(lines) == dual_store.kb_store.size:
                print(f"\n✅ 元数据和向量索引已同步！")
            else:
                print(f"\n⚠️ 元数据({len(lines)})和向量({dual_store.kb_store.size})不同步")
    else:
        print("\n❌ 知识库元数据文件不存在")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

