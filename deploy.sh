#!/bin/bash

# Orina Proxy API 快速部署脚本
# 使用方法: ./deploy.sh [production|development]

set -e

MODE=${1:-development}
PROJECT_NAME="orina-proxy"

echo "🚀 开始部署 Orina Proxy API ($MODE 模式)"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建环境配置文件
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp .env.example .env
    
    echo "⚠️  请编辑 .env 文件配置以下参数："
    echo "   - API_KEYS: 设置API密钥"
    echo "   - TOKEN_POOL: 设置token池"
    echo "   - AVAILABLE_MODELS: 设置可用模型"
    echo ""
    echo "配置完成后重新运行此脚本"
    exit 0
fi

# 检查必要的环境变量
echo "🔍 检查配置..."
if ! grep -q "API_KEYS" .env || grep -q "your-api-key" .env; then
    echo "⚠️  请在 .env 文件中配置 API_KEYS"
    exit 1
fi

if ! grep -q "TOKEN_POOL" .env || grep -q "your_token" .env; then
    echo "⚠️  请在 .env 文件中配置 TOKEN_POOL"
    exit 1
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down 2>/dev/null || true

# 构建和启动服务
echo "🔨 构建和启动服务..."
if [ "$MODE" = "production" ]; then
    docker-compose up -d --build
else
    docker-compose up --build
fi

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
echo "🔍 执行健康检查..."
if curl -f http://localhost:3333/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "📋 服务信息："
    echo "   - API 地址: http://localhost:3333"
    echo "   - API 文档: http://localhost:3333/docs"
    echo "   - 健康检查: http://localhost:3333/health"
    echo ""
    echo "📝 使用示例："
    echo "   curl -H \"Authorization: Bearer your-api-key\" http://localhost:3333/v1/models"
    echo ""
    echo "📊 查看日志:"
    echo "   docker-compose logs -f"
else
    echo "❌ 服务启动失败，请检查日志："
    echo "   docker-compose logs"
    exit 1
fi
