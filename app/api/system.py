"""
健康检查和系统信息API路由
"""

import logging
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.services.proxy import proxy_service
from app.services.token_manager import token_manager
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["System"])

@router.get("/")
async def root():
    """根路径信息"""
    return {
        "message": "OpenAI-compatible LLM Proxy API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查token池状态
        token_status = token_manager.get_pool_status()
        
        # 计算成功率
        total_requests = proxy_service.stats["total_requests"]
        success_rate = (
            proxy_service.stats["successful_requests"] / total_requests * 100
            if total_requests > 0 else 100
        )
        
        # 计算运行时间
        uptime = datetime.now() - proxy_service.stats["start_time"]
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "api_key_validation": "enabled" if settings.require_api_key else "disabled",
            "statistics": {
                "total_requests": total_requests,
                "successful_requests": proxy_service.stats["successful_requests"],
                "failed_requests": proxy_service.stats["failed_requests"],
                "success_rate": f"{success_rate:.2f}%"
            },
            "token_pool": token_status,
            "models": settings.available_models
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )
@router.delete("/admin/conversations")
async def delete_all_conversations():
    """管理端点：删除所有项目下的conversations"""
    try:
        # 获取一个可用token
        token = await token_manager.get_token()
        if not token:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "message": "No available tokens in the pool",
                    "timestamp": datetime.now().isoformat()
                }
            )
        
        # 使用proxy_service的异步上下文管理器
        async with proxy_service:
            # 获取所有projects
            projects = await proxy_service.get_projects(token)
            if not projects:
                return {
                    "status": "success",
                    "message": "No projects found",
                    "deleted_conversations": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            total_deleted = 0
            project_results = []
            
            # 遍历每个project，删除其下的所有conversations
            for project in projects:
                project_id = project.get("id")
                project_name = project.get("name", "Unknown")
                
                if project_id:
                    # 删除该项目下的所有conversations
                    success = await proxy_service.delete_all_conversations(token, project_id)
                    
                    # 获取删除前的conversations数量（用于统计）
                    conversations = await proxy_service.get_conversations(token, project_id)
                    deleted_count = len(conversations) if conversations else 0
                    
                    if success:
                        total_deleted += deleted_count
                        project_results.append({
                            "project_id": project_id,
                            "project_name": project_name,
                            "status": "success",
                            "deleted_conversations": deleted_count
                        })
                    else:
                        project_results.append({
                            "project_id": project_id,
                            "project_name": project_name,
                            "status": "partial_failure",
                            "deleted_conversations": 0
                        })
            
            return {
                "status": "success",
                "message": f"Deleted conversations from {len(projects)} projects",
                "total_deleted_conversations": total_deleted,
                "project_results": project_results,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Failed to delete all conversations: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to delete conversations: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )