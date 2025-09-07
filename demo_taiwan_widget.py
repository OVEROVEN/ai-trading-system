#!/usr/bin/env python3
"""
台股TradingView Widget完整演示
展示增強版台股Widget的所有功能和使用方式
"""

import asyncio
import sys
import os
import webbrowser
import time
from pathlib import Path

# 添加src目錄到路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.visualization.enhanced_taiwan_widget import get_enhanced_taiwan_widget

def create_demo_charts():
    """創建演示圖表"""
    print("創建台股TradingView Widget演示圖表...")
    
    widget = get_enhanced_taiwan_widget()
    
    # 創建演示目錄
    demo_dir = "demo_charts"
    os.makedirs(demo_dir, exist_ok=True)
    
    # 熱門台股列表
    popular_stocks = [
        ("2330", "台積電", "半導體龍頭"),
        ("2454", "聯發科", "IC設計龍頭"),
        ("2881", "富邦金", "金融龍頭"),
        ("2603", "長榮", "航運龍頭"),
        ("0050", "台灣50", "市值型ETF"),
        ("0056", "高股息", "股息型ETF"),
        ("2412", "中華電", "電信龍頭"),
        ("2317", "鴻海", "電子代工"),
    ]
    
    # 為每個股票創建圖表
    created_files = []
    
    for symbol, name, description in popular_stocks:
        try:
            print(f"創建 {symbol} ({name}) 圖表...")
            
            # 創建深色主題圖表
            html_content = widget.create_enhanced_widget(
                symbol=symbol,
                theme="dark",
                additional_studies=[
                    "MACD@tv-basicstudies",
                    "MA@tv-basicstudies"  # 移動平均線
                ],
                custom_config={
                    "save_image": True,
                    "withdateranges": True,
                    "hide_side_toolbar": False
                }
            )
            
            filename = f"{demo_dir}/{symbol}_{name}_dark.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            created_files.append((symbol, name, description, filename))
            print(f"  完成: {filename}")
            
        except Exception as e:
            print(f"  錯誤: {str(e)}")
    
    return created_files, demo_dir

def create_demo_index(created_files, demo_dir):
    """創建演示索引頁面"""
    
    stock_cards = ""
    for symbol, name, description, filename in created_files:
        # 獲取股票詳細資訊
        widget = get_enhanced_taiwan_widget()
        stock_info = widget.get_stock_info(symbol)
        
        card_html = f"""
        <div class="stock-card" onclick="openChart('{os.path.basename(filename)}')">
            <div class="stock-header">
                <div class="stock-code">{symbol}</div>
                <div class="stock-exchange">{stock_info['exchange']}</div>
            </div>
            <div class="stock-name">{name}</div>
            <div class="stock-description">{description}</div>
            <div class="stock-industry">
                <span class="industry-badge" style="background-color: {stock_info['industry_color']};">
                    {stock_info['industry']}
                </span>
            </div>
            <div class="stock-tradingview">TradingView: {stock_info['tradingview_symbol']}</div>
        </div>
        """
        stock_cards += card_html
    
    index_html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台股TradingView Widget 演示</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .features {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
            color: white;
        }}
        
        .features h2 {{
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        
        .feature-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .feature-icon {{
            width: 24px;
            height: 24px;
            background: #4CAF50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        
        .stocks-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stock-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .stock-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .stock-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #4CAF50, #2196F3);
        }}
        
        .stock-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .stock-code {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #2962FF;
        }}
        
        .stock-exchange {{
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 8px;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .stock-name {{
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }}
        
        .stock-description {{
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 15px;
        }}
        
        .stock-industry {{
            margin-bottom: 10px;
        }}
        
        .industry-badge {{
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .stock-tradingview {{
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            color: #888;
            background: #f5f5f5;
            padding: 5px 8px;
            border-radius: 4px;
        }}
        
        .api-section {{
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 40px;
        }}
        
        .api-section h2 {{
            color: #333;
            margin-bottom: 20px;
        }}
        
        .api-endpoint {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        
        .api-endpoint .method {{
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .api-endpoint .url {{
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            opacity: 0.8;
        }}
        
        .quick-start {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            color: white;
        }}
        
        .command {{
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            margin: 10px 0;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>台股TradingView Widget</h1>
            <p>專業級台股圖表解決方案</p>
        </div>
        
        <div class="features">
            <h2>功能特色</h2>
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>專業級TradingView圖表介面</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>台股專用符號格式支援</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>內建多種技術指標</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>響應式設計支援</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>詳細股票資訊面板</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>產業分類顏色編碼</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>免費且完全合規</div>
                </div>
                <div class="feature-item">
                    <div class="feature-icon">✓</div>
                    <div>支援上市上櫃股票</div>
                </div>
            </div>
        </div>
        
        <div class="quick-start">
            <h2>快速啟動</h2>
            <p><strong>1. 啟動API服務器:</strong></p>
            <div class="command">uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000</div>
            
            <p><strong>2. 訪問圖表 (任選一種方式):</strong></p>
            <div class="command">http://localhost:8000/chart/taiwan-widget/2330</div>
            <div class="command">直接開啟下方的HTML文件</div>
        </div>
        
        <h2 style="color: white; text-align: center; margin-bottom: 30px;">熱門台股圖表演示</h2>
        <div class="stocks-grid">
            {stock_cards}
        </div>
        
        <div class="api-section">
            <h2>API端點說明</h2>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="url">/chart/taiwan-widget/{{symbol}}</span>
                <p>顯示台股圖表頁面 (例: /chart/taiwan-widget/2330)</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="url">/api/taiwan-widget/stock-info/{{symbol}}</span>
                <p>獲取台股詳細資訊JSON (例: /api/taiwan-widget/stock-info/2330)</p>
            </div>
            
            <div class="api-endpoint">
                <span class="method">GET</span>
                <span class="url">/api/taiwan-widget/symbol-search?query={{關鍵字}}</span>
                <p>搜尋台股符號 (例: /api/taiwan-widget/symbol-search?query=台積電)</p>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 台股TradingView Widget - 使用TradingView免費Widget + 台股開放資料</p>
            <p>完全免費，無授權問題，專業級圖表解決方案</p>
        </div>
    </div>

    <script>
        function openChart(filename) {{
            window.open(filename, '_blank');
        }}
        
        // 添加一些互動效果
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.stock-card');
            cards.forEach(card => {{
                card.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-5px) scale(1.02)';
                }});
                card.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0) scale(1)';
                }});
            }});
        }});
    </script>
