'use client';

import { useLanguage } from '../contexts/LanguageContext';

export function FeatureCards() {
  const { t } = useLanguage();
  
  const features = [
    {
      icon: '📈',
      titleKey: 'technicalAnalysis',
      descriptionKey: 'technicalAnalysisDesc',
      statusKey: 'active'
    },
    {
      icon: '🔍',
      titleKey: 'patternRecognition',
      descriptionKey: 'patternRecognitionDesc',
      statusKey: 'active'
    },
    {
      icon: '🤖',
      titleKey: 'aiInsights',
      descriptionKey: 'aiInsightsDesc',
      statusKey: 'active'
    },
    {
      icon: '🌍',
      titleKey: 'multiMarket',
      descriptionKey: 'multiMarketDesc',
      statusKey: 'active'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      {features.map((feature, index) => (
        <div 
          key={index}
          className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6 hover:border-blue-500/50 transition-all duration-300 group cursor-pointer"
        >
          <div className="text-center">
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
              {feature.icon}
            </div>
            <h3 className="font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
              {t(feature.titleKey)}
            </h3>
            <p className="text-sm text-slate-400 mb-3 leading-relaxed">
              {t(feature.descriptionKey)}
            </p>
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-green-600/20 rounded-full border border-green-500/30">
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              <span className="text-xs text-green-200">{t(feature.statusKey)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}