from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union, Literal, AsyncGenerator
from datetime import datetime
import uuid
import json
import logging

logger = logging.getLogger(__name__)

# OpenAI API 兼容模型

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: Literal["system", "user", "assistant"] = Field(..., description="消息角色")
    content: str = Field(..., description="消息内容")

class ChatCompletionRequest(BaseModel):
    """OpenAI兼容的聊天完成请求"""
    model: str = Field(..., description="模型名称")
    messages: List[ChatMessage] = Field(..., description="消息列表")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="最大token数")
    stream: Optional[bool] = Field(False, description="是否流式输出")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Top-p采样")
    frequency_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0, description="存在惩罚")
    stop: Optional[Union[str, List[str]]] = Field(None, description="停止序列")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "claude-4-default",
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": False
            }
        }

class ChatCompletionChoice(BaseModel):
    """聊天完成选择"""
    index: int = Field(..., description="选择索引")
    message: ChatMessage = Field(..., description="响应消息")
    finish_reason: Optional[str] = Field(None, description="完成原因")

class ChatCompletionDelta(BaseModel):
    """流式响应增量"""
    role: Optional[str] = Field(None, description="消息角色")
    content: Optional[str] = Field(None, description="增量内容")

class ChatCompletionStreamChoice(BaseModel):
    """流式聊天完成选择"""
    index: int = Field(..., description="选择索引")
    delta: ChatCompletionDelta = Field(..., description="增量数据")
    finish_reason: Optional[str] = Field(None, description="完成原因")

class ChatCompletionUsage(BaseModel):
    """使用情况统计"""
    prompt_tokens: int = Field(..., description="提示token数")
    completion_tokens: int = Field(..., description="完成token数")
    total_tokens: int = Field(..., description="总token数")

class ChatCompletionResponse(BaseModel):
    """OpenAI兼容的聊天完成响应"""
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}", description="请求ID")
    object: str = Field(default="chat.completion", description="对象类型")
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[ChatCompletionChoice] = Field(..., description="响应选择列表")
    usage: Optional[ChatCompletionUsage] = Field(None, description="使用情况")

class ChatCompletionStreamResponse(BaseModel):
    """OpenAI兼容的流式聊天完成响应"""
    id: str = Field(..., description="请求ID")
    object: str = Field(default="chat.completion.chunk", description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[ChatCompletionStreamChoice] = Field(..., description="流式响应选择列表")
    usage: Optional[ChatCompletionUsage] = Field(None, description="使用情况（仅在最后一个chunk中）")

class ModelInfo(BaseModel):
    """模型信息"""
    id: str = Field(..., description="模型ID")
    object: str = Field(default="model", description="对象类型")
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()), description="创建时间戳")
    owned_by: str = Field(default="proxy", description="拥有者")

class ModelsResponse(BaseModel):
    """模型列表响应"""
    object: str = Field(default="list", description="对象类型")
    data: List[ModelInfo] = Field(..., description="模型列表")

class ErrorResponse(BaseModel):
    """错误响应"""
    error: Dict[str, Any] = Field(..., description="错误信息")
    
    @classmethod
    def create(cls, message: str, type: str = "invalid_request_error", code: Optional[str] = None):
        """创建错误响应"""
        error_data = {
            "message": message,
            "type": type
        }
        if code:
            error_data["code"] = code
        return cls(error=error_data)

# 内部使用的模型

class InternalChatRequest(BaseModel):
    """内部聊天请求模型（转换为目标API格式）"""
    conversationId: str = Field(..., description="对话ID")
    mode: str = Field(..., description="模型模式")
    message: Optional[str] = Field(None, description="用户消息")
    messages: Optional[List[Dict[str, Any]]] = Field(None, description="消息历史")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大token数")
    stream: Optional[bool] = Field(False, description="是否流式输出")

# 工具函数

def generate_conversation_id() -> str:
    """生成64位UUID作为对话ID"""
    return str(uuid.uuid4())

def openai_to_internal_model_name(openai_model: str) -> str:
    """将OpenAI模型名转换为内部模型名 - 直接返回传入的模型名"""
    return openai_model

def messages_to_single_message(messages: List[ChatMessage]) -> str:
    """将消息列表转换为单个消息字符串"""
    if not messages:
        return ""
    
    # 如果只有一条用户消息，直接返回
    if len(messages) == 1 and messages[0].role == "user":
        return messages[0].content
    
    # 否则将所有消息合并
    combined_message = ""
    for msg in messages:
        if msg.role == "system":
            combined_message += f"System: {msg.content}\n"
        elif msg.role == "user":
            combined_message += f"User: {msg.content}\n"
        elif msg.role == "assistant":
            combined_message += f"Assistant: {msg.content}\n"
    
    return combined_message.strip()

