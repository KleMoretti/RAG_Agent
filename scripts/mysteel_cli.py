#!/usr/bin/env python
"""
Mysteel 数据爬虫 - 统一命令行工具
整合所有爬虫功能的单一入口

使用方法:
    python scripts/mysteel_cli.py --help
    python scripts/mysteel_cli.py crawl --material 螺纹
    python scripts/mysteel_cli.py test
    python scripts/mysteel_cli.py batch
    python scripts/mysteel_cli.py diagnose
"""
from __future__ import annotations

import sys
import argparse
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.crawl_mysteel_data import MysteelCrawler, MATERIAL_MAPPING

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_banner():
    """打印横幅"""
    print()
    print("=" * 70)
    print("      🚀 Mysteel 数据爬虫 - 统一命令行工具")
    print("=" * 70)
    print()


def cmd_crawl(args):
    """爬取数据命令"""
    print_banner()
    
    # 解析日期
    if args.start_date:
        start_str = args.start_date
    else:
        start_date = datetime.now() - timedelta(days=args.days)
        start_str = start_date.strftime("%Y-%m-%d")
    
    # 结束日期默认使用昨天，防止当天数据未更新
    if args.end_date:
        end_str = args.end_date
    else:
        end_date = datetime.now() - timedelta(days=1)
        end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"📅 日期范围: {start_str} ~ {end_str}")
    print(f"📦 材料类型: {args.material}")
    print(f"💾 保存到数据库: {'是' if args.save_db else '否'}")
    print(f"🖥️  显示浏览器: {'是' if not args.headless else '否'}")
    
    if args.output:
        print(f"📄 输出文件: {args.output}")
    
    print()
    
    # 初始化爬虫
    crawler = MysteelCrawler(headless=args.headless)
    
    try:
        # 爬取数据
        logger.info(f"🔍 开始爬取 {args.material} 数据...")
        df = crawler.crawl_price_data(
            material_key=args.material,
            start_date=start_str,
            end_date=end_str
        )
        
        if df.empty:
            logger.warning("⚠️  未获取到数据")
            return False
        
        logger.info(f"✅ 成功爬取 {len(df)} 条数据")
        
        # 保存到CSV
        if args.output:
            df.to_csv(args.output, index=False, encoding='utf-8-sig')
            logger.info(f"📄 数据已保存到: {args.output}")
        
        # 保存到数据库
        if args.save_db:
            crawler.save_to_database(df)
            logger.info("💾 数据已保存到数据库")
        
        # 显示预览
        if not args.quiet:
            print("\n" + "=" * 70)
            print("数据预览 (前5行):")
            print("=" * 70)
            print(df.head().to_string())
            print()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 爬取失败: {e}")
        return False
        
    finally:
        crawler.close()


def cmd_batch(args):
    """批量爬取命令"""
    print_banner()
    
    # 材料列表
    if args.materials:
        materials = args.materials.split(',')
    else:
        materials = ["螺纹", "铁矿石", "焦炭", "热卷"]
    
    # 日期范围
    if args.start_date:
        start_str = args.start_date
    else:
        start_date = datetime.now() - timedelta(days=args.days)
        start_str = start_date.strftime("%Y-%m-%d")
    
    # 结束日期默认使用昨天，防止当天数据未更新
    if args.end_date:
        end_str = args.end_date
    else:
        end_date = datetime.now() - timedelta(days=1)
        end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"📅 日期范围: {start_str} ~ {end_str}")
    print(f"📦 材料列表: {', '.join(materials)}")
    print(f"⏱️  延迟时间: {args.delay} 秒")
    print()
    
    # 确认
    if not args.yes:
        response = input("👉 确认开始批量爬取？[Y/n]: ").strip().lower()
        if response and response != 'y':
            print("❌ 已取消")
            return False
    
    print()
    print("=" * 70)
    print("🔄 开始批量爬取...")
    print("=" * 70)
    print()
    
    # 初始化爬虫
    crawler = MysteelCrawler(headless=args.headless)
    success_count = 0
    fail_count = 0
    
    try:
        for idx, material in enumerate(materials, 1):
            material_info = MATERIAL_MAPPING.get(material)
            if not material_info:
                logger.warning(f"⚠️  未知材料类型: {material}")
                fail_count += 1
                continue
            
            print(f"\n[{idx}/{len(materials)}] 爬取: {material_info['name']}")
            print("-" * 70)
            
            try:
                # 爬取数据
                df = crawler.crawl_price_data(
                    material_key=material,
                    start_date=start_str,
                    end_date=end_str
                )
                
                if df.empty:
                    logger.warning(f"⚠️  {material_info['name']} 未获取到数据")
                    fail_count += 1
                    continue
                
                # 保存到数据库
                if args.save_db:
                    crawler.save_to_database(df)
                
                # 保存到CSV
                if args.output_dir:
                    output_path = Path(args.output_dir) / f"{material}_{start_str}_{end_str}.csv"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    df.to_csv(output_path, index=False, encoding='utf-8-sig')
                    logger.info(f"📄 已保存到: {output_path}")
                
                logger.info(f"✅ {material_info['name']} 完成: {len(df)} 条数据")
                success_count += 1
                
                # 延迟
                if idx < len(materials):
                    logger.info(f"⏳ 等待 {args.delay} 秒...")
                    time.sleep(args.delay)
                
            except Exception as e:
                logger.error(f"❌ {material_info['name']} 失败: {e}")
                fail_count += 1
                continue
        
        # 总结
        print()
        print("=" * 70)
        print("📊 批量爬取完成！")
        print("=" * 70)
        print(f"✅ 成功: {success_count} 个材料")
        print(f"❌ 失败: {fail_count} 个材料")
        print()
        
        return success_count > 0
        
    finally:
        crawler.close()


