#!/usr/bin/env python3
"""
LLM Proxy API 启动脚本
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"依赖安装失败: {e}")
        sys.exit(1)

def create_env_file():
    """创建环境配置文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("创建环境配置文件...")
        env_file.write_text(env_example.read_text())
        print("已创建 .env 文件，请根据需要修改配置")

def start_server(host="0.0.0.0", port=3333, reload=False, workers=1):
    """启动服务器"""
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--workers", str(workers)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"启动服务器: http://{host}:{port}")
    print("API文档: http://{}:{}/docs".format(host, port))
    print("按 Ctrl+C 停止服务器")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n服务器已停止")

def main():
    parser = argparse.ArgumentParser(description="LLM Proxy API 启动脚本")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=3333, help="服务器端口")
    parser.add_argument("--reload", action="store_true", help="开启自动重载（开发模式）")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    parser.add_argument("--install", action="store_true", help="安装依赖")
    parser.add_argument("--setup", action="store_true", help="初始化设置")
    
    args = parser.parse_args()
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    if args.install or args.setup:
        install_dependencies()
    
    # 创建环境配置文件
    if args.setup:
        create_env_file()
        print("设置完成！现在可以运行: python start.py")
        return
    
    # 启动服务器
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )

if __name__ == "__main__":
    main()
