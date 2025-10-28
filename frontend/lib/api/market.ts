/**
 * 市场数据API客户端
 * 提供价格数据、新闻、趋势分析等接口
 */

import apiClient from "./client";

// ==================== 类型定义 ====================

export interface PriceData {
    id: number;
    material_type: string;
    category: string;
    price: number;
    unit: string;
    region?: string;
    source?: string;
    price_date: string;
    change_rate?: number;
    change_amount?: number;
    volume?: number;
    high_price?: number;
    low_price?: number;
    meta_data?: Record<string, any>;
    created_at: string;
    created_by?: number;
}

export interface MarketNews {
    id: number;
    title: string;
    content?: string;
    summary?: string;
    source: string;
    category: string;
    url?: string;
    publish_time: string;
    sentiment?: "positive" | "negative" | "neutral";
    keywords?: string[];
    related_materials?: string[];
    is_important: boolean;
    meta_data?: Record<string, any>;
    created_at: string;
    created_by?: number;
}

export interface TrendAnalysis {
    material_type: string;
    current_price: number;
    avg_price_7d: number;
    avg_price_30d: number;
    change_rate_7d: number;
    change_rate_30d: number;
    trend: "上涨" | "下跌" | "震荡";
    forecast_7d: {
        min: number;
        max: number;
        avg: number;
    };
    confidence: "高" | "中等" | "低";
}

export interface MarketSummary {
    latest_prices: Array<{
        id: number;  // 添加唯一ID，用于React key
        material_type: string;
        category: string;
        price: number;
        unit: string;
        change_rate?: number;
        price_date: string;
    }>;
    statistics: {
        total_materials: number;
        total_news: number;
        recent_news_count: number;
    };
}

export interface BatchUploadResponse {
    success_count: number;
    error_count: number;
    errors: Array<{
        row: number;
        error: string;
    }>;
    message: string;
}

export interface DataSource {
    id: number;
    name: string;
    source_type: string;
    api_url?: string;
    data_format?: string;
    update_frequency?: number;
    is_active: boolean;
    last_update?: string;
    error_count: number;
    description?: string;
    created_at: string;
    updated_at: string;
}

// ==================== API 接口 ====================

/**
 * 获取价格数据列表
 */
export async function getPrices(params?: {
    material_type?: string;
    category?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
}): Promise<PriceData[]> {
    const { data } = await apiClient.get<PriceData[]>("/api/market/prices", {
        params,
    });
    return data;
}

/**
 * 创建价格数据
 */
export async function createPrice(priceData: {
    material_type: string;
    category: string;
    price: number;
    unit?: string;
    region?: string;
    source?: string;
    price_date: string;
    change_rate?: number;
    change_amount?: number;
    volume?: number;
    high_price?: number;
    low_price?: number;
    meta_data?: Record<string, any>;
}): Promise<PriceData> {
    const { data } = await apiClient.post<PriceData>(
        "/api/market/prices",
        priceData
    );
    return data;
}

/**
 * 批量上传价格数据
 */
export async function batchUploadPrices(
    file: File
): Promise<BatchUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await apiClient.post<BatchUploadResponse>(
        "/api/market/prices/batch-upload",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );
    return data;
}

/**
 * 删除价格数据
 */
export async function deletePrice(priceId: number): Promise<void> {
    await apiClient.delete(`/api/market/prices/${priceId}`);
}

/**
 * 获取市场新闻列表
 */
export async function getNews(params?: {
    category?: string;
    start_date?: string;
    end_date?: string;
    is_important?: boolean;
    limit?: number;
}): Promise<MarketNews[]> {
    const { data } = await apiClient.get<MarketNews[]>("/api/market/news", {
        params,
    });
    return data;
}

/**
 * 创建市场新闻
 */
export async function createNews(newsData: {
    title: string;
    content?: string;
    summary?: string;
    source: string;
    category: string;
    url?: string;
    publish_time: string;
    sentiment?: "positive" | "negative" | "neutral";
    keywords?: string[];
    related_materials?: string[];
    is_important?: boolean;
    meta_data?: Record<string, any>;
}): Promise<MarketNews> {
    const { data } = await apiClient.post<MarketNews>(
        "/api/market/news",
        newsData
    );
    return data;
}

/**
 * 获取趋势分析
 */
export async function getTrendAnalysis(
    material_types?: string[]
): Promise<TrendAnalysis[]> {
    const { data} = await apiClient.get<TrendAnalysis[]>(
        "/api/market/analysis/trend",
        {
            params: material_types
                ? { material_types: material_types }
                : undefined,
        }
    );
    return data;
}

/**
 * 获取市场概况
 */
export async function getMarketSummary(): Promise<MarketSummary> {
    const { data } = await apiClient.get<MarketSummary>(
        "/api/market/analysis/summary"
    );
    return data;
}

/**
 * 获取数据源列表
 */
export async function getDataSources(): Promise<DataSource[]> {
    const { data } = await apiClient.get<DataSource[]>(
        "/api/market/data-sources"
    );
    return data;
}

/**
 * 创建数据源
 */
export async function createDataSource(sourceData: {
    name: string;
    source_type: string;
    api_url?: string;
    api_key?: string;
    headers?: Record<string, string>;
    params?: Record<string, any>;
    data_format?: string;
    update_frequency?: number;
    description?: string;
    meta_data?: Record<string, any>;
}): Promise<DataSource> {
    const { data } = await apiClient.post<DataSource>(
        "/api/market/data-sources",
        sourceData
    );
    return data;
}

