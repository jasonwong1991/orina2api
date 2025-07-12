"""
API Key验证中间件
"""
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

class APIKeyMiddleware(BaseHTTPMiddleware):
    """API Key验证中间件"""
    
    def __init__(self, app, api_keys: List[str], require_api_key: bool = True):
        super().__init__(app)
        self.api_keys = set(api_keys)
        self.require_api_key = require_api_key
        # 不需要验证的路径
        self.exempt_paths = {
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc"
        }
    
    async def dispatch(self, request: Request, call_next):
        # 如果不需要API key验证，直接通过
        if not self.require_api_key:
            return await call_next(request)
        
        # 检查是否是豁免路径
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # 检查API key
        api_key = self._extract_api_key(request)
        
        if not api_key:
            logger.warning(f"Missing API key for request: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "message": "Missing API key. Please provide an API key in the Authorization header or api_key parameter.",
                        "type": "authentication_error",
                        "code": "missing_api_key"
                    }
                }
            )
        
        if not self._validate_api_key(api_key):
            logger.warning(f"Invalid API key for request: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": {
                        "message": "Invalid API key provided.",
                        "type": "authentication_error", 
                        "code": "invalid_api_key"
                    }
                }
            )
        
        logger.debug(f"API key validated successfully for request: {request.url.path}")
        return await call_next(request)
    
    def _extract_api_key(self, request: Request) -> str:
        """从请求中提取API key"""
        # 1. 从Authorization header中提取 (Bearer token格式)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # 移除 "Bearer " 前缀
        
        # 2. 从query参数中提取
        api_key = request.query_params.get("api_key")
        if api_key:
            return api_key
        
        # 3. 从header中直接提取
        api_key = request.headers.get("X-API-Key") or request.headers.get("api-key")
        if api_key:
            return api_key
        
        return ""
    
    def _validate_api_key(self, api_key: str) -> bool:
        """验证API key是否有效"""
        if not self.api_keys:
            # 如果没有配置API key，则允许任何非空key
            return bool(api_key)
        
        return api_key in self.api_keys
    
    def update_api_keys(self, api_keys: List[str]):
        """更新API key列表"""
        self.api_keys = set(api_keys)
        logger.info(f"Updated API keys, total count: {len(self.api_keys)}")