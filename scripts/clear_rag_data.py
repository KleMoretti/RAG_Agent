#!/usr/bin/env python3
"""
清理RAG数据脚本 - 删除向量库和处理后的文件

使用场景：
1. 清空所有数据，准备重新上传
2. 清理损坏的索引数据
3. 重置系统到初始状态

⚠️ 警告：此操作不可恢复！请确认后再执行。
"""
import shutil
from pathlib import Path
import argparse
import sys


def clear_vector_store(data_dir: Path, dry_run: bool = False):
    """清除向量库索引文件"""
    embed_dir = data_dir / "embeddings"
    
    files_to_remove = [
        # 旧版单索引（向后兼容）
        embed_dir / "index.faiss",
        embed_dir / "index.meta.jsonl",
        embed_dir / "index_fast.faiss",
        embed_dir / "index_fast.meta.jsonl",
        embed_dir / "index_fast.config.json",
        # 新版双索引
        embed_dir / "knowledge_base.faiss",
        embed_dir / "knowledge_base.meta.jsonl",
        embed_dir / "user_uploads.faiss",
        embed_dir / "user_uploads.meta.jsonl",
    ]
    
    removed_count = 0
    removed_size = 0
    
    print("\n[1] 清理向量库索引...")
    for file in files_to_remove:
        if file.exists():
            size = file.stat().st_size / 1024  # KB
            removed_size += size
            if dry_run:
                print(f"   [DRY RUN] 将删除: {file.name} ({size:.1f} KB)")
            else:
                file.unlink()
                print(f"   ✅ 已删除: {file.name} ({size:.1f} KB)")
            removed_count += 1
        else:
            print(f"   ⏭️  跳过（不存在）: {file.name}")
    
    return removed_count, removed_size


def clear_processed_files(data_dir: Path, dry_run: bool = False, keep_raw: bool = True):
    """清除处理后的文件"""
    processed_dir = data_dir / "processed"
    
    if not processed_dir.exists():
        print("\n[2] processed目录不存在，跳过")
        return 0, 0
    
    print("\n[2] 清理processed目录...")
    
    # 统计文件
    all_files = list(processed_dir.rglob("*"))
    files = [f for f in all_files if f.is_file()]
    
    removed_count = 0
    removed_size = 0
    
    for file in files:
        size = file.stat().st_size / 1024  # KB
        removed_size += size
        if dry_run:
            print(f"   [DRY RUN] 将删除: {file.name} ({size:.1f} KB)")
        else:
            file.unlink()
            removed_count += 1
    
    if not dry_run and removed_count > 0:
        print(f"   ✅ 已删除 {removed_count} 个文件 (总计 {removed_size:.1f} KB)")
    
    return removed_count, removed_size


def clear_raw_files(data_dir: Path, dry_run: bool = False):
    """清除原始上传文件（可选）"""
    raw_dir = data_dir / "raw"
    
    if not raw_dir.exists():
        print("\n[3] raw目录不存在，跳过")
        return 0, 0
    
    print("\n[3] 清理raw目录...")
    
    # 统计文件
    all_files = list(raw_dir.rglob("*"))
    files = [f for f in all_files if f.is_file()]
    
    removed_count = 0
    removed_size = 0
    
    for file in files:
        size = file.stat().st_size / 1024  # KB
        removed_size += size
        if dry_run:
            print(f"   [DRY RUN] 将删除: {file.name} ({size:.1f} KB)")
        else:
            file.unlink()
            removed_count += 1
    
    if not dry_run and removed_count > 0:
        print(f"   ✅ 已删除 {removed_count} 个文件 (总计 {removed_size:.1f} KB)")
    
    return removed_count, removed_size


def backup_data(data_dir: Path):
    """备份数据（可选）"""
    import datetime
    
    backup_dir = data_dir.parent / f"data_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\n[备份] 正在备份数据到 {backup_dir}...")
    
    try:
        shutil.copytree(data_dir, backup_dir)
        print(f"   ✅ 备份完成: {backup_dir}")
        return True
    except Exception as e:
        print(f"   ❌ 备份失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="清理RAG系统数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预览将要删除的文件（不实际删除）
  python scripts/clear_rag_data.py --dry-run
  
  # 清理向量库和processed文件（保留raw原始文件）
  python scripts/clear_rag_data.py
  
  # 清理所有数据（包括raw原始文件）
  python scripts/clear_rag_data.py --all
  
  # 清理前先备份
  python scripts/clear_rag_data.py --backup
  
  # 强制执行，不询问确认
  python scripts/clear_rag_data.py --force
"""
    )
    
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='预览模式，只显示将要删除的文件，不实际删除')
    parser.add_argument('--all', '-a', action='store_true',
                       help='删除所有数据，包括raw原始文件')
    parser.add_argument('--backup', '-b', action='store_true',
                       help='清理前先备份数据')
    parser.add_argument('--force', '-f', action='store_true',
                       help='强制执行，不询问确认')
    parser.add_argument('--data-dir', default='data',
                       help='数据目录路径（默认: data）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    if not data_dir.exists():
        print(f"❌ 错误：数据目录不存在: {data_dir}")
        return 1
    
    print("=" * 60)
    print("RAG数据清理工具")
    print("=" * 60)
    
    if args.dry_run:
        print("\n⚠️  预览模式（不会实际删除文件）")
    
    # 备份
    if args.backup and not args.dry_run:
        if not backup_data(data_dir):
            response = input("\n备份失败，是否继续清理？(y/N): ")
            if response.lower() != 'y':
                print("已取消")
                return 0
    
    # 确认
    if not args.force and not args.dry_run:
        print("\n⚠️  警告：此操作将删除以下数据：")
        print("  - 向量库索引（index.faiss, index.meta.jsonl）")
        print("  - 处理后的文件（processed目录）")
        if args.all:
            print("  - 原始上传文件（raw目录）")
        print("\n此操作不可恢复！")
        
        response = input("\n确认执行？(yes/N): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
    
    # 执行清理
    total_files = 0
    total_size = 0
    
    # 清理向量库
    count, size = clear_vector_store(data_dir, args.dry_run)
    total_files += count
    total_size += size
    
    # 清理processed
    count, size = clear_processed_files(data_dir, args.dry_run)
    total_files += count
    total_size += size
    
    # 清理raw（可选）
    if args.all:
        count, size = clear_raw_files(data_dir, args.dry_run)
        total_files += count
        total_size += size
    
    # 汇总
    print("\n" + "=" * 60)
    print("清理汇总")
    print("=" * 60)
    
    if args.dry_run:
        print(f"[DRY RUN] 将删除 {total_files} 个文件，总计 {total_size:.1f} KB ({total_size/1024:.1f} MB)")
        print("\n提示：使用不带 --dry-run 参数的命令来实际执行清理")
    else:
        print(f"✅ 已删除 {total_files} 个文件，总计 {total_size:.1f} KB ({total_size/1024:.1f} MB)")
        print("\n✅ 清理完成！")
        print("\n下一步：")
        print("  1. 启动后端: python manage.py start backend")
        print("  2. 访问前端，重新上传PDF文件")
        print("  3. 系统会自动生成正确的索引（包含file_id字段）")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

