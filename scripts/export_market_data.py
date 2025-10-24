"""
市场数据导出工具
将数据库中的 Mysteel 数据导出为 CSV 文件

使用方法：
    python scripts/export_market_data.py --output mysteel_backup.csv
    python scripts/export_market_data.py --material 螺纹 --start-date 2025-01-01
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.api.db import get_db
from src.api.models import MarketPriceData
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def export_market_data(
    output_path: str,
    material_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    source: str = "Mysteel"
):
    """
    导出市场数据
    
    Args:
        output_path: 输出CSV文件路径
        material_type: 材料类型（可选）
        start_date: 开始日期（可选）
        end_date: 结束日期（可选）
        source: 数据来源（默认 Mysteel）
    """
    logger.info("🔍 开始导出市场数据...")
    
    try:
        # 连接数据库
        db = next(get_db())
        
        # 构建查询
        query = db.query(MarketPriceData)
        
        if source:
            query = query.filter(MarketPriceData.source == source)
        
        if material_type:
            query = query.filter(MarketPriceData.material_type == material_type)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(MarketPriceData.price_date >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(MarketPriceData.price_date <= end_dt)
        
        # 执行查询
        results = query.order_by(MarketPriceData.price_date.desc()).all()
        
        if not results:
            logger.warning("⚠️  未找到符合条件的数据")
            return
        
        # 转换为 DataFrame
        data = []
        for record in results:
            data.append({
                "id": record.id,
                "material_type": record.material_type,
                "category": record.category,
                "price": record.price,
                "unit": record.unit,
                "region": record.region,
                "source": record.source,
                "price_date": record.price_date.strftime("%Y-%m-%d"),
                "change_rate": record.change_rate,
                "change_amount": record.change_amount,
                "volume": record.volume,
                "high_price": record.high_price,
                "low_price": record.low_price,
                "created_at": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "created_by": record.created_by,
            })
        
        df = pd.DataFrame(data)
        
        # 保存到 CSV
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        
        logger.info(f"✅ 成功导出 {len(df)} 条数据到: {output_path}")
        
        # 显示统计信息
        print("\n📊 数据统计:")
        print(f"   总记录数: {len(df)}")
        print(f"   材料类型: {df['material_type'].nunique()} 种")
        print(f"   日期范围: {df['price_date'].min()} ~ {df['price_date'].max()}")
        print(f"   数据来源: {', '.join(df['source'].unique())}")
        
        # 按材料统计
        print("\n📈 材料分布:")
        material_counts = df['material_type'].value_counts()
        for material, count in material_counts.items():
            print(f"   - {material}: {count} 条")
        
    except Exception as e:
        logger.error(f"❌ 导出失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Mysteel 市场数据导出工具")
    parser.add_argument(
        "--output",
        type=str,
        default=f"mysteel_export_{datetime.now().strftime('%Y%m%d')}.csv",
        help="输出CSV文件路径",
    )
    parser.add_argument(
        "--material",
        type=str,
        default=None,
        help="材料类型（可选，如: 螺纹钢、铁矿石）",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="开始日期（YYYY-MM-DD）",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="结束日期（YYYY-MM-DD）",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="Mysteel",
        help="数据来源（默认 Mysteel）",
    )
    
    args = parser.parse_args()
    
    try:
        export_market_data(
            output_path=args.output,
            material_type=args.material,
            start_date=args.start_date,
            end_date=args.end_date,
            source=args.source,
        )
        
        print("\n🎉 导出完成！")
        
    except Exception as e:
        logger.error(f"❌ 任务失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

