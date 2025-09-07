#!/usr/bin/env python3
"""
核心API服務單元測試
測試微服務架構中的核心功能
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd
from datetime import datetime

# 導入核心服務
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.main_core import app
from src.auth.models import User

# 測試客戶端
client = TestClient(app)

class TestCoreServiceBasic:
    """基礎服務測試"""
    
    def test_root_endpoint(self):
        """測試根端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Auto Trade Core API"
        assert data["version"] == "2.0.0"
        assert data["architecture"] == "microservices"
        assert "stock_data_analysis" in data["features"]
    
    def test_health_check(self):
        """測試健康檢查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "core-api"
        assert "dependencies" in data
        assert "database" in data["dependencies"]
    
    def test_symbols_endpoint(self):
        """測試股票代碼端點"""
        response = client.get("/symbols")
        assert response.status_code == 200
        data = response.json()
        assert "us_symbols" in data
        assert "tw_symbols" in data
        assert "total" in data
        assert isinstance(data["us_symbols"], list)
        assert isinstance(data["tw_symbols"], list)

class TestStockAnalysis:
    """股票分析功能測試"""
    
    @patch('src.auth.auth.get_current_user')
    @patch('src.data_fetcher.us_stocks.USStockDataFetcher.get_stock_data')
    @patch('src.analysis.technical_indicators.IndicatorAnalyzer.calculate_all_indicators')
    def test_analyze_stock_success(self, mock_indicators, mock_data, mock_user):
        """測試股票分析成功案例"""
        # Mock用戶
        mock_user.return_value = User(
            id="test-user-id",
            email="test@example.com",
            is_active=True
        )
        
        # Mock股票數據
        mock_stock_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [104, 105, 106],
            'volume': [1000000, 1100000, 1200000]
        }, index=pd.date_range('2023-01-01', periods=3))
        
        mock_data.return_value = mock_stock_data
        
        # Mock技術指標
        mock_indicators.return_value = {
            'rsi': 65.5,
            'macd': 2.1,
            'sma_20': 104.5
        }
        
        # 測試分析請求
        response = client.post(
            "/analyze/AAPL",
            json={
                "symbol": "AAPL",
                "period": "3mo",
                "include_ai": False,
                "include_patterns": False
            },
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["market"] == "US"
        assert "current_price" in data
        assert "indicators" in data
        assert data["data_points"] == 3
    
    @patch('src.auth.auth.get_current_user')
    def test_analyze_stock_unauthorized(self, mock_user):
        """測試未授權訪問"""
        mock_user.side_effect = Exception("Unauthorized")
        
        response = client.post(
            "/analyze/AAPL",
            json={"symbol": "AAPL"}
        )
        
        # 應該返回401或403
        assert response.status_code in [401, 403, 500]
    
    @patch('src.auth.auth.get_current_user')
    @patch('src.data_fetcher.us_stocks.USStockDataFetcher.get_stock_data')
    def test_analyze_stock_no_data(self, mock_data, mock_user):
        """測試股票數據不存在"""
        mock_user.return_value = User(id="test", email="test@example.com", is_active=True)
        mock_data.return_value = pd.DataFrame()  # 空數據框
        
        response = client.post(
            "/analyze/INVALID",
            json={"symbol": "INVALID"},
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == 404
        assert "股票數據未找到" in response.json()["detail"]

class TestChartIntegration:
    """圖表服務整合測試"""
    
    @patch('src.auth.auth.get_current_user')
    @patch('httpx.AsyncClient.post')
    def test_chart_generation_success(self, mock_http, mock_user):
        """測試圖表生成成功"""
        mock_user.return_value = User(id="test", email="test@example.com", is_active=True)
        
        # Mock圖表服務響應
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chart_html": "<div>Mock Chart</div>",
            "chart_type": "professional",
            "success": True
        }
        mock_http.return_value = mock_response
        
        with patch('src.api.main_core.analyze_stock') as mock_analyze:
            mock_analyze.return_value = {
                "symbol": "AAPL",
                "indicators": {"rsi": 65},
                "patterns": []
            }
            
            response = client.get(
                "/chart/AAPL?chart_type=professional",
                headers={"Authorization": "Bearer fake-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "chart_html" in data
    
    @patch('src.auth.auth.get_current_user')
    @patch('httpx.AsyncClient.post')
    def test_chart_service_unavailable(self, mock_http, mock_user):
        """測試圖表服務不可用"""
        mock_user.return_value = User(id="test", email="test@example.com", is_active=True)
        
        # Mock圖表服務錯誤
        mock_response = Mock()
        mock_response.status_code = 503
        mock_http.return_value = mock_response
        
        with patch('src.api.main_core.analyze_stock') as mock_analyze:
            mock_analyze.return_value = {"symbol": "AAPL"}
            
            response = client.get(
                "/chart/AAPL",
                headers={"Authorization": "Bearer fake-token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["fallback"] is True
            assert "圖表服務暫時不可用" in data["chart_html"]

class TestAIIntegration:
    """AI功能整合測試"""
    
    @patch('src.auth.auth.get_current_user')
    @patch('src.analysis.ai_strategy_advisor.AIStrategyAdvisor.get_strategy_advice')
    def test_ai_strategy_advice(self, mock_ai, mock_user):
        """測試AI策略建議"""
        mock_user.return_value = User(id="test", email="test@example.com", is_active=True)
        mock_ai.return_value = "建議買入，技術指標顯示強勢上升趨勢"
        
        response = client.post(
            "/ai/strategy-advice",
            json={
                "symbol": "AAPL",
                "market_data": {"price": 150},
                "preferences": {"risk_level": "moderate"}
            },
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "advice" in data
        assert "timestamp" in data
    
    @patch('src.auth.auth.get_current_user')
    @patch('src.analysis.ai_strategy_advisor.AIStrategyAdvisor.get_strategy_advice')
    def test_ai_service_error(self, mock_ai, mock_user):
        """測試AI服務錯誤"""
        mock_user.return_value = User(id="test", email="test@example.com", is_active=True)
        mock_ai.side_effect = Exception("AI service unavailable")
        
        response = client.post(
            "/ai/strategy-advice",
            json={"symbol": "AAPL"},
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == 500
        assert "AI服務暫時不可用" in response.json()["detail"]

class TestErrorHandling:
    """錯誤處理測試"""
    
    def test_invalid_endpoints(self):
        """測試無效端點"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_malformed_requests(self):
        """測試格式錯誤的請求"""
        response = client.post(
            "/analyze/AAPL",
            json={"invalid": "data"},
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # 可能返回422或500，取決於驗證器
        assert response.status_code in [422, 500]

if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v", "--tb=short"])