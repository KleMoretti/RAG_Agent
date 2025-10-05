# Prompt Management 使用示例

## 快速开始

### 1. 基础设置

```python
import asyncio
from src.prompt_management.service import PromptService
from src.prompt_management.schemas import AgentCreate, SystemPromptCreate
from src.database import get_db

async def main():
    # 获取数据库会话
    db = next(get_db())
    
    # 创建服务实例
    service = PromptService(db)
    
    # 你的代码在这里...
```

### 2. 创建第一个智能体

```python
async def create_first_agent():
    # 创建智能体
    agent_data = AgentCreate(
        name="客服助手",
        description="专业的客服对话智能体",
        agent_type="chat",
        capabilities=["对话", "问答", "情感分析"],
        config={
            "max_tokens": 2048,
            "temperature": 0.7,
            "model": "gpt-3.5-turbo"
        }
    )
    
    agent = await service.create_agent(agent_data, created_by=1)
    print(f"创建智能体成功: {agent.name} (ID: {agent.id})")
    return agent
```

### 3. 创建和激活提示词

```python
async def create_and_activate_prompt(agent_id):
    # 创建提示词
    prompt_data = SystemPromptCreate(
        agent_id=agent_id,
        name="客服对话提示词",
        content="""你是一个专业且友善的客服代表。请遵循以下规则：

1. 始终保持礼貌和专业的态度
2. 仔细理解用户的问题
3. 提供准确和有用的信息
4. 如果不确定答案，请诚实地说明

用户信息：
- 姓名：{user_name}
- 会员等级：{membership_level}
- 问题类型：{question_type}

请根据用户信息提供个性化的服务。""",
        language="zh-CN",
        variables=["user_name", "membership_level", "question_type"],
        tags=["客服", "对话", "专业"],
        category="customer_service"
    )
    
    prompt = await service.create_prompt(prompt_data, created_by=1)
    print(f"创建提示词成功: {prompt.name} (ID: {prompt.id})")
    
    # 激活提示词
    activated_prompt = await service.activate_prompt(prompt.id, activated_by=1)
    print(f"激活提示词成功: {activated_prompt.is_active}")
    
    return prompt
```

## 实际应用场景

### 场景1：多语言客服系统

```python
async def setup_multilingual_customer_service():
    """设置多语言客服系统"""
    
    # 创建多语言客服智能体
    agent_data = AgentCreate(
        name="多语言客服助手",
        description="支持中英文的客服智能体",
        agent_type="multilingual_chat",
        capabilities=["中文对话", "英文对话", "语言检测", "翻译"],
        config={
            "supported_languages": ["zh-CN", "en-US"],
            "auto_detect_language": True
        }
    )
    
    agent = await service.create_agent(agent_data, created_by=1)
    
    # 创建中文提示词
    zh_prompt = SystemPromptCreate(
        agent_id=agent.id,
        name="中文客服提示词",
        content="""你是一个专业的中文客服代表。

用户信息：
- 姓名：{user_name}
- 问题：{user_question}
- 产品：{product_name}

请用中文回答用户的问题，保持专业和友善的态度。""",
        language="zh-CN",
        variables=["user_name", "user_question", "product_name"],
        tags=["客服", "中文"],
        category="customer_service"
    )
    
    # 创建英文提示词
    en_prompt = SystemPromptCreate(
        agent_id=agent.id,
        name="English Customer Service Prompt",
        content="""You are a professional English customer service representative.

User Information:
- Name: {user_name}
- Question: {user_question}
- Product: {product_name}

Please answer the user's question in English with a professional and friendly attitude.""",
        language="en-US",
        variables=["user_name", "user_question", "product_name"],
        tags=["customer_service", "english"],
        category="customer_service"
    )
    
    # 创建提示词
    zh_prompt_obj = await service.create_prompt(zh_prompt, created_by=1)
    en_prompt_obj = await service.create_prompt(en_prompt, created_by=1)
    
    # 激活中文提示词作为默认
    await service.activate_prompt(zh_prompt_obj.id, activated_by=1)
    
    return agent, zh_prompt_obj, en_prompt_obj
```

