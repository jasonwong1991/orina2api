from pydantic_settings import BaseSettings
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # 基础配置
    app_name: str = "LLM Proxy API"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 3333
    
    # 目标API配置
    target_api_url: str = "https://api.orionai.asia/chat"
    conversation_api_url: str = "https://api.orionai.asia/conversation"
    project_api_url: str = "https://api.orionai.asia/project"
    message_api_url: str = "https://api.orionai.asia/conversation"  # 用于发送消息
    
    # API Key配置
    api_keys: List[str] = []  # 允许的API key列表
    require_api_key: bool = True  # 是否需要API key验证
    
    # Token池配置 (从环境变量读取)
    token_pool: str = ""  # JSON字符串格式的token数组
    
    # 模型配置 (数组格式) - 从.env文件读取
    available_models: List[str] = []
    
    # 请求配置
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # 请求头配置
    default_headers: Dict[str, str] = {
        'accept': '*/*',
        'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,zh-CN;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.orionai.asia',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.orionai.asia/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def token_pool_list(self) -> List[str]:
        """解析token_pool JSON字符串为列表"""
        if self.token_pool:
            try:
                return json.loads(self.token_pool)
            except json.JSONDecodeError:
                logger.warning("Failed to parse TOKEN_POOL JSON, using empty list")
                return []
        return []

settings = Settings()