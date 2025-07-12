# OpenAI-Compatible LLM Proxy API

一个完全兼容OpenAI API格式的LLM接口反向代理服务，支持API key验证、token池管理和自动UUID生成。

## 🚀 功能特性

- 🔗 **OpenAI API兼容**: 完全兼容OpenAI API格式，支持现有的OpenAI SDK
- 🔐 **API Key验证**: 支持多种API key验证方式，防止未授权访问
- 🔄 **Token池管理**: 支持多个token轮换使用，自动故障转移
- 🆔 **自动对话管理**: 每次聊天前自动删除旧对话并创建新的对话ID，确保会话隔离
- 🧹 **智能清理**: 自动清理项目下的所有conversation，避免对话历史积累
- 📡 **动态Referer**: 根据对话ID动态生成referer头部，提高API兼容性
- 🎯 **智能重试**: 自动重试失败的请求，支持指数退避
- 📊 **状态监控**: 实时监控服务状态和token池状态
- 🛡️ **错误处理**: 完善的错误处理和日志记录
- 🐳 **Docker支持**: 完整的Docker部署方案，支持.env配置
- 🏗️ **模块化架构**: 清晰的代码结构，易于维护和扩展

## 📁 项目结构

```
orina2api/
├── app/                     # 主应用包
│   ├── api/                # API路由模块
│   │   ├── v1.py           # OpenAI兼容API
│   │   └── system.py       # 系统API
│   ├── core/               # 核心配置
│   │   └── config.py       # 应用配置
│   ├── models/             # 数据模型
│   │   └── schemas.py      # Pydantic模型
│   ├── services/           # 业务服务
│   │   ├── proxy.py        # 代理服务
│   │   └── token_manager.py # Token管理
│   ├── middleware/         # 中间件
│   │   └── auth.py         # 认证中间件
│   └── main.py             # FastAPI应用
├── tests/                  # 测试模块
├── docs/                   # 文档目录
├── main.py                 # 应用入口
├── start.py                # 启动脚本
├── requirements.txt        # 依赖列表
├── pyproject.toml          # 项目配置
└── .env.example            # 环境配置示例
```

## 📋 API接口

### 核心接口（OpenAI兼容）

- `GET /v1/models` - 获取可用模型列表
- `POST /v1/chat/completions` - 创建聊天完成

### 辅助接口

- `GET /health` - 健康检查
- `GET /` - 根路径信息
- `DELETE /admin/conversations` - 删除所有项目下的conversations（管理接口）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 使用启动脚本自动安装
python start.py --setup

# 或手动安装
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# API Key配置
API_KEYS=["your-api-key-1", "your-api-key-2"]
REQUIRE_API_KEY=true

# Token池配置
TOKEN_POOL=["your_token_1", "your_token_2", "your_token_3"]

# 模型配置
AVAILABLE_MODELS=["ChatGPT 4.1 Mini-Default", "ChatGPT 4.1 Mini-Writer", "ChatGPT 4.1 Mini-Researcher", "ChatGPT 4.1 Mini-Study", "ChatGPT 4.1 Mini-Developer", "ChatGPT 4.1 Mini-SEO Mode", "ChatGPT 4.1 Mini-Cybersecurity Mode", "Claude 4-Default", "Claude 4-Writer", "Claude 4-Researcher", "Claude 4-Study", "Claude 4-Developer", "Claude 4-SEO Mode", "Claude 4-Cybersecurity Mode", "o4-Default", "o4-Writer", "o4-Researcher", "o4-Study", "o4-Developer", "o4-SEO Mode", "o4-Cybersecurity Mode"]
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
python start.py --reload

# 生产模式
python start.py --workers 4

# 自定义端口
python start.py --port 9000
```

### 4. 访问服务

- API服务: http://localhost:3333
- API文档: http://localhost:3333/docs
- 健康检查: http://localhost:3333/health

## 🎯 使用示例

### 对话管理流程

现在每次聊天请求都会自动执行以下流程：

1. **清理旧对话**: 自动删除项目下的所有现有conversations
2. **创建新对话**: 调用 `POST /conversation` 接口创建新的对话ID
3. **动态Referer**: 根据对话ID生成动态的referer头部
4. **发起聊天**: 使用创建的对话ID进行实际的聊天请求

```
请求流程:
用户请求 → 删除旧对话 → 创建新对话 → 获取对话ID → 更新Headers → 发起聊天 → 返回响应
```

这确保了每次聊天都是全新的对话，避免了对话历史的积累和干扰。

### 手动管理

如果需要手动清理所有conversations，可以使用管理接口：

```bash
curl -X DELETE "http://localhost:3333/admin/conversations"
```

详细使用说明请参考：[Conversation管理功能文档](docs/conversation_management.md)

### OpenAI SDK兼容

```python
import openai