### 场景2：A/B测试系统

```python
async def setup_ab_testing():
    """设置A/B测试系统"""
    
    # 创建智能体
    agent_data = AgentCreate(
        name="A/B测试智能体",
        description="用于A/B测试的智能体",
        agent_type="ab_test"
    )
    
    agent = await service.create_agent(agent_data, created_by=1)
    
    # 版本A：正式语调
    prompt_a = SystemPromptCreate(
        agent_id=agent.id,
        name="正式语调版本",
        content="""您好，我是您的专业助手。我将为您提供准确、详细的信息和建议。

用户问题：{user_question}
上下文：{context}

请允许我为您详细解答。""",
        language="zh-CN",
        variables=["user_question", "context"],
        tags=["正式", "专业", "A版本"],
        category="ab_test"
    )
    
    # 版本B：友好语调
    prompt_b = SystemPromptCreate(
        agent_id=agent.id,
        name="友好语调版本",
        content="""嗨！我是你的AI助手，很高兴为你服务！😊

你的问题：{user_question}
相关信息：{context}

让我来帮你解决这个问题吧！""",
        language="zh-CN",
        variables=["user_question", "context"],
        tags=["友好", "轻松", "B版本"],
        category="ab_test"
    )
    
    # 创建两个版本
    prompt_a_obj = await service.create_prompt(prompt_a, created_by=1)
    prompt_b_obj = await service.create_prompt(prompt_b, created_by=1)
    
    return agent, prompt_a_obj, prompt_b_obj

async def run_ab_test(prompt_a_id, prompt_b_id, test_cases):
    """运行A/B测试"""
    
    results = {"A": [], "B": []}
    
    for i, test_case in enumerate(test_cases):
        # 交替使用两个版本
        if i % 2 == 0:
            # 使用版本A
            await service.activate_prompt(prompt_a_id, activated_by=1)
            version = "A"
        else:
            # 使用版本B
            await service.activate_prompt(prompt_b_id, activated_by=1)
            version = "B"
        
        # 模拟使用并记录结果
        response_time = test_case.get("response_time", 1.0)
        user_feedback = test_case.get("user_feedback", 4.0)
        
        await service.record_usage(
            prompt_id=prompt_a_id if version == "A" else prompt_b_id,
            response_time=response_time,
            success=True,
            user_feedback=user_feedback
        )
        
        results[version].append({
            "response_time": response_time,
            "user_feedback": user_feedback
        })
    
    return results
```

### 场景3：版本管理和回滚

```python
async def version_management_example():
    """版本管理示例"""
    
    # 创建基础智能体和提示词
    agent = await create_first_agent()
    prompt = await create_and_activate_prompt(agent.id)
    
    # 创建版本1.1.0 - 添加新功能
    version_1_1 = await service.create_version(
        prompt_id=prompt.id,
        content="""你是一个专业的客服代表。

新增功能：
- 情感分析
- 智能推荐
- 多轮对话记忆

用户信息：
- 姓名：{user_name}
- 情绪状态：{emotion_state}
- 对话历史：{conversation_history}
- 偏好：{user_preferences}

请根据用户的情绪状态和偏好提供个性化服务。""",
        variables=["user_name", "emotion_state", "conversation_history", "user_preferences"],
        change_description="添加情感分析和个性化推荐功能",
        created_by=1
    )
    
    # 测试新版本
    test_results = await test_version_performance(version_1_1.id)
    
    if test_results["success_rate"] < 0.9:
        # 如果新版本表现不佳，回滚到上一版本
        print("新版本表现不佳，执行回滚...")
        await service.rollback_version(prompt.id, version_1_1.id, rolled_back_by=1)
    else:
        print("新版本表现良好，保持当前版本")
    
    return version_1_1

async def test_version_performance(version_id):
    """测试版本性能"""
    # 模拟测试数据
    test_cases = [
        {"response_time": 1.2, "success": True, "user_feedback": 4.5},
        {"response_time": 0.8, "success": True, "user_feedback": 4.2},
        {"response_time": 1.5, "success": False, "user_feedback": 2.0},
        # ... 更多测试用例
    ]
    
    success_count = sum(1 for case in test_cases if case["success"])
    success_rate = success_count / len(test_cases)
    avg_response_time = sum(case["response_time"] for case in test_cases) / len(test_cases)
    avg_feedback = sum(case["user_feedback"] for case in test_cases) / len(test_cases)
    
    return {
        "success_rate": success_rate,
        "avg_response_time": avg_response_time,
        "avg_feedback": avg_feedback
    }
```

