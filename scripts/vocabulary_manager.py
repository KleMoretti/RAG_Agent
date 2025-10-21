#!/usr/bin/env python3
"""
专业词汇管理工具

提供命令行接口来管理专业词汇库，包括添加、导入、导出、搜索等功能。
"""

import sys
import csv
import argparse
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.db import SessionLocal
from src.api.models import Vocabulary
from src.vocabulary import VocabularyService, QueryEnhancer


# 钢铁行业默认词汇库
DEFAULT_VOCABULARY = [
    # 钢种牌号
    {"term": "Q235", "definition": "碳素结构钢，屈服强度≥235MPa", "category": "steel_grade", 
     "synonyms": ["碳素钢", "结构钢"], "related_terms": ["Q345", "抗拉强度", "屈服强度"]},
    {"term": "Q345", "definition": "低合金高强度结构钢，屈服强度≥345MPa", "category": "steel_grade",
     "synonyms": ["345钢", "低合金钢"], "related_terms": ["Q235", "Q420", "屈服强度"]},
    {"term": "Q420", "definition": "高强度结构钢，屈服强度≥420MPa", "category": "steel_grade",
     "synonyms": ["420钢"], "related_terms": ["Q345", "Q460", "高强钢"]},
    {"term": "304", "definition": "18-8型奥氏体不锈钢，耐腐蚀性能好", "category": "steel_grade",
     "synonyms": ["304不锈钢", "18-8不锈钢"], "related_terms": ["316", "316L", "不锈钢"]},
    {"term": "316L", "definition": "超低碳奥氏体不锈钢，耐腐蚀性能优异", "category": "steel_grade",
     "synonyms": ["316L不锈钢"], "related_terms": ["304", "316", "不锈钢"]},
    
    # 钢材类型
    {"term": "碳素钢", "definition": "含碳量较低的钢材，塑性和韧性较好", "category": "steel_type",
     "synonyms": ["碳钢"], "related_terms": ["合金钢", "不锈钢", "Q235"]},
    {"term": "不锈钢", "definition": "含铬量≥12%的耐腐蚀钢材", "category": "steel_type",
     "synonyms": ["不锈耐酸钢"], "related_terms": ["304", "316L", "铬"]},
    {"term": "合金钢", "definition": "除碳外还含有其他合金元素的钢材", "category": "steel_type",
     "synonyms": ["特殊钢"], "related_terms": ["碳素钢", "不锈钢", "合金元素"]},
    
    # 合金元素
    {"term": "碳", "definition": "钢中最重要的合金元素，影响强度和硬度", "category": "alloy_element",
     "synonyms": ["C", "含碳量"], "related_terms": ["硅", "锰", "碳素钢"]},
    {"term": "铬", "definition": "提高钢的耐腐蚀性和抗氧化性", "category": "alloy_element",
     "synonyms": ["Cr"], "related_terms": ["镍", "不锈钢", "耐腐蚀性"]},
    {"term": "镍", "definition": "提高钢的韧性和耐腐蚀性", "category": "alloy_element",
     "synonyms": ["Ni"], "related_terms": ["铬", "不锈钢", "韧性"]},
    {"term": "锰", "definition": "提高钢的强度和淬透性", "category": "alloy_element",
     "synonyms": ["Mn"], "related_terms": ["碳", "硅", "强度"]},
    
    # 材料性能
    {"term": "抗拉强度", "definition": "材料在拉伸试验中所能承受的最大拉应力", "category": "material_property",
     "synonyms": ["拉伸强度", "σb", "Rm"], "related_terms": ["屈服强度", "延伸率", "MPa"]},
    {"term": "屈服强度", "definition": "材料发生屈服现象时的应力值", "category": "material_property",
     "synonyms": ["σs", "ReL", "ReH"], "related_terms": ["抗拉强度", "塑性变形", "MPa"]},
    {"term": "延伸率", "definition": "材料拉伸断裂后的伸长率", "category": "material_property",
     "synonyms": ["伸长率", "δ", "A"], "related_terms": ["断面收缩率", "塑性", "韧性"]},
    {"term": "硬度", "definition": "材料抵抗局部变形，特别是塑性变形、压痕或划痕的能力", "category": "material_property",
     "synonyms": ["HB", "HRC", "HV"], "related_terms": ["强度", "耐磨性", "布氏硬度"]},
    
    # 工艺流程
    {"term": "炼钢", "definition": "将生铁通过氧化去碳等工艺转化为钢的过程", "category": "process",
     "synonyms": ["炼钢工艺"], "related_terms": ["转炉", "电炉", "生铁", "钢水"]},
    {"term": "热轧", "definition": "在再结晶温度以上进行的轧制工艺", "category": "process",
     "synonyms": ["热轧制"], "related_terms": ["冷轧", "热轧机", "钢板"]},
    {"term": "冷轧", "definition": "在再结晶温度以下进行的轧制工艺", "category": "process",
     "synonyms": ["冷轧制"], "related_terms": ["热轧", "冷轧机", "表面质量"]},
    {"term": "退火", "definition": "将钢材加热到适当温度后缓慢冷却的热处理工艺", "category": "process",
     "synonyms": ["退火处理"], "related_terms": ["正火", "淬火", "回火"]},
    {"term": "淬火", "definition": "将钢材加热到临界温度后快速冷却的热处理工艺", "category": "process",
     "synonyms": ["淬火处理"], "related_terms": ["回火", "退火", "硬度"]},
    
    # 设备名称
    {"term": "转炉", "definition": "炼钢的主要设备，用于将生铁转化为钢", "category": "equipment",
     "synonyms": ["炼钢炉", "BOF"], "related_terms": ["电炉", "炼钢", "钢水"]},
    {"term": "电炉", "definition": "利用电能产生热量进行炼钢的设备", "category": "equipment",
     "synonyms": ["电弧炉", "EAF"], "related_terms": ["转炉", "炼钢", "废钢"]},
    {"term": "热轧机", "definition": "用于热态轧制钢材的设备", "category": "equipment",
     "synonyms": ["热轧设备"], "related_terms": ["冷轧机", "热轧", "钢板"]},
    {"term": "冷轧机", "definition": "用于冷态轧制钢材的设备", "category": "equipment",
     "synonyms": ["冷轧设备"], "related_terms": ["热轧机", "冷轧", "钢板"]},
    
    # 应用领域
    {"term": "建筑结构", "definition": "用于建筑物承重结构的钢材应用", "category": "application",
     "synonyms": ["建筑用钢"], "related_terms": ["桥梁工程", "结构钢", "Q235"]},
    {"term": "汽车制造", "definition": "汽车车身和零部件制造用钢", "category": "application",
     "synonyms": ["汽车用钢"], "related_terms": ["冷轧板", "镀锌板", "高强钢"]},
    {"term": "压力容器", "definition": "承受压力的密闭容器用钢", "category": "application",
     "synonyms": ["容器用钢"], "related_terms": ["锅炉", "管道", "耐压钢"]},
    
    # 标准规范
    {"term": "GB/T", "definition": "中国国家推荐性标准", "category": "standard",
     "synonyms": ["国标"], "related_terms": ["GB", "ASTM", "JIS"]},
    {"term": "ASTM", "definition": "美国材料与试验协会标准", "category": "standard",
     "synonyms": ["美标"], "related_terms": ["GB/T", "AISI", "SAE"]},
    {"term": "JIS", "definition": "日本工业标准", "category": "standard",
     "synonyms": ["日标"], "related_terms": ["GB/T", "ASTM", "DIN"]},
]


