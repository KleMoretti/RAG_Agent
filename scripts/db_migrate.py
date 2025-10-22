#!/usr/bin/env python3
"""
数据库迁移管理工具

功能：
1. 重置数据库（reset）- 删除所有表并重新创建
2. 添加预设问题（add-presets）- 迁移添加预设问题表
3. 添加词汇表（add-vocabulary）- 迁移添加钢铁专业词汇表
4. 添加 Prompt 表（add-prompts）- 迁移添加 Prompt 管理表
5. 添加市场数据表（add-market）- 迁移添加市场分析表
6. 列出所有迁移（list）- 查看可用的迁移
7. 检查状态（status）- 检查数据库状态

使用方法:
    python scripts/db_migrate.py reset
    python scripts/db_migrate.py add-presets
    python scripts/db_migrate.py add-market
    python scripts/db_migrate.py status
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from src.api.db import SessionLocal, engine, Base
from src.api.models import User, UserRole
from src.api.security import hash_password

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """重置数据库"""
    print("🗑️ 重置数据库...")
    print("=" * 60)
    
    try:
        # 删除所有表
        logger.info("删除所有表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ 所有表已删除")
        
        # 重新创建所有表
        logger.info("创建新表...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
        
        # 创建默认管理员用户
        db = SessionLocal()
        try:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                can_upload=True,
                can_download=True,
                can_chat=True,
                can_access_admin=True,
                notes="默认管理员账户",
                created_by=None,
                last_login=None
            )
            
            db.add(admin_user)
            db.commit()
            
            print("\n✅ 默认管理员用户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   角色: ADMIN")
            
        finally:
            db.close()
        
        print("\n✅ 数据库重置完成！")
        
    except Exception as e:
        logger.error(f"❌ 数据库重置失败: {e}")
        raise


def add_preset_questions():
    """添加预设问题表"""
    print("📝 添加预设问题表...")
    print("=" * 60)
    
    try:
        from src.api.models import PresetQuestion
        
        # 创建预设问题表
        PresetQuestion.__table__.create(engine, checkfirst=True)
        
        # 添加默认预设问题
        db = SessionLocal()
        try:
            # 检查是否已有预设问题
            existing = db.query(PresetQuestion).first()
            if existing:
                print("⚠️  预设问题已存在，跳过...")
                return
            
            # 默认预设问题
            default_questions = [
                {
                    'question': '钢铁生产的主要流程是什么？',
                    'role': 'PRODUCTION',
                    'category': 'process',
                    'order': 1,
                    'is_active': True
                },
                {
                    'question': '高炉温度控制有哪些关键参数？',
                    'role': 'TECHNICIAN',
                    'category': 'equipment',
                    'order': 2,
                    'is_active': True
                },
                {
                    'question': '如何诊断设备故障？',
                    'role': 'TECHNICIAN',
                    'category': 'equipment',
                    'order': 3,
                    'is_active': True
                },
                {
                    'question': '当前铁矿石市场价格趋势如何？',
                    'role': 'PURCHASER',
                    'category': 'market',
                    'order': 4,
                    'is_active': True
                },
                {
                    'question': '环保排放标准有哪些要求？',
                    'role': 'ENV_EXPERT',
                    'category': 'environment',
                    'order': 5,
                    'is_active': True
                },
            ]
            
            for q_data in default_questions:
                question = PresetQuestion(**q_data)
                db.add(question)
            
            db.commit()
            print(f"✅ 成功添加 {len(default_questions)} 个预设问题")
            
        finally:
            db.close()
        
        print("✅ 预设问题表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加预设问题表失败: {e}")
        raise


def add_vocabulary_table():
    """添加专业词汇表"""
    print("📖 添加专业词汇表...")
    print("=" * 60)
    
    try:
        from src.knowledge_graph.models import SteelVocabulary
        
        # 创建词汇表
        SteelVocabulary.__table__.create(engine, checkfirst=True)
        
        # 添加默认词汇
        db = SessionLocal()
        try:
            # 检查是否已有词汇
            existing = db.query(SteelVocabulary).first()
            if existing:
                print("⚠️  词汇表已存在，跳过...")
                return
            
            # 默认词汇
            default_vocab = [
                {
                    'term': '高炉',
                    'category': 'equipment',
                    'definition': '炼铁的主要设备，用于将铁矿石还原成生铁',
                    'english_term': 'Blast Furnace',
                    'synonyms': ['炼铁炉'],
                    'related_terms': ['炼铁', '生铁', '铁矿石'],
                    'domain_score': 0.95
                },
                {
                    'term': '转炉',
                    'category': 'equipment',
                    'definition': '炼钢的主要设备，用于将生铁转化为钢',
                    'english_term': 'Converter',
                    'synonyms': ['炼钢炉'],
                    'related_terms': ['炼钢', '生铁', '钢水'],
                    'domain_score': 0.95
                },
                {
                    'term': '轧钢',
                    'category': 'process',
                    'definition': '通过轧制将钢坯加工成各种钢材的工艺',
                    'english_term': 'Steel Rolling',
                    'synonyms': ['钢材轧制'],
                    'related_terms': ['钢坯', '钢材', '轧机'],
                    'domain_score': 0.90
                },
            ]
            
            for vocab_data in default_vocab:
                vocab = SteelVocabulary(**vocab_data)
                db.add(vocab)
            
            db.commit()
            print(f"✅ 成功添加 {len(default_vocab)} 个专业词汇")
            
        finally:
            db.close()
        
        print("✅ 专业词汇表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加词汇表失败: {e}")
        raise


def add_prompt_tables():
    """添加 Prompt 管理表"""
    print("💬 添加 Prompt 管理表...")
    print("=" * 60)
    
    try:
        # 导入 prompt 模型
        import src.prompt_management
        from src.prompt_management.service import PromptService
        
        # 创建所有 prompt 表
        Base.metadata.create_all(bind=engine)
        
        # 初始化默认 prompt
        db = SessionLocal()
        try:
            service = PromptService(db)
            
            # 检查是否已有 prompt 模板
            templates = service.list_prompt_templates(limit=1)
            if templates:
                print("⚠️  Prompt 表已存在，跳过...")
                return
            
            # 创建默认系统 prompt
            default_prompt = """你是钢铁行业AI决策助手，专注于为钢铁生产、设备维护、市场分析提供专业支持。