# 配置客户端指向本地代理
client = openai.OpenAI(
    base_url="http://localhost:3333/v1",
    api_key="your-api-key"  # 使用配置的API key
)

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_NAME` | 应用名称 | LLM Proxy API |
| `DEBUG` | 调试模式 | false |
| `HOST` | 服务器主机 | 0.0.0.0 |
| `PORT` | 服务器端口 | 3333 |
| `API_KEYS` | API密钥列表（JSON数组） | [] |
| `REQUIRE_API_KEY` | 是否需要API key验证 | true |
| `TARGET_API_URL` | 目标聊天API地址 | https://api.orionai.asia/chat |
| `CONVERSATION_API_URL` | 对话创建API地址 | https://api.orionai.asia/conversation |
| `PROJECT_API_URL` | 项目API地址 | https://api.orionai.asia/project |
| `MESSAGE_API_URL` | 消息API地址 | https://api.orionai.asia/conversation |
| `TOKEN_POOL` | Token池（JSON数组） | [] |
| `AVAILABLE_MODELS` | 可用模型列表（JSON数组） | [] |
| `TIMEOUT` | 请求超时时间（秒） | 30 |
| `MAX_RETRIES` | 最大重试次数 | 3 |
| `RETRY_DELAY` | 重试延迟（秒） | 1.0 |

### API Key验证

API支持多种API key验证方式：

1. **Authorization Header（推荐）**
   ```bash
   curl -H "Authorization: Bearer your-api-key" ...
   ```

2. **Query参数**
   ```bash
   curl "http://localhost:3333/v1/models?api_key=your-api-key"
   ```

3. **自定义Header**
   ```bash
   curl -H "X-API-Key: your-api-key" ...
   # 或
   curl -H "api-key: your-api-key" ...
   ```

**配置说明：**
- `REQUIRE_API_KEY=true`: 启用API key验证
- `REQUIRE_API_KEY=false`: 禁用API key验证（开发模式）
- `API_KEYS`: JSON数组格式的API key列表

**豁免路径：**
以下路径不需要API key验证：
- `/` - 根路径
- `/health` - 健康检查
- `/docs` - API文档

### Token池管理

Token池支持以下特性：

- **自动轮换**: 使用最少使用的token
- **故障转移**: 自动标记失败的token并切换
- **自动恢复**: 失败的token会在一定时间后重新尝试
- **负载均衡**: 平均分配请求到不同token

### 模型配置

支持动态配置可用模型：

```json
[
  "ChatGPT 4.1 Mini-Default", "ChatGPT 4.1 Mini-Writer", "ChatGPT 4.1 Mini-Researcher", "ChatGPT 4.1 Mini-Study", "ChatGPT 4.1 Mini-Developer", "ChatGPT 4.1 Mini-SEO Mode", "ChatGPT 4.1 Mini-Cybersecurity Mode",
  "ChatGPT 4.1-Default", "ChatGPT 4.1-Writer", "ChatGPT 4.1-Researcher", "ChatGPT 4.1-Study", "ChatGPT 4.1-Developer", "ChatGPT 4.1-SEO Mode", "ChatGPT 4.1-Cybersecurity Mode",
  "o4-Default", "o4-Writer", "o4-Researcher", "o4-Study", "o4-Developer", "o4-SEO Mode", "o4-Cybersecurity Mode",
  "Gemini 2.5 Flash 05-20-Default", "Gemini 2.5 Flash 05-20-Writer", "Gemini 2.5 Flash 05-20-Researcher", "Gemini 2.5 Flash 05-20-Study", "Gemini 2.5 Flash 05-20-Developer", "Gemini 2.5 Flash 05-20-SEO Mode", "Gemini 2.5 Flash 05-20-Cybersecurity Mode",
  "Gemini 2.5 Pro 06-05-Default", "Gemini 2.5 Pro 06-05-Writer", "Gemini 2.5 Pro 06-05-Researcher", "Gemini 2.5 Pro 06-05-Study", "Gemini 2.5 Pro 06-05-Developer", "Gemini 2.5 Pro 06-05-SEO Mode", "Gemini 2.5 Pro 06-05-Cybersecurity Mode",
  "Claude 3.5 Sonnet-Default", "Claude 3.5 Sonnet-Writer", "Claude 3.5 Sonnet-Researcher", "Claude 3.5 Sonnet-Study", "Claude 3.5 Sonnet-Developer", "Claude 3.5 Sonnet-SEO Mode", "Claude 3.5 Sonnet-Cybersecurity Mode",
  "Claude 4-Default", "Claude 4-Writer", "Claude 4-Researcher", "Claude 4-Study", "Claude 4-Developer", "Claude 4-SEO Mode", "Claude 4-Cybersecurity Mode",
  "DeepSeek R1-Default", "DeepSeek R1-Writer", "DeepSeek R1-Researcher", "DeepSeek R1-Study", "DeepSeek R1-Developer", "DeepSeek R1-SEO Mode", "DeepSeek R1-Cybersecurity Mode",
  "DeepSeek V3-Default", "DeepSeek V3-Writer", "DeepSeek V3-Researcher", "DeepSeek V3-Study", "DeepSeek V3-Developer", "DeepSeek V3-SEO Mode", "DeepSeek V3-Cybersecurity Mode",
  "Grok 3 Mini-Default", "Grok 3 Mini-Writer", "Grok 3 Mini-Researcher", "Grok 3 Mini-Study", "Grok 3 Mini-Developer", "Grok 3 Mini-SEO Mode", "Grok 3 Mini-Cybersecurity Mode",
  "Grok 3-Default", "Grok 3-Writer", "Grok 3-Researcher", "Grok 3-Study", "Grok 3-Developer", "Grok 3-SEO Mode", "Grok 3-Cybersecurity Mode",
  "Grok 4-Default", "Grok 4-Writer", "Grok 4-Researcher", "Grok 4-Study", "Grok 4-Developer", "Grok 4-SEO Mode", "Grok 4-Cybersecurity Mode"
]
```

## 🐳 部署

### Docker部署

1. **使用Docker Compose（推荐）**

```bash
# 复制环境配置
cp .env.example .env

