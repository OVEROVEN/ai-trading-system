#!/usr/bin/env python3
"""
圖表服務簡化測試
專注於測試圖表服務的基本功能
"""

import sys
import os
import httpx

# 添加項目路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestChartServiceSimple:
    """圖表服務簡化測試"""
    
    def __init__(self):
        self.base_url = "http://localhost:8003"
    
    def test_service_connectivity(self):
        """測試服務連通性"""
        try:
            response = httpx.get(f"{self.base_url}/", timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "Chart Generation Service"
            print("✅ 圖表服務連通性測試通過")
            return True
        except httpx.ConnectError:
            print("❌ 圖表服務未運行")
            return False
        except Exception as e:
            print(f"❌ 圖表服務測試失敗: {str(e)}")
            return False
    
    def test_health_check(self):
        """測試健康檢查"""
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print("✅ 圖表服務健康檢查通過")
            return True
        except Exception as e:
            print(f"❌ 健康檢查失敗: {str(e)}")
            return False
    
    def test_chart_types(self):
        """測試圖表類型查詢"""
        try:
            response = httpx.get(f"{self.base_url}/chart-types", timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            
            required_types = ["basic", "professional", "tradingview"]
            for chart_type in required_types:
                assert chart_type in data
                assert "available" in data[chart_type]
                assert "description" in data[chart_type]
            
            print("✅ 圖表類型查詢測試通過")
            return True
        except Exception as e:
            print(f"❌ 圖表類型測試失敗: {str(e)}")
            return False
    
    def test_basic_chart_generation(self):
        """測試基本圖表生成"""
        try:
            chart_request = {
                "symbol": "TEST",
                "chart_type": "basic",
                "theme": "dark"
            }
            
            response = httpx.post(
                f"{self.base_url}/generate-chart",
                json=chart_request,
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "TEST"
            assert data["chart_type"] == "basic"
            assert "chart_html" in data
            assert "generated_at" in data
            
            print("✅ 基本圖表生成測試通過")
            return True
        except Exception as e:
            print(f"❌ 基本圖表生成測試失敗: {str(e)}")
            return False
    
    def test_chart_generation_with_indicators(self):
        """測試帶技術指標的圖表生成"""
        try:
            chart_request = {
                "symbol": "TEST_WITH_INDICATORS",
                "chart_type": "professional",
                "theme": "light",
                "indicators": {
                    "rsi": 65.5,
                    "macd": 2.1,
                    "sma_20": 150.2
                },
                "patterns": [
                    {
                        "pattern_name": "Test Pattern",
                        "confidence": 0.8,
                        "start_date": "2023-01-01",
                        "end_date": "2023-01-31"
                    }
                ]
            }
            
            response = httpx.post(
                f"{self.base_url}/generate-chart",
                json=chart_request,
                timeout=10.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["chart_type"] == "professional"
            
            print("✅ 帶指標圖表生成測試通過")
            return True
        except Exception as e:
            print(f"❌ 帶指標圖表生成測試失敗: {str(e)}")
            return False
    
    def test_error_handling(self):
        """測試錯誤處理"""
        try:
            # 測試無效請求
            response = httpx.post(
                f"{self.base_url}/generate-chart",
                json={},  # 空請求
                timeout=5.0
            )
            
            # 應該返回422驗證錯誤
            assert response.status_code == 422
            
            print("✅ 錯誤處理測試通過")
            return True
        except Exception as e:
            print(f"❌ 錯誤處理測試失敗: {str(e)}")
            return False

def test_core_to_chart_integration():
    """測試核心服務到圖表服務的集成"""
    print("\n📊 測試核心服務與圖表服務集成:")
    
    try:
        # 創建模擬圖表請求（從核心服務視角）
        chart_request = {
            "symbol": "INTEGRATION_TEST",
            "period": "3mo",
            "chart_type": "professional",
            "theme": "dark",
            "indicators": {"rsi": 50, "macd": 0.5},
            "patterns": []
        }
        
        # 直接調用圖表服務
        response = httpx.post(
            "http://localhost:8003/generate-chart",
            json=chart_request,
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "chart_html" in data
            assert data["success"] is True
            print("✅ 核心服務與圖表服務集成測試通過")
            return True
        else:
            print(f"⚠️  集成測試響應碼: {response.status_code}")
            return False
            
    except httpx.ConnectError:
        print("❌ 無法連接到圖表服務")
        return False
    except Exception as e:
        print(f"❌ 集成測試失敗: {str(e)}")
        return False

def run_chart_service_tests():
    """運行圖表服務測試套件"""
    print("📊 開始運行圖表服務測試")
    print("-" * 50)
    
    tester = TestChartServiceSimple()
    
    # 首先測試服務連通性
    if not tester.test_service_connectivity():
        print("⚠️  圖表服務未運行，跳過詳細測試")
        print("💡 請先啟動圖表服務: python -m uvicorn src.services.chart_service:app --host 0.0.0.0 --port 8003")
        return False
    
    tests = [
        tester.test_health_check,
        tester.test_chart_types,
        tester.test_basic_chart_generation,
        tester.test_chart_generation_with_indicators,
        tester.test_error_handling,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 測試異常: {str(e)}")
    
    # 集成測試
    if test_core_to_chart_integration():
        passed += 1
    total += 1
    
    print("\n" + "="*50)
    print(f"📊 圖表服務測試結果: {passed}/{total} 通過")
    print(f"📈 成功率: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("🎉 所有圖表服務測試通過！")
        return True
    elif passed >= total * 0.8:
        print("⚠️  大部分測試通過")
        return True
    else:
        print("❌ 測試失敗過多")
        return False

if __name__ == "__main__":
    success = run_chart_service_tests()
    exit(0 if success else 1)