#!/bin/bash

# 自动发布脚本
# 用法: ./scripts/release.sh [version]
# 例如: ./scripts/release.sh v1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查是否在主分支
check_main_branch() {
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        log_error "必须在 main 分支上进行发布，当前分支: $current_branch"
        exit 1
    fi
    log_success "当前在 main 分支"
}

# 检查工作目录是否干净
check_clean_working_directory() {
    if [ -n "$(git status --porcelain)" ]; then
        log_error "工作目录不干净，请先提交或暂存所有更改"
        git status --short
        exit 1
    fi
    log_success "工作目录干净"
}

# 检查是否与远程同步
check_sync_with_remote() {
    git fetch origin
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/main)
    
    if [ "$local_commit" != "$remote_commit" ]; then
        log_error "本地分支与远程分支不同步，请先拉取最新代码"
        exit 1
    fi
    log_success "与远程分支同步"
}

# 验证版本格式
validate_version() {
    local version=$1
    if [[ ! $version =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9]+)?$ ]]; then
        log_error "版本格式无效: $version"
        log_info "正确格式: v1.0.0 或 v1.0.0-beta"
        exit 1
    fi
    log_success "版本格式有效: $version"
}

# 检查版本是否已存在
check_version_exists() {
    local version=$1
    if git tag -l | grep -q "^$version$"; then
        log_error "版本 $version 已存在"
        exit 1
    fi
    log_success "版本 $version 可用"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    if command -v python3 &> /dev/null; then
        python3 -m pytest tests/ -v
    elif command -v python &> /dev/null; then
        python -m pytest tests/ -v
    else
        log_error "找不到 Python 解释器"
        exit 1
    fi
    log_success "所有测试通过"
}

# 更新版本号
update_version() {
    local version=$1
    local version_number=${version#v}
    
    log_info "更新 pyproject.toml 中的版本号为 $version_number"
    
    # 使用 sed 更新版本号
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/version = \".*\"/version = \"$version_number\"/" pyproject.toml
    else
        # Linux
        sed -i "s/version = \".*\"/version = \"$version_number\"/" pyproject.toml
    fi
    
    log_success "版本号已更新"
}

# 创建发布提交
create_release_commit() {
    local version=$1
    
    log_info "创建发布提交..."
    git add pyproject.toml
    git commit -m "chore: bump version to $version"
    log_success "发布提交已创建"
}

# 创建标签
create_tag() {
    local version=$1
    
    log_info "创建标签 $version..."
    git tag -a "$version" -m "Release $version"
    log_success "标签 $version 已创建"
}

# 推送到远程
push_to_remote() {
    local version=$1
    
    log_info "推送提交和标签到远程仓库..."
    git push origin main
    git push origin "$version"
    log_success "已推送到远程仓库"
}

# 主函数
main() {
    local version=$1
    
    # 检查参数
    if [ -z "$version" ]; then
        log_error "请提供版本号"
        echo "用法: $0 <version>"
        echo "例如: $0 v1.0.0"
        exit 1
    fi
    
    log_info "开始发布流程: $version"
    
    # 执行检查
    check_main_branch
    check_clean_working_directory
    check_sync_with_remote
    validate_version "$version"
    check_version_exists "$version"
    
    # 运行测试
    run_tests
    
    # 更新版本并发布
    update_version "$version"
    create_release_commit "$version"
    create_tag "$version"
    push_to_remote "$version"
    
    log_success "发布完成！"
    log_info "GitHub Actions 将自动构建和发布 Docker 镜像"
    log_info "查看发布状态: https://github.com/jasonwong1991/orina2api/actions"
}

# 运行主函数
main "$@"