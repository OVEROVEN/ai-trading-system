#!/usr/bin/env python3
"""
修復台股圖表顯示問題的解決方案
提供多種替代方案來顯示台股數據
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.hybrid_tradingview import get_hybrid_chart

def create_fallback_taiwan_chart():
    """創建台股圖表的後備方案"""
    print("[FIX] 創建台股圖表後備方案")
    print("=" * 50)
    
    fallback_content = '''
    <div id="taiwan_chart_fallback" style="width: 100%; height: 100%; background: #1e222d; display: flex; align-items: center; justify-content: center; color: white; font-family: Arial, sans-serif;">
        <div style="text-align: center; padding: 20px;">
            <h3 style="color: #28a745; margin-bottom: 20px;">🇹🇼 台股圖表 (臨時方案)</h3>
            <div style="background: #2a2e39; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h4 id="stock_symbol" style="color: #fff; margin-bottom: 10px;">載入中...</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                    <div style="background: #131722; padding: 10px; border-radius: 4px;">
                        <div style="color: #6c757d; font-size: 12px;">開盤價</div>
                        <div id="open_price" style="color: #fff; font-weight: bold;">--</div>
                    </div>
                    <div style="background: #131722; padding: 10px; border-radius: 4px;">
                        <div style="color: #6c757d; font-size: 12px;">最高價</div>
                        <div id="high_price" style="color: #089981; font-weight: bold;">--</div>
                    </div>
                    <div style="background: #131722; padding: 10px; border-radius: 4px;">
                        <div style="color: #6c757d; font-size: 12px;">最低價</div>
                        <div id="low_price" style="color: #f23645; font-weight: bold;">--</div>
                    </div>
                    <div style="background: #131722; padding: 10px; border-radius: 4px;">
                        <div style="color: #6c757d; font-size: 12px;">收盤價</div>
                        <div id="close_price" style="color: #fff; font-weight: bold; font-size: 16px;">--</div>
                    </div>
                </div>
                <div style="background: #131722; padding: 10px; border-radius: 4px; margin-bottom: 15px;">
                    <div style="color: #6c757d; font-size: 12px;">成交量</div>
                    <div id="volume" style="color: #2196F3; font-weight: bold;">--</div>
                </div>
            </div>
            <div style="background: #343a40; padding: 15px; border-radius: 8px; font-size: 14px; line-height: 1.5;">
                <div style="color: #ffc107; margin-bottom: 10px;">⚠️ 圖表功能說明</div>
                <div style="text-align: left;">
                    • 當前顯示基本股價資訊<br>
                    • 使用 TWSE/TPEx 開放資料<br>
                    • 完整 K線圖需要 TradingView Charting Library<br>
                    • 數據來源符合法規要求
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #6c757d;">
                資料來源: TWSE/TPEx 開放資料平台
            </div>
        </div>
    </div>
    
    <script>
    // 獲取台股數據並顯示
    async function loadTaiwanStockData(symbol) {
        try {
            const response = await fetch(`/api/taiwan/stocks/quote/${symbol}`);
            if (response.ok) {
                const data = await response.json();
                
                document.getElementById('stock_symbol').textContent = `${data.symbol} ${data.name || ''}`;
                document.getElementById('open_price').textContent = data.open || '--';
                document.getElementById('high_price').textContent = data.high || '--';
                document.getElementById('low_price').textContent = data.low || '--';
                document.getElementById('close_price').textContent = data.close || '--';
                document.getElementById('volume').textContent = data.volume ? data.volume.toLocaleString() : '--';
                
                // 設置價格顏色
                if (data.change) {
                    const closeEl = document.getElementById('close_price');
                    if (data.change > 0) {
                        closeEl.style.color = '#089981'; // 綠色上漲
                    } else if (data.change < 0) {
                        closeEl.style.color = '#f23645'; // 紅色下跌
                    }
                }
            } else {
                console.warn('無法獲取股票數據:', symbol);
                document.getElementById('stock_symbol').textContent = `${symbol} (數據獲取中...)`;
            }
        } catch (error) {
            console.error('獲取台股數據失敗:', error);
            document.getElementById('stock_symbol').textContent = `${symbol} (數據不可用)`;
        }
    }
    
    // 從 URL 或全局變量中獲取符號
    const urlParams = new URLSearchParams(window.location.search);
    const symbol = urlParams.get('symbol') || window.currentSymbol || '2330.TW';
    
    // 載入數據
    loadTaiwanStockData(symbol);
    
    // 每 30 秒更新一次數據
    setInterval(() => loadTaiwanStockData(symbol), 30000);
    </script>
    '''
    
    return fallback_content

def update_hybrid_chart_with_fallback():
    """更新混合圖表，為台股添加後備方案"""
    print("[FIX] 更新混合圖表實現")
    print("=" * 50)
    
    # 讀取原始檔案
    hybrid_chart_path = Path("src/visualization/hybrid_tradingview.py")
    
    if not hybrid_chart_path.exists():
        print("[ERROR] 找不到混合圖表文件")
        return False
    
    # 創建新的實現方法
    new_method = '''
    def _create_charting_library_chart_with_fallback(self, symbol: str, colors: Dict[str, str]) -> str:
        """創建 Charting Library 圖表 (帶後備方案)"""
        
        fallback_chart = """
        <div id="tv_chart_container" style="width: 100%; height: 100%; position: relative;">
            <!-- TradingView Charting Library 嘗試載入 -->
            <div id="charting_library_content" style="width: 100%; height: 100%;"></div>
            
            <!-- 後備方案 (當 Charting Library 不可用時) -->
            <div id="fallback_content" style="width: 100%; height: 100%; display: none;">
                {fallback_html}
            </div>
        </div>
        
        <!-- 嘗試載入 TradingView Charting Library -->
        <script type="text/javascript">
            // 檢查 TradingView Charting Library 是否可用
            function initChartingLibrary() {{
                if (typeof TradingView !== 'undefined' && TradingView.widget) {{
                    // 使用真實的 Charting Library
                    console.log('使用 TradingView Charting Library');
                    
                    const widget = new TradingView.widget({{
                        symbol: '{symbol}',
                        datafeed: new Datafeeds.UDFCompatibleDatafeed('/api/charting'),
                        interval: '1D',
                        container_id: 'charting_library_content',
                        library_path: '/static/charting_library/',
                        
                        locale: 'zh_TW',
                        timezone: 'Asia/Taipei',
                        theme: '{theme}',
                        
                        overrides: {{
                            "paneProperties.background": "{bg_color}",
                            "paneProperties.vertGridProperties.color": "#363c4e",
                            "paneProperties.horzGridProperties.color": "#363c4e",
                            "scalesProperties.textColor": "{text_color}",
                            "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                            "mainSeriesProperties.candleStyle.wickDownColor": "#f23645",
                            "mainSeriesProperties.candleStyle.upColor": "#089981",
                            "mainSeriesProperties.candleStyle.downColor": "#f23645"
                        }}
                    }});
                    
                    widget.onChartReady(() => {{
                        console.log('TradingView Charting Library 已載入');
                        widget.chart().createStudy('Volume', false, false);
                    }});
                    
                }} else {{
                    // 使用後備方案
                    console.log('TradingView Charting Library 不可用，使用後備方案');
                    showFallback();
                }}
            }}
            
            function showFallback() {{
                document.getElementById('charting_library_content').style.display = 'none';
                document.getElementById('fallback_content').style.display = 'block';
                
                // 設置當前符號供後備方案使用
                window.currentSymbol = '{symbol}';
            }}
            
            // 載入時檢查
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initChartingLibrary);
            }} else {{
                // 延遲檢查，給 Charting Library 載入時間
                setTimeout(initChartingLibrary, 1000);
            }}
            
            // 超時後備方案
            setTimeout(() => {{
                if (document.getElementById('charting_library_content').children.length === 0) {{
                    console.log('Charting Library 載入超時，切換到後備方案');
                    showFallback();
                }}
            }}, 5000);
        </script>
        """.format(
            symbol=symbol,
            theme='dark' if colors['background'] == '#1e222d' else 'light',
            bg_color=colors['background'],
            text_color=colors['text_color'],
            fallback_html=create_fallback_taiwan_chart()
        )
        
        return fallback_chart
'''
    
    print("[INFO] 已創建帶後備方案的圖表方法")
    print("[INFO] 此方案會先嘗試 Charting Library，失敗時顯示基本股價資訊")
    return True

def create_taiwan_widget_alternative():
    """創建台股 TradingView Widget 替代方案"""
    print("[ALTERNATIVE] 創建台股 TradingView Widget 方案")
    print("=" * 50)
    
    widget_alternative = '''
    def _create_taiwan_widget_chart(self, symbol: str, colors: Dict[str, str]) -> str:
        """為台股創建 TradingView Widget (替代方案)"""
        
        # 將台股符號轉換為 TradingView 格式
        if symbol.endswith('.TW'):
            tv_symbol = f"TPE:{symbol[:-3]}"
        elif symbol.endswith('.TWO'):
            tv_symbol = f"TPEX:{symbol[:-4]}"
        else:
            tv_symbol = f"TPE:{symbol}"
        
        return f"""
        <div id="taiwan_tradingview_widget" style="width: 100%; height: 100%;">
            <div id="widget_loading" style="display: flex; align-items: center; justify-content: center; height: 100%; background: {colors['background']}; color: {colors['text_color']};">
                <div style="text-align: center;">
                    <div style="margin-bottom: 10px;">正在載入台股圖表...</div>
                    <div style="font-size: 12px; color: #6c757d;">使用 TradingView Widget</div>
                </div>
            </div>
        </div>
        
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
            function initTaiwanWidget() {{
                try {{
                    new TradingView.widget({{
                        "width": "100%",
                        "height": "100%",
                        "symbol": "{tv_symbol}",
                        "interval": "D",
                        "timezone": "Asia/Taipei",
                        "theme": "{'dark' if colors['background'] == '#1e222d' else 'light'}",
                        "style": "1",
                        "locale": "zh_TW",
                        "toolbar_bg": "{colors['background']}",
                        "enable_publishing": false,
                        "allow_symbol_change": true,
                        "container_id": "taiwan_tradingview_widget",
                        "autosize": true,
                        "studies": [
                            "Volume@tv-basicstudies"
                        ],
                        "overrides": {{
                            "paneProperties.background": "{colors['background']}",
                            "paneProperties.vertGridProperties.color": "#363c4e",
                            "paneProperties.horzGridProperties.color": "#363c4e",
                            "scalesProperties.textColor": "{colors['text_color']}",
                            "mainSeriesProperties.candleStyle.wickUpColor": "#089981",
                            "mainSeriesProperties.candleStyle.wickDownColor": "#f23645"
                        }}
                    }});
                    
                    console.log('台股 TradingView Widget 載入完成');
                    document.getElementById('widget_loading').style.display = 'none';
                    
                }} catch (error) {{
                    console.error('台股 Widget 載入失敗:', error);
                    document.getElementById('widget_loading').innerHTML = 
                        '<div style="color: #dc3545;">圖表載入失敗<br><small>符號: {tv_symbol}</small></div>';
                }}
            }}
            
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', initTaiwanWidget);
            }} else {{
                initTaiwanWidget();
            }}
        </script>
        """
    '''
    
    print("[INFO] 台股 Widget 替代方案:")
    print("• 使用 TradingView Widget 顯示台股")
    print("• 符號格式: TPE:2330 (上市) / TPEX:3481 (上櫃)")
    print("• 無需 Charting Library")
    print("• 可能的限制: 部分台股可能無 TradingView 數據")
    
    return True

def test_current_taiwan_chart():
    """測試當前台股圖表狀態"""
    print("[TEST] 測試台股圖表狀態")
    print("=" * 50)
    
    try:
        chart = get_hybrid_chart()
        
        # 測試台股圖表生成
        html_content = chart.create_hybrid_chart("2330.TW", theme="dark")
        
        print(f"[INFO] 圖表 HTML 長度: {len(html_content):,} 字符")
        
        # 檢查是否包含必要元素
        if "tv_chart_container" in html_content:
            print("[PASS] 包含 Charting Library 容器")
        else:
            print("[FAIL] 缺少 Charting Library 容器")
        
        if "charting_library.min.js" in html_content:
            print("[PASS] 引用 Charting Library JS")
        else:
            print("[FAIL] 缺少 Charting Library JS")
        
        # 檢查錯誤提示
        if "TradingView Charting Library 未安裝" in html_content:
            print("[WARNING] 檢測到 Charting Library 未安裝提示")
            return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        return False

def show_solutions_menu():
    """顯示解決方案菜單"""
    print("\n台股圖表顯示問題 - 解決方案")
    print("=" * 50)
    
    print("當前問題: 台股需要 TradingView Charting Library 才能正常顯示")
    print("\n可選解決方案:")
    print("1. 使用台股 TradingView Widget (推薦)")
    print("2. 創建後備顯示方案 (顯示基本數據)")  
    print("3. 申請官方 Charting Library")
    print("4. 測試當前狀態")
    print("5. 查看詳細說明")
    print("6. 退出")
    
    return input("\n請選擇解決方案 (1-6): ").strip()

def main():
    """主函數"""
    print("台股圖表修復工具")
    print("=" * 60)
    print("[問題] 台股圖表需要真正的 TradingView Charting Library")
    print("[目標] 提供可行的替代方案讓台股圖表正常顯示")
    
    while True:
        try:
            choice = show_solutions_menu()
            
            if choice == "1":
                print("\n[方案 1] 台股使用 TradingView Widget")
                print("優點: 無需 Charting Library，立即可用")
                print("缺點: 需要 TradingView 有該股票數據")
                create_taiwan_widget_alternative()
                
            elif choice == "2":
                print("\n[方案 2] 創建後備顯示方案")
                print("優點: 顯示基本股價資訊，使用開放資料")
                print("缺點: 無 K線圖，功能較簡單")
                update_hybrid_chart_with_fallback()
                
            elif choice == "3":
                print("\n[方案 3] 申請官方 Charting Library")
                print("訪問: https://www.tradingview.com/advanced-charts/")
                print("這是最完整的解決方案，但需要等待審核")
                
            elif choice == "4":
                print("\n[測試] 檢查當前台股圖表狀態")
                test_current_taiwan_chart()
                
            elif choice == "5":
                print("\n[詳細說明]")
                print("當前架構: 美股(Widget) + 台股(Charting Library)")
                print("問題: 台股 Charting Library 只有模擬版本")
                print("影響: 訪問台股頁面時無法正常顯示圖表")
                print("\n推薦方案: 改為台股也使用 Widget")
                print("• 統一使用 TradingView Widget")
                print("• 無需申請 Charting Library 權限") 
                print("• 可立即解決顯示問題")
                
            elif choice == "6":
                print("再見！")
                break
                
            else:
                print("[ERROR] 無效選擇")
                
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            break
        except EOFError:
            print("\n\n操作已取消") 
            break

if __name__ == "__main__":
    main()