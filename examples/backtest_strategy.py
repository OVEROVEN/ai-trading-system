#!/usr/bin/env python3
"""
策略回測範例
"""
import requests
import json
from datetime import datetime, timedelta

def run_backtest(symbol, strategy_name, start_date, end_date, **strategy_params):
    """
    執行回測
    
    Args:
        symbol: 股票代號
        strategy_name: 策略名稱 ('rsi_macd' 或 'ma_crossover')
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        **strategy_params: 策略參數
    """
    
    url = "http://localhost:8000/backtest"
    
    payload = {
        "symbol": symbol,
        "start_date": start_date,
        "end_date": end_date,
        "strategy_name": strategy_name,
        "strategy_params": strategy_params,
        "initial_capital": 100000,  # 初始資金 10萬
        "commission": 0.001425,     # 手續費 0.1425%
        "stop_loss_pct": 0.02,      # 停損 2%
        "take_profit_pct": 0.06     # 停利 6%
    }
    
    try:
        print(f"🔄 回測 {symbol} ({strategy_name})...")
        print(f"📅 期間: {start_date} 到 {end_date}")
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 {data['symbol']} 回測結果")
            print(f"策略: {data['strategy_name']}")
            
            # 績效指標
            perf = data['performance_metrics']
            print(f"\n💰 績效表現:")
            print(f"  總報酬率: {perf['total_return_pct']:.2f}%")
            print(f"  夏普比率: {perf['sharpe_ratio']:.2f}")
            print(f"  最大回撤: {perf['max_drawdown_pct']:.2f}%")
            print(f"  波動率: {perf['volatility']:.2f}%")
            print(f"  卡瑪比率: {perf['calmar_ratio']:.2f}")
            print(f"  索提諾比率: {perf['sortino_ratio']:.2f}")
            
            # 交易統計
            trades = data['trade_statistics']
            print(f"\n📈 交易統計:")
            print(f"  總交易次數: {trades['total_trades']}")
            print(f"  獲利交易: {trades['winning_trades']}")
            print(f"  虧損交易: {trades['losing_trades']}")
            print(f"  勝率: {trades['win_rate']:.1f}%")
            print(f"  平均獲利: ${trades['avg_profit']:.2f}")
            print(f"  平均虧損: ${trades['avg_loss']:.2f}")
            print(f"  獲利因子: {trades['profit_factor']:.2f}")
            
            # 風險指標
            risk = data['risk_metrics']
            print(f"\n⚠️  風險指標:")
            print(f"  風險值(VaR 95%): {risk['value_at_risk_95']:.2f}%")
            if risk['beta']:
                print(f"  Beta: {risk['beta']:.2f}")
            if risk['alpha']:
                print(f"  Alpha: {risk['alpha']:.2f}")
            
            # 投資總結
            summary = data['summary']
            print(f"\n💼 投資總結:")
            print(f"  初始資金: ${summary['initial_capital']:,}")
            print(f"  最終價值: ${summary['final_value']:,}")
            print(f"  投資報酬率: {summary['roi']:.2f}%")
            
            # 交易樣本
            if data['sample_trades']:
                print(f"\n📋 交易記錄 (前5筆):")
                for i, trade in enumerate(data['sample_trades'][:5]):
                    print(f"  {i+1}. {trade['entry_date'][:10]} 進場 ${trade['entry_price']:.2f}")
                    if trade['exit_date']:
                        print(f"     {trade['exit_date'][:10]} 出場 ${trade['exit_price']:.2f}")
                        print(f"     損益: ${trade['profit_loss']:.2f} ({trade['profit_loss_pct']:.2f}%)")
                        print(f"     持有: {trade['hold_period']} 天, 原因: {trade['exit_reason']}")
            
        else:
            print(f"❌ 回測失敗: {response.text}")
            
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def get_available_strategies():
    """獲取可用策略"""
    try:
        response = requests.get("http://localhost:8000/backtest/strategies")
        if response.status_code == 200:
            data = response.json()
            print("📋 可用策略:")
            for strategy, details in data['strategy_details'].items():
                print(f"\n🎯 {details['name']} ({strategy})")
                print(f"   描述: {details['description']}")
                print(f"   參數:")
                for param, info in details['parameters'].items():
                    print(f"     {param}: {info['description']} (預設: {info['default']})")
        else:
            print(f"❌ 獲取策略失敗: {response.text}")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")

def main():
    """主程式"""
    print("🚀 策略回測範例")
    
    # 顯示可用策略
    get_available_strategies()
    
    print("\n" + "="*60)
    
    # 計算日期 (最近3個月)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # 回測 RSI+MACD 策略 (AAPL)
    run_backtest(
        symbol="AAPL",
        strategy_name="rsi_macd",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        rsi_oversold=30,
        rsi_overbought=70
    )
    
    print("\n" + "="*60)
    
    # 回測移動平均策略 (台積電)
    run_backtest(
        symbol="2330.TW",
        strategy_name="ma_crossover",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        fast_period=20,
        slow_period=50
    )

if __name__ == "__main__":
    main()