'use client';

import { useState, useEffect } from 'react';
import { StockSearch } from '../components/StockSearch';
import { TradingChart } from '../components/TradingChart';
import { MarketData } from '../components/MarketData';
import { AIAnalysis } from '../components/AIAnalysis';
import { PerformancePanel } from '../components/PerformancePanel';
import { FeatureCards } from '../components/FeatureCards';
import { StatusBar } from '../components/StatusBar';
import { LanguageSwitcher } from '../components/LanguageSwitcher';
import { AuthButton } from '../components/AuthButton';
import { RedemptionCode } from '../components/RedemptionCode';
import { useLanguage } from '../contexts/LanguageContext';
import { useModal } from '../contexts/ModalContext';
import { analyzeStock } from '../lib/api';

export default function TradingDashboard() {
  const { t, language } = useLanguage();
  const { isAuthModalOpen } = useModal();
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol);
    // 這會觸發所有組件的更新
  };

  const handleAnalyzeStock = async (symbol: string) => {
    setLoading(true);
    try {
      const data = await analyzeStock(symbol, {
        period: '3mo',
        include_ai: true,
        language: language // 傳送當前語言設定給 AI 分析
      });
      setAnalysisData(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Header */}
      <header className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between min-h-16 py-2">
            <div className="flex items-center space-x-3">
              <div className="text-2xl">🚀</div>
              <div>
                <h1 className="text-xl font-bold text-white">{t('appTitle')}</h1>
                <p className="text-sm text-slate-300">{t('subtitle')}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <LanguageSwitcher />
              <AuthButton />
            </div>
          </div>
        </div>
      </header>

      <div 
        className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6"
        style={{ pointerEvents: isAuthModalOpen ? 'none' : 'auto' }}
      >
        {/* Stock Search Section */}
        <div className="mb-6">
          <StockSearch 
            selectedSymbol={selectedSymbol}
            onSymbolChange={handleSymbolChange}
            onAnalyze={handleAnalyzeStock}
            loading={loading}
          />
        </div>

        {/* Main Chart Section */}
        <div className="mb-6">
          <TradingChart 
            symbol={selectedSymbol}
            className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700"
          />
        </div>

        {/* Data Panels Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <MarketData 
            symbol={selectedSymbol}
            analysisData={analysisData}
          />
          <AIAnalysis 
            symbol={selectedSymbol}
            analysisData={analysisData}
            loading={loading}
          />
          <PerformancePanel 
            symbol={selectedSymbol}
            analysisData={analysisData}
          />
        </div>

        {/* Redemption Code Section */}
        <div className="mb-6">
          <RedemptionCode />
        </div>

        {/* Feature Cards */}
        <FeatureCards />

        {/* Status Bar */}
        <StatusBar />
      </div>
    </div>
  );
}