#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""文件迁移脚本：将旧的 data/raw 和 data/processed 文件迁移到知识库目录

使用场景：
- 首次启用双向量存储时，将现有文件迁移到知识库
- 确保旧文件能够被新系统检索到

运行方式：
    python scripts/migrate_files_to_kb.py [--dry-run]
"""

import sys
import shutil
from pathlib import Path
from typing import List, Tuple

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import get_settings


def migrate_files(dry_run: bool = False) -> Tuple[int, int]:
    """迁移文件到知识库目录
    
    Args:
        dry_run: 如果为 True，只打印操作不实际执行
    
    Returns:
        (成功数量, 失败数量)
    """
    settings = get_settings()
    
    # 旧目录
    old_raw_dir = Path("data/raw")
    old_processed_dir = Path("data/processed")
    
    # 新目录（知识库）
    kb_raw_dir = Path(settings.knowledge_base_raw_dir)
    kb_processed_dir = Path(settings.knowledge_base_processed_dir)
    
    success_count = 0
    failed_count = 0
    
    print("=" * 60)
    print("📦 文件迁移工具：旧目录 → 知识库目录")
    print("=" * 60)
    print()
    
    if dry_run:
        print("🔍 [试运行模式] 不会实际移动文件，仅显示操作计划\n")
    
    print(f"📂 旧目录:")
    print(f"   原始文件: {old_raw_dir.absolute()}")
    print(f"   处理文件: {old_processed_dir.absolute()}")
    print()
    print(f"📚 知识库目录:")
    print(f"   原始文件: {kb_raw_dir.absolute()}")
    print(f"   处理文件: {kb_processed_dir.absolute()}")
    print()
    
    # 检查旧目录是否存在
    if not old_raw_dir.exists():
        print(f"⚠️  旧原始文件目录不存在: {old_raw_dir}")
        print("✅ 无需迁移")
        return 0, 0
    
    # 收集需要迁移的文件
    raw_files: List[Path] = []
    processed_files: List[Path] = []
    
    # 扫描原始文件（排除隐藏文件和目录）
    if old_raw_dir.exists():
        for item in old_raw_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                raw_files.append(item)
    
    # 扫描处理文件
    if old_processed_dir.exists():
        for item in old_processed_dir.iterdir():
            if item.is_file() and not item.name.startswith('.'):
                processed_files.append(item)
    
    print(f"📊 发现文件:")
    print(f"   原始文件: {len(raw_files)} 个")
    print(f"   处理文件: {len(processed_files)} 个")
    print()
    
    if len(raw_files) == 0 and len(processed_files) == 0:
        print("✅ 没有需要迁移的文件")
        return 0, 0
    
    # 迁移原始文件
    print("🔄 开始迁移原始文件...")
    for file_path in raw_files:
        target_path = kb_raw_dir / file_path.name
        
        try:
            if target_path.exists():
                print(f"⏭️  跳过（已存在）: {file_path.name}")
                continue
            
            if dry_run:
                print(f"📝 [试运行] 将移动: {file_path.name}")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"✅ 已迁移: {file_path.name}")
            
            success_count += 1
        except Exception as e:
            print(f"❌ 失败: {file_path.name} - {e}")
            failed_count += 1
    
    print()
    
    # 迁移处理文件
    print("🔄 开始迁移处理文件...")
    for file_path in processed_files:
        target_path = kb_processed_dir / file_path.name
        
        try:
            if target_path.exists():
                print(f"⏭️  跳过（已存在）: {file_path.name}")
                continue
            
            if dry_run:
                print(f"📝 [试运行] 将移动: {file_path.name}")
            else:
                shutil.move(str(file_path), str(target_path))
                print(f"✅ 已迁移: {file_path.name}")
            
            success_count += 1
        except Exception as e:
            print(f"❌ 失败: {file_path.name} - {e}")
            failed_count += 1
    
    print()
    print("=" * 60)
    print("📊 迁移统计")
    print("=" * 60)
    print(f"✅ 成功: {success_count} 个文件")
    print(f"❌ 失败: {failed_count} 个文件")
    print()
    
    return success_count, failed_count


def migrate_vector_index(dry_run: bool = False) -> bool:
    """迁移向量索引到知识库索引
    
    Args:
        dry_run: 如果为 True，只打印操作不实际执行
    
    Returns:
        是否成功
    """
    settings = get_settings()
    
    old_index_path = Path("data/embeddings/index.faiss")
    old_meta_path = Path("data/embeddings/index.meta.jsonl")
    kb_index_path = Path(settings.knowledge_base_index_path)
    
    print("🔄 迁移向量索引...")
    print()
    
    if not old_index_path.exists():
        print("⚠️  旧向量索引不存在，跳过")
        return True
    
    try:
        if kb_index_path.exists():
            print(f"⚠️  知识库索引已存在: {kb_index_path}")
            print("   如需重新索引，请使用: python scripts/rag_cli.py build --rebuild")
            return True
        
        if dry_run:
            print(f"📝 [试运行] 将复制索引: {old_index_path} → {kb_index_path}")
            if old_meta_path.exists():
                print(f"📝 [试运行] 将复制元数据: {old_meta_path}")
        else:
            # 复制索引文件（不是移动，保留原文件以防问题）
            kb_index_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(old_index_path), str(kb_index_path))
            print(f"✅ 已复制索引: {kb_index_path}")
            
            # 复制元数据文件
            if old_meta_path.exists():
                kb_meta_path = kb_index_path.parent / (kb_index_path.stem + ".meta.jsonl")
                shutil.copy(str(old_meta_path), str(kb_meta_path))
                print(f"✅ 已复制元数据: {kb_meta_path}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ 索引迁移失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="迁移文件到知识库目录")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式（不实际移动文件）"
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="跳过向量索引迁移"
    )
    args = parser.parse_args()
    
    # 迁移文件
    success, failed = migrate_files(dry_run=args.dry_run)
    
    # 迁移向量索引
    if not args.skip_index:
        print()
        migrate_vector_index(dry_run=args.dry_run)
    
    print()
    if args.dry_run:
        print("🔍 试运行完成！使用以下命令执行实际迁移：")
        print("   python scripts/migrate_files_to_kb.py")
    else:
        print("✅ 迁移完成！")
        print()
        print("📝 后续步骤：")
        print("   1. 重新索引文件（如果索引未自动迁移）：")
        print("      python scripts/rag_cli.py build --rebuild")
        print("   2. 启动系统验证迁移结果：")
        print("      python manage.py start all")
        print("   3. 测试检索功能，确认文件可以被搜索到")
        print()
        print("⚠️  注意：旧目录的文件已移动到知识库，如果一切正常，可以删除空目录：")
        print("   rm -rf data/raw data/processed")
    
    # 返回退出码
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

