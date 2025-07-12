import asyncio
import random
import logging
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
from app.core.config import settings

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens.copy()
        self.current_index = 0
        self.failed_tokens = set()
        self.token_last_used = {}
        self.token_failure_count = {}
        self.lock = asyncio.Lock()
        
    async def get_token(self) -> Optional[str]:
        """获取下一个可用的token"""
        async with self.lock:
            if not self.tokens:
                logger.error("No tokens available in the pool")
                return None
                
            # 清理过期的失败记录
            await self._cleanup_failed_tokens()
            
            # 获取可用的token
            available_tokens = [token for token in self.tokens if token not in self.failed_tokens]
            
            if not available_tokens:
                logger.warning("All tokens are currently marked as failed, resetting...")
                self.failed_tokens.clear()
                self.token_failure_count.clear()
                available_tokens = self.tokens.copy()
            
            # 轮换策略：使用最少使用的token
            token = self._get_least_used_token(available_tokens)
            self.token_last_used[token] = datetime.now()
            
            logger.info(f"Selected token ending with: ...{token[-10:]}")
            return token
    
    def _get_least_used_token(self, available_tokens: List[str]) -> str:
        """获取最少使用的token"""
        if not available_tokens:
            return self.tokens[0]
            
        # 按最后使用时间排序，选择最久未使用的
        sorted_tokens = sorted(
            available_tokens,
            key=lambda t: self.token_last_used.get(t, datetime.min)
        )
        return sorted_tokens[0]
    
    async def mark_token_failed(self, token: str, error_msg: str = ""):
        """标记token为失败状态"""
        async with self.lock:
            self.failed_tokens.add(token)
            self.token_failure_count[token] = self.token_failure_count.get(token, 0) + 1
            logger.warning(f"Token marked as failed: ...{token[-10:]} - {error_msg}")
            
            # 如果失败次数过多，从池中移除
            if self.token_failure_count[token] >= 5:
                logger.error(f"Token removed from pool due to repeated failures: ...{token[-10:]}")
                if token in self.tokens:
                    self.tokens.remove(token)
    
    async def mark_token_success(self, token: str):
        """标记token为成功状态"""
        async with self.lock:
            if token in self.failed_tokens:
                self.failed_tokens.remove(token)
                logger.info(f"Token restored to active status: ...{token[-10:]}")
            
            # 重置失败计数
            if token in self.token_failure_count:
                self.token_failure_count[token] = 0
    
    async def _cleanup_failed_tokens(self):
        """清理过期的失败token记录"""
        current_time = datetime.now()
        cleanup_threshold = timedelta(minutes=10)  # 10分钟后重试失败的token
        
        tokens_to_restore = []
        for token in list(self.failed_tokens):
            last_used = self.token_last_used.get(token)
            if last_used and (current_time - last_used) > cleanup_threshold:
                tokens_to_restore.append(token)
        
        for token in tokens_to_restore:
            self.failed_tokens.remove(token)
            logger.info(f"Token restored after cleanup: ...{token[-10:]}")
    
    def add_token(self, token: str):
        """添加新token到池中"""
        if token not in self.tokens:
            self.tokens.append(token)
            logger.info(f"New token added to pool: ...{token[-10:]}")
    
    def remove_token(self, token: str):
        """从池中移除token"""
        if token in self.tokens:
            self.tokens.remove(token)
            logger.info(f"Token removed from pool: ...{token[-10:]}")
    
    def get_pool_status(self) -> dict:
        """获取token池状态"""
        return {
            "total_tokens": len(self.tokens),
            "failed_tokens": len(self.failed_tokens),
            "available_tokens": len(self.tokens) - len(self.failed_tokens),
            "token_details": [
                {
                    "token_suffix": token[-10:],
                    "status": "failed" if token in self.failed_tokens else "active",
                    "failure_count": self.token_failure_count.get(token, 0),
                    "last_used": self.token_last_used.get(token)
                }
                for token in self.tokens
            ]
        }
    
    def validate_token(self, token: str) -> bool:
        """验证token格式"""
        try:
            # 简单的JWT格式验证
            jwt.decode(token, options={"verify_signature": False})
            return True
        except:
            return False

# 全局token管理器实例
token_manager = TokenManager(settings.token_pool_list)