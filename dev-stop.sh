#!/bin/bash

# AI Trading System - Local Development Stop Script
echo "🛑 Stopping AI Trading System Local Development Environment..."

# 停止並移除容器
docker-compose -f docker-compose.local.yml down

echo "✅ All services stopped!"
echo ""
echo "💡 To clean up everything (including data):"
echo "   docker-compose -f docker-compose.local.yml down -v"
echo "   docker system prune -f"