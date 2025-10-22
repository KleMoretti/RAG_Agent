"""
市场数据查询工具
供Market Agent使用，查询价格数据、新闻、趋势分析等
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..tools import Tool
from src.api.models import MarketPriceData, MarketNews
from src.api.db import get_db


class MarketQueryTool(Tool):
    """市场数据查询工具"""

    def __init__(self):
        super().__init__(
            name="market_query",
            description=(
                "查询钢铁市场数据，包括价格、新闻、趋势分析。"
                "支持的查询类型: "
                "1. 'price' - 查询价格数据 (参数: material_type, days)"
                "2. 'news' - 查询市场新闻 (参数: category, days)"
                "3. 'trend' - 查询价格趋势 (参数: material_type)"
                "4. 'compare' - 比较多个材料价格 (参数: material_types)"
            ),
        )
        self.db: Session = next(get_db())

    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        执行市场数据查询

        Args:
            query_type: 查询类型 (price/news/trend/compare)
            material_type: 材料类型（铁矿石、螺纹钢等）
            material_types: 材料类型列表（用于比较）
            category: 新闻分类
            days: 查询天数（默认7天）

        Returns:
            查询结果字典
        """
        query_type = kwargs.get("query_type", "price")

        try:
            if query_type == "price":
                return self._query_price(**kwargs)
            elif query_type == "news":
                return self._query_news(**kwargs)
            elif query_type == "trend":
                return self._query_trend(**kwargs)
            elif query_type == "compare":
                return self._compare_materials(**kwargs)
            else:
                return {
                    "success": False,
                    "error": f"不支持的查询类型: {query_type}",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _query_price(self, **kwargs: Any) -> Dict[str, Any]:
        """查询价格数据"""
        material_type = kwargs.get("material_type", "铁矿石")
        days = kwargs.get("days", 7)

        date_start = datetime.utcnow() - timedelta(days=days)

        prices = (
            self.db.query(MarketPriceData)
            .filter(
                MarketPriceData.material_type == material_type,
                MarketPriceData.price_date >= date_start,
            )
            .order_by(desc(MarketPriceData.price_date))
            .all()
        )

        if not prices:
            return {
                "success": False,
                "message": f"未找到{material_type}的价格数据",
            }

        latest_price = prices[0]
        price_list = [
            {
                "date": p.price_date.strftime("%Y-%m-%d"),
                "price": p.price,
                "change_rate": p.change_rate,
                "volume": p.volume,
            }
            for p in prices
        ]

        # 计算统计信息
        avg_price = sum(p.price for p in prices) / len(prices)
        max_price = max(p.price for p in prices)
        min_price = min(p.price for p in prices)

        return {
            "success": True,
            "material_type": material_type,
            "current_price": latest_price.price,
            "unit": latest_price.unit,
            "change_rate": latest_price.change_rate,
            "price_date": latest_price.price_date.strftime("%Y-%m-%d %H:%M"),
            "statistics": {
                "avg_price": round(avg_price, 2),
                "max_price": max_price,
                "min_price": min_price,
                "volatility": round((max_price - min_price) / avg_price * 100, 2),
            },
            "price_history": price_list[:10],  # 返回最近10条
        }

    def _query_news(self, **kwargs: Any) -> Dict[str, Any]:
        """查询市场新闻"""
        category = kwargs.get("category")
        days = kwargs.get("days", 7)

        date_start = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(MarketNews).filter(MarketNews.publish_time >= date_start)

        if category:
            query = query.filter(MarketNews.category == category)

        news_list = query.order_by(desc(MarketNews.publish_time)).limit(10).all()

        if not news_list:
            return {
                "success": False,
                "message": f"未找到{'分类为' + category + '的' if category else ''}市场新闻",
            }

        return {
            "success": True,
            "count": len(news_list),
            "news": [
                {
                    "title": n.title,
                    "summary": n.summary or n.content[:200] if n.content else None,
                    "source": n.source,
                    "category": n.category,
                    "publish_time": n.publish_time.strftime("%Y-%m-%d %H:%M"),
                    "sentiment": n.sentiment,
                    "is_important": n.is_important,
                    "keywords": n.keywords,
                }
                for n in news_list
            ],
        }

    def _query_trend(self, **kwargs: Any) -> Dict[str, Any]:
        """查询价格趋势"""
        material_type = kwargs.get("material_type", "铁矿石")

        # 获取最近30天的数据
        now = datetime.utcnow()
        date_7d_ago = now - timedelta(days=7)
        date_30d_ago = now - timedelta(days=30)

        # 最新价格
        latest_price = (
            self.db.query(MarketPriceData)
            .filter(MarketPriceData.material_type == material_type)
            .order_by(desc(MarketPriceData.price_date))
            .first()
        )

        if not latest_price:
            return {
                "success": False,
                "message": f"未找到{material_type}的价格数据",
            }

        # 7天平均价格
        avg_7d = (
            self.db.query(func.avg(MarketPriceData.price))
            .filter(
                MarketPriceData.material_type == material_type,
                MarketPriceData.price_date >= date_7d_ago,
            )
            .scalar()
        ) or 0.0

        # 30天平均价格
        avg_30d = (
            self.db.query(func.avg(MarketPriceData.price))
            .filter(
                MarketPriceData.material_type == material_type,
                MarketPriceData.price_date >= date_30d_ago,
            )
            .scalar()
        ) or 0.0

        # 计算涨跌幅
        change_rate_7d = (
            ((latest_price.price - avg_7d) / avg_7d * 100) if avg_7d > 0 else 0.0
        )
        change_rate_30d = (
            ((latest_price.price - avg_30d) / avg_30d * 100) if avg_30d > 0 else 0.0
        )

        # 判断趋势
        if change_rate_7d > 2:
            trend = "上涨"
            trend_description = f"近期呈上涨趋势，7天涨幅{change_rate_7d:.2f}%"
        elif change_rate_7d < -2:
            trend = "下跌"
            trend_description = f"近期呈下跌趋势，7天跌幅{abs(change_rate_7d):.2f}%"
        else:
            trend = "震荡"
            trend_description = f"近期价格震荡，7天变化{change_rate_7d:.2f}%"

        # 简单预测
        forecast_min = latest_price.price * 0.98
        forecast_max = latest_price.price * 1.02
        forecast_avg = (forecast_min + forecast_max) / 2

        return {
            "success": True,
            "material_type": material_type,
            "current_price": latest_price.price,
            "unit": latest_price.unit,
            "avg_price_7d": round(avg_7d, 2),
            "avg_price_30d": round(avg_30d, 2),
            "change_rate_7d": round(change_rate_7d, 2),
            "change_rate_30d": round(change_rate_30d, 2),
            "trend": trend,
            "trend_description": trend_description,
            "forecast_7d": {
                "min": round(forecast_min, 2),
                "max": round(forecast_max, 2),
                "avg": round(forecast_avg, 2),
            },
        }

    def _compare_materials(self, **kwargs: Any) -> Dict[str, Any]:
        """比较多个材料价格"""
        material_types = kwargs.get("material_types", ["铁矿石", "螺纹钢", "焦炭"])

        comparisons = []

        for material_type in material_types:
            latest_price = (
                self.db.query(MarketPriceData)
                .filter(MarketPriceData.material_type == material_type)
                .order_by(desc(MarketPriceData.price_date))
                .first()
            )

            if latest_price:
                comparisons.append(
                    {
                        "material_type": material_type,
                        "price": latest_price.price,
                        "unit": latest_price.unit,
                        "change_rate": latest_price.change_rate,
                        "price_date": latest_price.price_date.strftime("%Y-%m-%d"),
                    }
                )

        if not comparisons:
            return {
                "success": False,
                "message": "未找到任何价格数据",
            }

        return {
            "success": True,
            "count": len(comparisons),
            "comparisons": comparisons,
        }


# 工具实例（供 Agent 使用）
market_query_tool = MarketQueryTool()

