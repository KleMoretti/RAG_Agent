import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

/**
 * 格式化文件大小
 * @param bytes - 字节数
 * @returns 格式化后的字符串（如 "1.5 MB"）
 */
export function formatBytes(bytes: number): string {
    if (bytes === 0) return "0 Bytes";

    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
}

/**
 * 格式化日期时间
 * @param dateString - ISO 日期字符串
 * @returns 格式化后的日期时间字符串
 */
export function formatDate(dateString: string): string {
    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
        return "无效日期";
    }

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    // 相对时间（24小时内）
    if (diffMins < 1) {
        return "刚刚";
    } else if (diffMins < 60) {
        return `${diffMins} 分钟前`;
    } else if (diffHours < 24) {
        return `${diffHours} 小时前`;
    } else if (diffDays < 7) {
        return `${diffDays} 天前`;
    }

    // 绝对时间
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");

    const currentYear = now.getFullYear();

    if (year === currentYear) {
        return `${month}-${day} ${hours}:${minutes}`;
    } else {
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }
}

/**
 * 格式化相对时间
 * @param dateString - ISO 日期字符串
 * @returns 相对时间字符串
 */
export function formatRelativeTime(dateString: string): string {
    const date = new Date(dateString);

    if (isNaN(date.getTime())) {
        return "无效日期";
    }

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffSecs < 60) {
        return "刚刚";
    } else if (diffMins < 60) {
        return `${diffMins} 分钟前`;
    } else if (diffHours < 24) {
        return `${diffHours} 小时前`;
    } else if (diffDays < 30) {
        return `${diffDays} 天前`;
    } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30);
        return `${months} 个月前`;
    } else {
        const years = Math.floor(diffDays / 365);
        return `${years} 年前`;
    }
}

/**
 * 截断文本
 * @param text - 原始文本
 * @param maxLength - 最大长度
 * @returns 截断后的文本
 */
export function truncateText(text: string, maxLength: number = 50): string {
    if (text.length <= maxLength) {
        return text;
    }
    return text.slice(0, maxLength) + "...";
}
