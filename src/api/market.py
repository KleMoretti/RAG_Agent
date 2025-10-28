"""
市场数据管理API
提供价格数据、市场新闻、数据源管理等接口
"""
from __future__ import annotations

import logging
from typing import List, Optional
from datetime import datetime, timedelta
import io

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, func
import pandas as pd

from src.api.db import get_db
from src.api.models import (
    User,
    UserRole,
    MarketPriceData,
    MarketNews,
    MarketDataSource,
)
from src.api.auth import _get_current_user

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market", tags=["market"])


# 权限检查
def require_manager_or_admin(user: User = Depends(_get_current_user)) -> User:
    """要求经理或管理员权限"""
    if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        logger.warning(
            f"User {user.username} (role={user.role}) attempted market management access"
        )
        raise HTTPException(status_code=403, detail="需要经理或管理员权限")
    return user


# ==================== Pydantic 模型 ====================

class PriceDataCreate(BaseModel):
    """价格数据创建请求"""

    material_type: str = Field(..., description="材料类型（铁矿石、螺纹钢等）")
    category: str = Field(..., description="分类（raw_material/product）")
    price: float = Field(..., description="价格（元/吨）")
    unit: str = Field(default="元/吨", description="单位")
    region: Optional[str] = Field(None, description="地区")
    source: Optional[str] = Field(None, description="数据来源")
    price_date: datetime = Field(..., description="价格日期")
    change_rate: Optional[float] = Field(None, description="涨跌幅（%）")
    change_amount: Optional[float] = Field(None, description="涨跌金额")
    volume: Optional[float] = Field(None, description="成交量（吨）")
    high_price: Optional[float] = Field(None, description="最高价")
    low_price: Optional[float] = Field(None, description="最低价")
    meta_data: Optional[dict] = Field(None, description="其他元数据")


class PriceDataUpdate(BaseModel):
    """价格数据更新请求"""

    price: Optional[float] = None
    change_rate: Optional[float] = None
    change_amount: Optional[float] = None
    volume: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    meta_data: Optional[dict] = None


class PriceDataResponse(BaseModel):
    """价格数据响应"""

    id: int
    material_type: str
    category: str
    price: float
    unit: str
    region: Optional[str]
    source: Optional[str]
    price_date: datetime
    change_rate: Optional[float]
    change_amount: Optional[float]
    volume: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    meta_data: Optional[dict]
    created_at: datetime
    created_by: Optional[int]


class NewsCreate(BaseModel):
    """新闻创建请求"""

    title: str = Field(..., max_length=256, description="新闻标题")
    content: Optional[str] = Field(None, description="新闻内容")
    summary: Optional[str] = Field(None, description="摘要")
    source: str = Field(..., max_length=128, description="来源")
    category: str = Field(..., max_length=64, description="分类（供应/需求/政策等）")
    url: Optional[str] = Field(None, max_length=512, description="原文链接")
    publish_time: datetime = Field(..., description="发布时间")
    sentiment: Optional[str] = Field(None, description="情绪（positive/negative/neutral）")
    keywords: Optional[List[str]] = Field(None, description="关键词")
    related_materials: Optional[List[str]] = Field(None, description="相关材料")
    is_important: bool = Field(default=False, description="是否重要")
    meta_data: Optional[dict] = Field(None, description="其他元数据")


class NewsResponse(BaseModel):
    """新闻响应"""

    id: int
    title: str
    content: Optional[str]
    summary: Optional[str]
    source: str
    category: str
    url: Optional[str]
    publish_time: datetime
    sentiment: Optional[str]
    keywords: Optional[List[str]]
    related_materials: Optional[List[str]]
    is_important: bool
    meta_data: Optional[dict]
    created_at: datetime
    created_by: Optional[int]


