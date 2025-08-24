#!/bin/bash

# 文件传输系统启动脚本

echo "正在启动文件传输系统..."

# 激活虚拟环境
source venv/bin/activate

# 检查数据库迁移
echo "检查数据库迁移..."
python manage.py makemigrations --check
python manage.py migrate

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput

# 启动开发服务器
echo "启动开发服务器..."
echo "系统将在 http://localhost:8001 启动"
echo "管理后台: http://localhost:8001/admin"
echo "默认账号: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务器"

python manage.py runserver 0.0.0.0:8001