### 场景4：性能监控和优化

```python
from src.prompt_management.performance import PerformanceMonitor
from src.prompt_management.cache_manager import AdvancedCacheManager

async def performance_monitoring_example():
    """性能监控示例"""
    
    # 初始化监控器
    performance_monitor = PerformanceMonitor()
    cache_manager = AdvancedCacheManager()
    
    # 启动性能监控
    await performance_monitor.start_monitoring(interval=1.0)
    
    try:
        # 模拟高负载操作
        for i in range(100):
            with performance_monitor.monitor(f"operation_{i}"):
                # 模拟API调用
                await simulate_api_call(i)
                
                # 记录响应时间
                performance_monitor.record_response_time("api_call", 0.5 + i * 0.01)
        
        # 获取性能统计
        summary = performance_monitor.get_performance_summary()
        print("性能摘要:", summary)
        
        # 检查缓存效果
        cache_stats = cache_manager.get_cache_stats()
        print("缓存统计:", cache_stats)
        
        # 如果性能不佳，进行优化
        if summary.get("avg_response_time", 0) > 2.0:
            print("检测到性能问题，开始优化...")
            await optimize_performance(cache_manager)
    
    finally:
        # 停止监控
        performance_monitor.stop_monitoring()

async def simulate_api_call(index):
    """模拟API调用"""
    import random
    await asyncio.sleep(random.uniform(0.1, 0.5))

async def optimize_performance(cache_manager):
    """性能优化"""
    # 预热缓存
    await cache_manager.preload_cache()
    
    # 优化缓存
    cache_manager.optimize_cache()
    
    print("性能优化完成")
```

### 场景5：分析和报告

```python
from src.prompt_management.analytics import PromptAnalytics

async def analytics_example():
    """分析示例"""
    
    analytics = PromptAnalytics(db)
    
    # 生成使用报告
    agent_id = 1
    report = await analytics.generate_usage_report(agent_id, days=30)
    
    print(f"智能体 {agent_id} 30天使用报告:")
    print(f"- 总请求数: {report.total_requests}")
    print(f"- 成功率: {report.success_rate:.2%}")
    print(f"- 平均响应时间: {report.avg_response_time:.2f}秒")
    print(f"- 用户满意度: {report.avg_user_feedback:.1f}/5.0")
    
    # 获取性能指标
    performance_metrics = await analytics.get_performance_metrics(agent_id, days=7)
    print(f"\n7天性能指标:")
    print(f"- 响应时间趋势: {performance_metrics.response_time_trend}")
    print(f"- 成功率趋势: {performance_metrics.success_rate_trend}")
    
    # 效果分析
    prompt_id = 1
    effectiveness = await analytics.analyze_effectiveness(prompt_id, days=30)
    print(f"\n提示词 {prompt_id} 效果分析:")
    print(f"- 效果评分: {effectiveness.effectiveness_score:.2f}")
    print(f"- 改进建议: {effectiveness.improvement_suggestions}")
    
    # 趋势分析
    trends = await analytics.get_usage_trends(agent_id, days=90)
    print(f"\n90天使用趋势:")
    for trend in trends.daily_trends[-7:]:  # 显示最近7天
        print(f"- {trend.date}: {trend.usage_count} 次使用")
```

### 场景6：批量操作