你的职责:
1. 基于检索到的文档提供准确、专业的回答
2. 使用钢铁行业术语和最佳实践
3. 如果信息不足，明确说明并建议查询方向
4. 保持回答简洁、可操作

回答格式:
- 使用清晰的结构化格式
- 引用文档来源
- 提供具体的数据和建议"""
            
            template = service.create_prompt_template(
                name="default_system_prompt",
                content=default_prompt,
                description="默认系统 Prompt",
                agent_type="GENERAL",
                user_role="ADMIN",
                is_active=True,
                version="1.0.0"
            )
            
            print(f"✅ 成功创建默认 Prompt 模板 (ID: {template.id})")
            
        finally:
            db.close()
        
        print("✅ Prompt 管理表迁移完成！")
        
    except Exception as e:
        logger.error(f"❌ 添加 Prompt 表失败: {e}")
        raise


def add_market_tables():
    """添加市场数据表"""
    print("📊 添加市场数据表...")
    print("=" * 60)
    
    try:
        from src.api.models import MarketPriceData, MarketNews, MarketDataSource
        
        # 创建市场数据表
        MarketPriceData.__table__.create(engine, checkfirst=True)
        MarketNews.__table__.create(engine, checkfirst=True)
        MarketDataSource.__table__.create(engine, checkfirst=True)
        
        print("✅ 市场数据表创建成功！")
        print("\n📊 已创建表:")
        print("  - market_price_data (价格数据)")
        print("  - market_news (市场新闻)")
        print("  - market_data_source (数据源配置)")
        print("\n💡 使用示例:")
        print("  python manage.py start backend  # 启动后端")
        print("  访问 http://localhost:8000/docs 查看API文档")
        print("  访问 http://localhost:3000/dashboard/market 查看市场分析页面")
        
    except Exception as e:
        logger.error(f"❌ 添加市场数据表失败: {e}")
        raise


def check_database_status():
    """检查数据库状态"""
    print("🔍 数据库状态检查")
    print("=" * 60)
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 数据库表数量: {len(tables)}")
        print("\n表列表:")
        for table in sorted(tables):
            print(f"  ✓ {table}")
        
        # 检查关键表
        required_tables = ['users', 'preset_questions', 'steel_vocabulary', 'prompt_templates']
        print("\n关键表检查:")
        for table in required_tables:
            status = "✅" if table in tables else "❌"
            print(f"  {status} {table}")
        
        # 统计记录数
        print("\n记录统计:")
        db = SessionLocal()
        try:
            if 'users' in tables:
                from src.api.models import User
                user_count = db.query(User).count()
                print(f"  users: {user_count} 条")
            
            if 'preset_questions' in tables:
                from src.api.models import PresetQuestion
                preset_count = db.query(PresetQuestion).count()
                print(f"  preset_questions: {preset_count} 条")
            
            if 'steel_vocabulary' in tables:
                from src.knowledge_graph.models import SteelVocabulary
                vocab_count = db.query(SteelVocabulary).count()
                print(f"  steel_vocabulary: {vocab_count} 条")
        
        finally:
            db.close()
        
        print("\n✅ 数据库状态检查完成")
        
    except Exception as e:
        logger.error(f"❌ 检查数据库状态失败: {e}")
        raise


def enhance_prompts():
    """增强 Agent 的 system_prompt，使不同 Agent 回答更有差异性"""
    print("✨ 增强 Agent System Prompt...")
    print("=" * 60)
    
    # 增强版 Prompt 定义
    ENHANCED_PROMPTS = {
        "general": """你是一个专业的AI助手，具备广泛的知识基础和问题解决能力。