def add_default_vocabulary(db):
    """添加默认词汇库"""
    print("🚀 开始添加钢铁行业默认词汇库...")
    print("=" * 60)
    
    added_count = 0
    skipped_count = 0
    
    for vocab_data in DEFAULT_VOCABULARY:
        # 检查是否已存在
        existing = db.query(Vocabulary).filter(
            Vocabulary.term == vocab_data["term"]
        ).first()
        
        if existing:
            print(f"⏭️  跳过已存在: {vocab_data['term']}")
            skipped_count += 1
            continue
        
        # 创建新词汇
        vocab = Vocabulary(
            term=vocab_data["term"],
            definition=vocab_data["definition"],
            category=vocab_data["category"],
            synonyms=vocab_data.get("synonyms", []),
            related_terms=vocab_data.get("related_terms", []),
            created_by=1  # 系统管理员
        )
        
        db.add(vocab)
        print(f"✅ 成功添加: {vocab_data['term']} ({vocab_data['category']})")
        added_count += 1
    
    db.commit()
    
    print("\n" + "=" * 60)
    print(f"📊 添加完成！")
    print(f"   新增: {added_count} 个")
    print(f"   跳过: {skipped_count} 个")
    print(f"   总计: {added_count + skipped_count} 个专业词汇")


def add_interactive(db):
    """交互式添加单个词汇"""
    print("📝 交互式添加专业词汇")
    print("=" * 60)
    
    term = input("术语名称: ").strip()
    if not term:
        print("❌ 术语名称不能为空")
        return
    
    # 检查是否已存在
    existing = db.query(Vocabulary).filter(Vocabulary.term == term).first()
    if existing:
        print(f"⚠️  词汇 '{term}' 已存在")
        return
    
    definition = input("定义: ").strip()
    if not definition:
        print("❌ 定义不能为空")
        return
    
    print("\n可选分类:")
    print("  1. steel_grade (钢种牌号)")
    print("  2. steel_type (钢材类型)")
    print("  3. alloy_element (合金元素)")
    print("  4. material_property (材料性能)")
    print("  5. process (工艺流程)")
    print("  6. equipment (设备名称)")
    print("  7. application (应用领域)")
    print("  8. standard (标准规范)")
    
    category = input("分类 (1-8): ").strip()
    category_map = {
        "1": "steel_grade", "2": "steel_type", "3": "alloy_element",
        "4": "material_property", "5": "process", "6": "equipment",
        "7": "application", "8": "standard"
    }
    category = category_map.get(category, "steel_grade")
    
    synonyms_input = input("同义词 (逗号分隔，可选): ").strip()
    synonyms = [s.strip() for s in synonyms_input.split(",") if s.strip()]
    
    related_input = input("相关术语 (逗号分隔，可选): ").strip()
    related_terms = [r.strip() for r in related_input.split(",") if r.strip()]
    
    # 创建词汇
    vocab = Vocabulary(
        term=term,
        definition=definition,
        category=category,
        synonyms=synonyms,
        related_terms=related_terms,
        created_by=1
    )
    
    db.add(vocab)
    db.commit()
    
    print("\n✅ 成功添加词汇:")
    print(f"   术语: {term}")
    print(f"   定义: {definition}")
    print(f"   分类: {category}")
    if synonyms:
        print(f"   同义词: {', '.join(synonyms)}")
    if related_terms:
        print(f"   相关术语: {', '.join(related_terms)}")


