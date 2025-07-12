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