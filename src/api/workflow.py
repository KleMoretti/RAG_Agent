"""工艺流程管理 API 路由"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.db import get_db
from src.api.models import ProcessWorkflow, User
from src.api.auth import get_current_user, require_manager_or_admin

router = APIRouter(prefix="/api/workflow", tags=["workflow"])


# Pydantic 模型
class ProcessNode(BaseModel):
    """流程节点"""
    id: str
    name: str
    type: str
    description: str
    position: dict
    status: str | None = None
    parameters: List[dict] | None = None
    relatedDocs: List[str] | None = None


class ProcessEdge(BaseModel):
    """流程连线"""
    id: str
    source: str
    target: str


class WorkflowCreate(BaseModel):
    """创建工艺流程请求"""
    name: str
    description: str | None = None
    template_id: str | None = None
    nodes: List[ProcessNode]
    edges: List[ProcessEdge]
    workflow_metadata: dict | None = None


class WorkflowUpdate(BaseModel):
    """更新工艺流程请求"""
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    nodes: List[ProcessNode] | None = None
    edges: List[ProcessEdge] | None = None
    workflow_metadata: dict | None = None


class WorkflowResponse(BaseModel):
    """工艺流程响应"""
    id: int
    name: str
    description: str | None
    template_id: str | None
    is_custom: bool
    is_active: bool
    nodes: List[ProcessNode]
    edges: List[ProcessEdge]
    workflow_metadata: dict | None
    created_at: str
    updated_at: str
    created_by: int | None

    class Config:
        from_attributes = True


# API 端点
@router.post("/workflows", response_model=WorkflowResponse)
def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """创建自定义工艺流程（需要管理员或经理权限）"""
    # 将 Pydantic 模型转换为字典
    nodes_dict = [node.model_dump() for node in workflow.nodes]
    edges_dict = [edge.model_dump() for edge in workflow.edges]

    # 创建数据库记录
    db_workflow = ProcessWorkflow(
        name=workflow.name,
        description=workflow.description,
        template_id=workflow.template_id,
        is_custom=True,
        nodes={"nodes": nodes_dict},
        edges={"edges": edges_dict},
        workflow_metadata=workflow.workflow_metadata,
        created_by=current_user.id,
    )

    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)

    # 转换为响应格式
    return WorkflowResponse(
        id=db_workflow.id,
        name=db_workflow.name,
        description=db_workflow.description,
        template_id=db_workflow.template_id,
        is_custom=db_workflow.is_custom,
        is_active=db_workflow.is_active,
        nodes=[ProcessNode(**node) for node in db_workflow.nodes.get("nodes", [])],
        edges=[ProcessEdge(**edge) for edge in db_workflow.edges.get("edges", [])],
        workflow_metadata=db_workflow.workflow_metadata,
        created_at=db_workflow.created_at.isoformat(),
        updated_at=db_workflow.updated_at.isoformat(),
        created_by=db_workflow.created_by,
    )


@router.get("/workflows", response_model=List[WorkflowResponse])
def list_workflows(
    is_active: bool | None = None,
    is_custom: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取工艺流程列表"""
    query = db.query(ProcessWorkflow)

    if is_active is not None:
        query = query.filter(ProcessWorkflow.is_active == is_active)
    if is_custom is not None:
        query = query.filter(ProcessWorkflow.is_custom == is_custom)

    workflows = query.order_by(ProcessWorkflow.updated_at.desc()).all()

    # 转换为响应格式
    return [
        WorkflowResponse(
            id=wf.id,
            name=wf.name,
            description=wf.description,
            template_id=wf.template_id,
            is_custom=wf.is_custom,
            is_active=wf.is_active,
            nodes=[ProcessNode(**node) for node in wf.nodes.get("nodes", [])],
            edges=[ProcessEdge(**edge) for edge in wf.edges.get("edges", [])],
            workflow_metadata=wf.workflow_metadata,
            created_at=wf.created_at.isoformat(),
            updated_at=wf.updated_at.isoformat(),
            created_by=wf.created_by,
        )
        for wf in workflows
    ]


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个工艺流程详情"""
    workflow = db.query(ProcessWorkflow).filter(ProcessWorkflow.id == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="工艺流程不存在")

    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        template_id=workflow.template_id,
        is_custom=workflow.is_custom,
        is_active=workflow.is_active,
        nodes=[ProcessNode(**node) for node in workflow.nodes.get("nodes", [])],
        edges=[ProcessEdge(**edge) for edge in workflow.edges.get("edges", [])],
        workflow_metadata=workflow.workflow_metadata,
        created_at=workflow.created_at.isoformat(),
        updated_at=workflow.updated_at.isoformat(),
        created_by=workflow.created_by,
    )


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """更新工艺流程（需要管理员或经理权限）"""
    db_workflow = db.query(ProcessWorkflow).filter(ProcessWorkflow.id == workflow_id).first()

    if not db_workflow:
        raise HTTPException(status_code=404, detail="工艺流程不存在")

    # 更新字段
    if workflow_update.name is not None:
        db_workflow.name = workflow_update.name
    if workflow_update.description is not None:
        db_workflow.description = workflow_update.description
    if workflow_update.is_active is not None:
        db_workflow.is_active = workflow_update.is_active
    if workflow_update.nodes is not None:
        nodes_dict = [node.model_dump() for node in workflow_update.nodes]
        db_workflow.nodes = {"nodes": nodes_dict}
    if workflow_update.edges is not None:
        edges_dict = [edge.model_dump() for edge in workflow_update.edges]
        db_workflow.edges = {"edges": edges_dict}
    if workflow_update.workflow_metadata is not None:
        db_workflow.workflow_metadata = workflow_update.workflow_metadata

    db.commit()
    db.refresh(db_workflow)

    return WorkflowResponse(
        id=db_workflow.id,
        name=db_workflow.name,
        description=db_workflow.description,
        template_id=db_workflow.template_id,
        is_custom=db_workflow.is_custom,
        is_active=db_workflow.is_active,
        nodes=[ProcessNode(**node) for node in db_workflow.nodes.get("nodes", [])],
        edges=[ProcessEdge(**edge) for edge in db_workflow.edges.get("edges", [])],
        workflow_metadata=db_workflow.workflow_metadata,
        created_at=db_workflow.created_at.isoformat(),
        updated_at=db_workflow.updated_at.isoformat(),
        created_by=db_workflow.created_by,
    )


@router.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    """删除工艺流程（需要管理员或经理权限）"""
    db_workflow = db.query(ProcessWorkflow).filter(ProcessWorkflow.id == workflow_id).first()

    if not db_workflow:
        raise HTTPException(status_code=404, detail="工艺流程不存在")

    db.delete(db_workflow)
    db.commit()

    return {"message": "工艺流程已删除", "id": workflow_id}