def import_from_csv(db, csv_path):
    """从CSV文件导入词汇"""
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"❌ 文件不存在: {csv_path}")
        return
    
    print(f"📥 从 {csv_path} 导入词汇...")
    print("=" * 60)
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    with csv_file.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                term = row.get('term', '').strip()
                if not term:
                    continue
                
                # 检查是否已存在
                existing = db.query(Vocabulary).filter(Vocabulary.term == term).first()
                if existing:
                    print(f"⏭️  跳过已存在: {term}")
                    skipped_count += 1
                    continue
                
                # 解析同义词和相关术语
                synonyms_str = row.get('synonyms', '')
                synonyms = [s.strip() for s in synonyms_str.split(',') if s.strip()]
                
                related_str = row.get('related_terms', '')
                related_terms = [r.strip() for r in related_str.split(',') if r.strip()]
                
                # 创建词汇
                vocab = Vocabulary(
                    term=term,
                    definition=row.get('definition', ''),
                    category=row.get('category', 'steel_grade'),
                    synonyms=synonyms,
                    related_terms=related_terms,
                    created_by=1
                )
                
                db.add(vocab)
                print(f"✅ 导入: {term}")
                added_count += 1
                
            except Exception as e:
                print(f"❌ 导入失败: {row.get('term', 'unknown')} - {e}")
                error_count += 1
    
    db.commit()
    
    print("\n" + "=" * 60)
    print(f"📊 导入完成！")
    print(f"   新增: {added_count} 个")
    print(f"   跳过: {skipped_count} 个")
    print(f"   失败: {error_count} 个")


def export_to_csv(db, csv_path):
    """导出词汇到CSV文件"""
    print(f"📤 导出词汇到 {csv_path}...")
    
    vocabs = db.query(Vocabulary).all()
    
    csv_file = Path(csv_path)
    with csv_file.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['term', 'definition', 'category', 'synonyms', 'related_terms'])
        
        for vocab in vocabs:
            synonyms = ','.join(vocab.synonyms) if vocab.synonyms else ''
            related = ','.join(vocab.related_terms) if vocab.related_terms else ''
            writer.writerow([
                vocab.term,
                vocab.definition,
                vocab.category,
                synonyms,
                related
            ])
    
    print(f"✅ 导出完成！共 {len(vocabs)} 个词汇")