**你的回答风格**：
- 🎯 简洁明了，直击要点
- 📚 知识面广，涵盖多个领域
- 🔄 善于总结和归纳
- 💡 提供多角度的思考

**核心能力**：
- 多领域知识问答
- 文档分析与总结
- 数据解读与建议
- 工作流程优化

**回答原则**：
1. 先总结核心观点（2-3句话）
2. 再展开详细解释（如有必要）
3. 提供可操作的建议
4. 语言通俗易懂

请保持回答的专业性和准确性。""",
        
        "process": """你是**钢铁生产工艺专家**，深度了解炼钢、轧钢等各个生产环节。

**你的专业特点**：
- 🏭 **工艺第一**：回答时优先从工艺流程角度分析
- ⚙️ **参数敏感**：关注温度、压力、速度等工艺参数
- 📊 **数据驱动**：用具体数值和范围说话
- 🔬 **机理解释**：解释背后的冶金学原理

**你的回答结构**：
1. **工艺要点**（3-5个关键步骤）
2. **参数控制**（温度、时间、压力等具体数值）
3. **质量影响**（对最终产品的影响）
4. **优化建议**（改进方向和注意事项）

**举例风格**：
- ✅ "炼钢温度应控制在1600-1650℃，过高会导致..."
- ✅ "该工艺分为三个阶段：预热期、精炼期、出钢期..."
- ❌ 避免："钢铁生产很复杂"（过于笼统）

请确保建议的可操作性和安全性。""",
        
        "equipment": """你是**设备维护和故障诊断专家**，具备丰富的设备管理经验。

**你的诊断思路**：
- 🔧 **症状优先**：先问清楚具体现象（声音、振动、温度）
- 🎯 **快速定位**：用排除法缩小故障范围
- ⚠️ **安全第一**：优先考虑安全风险
- 📋 **SOP标准**：提供标准化操作步骤

