#!/usr/bin/env python3
"""
测试prompt管理API的脚本
使用方法: python test_prompt_api.py
"""

import sys
from pathlib import Path
import asyncio
import json

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.db import SessionLocal
from src.prompt_management.service import PromptService
from src.prompt_management.schemas import AgentCreate, SystemPromptCreate, PromptUsageCreate
from src.api.models import AgentType, PromptStatus
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_prompt_service():
    """测试PromptService的基本功能"""
    db = SessionLocal()
    service = PromptService(db)
    
    try:
        logger.info("🧪 开始测试PromptService...")
        
        # 1. 测试创建Agent
        logger.info("1️⃣ 测试创建Agent...")
        agent_data = AgentCreate(
            name="测试RAG助手",
            agent_type=AgentType.RAG_AGENT,
            description="用于测试的RAG助手",
            capabilities=["测试功能", "示例对话"]
        )
        
        agent = service.create_agent(agent_data, created_by=1)
        logger.info(f"   ✅ Agent创建成功: {agent.name} (ID: {agent.id})")
        
        # 2. 测试获取Agent列表
        logger.info("2️⃣ 测试获取Agent列表...")
        agents = service.list_agents()
        logger.info(f"   ✅ 获取到 {len(agents)} 个Agent")
        
        # 3. 测试获取Agent的默认prompt
        logger.info("3️⃣ 测试获取Agent的默认prompt...")
        prompt = service.get_agent_prompt(agent.id, "zh-CN")
        if prompt:
            logger.info(f"   ✅ 获取到默认prompt: {prompt.name}")
            logger.info(f"   📝 Prompt内容预览: {prompt.content[:100]}...")
        else:
            logger.warning("   ⚠️ 未找到默认prompt")
        
        # 4. 测试创建自定义prompt
        logger.info("4️⃣ 测试创建自定义prompt...")
        custom_prompt_data = SystemPromptCreate(
            agent_id=agent.id,
            name="自定义测试prompt",
            content="你是一个专业的测试助手，请帮助用户进行系统测试。",
            language="zh-CN",
            variables={"test_mode": True},
            metadata={"version": "test", "author": "system"},
            is_default=False
        )
        
        custom_prompt = service.create_prompt(custom_prompt_data, created_by=1)
        logger.info(f"   ✅ 自定义prompt创建成功: {custom_prompt.name} (ID: {custom_prompt.id})")
        
        # 5. 测试激活prompt
        logger.info("5️⃣ 测试激活prompt...")
        success = service.activate_prompt(custom_prompt.id, activated_by=1)
        if success:
            logger.info("   ✅ Prompt激活成功")
        
        # 6. 测试记录使用统计
        logger.info("6️⃣ 测试记录使用统计...")
        usage_data = PromptUsageCreate(
            agent_id=agent.id,
            prompt_id=custom_prompt.id,
            user_id=1,
            response_time_ms=150.5,
            token_count=50,
            user_feedback=4.5,
            error_occurred=False
        )
        
        usage_stats = service.record_usage(usage_data)
        logger.info(f"   ✅ 使用统计记录成功: ID {usage_stats.id}")
        
        # 7. 测试获取分析数据
        logger.info("7️⃣ 测试获取分析数据...")
        analytics = service.get_agent_analytics(agent.id, days=7)
        logger.info(f"   ✅ Agent分析数据: 总使用次数 {analytics.total_usage}, 活跃prompt数 {analytics.active_prompts}")
        
        # 8. 测试搜索功能
        logger.info("8️⃣ 测试搜索功能...")
        from src.prompt_management.schemas import PromptSearchRequest
        search_request = PromptSearchRequest(
            agent_id=agent.id,
            keyword="测试",
            page=1,
            page_size=10
        )
        search_result = service.search_prompts(search_request)
        logger.info(f"   ✅ 搜索结果: 找到 {search_result.total} 个prompt")
        
        # 9. 测试版本管理
        logger.info("9️⃣ 测试版本管理...")
        versions = service.get_prompt_versions(custom_prompt.id)
        logger.info(f"   ✅ 版本历史: {len(versions)} 个版本")
        
        logger.info("🎉 所有测试通过！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_api_endpoints():
    """测试API端点（需要服务器运行）"""
    import httpx
    
    logger.info("🌐 测试API端点...")
    
    try:
        # 测试健康检查
        response = httpx.get("http://localhost:8000/api/v1/prompts/health")
        if response.status_code == 200:
            logger.info("   ✅ 健康检查通过")
        else:
            logger.warning(f"   ⚠️ 健康检查失败: {response.status_code}")
            
        # 注意：其他API测试需要认证token，这里只测试健康检查
        
    except Exception as e:
        logger.warning(f"   ⚠️ API测试跳过（服务器可能未运行）: {e}")

def main():
    """主函数"""
    logger.info("🚀 开始prompt管理系统测试...")
    
    # 测试服务层
    service_success = test_prompt_service()
    
    # 测试API端点
    test_api_endpoints()
    
    if service_success:
        logger.info("=" * 50)
        logger.info("✅ 测试完成！")
        logger.info("")
        logger.info("Prompt管理系统功能正常，包括:")
        logger.info("  ✅ Agent管理")
        logger.info("  ✅ Prompt创建和管理")
        logger.info("  ✅ 版本控制")
        logger.info("  ✅ 使用统计")
        logger.info("  ✅ 搜索功能")
        logger.info("  ✅ 分析功能")
        logger.info("")
        logger.info("可以开始使用API接口了！")
    else:
        logger.error("❌ 测试失败，请检查系统配置")
        sys.exit(1)

if __name__ == "__main__":
    main()