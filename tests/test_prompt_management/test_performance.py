"""
测试性能监控功能
"""
import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.prompt_management.performance import PerformanceMonitor, PerformanceMetric, monitor_performance


class TestPerformanceMonitor:
    """测试性能监控器"""
    
    def test_monitor_initialization(self, performance_monitor):
        """测试监控器初始化"""
        assert performance_monitor.metrics == []
        assert performance_monitor.response_times == {}
        assert performance_monitor.system_stats == []
        assert performance_monitor.monitoring_active is False
    
    def test_record_metric(self, performance_monitor):
        """测试记录性能指标"""
        performance_monitor.record_metric("test_metric", 1.5, {"tag": "test"})
        
        assert len(performance_monitor.metrics) == 1
        metric = performance_monitor.metrics[0]
        assert metric.name == "test_metric"
        assert metric.value == 1.5
        assert metric.tags == {"tag": "test"}
        assert isinstance(metric.timestamp, datetime)
    
    def test_record_response_time(self, performance_monitor):
        """测试记录响应时间"""
        performance_monitor.record_response_time("test_endpoint", 2.5)
        
        assert "test_endpoint" in performance_monitor.response_times
        times = performance_monitor.response_times["test_endpoint"]
        assert len(times) == 1
        assert times[0] == 2.5
    
    def test_get_response_time_stats(self, performance_monitor):
        """测试获取响应时间统计"""
        # 记录多个响应时间
        times = [1.0, 2.0, 3.0, 4.0, 5.0]
        for t in times:
            performance_monitor.record_response_time("test_endpoint", t)
        
        stats = performance_monitor.get_response_time_stats("test_endpoint")
        
        assert stats.endpoint == "test_endpoint"
        assert stats.count == 5
        assert stats.avg == 3.0
        assert stats.min == 1.0
        assert stats.max == 5.0
        assert stats.p95 == 5.0  # 95th percentile
    
    def test_get_response_time_stats_all_endpoints(self, performance_monitor):
        """测试获取所有端点的响应时间统计"""
        # 记录多个端点的响应时间
        performance_monitor.record_response_time("endpoint1", 1.0)
        performance_monitor.record_response_time("endpoint1", 2.0)
        performance_monitor.record_response_time("endpoint2", 3.0)
        
        all_stats = performance_monitor.get_response_time_stats()
        
        assert len(all_stats) == 2
        endpoint_names = [stat.endpoint for stat in all_stats]
        assert "endpoint1" in endpoint_names
        assert "endpoint2" in endpoint_names
    
    def test_collect_system_stats(self, performance_monitor):
        """测试收集系统统计"""
        performance_monitor.collect_system_stats()
        
        assert len(performance_monitor.system_stats) == 1
        stats = performance_monitor.system_stats[0]
        assert stats.cpu_percent >= 0
        assert stats.memory_percent >= 0
        assert stats.disk_usage >= 0
        assert isinstance(stats.timestamp, datetime)
    
    def test_get_system_stats(self, performance_monitor):
        """测试获取系统统计"""
        # 收集一些统计数据
        performance_monitor.collect_system_stats()
        time.sleep(0.1)
        performance_monitor.collect_system_stats()
        
        # 获取最近1分钟的统计
        recent_stats = performance_monitor.get_system_stats(minutes=1)
        
        assert len(recent_stats) == 2
        assert all(isinstance(stat.timestamp, datetime) for stat in recent_stats)
    
    def test_get_metrics(self, performance_monitor):
        """测试获取指标"""
        # 记录一些指标
        performance_monitor.record_metric("metric1", 1.0)
        performance_monitor.record_metric("metric2", 2.0)
        performance_monitor.record_metric("metric1", 3.0)
        
        # 获取特定指标
        metric1_data = performance_monitor.get_metrics("metric1", minutes=1)
        assert len(metric1_data) == 2
        assert all(m.name == "metric1" for m in metric1_data)
        
        # 获取所有指标
        all_metrics = performance_monitor.get_metrics(minutes=1)
        assert len(all_metrics) == 3
    
    def test_clear_metrics(self, performance_monitor):
        """测试清理指标"""
        # 记录一些指标
        performance_monitor.record_metric("test_metric", 1.0)
        
        # 立即清理（0小时前的指标）
        removed_count = performance_monitor.clear_metrics(hours=0)
        
        assert removed_count == 1
        assert len(performance_monitor.metrics) == 0
    
    def test_get_performance_summary(self, performance_monitor):
        """测试获取性能摘要"""
        # 记录一些数据
        performance_monitor.record_response_time("endpoint1", 1.0)
        performance_monitor.record_response_time("endpoint1", 2.0)
        performance_monitor.record_metric("cpu_usage", 50.0)
        performance_monitor.collect_system_stats()
        
        summary = performance_monitor.get_performance_summary()
        
        assert "total_endpoints" in summary
        assert "total_metrics" in summary
        assert "avg_response_time" in summary
        assert "system_health" in summary
        assert summary["total_endpoints"] == 1
        assert summary["total_metrics"] == 1
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, performance_monitor):
        """测试启动和停止监控"""
        # 启动监控
        await performance_monitor.start_monitoring(interval=0.1)
        assert performance_monitor.monitoring_active is True
        
        # 等待一段时间让监控收集数据
        await asyncio.sleep(0.3)
        
        # 停止监控
        performance_monitor.stop_monitoring()
        assert performance_monitor.monitoring_active is False
        
        # 验证收集了系统统计数据
        assert len(performance_monitor.system_stats) > 0
    
    def test_monitor_performance_decorator(self):
        """测试性能监控装饰器"""
        @monitor_performance("test_function")
        def test_function():
            time.sleep(0.1)
            return "result"
        
        result = test_function()
        
        assert result == "result"
        # 注意：装饰器会记录到全局监控器中
    
    @pytest.mark.asyncio
    async def test_monitor_performance_async_decorator(self):
        """测试异步性能监控装饰器"""
        @monitor_performance("test_async_function")
        async def test_async_function():
            await asyncio.sleep(0.1)
            return "async_result"
        
        result = await test_async_function()
        
        assert result == "async_result"
    
    def test_monitor_performance_context_manager(self, performance_monitor):
        """测试性能监控上下文管理器"""
        with performance_monitor.monitor("test_operation"):
            time.sleep(0.1)
        
        # 验证记录了响应时间
        stats = performance_monitor.get_response_time_stats("test_operation")
        assert stats.count == 1
        assert stats.avg >= 0.1
    
    @pytest.mark.asyncio
    async def test_monitor_performance_async_context_manager(self, performance_monitor):
        """测试异步性能监控上下文管理器"""
        async with performance_monitor.async_monitor("test_async_operation"):
            await asyncio.sleep(0.1)
        
        # 验证记录了响应时间
        stats = performance_monitor.get_response_time_stats("test_async_operation")
        assert stats.count == 1
        assert stats.avg >= 0.1
    
    def test_performance_metric_data_class(self):
        """测试性能指标数据类"""
        timestamp = datetime.utcnow()
        metric = PerformanceMetric(
            name="test_metric",
            value=1.5,
            timestamp=timestamp,
            tags={"env": "test"}
        )
        
        assert metric.name == "test_metric"
        assert metric.value == 1.5
        assert metric.timestamp == timestamp
        assert metric.tags == {"env": "test"}
    
    def test_memory_management(self, performance_monitor):
        """测试内存管理"""
        # 记录大量指标
        for i in range(10000):
            performance_monitor.record_metric(f"metric_{i % 10}", i)
        
        # 清理旧指标
        removed_count = performance_monitor.clear_metrics(hours=0)
        
        assert removed_count == 10000
        assert len(performance_monitor.metrics) == 0
    
    def test_concurrent_metric_recording(self, performance_monitor):
        """测试并发指标记录"""
        import threading
        
        def record_metrics():
            for i in range(100):
                performance_monitor.record_metric("concurrent_metric", i)
        
        # 启动多个线程并发记录指标
        threads = [threading.Thread(target=record_metrics) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # 验证所有指标都被记录
        metrics = performance_monitor.get_metrics("concurrent_metric")
        assert len(metrics) == 500  # 5 threads * 100 metrics each
    
    def test_error_handling(self, performance_monitor):
        """测试错误处理"""
        # 测试获取不存在的端点统计
        stats = performance_monitor.get_response_time_stats("nonexistent_endpoint")
        assert stats.count == 0
        assert stats.avg == 0
        
        # 测试获取空的系统统计
        system_stats = performance_monitor.get_system_stats(minutes=1)
        assert isinstance(system_stats, list)
        
        # 测试清理不存在的指标
        removed_count = performance_monitor.clear_metrics(hours=24)
        assert removed_count == 0