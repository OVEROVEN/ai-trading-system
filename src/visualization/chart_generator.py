#!/usr/bin/env python3
"""
K線圖和技術分析圖表生成器
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import mplfinance as mpf
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ChartGenerator:
    """K線圖和技術分析圖表生成器"""
    
    def __init__(self):
        """初始化圖表生成器"""
        # 設定中文字體（如果需要）
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
    def create_candlestick_chart(self, 
                               data: pd.DataFrame,
                               symbol: str,
                               indicators: Dict[str, Any] = None,
                               patterns: List[Dict] = None,
                               signals: List[Dict] = None,
                               chart_type: str = "plotly") -> str:
        """
        創建K線圖
        
        Args:
            data: OHLCV 數據
            symbol: 股票代號
            indicators: 技術指標數據
            patterns: 形態標記
            signals: 交易訊號
            chart_type: 圖表類型 ("plotly" 或 "mplfinance")
            
        Returns:
            Base64 編碼的圖表或 HTML 字符串
        """
        try:
            if chart_type == "plotly":
                return self._create_plotly_chart(data, symbol, indicators, patterns, signals)
            else:
                return self._create_mplfinance_chart(data, symbol, indicators, patterns, signals)
        except Exception as e:
            logger.error(f"創建圖表失敗: {str(e)}")
            return None
    
    def _create_plotly_chart(self, 
                           data: pd.DataFrame,
                           symbol: str,
                           indicators: Dict[str, Any] = None,
                           patterns: List[Dict] = None,
                           signals: List[Dict] = None) -> str:
        """創建 Plotly 互動式K線圖"""
        
        # 創建子圖
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=(f'{symbol} K線圖', 'RSI', 'MACD')
        )
        
        # 主K線圖
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='K線',
                increasing_line_color='red',
                decreasing_line_color='green'
            ),
            row=1, col=1
        )
        
        # 成交量（作為柱狀圖）
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='成交量',
                marker_color='rgba(0,0,255,0.3)',
                yaxis='y2'
            ),
            row=1, col=1
        )
        
        # 添加技術指標
        if indicators:
            # 移動平均線
            if 'sma_20' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['sma_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'sma_50' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['sma_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            # 布林帶
            if 'bb_upper' in data.columns and 'bb_lower' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['bb_upper'],
                        mode='lines',
                        name='布林帶上軌',
                        line=dict(color='gray', width=1, dash='dash'),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['bb_lower'],
                        mode='lines',
                        name='布林帶下軌',
                        line=dict(color='gray', width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)'
                    ),
                    row=1, col=1
                )
            
            # RSI 指標
            if 'rsi' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['rsi'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple')
                    ),
                    row=2, col=1
                )
                
                # RSI 超買超賣線
                fig.add_hline(y=70, row=2, col=1, line_dash="dash", line_color="red", opacity=0.5)
                fig.add_hline(y=30, row=2, col=1, line_dash="dash", line_color="green", opacity=0.5)
            
            # MACD 指標
            if 'macd' in data.columns and 'macd_signal' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue')
                    ),
                    row=3, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd_signal'],
                        mode='lines',
                        name='MACD Signal',
                        line=dict(color='red')
                    ),
                    row=3, col=1
                )
                
                if 'macd_histogram' in data.columns:
                    fig.add_trace(
                        go.Bar(
                            x=data.index,
                            y=data['macd_histogram'],
                            name='MACD Histogram',
                            marker_color='gray',
                            opacity=0.5
                        ),
                        row=3, col=1
                    )
        
        # 添加形態標記
        if patterns:
            for pattern in patterns:
                self._add_pattern_annotation(fig, pattern, row=1)
        
        # 添加交易訊號
        if signals:
            for signal in signals:
                self._add_signal_marker(fig, signal, data, row=1)
        
        # 設定圖表佈局
        fig.update_layout(
            title=f'{symbol} 技術分析圖表',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # 設定Y軸
        fig.update_yaxes(title_text="價格", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        # 返回 HTML 字符串
        return fig.to_html(include_plotlyjs='cdn')
    
    def _create_mplfinance_chart(self,
                               data: pd.DataFrame,
                               symbol: str,
                               indicators: Dict[str, Any] = None,
                               patterns: List[Dict] = None,
                               signals: List[Dict] = None) -> str:
        """創建 mplfinance K線圖並返回 Base64 編碼"""
        
        try:
            # 準備數據
            df = data.copy()
            df.columns = [col.capitalize() for col in df.columns]  # mplfinance 需要大寫列名
            
            # 準備附加圖表
            add_plots = []
            
            # 添加移動平均線
            if 'Sma_20' in df.columns:
                add_plots.append(mpf.make_addplot(df['Sma_20'], color='blue', width=1))
            if 'Sma_50' in df.columns:
                add_plots.append(mpf.make_addplot(df['Sma_50'], color='orange', width=1))
            
            # 添加RSI（在單獨面板）
            if 'Rsi' in df.columns:
                add_plots.append(mpf.make_addplot(df['Rsi'], panel=1, color='purple', ylabel='RSI'))
            
            # 設定樣式
            style = mpf.make_mpf_style(
                base_mpl_style='seaborn-v0_8',
                marketcolors=mpf.make_marketcolors(
                    up='red', down='green',  # 台股習慣：紅漲綠跌
                    edge='inherit',
                    wick='inherit',
                    volume='in'
                )
            )
            
            # 創建圖表
            fig, axes = mpf.plot(
                df,
                type='candle',
                style=style,
                addplot=add_plots,
                volume=True,
                title=f'{symbol} K線圖',
                ylabel='價格',
                ylabel_lower='成交量',
                figsize=(12, 8),
                returnfig=True
            )
            
            # 添加形態和訊號標記
            if patterns or signals:
                ax = axes[0]  # 主圖軸
                
                # 添加形態標記
                if patterns:
                    for pattern in patterns:
                        self._add_pattern_to_mpl(ax, pattern, df)
                
                # 添加交易訊號
                if signals:
                    for signal in signals:
                        self._add_signal_to_mpl(ax, signal, df)
            
            # 轉換為 Base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            # 編碼為 Base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"創建 mplfinance 圖表失敗: {str(e)}")
            plt.close('all')
            return None
    
    def _add_pattern_annotation(self, fig, pattern: Dict, row: int = 1):
        """在 Plotly 圖表上添加形態標記"""
        try:
            # 假設形態有開始和結束日期
            start_date = pattern.get('start_date')
            end_date = pattern.get('end_date')
            pattern_name = pattern.get('pattern_name', '形態')
            
            if start_date and end_date:
                # 添加形態區域標記
                fig.add_vrect(
                    x0=start_date,
                    x1=end_date,
                    fillcolor="yellow",
                    opacity=0.2,
                    layer="below",
                    line_width=0,
                    row=row, col=1
                )
                
                # 添加標註
                fig.add_annotation(
                    x=end_date,
                    y=pattern.get('target_price', 0),
                    text=f"{pattern_name}<br>信心度: {pattern.get('confidence', 0):.2f}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="blue",
                    bgcolor="white",
                    bordercolor="blue",
                    row=row, col=1
                )
        except Exception as e:
            logger.warning(f"添加形態標記失敗: {str(e)}")
    
    def _add_signal_marker(self, fig, signal: Dict, data: pd.DataFrame, row: int = 1):
        """在 Plotly 圖表上添加交易訊號標記"""
        try:
            signal_type = signal.get('type', '').upper()
            signal_date = signal.get('date')
            
            if signal_date and signal_date in data.index:
                price = data.loc[signal_date, 'close']
                
                # 買入訊號（綠色向上箭頭）
                if signal_type == 'BUY':
                    fig.add_annotation(
                        x=signal_date,
                        y=price * 0.98,  # 稍微低於價格
                        text="BUY",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="green",
                        arrowsize=2,
                        bgcolor="green",
                        font=dict(color="white", size=10),
                        row=row, col=1
                    )
                
                # 賣出訊號（紅色向下箭頭）
                elif signal_type == 'SELL':
                    fig.add_annotation(
                        x=signal_date,
                        y=price * 1.02,  # 稍微高於價格
                        text="SELL",
                        showarrow=True,
                        arrowhead=3,
                        arrowcolor="red",
                        arrowsize=2,
                        bgcolor="red",
                        font=dict(color="white", size=10),
                        row=row, col=1
                    )
        except Exception as e:
            logger.warning(f"添加訊號標記失敗: {str(e)}")
    
    def _add_pattern_to_mpl(self, ax, pattern: Dict, data: pd.DataFrame):
        """在 matplotlib 圖表上添加形態標記"""
        try:
            start_date = pattern.get('start_date')
            end_date = pattern.get('end_date')
            
            if start_date and end_date:
                # 找到對應的索引
                start_idx = data.index.get_loc(start_date) if start_date in data.index else None
                end_idx = data.index.get_loc(end_date) if end_date in data.index else None
                
                if start_idx is not None and end_idx is not None:
                    # 添加背景區域
                    ax.axvspan(start_idx, end_idx, alpha=0.2, color='yellow')
                    
                    # 添加文字標註
                    ax.annotate(
                        f"{pattern.get('pattern_name', 'Pattern')}\n{pattern.get('confidence', 0):.2f}",
                        xy=(end_idx, pattern.get('target_price', data.iloc[end_idx]['Close'])),
                        xytext=(10, 10),
                        textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8),
                        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
                    )
        except Exception as e:
            logger.warning(f"添加形態標記失敗: {str(e)}")
    
    def _add_signal_to_mpl(self, ax, signal: Dict, data: pd.DataFrame):
        """在 matplotlib 圖表上添加交易訊號"""
        try:
            signal_type = signal.get('type', '').upper()
            signal_date = signal.get('date')
            
            if signal_date and signal_date in data.index:
                idx = data.index.get_loc(signal_date)
                price = data.iloc[idx]['Close']
                
                if signal_type == 'BUY':
                    ax.annotate('BUY', xy=(idx, price), xytext=(idx, price * 0.98),
                               arrowprops=dict(facecolor='green', shrink=0.05),
                               fontsize=8, ha='center', color='green')
                elif signal_type == 'SELL':
                    ax.annotate('SELL', xy=(idx, price), xytext=(idx, price * 1.02),
                               arrowprops=dict(facecolor='red', shrink=0.05),
                               fontsize=8, ha='center', color='red')
        except Exception as e:
            logger.warning(f"添加訊號標記失敗: {str(e)}")
    
    def create_performance_chart(self, equity_curve: pd.Series, benchmark: pd.Series = None) -> str:
        """創建績效比較圖表"""
        try:
            fig = go.Figure()
            
            # 策略績效曲線
            fig.add_trace(go.Scatter(
                x=equity_curve.index,
                y=equity_curve.values,
                mode='lines',
                name='策略績效',
                line=dict(color='blue', width=2)
            ))
            
            # 基準績效（如果提供）
            if benchmark is not None:
                fig.add_trace(go.Scatter(
                    x=benchmark.index,
                    y=benchmark.values,
                    mode='lines',
                    name='基準績效',
                    line=dict(color='gray', width=1, dash='dash')
                ))
            
            fig.update_layout(
                title='策略績效比較',
                xaxis_title='日期',
                yaxis_title='資產價值',
                template='plotly_white',
                height=400
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"創建績效圖表失敗: {str(e)}")
            return None
    
    def create_pattern_heatmap(self, pattern_stats: Dict) -> str:
        """創建形態統計熱力圖"""
        try:
            import plotly.express as px
            
            # 準備數據
            patterns = list(pattern_stats.keys())
            metrics = ['confidence', 'success_rate', 'avg_return']
            
            data = []
            for pattern in patterns:
                for metric in metrics:
                    data.append({
                        'Pattern': pattern,
                        'Metric': metric,
                        'Value': pattern_stats[pattern].get(metric, 0)
                    })
            
            df = pd.DataFrame(data)
            pivot_df = df.pivot(index='Pattern', columns='Metric', values='Value')
            
            fig = px.imshow(
                pivot_df,
                title='形態表現熱力圖',
                color_continuous_scale='RdYlGn',
                aspect='auto'
            )
            
            return fig.to_html(include_plotlyjs='cdn')
            
        except Exception as e:
            logger.error(f"創建熱力圖失敗: {str(e)}")
            return None