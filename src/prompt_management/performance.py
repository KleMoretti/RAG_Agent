"""
性能监控和指标收集模块
提供API响应时间、缓存性能、系统资源使用等监控功能
"""
from __future__ import annotations

import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
from threading import Lock
from contextlib import contextmanager
from functools import wraps

from config.logging_config import setup_logging

logger = setup_logging()


@dataclass
class PerformanceMetric:
    """性能指标"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags
        }


@dataclass
class ResponseTimeStats:
    """响应时间统计"""
    count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    p95_time: float = 0.0
    p99_time: float = 0.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def add_time(self, response_time: float) -> None:
        """添加响应时间"""
        self.count += 1
        self.total_time += response_time
        self.min_time = min(self.min_time, response_time)
        self.max_time = max(self.max_time, response_time)
        self.avg_time = self.total_time / self.count
        
        self.recent_times.append(response_time)
        
        # 计算百分位数
        if len(self.recent_times) >= 20:  # 至少20个样本才计算百分位数
            sorted_times = sorted(self.recent_times)
            self.p95_time = sorted_times[int(len(sorted_times) * 0.95)]
            self.p99_time = sorted_times[int(len(sorted_times) * 0.99)]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "avg_time": round(self.avg_time, 3),
            "min_time": round(self.min_time, 3),
            "max_time": round(self.max_time, 3),
            "p95_time": round(self.p95_time, 3),
            "p99_time": round(self.p99_time, 3)
        }


@dataclass
class SystemResourceStats:
    """系统资源统计"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_percent": round(self.cpu_percent, 2),
            "memory_percent": round(self.memory_percent, 2),
            "memory_used_mb": round(self.memory_used_mb, 2),
            "memory_available_mb": round(self.memory_available_mb, 2),
            "disk_usage_percent": round(self.disk_usage_percent, 2),
            "timestamp": self.timestamp.isoformat()
        }


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics: List[PerformanceMetric] = []
        self.response_times: Dict[str, ResponseTimeStats] = defaultdict(ResponseTimeStats)
        self.system_stats: List[SystemResourceStats] = []
        self.lock = Lock()
        self._monitoring = False
        self._monitor_task = None
    
    def record_metric(self, name: str, value: float, unit: str = "", tags: Dict[str, str] = None) -> None:
        """记录性能指标"""
        with self.lock:
            metric = PerformanceMetric(
                name=name,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                tags=tags or {}
            )
            
            self.metrics.append(metric)
            
            # 保持指标数量在限制内
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def record_response_time(self, endpoint: str, response_time: float) -> None:
        """记录API响应时间"""
        # 创建指标对象（避免在锁内调用其他需要锁的方法）
        metric = PerformanceMetric(
            name="api_response_time",
            value=response_time,
            unit="seconds",
            timestamp=datetime.utcnow(),
            tags={"endpoint": endpoint}
        )
        
        with self.lock:
            # 更新响应时间统计
            self.response_times[endpoint].add_time(response_time)
            
            # 添加指标到列表
            self.metrics.append(metric)
            
            # 保持指标数量在限制内
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
    
    def get_response_time_stats(self, endpoint: str = None) -> Dict[str, Any]:
        """获取响应时间统计"""
        with self.lock:
            if endpoint:
                if endpoint in self.response_times:
                    return {endpoint: self.response_times[endpoint].to_dict()}
                return {}
            
            return {ep: stats.to_dict() for ep, stats in self.response_times.items()}
    
    def collect_system_stats(self) -> SystemResourceStats:
        """收集系统资源统计"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_available_mb = memory.available / (1024 * 1024)
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            stats = SystemResourceStats(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.system_stats.append(stats)
                
                # 保持最近1小时的数据（每30秒一次，120个数据点）
                if len(self.system_stats) > 120:
                    self.system_stats = self.system_stats[-120:]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to collect system stats: {e}")
            return SystemResourceStats(0, 0, 0, 0, 0, datetime.utcnow())
    
    def get_system_stats(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """获取系统资源统计（最近N分钟）"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            recent_stats = [
                stats for stats in self.system_stats 
                if stats.timestamp >= cutoff_time
            ]
            return [stats.to_dict() for stats in recent_stats]
    
    def get_metrics(self, name: str = None, minutes: int = 60) -> List[Dict[str, Any]]:
        """获取性能指标（最近N分钟）"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            filtered_metrics = [
                metric for metric in self.metrics
                if metric.timestamp >= cutoff_time and (name is None or metric.name == name)
            ]
            
            return [metric.to_dict() for metric in filtered_metrics]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        with self.lock:
            # 最近的系统状态
            latest_system = self.system_stats[-1] if self.system_stats else None
            
            # API响应时间摘要
            api_summary = {}
            for endpoint, stats in self.response_times.items():
                if stats.count > 0:
                    api_summary[endpoint] = {
                        "requests": stats.count,
                        "avg_response_time": round(stats.avg_time, 3),
                        "p95_response_time": round(stats.p95_time, 3)
                    }
            
            # 最近1小时的指标统计
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            
            metric_counts = defaultdict(int)
            for metric in recent_metrics:
                metric_counts[metric.name] += 1
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system_resources": latest_system.to_dict() if latest_system else None,
                "api_performance": api_summary,
                "metrics_count": dict(metric_counts),
                "total_metrics": len(recent_metrics)
            }
    
    async def start_monitoring(self, interval: int = 30) -> None:
        """开始系统监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        logger.info(f"Starting performance monitoring with {interval}s interval")
        
        async def monitor_loop():
            while self._monitoring:
                try:
                    self.collect_system_stats()
                    await asyncio.sleep(interval)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(interval)
        
        self._monitor_task = asyncio.create_task(monitor_loop())
    
    def stop_monitoring(self) -> None:
        """停止系统监控"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
        
        logger.info("Stopped performance monitoring")
    
    def clear_metrics(self, older_than_hours: int = 24) -> int:
        """清理旧指标"""
        with self.lock:
            cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
            
            # 清理通用指标
            old_count = len(self.metrics)
            self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            
            # 清理系统统计
            self.system_stats = [s for s in self.system_stats if s.timestamp >= cutoff_time]
            
            removed_count = old_count - len(self.metrics)
            logger.info(f"Cleared {removed_count} old metrics")
            return removed_count


# 全局性能监控器实例
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def init_performance_monitor() -> PerformanceMonitor:
    """初始化性能监控器"""
    global _performance_monitor
    _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# 装饰器：自动记录函数执行时间
def monitor_performance(endpoint_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            monitor = get_performance_monitor()
            
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                
                name = endpoint_name or f"{func.__module__}.{func.__name__}"
                monitor.record_response_time(name, response_time)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            monitor = get_performance_monitor()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                response_time = end_time - start_time
                
                name = endpoint_name or f"{func.__module__}.{func.__name__}"
                monitor.record_response_time(name, response_time)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


@contextmanager
def performance_timer(operation_name: str):
    """性能计时上下文管理器"""
    start_time = time.time()
    monitor = get_performance_monitor()
    
    try:
        yield
    finally:
        end_time = time.time()
        response_time = end_time - start_time
        monitor.record_response_time(operation_name, response_time)