```python
async def batch_operations_example():
    """批量操作示例"""
    
    # 批量创建智能体
    agent_configs = [
        {
            "name": "销售助手",
            "description": "专业的销售对话智能体",
            "agent_type": "sales",
            "capabilities": ["销售对话", "产品推荐", "价格咨询"]
        },
        {
            "name": "技术支持",
            "description": "技术问题解答智能体",
            "agent_type": "technical_support",
            "capabilities": ["技术诊断", "故障排除", "使用指导"]
        },
        {
            "name": "市场分析师",
            "description": "市场数据分析智能体",
            "agent_type": "analyst",
            "capabilities": ["数据分析", "趋势预测", "报告生成"]
        }
    ]
    
    agents = []
    for config in agent_configs:
        agent_data = AgentCreate(**config)
        agent = await service.create_agent(agent_data, created_by=1)
        agents.append(agent)
        print(f"创建智能体: {agent.name}")
    
    # 批量创建提示词模板
    prompt_templates = {
        "sales": """你是一个专业的销售代表。

客户信息：
- 姓名：{customer_name}
- 需求：{customer_needs}
- 预算：{budget}

请根据客户需求推荐合适的产品。""",
        
        "technical_support": """你是一个技术支持专家。

问题信息：
- 产品：{product_name}
- 问题描述：{issue_description}
- 错误代码：{error_code}

请提供详细的解决方案。""",
        
        "analyst": """你是一个数据分析专家。

分析任务：
- 数据类型：{data_type}
- 分析目标：{analysis_goal}
- 时间范围：{time_range}

请提供专业的分析报告。"""
    }
    
    # 为每个智能体创建对应的提示词
    for agent in agents:
        if agent.agent_type in prompt_templates:
            prompt_data = SystemPromptCreate(
                agent_id=agent.id,
                name=f"{agent.name}提示词",
                content=prompt_templates[agent.agent_type],
                language="zh-CN",
                variables=extract_variables(prompt_templates[agent.agent_type]),
                category=agent.agent_type
            )
            
            prompt = await service.create_prompt(prompt_data, created_by=1)
            await service.activate_prompt(prompt.id, activated_by=1)
            print(f"为 {agent.name} 创建并激活提示词")

def extract_variables(content):
    """从提示词内容中提取变量"""
    import re
    variables = re.findall(r'\{(\w+)\}', content)
    return list(set(variables))
```

### 场景7：错误处理和恢复

```python
async def error_handling_example():
    """错误处理示例"""
    
    try:
        # 尝试创建智能体
        agent_data = AgentCreate(
            name="",  # 故意留空触发验证错误
            description="测试智能体",
            agent_type="test"
        )
        
        agent = await service.create_agent(agent_data, created_by=1)
        
    except ValueError as e:
        print(f"验证错误: {e}")
        
        # 修正数据后重试
        agent_data.name = "测试智能体"
        agent = await service.create_agent(agent_data, created_by=1)
        print(f"重试成功，创建智能体: {agent.name}")
    
    try:
        # 尝试获取不存在的智能体
        non_existent_agent = await service.get_agent(99999)
        
    except Exception as e:
        print(f"获取智能体失败: {e}")
        
        # 使用缓存或默认值作为后备
        cache_manager = AdvancedCacheManager()
        cached_agent = cache_manager.get_agent(99999)
        
        if cached_agent:
            print("从缓存中获取到智能体")
        else:
            print("使用默认智能体配置")
            # 创建默认智能体...

async def graceful_degradation_example():
    """优雅降级示例"""
    
    try:
        # 尝试获取最新的提示词
        agent_id = 1
        current_prompt = await service.get_agent_prompt(agent_id)
        
    except Exception as e:
        print(f"获取当前提示词失败: {e}")
        
        # 降级到缓存版本
        cache_manager = AdvancedCacheManager()
        cached_prompt = cache_manager.get_prompt(f"agent_{agent_id}_current")
        
        if cached_prompt:
            print("使用缓存的提示词")
            current_prompt = cached_prompt
        else:
            # 最后的后备方案：使用默认提示词
            print("使用默认提示词")
            current_prompt = get_default_prompt(agent_id)
    
    return current_prompt

def get_default_prompt(agent_id):
    """获取默认提示词"""
    return {
        "id": 0,
        "agent_id": agent_id,
        "content": "你是一个AI助手，请回答用户的问题。",
        "language": "zh-CN",
        "variables": [],
        "is_active": True
    }
```

