'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface MarketDataProps {
  symbol: string;
  analysisData: any;
}

export function MarketData({ symbol, analysisData }: MarketDataProps) {
  const { t } = useLanguage();
  const [marketInfo, setMarketInfo] = useState({
    status: t('liveData'),
    period: t('threeMonths'),
    lastUpdate: ''
  });

  useEffect(() => {
    // 初始化時間並設定更新間隔
    const updateTime = () => {
      setMarketInfo(prev => ({
        ...prev,
        lastUpdate: new Date().toLocaleTimeString('en-US', { hour12: false })
      }));
    };
    
    // 立即更新時間
    updateTime();
    
    // 設定定期更新
    const interval = setInterval(updateTime, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
      <div className="flex items-center space-x-3 mb-4">
        <span className="text-xl">📈</span>
        <h3 className="text-lg font-semibold text-white">{t('marketData')}</h3>
      </div>
      
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-slate-400">{t('symbol')}</span>
          <span className="text-white font-mono text-lg">{symbol}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-slate-400">{t('status')}</span>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm">{marketInfo.status}</span>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-slate-400">{t('period')}</span>
          <span className="text-white">{marketInfo.period}</span>
        </div>

        {analysisData && (
          <>
            <div className="border-t border-slate-600 pt-4">
              <h4 className="text-sm font-medium text-slate-300 mb-3">{t('currentPrice')}</h4>
              <div className="text-2xl font-bold text-white">
                ${analysisData.current_price?.toFixed(2) || '---'}
              </div>
              {analysisData.price_change && (
                <div className={`text-sm ${analysisData.price_change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {analysisData.price_change >= 0 ? '↗' : '↘'} 
                  {Math.abs(analysisData.price_change).toFixed(2)}%
                </div>
              )}
            </div>

            <div className="border-t border-slate-600 pt-4">
              <h4 className="text-sm font-medium text-slate-300 mb-3">{t('keyMetrics')}</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-slate-400">{t('volume')}</div>
                  <div className="text-white">{analysisData.volume?.toLocaleString() || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-slate-400">{t('marketCap')}</div>
                  <div className="text-white">
                    {analysisData.market_cap ? `$${(analysisData.market_cap / 1e9).toFixed(1)}B` : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
        
        <div className="border-t border-slate-600 pt-4 text-xs text-slate-500">
          {t('lastUpdated')}: {marketInfo.lastUpdate}
        </div>
      </div>
    </div>
  );
}