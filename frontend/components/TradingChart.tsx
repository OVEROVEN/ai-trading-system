'use client';

import { useEffect, useRef } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface TradingChartProps {
  symbol: string;
  className?: string;
}

export function TradingChart({ symbol, className = '' }: TradingChartProps) {
  const { language, t } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // 清空容器
    containerRef.current.innerHTML = '';

    // 創建圖表容器
    const chartContainer = document.createElement('div');
    chartContainer.id = `tradingview_${symbol}_${Date.now()}`;
    chartContainer.style.height = '500px';
    containerRef.current.appendChild(chartContainer);

    // 創建TradingView腳本
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: symbol.includes('.TW') ? `TWSE:${symbol.replace('.TW', '')}` : `NASDAQ:${symbol}`,
      interval: '1D',
      timezone: 'Asia/Taipei',
      theme: 'dark',
      style: '1',
      locale: language === 'zh-TW' ? 'zh_TW' : 'en',
      toolbar_bg: '#f1f3f6',
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: true,
      container_id: chartContainer.id,
      studies: [
        'RSI@tv-basicstudies',
        'MACD@tv-basicstudies',
        'Volume@tv-basicstudies'
      ],
      overrides: {
        'paneProperties.background': '#1e293b',
        'paneProperties.vertGridProperties.color': '#334155',
        'paneProperties.horzGridProperties.color': '#334155',
        'symbolWatermarkProperties.transparency': 90,
        'scalesProperties.textColor': '#cbd5e1'
      }
    });

    chartContainer.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, language]);

  return (
    <div className={`relative ${className}`}>
      {/* Chart Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700">
        <div className="flex items-center space-x-3">
          <span className="text-lg">📊</span>
          <div>
            <h2 className="text-lg font-semibold text-white">{t('chartAnalysis')} - {symbol}</h2>
            <p className="text-sm text-slate-400">{t('chartDescription')}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors">
            {t('saveButton')}
          </button>
          <button className="px-3 py-1 bg-slate-600 text-white text-sm rounded hover:bg-slate-700 transition-colors">
            {t('fullscreenButton')}
          </button>
        </div>
      </div>
      
      {/* Chart Container */}
      <div ref={containerRef} className="relative bg-slate-800 min-h-[500px]">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-400">Loading chart for {symbol}...</p>
          </div>
        </div>
      </div>
    </div>
  );
}