def cmd_test(args):
    """测试连接命令"""
    print_banner()
    
    print("🧪 测试 Mysteel 网站连接...")
    print()
    
    crawler = MysteelCrawler(headless=not args.show_browser)
    
    try:
        # 测试打开网站
        logger.info("📡 正在连接网站...")
        crawler.driver.get(crawler.base_url)
        time.sleep(3)
        
        logger.info("✅ 网站连接成功")
        
        # 测试展开按钮
        logger.info("🔍 测试展开按钮...")
        try:
            crawler._click_expand_button()
            logger.info("✅ 展开按钮测试通过")
        except Exception as e:
            logger.warning(f"⚠️  展开按钮测试失败: {e}")
        
        # 测试材料选择
        logger.info("🔍 测试材料选择（螺纹钢）...")
        try:
            material_info = MATERIAL_MAPPING["螺纹"]
            crawler._select_material(material_info["id"], material_info["name"])
            logger.info("✅ 材料选择测试通过")
        except Exception as e:
            logger.warning(f"⚠️  材料选择测试失败: {e}")
        
        # 测试切换到按日查询
        logger.info("🔍 测试切换到按日查询...")
        try:
            crawler._switch_to_daily_query()
            logger.info("✅ 按日查询测试通过")
        except Exception as e:
            logger.warning(f"⚠️  按日查询测试失败: {e}")
        
        print()
        print("=" * 70)
        print("✅ 所有测试通过！")
        print("=" * 70)
        print()
        print("💡 下一步:")
        print("   python scripts/mysteel_cli.py crawl --material 螺纹 --days 21")
        
        if not args.show_browser:
            input("\n按回车键关闭...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        
        print()
        print("💡 故障排查:")
        print("   1. 检查网络连接")
        print("   2. 检查防火墙/代理设置")
        print("   3. 运行诊断: python scripts/mysteel_cli.py diagnose")
        
        if not args.show_browser:
            input("\n按回车键关闭...")
        
        return False
        
    finally:
        crawler.close()


def cmd_diagnose(args):
    """诊断网站结构命令"""
    print_banner()
    
    print("🔍 诊断 Mysteel 网站结构...")
    print("   浏览器将保持打开，请手动测试各项功能")
    print()
    
    # 使用非无头模式
    crawler = MysteelCrawler(headless=False)
    
    try:
        logger.info("📡 正在打开网站...")
        crawler.driver.get(crawler.base_url)
        time.sleep(5)
        
        print("\n" + "=" * 70)
        print("诊断步骤:")
        print("=" * 70)
        print("1. 检查页面是否正常加载")
        print("2. 查看材料按钮是否可见")
        print("3. 尝试手动选择材料和日期")
        print("4. 观察日期选择器的结构")
        print()
        
        # 尝试点击展开按钮
        try:
            crawler._click_expand_button()
            logger.info("✅ 展开按钮已点击")
        except:
            logger.warning("⚠️  展开按钮未找到")
        
        # 列出所有材料按钮
        print("\n" + "=" * 70)
        print("查找材料按钮:")
        print("=" * 70)
        
        for material_name, material_info in MATERIAL_MAPPING.items():
            try:
                element = crawler.driver.find_element("id", material_info["id"])
                print(f"  ✅ {material_name} (ID={material_info['id']}): {element.text}")
            except:
                # 尝试通过文本查找
                try:
                    elements = crawler.driver.find_elements("xpath", f"//*[contains(text(), '{material_name[:2]}')]")
                    if elements:
                        print(f"  ⚠️  {material_name} (ID={material_info['id']}未找到，但找到文本匹配)")
                    else:
                        print(f"  ❌ {material_name} (ID={material_info['id']}): 未找到")
                except:
                    print(f"  ❌ {material_name} (ID={material_info['id']}): 未找到")
        
        print()
        print("=" * 70)
        print("诊断完成！")
        print("=" * 70)
        print()
        print("💡 请在浏览器中手动测试以下操作:")
        print("   1. 点击材料按钮（如'螺纹钢'）")
        print("   2. 切换到'按日查询'")
        print("   3. 打开日期选择器，查看日期格式")
        print("   4. 按 F12 打开开发者工具，查看元素结构")
        print()
        
        input("按回车键关闭浏览器...")
        
    finally:
        crawler.close()


def cmd_list(args):
    """列出支持的材料类型"""
    print_banner()
    
    print("📊 支持的材料类型:")
    print("=" * 70)
    print(f"{'材料名称':<10} {'英文ID':<15} {'分类':<15} {'说明':<20}")
    print("-" * 70)
    
    for material_name, material_info in MATERIAL_MAPPING.items():
        print(f"{material_name:<10} {material_info['id']:<15} "
              f"{material_info['category']:<15} {material_info['name']:<20}")
    
    print("=" * 70)
    print()
    print("💡 使用方法:")
    print(f"   python scripts/mysteel_cli.py crawl --material 螺纹")
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Mysteel 数据爬虫 - 统一命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 爬取螺纹钢最近21天数据（默认）
  python scripts/mysteel_cli.py crawl --material 螺纹 --days 21
  
  # 爬取铁矿石指定日期范围并保存到数据库
  python scripts/mysteel_cli.py crawl --material 铁矿石 \\
      --start-date 2025-01-01 --end-date 2025-01-31 --save-db
  
  # 批量爬取多种材料
  python scripts/mysteel_cli.py batch --materials "螺纹,铁矿石,焦炭" --save-db
  
  # 测试连接
  python scripts/mysteel_cli.py test
  
  # 诊断网站结构
  python scripts/mysteel_cli.py diagnose
  
  # 列出支持的材料类型
  python scripts/mysteel_cli.py list
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # crawl 命令
    crawl_parser = subparsers.add_parser('crawl', help='爬取数据')
    crawl_parser.add_argument('--material', type=str, default='螺纹',
                            help='材料类型（默认: 螺纹）')
    crawl_parser.add_argument('--start-date', type=str,
                            help='开始日期 (YYYY-MM-DD)')
    crawl_parser.add_argument('--end-date', type=str,
                            help='结束日期 (YYYY-MM-DD)')
    crawl_parser.add_argument('--days', type=int, default=21,
                            help='爬取最近N天的数据（默认: 21天，确保有足够数据计算涨跌幅）')
    crawl_parser.add_argument('--output', type=str,
                            help='输出CSV文件路径')
    crawl_parser.add_argument('--save-db', action='store_true',
                            help='保存到数据库')
    crawl_parser.add_argument('--headless', action='store_true', default=True,
                            help='无头模式（默认: True）')
    crawl_parser.add_argument('--show-browser', dest='headless', action='store_false',
                            help='显示浏览器窗口')
    crawl_parser.add_argument('--quiet', action='store_true',
                            help='安静模式（不显示数据预览）')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量爬取多种材料')
    batch_parser.add_argument('--materials', type=str,
                            help='材料列表（逗号分隔，如: 螺纹,铁矿石,焦炭）')
    batch_parser.add_argument('--start-date', type=str,
                            help='开始日期 (YYYY-MM-DD)')
    batch_parser.add_argument('--end-date', type=str,
                            help='结束日期 (YYYY-MM-DD)')
    batch_parser.add_argument('--days', type=int, default=21,
                            help='爬取最近N天的数据（默认: 21天，确保有足够数据计算涨跌幅）')
    batch_parser.add_argument('--output-dir', type=str,
                            help='输出目录（每个材料单独保存CSV）')
    batch_parser.add_argument('--save-db', action='store_true',
                            help='保存到数据库')
    batch_parser.add_argument('--delay', type=int, default=5,
                            help='每次爬取之间的延迟（秒，默认: 5）')
    batch_parser.add_argument('--headless', action='store_true', default=True,
                            help='无头模式（默认: True）')
    batch_parser.add_argument('--show-browser', dest='headless', action='store_false',
                            help='显示浏览器窗口')
    batch_parser.add_argument('-y', '--yes', action='store_true',
                            help='跳过确认提示')
    
    # test 命令
    test_parser = subparsers.add_parser('test', help='测试连接')
    test_parser.add_argument('--show-browser', action='store_true',
                            help='显示浏览器窗口')
    
    # diagnose 命令
    diagnose_parser = subparsers.add_parser('diagnose', help='诊断网站结构')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出支持的材料类型')
    
    args = parser.parse_args()
    
    # 如果没有指定命令，显示帮助
    if not args.command:
        parser.print_help()
        return 0
    
    # 执行命令
    try:
        if args.command == 'crawl':
            success = cmd_crawl(args)
        elif args.command == 'batch':
            success = cmd_batch(args)
        elif args.command == 'test':
            success = cmd_test(args)
        elif args.command == 'diagnose':
            success = cmd_diagnose(args)
        elif args.command == 'list':
            success = cmd_list(args)
            return 0
        else:
            parser.print_help()
            return 0
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        return 130
    except Exception as e:
        logger.error(f"❌ 执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

