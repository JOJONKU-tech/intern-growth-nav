#!/bin/bash
cd "$(dirname "$0")"

# Create static dir if needed
mkdir -p static

# Install deps
PIP_CERT=/etc/ssl/cert.pem pip3 install fastapi uvicorn -q 2>/dev/null

echo ""
echo "  ================================="
echo "   业务部实习生成长导航"
echo "   http://localhost:8000"
echo "  ================================="
echo ""
echo "  演示账号："
echo "    导师-张伟 (研发, id=2)"
echo "    导师-李明 (产品, id=3)"
echo "    导师-陈芳 (销售, id=4)"
echo "    实习生-赵一 (研发, id=5)"
echo "    实习生-冯九 (产品, id=13)"
echo "    实习生-韩十五 (销售, id=19)"
echo "    HR-王芳 (id=1)"
echo ""

PIP_CERT=/etc/ssl/cert.pem python3 app.py
