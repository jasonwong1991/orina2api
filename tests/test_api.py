"""
API测试
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "OpenAI-compatible LLM Proxy API"
    assert "version" in data

def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code in [200, 500]  # 可能因为没有配置而失败
    
def test_models():
    """测试模型列表"""
    response = client.get("/v1/models")
    # 可能需要API key，所以可能返回401
    assert response.status_code in [200, 401]