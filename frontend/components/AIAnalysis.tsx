'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useAuth } from '../contexts/AuthContext';

interface AIAnalysisProps {
  symbol: string;
  analysisData: any;
  loading: boolean;
}

export function AIAnalysis({ symbol, analysisData, loading }: AIAnalysisProps) {
  const { t } = useLanguage();
  const { user, isAuthenticated, token } = useAuth();
  const [aiInsights, setAiInsights] = useState<string[]>([]);

  useEffect(() => {
    if (analysisData?.ai_analysis) {
      // 解析AI分析結果 - 處理對象結構，確保回傳陣列
      let insights: string[] = [];
      
      try {
        if (analysisData.ai_analysis.key_factors) {
          // 檢查 key_factors 是否為數組
          if (Array.isArray(analysisData.ai_analysis.key_factors)) {
            insights = analysisData.ai_analysis.key_factors.slice(0, 5);
          } else if (typeof analysisData.ai_analysis.key_factors === 'string') {
            // 如果 key_factors 是字符串，分割處理
            insights = [analysisData.ai_analysis.key_factors];
          }
        } else if (typeof analysisData.ai_analysis === 'string') {
          // 備用：如果是字符串則分割
          insights = analysisData.ai_analysis.split('\n')
            .filter((line: string) => line.trim().length > 0)
            .slice(0, 5);
        } else if (analysisData.ai_analysis.reasoning) {
          // 使用 reasoning 文本分割成洞察
          insights = [analysisData.ai_analysis.reasoning];
        }
        
        // 確保 insights 是有效陣列
        if (!Array.isArray(insights)) {
          insights = [];
        }
        
        setAiInsights(insights);
      } catch (error) {
        console.warn('Error parsing AI analysis data:', error);
        setAiInsights([]);
      }
    } else {
      // 清空舊數據
      setAiInsights([]);
    }
  }, [analysisData]);

  if (loading) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
        <div className="flex items-center space-x-3 mb-4">
          <span className="text-xl">🤖</span>
          <h3 className="text-lg font-semibold text-white">{t('ai_analysis')}</h3>
        </div>
        
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-slate-400">{t('analyzing')} {symbol}...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-xl">🤖</span>
          <h3 className="text-lg font-semibold text-white">{t('ai_analysis')}</h3>
        </div>
        <div className="px-2 py-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full">
          <span className="text-xs text-white font-medium">GPT-4 Powered</span>
        </div>
      </div>
      
      {!analysisData ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🎯</div>
          <p className="text-slate-400">{t('generating_analysis')}</p>
        </div>
      ) : analysisData.ai_analysis?.login_required ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">🔐</div>
          <h4 className="text-lg font-semibold text-white mb-2">需要登入才能使用AI分析</h4>
          <p className="text-slate-400 mb-4">請登入您的帳號以獲得完整的AI交易建議</p>
          <div className="flex flex-col gap-2 max-w-sm mx-auto">
            <div className="bg-slate-700/50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <span>🤖</span>
                <span>GPT-4 驅動的智能分析</span>
              </div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <span>📊</span>
                <span>精準進場點與目標價</span>
              </div>
            </div>
            <div className="bg-slate-700/50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <span>⚡</span>
                <span>即時策略建議</span>
              </div>
            </div>
          </div>
        </div>
      ) : analysisData.ai_analysis?.quota_exceeded ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-4">⏰</div>
          <h4 className="text-lg font-semibold text-white mb-2">AI分析配額已用完</h4>
          <p className="text-slate-400 mb-2">
            剩餘配額: {analysisData.ai_analysis.remaining_quota || 0} 次
          </p>
          <p className="text-slate-400">請明天再試或考慮升級為付費用戶</p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* AI Recommendation */}
          <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-lg p-4 border border-blue-500/30">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm font-medium text-blue-200">{t('ai_recommendation')}</span>
              <div className="px-2 py-0.5 bg-blue-600 text-white text-xs rounded-full">
                {analysisData.ai_analysis?.recommendation || analysisData.ai_recommendation || t('analyzing')}
              </div>
            </div>
            <p className="text-sm text-slate-300">
              {analysisData.ai_analysis?.reasoning || analysisData.ai_summary || t('generating_analysis')}
            </p>
          </div>

          {/* Key Insights */}
          {aiInsights.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-slate-300 mb-3">{t('key_insights')}</h4>
              <div className="space-y-2">
                {aiInsights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-2 text-sm">
                    <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-slate-300">{insight}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Trading Price Levels */}
          {(analysisData.ai_analysis?.entry_price || analysisData.ai_analysis?.price_target || analysisData.ai_analysis?.stop_loss) && (
            <div className="bg-gradient-to-r from-green-600/20 to-blue-600/20 rounded-lg p-4 border border-green-500/30">
              <h4 className="text-sm font-medium text-green-200 mb-3">📊 {t('trading_price_levels')}</h4>
              <div className="grid grid-cols-1 gap-3">
                {analysisData.ai_analysis?.entry_price && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-400">🎯 {t('entry_price')}</span>
                    <span className="text-green-400 font-semibold">
                      ${analysisData.ai_analysis.entry_price.toFixed(2)}
                    </span>
                  </div>
                )}
                {analysisData.ai_analysis?.price_target && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-400">🚀 {t('target_price')}</span>
                    <span className="text-blue-400 font-semibold">
                      ${analysisData.ai_analysis.price_target.toFixed(2)}
                    </span>
                  </div>
                )}
                {analysisData.ai_analysis?.stop_loss && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-slate-400">🛑 {t('stop_loss')}</span>
                    <span className="text-red-400 font-semibold">
                      ${analysisData.ai_analysis.stop_loss.toFixed(2)}
                    </span>
                  </div>
                )}
                {analysisData.ai_analysis?.entry_price && analysisData.ai_analysis?.price_target && (
                  <div className="flex justify-between items-center pt-2 border-t border-slate-600">
                    <span className="text-sm text-slate-400">📈 {t('potential_return')}</span>
                    <span className="text-yellow-400 font-semibold">
                      {(() => {
                        const recommendation = analysisData.ai_analysis.recommendation;
                        const entryPrice = analysisData.ai_analysis.entry_price;
                        const targetPrice = analysisData.ai_analysis.price_target;
                        let returnPercent = 0;
                        
                        if (recommendation === 'BUY') {
                          // 買進：目標價高於進場價 = 正報酬
                          returnPercent = ((targetPrice - entryPrice) / entryPrice) * 100;
                        } else if (recommendation === 'SELL') {
                          // 賣出(做空)：進場價高於目標價 = 正報酬
                          returnPercent = ((entryPrice - targetPrice) / entryPrice) * 100;
                        } else {
                          // HOLD或其他：計算絕對值差異
                          returnPercent = Math.abs((targetPrice - entryPrice) / entryPrice) * 100;
                        }
                        
                        return `+${Math.abs(returnPercent).toFixed(1)}%`;
                      })()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Confidence and Risk Scores */}
          <div className="border-t border-slate-600 pt-4 space-y-4">
            {/* AI Confidence */}
            {analysisData.ai_analysis?.confidence && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-slate-400">{t('ai_confidence')}</span>
                  <span className="text-white font-semibold">
                    {(analysisData.ai_analysis.confidence * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${analysisData.ai_analysis.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {/* Risk Score */}
            {analysisData.ai_analysis?.risk_score !== undefined && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-slate-400">{t('risk_level')}</span>
                  <span className="text-white font-semibold">
                    {analysisData.ai_analysis.risk_score < 0.3 ? t('low') : 
                     analysisData.ai_analysis.risk_score < 0.7 ? t('medium') : t('high')}
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-500 ${ 
                      analysisData.ai_analysis.risk_score < 0.3 ? 'bg-green-500' :
                      analysisData.ai_analysis.risk_score < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${analysisData.ai_analysis.risk_score * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {/* Technical Score (fallback) */}
            {analysisData.technical_score && !analysisData.ai_analysis?.confidence && (
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-slate-400">{t('technical_score')}</span>
                  <span className="text-white font-semibold">
                    {(analysisData.technical_score * 100).toFixed(0)}/100
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${analysisData.technical_score * 100}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          <div className="text-xs text-slate-500 mt-4 text-center">
            ⚡ {t('ai_powered_description')}
          </div>
        </div>
      )}
    </div>
  );
}
