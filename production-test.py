#!/usr/bin/env python3
"""
生產環境測試腳本
模擬生產部署環境的完整測試
"""

import httpx
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import json

class ProductionEnvironmentTester:
    """生產環境測試器"""
    
    def __init__(self):
        # 本地微服務配置 (模擬生產環境)
        self.core_service = "http://localhost:8002"
        self.chart_service = "http://localhost:8003"
        
        # Railway生產URL (當可用時)
        self.production_urls = {
            "core": "https://auto-trade-production.up.railway.app",
            "chart": "https://chart-service-production.up.railway.app"
        }
        
        self.test_results = {}
    
    def test_service_health(self):
        """測試服務健康狀態"""
        print("🏥 測試服務健康狀態:")
        
        services = {
            "核心服務": f"{self.core_service}/health",
            "圖表服務": f"{self.chart_service}/health"
        }
        
        healthy_services = 0
        for name, url in services.items():
            try:
                start_time = time.time()
                response = httpx.get(url, timeout=5.0)
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {name}: 健康 ({end_time-start_time:.3f}s)")
                    if name == "核心服務":
                        deps = data.get("dependencies", {})
                        for dep, status in deps.items():
                            print(f"    - {dep}: {status}")
                    elif name == "圖表服務":
                        gens = data.get("generators_status", {})
                        available_count = sum(1 for status in gens.values() if status == "available")
                        print(f"    - 圖表生成器: {available_count}/{len(gens)} 可用")
                    healthy_services += 1
                else:
                    print(f"  ❌ {name}: 狀態碼 {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {name}: {str(e)}")
        
        return healthy_services == len(services)
    
    def test_data_consistency(self):
        """測試數據一致性"""
        print("\n📊 測試數據一致性:")
        
        try:
            response = httpx.get(f"{self.core_service}/symbols", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                
                # 驗證數據結構完整性
                required_keys = ["us_symbols", "tw_symbols", "total"]
                for key in required_keys:
                    if key not in data:
                        print(f"  ❌ 缺少必需字段: {key}")
                        return False
                
                # 驗證數據邏輯一致性
                actual_total = len(data["us_symbols"]) + len(data["tw_symbols"])
                if data["total"] != actual_total:
                    print(f"  ❌ 數據總數不一致: 聲稱{data['total']}, 實際{actual_total}")
                    return False
                
                print(f"  ✅ 數據一致性驗證通過")
                print(f"    - 美股: {len(data['us_symbols'])} 個")
                print(f"    - 台股: {len(data['tw_symbols'])} 個")
                print(f"    - 總計: {data['total']} 個")
                return True
                
        except Exception as e:
            print(f"  ❌ 數據一致性測試失敗: {str(e)}")
            return False
    
    def test_service_integration(self):
        """測試服務間集成"""
        print("\n🔄 測試服務間集成:")
        
        try:
            # 測試圖表生成請求
            chart_request = {
                "symbol": "INTEGRATION_TEST",
                "chart_type": "professional",
                "theme": "dark",
                "indicators": {
                    "rsi": 65.2,
                    "macd": 1.8,
                    "sma_20": 150.5
                },
                "patterns": [
                    {"pattern_name": "Production Test Pattern", "confidence": 0.85}
                ]
            }
            
            response = httpx.post(
                f"{self.chart_service}/generate-chart",
                json=chart_request,
                timeout=15.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"  ✅ 圖表生成成功")
                    print(f"    - 符號: {data.get('symbol')}")
                    print(f"    - 類型: {data.get('chart_type')}")
                    print(f"    - HTML長度: {len(data.get('chart_html', ''))} 字符")
                    return True
                else:
                    print(f"  ❌ 圖表生成失敗: {data.get('error', '未知錯誤')}")
            else:
                print(f"  ❌ 圖表服務響應異常: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 服務集成測試失敗: {str(e)}")
            
        return False
    
    def test_performance_under_load(self):
        """測試負載下的性能"""
        print("\n⚡ 測試負載性能:")
        
        def make_concurrent_request(endpoint, request_id):
            try:
                start_time = time.time()
                response = httpx.get(endpoint, timeout=10.0)
                end_time = time.time()
                
                return {
                    'id': request_id,
                    'success': response.status_code == 200,
                    'response_time': end_time - start_time,
                    'endpoint': endpoint
                }
            except Exception:
                return {
                    'id': request_id,
                    'success': False,
                    'response_time': None,
                    'endpoint': endpoint
                }
        
        # 創建並發請求
        endpoints = [
            f"{self.core_service}/health",
            f"{self.core_service}/symbols",
            f"{self.chart_service}/health"
        ]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            # 每個端點發送5個並發請求
            for endpoint in endpoints:
                for i in range(5):
                    futures.append(
                        executor.submit(make_concurrent_request, endpoint, f"{endpoint.split('/')[-1]}_{i}")
                    )
            
            results = [future.result() for future in futures]
        
        # 分析結果
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        if successful:
            avg_response_time = sum(r['response_time'] for r in successful) / len(successful)
            max_response_time = max(r['response_time'] for r in successful)
            min_response_time = min(r['response_time'] for r in successful)
            
            print(f"  📊 負載測試結果:")
            print(f"    - 成功請求: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
            print(f"    - 平均響應時間: {avg_response_time:.3f}s")
            print(f"    - 最快響應: {min_response_time:.3f}s")
            print(f"    - 最慢響應: {max_response_time:.3f}s")
            
            # 性能標準: 成功率>80%, 平均響應時間<1s
            performance_good = len(successful)/len(results) >= 0.8 and avg_response_time < 1.0
            
            if performance_good:
                print(f"  ✅ 負載性能良好")
                return True
            else:
                print(f"  ⚠️  負載性能需要優化")
                return False
        else:
            print(f"  ❌ 所有負載測試請求都失敗")
            return False
    
    def test_error_handling(self):
        """測試錯誤處理機制"""
        print("\n🚨 測試錯誤處理:")
        
        test_cases = [
            {
                "name": "無效圖表請求",
                "url": f"{self.chart_service}/generate-chart",
                "method": "POST",
                "data": {"invalid": "request"},
                "expected_status": 422
            },
            {
                "name": "不存在的端點",
                "url": f"{self.core_service}/nonexistent",
                "method": "GET",
                "expected_status": 404
            }
        ]
        
        passed_tests = 0
        for test_case in test_cases:
            try:
                if test_case["method"] == "POST":
                    response = httpx.post(
                        test_case["url"],
                        json=test_case.get("data", {}),
                        timeout=5.0
                    )
                else:
                    response = httpx.get(test_case["url"], timeout=5.0)
                
                if response.status_code == test_case["expected_status"]:
                    print(f"  ✅ {test_case['name']}: 正確處理 ({response.status_code})")
                    passed_tests += 1
                else:
                    print(f"  ❌ {test_case['name']}: 預期{test_case['expected_status']}, 實際{response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {test_case['name']}: 異常 - {str(e)}")
        
        return passed_tests == len(test_cases)
    
    def test_production_readiness(self):
        """測試生產就緒性"""
        print("\n🚀 測試生產就緒性:")
        
        readiness_checks = [
            ("服務健康", self.test_service_health),
            ("數據一致性", self.test_data_consistency), 
            ("服務集成", self.test_service_integration),
            ("負載性能", self.test_performance_under_load),
            ("錯誤處理", self.test_error_handling)
        ]
        
        passed_checks = 0
        total_checks = len(readiness_checks)
        
        for check_name, check_func in readiness_checks:
            try:
                if check_func():
                    self.test_results[check_name] = "通過"
                    passed_checks += 1
                else:
                    self.test_results[check_name] = "失敗"
            except Exception as e:
                self.test_results[check_name] = f"異常: {str(e)}"
                print(f"  ❌ {check_name} 檢查異常: {str(e)}")
        
        return passed_checks, total_checks
    
    def generate_production_report(self):
        """生成生產就緒報告"""
        passed, total = self.test_production_readiness()
        
        print("\n" + "="*80)
        print("🎯 生產環境就緒性評估報告")
        print("="*80)
        
        print(f"\n📊 總體統計:")
        print(f"  - 檢查項目: {total}")
        print(f"  - 通過項目: {passed}")
        print(f"  - 失敗項目: {total - passed}")
        print(f"  - 就緒度: {(passed/total*100):.1f}%")
        
        print(f"\n📋 詳細結果:")
        for check_name, result in self.test_results.items():
            status_icon = "✅" if result == "通過" else "❌"
            print(f"  {status_icon} {check_name}: {result}")
        
        print(f"\n🎯 部署建議:")
        if passed == total:
            print("  🎉 所有檢查通過！系統已準備好生產部署")
            print("  🚀 建議: 立即部署到Railway雲平台")
            print("  📋 下一步: 配置生產環境變數和域名")
        elif passed >= total * 0.8:
            print("  ✅ 大部分檢查通過，基本滿足生產要求")
            print("  ⚠️  建議: 修復失敗項目後部署")
            print("  🔧 優先處理性能和錯誤處理問題")
        else:
            print("  ❌ 多項檢查失敗，需要重大修復")
            print("  🛠️  建議: 解決所有失敗項目後重新測試")
            print("  ⏰ 推遲生產部署直到問題解決")
        
        print(f"\n🏗️  微服務架構優勢:")
        print("  ✨ 獨立部署 - 核心服務和圖表服務可分別部署")
        print("  🛡️  故障隔離 - 單個服務故障不影響整體")
        print("  📈 可擴展性 - 可根據需求獨立擴展服務")
        print("  🔧 維護便利 - 可獨立更新和維護各服務")
        
        return passed >= total * 0.8

def main():
    """主函數"""
    print("🌐 AI交易系統 - 生產環境就緒性測試")
    print("="*80)
    
    tester = ProductionEnvironmentTester()
    
    # 運行完整的生產就緒性測試
    is_ready = tester.generate_production_report()
    
    if is_ready:
        print(f"\n✅ 系統已準備好進行生產部署！")
        return 0
    else:
        print(f"\n❌ 系統尚未準備好生產部署，請修復問題後重試。")
        return 1

if __name__ == "__main__":
    exit(main())