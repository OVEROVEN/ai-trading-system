'use client';

import { useLanguage } from '../contexts/LanguageContext';

interface PerformancePanelProps {
  symbol: string;
  analysisData: any;
}

export function PerformancePanel({ symbol, analysisData }: PerformancePanelProps) {
  const { t } = useLanguage();
  
  const performanceMetrics = [
    {
      labelKey: 'accuracy',
      value: '85.2%',
      change: '+2.1%',
      positive: true
    },
    {
      labelKey: 'winRate',
      value: '72.1%',
      change: '+0.5%',
      positive: true
    },
    {
      labelKey: 'riskScore',
      value: t('medium'),
      change: t('stable'),
      positive: true
    }
  ];

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
      <div className="flex items-center space-x-3 mb-6">
        <span className="text-xl">📊</span>
        <h3 className="text-lg font-semibold text-white">{t('performance')}</h3>
      </div>
      
      <div className="space-y-4">
        {performanceMetrics.map((metric, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="text-slate-400 text-sm">{t(metric.labelKey)}</span>
            <div className="text-right">
              <div className="text-white font-semibold">{metric.value}</div>
              <div className={`text-xs ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                {metric.change}
              </div>
            </div>
          </div>
        ))}
        
        {/* Technical Indicators Summary */}
        {analysisData?.technical_indicators && (
          <div className="border-t border-slate-600 pt-4">
            <h4 className="text-sm font-medium text-slate-300 mb-3">Technical Signals</h4>
            <div className="space-y-2">
              {Object.entries(analysisData.technical_indicators).slice(0, 3).map(([key, value]: [string, any]) => (
                <div key={key} className="flex justify-between items-center text-sm">
                  <span className="text-slate-400 capitalize">{key.replace('_', ' ')}</span>
                  <span className="text-white font-mono">
                    {typeof value === 'number' ? value.toFixed(2) : value}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Chart Mini */}
        <div className="border-t border-slate-600 pt-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3">Recent Performance</h4>
          <div className="flex items-end justify-between h-16 space-x-1">
            {[65, 72, 68, 85, 92, 88, 76, 82, 89, 85].map((height, index) => (
              <div 
                key={index}
                className="bg-gradient-to-t from-blue-600 to-blue-400 rounded-sm flex-1 transition-all duration-300"
                style={{ height: `${height}%` }}
              ></div>
            ))}
          </div>
          <div className="text-xs text-slate-500 mt-2 text-center">
            10-day performance trend
          </div>
        </div>
      </div>
    </div>
  );
}