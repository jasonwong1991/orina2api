#!/bin/bash

# 开发环境设置脚本
# 用法: ./scripts/setup-dev.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 版本
check_python() {
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_info "Python 版本: $python_version"
        
        # 检查是否为 3.9+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
            log_success "Python 版本符合要求 (>= 3.9)"
        else
            log_error "Python 版本过低，需要 3.9 或更高版本"
            exit 1
        fi
    else
        log_error "未找到 Python 3"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境..."
        python3 -m venv venv
        log_success "虚拟环境已创建"
    else
        log_info "虚拟环境已存在"
    fi
}

# 激活虚拟环境并安装依赖
install_dependencies() {
    log_info "激活虚拟环境并安装依赖..."
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装项目依赖
    pip install -r requirements.txt
    
    # 安装开发依赖
    pip install pytest pytest-asyncio pytest-cov httpx flake8 mypy black isort bandit safety
    
    log_success "依赖安装完成"
}

# 设置 Git hooks
setup_git_hooks() {
    log_info "设置 Git hooks..."
    
    # 创建 pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# 运行代码格式化
echo "运行代码格式化..."
source venv/bin/activate
black app/ tests/ --check --diff
isort app/ tests/ --check-only --diff

# 运行 linting
echo "运行 linting..."
flake8 app/ tests/

# 运行类型检查
echo "运行类型检查..."
mypy app/ --ignore-missing-imports

# 运行测试
echo "运行测试..."
python -m pytest tests/ -v

echo "所有检查通过！"
EOF

    chmod +x .git/hooks/pre-commit
    log_success "Git hooks 设置完成"
}

# 创建开发配置文件
create_dev_config() {
    if [ ! -f ".env" ]; then
        log_info "创建开发环境配置文件..."
        cp .env.example .env
        log_warning "请编辑 .env 文件设置您的配置"
    else
        log_info "开发环境配置文件已存在"
    fi
}

# 运行初始测试
run_initial_tests() {
    log_info "运行初始测试..."
    source venv/bin/activate
    python -m pytest tests/ -v
    log_success "初始测试通过"
}

# 显示开发指南
show_dev_guide() {
    echo
    log_success "开发环境设置完成！"
    echo
    echo "🚀 快速开始:"
    echo "  1. 激活虚拟环境: source venv/bin/activate"
    echo "  2. 启动开发服务器: python start.py"
    echo "  3. 访问 API 文档: http://localhost:8000/docs"
    echo
    echo "🔧 开发工具:"
    echo "  - 运行测试: python -m pytest tests/ -v"
    echo "  - 代码格式化: black app/ tests/"
    echo "  - 导入排序: isort app/ tests/"
    echo "  - 代码检查: flake8 app/ tests/"
    echo "  - 类型检查: mypy app/"
    echo "  - 安全检查: bandit -r app/"
    echo
    echo "📦 发布:"
    echo "  - 创建发布: ./scripts/release.sh v1.0.0"
    echo
    echo "📚 文档:"
    echo "  - API 文档: http://localhost:8000/docs"
    echo "  - README: ./README.md"
}

# 主函数
main() {
    log_info "设置 orina2api 开发环境..."
    
    check_python
    create_venv
    install_dependencies
    setup_git_hooks
    create_dev_config
    run_initial_tests
    show_dev_guide
}

# 运行主函数
main "$@"