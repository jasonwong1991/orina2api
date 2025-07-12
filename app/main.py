"""
FastAPI应用工厂和配置
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.proxy import proxy_service
from app.middleware.auth import APIKeyMiddleware
from app.api.v1 import router as v1_router
from app.api.system import router as system_router
from app.models.schemas import ErrorResponse

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting OpenAI-compatible LLM Proxy API...")
    
    # 启动时初始化
    async with proxy_service:
        logger.info(f"Proxy service initialized with {len(settings.token_pool_list)} tokens")
        logger.info(f"Available models: {settings.available_models}")
        logger.info(f"API key validation: {'enabled' if settings.require_api_key else 'disabled'}")
        
        yield
        
    logger.info("OpenAI-compatible LLM Proxy API shutdown complete")

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="OpenAI-compatible LLM Proxy",
        description="OpenAI兼容的LLM接口反向代理服务，支持token池和模型配置",
        version="1.0.0",
        lifespan=lifespan
    )

    # 添加API key验证中间件
    app.add_middleware(
        APIKeyMiddleware,
        api_keys=settings.api_keys,
        require_api_key=settings.require_api_key
    )

    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 全局异常处理器
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """全局异常处理器"""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.create("Internal server error", "internal_error").dict()
        )

    # 注册路由
    app.include_router(system_router)
    app.include_router(v1_router)
    
    return app

# 创建应用实例
app = create_app()