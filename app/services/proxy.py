import asyncio
import logging
import httpx
import uuid
from typing import Dict, Any, Optional, Union, AsyncGenerator, List
from datetime import datetime
import json
import random

from app.core.config import settings
from app.services.token_manager import token_manager
from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice, 
    ChatCompletionUsage, ChatMessage, ChatCompletionStreamResponse,
    ChatCompletionStreamChoice, ChatCompletionDelta,
    openai_to_internal_model_name,
    convert_stream_to_openai_format,
    messages_to_single_message
)

logger = logging.getLogger(__name__)

class ProxyService:
    def __init__(self):
        self.client = None
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "start_time": datetime.now()
        }
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.timeout),
            follow_redirects=True
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.client:
            await self.client.aclose()
    
    async def get_projects(self, token: str) -> Optional[List[Dict[str, Any]]]:
        """获取当前token的projects列表"""
        try:
            headers = {
                "accept": "*/*",
                "accept-language": "en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }
            
            cookies = {"token": token}
            
            response = await self.client.get(
                settings.project_api_url,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Get projects response status: {response.status_code}")
            
            if response.status_code == 200:
                projects = response.json()
                logger.info(f"Found {len(projects)} projects")
                return projects
            else:
                logger.error(f"Failed to get projects: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return None
    
    async def create_project(self, token: str) -> Optional[str]:
        """创建新的project，返回project ID"""
        try:
            headers = {
                "accept": "*/*",
                "accept-language": "en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }
            
            # 使用UUID v4作为项目名称
            project_name = str(uuid.uuid4())
            payload = {"name": project_name}
            cookies = {"token": token}
            
            response = await self.client.post(
                settings.project_api_url,
                json=payload,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Create project response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                project_id = response_data.get("id")
                if project_id:
                    logger.info(f"Successfully created project: {project_id}")
                    return project_id
                else:
                    logger.error(f"No project ID in response: {response_data}")
                    return None
            else:
                logger.error(f"Failed to create project: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return None
    
    async def get_conversations(self, token: str, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """获取project的conversations列表"""
        try:
            headers = {
                "accept": "*/*",
                "accept-language": "en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"137\", \"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            }
            
            cookies = {"token": token}
            url = f"{settings.project_api_url}/{project_id}/conversations"
            
            response = await self.client.get(
                url,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Get conversations response status: {response.status_code}")
            
            if response.status_code == 200:
                conversations = response.json()
                logger.info(f"Found {len(conversations)} conversations")
                return conversations
            else:
                logger.error(f"Failed to get conversations: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting conversations: {e}")
            return None
    
    async def create_conversation(self, token: str, project_id: str) -> Optional[str]:
        """创建新的对话，返回conversation ID"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'referrer': f'https://www.orionai.asia/project/{project_id}',
                'referrerPolicy': 'no-referrer-when-downgrade'
            }
            
            payload = {"projectId": project_id}
            cookies = {"token": token}
            
            response = await self.client.post(
                settings.conversation_api_url,
                json=payload,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Create conversation response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                conversation_id = response_data.get("id") or response_data.get("conversationId") or response_data.get("conversation_id")
                if conversation_id:
                    logger.info(f"Successfully created conversation: {conversation_id}")
                    return conversation_id
                else:
                    logger.error(f"No conversation ID in response: {response_data}")
                    return None
            else:
                logger.error(f"Failed to create conversation: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    async def delete_conversation(self, token: str, conversation_id: str) -> bool:
        """删除指定的conversation"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'origin': 'https://www.orionai.asia',
                'referer': f'https://www.orionai.asia/',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
            }
            
            cookies = {"token": token}
            url = f"{settings.conversation_api_url}/{conversation_id}"
            
            response = await self.client.delete(
                url,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Delete conversation response status: {response.status_code}")
            
            if response.status_code in [200, 204]:
                logger.info(f"Successfully deleted conversation: {conversation_id}")
                return True
            else:
                logger.error(f"Failed to delete conversation: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return False
    
    async def delete_all_conversations(self, token: str, project_id: str) -> bool:
        """删除项目下的所有conversation"""
        try:
            # 获取所有conversations
            conversations = await self.get_conversations(token, project_id)
            if not conversations:
                logger.info(f"No conversations found in project {project_id}")
                return True
            
            # 删除每个conversation
            deleted_count = 0
            for conversation in conversations:
                conversation_id = conversation.get("id")
                if conversation_id:
                    success = await self.delete_conversation(token, conversation_id)
                    if success:
                        deleted_count += 1
                    else:
                        logger.warning(f"Failed to delete conversation {conversation_id}")
            
            logger.info(f"Successfully deleted {deleted_count}/{len(conversations)} conversations in project {project_id}")
            return deleted_count == len(conversations)
            
        except Exception as e:
            logger.error(f"Error deleting all conversations: {e}")
            return False
        """创建新的对话，返回conversation ID"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'referrer': f'https://www.orionai.asia/project/{project_id}',
                'referrerPolicy': 'no-referrer-when-downgrade'
            }
            
            payload = {"projectId": project_id}
            cookies = {"token": token}
            
            response = await self.client.post(
                settings.conversation_api_url,
                json=payload,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Create conversation response status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                conversation_id = response_data.get("id") or response_data.get("conversationId") or response_data.get("conversation_id")
                if conversation_id:
                    logger.info(f"Successfully created conversation: {conversation_id}")
                    return conversation_id
                else:
                    logger.error(f"No conversation ID in response: {response_data}")
                    return None
            else:
                logger.error(f"Failed to create conversation: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return None
    
    async def get_project_and_conversation(self, token: str) -> tuple[Optional[str], Optional[str]]:
        """获取或创建project和conversation，返回(project_id, conversation_id)"""
        # 1. 获取projects列表
        projects = await self.get_projects(token)
        
        project_id = None
        if projects and len(projects) > 0:
            # 随机选择一个project
            selected_project = random.choice(projects)
            project_id = selected_project.get("id")
            logger.info(f"Selected existing project: {project_id}")
        else:
            # 创建新project
            project_id = await self.create_project(token)
            if not project_id:
                logger.error("Failed to create project")
                return None, None
        
        # 2. 删除项目下的所有现有conversations
        logger.info(f"Deleting all existing conversations in project {project_id}")
        delete_success = await self.delete_all_conversations(token, project_id)
        if delete_success:
            logger.info("Successfully deleted all existing conversations")
        else:
            logger.warning("Failed to delete some conversations, but continuing...")
        
        # 3. 创建新conversation
        conversation_id = await self.create_conversation(token, project_id)
        if not conversation_id:
            logger.error("Failed to create conversation")
            return project_id, None
        
        logger.info(f"Created new conversation: {conversation_id}")
        return project_id, conversation_id
    async def send_message(self, token: str, conversation_id: str, project_id: str, message_content: str) -> bool:
        """发送消息到conversation，返回是否成功"""
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'origin': 'https://www.orionai.asia',
                'pragma': 'no-cache',
                'priority': 'u=1, i',
                'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'referer': f'https://www.orionai.asia/project/{project_id}/conversation/{conversation_id}',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
            }
            
            payload = {
                "content": message_content,
                "role": "user"
            }
            cookies = {"token": token}
            url = f"{settings.message_api_url}/{conversation_id}/message"
            
            response = await self.client.post(
                url,
                json=payload,
                headers=headers,
                cookies=cookies
            )
            
            logger.info(f"Send message response status: {response.status_code}")
            logger.info(f"Send message response headers: {dict(response.headers)}")
            logger.info(f"Send message response body: {response.text}")
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully sent message to conversation: {conversation_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    
    async def forward_request(self, request: ChatCompletionRequest) -> Union[ChatCompletionResponse, AsyncGenerator[str, None]]:
        """转发OpenAI格式请求到目标API，支持流式和非流式响应"""
        self.stats["total_requests"] += 1
        
        # 生成请求ID
        request_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created_time = int(datetime.now().timestamp())
        
        # 获取模型名称（直接使用传入的模型名）
        model_name = openai_to_internal_model_name(request.model)
        
        # 转换消息为单个字符串
        message_content = messages_to_single_message(request.messages)
        
        token = await token_manager.get_token()
        if not token:
            self.stats["failed_requests"] += 1
            if request.stream:
                return self._create_error_stream(request.model, "No available tokens in the pool", request_id, created_time)
            else:
                return self._create_error_response(request.model, "No available tokens in the pool")
        
        # 获取或创建project和conversation
        project_id, conversation_id = await self.get_project_and_conversation(token)
        if not project_id or not conversation_id:
            self.stats["failed_requests"] += 1
            await token_manager.mark_token_failed(token, "Failed to get project or conversation")
            if request.stream:
                return self._create_error_stream(request.model, "Failed to get project or conversation", request_id, created_time)
            else:
                return self._create_error_response(request.model, "Failed to get project or conversation")
        
        # 第一步：发送消息到conversation
        message_sent = await self.send_message(token, conversation_id, project_id, message_content)
        if not message_sent:
            self.stats["failed_requests"] += 1
            await token_manager.mark_token_failed(token, "Failed to send message")
            if request.stream:
                return self._create_error_stream(request.model, "Failed to send message", request_id, created_time)
            else:
                return self._create_error_response(request.model, "Failed to send message")
        
        # 准备聊天请求（第二步）
        headers = settings.default_headers.copy()
        headers['referer'] = f'https://www.orionai.asia/project/{project_id}/conversation/{conversation_id}'
        cookies = {"token": token}
        
        # 构建请求体 - 只包含conversationId和mode
        payload = {
            "conversationId": conversation_id,
            "mode": model_name
        }
        
        # 执行请求
        for attempt in range(settings.max_retries):
            try:
                logger.info(f"Forwarding {'streaming' if request.stream else 'non-streaming'} request (attempt {attempt + 1}/{settings.max_retries}) to {settings.target_api_url}")
                logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                
                if request.stream:
                    # 流式请求 - 需要在这里直接处理流，不能返回生成器
                    async def stream_generator():
                        async with self.client.stream(
                            "POST",
                            settings.target_api_url,
                            json=payload,
                            headers=headers,
                            cookies=cookies
                        ) as response:
                            logger.info(f"Stream response status: {response.status_code}")
                            logger.info(f"Stream response headers: {dict(response.headers)}")
                            
                            if response.status_code in [200, 201]:
                                await token_manager.mark_token_success(token)
                                self.stats["successful_requests"] += 1
                                
                                logger.info("Starting to process stream response...")
                                # 在上下文内部处理流式响应
                                async for chunk in convert_stream_to_openai_format(
                                    response,
                                    request_id,
                                    request.model,
                                    created_time
                                ):
                                    yield chunk
                                logger.info("Finished processing stream response")
                                return
                            
                            elif response.status_code in [401, 403]:
                                # 认证错误，需要在外层重试
                                raise httpx.HTTPStatusError(
                                    f"Auth error: {response.status_code}",
                                    request=response.request,
                                    response=response
                                )
                            
                            else:
                                error_msg = f"HTTP {response.status_code}: {await response.aread()}"
                                logger.error(error_msg)
                                self.stats["failed_requests"] += 1
                                async for chunk in self._create_error_stream(request.model, error_msg, request_id, created_time):
                                    yield chunk
                                return
                    
                    try:
                        return stream_generator()
                    except httpx.HTTPStatusError as e:
                        if "Auth error" in str(e):
                            # 认证错误，标记token失败并尝试下一个
                            await token_manager.mark_token_failed(token, str(e))
                            token = await token_manager.get_token()
                            if not token:
                                break
                            cookies = {"token": token}
                            # 重新获取project和conversation
                            project_id, conversation_id = await self.get_project_and_conversation(token)
                            if not project_id or not conversation_id:
                                break
                            payload["conversationId"] = conversation_id
                            headers['referer'] = f'https://www.orionai.asia/project/{project_id}/conversation/{conversation_id}'
                            continue
                        else:
                            raise
                
                else:
                    # 非流式请求
                    response = await self.client.post(
                        settings.target_api_url,
                        json=payload,
                        headers=headers,
                        cookies=cookies
                    )
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response headers: {dict(response.headers)}")
                    logger.info(f"Response body: {response.text}")
                    
                    if response.status_code in [200, 201]:
                        await token_manager.mark_token_success(token)
                        self.stats["successful_requests"] += 1
                        
                        try:
                            response_data = response.json()
                            return self._convert_to_openai_response(
                                request.model, 
                                response_data,
                                request_id,
                                created_time
                            )
                        except Exception as e:
                            logger.error(f"Failed to parse response: {e}")
                            return self._create_error_response(
                                request.model,
                                f"Failed to parse response: {str(e)}"
                            )
                    
                    elif response.status_code in [401, 403]:
                        # 认证错误，标记token失败并尝试下一个
                        await token_manager.mark_token_failed(token, f"Auth error: {response.status_code}")
                        token = await token_manager.get_token()
                        if not token:
                            break
                        cookies = {"token": token}
                        # 重新获取project和conversation
                        project_id, conversation_id = await self.get_project_and_conversation(token)
                        if not project_id or not conversation_id:
                            break
                        payload["conversationId"] = conversation_id
                        headers['referer'] = f'https://www.orionai.asia/project/{project_id}/conversation/{conversation_id}'
                        continue
                        
                    elif response.status_code in [429, 502, 503, 504]:
                        # 临时错误，等待后重试
                        if attempt < settings.max_retries - 1:
                            wait_time = settings.retry_delay * (2 ** attempt)
                            logger.warning(f"Temporary error {response.status_code}, retrying in {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                    
                    # 其他错误
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    self.stats["failed_requests"] += 1
                    return self._create_error_response(request.model, error_msg)
                
            except httpx.TimeoutException:
                error_msg = f"Request timeout (attempt {attempt + 1})"
                logger.error(error_msg)
                if attempt < settings.max_retries - 1:
                    await asyncio.sleep(settings.retry_delay)
                    continue
                    
            except httpx.RequestError as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                if attempt < settings.max_retries - 1:
                    await asyncio.sleep(settings.retry_delay)
                    continue
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                break
        
        # 所有重试都失败了
        await token_manager.mark_token_failed(token, "Max retries exceeded")
        self.stats["failed_requests"] += 1
        
        if request.stream:
            return self._create_error_stream(request.model, "Request failed after all retries", request_id, created_time)
        else:
            return self._create_error_response(request.model, "Request failed after all retries")
    
    def _convert_to_openai_response(self, model: str, response_data: Dict[str, Any], request_id: str, created_time: int) -> ChatCompletionResponse:
        """将目标API响应转换为OpenAI格式"""
        try:
            # 尝试从响应中提取内容
            content = "I'm sorry, I couldn't process your request."
            
            # 根据实际API响应格式调整这里的解析逻辑
            if isinstance(response_data, dict):
                # 常见的响应格式
                if "choices" in response_data and response_data["choices"]:
                    choice = response_data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        content = choice["message"]["content"]
                    elif "text" in choice:
                        content = choice["text"]
                elif "response" in response_data:
                    content = response_data["response"]
                elif "content" in response_data:
                    content = response_data["content"]
                elif "message" in response_data:
                    content = response_data["message"]
                elif isinstance(response_data, str):
                    content = response_data
            
            # 创建响应消息
            response_message = ChatMessage(role="assistant", content=content)
            
            # 创建选择
            choice = ChatCompletionChoice(
                index=0,
                message=response_message,
                finish_reason="stop"
            )
            
            # 估算token使用量（简单估算）
            prompt_tokens = 50  # 默认估算值
            completion_tokens = len(content.split()) * 1.3
            
            usage = ChatCompletionUsage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )
            
            return ChatCompletionResponse(
                id=request_id,
                created=created_time,
                model=model,
                choices=[choice],
                usage=usage
            )
            
        except Exception as e:
            logger.error(f"Error converting response: {e}")
            return self._create_error_response(model, f"Response conversion error: {str(e)}")
    
    def _create_error_response(self, model: str, error_message: str) -> ChatCompletionResponse:
        """创建错误响应"""
        error_message_obj = ChatMessage(
            role="assistant", 
            content=f"Error: {error_message}"
        )
        
        choice = ChatCompletionChoice(
            index=0,
            message=error_message_obj,
            finish_reason="error"
        )
        
        return ChatCompletionResponse(
            model=model,
            choices=[choice],
            usage=ChatCompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0
            )
        )
    
    async def _create_error_stream(self, model: str, error_message: str, request_id: str, created_time: int) -> AsyncGenerator[str, None]:
        """创建错误流式响应"""
        error_chunk = ChatCompletionStreamResponse(
            id=request_id,
            created=created_time,
            model=model,
            choices=[
                ChatCompletionStreamChoice(
                    index=0,
                    delta=ChatCompletionDelta(
                        role="assistant",
                        content=f"Error: {error_message}"
                    ),
                    finish_reason="error"
                )
            ]
        )
        yield f"data: {error_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        uptime = datetime.now() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime": str(uptime),
            "success_rate": (
                self.stats["successful_requests"] / max(self.stats["total_requests"], 1)
            ) * 100
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 检查目标API连通性
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(settings.target_api_url.replace('/chat', ''))
                api_status = "reachable" if response.status_code < 500 else "unreachable"
        except:
            api_status = "unreachable"
        
        token_status = token_manager.get_pool_status()
        
        return {
            "status": "healthy" if token_status["available_tokens"] > 0 and api_status == "reachable" else "degraded",
            "api_connectivity": api_status,
            "token_pool": token_status,
            "stats": self.get_stats()
        }

# 全局代理服务实例
proxy_service = ProxyService()