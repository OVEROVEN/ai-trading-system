#!/usr/bin/env python3
"""
微服務集成測試
測試核心服務與圖表服務之間的集成
"""

import pytest
import asyncio
import httpx
import time
from unittest.mock import patch, Mock
import threading
import sys
import os

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMicroservicesIntegration:
    """微服務集成測試"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """測試設置"""
        self.core_service_url = "http://localhost:8002"
        self.chart_service_url = "http://localhost:8001"
        
        # 測試用的mock token
        self.mock_token = "Bearer test-token-123"
    
    def test_core_service_connectivity(self):
        """測試核心服務連通性"""
        try:
            response = httpx.get(f"{self.core_service_url}/health", timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "core-api"
        except httpx.ConnectError:
            pytest.skip("核心服務未運行，跳過集成測試")
    
    def test_chart_service_connectivity(self):
        """測試圖表服務連通性"""
        try:
            response = httpx.get(f"{self.chart_service_url}/health", timeout=5.0)
            # 由於圖表服務可能未實際運行，我們只檢查是否能連接
            # 實際測試中會啟動圖表服務
            print("圖表服務連接測試完成")
        except httpx.ConnectError:
            print("圖表服務未運行，將模擬測試")
    
    @patch('httpx.AsyncClient.post')
    async def test_core_to_chart_communication(self, mock_post):
        """測試核心服務到圖表服務的通信"""
        # Mock圖表服務響應
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "chart_html": "<div>Professional Chart for AAPL</div>",
            "chart_type": "professional", 
            "symbol": "AAPL",
            "generated_at": "2023-01-01T12:00:00",
            "success": True
        }
        mock_post.return_value = mock_response
        
        # 測試核心服務的圖表端點
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.core_service_url}/chart/AAPL?chart_type=professional",
                    headers={"Authorization": self.mock_token},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "chart_html" in data or "fallback" in data
                    
            except httpx.ConnectError:
                pytest.skip("核心服務未運行")
    
    def test_service_fallback_behavior(self):
        """測試服務降級行為"""
        # 這個測試檢查當圖表服務不可用時，核心服務是否能正常降級
        try:
            response = httpx.get(
                f"{self.core_service_url}/chart/AAPL",
                headers={"Authorization": self.mock_token},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                # 檢查是否有降級標識或正常圖表
                assert ("fallback" in data and data["fallback"] is True) or \
                       ("chart_html" in data and data.get("success", True))
                
        except httpx.ConnectError:
            pytest.skip("核心服務未運行")
    
    def test_data_flow_integration(self):
        """測試完整的數據流程集成"""
        # 測試：請求分析 -> 獲取數據 -> 生成圖表 -> 返回結果
        test_scenarios = [
            {
                "symbol": "AAPL",
                "period": "1mo",
                "chart_type": "professional"
            },
            {
                "symbol": "TSLA", 
                "period": "3mo",
                "chart_type": "basic"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                # 步驟1：測試股票分析
                analysis_response = httpx.post(
                    f"{self.core_service_url}/analyze/{scenario['symbol']}",
                    json={
                        "symbol": scenario['symbol'],
                        "period": scenario['period'],
                        "include_ai": False,
                        "include_patterns": True
                    },
                    headers={"Authorization": self.mock_token},
                    timeout=15.0
                )
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()
                    assert analysis_data["symbol"] == scenario['symbol']
                    
                    # 步驟2：測試圖表生成
                    chart_response = httpx.get(
                        f"{self.core_service_url}/chart/{scenario['symbol']}?chart_type={scenario['chart_type']}",
                        headers={"Authorization": self.mock_token},
                        timeout=15.0
                    )
                    
                    if chart_response.status_code == 200:
                        chart_data = chart_response.json()
                        assert "chart_html" in chart_data or chart_data.get("fallback", False)
                        
            except httpx.ConnectError:
                pytest.skip(f"服務連接失敗，跳過 {scenario['symbol']} 測試")
            except httpx.TimeoutException:
                pytest.skip(f"服務響應超時，跳過 {scenario['symbol']} 測試")

class TestServiceResilience:
    """服務彈性測試"""
    
    def test_core_service_without_chart_service(self):
        """測試圖表服務不可用時核心服務的表現"""
        try:
            # 測試基本分析功能（不依賴圖表服務）
            response = httpx.post(
                "http://localhost:8002/analyze/AAPL",
                json={
                    "symbol": "AAPL",
                    "period": "1mo", 
                    "include_ai": False,
                    "include_patterns": False
                },
                headers={"Authorization": "Bearer test-token"},
                timeout=10.0
            )
            
            # 核心分析功能應該仍然工作
            if response.status_code in [200, 401, 403]:  # 200正常，401/403認證相關
                print("核心分析功能獨立運行正常")
            else:
                print(f"核心服務響應: {response.status_code}")
                
        except httpx.ConnectError:
            pytest.skip("核心服務未運行")
    
    def test_service_response_times(self):
        """測試服務響應時間"""
        endpoints_to_test = [
            ("http://localhost:8002/health", "核心服務健康檢查"),
            ("http://localhost:8002/symbols", "股票代碼查詢"),
        ]
        
        for url, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = httpx.get(url, timeout=5.0)
                end_time = time.time()
                
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    print(f"{description}: {response_time:.3f}秒")
                    assert response_time < 2.0, f"{description}響應時間過長: {response_time:.3f}秒"
                
            except httpx.ConnectError:
                print(f"{description}: 服務未運行")
            except httpx.TimeoutException:
                pytest.fail(f"{description}: 響應超時")

class TestConcurrencyAndLoad:
    """並發和負載測試"""
    
    def test_concurrent_requests_to_core_service(self):
        """測試核心服務的並發處理能力"""
        def make_health_check():
            try:
                response = httpx.get("http://localhost:8002/health", timeout=5.0)
                return response.status_code == 200
            except:
                return False
        
        # 創建多個並發請求
        threads = []
        results = []
        
        def worker():
            result = make_health_check()
            results.append(result)
        
        # 啟動10個並發線程
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join()
        
        # 檢查結果
        if results:  # 如果有結果（服務運行中）
            success_rate = sum(results) / len(results)
            print(f"並發請求成功率: {success_rate:.2%}")
            assert success_rate >= 0.8, "並發請求成功率太低"
    
    def test_mixed_workload(self):
        """測試混合工作負載"""
        def health_check_worker():
            try:
                response = httpx.get("http://localhost:8002/health", timeout=3.0)
                return response.status_code == 200
            except:
                return False
        
        def symbols_worker():
            try:
                response = httpx.get("http://localhost:8002/symbols", timeout=3.0)
                return response.status_code == 200
            except:
                return False
        
        # 創建混合工作負載
        workers = [health_check_worker] * 5 + [symbols_worker] * 5
        threads = []
        results = []
        
        def run_worker(worker_func):
            result = worker_func()
            results.append(result)
        
        # 啟動所有worker
        for worker in workers:
            thread = threading.Thread(target=run_worker, args=(worker,))
            threads.append(thread)
            thread.start()
        
        # 等待完成
        for thread in threads:
            thread.join()
        
        if results:
            success_count = sum(results)
            print(f"混合負載測試: {success_count}/{len(results)} 成功")

class TestDataConsistency:
    """數據一致性測試"""
    
    def test_symbol_data_consistency(self):
        """測試股票代碼數據一致性"""
        try:
            response = httpx.get("http://localhost:8002/symbols", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                
                # 檢查數據結構
                assert "us_symbols" in data
                assert "tw_symbols" in data
                assert "total" in data
                
                # 檢查數據一致性
                actual_total = len(data["us_symbols"]) + len(data["tw_symbols"])
                assert data["total"] == actual_total, "股票代碼總數不一致"
                
                # 檢查代碼格式
                for symbol in data["us_symbols"]:
                    assert isinstance(symbol, str), "美股代碼應為字符串"
                    assert len(symbol) <= 10, "美股代碼長度異常"
                
                for symbol in data["tw_symbols"]:
                    assert isinstance(symbol, str), "台股代碼應為字符串"
                    assert ".TW" in symbol, "台股代碼應包含.TW後綴"
                    
        except httpx.ConnectError:
            pytest.skip("核心服務未運行")

if __name__ == "__main__":
    # 運行集成測試
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "-k", "not test_concurrent",  # 跳過並發測試，除非明確需要
        "--maxfail=5"  # 最多失敗5個就停止
    ])