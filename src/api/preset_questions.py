"""
Agent预设问题管理API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.api.db import get_db
from src.api.models import AgentPresetQuestion, Agent
from src.api.auth import get_current_user, require_admin
from pydantic import BaseModel, Field


# Pydantic模型
class PresetQuestionBase(BaseModel):
    title: str = Field(..., max_length=128, description="问题标题")
    question: str = Field(..., description="问题内容")
    category: Optional[str] = Field(None, max_length=64, description="问题分类")
    order_index: int = Field(0, description="显示顺序")
    is_active: bool = Field(True, description="是否激活")
    tags: Optional[List[str]] = Field(None, description="标签")
    difficulty_level: Optional[str] = Field(None, description="难度级别")
    expected_response_type: Optional[str] = Field(None, description="期望响应类型")


class PresetQuestionCreate(PresetQuestionBase):
    agent_id: int = Field(..., description="Agent ID")


class PresetQuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=128, description="问题标题")
    question: Optional[str] = Field(None, description="问题内容")
    category: Optional[str] = Field(None, max_length=64, description="问题分类")
    order_index: Optional[int] = Field(None, description="显示顺序")
    is_active: Optional[bool] = Field(None, description="是否激活")
    tags: Optional[List[str]] = Field(None, description="标签")
    difficulty_level: Optional[str] = Field(None, description="难度级别")
    expected_response_type: Optional[str] = Field(None, description="期望响应类型")


class PresetQuestionResponse(PresetQuestionBase):
    id: int
    agent_id: int
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentPresetQuestionsResponse(BaseModel):
    agent_id: int
    agent_name: str
    questions: List[PresetQuestionResponse]


# 路由器
router = APIRouter(prefix="/api/preset-questions", tags=["预设问题"])


@router.get("/agent/{agent_id}", response_model=List[PresetQuestionResponse])
async def get_agent_preset_questions(
    agent_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """获取指定Agent的预设问题"""
    
    # 验证Agent是否存在
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found"
        )
    
    # 构建查询条件
    query = db.query(AgentPresetQuestion).filter(AgentPresetQuestion.agent_id == agent_id)
    
    if active_only:
        query = query.filter(AgentPresetQuestion.is_active == True)
    
    # 按顺序排序
    questions = query.order_by(AgentPresetQuestion.order_index, AgentPresetQuestion.id).all()
    
    return questions


@router.get("/agent/{agent_name}/by-name", response_model=List[PresetQuestionResponse])
async def get_agent_preset_questions_by_name(
    agent_name: str,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """通过Agent名称获取预设问题"""
    
    # 查找Agent
    agent = db.query(Agent).filter(Agent.name == agent_name).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with name '{agent_name}' not found"
        )
    
    return await get_agent_preset_questions(agent.id, active_only, db)


@router.get("/all", response_model=List[AgentPresetQuestionsResponse])
async def get_all_preset_questions(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """获取所有Agent的预设问题"""
    
    # 获取所有激活的Agent
    agents = db.query(Agent).filter(Agent.is_active == True).all()
    
    result = []
    for agent in agents:
        # 构建查询条件
        query = db.query(AgentPresetQuestion).filter(AgentPresetQuestion.agent_id == agent.id)
        
        if active_only:
            query = query.filter(AgentPresetQuestion.is_active == True)
        
        questions = query.order_by(AgentPresetQuestion.order_index, AgentPresetQuestion.id).all()
        
        result.append(AgentPresetQuestionsResponse(
            agent_id=agent.id,
            agent_name=agent.name,
            questions=questions
        ))
    
    return result


@router.post("/", response_model=PresetQuestionResponse)
async def create_preset_question(
    question_data: PresetQuestionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """创建新的预设问题（需要管理员权限）"""
    
    # 验证Agent是否存在
    agent = db.query(Agent).filter(Agent.id == question_data.agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {question_data.agent_id} not found"
        )
    
    # 创建预设问题
    db_question = AgentPresetQuestion(
        agent_id=question_data.agent_id,
        title=question_data.title,
        question=question_data.question,
        category=question_data.category,
        order_index=question_data.order_index,
        is_active=question_data.is_active,
        tags=question_data.tags,
        difficulty_level=question_data.difficulty_level,
        expected_response_type=question_data.expected_response_type,
        created_by=current_user.id
    )
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    
    return db_question


@router.put("/{question_id}", response_model=PresetQuestionResponse)
async def update_preset_question(
    question_id: int,
    question_data: PresetQuestionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """更新预设问题（需要管理员权限）"""
    
    # 查找问题
    db_question = db.query(AgentPresetQuestion).filter(AgentPresetQuestion.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset question with id {question_id} not found"
        )
    
    # 更新字段
    update_data = question_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    db.commit()
    db.refresh(db_question)
    
    return db_question


@router.delete("/{question_id}")
async def delete_preset_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """删除预设问题（需要管理员权限）"""
    
    # 查找问题
    db_question = db.query(AgentPresetQuestion).filter(AgentPresetQuestion.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset question with id {question_id} not found"
        )
    
    db.delete(db_question)
    db.commit()
    
    return {"message": "Preset question deleted successfully"}


@router.post("/{question_id}/increment-usage")
async def increment_question_usage(
    question_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """增加问题使用次数"""
    
    # 查找问题
    db_question = db.query(AgentPresetQuestion).filter(AgentPresetQuestion.id == question_id).first()
    if not db_question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset question with id {question_id} not found"
        )
    
    # 增加使用次数
    db_question.usage_count += 1
    db.commit()
    
    return {"message": "Usage count incremented", "usage_count": db_question.usage_count}


@router.get("/categories", response_model=List[str])
async def get_question_categories(db: Session = Depends(get_db)):
    """获取所有问题分类"""
    
    categories = db.query(AgentPresetQuestion.category).distinct().filter(
        AgentPresetQuestion.category.isnot(None)
    ).all()
    
    return [cat[0] for cat in categories if cat[0]]


@router.get("/stats/usage")
async def get_usage_stats(
    agent_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin)
):
    """获取预设问题使用统计（需要管理员权限）"""
    
    query = db.query(AgentPresetQuestion)
    
    if agent_id:
        query = query.filter(AgentPresetQuestion.agent_id == agent_id)
    
    questions = query.order_by(desc(AgentPresetQuestion.usage_count)).all()
    
    stats = {
        "total_questions": len(questions),
        "total_usage": sum(q.usage_count for q in questions),
        "most_used": [
            {
                "id": q.id,
                "title": q.title,
                "usage_count": q.usage_count,
                "agent_id": q.agent_id
            }
            for q in questions[:10]  # 前10个最常用的问题
        ]
    }
    
    return stats