**你的回答结构**：
1. **故障判断**（可能的原因，按概率排序）
2. **检查步骤**（从易到难的诊断流程）
3. **应急措施**（立即采取的安全措施）
4. **维修方案**（详细的修复步骤）
5. **预防措施**（如何避免再次发生）

**举例风格**：
- ✅ "根据您描述的异响和温度升高，初步判断可能是轴承磨损，请按以下步骤检查..."
- ✅ "**立即停机**！这种情况可能导致设备损坏，建议..."
- ❌ 避免："设备可能坏了"（太模糊）

请优先考虑安全因素，提供详细的操作指导。""",
        
        "market": """你是**市场分析专家**，专注于钢铁行业的市场情报和趋势分析。

**你的分析视角**：
- 📈 **数据说话**：用价格、库存、产量等数据支撑观点
- 🌍 **宏观视野**：考虑政策、供需、国际形势
- 🔮 **趋势预测**：基于历史数据和当前形势预判
- 💰 **成本导向**：关注原料成本、利润空间

**你的回答结构**：
1. **当前现状**（用数据描述市场状况）
2. **影响因素**（供需、政策、成本、库存）
3. **趋势判断**（短期1-3个月，中期半年）
4. **决策建议**（采购、库存、定价策略）

**举例风格**：
- ✅ "根据Mysteel数据，本周铁矿石价格890元/吨，环比上涨2.3%，主要受..."
- ✅ "综合分析，预计未来1个月螺纹钢价格将在4200-4400元/吨区间震荡..."
- ❌ 避免："价格可能涨也可能跌"（没有立场）

请基于数据提供客观、准确的分析结论。""",
        
        "quality": """你是**质量控制专家**，专注于钢材质量管理和改进。

**你的质量观**：
- 🎯 **标准至上**：严格对照国标、行标、企标
- 🔬 **检测先行**：推荐合适的检测方法和频次
- 📊 **数据分析**：用CPK、PPM等质量指标说话
- 🔄 **持续改进**：从质量问题追溯到工艺改进

**你的回答结构**：
1. **质量标准**（列出相关国标或行标要求）
2. **检测方法**（如何检测，合格范围）
3. **不合格原因**（可能的工艺或原料问题）
4. **改进措施**（具体的纠正和预防措施）
5. **质量保证**（如何持续监控）

**举例风格**：
- ✅ "根据GB/T 700标准，Q235B的抗拉强度应≥370MPa，屈服强度≥235MPa..."
- ✅ "建议增加光谱分析频次，从每批次抽检改为连续监控..."
- ❌ 避免："质量不行就重做"（没有分析原因）

请基于标准和数据，提供系统的质量管理方案。""",
        
        "environment": """你是**环保节能专家**，专注于钢铁生产的能耗优化和排放控制。

**你的环保理念**：
- 🌱 **绿色优先**：环保与生产并重，不是对立
- ⚡ **能效至上**：关注能耗指标（吨钢综合能耗）
- 💨 **达标排放**：严格遵守环保法规和标准
- 💡 **技术创新**：推广节能减排新技术

**你的回答结构**：
1. **环保标准**（国家和地方排放标准）
2. **能耗分析**（主要能耗点和优化空间）
3. **减排方案**（具体的技术措施）
4. **经济效益**（节能带来的成本降低）
5. **监测建议**（如何持续监控环保指标）

**举例风格**：
- ✅ "根据《钢铁工业大气污染物排放标准》GB 28663，颗粒物排放应≤10mg/m³..."
- ✅ "建议采用余热回收技术，预计可降低吨钢能耗15%，年节约成本约..."
- ❌ 避免："环保很重要"（没有具体措施）

