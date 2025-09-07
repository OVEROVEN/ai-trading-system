'use client';

import { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface StockSearchProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  onAnalyze: (symbol: string) => void;
  loading: boolean;
}

export function StockSearch({ selectedSymbol, onSymbolChange, onAnalyze, loading }: StockSearchProps) {
  const { t } = useLanguage();
  const [inputSymbol, setInputSymbol] = useState(selectedSymbol);

  const popularSymbols = [
    { symbol: 'AAPL', name: 'Apple' },
    { symbol: 'GOOGL', name: 'Google' },
    { symbol: 'MSFT', name: 'Microsoft' },
    { symbol: 'TSLA', name: 'Tesla' },
    { symbol: 'AMZN', name: 'Amazon' },
    { symbol: 'META', name: 'Meta' },
    { symbol: 'NVDA', name: 'NVIDIA' },
    { symbol: '2330.TW', name: 'TSMC' }
  ];

  const handleAnalyze = () => {
    if (inputSymbol.trim()) {
      onSymbolChange(inputSymbol.trim().toUpperCase());
      onAnalyze(inputSymbol.trim().toUpperCase());
    }
  };

  const handlePopularClick = (symbol: string) => {
    setInputSymbol(symbol);
    onSymbolChange(symbol);
    onAnalyze(symbol);
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Search Input */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <input
              type="text"
              value={inputSymbol}
              onChange={(e) => setInputSymbol(e.target.value)}
              placeholder={t('searchPlaceholder')}
              className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyze()}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:opacity-50 text-white text-sm rounded-md transition-colors"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span>{t('analyzing')}</span>
                </div>
              ) : (
                t('analyzeButton')
              )}
            </button>
          </div>
        </div>

        {/* Popular Stocks */}
        <div className="flex-1 lg:max-w-2xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-slate-400 mr-2">{t('popular')}</span>
            {popularSymbols.map((stock) => (
              <button
                key={stock.symbol}
                onClick={() => handlePopularClick(stock.symbol)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                  selectedSymbol === stock.symbol
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 hover:text-white'
                }`}
              >
                {stock.symbol}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}