</body>
</html>
    """
    
    index_filename = f"{demo_dir}/index.html"
    with open(index_filename, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    return index_filename

def open_demo_in_browser(index_file):
    """在瀏覽器中開啟演示"""
    try:
        file_path = os.path.abspath(index_file)
        webbrowser.open(f'file://{file_path}')
        print(f"\n演示已在瀏覽器中開啟: {file_path}")
        return True
    except Exception as e:
        print(f"無法開啟瀏覽器: {str(e)}")
        return False

def show_usage_examples():
    """顯示使用範例"""
    print("\n" + "="*60)
    print("使用範例")
    print("="*60)
    
    print("\n1. Python程式碼範例:")
    print("""
from src.visualization.enhanced_taiwan_widget import get_enhanced_taiwan_widget

# 獲取Widget實例
widget = get_enhanced_taiwan_widget()

# 創建台積電圖表
html = widget.create_enhanced_widget(
    symbol="2330",
    theme="dark",
    additional_studies=["MACD@tv-basicstudies"]
)

# 獲取股票資訊
info = widget.get_stock_info("2330")
print(f"{info['name']} - {info['industry']}")
    """)
    
    print("\n2. API使用範例:")
    print("""
# 顯示台積電圖表
GET http://localhost:8000/chart/taiwan-widget/2330

# 獲取台積電資訊
GET http://localhost:8000/api/taiwan-widget/stock-info/2330

# 搜尋股票
GET http://localhost:8000/api/taiwan-widget/symbol-search?query=台積電
    """)
    
    print("\n3. cURL命令範例:")
    print("""
# 獲取股票資訊
curl http://localhost:8000/api/taiwan-widget/stock-info/2330

# 搜尋股票
curl "http://localhost:8000/api/taiwan-widget/symbol-search?query=半導體"
    """)

def main():
    """主演示函數"""
    print("="*60)
    print("台股TradingView Widget 完整演示")
    print("="*60)
    print("\n這個演示將展示增強版台股Widget的所有功能...")
    
    try:
        # 創建演示圖表
        print("\n第1步: 創建演示圖表...")
        created_files, demo_dir = create_demo_charts()
        print(f"已創建 {len(created_files)} 個演示圖表")
        
        # 創建索引頁面
        print("\n第2步: 創建演示索引頁面...")
        index_file = create_demo_index(created_files, demo_dir)
        print(f"演示索引頁面: {index_file}")
        
        # 顯示使用範例
        show_usage_examples()
        
        print("\n" + "="*60)
        print("演示創建完成!")
        print("="*60)
        
        print(f"\n演示文件位置: {os.path.abspath(demo_dir)}")
        print(f"主要索引頁面: {os.path.abspath(index_file)}")
        
        print("\n查看演示的方式:")
        print("1. 直接開啟HTML文件 (推薦)")
        print("2. 啟動API服務器後訪問端點")
        
        # 詢問是否開啟瀏覽器
        try:
            choice = input("\n是否要在瀏覽器中開啟演示? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                if open_demo_in_browser(index_file):
                    print("演示已開啟，請在瀏覽器中查看各個圖表!")
                else:
                    print(f"請手動開啟: {os.path.abspath(index_file)}")
        except (KeyboardInterrupt, EOFError):
            print("\n跳過瀏覽器開啟")
        
        print("\n如需啟動API服務器，請運行:")
        print("uv run python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000")
        
        return 0
        
    except Exception as e:
        print(f"\n演示創建失敗: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)