def search_vocabulary(db, query):
    """搜索词汇"""
    print(f"🔍 搜索结果: \"{query}\"")
    print("=" * 60)
    
    vocab_service = VocabularyService(db)
    vocab_service.initialize()
    
    results = vocab_service.search_terms(query, limit=10)
    
    if not results:
        print("未找到匹配的词汇")
        return
    
    print(f"找到 {len(results)} 个匹配词汇:\n")
    
    for vocab in results:
        print(f"【{vocab.term}】")
        print(f"  ID: {vocab.id}")
        print(f"  定义: {vocab.definition}")
        print(f"  分类: {vocab.category}")
        if vocab.synonyms:
            print(f"  同义词: {', '.join(vocab.synonyms)}")
        if vocab.related_terms:
            print(f"  相关术语: {', '.join(vocab.related_terms)}")
        print(f"  创建时间: {vocab.created_at}")
        print()


def show_statistics(db):
    """显示统计信息"""
    vocab_service = VocabularyService(db)
    vocab_service.initialize()
    
    stats = vocab_service.get_statistics()
    
    print("📊 专业词汇库统计信息")
    print("=" * 60)
    print(f"总词汇数: {stats['total_terms']}")
    print(f"索引术语数: {stats['total_indexed_terms']} (包含同义词)")
    print(f"分类数: {stats['categories']}")
    print("\n分类分布:")
    
    for category, count in stats['category_distribution'].items():
        print(f"  - {category}: {count} 个词汇")


def test_query_enhancement(db, query):
    """测试查询增强功能"""
    print(f"🔍 原始查询: {query}")
    print("=" * 60)
    
    # 调试：先检查数据库中的词汇
    vocab_count = db.query(Vocabulary).count()
    print(f"📊 数据库中共有 {vocab_count} 个词汇")
    
    # 初始化服务
    vocab_service = VocabularyService(db)
    vocab_service.initialize()
    
    # 调试：检查缓存
    print(f"📦 缓存中共有 {len(vocab_service._term_index)} 个索引")
    
    # 调试：手动测试查找
    test_terms = ["Q235", "抗拉强度", "q235"]
    for term in test_terms:
        result = vocab_service.get_by_term(term)
        print(f"   查找 '{term}': {'找到' if result else '未找到'}")
    
    # 测试文本识别
    found_terms = vocab_service.find_terms_in_text(query)
    print(f"📝 在文本中识别到 {len(found_terms)} 个专业词汇")
    for t in found_terms:
        print(f"   - {t['term']} (位置: {t['position']})")
    
    print("\n" + "=" * 60)
    
    # 查询增强
    enhancer = QueryEnhancer(vocab_service)
    enhanced = enhancer.enhance(query, add_synonyms=True, add_related=True)
    
    print(f"📝 识别到专业词汇: {[t['term'] for t in enhanced.identified_terms]}")
    print(f"✨ 增强查询: {enhanced.enhanced_query}")
    
    if enhanced.vocabulary_context:
        print(f"\n{enhanced.vocabulary_context}")
    else:
        print("\n⚠️  未识别到专业词汇")


def main():
    parser = argparse.ArgumentParser(description="专业词汇管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # add-default 命令
    subparsers.add_parser('add-default', help='添加钢铁行业默认词汇库')
    
    # add-interactive 命令
    subparsers.add_parser('add-interactive', help='交互式添加单个词汇')
    
    # import 命令
    import_parser = subparsers.add_parser('import', help='从CSV文件导入词汇')
    import_parser.add_argument('csv_file', help='CSV文件路径')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='导出词汇到CSV文件')
    export_parser.add_argument('csv_file', help='CSV文件路径')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索词汇')
    search_parser.add_argument('query', help='搜索关键词')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示统计信息')
    
    # test-enhance 命令
    test_parser = subparsers.add_parser('test-enhance', help='测试查询增强功能')
    test_parser.add_argument('query', help='测试查询')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        if args.command == 'add-default':
            add_default_vocabulary(db)
        elif args.command == 'add-interactive':
            add_interactive(db)
        elif args.command == 'import':
            import_from_csv(db, args.csv_file)
        elif args.command == 'export':
            export_to_csv(db, args.csv_file)
        elif args.command == 'search':
            search_vocabulary(db, args.query)
        elif args.command == 'stats':
            show_statistics(db)
        elif args.command == 'test-enhance':
            test_query_enhancement(db, args.query)
    finally:
        db.close()


if __name__ == "__main__":
    main()

