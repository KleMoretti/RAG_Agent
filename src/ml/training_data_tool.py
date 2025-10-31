"""训练数据查询工具 - 用于 Agent 查询设备故障训练数据"""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import numpy as np

from config.settings import get_settings
from src.agent.tools import Tool

cfg = get_settings()


class TrainingDataQueryTool(Tool):
    """训练数据查询工具
    
    用于查询设备故障训练数据，支持：
    - 查询特定设备类型的历史数据
    - 分析故障率统计
    - 查询特定参数范围的样本
    - 对比正常和故障样本的参数差异
    """
    
    def __init__(self):
        super().__init__(
            name="training_data_query",
            description=(
                "查询设备故障训练数据。用于回答关于设备参数、故障模式、历史数据的问题。"
                "可以查询温度、压力、振动、湿度等参数的历史值，以及故障率统计。"
                "示例查询：'Turbine设备的平均温度是多少？'，'故障样本的振动值范围？'"
            ),
        )
        # 新的ML目录结构：data/ml/training_data/
        # 使用项目根目录的 data/ml/training_data/，而不是 data/raw/ml/training_data/
        project_root = Path(cfg.data_dir).parent  # data/raw -> data
        self.data_path = project_root / "ml" / "training_data" / "equipment_anomaly_data.csv"
        self._df: pd.DataFrame | None = None
    
    @property
    def df(self) -> pd.DataFrame:
        """延迟加载训练数据"""
        if self._df is None:
            if not self.data_path.exists():
                raise FileNotFoundError(
                    f"训练数据文件不存在: {self.data_path}\n"
                    f"请确保文件已放置在 data/ml_models/ 目录下"
                )
            self._df = pd.read_csv(self.data_path)
            print(f"✅ 已加载训练数据: {len(self._df)} 条记录")
        return self._df
    
    def execute(self, **kwargs) -> str:
        """执行训练数据查询
        
        支持的查询类型:
        - query_type="statistics": 整体统计信息
        - query_type="equipment_stats": 特定设备类型统计 (equipment_type="Turbine")
        - query_type="fault_analysis": 故障样本分析
        - query_type="parameter_range": 参数范围查询 (parameter="temperature", condition="faulty")
        - query_type="compare": 对比正常和故障样本
        """
        query_type = kwargs.get("query_type", "statistics")
        
        try:
            if query_type == "statistics":
                return self._get_statistics()
            elif query_type == "equipment_stats":
                equipment_type = kwargs.get("equipment_type", "Turbine")
                return self._get_equipment_stats(equipment_type)
            elif query_type == "fault_analysis":
                return self._get_fault_analysis()
            elif query_type == "parameter_range":
                parameter = kwargs.get("parameter", "temperature")
                condition = kwargs.get("condition", "all")  # all, faulty, normal
                return self._get_parameter_range(parameter, condition)
            elif query_type == "compare":
                return self._compare_normal_vs_faulty()
            else:
                return f"❌ 不支持的查询类型: {query_type}"
        except Exception as e:
            return f"❌ 查询失败: {str(e)}"
    
    def _get_statistics(self) -> str:
        """获取整体统计信息"""
        df = self.df
        total = len(df)
        faulty_count = int(df['faulty'].sum())
        faulty_rate = faulty_count / total * 100
        
        equipment_types = df['equipment'].unique().tolist()
        locations = df['location'].unique().tolist()
        
        result = [
            "📊 训练数据整体统计",
            "=" * 60,
            f"总样本数: {total}",
            f"故障样本: {faulty_count} ({faulty_rate:.2f}%)",
            f"正常样本: {total - faulty_count} ({100 - faulty_rate:.2f}%)",
            f"设备类型: {', '.join(equipment_types)}",
            f"位置分布: {', '.join(locations)}",
            "",
            "参数统计 (全部样本):",
            f"  温度: {df['temperature'].min():.2f}~{df['temperature'].max():.2f}°C (均值: {df['temperature'].mean():.2f}°C)",
            f"  压力: {df['pressure'].min():.2f}~{df['pressure'].max():.2f} psi (均值: {df['pressure'].mean():.2f} psi)",
            f"  振动: {df['vibration'].min():.2f}~{df['vibration'].max():.2f} mm/s (均值: {df['vibration'].mean():.2f} mm/s)",
            f"  湿度: {df['humidity'].min():.2f}~{df['humidity'].max():.2f}% (均值: {df['humidity'].mean():.2f}%)",
        ]
        
        return "\n".join(result)
    
    def _get_equipment_stats(self, equipment_type: str) -> str:
        """获取特定设备类型的统计"""
        df = self.df
        eq_df = df[df['equipment'] == equipment_type]
        
        if len(eq_df) == 0:
            available = ', '.join(df['equipment'].unique())
            return f"❌ 未找到设备类型 '{equipment_type}'。可用类型: {available}"
        
        total = len(eq_df)
        faulty_count = int(eq_df['faulty'].sum())
        faulty_rate = faulty_count / total * 100
        
        result = [
            f"📊 {equipment_type} 设备统计",
            "=" * 60,
            f"样本数: {total}",
            f"故障样本: {faulty_count} ({faulty_rate:.2f}%)",
            f"正常样本: {total - faulty_count} ({100 - faulty_rate:.2f}%)",
            "",
            "参数统计 (全部样本):",
            f"  温度: {eq_df['temperature'].min():.2f}~{eq_df['temperature'].max():.2f}°C (均值: {eq_df['temperature'].mean():.2f}°C)",
            f"  压力: {eq_df['pressure'].min():.2f}~{eq_df['pressure'].max():.2f} psi (均值: {eq_df['pressure'].mean():.2f} psi)",
            f"  振动: {eq_df['vibration'].min():.2f}~{eq_df['vibration'].max():.2f} mm/s (均值: {eq_df['vibration'].mean():.2f} mm/s)",
            f"  湿度: {eq_df['humidity'].min():.2f}~{eq_df['humidity'].max():.2f}% (均值: {eq_df['humidity'].mean():.2f}%)",
        ]
        
        return "\n".join(result)
    
    def _get_fault_analysis(self) -> str:
        """分析故障样本特征"""
        df = self.df
        faulty_df = df[df['faulty'] == 1.0]
        normal_df = df[df['faulty'] == 0.0]
        
        result = [
            "🔍 故障样本分析",
            "=" * 60,
            f"故障样本数: {len(faulty_df)} ({len(faulty_df)/len(df)*100:.2f}%)",
            "",
            "故障样本参数特征:",
            f"  温度: {faulty_df['temperature'].mean():.2f}°C (正常样本: {normal_df['temperature'].mean():.2f}°C)",
            f"  压力: {faulty_df['pressure'].mean():.2f} psi (正常样本: {normal_df['pressure'].mean():.2f} psi)",
            f"  振动: {faulty_df['vibration'].mean():.2f} mm/s (正常样本: {normal_df['vibration'].mean():.2f} mm/s)",
            f"  湿度: {faulty_df['humidity'].mean():.2f}% (正常样本: {normal_df['humidity'].mean():.2f}%)",
            "",
            "设备类型故障分布:",
        ]
        
        for equipment in df['equipment'].unique():
            eq_df = df[df['equipment'] == equipment]
            eq_faulty = eq_df['faulty'].sum()
            eq_total = len(eq_df)
            result.append(f"  {equipment}: {int(eq_faulty)}/{eq_total} ({eq_faulty/eq_total*100:.2f}%)")
        
        return "\n".join(result)
    
    def _get_parameter_range(self, parameter: str, condition: str) -> str:
        """获取参数范围"""
        df = self.df
        
        if parameter not in ['temperature', 'pressure', 'vibration', 'humidity']:
            return f"❌ 不支持的参数: {parameter}。支持: temperature, pressure, vibration, humidity"
        
        if condition == "faulty":
            data = df[df['faulty'] == 1.0][parameter]
            title = f"故障样本的{parameter}参数"
        elif condition == "normal":
            data = df[df['faulty'] == 0.0][parameter]
            title = f"正常样本的{parameter}参数"
        else:
            data = df[parameter]
            title = f"全部样本的{parameter}参数"
        
        result = [
            f"📊 {title}",
            "=" * 60,
            f"样本数: {len(data)}",
            f"最小值: {data.min():.2f}",
            f"最大值: {data.max():.2f}",
            f"均值: {data.mean():.2f}",
            f"中位数: {data.median():.2f}",
            f"标准差: {data.std():.2f}",
            f"25%分位: {data.quantile(0.25):.2f}",
            f"75%分位: {data.quantile(0.75):.2f}",
        ]
        
        return "\n".join(result)
    
    def _compare_normal_vs_faulty(self) -> str:
        """对比正常和故障样本"""
        df = self.df
        faulty_df = df[df['faulty'] == 1.0]
        normal_df = df[df['faulty'] == 0.0]
        
        result = [
            "⚖️  正常 vs 故障样本对比",
            "=" * 60,
            f"正常样本数: {len(normal_df)} ({len(normal_df)/len(df)*100:.2f}%)",
            f"故障样本数: {len(faulty_df)} ({len(faulty_df)/len(df)*100:.2f}%)",
            "",
            "参数对比 (均值):",
        ]
        
        for param in ['temperature', 'pressure', 'vibration', 'humidity']:
            normal_mean = normal_df[param].mean()
            faulty_mean = faulty_df[param].mean()
            diff = ((faulty_mean - normal_mean) / normal_mean) * 100
            diff_sign = "↑" if diff > 0 else "↓"
            
            result.append(
                f"  {param}: 正常={normal_mean:.2f}, 故障={faulty_mean:.2f} "
                f"({diff_sign}{abs(diff):.1f}%)"
            )
        
        return "\n".join(result)


# 创建全局实例（可选）
_training_data_tool_instance = None


def get_training_data_tool() -> TrainingDataQueryTool:
    """获取训练数据查询工具实例（单例模式）"""
    global _training_data_tool_instance
    if _training_data_tool_instance is None:
        _training_data_tool_instance = TrainingDataQueryTool()
    return _training_data_tool_instance