class DataSourceCreate(BaseModel):
    """数据源创建请求"""

    name: str = Field(..., max_length=128, description="数据源名称")
    source_type: str = Field(..., description="类型（api/upload/manual）")
    api_url: Optional[str] = Field(None, max_length=512, description="API地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    headers: Optional[dict] = Field(None, description="请求头")
    params: Optional[dict] = Field(None, description="请求参数")
    data_format: Optional[str] = Field(None, description="数据格式（json/xml/csv）")
    update_frequency: Optional[int] = Field(None, description="更新频率（分钟）")
    description: Optional[str] = Field(None, description="描述")
    meta_data: Optional[dict] = Field(None, description="其他配置")


class DataSourceResponse(BaseModel):
    """数据源响应"""

    id: int
    name: str
    source_type: str
    api_url: Optional[str]
    data_format: Optional[str]
    update_frequency: Optional[int]
    is_active: bool
    last_update: Optional[datetime]
    error_count: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class TrendAnalysisResponse(BaseModel):
    """趋势分析响应"""

    material_type: str
    current_price: float
    avg_price_7d: float
    avg_price_30d: float
    change_rate_7d: float
    change_rate_30d: float
    trend: str  # "上涨"/"下跌"/"震荡"
    forecast_7d: dict  # {"min": float, "max": float, "avg": float}
    confidence: str  # "高"/"中等"/"低"


class BatchUploadResponse(BaseModel):
    """批量上传响应"""

    success_count: int
    error_count: int
    errors: List[dict]
    message: str


# ==================== 辅助函数 ====================

def _calculate_change_rate(
    db: Session,
    material_type: str,
    current_price: float,
    price_date: datetime,
) -> tuple[float | None, float | None]:
    """
    自动计算涨跌幅和涨跌金额
    基于上周同期数据（7天前）
    
    Returns:
        (change_rate, change_amount) 或 (None, None) 如果没有历史数据
    """
    # 查询7天前的最近一条数据
    last_week_date = price_date - timedelta(days=7)
    last_week_price = (
        db.query(MarketPriceData)
        .filter(
            MarketPriceData.material_type == material_type,
            MarketPriceData.price_date <= last_week_date,
        )
        .order_by(MarketPriceData.price_date.desc())
        .first()
    )
    
    if last_week_price and last_week_price.price > 0:
        change_amount = current_price - last_week_price.price
        change_rate = (change_amount / last_week_price.price) * 100
        return round(change_rate, 2), round(change_amount, 2)
    
    return None, None


# ==================== 价格数据接口 ====================

@router.get("/prices", response_model=List[PriceDataResponse])
def list_prices(
    material_type: Optional[str] = Query(None, description="材料类型筛选"),
    category: Optional[str] = Query(None, description="分类筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(_get_current_user),
):
    """
    获取价格数据列表
    支持按材料类型、分类、日期范围筛选
    """
    query = db.query(MarketPriceData)

    if material_type:
        query = query.filter(MarketPriceData.material_type == material_type)
    if category:
        query = query.filter(MarketPriceData.category == category)
    if start_date:
        query = query.filter(MarketPriceData.price_date >= start_date)
    if end_date:
        query = query.filter(MarketPriceData.price_date <= end_date)

    prices = query.order_by(desc(MarketPriceData.price_date)).limit(limit).all()

    return [
        PriceDataResponse(
            id=p.id,
            material_type=p.material_type,
            category=p.category,
            price=p.price,
            unit=p.unit,
            region=p.region,
            source=p.source,
            price_date=p.price_date,
            change_rate=p.change_rate,
            change_amount=p.change_amount,
            volume=p.volume,
            high_price=p.high_price,
            low_price=p.low_price,
            meta_data=p.meta_data,
            created_at=p.created_at,
            created_by=p.created_by,
        )
        for p in prices
    ]


@router.post("/prices", response_model=PriceDataResponse)
def create_price(
    price_data: PriceDataCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    创建价格数据
    需要经理或管理员权限
    自动计算涨跌幅（如果未提供）
    """
    # 如果没有提供 change_rate，自动计算
    change_rate = price_data.change_rate
    change_amount = price_data.change_amount
    
    if change_rate is None or change_rate == 0:
        calc_rate, calc_amount = _calculate_change_rate(
            db, price_data.material_type, price_data.price, price_data.price_date
        )
        if calc_rate is not None:
            change_rate = calc_rate
            change_amount = calc_amount
            logger.info(
                f"Auto-calculated change_rate for {price_data.material_type}: {change_rate}%"
            )
    
    new_price = MarketPriceData(
        material_type=price_data.material_type,
        category=price_data.category,
        price=price_data.price,
        unit=price_data.unit,
        region=price_data.region,
        source=price_data.source,
        price_date=price_data.price_date,
        change_rate=change_rate,
        change_amount=change_amount,
        volume=price_data.volume,
        high_price=price_data.high_price,
        low_price=price_data.low_price,
        meta_data=price_data.meta_data,
        created_by=user.id,
    )

    db.add(new_price)
    db.commit()
    db.refresh(new_price)

    logger.info(
        f"User {user.username} created price data for {price_data.material_type}"
    )

    return PriceDataResponse(
        id=new_price.id,
        material_type=new_price.material_type,
        category=new_price.category,
        price=new_price.price,
        unit=new_price.unit,
        region=new_price.region,
        source=new_price.source,
        price_date=new_price.price_date,
        change_rate=new_price.change_rate,
        change_amount=new_price.change_amount,
        volume=new_price.volume,
        high_price=new_price.high_price,
        low_price=new_price.low_price,
        meta_data=new_price.meta_data,
        created_at=new_price.created_at,
        created_by=new_price.created_by,
    )


@router.post("/prices/batch-upload", response_model=BatchUploadResponse)
async def batch_upload_prices(
    file: UploadFile = File(..., description="Excel或CSV文件"),
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    批量上传价格数据
    支持Excel (.xlsx, .xls) 和 CSV 格式
    
    文件格式要求：
    列名: material_type, category, price, unit, region, source, price_date, 
          change_rate, change_amount, volume, high_price, low_price
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 检查文件格式
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ["xlsx", "xls", "csv"]:
        raise HTTPException(
            status_code=400, detail="不支持的文件格式，仅支持 .xlsx, .xls, .csv"
        )

    try:
        # 读取文件
        contents = await file.read()
        if file_ext == "csv":
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 验证必填列
        required_columns = ["material_type", "category", "price", "price_date"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必填列: {', '.join(missing_columns)}",
            )

        success_count = 0
        error_count = 0
        errors = []

        # 批量插入
        for idx, row in df.iterrows():
            try:
                # 解析日期
                price_date = pd.to_datetime(row["price_date"])
                
                # 获取原始 change_rate
                change_rate = (
                    float(row["change_rate"])
                    if pd.notna(row.get("change_rate")) and float(row.get("change_rate", 0)) != 0
                    else None
                )
                change_amount = (
                    float(row["change_amount"])
                    if pd.notna(row.get("change_amount"))
                    else None
                )
                
                # 如果没有提供 change_rate，自动计算
                if change_rate is None:
                    calc_rate, calc_amount = _calculate_change_rate(
                        db, str(row["material_type"]), float(row["price"]), price_date
                    )
                    if calc_rate is not None:
                        change_rate = calc_rate
                        change_amount = calc_amount

                new_price = MarketPriceData(
                    material_type=str(row["material_type"]),
                    category=str(row["category"]),
                    price=float(row["price"]),
                    unit=str(row.get("unit", "元/吨")),
                    region=str(row["region"]) if pd.notna(row.get("region")) else None,
                    source=str(row["source"]) if pd.notna(row.get("source")) else None,
                    price_date=price_date,
                    change_rate=change_rate,
                    change_amount=change_amount,
                    volume=(
                        float(row["volume"]) if pd.notna(row.get("volume")) else None
                    ),
                    high_price=(
                        float(row["high_price"])
                        if pd.notna(row.get("high_price"))
                        else None
                    ),
                    low_price=(
                        float(row["low_price"])
                        if pd.notna(row.get("low_price"))
                        else None
                    ),
                    created_by=user.id,
                )

                db.add(new_price)
                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append({"row": idx + 2, "error": str(e)})  # +2 因为有表头和从0开始
                logger.error(f"Error importing row {idx + 2}: {str(e)}")

        db.commit()

        logger.info(
            f"User {user.username} batch uploaded {success_count} price records"
        )

        return BatchUploadResponse(
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            message=f"成功导入 {success_count} 条数据，失败 {error_count} 条",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量上传失败: {str(e)}")


@router.delete("/prices/{price_id}")
def delete_price(
    price_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    删除价格数据
    需要经理或管理员权限
    """
    price = db.query(MarketPriceData).filter(MarketPriceData.id == price_id).first()
    if not price:
        raise HTTPException(status_code=404, detail="价格数据不存在")

    db.delete(price)
    db.commit()

    logger.info(f"User {user.username} deleted price data {price_id}")

    return {"success": True, "message": "删除成功"}


# ==================== 市场新闻接口 ====================

@router.get("/news", response_model=List[NewsResponse])
def list_news(
    category: Optional[str] = Query(None, description="分类筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    is_important: Optional[bool] = Query(None, description="是否重要"),
    limit: int = Query(50, ge=1, le=500, description="返回数量"),
    db: Session = Depends(get_db),
    user: User = Depends(_get_current_user),
):
    """
    获取市场新闻列表
    支持按分类、日期范围、重要性筛选
    """
    query = db.query(MarketNews)

    if category:
        query = query.filter(MarketNews.category == category)
    if start_date:
        query = query.filter(MarketNews.publish_time >= start_date)
    if end_date:
        query = query.filter(MarketNews.publish_time <= end_date)
    if is_important is not None:
        query = query.filter(MarketNews.is_important == is_important)

    news_list = query.order_by(desc(MarketNews.publish_time)).limit(limit).all()

    return [
        NewsResponse(
            id=n.id,
            title=n.title,
            content=n.content,
            summary=n.summary,
            source=n.source,
            category=n.category,
            url=n.url,
            publish_time=n.publish_time,
            sentiment=n.sentiment,
            keywords=n.keywords,
            related_materials=n.related_materials,
            is_important=n.is_important,
            meta_data=n.meta_data,
            created_at=n.created_at,
            created_by=n.created_by,
        )
        for n in news_list
    ]


@router.post("/news", response_model=NewsResponse)
def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    创建市场新闻
    需要经理或管理员权限
    """
    new_news = MarketNews(
        title=news_data.title,
        content=news_data.content,
        summary=news_data.summary,
        source=news_data.source,
        category=news_data.category,
        url=news_data.url,
        publish_time=news_data.publish_time,
        sentiment=news_data.sentiment,
        keywords=news_data.keywords,
        related_materials=news_data.related_materials,
        is_important=news_data.is_important,
        meta_data=news_data.meta_data,
        created_by=user.id,
    )

    db.add(new_news)
    db.commit()
    db.refresh(new_news)

    logger.info(f"User {user.username} created news: {news_data.title}")

    return NewsResponse(
        id=new_news.id,
        title=new_news.title,
        content=new_news.content,
        summary=new_news.summary,
        source=new_news.source,
        category=new_news.category,
        url=new_news.url,
        publish_time=new_news.publish_time,
        sentiment=new_news.sentiment,
        keywords=new_news.keywords,
        related_materials=new_news.related_materials,
        is_important=new_news.is_important,
        meta_data=new_news.meta_data,
        created_at=new_news.created_at,
        created_by=new_news.created_by,
    )


# ==================== 趋势分析接口 ====================

@router.get("/analysis/trend", response_model=List[TrendAnalysisResponse])
def analyze_trend(
    material_types: Optional[List[str]] = Query(None, description="材料类型列表"),
    db: Session = Depends(get_db),
    user: User = Depends(_get_current_user),
):
    """
    趋势分析
    分析指定材料的价格趋势
    """
    if not material_types:
        # 默认分析主要材料
        material_types = ["铁矿石", "螺纹钢", "焦炭", "废钢"]

    results = []

    for material_type in material_types:
        # 获取最近30天的数据
        now = datetime.utcnow()
        date_7d_ago = now - timedelta(days=7)
        date_30d_ago = now - timedelta(days=30)

        # 最新价格
        latest_price = (
            db.query(MarketPriceData)
            .filter(MarketPriceData.material_type == material_type)
            .order_by(desc(MarketPriceData.price_date))
            .first()
        )

        if not latest_price:
            continue

        # 7天平均价格
        avg_7d = (
            db.query(func.avg(MarketPriceData.price))
            .filter(
                MarketPriceData.material_type == material_type,
                MarketPriceData.price_date >= date_7d_ago,
            )
            .scalar()
        ) or 0.0

        # 30天平均价格
        avg_30d = (
            db.query(func.avg(MarketPriceData.price))
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
        elif change_rate_7d < -2:
            trend = "下跌"
        else:
            trend = "震荡"

        # 简单预测（基于近期趋势）
        forecast_min = latest_price.price * 0.98
        forecast_max = latest_price.price * 1.02
        forecast_avg = (forecast_min + forecast_max) / 2

        # 置信度（基于数据量）
        data_count = (
            db.query(func.count(MarketPriceData.id))
            .filter(
                MarketPriceData.material_type == material_type,
                MarketPriceData.price_date >= date_7d_ago,
            )
            .scalar()
        ) or 0

        if data_count >= 7:
            confidence = "高"
        elif data_count >= 3:
            confidence = "中等"
        else:
            confidence = "低"

        results.append(
            TrendAnalysisResponse(
                material_type=material_type,
                current_price=latest_price.price,
                avg_price_7d=round(avg_7d, 2),
                avg_price_30d=round(avg_30d, 2),
                change_rate_7d=round(change_rate_7d, 2),
                change_rate_30d=round(change_rate_30d, 2),
                trend=trend,
                forecast_7d={
                    "min": round(forecast_min, 2),
                    "max": round(forecast_max, 2),
                    "avg": round(forecast_avg, 2),
                },
                confidence=confidence,
            )
        )

    return results


@router.get("/analysis/summary")
def get_market_summary(
    db: Session = Depends(get_db),
    user: User = Depends(_get_current_user),
):
    """
    市场概况
    返回所有材料的最新价格和统计信息
    """
    # 获取所有材料的最新价格
    subquery = (
        db.query(
            MarketPriceData.material_type,
            func.max(MarketPriceData.price_date).label("max_date"),
        )
        .group_by(MarketPriceData.material_type)
        .subquery()
    )

    latest_prices = (
        db.query(MarketPriceData)
        .join(
            subquery,
            (MarketPriceData.material_type == subquery.c.material_type)
            & (MarketPriceData.price_date == subquery.c.max_date),
        )
        .order_by(MarketPriceData.id.desc())  # 按ID降序，取最新插入的记录
        .all()
    )

    # 去重：每个 material_type 只保留一条记录（最新的）
    seen_materials = set()
    unique_prices = []
    for p in latest_prices:
        if p.material_type not in seen_materials:
            seen_materials.add(p.material_type)
            unique_prices.append(p)

    # 计算"较上周"的涨跌幅
    prices_with_change = []
    for p in unique_prices:
        # 查询上周同期数据（7天前）
        last_week_date = p.price_date - timedelta(days=7)
        last_week_price = (
            db.query(MarketPriceData)
            .filter(
                MarketPriceData.material_type == p.material_type,
                MarketPriceData.price_date <= last_week_date,
            )
            .order_by(MarketPriceData.price_date.desc())
            .first()
        )
        
        # 计算涨跌幅
        if last_week_price and last_week_price.price > 0:
            change_rate = ((p.price - last_week_price.price) / last_week_price.price) * 100
        else:
            change_rate = p.change_rate  # 如果没有上周数据，使用原有数据
        
        prices_with_change.append({
            "id": p.id,
            "material_type": p.material_type,
            "category": p.category,
            "price": p.price,
            "unit": p.unit,
            "change_rate": change_rate,
            "price_date": p.price_date,
        })

    # 统计信息
    total_materials = (
        db.query(func.count(func.distinct(MarketPriceData.material_type))).scalar()
        or 0
    )
    total_news = db.query(func.count(MarketNews.id)).scalar() or 0
    recent_news_count = (
        db.query(func.count(MarketNews.id))
        .filter(MarketNews.publish_time >= datetime.utcnow() - timedelta(days=7))
        .scalar()
        or 0
    )

    return {
        "latest_prices": prices_with_change,
        "statistics": {
            "total_materials": total_materials,
            "total_news": total_news,
            "recent_news_count": recent_news_count,
        },
    }


# ==================== 数据源管理接口 ====================

@router.get("/data-sources", response_model=List[DataSourceResponse])
def list_data_sources(
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    获取数据源列表
    需要经理或管理员权限
    """
    sources = db.query(MarketDataSource).order_by(desc(MarketDataSource.created_at)).all()

    return [
        DataSourceResponse(
            id=s.id,
            name=s.name,
            source_type=s.source_type,
            api_url=s.api_url,
            data_format=s.data_format,
            update_frequency=s.update_frequency,
            is_active=s.is_active,
            last_update=s.last_update,
            error_count=s.error_count,
            description=s.description,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sources
    ]


@router.post("/data-sources", response_model=DataSourceResponse)
def create_data_source(
    source_data: DataSourceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_manager_or_admin),
):
    """
    创建数据源
    需要经理或管理员权限
    """
    # 检查名称是否已存在
    existing_source = (
        db.query(MarketDataSource)
        .filter(MarketDataSource.name == source_data.name)
        .first()
    )
    if existing_source:
        raise HTTPException(status_code=400, detail="数据源名称已存在")

    new_source = MarketDataSource(
        name=source_data.name,
        source_type=source_data.source_type,
        api_url=source_data.api_url,
        api_key=source_data.api_key,
        headers=source_data.headers,
        params=source_data.params,
        data_format=source_data.data_format,
        update_frequency=source_data.update_frequency,
        description=source_data.description,
        meta_data=source_data.meta_data,
        created_by=user.id,
    )

    db.add(new_source)
    db.commit()
    db.refresh(new_source)

    logger.info(f"User {user.username} created data source: {source_data.name}")

    return DataSourceResponse(
        id=new_source.id,
        name=new_source.name,
        source_type=new_source.source_type,
        api_url=new_source.api_url,
        data_format=new_source.data_format,
        update_frequency=new_source.update_frequency,
        is_active=new_source.is_active,
        last_update=new_source.last_update,
        error_count=new_source.error_count,
        description=new_source.description,
        created_at=new_source.created_at,
        updated_at=new_source.updated_at,
    )

