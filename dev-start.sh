#!/bin/bash

# AI Trading System - Local Development Startup Script
echo "🚀 Starting AI Trading System Local Development Environment..."

# 檢查 Docker 是否運行
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# 檢查環境文件
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local file not found. Please create it first."
    exit 1
fi

echo "📋 Environment Configuration:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - Database: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""

# 創建必要的目錄
mkdir -p logs
mkdir -p data

# 啟動開發環境
echo "🔄 Starting services..."
docker-compose -f docker-compose.local.yml up --build -d

# 等待服務啟動
echo "⏳ Waiting for services to start..."
sleep 10

# 檢查服務狀態
echo "📊 Service Status:"
docker-compose -f docker-compose.local.yml ps

# 顯示日誌
echo ""
echo "📝 Recent logs:"
docker-compose -f docker-compose.local.yml logs --tail=20

echo ""
echo "✅ Development environment started!"
echo ""
echo "🔗 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.local.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.local.yml down"
echo "   Restart: docker-compose -f docker-compose.local.yml restart"
echo ""
echo "Happy coding! 🎉"