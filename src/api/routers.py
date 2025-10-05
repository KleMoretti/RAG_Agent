from fastapi import APIRouter
from .auth import router as auth_router
from .admin import router as admin_router
from ..knowledge_graph.api import router as knowledge_graph_router
from ..prompt_management.router import router as prompt_router

api_router = APIRouter()

# 注册路由
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(knowledge_graph_router)
api_router.include_router(prompt_router)