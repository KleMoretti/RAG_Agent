"""
Prompt版本管理工具类
提供高级版本管理功能
"""
from __future__ import annotations

import re
import json
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from src.api.models import SystemPrompt, PromptVersion, PromptUsageStats, PromptStatus
from .schemas import PromptVersionResponse, SystemPromptResponse
from config.logging_config import setup_logging

logger = setup_logging()


@dataclass
class VersionComparison:
    """版本比较结果"""
    version_a: str
    version_b: str
    content_diff: str
    variables_diff: Dict[str, Any]
    meta_data_diff: Dict[str, Any]
    similarity_score: float


@dataclass
class VersionMetrics:
    """版本性能指标"""
    version: str
    usage_count: int
    avg_response_time: float
    avg_user_feedback: float
    error_rate: float
    performance_score: float


class VersionManager:
    """Prompt版本管理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_version_tag(self, prompt_id: int, tag_name: str, 
                          description: str = "", created_by: Optional[int] = None) -> bool:
        """
        为当前版本创建标签
        
        Args:
            prompt_id: Prompt ID
            tag_name: 标签名称（如 v1.0, stable, beta）
            description: 标签描述
            created_by: 创建者ID
            
        Returns:
            是否创建成功
        """
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            return False
        
        # 检查标签是否已存在
        existing_version = self.db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.meta_data.contains(f'"tag": "{tag_name}"')
            )
        ).first()
        
        if existing_version:
            logger.warning(f"Tag '{tag_name}' already exists for prompt {prompt_id}")
            return False
        
        # 创建带标签的版本记录
        metadata = prompt.meta_data.copy() if prompt.meta_data else {}
        metadata.update({
            "tag": tag_name,
            "tag_description": description,
            "tagged_at": datetime.utcnow().isoformat()
        })
        
        version = PromptVersion(
            prompt_id=prompt_id,
            version=prompt.version,
            content=prompt.content,
            variables=prompt.variables,
            meta_data=metadata,
            change_log=f"Tagged as '{tag_name}': {description}",
            created_by=created_by
        )
        
        self.db.add(version)
        self.db.commit()
        
        logger.info(f"Created version tag '{tag_name}' for prompt {prompt_id}")
        return True
    
    def get_tagged_versions(self, prompt_id: int) -> List[PromptVersionResponse]:
        """获取所有带标签的版本"""
        versions = self.db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.meta_data.contains('"tag"')
            )
        ).order_by(desc(PromptVersion.created_at)).all()
        
        return [PromptVersionResponse.model_validate(v) for v in versions]
    
    def compare_versions(self, prompt_id: int, version_a: str, version_b: str) -> VersionComparison:
        """
        比较两个版本的差异
        
        Args:
            prompt_id: Prompt ID
            version_a: 版本A
            version_b: 版本B
            
        Returns:
            版本比较结果
        """
        # 获取两个版本的记录
        version_a_record = self.db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version_a
            )
        ).first()
        
        version_b_record = self.db.query(PromptVersion).filter(
            and_(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version == version_b
            )
        ).first()
        
        if not version_a_record or not version_b_record:
            raise ValueError(f"Version {version_a} or {version_b} not found")
        
        # 计算内容差异
        content_diff = self._calculate_content_diff(
            version_a_record.content, 
            version_b_record.content
        )
        
        # 计算变量差异
        variables_diff = self._calculate_dict_diff(
            version_a_record.variables or {}, 
            version_b_record.variables or {}
        )
        
        # 计算元数据差异
        meta_data_diff = self._calculate_dict_diff(
            version_a_record.meta_data or {},
            version_b_record.meta_data or {}
        )
        
        # 计算相似度分数
        similarity_score = self._calculate_similarity(
            version_a_record.content, 
            version_b_record.content
        )
        
        return VersionComparison(
            version_a=version_a,
            version_b=version_b,
            content_diff=content_diff,
            variables_diff=variables_diff,
            meta_data_diff=meta_data_diff,
            similarity_score=similarity_score
        )
    
    def get_version_metrics(self, prompt_id: int, days: int = 30) -> List[VersionMetrics]:
        """
        获取各版本的性能指标
        
        Args:
            prompt_id: Prompt ID
            days: 统计天数
            
        Returns:
            版本性能指标列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 获取所有版本的使用统计
        version_stats = self.db.query(
            PromptVersion.version,
            func.count(PromptUsageStats.id).label("usage_count"),
            func.avg(PromptUsageStats.response_time_ms).label("avg_response_time"),
            func.avg(PromptUsageStats.user_feedback).label("avg_feedback"),
            func.sum(func.case([(PromptUsageStats.error_occurred == True, 1)], else_=0)).label("error_count")
        ).outerjoin(
            PromptUsageStats,
            and_(
                PromptUsageStats.prompt_id == prompt_id,
                PromptUsageStats.usage_date >= start_date
            )
        ).filter(
            PromptVersion.prompt_id == prompt_id
        ).group_by(PromptVersion.version).all()
        
        metrics = []
        for stat in version_stats:
            usage_count = stat.usage_count or 0
            error_rate = (stat.error_count or 0) / usage_count if usage_count > 0 else 0
            
            # 计算综合性能分数 (0-100)
            performance_score = self._calculate_performance_score(
                avg_response_time=stat.avg_response_time or 0,
                avg_feedback=stat.avg_feedback or 0,
                error_rate=error_rate,
                usage_count=usage_count
            )
            
            metrics.append(VersionMetrics(
                version=stat.version,
                usage_count=usage_count,
                avg_response_time=stat.avg_response_time or 0,
                avg_user_feedback=stat.avg_feedback or 0,
                error_rate=error_rate,
                performance_score=performance_score
            ))
        
        # 按性能分数排序
        return sorted(metrics, key=lambda x: x.performance_score, reverse=True)
    
    def suggest_best_version(self, prompt_id: int, days: int = 30) -> Optional[str]:
        """
        基于性能指标推荐最佳版本
        
        Args:
            prompt_id: Prompt ID
            days: 统计天数
            
        Returns:
            推荐的版本号，如果没有足够数据则返回None
        """
        metrics = self.get_version_metrics(prompt_id, days)
        
        if not metrics:
            return None
        
        # 过滤掉使用次数太少的版本（至少需要5次使用）
        qualified_metrics = [m for m in metrics if m.usage_count >= 5]
        
        if not qualified_metrics:
            # 如果没有足够使用的版本，返回使用次数最多的
            return max(metrics, key=lambda x: x.usage_count).version
        
        # 返回性能分数最高的版本
        return qualified_metrics[0].version
    
    def auto_cleanup_old_versions(self, prompt_id: int, keep_count: int = 10) -> int:
        """
        自动清理旧版本（保留最近的N个版本和所有带标签的版本）
        
        Args:
            prompt_id: Prompt ID
            keep_count: 保留的版本数量
            
        Returns:
            清理的版本数量
        """
        # 获取所有版本，按创建时间排序
        all_versions = self.db.query(PromptVersion).filter(
            PromptVersion.prompt_id == prompt_id
        ).order_by(desc(PromptVersion.created_at)).all()
        
        if len(all_versions) <= keep_count:
            return 0
        
        # 保留最近的版本和带标签的版本
        versions_to_keep = set()
        
        # 保留最近的N个版本
        for version in all_versions[:keep_count]:
            versions_to_keep.add(version.id)
        
        # 保留所有带标签的版本
        for version in all_versions:
            if version.meta_data and "tag" in version.meta_data:
                versions_to_keep.add(version.id)
        
        # 删除其他版本
        versions_to_delete = [v for v in all_versions if v.id not in versions_to_keep]
        
        deleted_count = 0
        for version in versions_to_delete:
            self.db.delete(version)
            deleted_count += 1
        
        if deleted_count > 0:
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old versions for prompt {prompt_id}")
        
        return deleted_count
    
    def export_version_history(self, prompt_id: int) -> Dict[str, Any]:
        """
        导出版本历史为JSON格式
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            版本历史数据
        """
        prompt = self.db.query(SystemPrompt).filter(SystemPrompt.id == prompt_id).first()
        if not prompt:
            raise ValueError(f"Prompt {prompt_id} not found")
        
        versions = self.db.query(PromptVersion).filter(
            PromptVersion.prompt_id == prompt_id
        ).order_by(PromptVersion.created_at).all()
        
        export_data = {
            "prompt_info": {
                "id": prompt.id,
                "name": prompt.name,
                "agent_id": prompt.agent_id,
                "language": prompt.language,
                "current_version": prompt.version,
                "exported_at": datetime.utcnow().isoformat()
            },
            "versions": [
                {
                    "version": v.version,
                    "content": v.content,
                    "variables": v.variables,
                    "metadata": v.meta_data,
                    "change_log": v.change_log,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                    "created_by": v.created_by
                }
                for v in versions
            ]
        }
        
        return export_data
    
    # ==================== 私有方法 ====================
    
    def _calculate_content_diff(self, content_a: str, content_b: str) -> str:
        """计算内容差异（简化版本）"""
        if content_a == content_b:
            return "No differences"
        
        # 简单的行级差异检测
        lines_a = content_a.split('\n')
        lines_b = content_b.split('\n')
        
        diff_lines = []
        max_lines = max(len(lines_a), len(lines_b))
        
        for i in range(max_lines):
            line_a = lines_a[i] if i < len(lines_a) else ""
            line_b = lines_b[i] if i < len(lines_b) else ""
            
            if line_a != line_b:
                diff_lines.append(f"Line {i+1}:")
                if line_a:
                    diff_lines.append(f"  - {line_a}")
                if line_b:
                    diff_lines.append(f"  + {line_b}")
        
        return '\n'.join(diff_lines) if diff_lines else "No differences"
    
    def _calculate_dict_diff(self, dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> Dict[str, Any]:
        """计算字典差异"""
        diff = {
            "added": {},
            "removed": {},
            "modified": {}
        }
        
        all_keys = set(dict_a.keys()) | set(dict_b.keys())
        
        for key in all_keys:
            if key not in dict_a:
                diff["added"][key] = dict_b[key]
            elif key not in dict_b:
                diff["removed"][key] = dict_a[key]
            elif dict_a[key] != dict_b[key]:
                diff["modified"][key] = {
                    "old": dict_a[key],
                    "new": dict_b[key]
                }
        
        return diff
    
    def _calculate_similarity(self, content_a: str, content_b: str) -> float:
        """计算内容相似度（0-1）"""
        if content_a == content_b:
            return 1.0
        
        # 使用简单的字符级相似度
        len_a, len_b = len(content_a), len(content_b)
        if len_a == 0 and len_b == 0:
            return 1.0
        if len_a == 0 or len_b == 0:
            return 0.0
        
        # 计算最长公共子序列长度
        lcs_length = self._lcs_length(content_a, content_b)
        similarity = (2.0 * lcs_length) / (len_a + len_b)
        
        return similarity
    
    def _lcs_length(self, s1: str, s2: str) -> int:
        """计算最长公共子序列长度"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]
    
    def _calculate_performance_score(self, avg_response_time: float, avg_feedback: float, 
                                   error_rate: float, usage_count: int) -> float:
        """
        计算综合性能分数 (0-100)
        
        考虑因素：
        - 响应时间（越低越好）
        - 用户反馈（越高越好）
        - 错误率（越低越好）
        - 使用次数（作为权重）
        """
        # 响应时间分数 (0-30分)
        # 假设理想响应时间是100ms，超过1000ms得0分
        time_score = max(0, 30 - (avg_response_time - 100) / 900 * 30)
        time_score = min(30, max(0, time_score))
        
        # 用户反馈分数 (0-40分)
        # 假设反馈分数是1-5分，转换为0-40分
        feedback_score = (avg_feedback - 1) / 4 * 40 if avg_feedback > 0 else 0
        feedback_score = min(40, max(0, feedback_score))
        
        # 错误率分数 (0-30分)
        # 错误率越低分数越高
        error_score = max(0, 30 - error_rate * 30)
        error_score = min(30, max(0, error_score))
        
        # 基础分数
        base_score = time_score + feedback_score + error_score
        
        # 使用次数权重（使用次数越多，分数越可信）
        usage_weight = min(1.0, usage_count / 100)  # 100次使用达到满权重
        
        # 最终分数
        final_score = base_score * usage_weight
        
        return round(final_score, 2)