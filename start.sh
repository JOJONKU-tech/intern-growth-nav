#!/bin/bash
set -e
cd "$(dirname "$0")/backend"

# Install deps if needed
PIP_CERT=/etc/ssl/cert.pem pip3 install -r requirements.txt -q 2>/dev/null || pip3 install fastapi uvicorn sqlalchemy -q 2>/dev/null

# Check if DB exists, if not seed
if [ ! -f intern_growth.db ]; then
  echo "首次启动，生成演示数据..."
  PIP_CERT=/etc/ssl/cert.pem python3 seed.py
  echo ""
fi

echo "==================================="
echo "  业务部实习生成长导航"
echo "  http://localhost:8000"
echo "==================================="
echo ""
echo "演示账号（点击角色卡片直接登录）："
echo ""
echo "  导师："
echo "    张伟（研发）   id=2"
echo "    李明（产品）   id=3"
echo "    陈芳（销售）   id=4"
echo ""
echo "  实习生："
echo "    赵一（研发）   id=5"
echo "    钱二（研发）   id=6"
echo "    冯九（产品）   id=11"
echo "    韩十五（销售） id=19"
echo "...共 20 人，登录页可选"
echo ""
echo "  HR："
echo "    王芳           id=1"
echo ""
echo "API 文档：http://localhost:8000/docs"
echo "==================================="
echo ""

PIP_CERT=/etc/ssl/cert.pem uvicorn main:app --host 0.0.0.0 --port 8000 --reload
