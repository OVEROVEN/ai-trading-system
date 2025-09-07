#!/usr/bin/env python3
"""
簡化版TradingView風格圖表生成器
修復兼容性問題，提供穩定的專業圖表
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TradingViewStyleChart:
    """簡化版TradingView風格圖表"""
    
    def __init__(self):
        """初始化圖表生成器"""
        self.dark_theme = {
            'background': '#131722',
            'paper': '#1e222d',
            'grid': '#2a2e39',
            'text': '#d1d4dc',
            'candle_up': '#26a69a',
            'candle_down': '#ef5350',
            'volume_up': 'rgba(38, 166, 154, 0.6)',
            'volume_down': 'rgba(239, 83, 80, 0.6)',
            'ma_20': '#2962ff',
            'ma_50': '#ff6d00',
            'ma_200': '#e040fb',
            'rsi': '#ff5722',
            'macd': '#00bcd4',
            'signal': '#ffeb3b'
        }
        
        self.light_theme = {
            'background': '#ffffff',
            'paper': '#ffffff',
            'grid': '#e1e1e1',
            'text': '#2e2e2e',
            'candle_up': '#26a69a',
            'candle_down': '#ef5350',
            'volume_up': 'rgba(38, 166, 154, 0.6)',
            'volume_down': 'rgba(239, 83, 80, 0.6)',
            'ma_20': '#2962ff',
            'ma_50': '#ff6d00',
            'ma_200': '#e040fb',
            'rsi': '#ff5722',
            'macd': '#00bcd4',
            'signal': '#ff9800'
        }
    
    def create_chart(self, 
                    data: pd.DataFrame,
                    symbol: str,
                    indicators: Dict[str, Any] = None,
                    patterns: List[Dict] = None,
                    signals: List[Dict] = None,
                    theme: str = "dark") -> str:
        """
        創建TradingView風格圖表
        """
        try:
            colors = self.dark_theme if theme == "dark" else self.light_theme
            
            # 創建子圖佈局
            fig = make_subplots(
                rows=4, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                row_heights=[0.55, 0.15, 0.15, 0.15],
                subplot_titles=(
                    f'{symbol} • Professional Chart',
                    'Volume', 
                    'RSI (14)', 
                    'MACD (12,26,9)'
                )
            )
            
            # 添加K線圖
            self._add_candlesticks(fig, data, colors)
            
            # 添加成交量
            self._add_volume(fig, data, colors)
            
            # 添加技術指標
            if indicators:
                self._add_indicators(fig, data, indicators, colors)
            
            # 添加形態標記
            if patterns:
                self._add_patterns(fig, patterns, colors)
            
            # 添加交易訊號
            if signals:
                self._add_signals(fig, signals, data, colors)
            
            # 應用專業樣式
            self._apply_styling(fig, colors)
            
            return fig.to_html(
                include_plotlyjs='cdn',
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'scrollZoom': True
                }
            )
            
        except Exception as e:
            logger.error(f"創建TradingView圖表失敗: {str(e)}")
            return self._create_error_chart(str(e))
    
    def _add_candlesticks(self, fig: go.Figure, data: pd.DataFrame, colors: Dict[str, str]):
        """添加K線圖"""
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                increasing_line_color=colors['candle_up'],
                decreasing_line_color=colors['candle_down'],
                increasing_fillcolor=colors['candle_up'],
                decreasing_fillcolor=colors['candle_down']
            ),
            row=1, col=1
        )
    
    def _add_volume(self, fig: go.Figure, data: pd.DataFrame, colors: Dict[str, str]):
        """添加成交量"""
        # 計算成交量顏色
        volume_colors = []
        for i in range(len(data)):
            if i == 0:
                volume_colors.append(colors['volume_up'])
            else:
                if data['close'].iloc[i] >= data['close'].iloc[i-1]:
                    volume_colors.append(colors['volume_up'])
                else:
                    volume_colors.append(colors['volume_down'])
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['volume'],
                name='Volume',
                marker_color=volume_colors
            ),
            row=2, col=1
        )
    
    def _add_indicators(self, fig: go.Figure, data: pd.DataFrame, 
                       indicators: Dict[str, Any], colors: Dict[str, str]):
        """添加技術指標"""
        
        # 移動平均線
        if 'sma_20' in data.columns and data['sma_20'] is not None:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['sma_20'],
                    mode='lines',
                    name='MA 20',
                    line=dict(color=colors['ma_20'], width=1.5)
                ),
                row=1, col=1
            )
        
        if 'sma_50' in data.columns and data['sma_50'] is not None:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['sma_50'],
                    mode='lines',
                    name='MA 50',
                    line=dict(color=colors['ma_50'], width=1.5)
                ),
                row=1, col=1
            )
        
        if 'sma_200' in data.columns and data['sma_200'] is not None:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['sma_200'],
                    mode='lines',
                    name='MA 200',
                    line=dict(color=colors['ma_200'], width=2)
                ),
                row=1, col=1
            )
        
        # 布林帶
        if 'bb_upper' in data.columns and 'bb_lower' in data.columns:
            if data['bb_upper'] is not None and data['bb_lower'] is not None:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['bb_upper'],
                        mode='lines',
                        name='BB Upper',
                        line=dict(color='rgba(128,128,128,0.5)', width=1),
                        showlegend=False
                    ),
                    row=1, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['bb_lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='rgba(128,128,128,0.5)', width=1),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)'
                    ),
                    row=1, col=1
                )
        
        # RSI 指標
        if 'rsi' in data.columns and data['rsi'] is not None:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['rsi'],
                    mode='lines',
                    name='RSI',
                    line=dict(color=colors['rsi'], width=2)
                ),
                row=3, col=1
            )
            
            # RSI 水平線
            fig.add_hline(y=70, row=3, col=1, line_dash="dash", line_color="red", opacity=0.5)
            fig.add_hline(y=30, row=3, col=1, line_dash="dash", line_color="green", opacity=0.5)
            fig.add_hline(y=50, row=3, col=1, line_dash="dot", line_color="gray", opacity=0.3)
        
        # MACD 指標
        if all(col in data.columns for col in ['macd', 'macd_signal']):
            if data['macd'] is not None and data['macd_signal'] is not None:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color=colors['macd'], width=2)
                    ),
                    row=4, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color=colors['signal'], width=1.5)
                    ),
                    row=4, col=1
                )
                
                if 'macd_histogram' in data.columns and data['macd_histogram'] is not None:
                    hist_colors = ['green' if h >= 0 else 'red' for h in data['macd_histogram']]
                    fig.add_trace(
                        go.Bar(
                            x=data.index,
                            y=data['macd_histogram'],
                            name='MACD Hist',
                            marker_color=hist_colors,
                            opacity=0.7
                        ),
                        row=4, col=1
                    )
    
    def _add_patterns(self, fig: go.Figure, patterns: List[Dict], colors: Dict[str, str]):
        """添加形態標記"""
        for pattern in patterns:
            try:
                start_date = pattern.get('start_date')
                end_date = pattern.get('end_date')
                pattern_name = pattern.get('pattern_name', 'Pattern')
                confidence = pattern.get('confidence', 0)
                
                if start_date and end_date:
                    # 形態區域標記
                    fig.add_vrect(
                        x0=start_date,
                        x1=end_date,
                        fillcolor='rgba(255, 193, 7, 0.3)',
                        layer="below",
                        line_width=0,
                        row=1, col=1
                    )
                    
                    # 標註
                    fig.add_annotation(
                        x=end_date,
                        y=pattern.get('target_price', 0),
                        text=f"<b>{pattern_name}</b><br>信心度: {confidence:.1%}",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor=colors['text'],
                        bgcolor=colors['paper'],
                        bordercolor=colors['text'],
                        font=dict(size=10, color=colors['text']),
                        row=1, col=1
                    )
            except Exception as e:
                logger.warning(f"添加形態標記失敗: {str(e)}")
    
    def _add_signals(self, fig: go.Figure, signals: List[Dict], 
                    data: pd.DataFrame, colors: Dict[str, str]):
        """添加交易訊號"""
        for signal in signals:
            try:
                signal_type = signal.get('type', '').upper()
                signal_date = signal.get('date')
                
                if signal_date and signal_date in data.index:
                    price = data.loc[signal_date, 'close']
                    
                    if signal_type == 'BUY':
                        fig.add_trace(
                            go.Scatter(
                                x=[signal_date],
                                y=[price * 0.98],
                                mode='markers',
                                name='Buy Signal',
                                marker=dict(
                                    symbol='triangle-up',
                                    size=15,
                                    color='#4caf50',
                                    line=dict(width=2, color='white')
                                ),
                                showlegend=False
                            ),
                            row=1, col=1
                        )
                    
                    elif signal_type == 'SELL':
                        fig.add_trace(
                            go.Scatter(
                                x=[signal_date],
                                y=[price * 1.02],
                                mode='markers',
                                name='Sell Signal',
                                marker=dict(
                                    symbol='triangle-down',
                                    size=15,
                                    color='#f44336',
                                    line=dict(width=2, color='white')
                                ),
                                showlegend=False
                            ),
                            row=1, col=1
                        )
            except Exception as e:
                logger.warning(f"添加訊號標記失敗: {str(e)}")
    
    def _apply_styling(self, fig: go.Figure, colors: Dict[str, str]):
        """應用TradingView風格"""
        fig.update_layout(
            font=dict(family="Inter, sans-serif", size=12, color=colors['text']),
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['paper'],
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=colors['text'])
            ),
            margin=dict(l=60, r=60, t=60, b=40),
            height=800
        )
        
        # 更新軸樣式
        fig.update_xaxes(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            zeroline=False,
            showspikes=True,
            spikecolor=colors['text'],
            spikesnap="cursor",
            spikemode="across"
        )
        
        fig.update_yaxes(
            gridcolor=colors['grid'],
            gridwidth=0.5,
            zeroline=False,
            showspikes=True,
            spikecolor=colors['text'],
            spikesnap="cursor",
            spikemode="across"
        )
        
        # 設定y軸標題
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        
        # 隱藏範圍滑塊
        fig.update_layout(xaxis_rangeslider_visible=False)
        
        # 設定hover模式
        fig.update_layout(hovermode='x unified')
    
    def _create_error_chart(self, error_message: str) -> str:
        """創建錯誤圖表"""
        fig = go.Figure()
        fig.add_annotation(
            text=f"圖表生成失敗<br>{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title="圖表錯誤",
            height=400,
            template="plotly_white"
        )
        return fig.to_html(include_plotlyjs='cdn')