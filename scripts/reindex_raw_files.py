#!/usr/bin/env python3
"""
批量重新索引脚本 - 从raw目录重新上传所有文件

使用场景：
1. 清理向量库后，批量重新索引现有PDF
2. 避免手动一个个上传文件
3. 自动生成包含file_id的正确metadata

前置条件：
- 后端服务已启动 (python manage.py start backend)
- data/raw/ 目录中有PDF文件
"""
import requests
from pathlib import Path
import argparse
import sys
from typing import List
import time


def reindex_file(file_path: Path, api_url: str, verbose: bool = False) -> dict:
    """重新索引单个文件"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            response = requests.post(api_url, files=files, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return {
                'success': True,
                'file': file_path.name,
                'chunks': len(result.get('chunks', [])),
                'file_id': result.get('file_id', ''),
                'message': result.get('message', '')
            }
        else:
            return {
                'success': False,
                'file': file_path.name,
                'error': f"HTTP {response.status_code}: {response.text[:200]}"
            }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'file': file_path.name,
            'error': "上传超时（60秒）"
        }
    except Exception as e:
        return {
            'success': False,
            'file': file_path.name,
            'error': str(e)
        }


def get_files_to_process(raw_dir: Path, extensions: tuple) -> List[Path]:
    """获取需要处理的文件"""
    files = []
    for ext in extensions:
        files.extend(raw_dir.glob(f"*{ext}"))
    return sorted(files, key=lambda x: x.name)


def main():
    parser = argparse.ArgumentParser(
        description="批量重新索引raw目录中的文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 重新索引所有PDF文件
  python scripts/reindex_raw_files.py
  
  # 指定自定义数据目录
  python scripts/reindex_raw_files.py --data-dir /path/to/data
  
  # 指定后端地址
  python scripts/reindex_raw_files.py --api-url http://localhost:8000
  
  # 详细模式
  python scripts/reindex_raw_files.py --verbose
  
  # 包含docx文件
  python scripts/reindex_raw_files.py --extensions .pdf .docx
  
  # 限制处理文件数量（测试用）
  python scripts/reindex_raw_files.py --limit 5
"""
    )
    
    parser.add_argument('--data-dir', default='data',
                       help='数据目录路径（默认: data）')
    parser.add_argument('--api-url', default='http://localhost:8000',
                       help='后端API地址（默认: http://localhost:8000）')
    parser.add_argument('--extensions', nargs='+', default=['.pdf'],
                       help='要处理的文件扩展名（默认: .pdf）')
    parser.add_argument('--limit', type=int,
                       help='限制处理的文件数量（用于测试）')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='每个文件之间的延迟秒数（默认: 0.5）')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出')
    parser.add_argument('--skip-errors', action='store_true',
                       help='遇到错误时继续处理下一个文件')
    
    args = parser.parse_args()
    
    # 检查数据目录
    data_dir = Path(args.data_dir)
    raw_dir = data_dir / "raw"
    
    if not raw_dir.exists():
        print(f"❌ 错误：raw目录不存在: {raw_dir}")
        return 1
    
    # 检查后端是否运行
    try:
        response = requests.get(f"{args.api_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠️  警告：后端健康检查失败")
    except:
        print(f"❌ 错误：无法连接到后端 {args.api_url}")
        print("   请确保后端已启动: python manage.py start backend")
        return 1
    
    # 获取文件列表
    files = get_files_to_process(raw_dir, tuple(args.extensions))
    
    if args.limit:
        files = files[:args.limit]
    
    if not files:
        print(f"❌ 未在 {raw_dir} 中找到文件（扩展名: {args.extensions}）")
        return 1
    
    print("=" * 60)
    print("批量重新索引工具")
    print("=" * 60)
    print(f"数据目录: {raw_dir}")
    print(f"API地址: {args.api_url}")
    print(f"文件数量: {len(files)}")
    print(f"文件类型: {', '.join(args.extensions)}")
    print("=" * 60)
    
    # 确认
    if not args.limit:
        response = input(f"\n确认重新索引 {len(files)} 个文件？(y/N): ")
        if response.lower() != 'y':
            print("已取消")
            return 0
    
    # 处理文件
    upload_api = f"{args.api_url}/api/upload"
    results = {
        'success': [],
        'failed': []
    }
    
    total_chunks = 0
    start_time = time.time()
    
    print(f"\n开始处理...\n")
    
    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {file_path.name}")
        
        result = reindex_file(file_path, upload_api, args.verbose)
        
        if result['success']:
            results['success'].append(result)
            total_chunks += result['chunks']
            print(f"  ✅ 成功: {result['chunks']} 个块")
            if args.verbose:
                print(f"     file_id: {result['file_id']}")
        else:
            results['failed'].append(result)
            print(f"  ❌ 失败: {result['error']}")
            if not args.skip_errors:
                response = input("     继续处理下一个文件？(Y/n): ")
                if response.lower() == 'n':
                    print("\n已中止")
                    break
        
        # 延迟，避免并发过多
        if i < len(files):
            time.sleep(args.delay)
    
    elapsed = time.time() - start_time
    
    # 汇总报告
    print("\n" + "=" * 60)
    print("处理汇总")
    print("=" * 60)
    print(f"✅ 成功: {len(results['success'])} 个文件")
    print(f"❌ 失败: {len(results['failed'])} 个文件")
    print(f"📄 总块数: {total_chunks}")
    print(f"⏱️  耗时: {elapsed:.1f} 秒")
    print(f"⚡ 平均速度: {elapsed/len(files):.1f} 秒/文件")
    
    # 失败详情
    if results['failed']:
        print("\n失败文件详情:")
        for result in results['failed']:
            print(f"  - {result['file']}: {result['error']}")
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("\n下一步：")
    print("  1. 运行诊断工具验证: python scripts/diagnose_rag.py")
    print("  2. 测试搜索: python scripts/rag_cli.py search '你的查询'")
    print("  3. 前端测试：访问聊天界面，询问文档内容")
    
    return 0 if not results['failed'] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已中断")
        sys.exit(1)

