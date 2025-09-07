#!/usr/bin/env python3
"""
圖表服務單元測試
測試可視化微服務的各項功能
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import pandas as pd
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.chart_service import app

# 測試客戶端
client = TestClient(app)

class TestChartServiceBasic:
    """圖表服務基礎測試"""
    
    def test_root_endpoint(self):
        """測試根端點"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Chart Generation Service"
        assert data["version"] == "1.0.0"
        assert "available_generators" in data
    
    def test_health_check(self):
        """測試健康檢查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "generators_status" in data
        assert "timestamp" in data
    
    def test_chart_types(self):
        """測試圖表類型查詢"""
        response = client.get("/chart-types")
        assert response.status_code == 200
        data = response.json()
        assert "basic" in data
        assert "professional" in data
        assert "tradingview" in data
        
        # 檢查每種類型都有availability和description
        for chart_type in data.values():
            assert "available" in chart_type
            assert "description" in chart_type
            assert isinstance(chart_type["available"], bool)
            assert isinstance(chart_type["description"], str)

class TestChartGeneration:
    """圖表生成功能測試"""
    
    def test_basic_chart_request(self):
        """測試基本圖表請求"""
        chart_request = {
            "symbol": "AAPL",
            "period": "3mo",
            "chart_type": "basic",
            "theme": "dark"
        }
        
        response = client.post("/generate-chart", json=chart_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["symbol"] == "AAPL"
        assert data["chart_type"] == "basic"
        assert data["success"] is True
        assert "chart_html" in data
        assert "generated_at" in data
    
    def test_professional_chart_request(self):
        """測試專業圖表請求"""
        chart_request = {
            "symbol": "TSLA",
            "period": "1y",
            "chart_type": "professional",
            "theme": "light",
            "indicators": {
                "rsi": 65.2,
                "macd": 1.8,
                "sma_20": 245.5
            },
            "patterns": [
                {
                    "pattern_name": "Head and Shoulders",
                    "confidence": 0.75,
                    "start_date": "2023-01-01",
                    "end_date": "2023-01-31"
                }
            ]
        }
        
        response = client.post("/generate-chart", json=chart_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["symbol"] == "TSLA"
        assert data["chart_type"] == "professional"
        assert data["success"] is True
    
    def test_tradingview_chart_request(self):
        """測試TradingView風格圖表"""
        chart_request = {
            "symbol": "GOOGL",
            "chart_type": "tradingview",
            "theme": "dark"
        }
        
        response = client.post("/generate-chart", json=chart_request)
        assert response.status_code == 200
        data = response.json()
        
        assert data["chart_type"] == "tradingview"
        assert "chart_html" in data

class TestChartGenerationWithData:
    """帶真實數據的圖表生成測試"""
    
    def test_chart_with_mock_data(self):
        """測試帶模擬數據的圖表生成"""
        # 創建模擬股票數據
        mock_data = {
            "open": [100, 101, 102, 103, 104],
            "high": [105, 106, 107, 108, 109],
            "low": [95, 96, 97, 98, 99],
            "close": [104, 105, 106, 107, 108],
            "volume": [1000000, 1100000, 1200000, 1300000, 1400000]
        }
        
        chart_request = {
            "symbol": "MOCK",
            "chart_type": "basic",
            "data": mock_data,
            "indicators": {
                "rsi": 58.5,
                "macd": 0.8
            }
        }
        
        with patch('pandas.DataFrame') as mock_df:
            # Mock pandas DataFrame
            mock_df.return_value = pd.DataFrame(mock_data)
            
            response = client.post("/generate-chart", json=chart_request)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

class TestErrorHandling:
    """錯誤處理測試"""
    
    def test_invalid_chart_type(self):
        """測試無效圖表類型"""
        chart_request = {
            "symbol": "AAPL",
            "chart_type": "invalid_type"
        }
        
        response = client.post("/generate-chart", json=chart_request)
        # 可能返回成功但使用默認類型，或者返回錯誤
        assert response.status_code in [200, 400, 422]
    
    def test_missing_required_fields(self):
        """測試缺少必需字段"""
        incomplete_request = {
            "chart_type": "basic"
            # 缺少symbol
        }
        
        response = client.post("/generate-chart", json=incomplete_request)
        assert response.status_code == 422  # Validation error
        
        error_detail = response.json()
        assert "detail" in error_detail
    
    def test_malformed_json(self):
        """測試格式錯誤的JSON"""
        response = client.post(
            "/generate-chart",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestChartGeneratorAvailability:
    """圖表生成器可用性測試"""
    
    @patch('src.services.chart_service.professional_chart_generator', None)
    def test_professional_generator_unavailable(self):
        """測試專業圖表生成器不可用"""
        chart_request = {
            "symbol": "AAPL",
            "chart_type": "professional"
        }
        
        response = client.post("/generate-chart", json=chart_request)
        
        # 應該返回503服務不可用，或者降級到其他生成器
        if response.status_code == 503:
            assert "專業圖表生成器不可用" in response.json()["detail"]
        elif response.status_code == 200:
            # 可能降級到基礎圖表
            data = response.json()
            assert data["success"] is False or "error" in data
    
    @patch('src.services.chart_service.tradingview_chart_generator', None)
    def test_tradingview_generator_unavailable(self):
        """測試TradingView圖表生成器不可用"""
        chart_request = {
            "symbol": "AAPL",
            "chart_type": "tradingview"
        }
        
        response = client.post("/generate-chart", json=chart_request)
        
        if response.status_code == 503:
            assert "TradingView圖表生成器不可用" in response.json()["detail"]

class TestPerformance:
    """性能測試"""
    
    def test_multiple_chart_requests(self):
        """測試多個圖表請求"""
        symbols = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        
        for symbol in symbols:
            chart_request = {
                "symbol": symbol,
                "chart_type": "basic"
            }
            
            response = client.post("/generate-chart", json=chart_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["symbol"] == symbol
    
    def test_concurrent_requests(self):
        """測試並發請求處理"""
        import threading
        import time
        
        results = []
        
        def make_request(symbol):
            chart_request = {
                "symbol": f"TEST{symbol}",
                "chart_type": "basic"
            }
            response = client.post("/generate-chart", json=chart_request)
            results.append(response.status_code)
        
        # 創建5個並發請求
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有請求完成
        for thread in threads:
            thread.join()
        
        # 檢查所有請求都成功
        assert all(status == 200 for status in results)
        assert len(results) == 5

class TestIntegrationWithCoreService:
    """與核心服務的集成測試"""
    
    def test_chart_service_response_format(self):
        """測試圖表服務響應格式符合核心服務期望"""
        chart_request = {
            "symbol": "INTEGRATION_TEST",
            "chart_type": "professional",
            "theme": "dark",
            "indicators": {"rsi": 50},
            "patterns": []
        }
        
        response = client.post("/generate-chart", json=chart_request)
        assert response.status_code == 200
        
        data = response.json()
        
        # 檢查核心服務期望的字段
        required_fields = ["chart_html", "chart_type", "symbol", "generated_at", "success"]
        for field in required_fields:
            assert field in data
        
        # 檢查數據類型
        assert isinstance(data["chart_html"], str)
        assert isinstance(data["chart_type"], str)
        assert isinstance(data["symbol"], str)
        assert isinstance(data["success"], bool)

if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v", "--tb=short"])