# 编辑配置文件
vim .env

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

2. **直接使用Docker**

```bash
# 构建镜像
docker build -t llm-proxy .

# 运行容器
docker run -d \
  --name llm-proxy \
  -p 3333:3333 \
  --env-file .env \
  llm-proxy

# 查看日志
docker logs -f llm-proxy
```

### 生产环境

```bash
# 使用Gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3333

# 或使用内置启动脚本
python start.py --workers 4 --host 0.0.0.0 --port 3333
```

## 📊 监控和日志

### 健康检查

```bash
GET /health
```

返回详细的健康状态，包括：
- API连通性检查
- Token池状态
- 服务统计信息

### 日志配置

日志级别根据DEBUG设置自动调整：
- 生产环境: INFO级别
- 开发环境: DEBUG级别

### 监控指标

服务提供以下监控指标：
- 总请求数
- 成功请求数
- 失败请求数
- 成功率
- 运行时间
- Token池状态

## 🛠️ 开发

### 开发环境设置

1. **克隆项目**
```bash
git clone <repository-url>
cd orina2api
```

2. **安装依赖**
```bash
pip install -r requirements.txt
# 或安装开发依赖
pip install -e ".[dev]"
```

3. **配置环境**
```bash
cp .env.example .env
# 编辑 .env 文件配置必要参数
```

4. **运行测试**
```bash
pytest
```

5. **启动开发服务器**
```bash
python start.py --reload
```

### 代码质量

项目使用以下工具确保代码质量：
- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **pytest**: 单元测试

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 🔧 故障排除

### 常见问题

1. **API key验证失败**
   - 检查API key是否正确配置在 `API_KEYS` 中
   - 确认请求头格式正确
   - 检查是否访问了豁免路径

2. **所有token都失效**
   - 检查token是否过期
   - 确认目标API是否正常
   - 查看日志了解具体错误

3. **请求超时**
   - 增加TIMEOUT设置
   - 检查网络连接
   - 确认目标API响应时间

4. **高错误率**
   - 检查token有效性
   - 确认请求格式正确
   - 查看目标API状态

5. **Docker配置问题**
   - 确认 `.env` 文件格式正确
   - 检查JSON数组格式
   - 验证环境变量是否正确传递

### 日志分析

查看详细日志：

```bash
# 如果使用systemd
journalctl -u llm-proxy -f

# 或查看应用日志
tail -f app.log
```

## 📄 许可证

MIT License

## 🔗 相关链接
