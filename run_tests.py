#!/usr/bin/env python3
"""
微服務測試執行器
運行完整的測試套件並生成報告
"""

import subprocess
import sys
import time
import os
from pathlib import Path

class TestRunner:
    """測試運行器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
    
    def print_header(self, title: str):
        """打印測試標題"""
        print("\n" + "="*60)
        print(f"🧪 {title}")
        print("="*60)
    
    def run_command(self, cmd: list, test_name: str) -> bool:
        """執行測試命令"""
        try:
            print(f"執行: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2分鐘超時
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            self.test_results[test_name] = {
                'success': success,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if success:
                print(f"✅ {test_name} 通過 ({duration:.2f}秒)")
            else:
                print(f"❌ {test_name} 失敗 ({duration:.2f}秒)")
                print("錯誤輸出:")
                print(result.stderr)
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} 超時")
            self.test_results[test_name] = {
                'success': False,
                'duration': 120,
                'error': 'timeout'
            }
            return False
        except Exception as e:
            print(f"🔥 {test_name} 執行異常: {str(e)}")
            self.test_results[test_name] = {
                'success': False,
                'duration': 0,
                'error': str(e)
            }
            return False
    
    def check_dependencies(self):
        """檢查測試依賴"""
        self.print_header("檢查測試環境")
        
        # 檢查pytest
        try:
            subprocess.run(['pytest', '--version'], capture_output=True, check=True)
            print("✅ pytest 可用")
        except:
            print("❌ pytest 不可用，請安裝: pip install pytest")
            return False
        
        # 檢查httpx
        try:
            import httpx
            print("✅ httpx 可用")
        except ImportError:
            print("❌ httpx 不可用，請安裝: pip install httpx")
            return False
        
        # 檢查核心服務是否運行
        try:
            import httpx
            response = httpx.get("http://localhost:8002/health", timeout=2.0)
            if response.status_code == 200:
                print("✅ 核心服務運行中 (localhost:8002)")
            else:
                print(f"⚠️  核心服務響應異常: {response.status_code}")
        except:
            print("⚠️  核心服務未運行，部分集成測試將跳過")
        
        return True
    
    def run_unit_tests(self):
        """運行單元測試"""
        self.print_header("單元測試")
        
        test_files = [
            ("tests/test_core_service.py", "核心服務單元測試"),
            ("tests/test_chart_service.py", "圖表服務單元測試"),
        ]
        
        success_count = 0
        for test_file, test_name in test_files:
            if os.path.exists(test_file):
                cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short']
                if self.run_command(cmd, test_name):
                    success_count += 1
            else:
                print(f"⚠️  測試文件不存在: {test_file}")
        
        print(f"\n📊 單元測試結果: {success_count}/{len(test_files)} 通過")
        return success_count == len(test_files)
    
    def run_integration_tests(self):
        """運行集成測試"""
        self.print_header("集成測試")
        
        cmd = ['python', '-m', 'pytest', 'tests/test_microservices_integration.py', '-v']
        success = self.run_command(cmd, "微服務集成測試")
        
        if success:
            print("✅ 所有集成測試通過")
        else:
            print("⚠️  部分集成測試失敗（可能因為服務未運行）")
        
        return success
    
    def run_performance_tests(self):
        """運行性能測試"""
        self.print_header("性能測試")
        
        # 簡單的健康檢查響應時間測試
        try:
            import httpx
            import time
            
            response_times = []
            for i in range(5):
                start = time.time()
                response = httpx.get("http://localhost:8002/health", timeout=5.0)
                end = time.time()
                
                if response.status_code == 200:
                    response_times.append(end - start)
                    
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                print(f"📊 核心服務響應時間: 平均 {avg_time:.3f}秒, 最大 {max_time:.3f}秒")
                
                # 判斷性能是否合格
                if avg_time < 1.0 and max_time < 2.0:
                    print("✅ 性能測試通過")
                    return True
                else:
                    print("⚠️  響應時間較慢")
                    return False
            else:
                print("⚠️  無法連接到核心服務")
                return False
                
        except Exception as e:
            print(f"⚠️  性能測試失敗: {str(e)}")
            return False
    
    def generate_report(self):
        """生成測試報告"""
        self.print_header("測試報告")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        
        print(f"📊 總測試數: {total_tests}")
        print(f"✅ 成功: {successful_tests}")
        print(f"❌ 失敗: {total_tests - successful_tests}")
        print(f"📈 成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # 詳細結果
        print("\n📋 詳細結果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通過" if result['success'] else "❌ 失敗"
            duration = result.get('duration', 0)
            print(f"  {status} {test_name} ({duration:.2f}秒)")
        
        # 推薦
        print("\n🎯 建議:")
        if successful_tests == total_tests:
            print("  🎉 所有測試通過！可以進行生產部署。")
        elif successful_tests / total_tests >= 0.8:
            print("  ⚠️  大部分測試通過，檢查失敗項目後可考慮部署。")
        else:
            print("  🚨 測試失敗過多，建議修復問題後再次測試。")
    
    def run_all_tests(self):
        """運行所有測試"""
        print("🚀 開始微服務測試套件")
        
        if not self.check_dependencies():
            print("❌ 測試環境檢查失敗")
            return False
        
        # 按順序執行測試
        self.run_unit_tests()
        self.run_integration_tests()
        self.run_performance_tests()
        
        # 生成報告
        self.generate_report()
        
        # 返回整體成功狀態
        success_count = sum(1 for result in self.test_results.values() if result['success'])
        return success_count >= len(self.test_results) * 0.8  # 80%通過即認為成功

def main():
    """主函數"""
    runner = TestRunner()
    
    # 改變工作目錄到項目根目錄
    os.chdir(runner.project_root)
    
    # 運行測試
    success = runner.run_all_tests()
    
    # 退出碼
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()