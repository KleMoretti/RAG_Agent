#!/usr/bin/env python3
"""
调试active prompt API性能问题的脚本
"""

import asyncio
import time
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.api.models import SystemPrompt, Agent, PromptStatus
from src.prompt_management.service import PromptService
from src.api.db import get_db
from config.logging_config import setup_logging

logger = setup_logging()

def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        db = next(get_db())
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"✅ 数据库连接正常: {result}")
        
        # 测试基本查询
        agent_count = db.query(Agent).count()
        prompt_count = db.query(SystemPrompt).count()
        print(f"✅ Agent数量: {agent_count}")
        print(f"✅ SystemPrompt数量: {prompt_count}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_agent_exists(agent_id: int = 6):
    """测试指定Agent是否存在"""
    print(f"\n=== 测试Agent {agent_id} 是否存在 ===")
    try:
        db = next(get_db())
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            print(f"✅ Agent存在: {agent.name} (类型: {agent.agent_type})")
            return True
        else:
            print(f"❌ Agent {agent_id} 不存在")
            return False
    except Exception as e:
        print(f"❌ 查询Agent失败: {e}")
        return False
    finally:
        db.close()

def test_prompt_query(agent_id: int = 6, language: str = "zh-CN"):
    """测试Prompt查询"""
    print(f"\n=== 测试Agent {agent_id} 的Prompt查询 ===")
    try:
        db = next(get_db())
        
        # 查询所有相关的prompts
        all_prompts = db.query(SystemPrompt).filter(
            SystemPrompt.agent_id == agent_id
        ).all()
        print(f"✅ Agent {agent_id} 总共有 {len(all_prompts)} 个Prompt")
        
        for prompt in all_prompts:
            print(f"  - ID: {prompt.id}, 状态: {prompt.status}, 默认: {prompt.is_default}, 语言: {prompt.language}")
        
        # 查询激活状态的默认Prompt
        active_prompts = db.query(SystemPrompt).filter(
            SystemPrompt.agent_id == agent_id,
            SystemPrompt.language == language,
            SystemPrompt.status == PromptStatus.ACTIVE,
            SystemPrompt.is_default == True
        ).all()
        
        print(f"✅ 激活状态的默认Prompt数量: {len(active_prompts)}")
        for prompt in active_prompts:
            print(f"  - ID: {prompt.id}, 名称: {prompt.name}")
        
        return len(active_prompts) > 0
        
    except Exception as e:
        print(f"❌ Prompt查询失败: {e}")
        return False
    finally:
        db.close()

def test_service_method(agent_id: int = 6, language: str = "zh-CN"):
    """测试PromptService的get_agent_prompt方法"""
    print(f"\n=== 测试PromptService.get_agent_prompt方法 ===")
    try:
        db = next(get_db())
        service = PromptService(db)
        
        # 测试不使用缓存
        print("测试不使用缓存...")
        start_time = time.time()
        result_no_cache = service.get_agent_prompt(agent_id, language, use_cache=False)
        end_time = time.time()
        
        print(f"✅ 不使用缓存耗时: {(end_time - start_time) * 1000:.2f}ms")
        if result_no_cache:
            print(f"✅ 找到Prompt: {result_no_cache.name}")
        else:
            print("❌ 未找到Prompt")
        
        # 测试使用缓存
        print("测试使用缓存...")
        start_time = time.time()
        result_with_cache = service.get_agent_prompt(agent_id, language, use_cache=True)
        end_time = time.time()
        
        print(f"✅ 使用缓存耗时: {(end_time - start_time) * 1000:.2f}ms")
        if result_with_cache:
            print(f"✅ 找到Prompt: {result_with_cache.name}")
        else:
            print("❌ 未找到Prompt")
        
        return result_no_cache is not None
        
    except Exception as e:
        print(f"❌ PromptService测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def test_cache_performance():
    """测试缓存性能"""
    print(f"\n=== 测试缓存性能 ===")
    try:
        from src.prompt_management.cache import get_prompt_cache
        cache = get_prompt_cache()
        
        # 清空缓存
        cache.clear()
        print("✅ 缓存已清空")
        
        # 获取缓存统计
        stats = cache.get_stats()
        print(f"✅ 缓存统计: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始诊断active prompt API性能问题...\n")
    
    # 测试步骤
    tests = [
        ("数据库连接", test_database_connection),
        ("Agent存在性", lambda: test_agent_exists(6)),
        ("Prompt查询", lambda: test_prompt_query(6, "zh-CN")),
        ("缓存性能", test_cache_performance),
        ("Service方法", lambda: test_service_method(6, "zh-CN")),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"执行测试: {test_name}")
        print(f"{'='*50}")
        
        try:
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            
            results[test_name] = {
                "success": result,
                "duration": end_time - start_time
            }
            
            status = "✅ 通过" if result else "❌ 失败"
            print(f"\n{test_name}: {status} (耗时: {(end_time - start_time) * 1000:.2f}ms)")
            
        except Exception as e:
            results[test_name] = {
                "success": False,
                "duration": 0,
                "error": str(e)
            }
            print(f"\n{test_name}: ❌ 异常 - {e}")
    
    # 输出总结
    print(f"\n{'='*50}")
    print("测试总结")
    print(f"{'='*50}")
    
    for test_name, result in results.items():
        status = "✅" if result["success"] else "❌"
        duration = result["duration"] * 1000
        print(f"{status} {test_name}: {duration:.2f}ms")
        if "error" in result:
            print(f"   错误: {result['error']}")

if __name__ == "__main__":
    main()