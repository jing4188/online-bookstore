#!/bin/bash

# 书店管理系统 Docker 启动脚本

echo "书店管理系统 Docker 部署脚本"
echo "==============================="

# 检查 Docker 是否已安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装或未在 PATH 中"
    exit 1
fi

# 检查 Docker Compose 是否已安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装或未在 PATH 中"
    exit 1
fi

echo "Docker 和 Docker Compose 已安装，继续部署..."

# 构建并启动服务
echo "正在构建并启动书店管理系统..."
docker-compose up --build -d

echo ""
echo "系统部署完成！"
echo "访问地址："
echo "  - 用户端: http://localhost:3000"
echo "  - 管理员端: http://localhost:5001"
echo ""
echo "默认管理员账号："
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo "要查看服务日志，请运行: docker-compose logs -f"
echo "要停止服务，请运行: docker-compose down"