def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """解析SSE格式的行"""
    logger.debug(f"Parsing SSE line: {repr(line)}")
    
    if not line.strip():
        logger.debug("Empty line after strip")
        return None
    
    # 处理SSE格式: "message\t{json_data}\t"
    if line.startswith("message\t"):
        try:
            # 移除前缀和后缀
            json_part = line[8:].rstrip('\t')
            logger.debug(f"Extracted JSON part: {json_part}")
            
            # 检查是否是结束标记
            if json_part == "[DONE]":
                logger.debug("Found [DONE] marker")
                return {"type": "done"}
            
            # 解析JSON
            data = json.loads(json_part)
            logger.debug(f"Successfully parsed JSON: {data}")
            return {"type": "data", "data": data}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SSE JSON: {e}, line: {line}")
            return None
    
    # 处理标准SSE格式: "data: {json_data}"
    elif line.startswith("data: "):
        try:
            json_part = line[6:]  # 移除 "data: " 前缀
            logger.debug(f"Standard SSE format, JSON part: {json_part}")
            
            # 检查是否是结束标记
            if json_part.strip() == "[DONE]":
                logger.debug("Found [DONE] marker in standard format")
                return {"type": "done"}
            
            # 解析JSON
            data = json.loads(json_part)
            logger.debug(f"Successfully parsed standard SSE JSON: {data}")
            return {"type": "data", "data": data}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse standard SSE JSON: {e}, line: {line}")
            return None
    
    # 处理其他可能的格式
    else:
        logger.debug(f"Unknown SSE line format: {line}")
        return None

async def convert_stream_to_openai_format(
    stream_response, 
    request_id: str, 
    model: str, 
    created_time: int
) -> AsyncGenerator[str, None]:
    """将目标API的流式响应转换为OpenAI格式"""
    try:
        logger.info("Starting stream conversion to OpenAI format")
        line_count = 0
        async for line in stream_response.aiter_lines():
            line_count += 1
            logger.debug(f"Processing line {line_count}: {line}")
            
            if not line:
                logger.debug("Empty line, skipping")
                continue
                
            parsed = parse_sse_line(line)
            if not parsed:
                logger.debug(f"Failed to parse SSE line: {line}")
                continue
                
            logger.debug(f"Parsed SSE data: {parsed}")
                
            if parsed["type"] == "done":
                logger.info("Received DONE signal, ending stream")
                # 发送结束标记
                yield "data: [DONE]\n\n"
                break
                
            elif parsed["type"] == "data":
                data = parsed["data"]
                logger.debug(f"Processing data chunk: {data}")
                
                # 提取内容和完成原因
                choices = data.get("choices", [])
                if not choices:
                    logger.debug("No choices in data, skipping")
                    continue
                    
                choice = choices[0]
                delta = choice.get("delta", {})
                content = delta.get("content", "")
                finish_reason = choice.get("finish_reason")
                
                logger.debug(f"Extracted content: '{content}', finish_reason: {finish_reason}")
                
                # 构建OpenAI格式的流式响应
                openai_chunk = ChatCompletionStreamResponse(
                    id=request_id,
                    created=created_time,
                    model=model,
                    choices=[
                        ChatCompletionStreamChoice(
                            index=0,
                            delta=ChatCompletionDelta(
                                role=delta.get("role"),
                                content=content
                            ),
                            finish_reason=finish_reason
                        )
                    ]
                )
                
                # 如果有usage信息，添加到最后一个chunk
                if "usage" in data:
                    usage_data = data["usage"]
                    openai_chunk.usage = ChatCompletionUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0)
                    )
                    logger.debug(f"Added usage data: {usage_data}")
                
                # 输出SSE格式
                chunk_json = openai_chunk.model_dump_json(exclude_none=True)
                output_line = f"data: {chunk_json}\n\n"
                logger.debug(f"Yielding chunk: {output_line[:100]}...")
                yield output_line
        
        logger.info(f"Stream conversion completed, processed {line_count} lines")
                
    except Exception as e:
        logger.error(f"Error converting stream: {e}", exc_info=True)
        # 发送错误并结束
        error_chunk = ChatCompletionStreamResponse(
            id=request_id,
            created=created_time,
            model=model,
            choices=[
                ChatCompletionStreamChoice(
                    index=0,
                    delta=ChatCompletionDelta(
                        role="assistant",
                        content=f"Error: {str(e)}"
                    ),
                    finish_reason="error"
                )
            ]
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"