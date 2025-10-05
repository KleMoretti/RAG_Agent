#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统健康监控脚本
定期检查数据库连接、系统资源和API响应，防止问题再次发生
"""

import asyncio
import time
import logging
import psutil
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from src.api.db import engine
from src.prompt_management.performance import get_performance_monitor
from config.logging_config import setup_logging

logger = setup_logging()

class SystemHealthMonitor:
    """系统健康监控器"""
    
    def __init__(self):
        self.monitoring = False
        self.check_interval = 60  # 检查间隔（秒）
        self.alert_thresholds = {
            'cpu_percent': 80,           # CPU使用率阈值
            'memory_percent': 90,        # 内存使用率阈值
            'db_connections': 25,        # 数据库连接数阈值
            'response_time': 5.0,        # 响应时间阈值（秒）
            'request_rate': 50,          # 请求频率阈值（请求/分钟）
        }
        
    async def start_monitoring(self):
        """开始监控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        logger.info("开始系统健康监控")
        
        while self.monitoring:
            try:
                await self.check_system_health()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        logger.info("停止系统健康监控")
    
    async def check_system_health(self):
        """检查系统健康状态"""
        timestamp = datetime.now()
        
        # 检查系统资源
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # 检查数据库连接
        db_connections = self.check_database_connections()
        
        # 检查API性能
        api_performance = self.check_api_performance()
        
        # 记录健康状态
        health_status = {
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'db_connections': db_connections,
            'api_performance': api_performance
        }
        
        # 检查是否需要告警
        await self.check_alerts(health_status)
        
        # 记录日志
        logger.info(f"系统健康检查: CPU={cpu_percent}%, 内存={memory.percent}%, "
                   f"数据库连接={db_connections}, API性能={api_performance}")
    
    def check_database_connections(self):
        """检查数据库连接状态"""
        try:
            pool = engine.pool
            checked_out = pool.checkedout()
            pool_size = pool.size()
            overflow = pool.overflow()
            
            total_connections = checked_out + max(0, overflow)
            
            return {
                'checked_out': checked_out,
                'pool_size': pool_size,
                'overflow': overflow,
                'total': total_connections
            }
        except Exception as e:
            logger.error(f"检查数据库连接失败: {e}")
            return {'error': str(e)}
    
    def check_api_performance(self):
        """检查API性能"""
        try:
            monitor = get_performance_monitor()
            summary = monitor.get_performance_summary()
            
            response_times = summary.get('response_times', {})
            
            # 计算平均响应时间
            total_requests = 0
            total_time = 0
            
            for endpoint_stats in response_times.values():
                count = endpoint_stats.get('count', 0)
                avg_time = endpoint_stats.get('avg_time', 0)
                total_requests += count
                total_time += count * avg_time
            
            avg_response_time = total_time / total_requests if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'avg_response_time': avg_response_time,
                'endpoints': len(response_times)
            }
        except Exception as e:
            logger.error(f"检查API性能失败: {e}")
            return {'error': str(e)}
    
    async def check_alerts(self, health_status):
        """检查是否需要发出告警"""
        alerts = []
        
        # CPU告警
        if health_status['cpu_percent'] > self.alert_thresholds['cpu_percent']:
            alerts.append(f"CPU使用率过高: {health_status['cpu_percent']}%")
        
        # 内存告警
        if health_status['memory_percent'] > self.alert_thresholds['memory_percent']:
            alerts.append(f"内存使用率过高: {health_status['memory_percent']}%")
        
        # 数据库连接告警
        db_conn = health_status['db_connections']
        if isinstance(db_conn, dict) and 'total' in db_conn:
            if db_conn['total'] > self.alert_thresholds['db_connections']:
                alerts.append(f"数据库连接数过多: {db_conn['total']}")
        
        # API性能告警
        api_perf = health_status['api_performance']
        if isinstance(api_perf, dict) and 'avg_response_time' in api_perf:
            if api_perf['avg_response_time'] > self.alert_thresholds['response_time']:
                alerts.append(f"API响应时间过长: {api_perf['avg_response_time']:.2f}s")
        
        # 发送告警
        if alerts:
            await self.send_alerts(alerts)
    
    async def send_alerts(self, alerts):
        """发送告警"""
        for alert in alerts:
            logger.warning(f"🚨 系统告警: {alert}")
            
        # 这里可以添加其他告警方式，如邮件、钉钉等
        # 例如：await self.send_email_alert(alerts)
        # 例如：await self.send_dingtalk_alert(alerts)
    
    def get_health_report(self):
        """获取健康报告"""
        try:
            # 系统资源
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            # 数据库状态
            db_status = self.check_database_connections()
            
            # API性能
            api_status = self.check_api_performance()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_mb': memory.used / 1024 / 1024,
                    'memory_available_mb': memory.available / 1024 / 1024
                },
                'database': db_status,
                'api': api_status,
                'monitoring': self.monitoring
            }
        except Exception as e:
            logger.error(f"获取健康报告失败: {e}")
            return {'error': str(e)}

# 全局监控实例
_health_monitor = None

def get_health_monitor():
    """获取健康监控实例"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = SystemHealthMonitor()
    return _health_monitor

async def main():
    """主函数 - 用于独立运行监控"""
    monitor = get_health_monitor()
    
    try:
        print("启动系统健康监控...")
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("收到中断信号，停止监控...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())