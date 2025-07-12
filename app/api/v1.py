"""
OpenAI兼容的API路由
"""

import logging
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Union

from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse, 
    ModelsResponse, ModelInfo, ErrorResponse
)
from app.services.proxy import proxy_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["OpenAI Compatible API"])

@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """
    列出可用模型
    
    兼容OpenAI API的模型列表接口
    """
    try:
        models = []
        for model_id in settings.available_models:
            model_info = ModelInfo(
                id=model_id,
                owned_by="proxy"
            )
            models.append(model_info)
        
        return ModelsResponse(data=models)
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse.create("Failed to list models").dict()
        )

@router.post("/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest):
    """
    创建聊天完成
    
    兼容OpenAI API的聊天完成接口，支持流式和非流式响应
    """
    try:
        logger.info(f"Received chat completion request for model: {request.model}, stream: {request.stream}")
        logger.debug(f"Request details: messages={len(request.messages)}, temperature={request.temperature}")
        
        # 转发请求
        response = await proxy_service.forward_request(request)
        
        if request.stream:
            # 流式响应
            logger.info("Returning streaming response")
            return StreamingResponse(
                response,
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            # 非流式响应
            logger.info("Chat completion request processed successfully")
            return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat completion: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse.create(f"Failed to process request: {str(e)}").dict()
        )