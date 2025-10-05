#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
诊断数据库连接和后台任务的脚本
检查是否存在连接泄漏或异常的后台查询
"""

import asyncio
import time
import psutil
import threading
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from src.api.db import engine, SessionLocal
from src.prompt_management.performance import get_performance_monitor
from config.settings import get_settings

def check_database_connections():
    """检查数据库连接池状态"""
    print("=== 数据库连接池状态 ===")
    
    # 检查连接池信息
    pool = engine.pool
    print(f"连接池类型: {type(pool).__name__}")
    print(f"连接池大小: {pool.size()}")
    print(f"已检出连接数: {pool.checkedout()}")
    print(f"溢出连接数: {pool.overflow()}")
    
    # 检查连接池状态
    try:
        print(f"连接池状态: {pool.status()}")
    except AttributeError:
        print("连接池状态: 无法获取详细状态")
    
    # 测试连接
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"数据库连接测试: 成功")
    except Exception as e:
        print(f"数据库连接测试: 失败 - {e}")

def check_active_threads():
    """检查活跃线程"""
    print("\n=== 活跃线程状态 ===")
    
    threads = threading.enumerate()
    print(f"总线程数: {len(threads)}")
    
    for thread in threads:
        print(f"线程: {thread.name} - 状态: {'活跃' if thread.is_alive() else '非活跃'}")

def check_system_resources():
    """检查系统资源使用"""
    print("\n=== 系统资源状态 ===")
    
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU使用率: {cpu_percent}%")
    
    # 内存使用
    memory = psutil.virtual_memory()
    print(f"内存使用率: {memory.percent}%")
    print(f"已用内存: {memory.used / 1024 / 1024:.2f} MB")
    print(f"可用内存: {memory.available / 1024 / 1024:.2f} MB")
    
    # 进程信息
    current_process = psutil.Process()
    print(f"当前进程CPU: {current_process.cpu_percent()}%")
    print(f"当前进程内存: {current_process.memory_info().rss / 1024 / 1024:.2f} MB")
    print(f"当前进程线程数: {current_process.num_threads()}")

def check_performance_monitor():
    """检查性能监控状态"""
    print("\n=== 性能监控状态 ===")
    
    try:
        monitor = get_performance_monitor()
        print(f"监控状态: {'运行中' if monitor._monitoring else '已停止'}")
        
        # 获取性能摘要
        summary = monitor.get_performance_summary()
        print(f"响应时间统计: {len(summary.get('response_times', {}))}")
        print(f"系统统计: {len(summary.get('system_stats', []))}")
        print(f"指标数量: {len(summary.get('metrics', []))}")
        
    except Exception as e:
        print(f"性能监控检查失败: {e}")

def check_database_queries():
    """检查数据库查询活动"""
    print("\n=== 数据库查询活动 ===")
    
    try:
        with engine.connect() as conn:
            # 检查MySQL进程列表
            result = conn.execute(text("SHOW PROCESSLIST"))
            processes = result.fetchall()
            
            print(f"活跃数据库连接数: {len(processes)}")
            
            for process in processes:
                if process[4] and process[4] != 'Sleep':  # 非空闲连接
                    print(f"活跃查询: ID={process[0]}, 用户={process[1]}, 状态={process[4]}, 时间={process[5]}s")
                    if process[7]:  # 查询内容
                        print(f"  查询: {process[7][:100]}...")
                        
    except Exception as e:
        print(f"数据库查询检查失败: {e}")

async def monitor_requests_for_period(duration=30):
    """监控一段时间内的请求活动"""
    print(f"\n=== 监控 {duration} 秒内的请求活动 ===")
    
    monitor = get_performance_monitor()
    initial_stats = monitor.get_performance_summary()
    initial_count = sum(stats['count'] for stats in initial_stats.get('response_times', {}).values())
    
    print(f"初始请求总数: {initial_count}")
    
    await asyncio.sleep(duration)
    
    final_stats = monitor.get_performance_summary()
    final_count = sum(stats['count'] for stats in final_stats.get('response_times', {}).values())
    
    new_requests = final_count - initial_count
    print(f"新增请求数: {new_requests}")
    print(f"平均请求频率: {new_requests / duration:.2f} 请求/秒")
    
    if new_requests > 100:  # 如果30秒内有超过100个请求
        print("⚠️  警告: 检测到异常高频的请求活动!")
        
        # 显示最活跃的端点
        response_times = final_stats.get('response_times', {})
        sorted_endpoints = sorted(response_times.items(), key=lambda x: x[1]['count'], reverse=True)
        
        print("最活跃的端点:")
        for endpoint, stats in sorted_endpoints[:5]:
            print(f"  {endpoint}: {stats['count']} 次请求")

def main():
    """主诊断函数"""
    print("开始系统诊断...")
    print("=" * 50)
    
    check_database_connections()
    check_active_threads()
    check_system_resources()
    check_performance_monitor()
    check_database_queries()
    
    # 异步监控请求活动
    print("\n开始监控请求活动...")
    asyncio.run(monitor_requests_for_period(30))
    
    print("\n诊断完成!")

if __name__ == "__main__":
    main()