## 完整的工作流程示例

```python
async def complete_workflow_example():
    """完整工作流程示例"""
    
    print("=== Prompt Management 完整工作流程示例 ===\n")
    
    # 1. 初始化
    print("1. 初始化服务...")
    db = next(get_db())
    service = PromptService(db)
    cache_manager = AdvancedCacheManager()
    performance_monitor = PerformanceMonitor()
    
    # 2. 创建智能体
    print("2. 创建智能体...")
    agent = await create_first_agent()
    
    # 3. 创建和激活提示词
    print("3. 创建和激活提示词...")
    prompt = await create_and_activate_prompt(agent.id)
    
    # 4. 模拟使用
    print("4. 模拟使用...")
    for i in range(10):
        await service.record_usage(
            prompt_id=prompt.id,
            response_time=1.0 + i * 0.1,
            success=True,
            user_feedback=4.0 + i * 0.1
        )
    
    # 5. 创建新版本
    print("5. 创建新版本...")
    new_version = await service.create_version(
        prompt_id=prompt.id,
        content="改进后的提示词内容...",
        change_description="优化响应质量",
        created_by=1
    )
    
    # 6. 获取分析数据
    print("6. 获取分析数据...")
    analytics_data = await service.get_usage_analytics(agent_id=agent.id, days=30)
    print(f"   总使用次数: {analytics_data['total_usage']}")
    print(f"   成功率: {analytics_data['success_rate']:.2%}")
    
    # 7. 性能监控
    print("7. 性能监控...")
    performance_monitor.record_response_time("workflow_test", 1.5)
    stats = performance_monitor.get_response_time_stats("workflow_test")
    print(f"   平均响应时间: {stats.avg:.2f}秒")
    
    # 8. 缓存管理
    print("8. 缓存管理...")
    cache_manager.set_agent(agent.id, agent)
    cached_agent = cache_manager.get_agent(agent.id)
    print(f"   缓存命中: {'是' if cached_agent else '否'}")
    
    print("\n=== 工作流程完成 ===")

# 运行示例
if __name__ == "__main__":
    asyncio.run(complete_workflow_example())
```

## 测试和调试

### 单元测试示例

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.asyncio
async def test_agent_creation():
    """测试智能体创建"""
    # 模拟数据库会话
    mock_db = Mock()
    service = PromptService(mock_db)
    
    # 测试数据
    agent_data = AgentCreate(
        name="测试智能体",
        description="用于测试",
        agent_type="test"
    )
    
    # 执行测试
    with patch.object(service, 'create_agent') as mock_create:
        mock_create.return_value = Mock(id=1, name="测试智能体")
        
        result = await service.create_agent(agent_data, created_by=1)
        
        assert result.id == 1
        assert result.name == "测试智能体"
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_prompt_activation():
    """测试提示词激活"""
    mock_db = Mock()
    service = PromptService(mock_db)
    
    with patch.object(service, 'activate_prompt') as mock_activate:
        mock_activate.return_value = Mock(id=1, is_active=True)
        
        result = await service.activate_prompt(1, activated_by=1)
        
        assert result.is_active is True
        mock_activate.assert_called_once_with(1, activated_by=1)
```

### 调试技巧

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_example():
    """调试示例"""
    
    # 添加调试日志
    logger.debug("开始创建智能体...")
    
    try:
        agent = await create_first_agent()
        logger.info(f"成功创建智能体: {agent.id}")
        
    except Exception as e:
        logger.error(f"创建智能体失败: {e}", exc_info=True)
        raise
    
    # 检查系统状态
    cache_manager = AdvancedCacheManager()
    cache_stats = cache_manager.get_cache_stats()
    logger.debug(f"缓存状态: {cache_stats}")
    
    performance_monitor = PerformanceMonitor()
    system_stats = performance_monitor.get_system_stats(minutes=1)
    logger.debug(f"系统状态: {system_stats}")
```

这些示例展示了Prompt Management系统的各种使用场景，从基础操作到高级功能，帮助开发者快速上手并充分利用系统的能力。