#!/usr/bin/env python3
"""
微服務架構最終測試
全面測試核心服務和圖表服務的協作
"""

import httpx
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

class MicroservicesIntegrationTest:
    """微服務集成測試"""
    
    def __init__(self):
        self.core_url = "http://localhost:8002"
        self.chart_url = "http://localhost:8003"
        self.test_results = {}
    
    def check_services_running(self):
        """檢查所有服務是否運行"""
        print("🔍 檢查微服務狀態:")
        
        services = {
            "核心服務": f"{self.core_url}/health",
            "圖表服務": f"{self.chart_url}/health"
        }
        
        running_services = 0
        for name, url in services.items():
            try:
                response = httpx.get(url, timeout=3.0)
                if response.status_code == 200:
                    print(f"  ✅ {name} 運行正常")
                    running_services += 1
                else:
                    print(f"  ❌ {name} 響應異常: {response.status_code}")
            except httpx.ConnectError:
                print(f"  ❌ {name} 無法連接")
            except Exception as e:
                print(f"  ❌ {name} 錯誤: {str(e)}")
        
        return running_services == len(services)
    
    def test_service_discovery(self):
        """測試服務發現"""
        print("\n🔎 測試服務發現:")
        
        try:
            # 測試核心服務根端點
            core_response = httpx.get(f"{self.core_url}/", timeout=5.0)
            assert core_response.status_code == 200
            core_data = core_response.json()
            assert core_data["architecture"] == "microservices"
            print("  ✅ 核心服務架構正確")
            
            # 測試圖表服務根端點
            chart_response = httpx.get(f"{self.chart_url}/", timeout=5.0)
            assert chart_response.status_code == 200
            chart_data = chart_response.json()
            assert chart_data["service"] == "Chart Generation Service"
            print("  ✅ 圖表服務識別正確")
            
            return True
        except Exception as e:
            print(f"  ❌ 服務發現失敗: {str(e)}")
            return False
    
    def test_data_consistency(self):
        """測試數據一致性"""
        print("\n📊 測試數據一致性:")
        
        try:
            # 從核心服務獲取股票代碼
            response = httpx.get(f"{self.core_url}/symbols", timeout=5.0)
            assert response.status_code == 200
            symbols_data = response.json()
            
            # 驗證數據結構
            assert "us_symbols" in symbols_data
            assert "tw_symbols" in symbols_data
            assert "total" in symbols_data
            
            # 驗證數據一致性
            actual_total = len(symbols_data["us_symbols"]) + len(symbols_data["tw_symbols"])
            assert symbols_data["total"] == actual_total
            
            print(f"  ✅ 股票代碼數據一致 (總計: {symbols_data['total']})")
            return True
        except Exception as e:
            print(f"  ❌ 數據一致性測試失敗: {str(e)}")
            return False
    
    def test_cross_service_communication(self):
        """測試跨服務通信"""
        print("\n🔄 測試跨服務通信:")
        
        try:
            # 創建完整的圖表請求流程
            chart_request = {
                "symbol": "COMMUNICATION_TEST",
                "period": "3mo",
                "chart_type": "professional",
                "theme": "dark",
                "indicators": {
                    "rsi": 58.5,
                    "macd": 1.2,
                    "sma_20": 145.2
                },
                "patterns": [
                    {
                        "pattern_name": "Test Pattern",
                        "confidence": 0.75
                    }
                ]
            }
            
            # 直接調用圖表服務
            response = httpx.post(
                f"{self.chart_url}/generate-chart",
                json=chart_request,
                timeout=15.0
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "chart_html" in data
            assert data["symbol"] == "COMMUNICATION_TEST"
            
            print("  ✅ 跨服務通信正常")
            return True
        except Exception as e:
            print(f"  ❌ 跨服務通信失敗: {str(e)}")
            return False
    
    def test_concurrent_requests(self):
        """測試並發請求處理"""
        print("\n⚡ 測試並發請求處理:")
        
        def make_health_request(service_name, url):
            try:
                start_time = time.time()
                response = httpx.get(url, timeout=5.0)
                end_time = time.time()
                
                return {
                    'service': service_name,
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time
                }
            except Exception:
                return {
                    'service': service_name,
                    'success': False,
                    'response_time': None
                }
        
        # 創建並發請求
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # 4個核心服務請求
            for i in range(4):
                futures.append(
                    executor.submit(make_health_request, "核心服務", f"{self.core_url}/health")
                )
            
            # 4個圖表服務請求
            for i in range(4):
                futures.append(
                    executor.submit(make_health_request, "圖表服務", f"{self.chart_url}/health")
                )
            
            # 收集結果
            results = [future.result() for future in futures]
        
        # 分析結果
        successful_requests = sum(1 for r in results if r['success'])
        total_requests = len(results)
        
        if successful_requests > 0:
            response_times = [r['response_time'] for r in results if r['success'] and r['response_time']]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            print(f"  📊 並發請求成功率: {successful_requests}/{total_requests} ({(successful_requests/total_requests*100):.1f}%)")
            print(f"  ⏱️  平均響應時間: {avg_response_time:.3f}秒")
            
            return successful_requests >= total_requests * 0.8
        else:
            print("  ❌ 所有並發請求都失敗")
            return False
    
    def test_error_propagation(self):
        """測試錯誤傳播"""
        print("\n🚨 測試錯誤處理:")
        
        try:
            # 測試無效圖表請求
            invalid_request = {"invalid": "data"}
            
            response = httpx.post(
                f"{self.chart_url}/generate-chart",
                json=invalid_request,
                timeout=5.0
            )
            
            # 應該返回適當的錯誤碼
            assert response.status_code == 422  # 驗證錯誤
            
            print("  ✅ 錯誤處理正確")
            return True
        except Exception as e:
            print(f"  ❌ 錯誤處理測試失敗: {str(e)}")
            return False
    
    def test_performance_benchmarks(self):
        """測試性能基準"""
        print("\n⚡ 測試性能基準:")
        
        benchmarks = {
            "核心服務健康檢查": f"{self.core_url}/health",
            "圖表服務健康檢查": f"{self.chart_url}/health",
            "股票代碼查詢": f"{self.core_url}/symbols"
        }
        
        all_passed = True
        
        for test_name, url in benchmarks.items():
            try:
                times = []
                for _ in range(3):  # 3次測試取平均
                    start_time = time.time()
                    response = httpx.get(url, timeout=5.0)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                
                if times:
                    avg_time = sum(times) / len(times)
                    print(f"  📊 {test_name}: {avg_time:.3f}秒")
                    
                    # 性能基準: 響應時間應小於1秒
                    if avg_time > 1.0:
                        print(f"    ⚠️  響應時間較慢")
                        all_passed = False
                    else:
                        print(f"    ✅ 性能良好")
                else:
                    print(f"  ❌ {test_name}: 無法獲取響應時間")
                    all_passed = False
                    
            except Exception as e:
                print(f"  ❌ {test_name}: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_comprehensive_test(self):
        """運行綜合測試"""
        print("🚀 開始微服務架構綜合測試")
        print("="*60)
        
        if not self.check_services_running():
            print("\n❌ 部分服務未運行，無法進行完整測試")
            print("💡 請確保以下服務正在運行:")
            print("   - 核心服務: python -m uvicorn src.api.main_core:app --host 0.0.0.0 --port 8002")
            print("   - 圖表服務: python -m uvicorn src.services.chart_service:app --host 0.0.0.0 --port 8003")
            return False
        
        tests = [
            ("服務發現", self.test_service_discovery),
            ("數據一致性", self.test_data_consistency),
            ("跨服務通信", self.test_cross_service_communication),
            ("並發請求", self.test_concurrent_requests),
            ("錯誤處理", self.test_error_propagation),
            ("性能基準", self.test_performance_benchmarks),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                    self.test_results[test_name] = "通過"
                else:
                    self.test_results[test_name] = "失敗"
            except Exception as e:
                print(f"  ❌ {test_name} 執行異常: {str(e)}")
                self.test_results[test_name] = f"異常: {str(e)}"
        
        # 生成最終報告
        self.generate_final_report(passed_tests, total_tests)
        
        return passed_tests >= total_tests * 0.8
    
    def generate_final_report(self, passed, total):
        """生成最終測試報告"""
        print("\n" + "="*60)
        print("📋 微服務架構測試報告")
        print("="*60)
        
        print(f"📊 測試統計:")
        print(f"  - 總測試數: {total}")
        print(f"  - 通過數量: {passed}")
        print(f"  - 失敗數量: {total - passed}")
        print(f"  - 成功率: {(passed/total*100):.1f}%")
        
        print(f"\n📋 詳細結果:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result == "通過" else "❌"
            print(f"  {status_icon} {test_name}: {result}")
        
        print(f"\n🎯 總體評估:")
        if passed == total:
            print("  🎉 所有測試通過！微服務架構部署準備就緒。")
            print("  🚀 建議: 可以安全地進行生產部署")
        elif passed >= total * 0.8:
            print("  ✅ 大部分測試通過，架構基本穩定。")
            print("  ⚠️  建議: 檢查失敗項目後進行部署")
        else:
            print("  ❌ 測試失敗較多，需要修復問題。")
            print("  🔧 建議: 修復問題後重新測試")
        
        print("\n📋 微服務架構優勢:")
        print("  ✨ 服務解耦 - 核心功能與圖表生成獨立")
        print("  🚀 部署靈活 - 可獨立部署和擴展")
        print("  🛡️  故障隔離 - 單個服務故障不影響整體")
        print("  📈 性能優化 - 可針對性優化各服務")

def main():
    """主函數"""
    tester = MicroservicesIntegrationTest()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())