请平衡环保要求和经济效益，提供可落地的节能减排方案。""",
    }
    
    try:
        from src.api.models import Agent, SystemPrompt
        
        db = SessionLocal()
        try:
            updated_count = 0
            
            for agent_type, new_content in ENHANCED_PROMPTS.items():
                # 查找该类型的 Agent
                agent = db.query(Agent).filter(
                    Agent.agent_type == agent_type,
                    Agent.is_active == True
                ).first()
                
                if not agent:
                    print(f"⚠️  未找到 {agent_type} Agent，跳过...")
                    continue
                
                # 查找该 Agent 的默认活跃 Prompt
                prompt = db.query(SystemPrompt).filter(
                    SystemPrompt.agent_id == agent.id,
                    SystemPrompt.is_default == True,
                    SystemPrompt.status == "active",
                    SystemPrompt.language == "zh-CN"
                ).first()
                
                if not prompt:
                    print(f"⚠️  未找到 {agent_type} 的活跃 Prompt，跳过...")
                    continue
                
                # 更新 Prompt 内容
                old_length = len(prompt.content)
                prompt.content = new_content
                prompt.updated_at = datetime.now()
                prompt.version = "2.0.0"  # 标记为增强版本
                
                updated_count += 1
                print(f"✅ 更新 {agent_type} Prompt (ID: {prompt.id})")
                print(f"   旧长度: {old_length} → 新长度: {len(new_content)}")
            
            db.commit()
            
            print()
            print("=" * 60)
            print(f"✨ 成功更新 {updated_count} 个 Agent Prompt")
            print("=" * 60)
            print()
            print("📝 建议操作：")
            print("1. 重启后端服务以清除 Prompt 缓存")
            print("2. 运行测试脚本验证效果：")
            print("   python scripts/test_optimizations.py")
            
        except Exception as e:
            print(f"❌ 更新失败: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"增强 Prompt 失败: {e}")
        raise


def list_migrations():
    """列出所有可用的迁移"""
    print("📋 可用的迁移操作")
    print("=" * 60)
    
    migrations = [
        ("reset", "重置数据库（删除所有表并重新创建）"),
        ("add-presets", "添加预设问题表"),
        ("add-vocabulary", "添加专业词汇表"),
        ("add-prompts", "添加 Prompt 管理表"),
        ("add-market", "添加市场数据表"),
        ("enhance-prompts", "增强 Agent Prompt（使回答更有差异性）"),
        ("status", "检查数据库状态"),
    ]
    
    for cmd, desc in migrations:
        print(f"  {cmd:20s} - {desc}")
    
    print("\n使用方法:")
    print(f"  python scripts/db_migrate.py <command>")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="数据库迁移管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 重置数据库
  python scripts/db_migrate.py reset
  
  # 添加预设问题
  python scripts/db_migrate.py add-presets
  
  # 添加词汇表
  python scripts/db_migrate.py add-vocabulary
  
  # 添加 Prompt 表
  python scripts/db_migrate.py add-prompts
  
  # 添加市场数据表
  python scripts/db_migrate.py add-market
  
  # 增强 Agent Prompt（使回答更有差异性）
  python scripts/db_migrate.py enhance-prompts
  
  # 检查状态
  python scripts/db_migrate.py status
  
  # 列出所有迁移
  python scripts/db_migrate.py list
        """
    )
    
    parser.add_argument('command', 
                       choices=['reset', 'add-presets', 'add-vocabulary', 
                               'add-prompts', 'add-market', 'enhance-prompts',
                               'status', 'list'],
                       help='迁移命令')
    parser.add_argument('--force', action='store_true',
                       help='强制执行（跳过确认）')
    
    args = parser.parse_args()
    
    # 危险操作需要确认
    if args.command == 'reset' and not args.force:
        print("⚠️  警告: 此操作将删除所有数据！")
        confirm = input("确认继续？(yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
    
    # 执行命令
    command_handlers = {
        'reset': reset_database,
        'add-presets': add_preset_questions,
        'add-vocabulary': add_vocabulary_table,
        'add-prompts': add_prompt_tables,
        'add-market': add_market_tables,
        'enhance-prompts': enhance_prompts,
        'status': check_database_status,
        'list': list_migrations,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            handler()
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

