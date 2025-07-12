# 贡献指南

感谢您对 orina2api 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/jasonwong1991/orina2api.git
cd orina2api
```

### 2. 设置开发环境

运行自动化设置脚本：

```bash
./scripts/setup-dev.sh
```

或手动设置：

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx flake8 mypy black isort

# 复制环境配置
cp .env.example .env
# 编辑 .env 文件设置您的配置
```

### 3. 运行项目

```bash
# 激活虚拟环境
source venv/bin/activate

# 启动开发服务器
python start.py

# 访问 API 文档
open http://localhost:8000/docs
```

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 开发和测试

```bash
# 运行测试
python -m pytest tests/ -v

# 代码格式化
black app/ tests/
isort app/ tests/

# 代码检查
flake8 app/ tests/
mypy app/ --ignore-missing-imports

# 安全检查
bandit -r app/
```

### 3. 提交更改

```bash
git add .
git commit -m "feat: add your feature description"
```

### 4. 推送并创建 Pull Request

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python 代码风格

- 使用 [Black](https://black.readthedocs.io/) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 进行导入排序
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用类型注解 (Type Hints)

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(api): add new endpoint for token management
fix(auth): resolve authentication middleware issue
docs: update API documentation
```

## 测试指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/test_api.py -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ -v --cov=app --cov-report=html
```

### 编写测试

- 为新功能编写对应的测试用例
- 确保测试覆盖率不低于 80%
- 使用描述性的测试名称
- 测试文件命名格式：`test_*.py`

示例测试：

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_async_function():
    """测试异步函数"""
    result = await some_async_function()
    assert result is not None
```

## 文档贡献

### API 文档

- API 文档使用 FastAPI 自动生成
- 确保所有端点都有适当的文档字符串
- 使用 Pydantic 模型定义请求和响应格式

### README 和其他文档

- 使用清晰、简洁的语言
- 提供实际的代码示例
- 保持文档与代码同步

## Pull Request 指南

### 提交前检查清单

- [ ] 代码通过所有测试
- [ ] 代码符合项目风格规范
- [ ] 添加了必要的测试用例
- [ ] 更新了相关文档
- [ ] 提交信息符合规范

### PR 描述模板

```markdown
## 变更类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 代码重构
- [ ] 其他

## 变更描述
简要描述您的变更内容

## 测试
- [ ] 添加了新的测试用例
- [ ] 所有测试通过
- [ ] 手动测试通过

## 相关 Issue
关闭 #issue_number

## 截图/演示
如果适用，请提供截图或演示
```

## 发布流程

项目维护者会使用以下命令创建新版本：

```bash
# 创建新版本
./scripts/release.sh v1.0.0
```

这将自动：
1. 运行所有测试
2. 更新版本号
3. 创建 Git 标签
4. 触发 GitHub Actions 自动发布

## 问题报告

### Bug 报告

使用 GitHub Issues 报告 Bug，请包含：

- 详细的问题描述
- 重现步骤
- 期望行为
- 实际行为
- 环境信息（Python 版本、操作系统等）
- 相关日志或错误信息

### 功能请求

提交功能请求时，请包含：

- 功能描述
- 使用场景
- 预期收益
- 可能的实现方案

## 社区准则

- 保持友好和专业的态度
- 尊重不同的观点和经验水平
- 提供建设性的反馈
- 遵循项目的行为准则

## 联系方式

如果您有任何问题或建议，可以通过以下方式联系我们：

- 创建 GitHub Issue
- 发起 GitHub Discussion
- 发送邮件至项目维护者

## 许可证

通过贡献代码，您同意您的贡献将在与项目相同的许可证下发布。

---

再次感谢您的贡献！🎉