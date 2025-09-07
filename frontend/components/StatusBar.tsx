'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

export function StatusBar() {
  const { t } = useLanguage();
  const [status, setStatus] = useState({
    apiConnected: true,
    realTimeData: true,
    aiAnalysisReady: true
  });

  const [currentTime, setCurrentTime] = useState<Date | null>(null);

  useEffect(() => {
    // 初始化時間
    setCurrentTime(new Date());
    
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const statusItems = [
    {
      label: t('apiConnected'),
      status: status.apiConnected,
      icon: '🔌'
    },
    {
      label: t('realTimeData'),
      status: status.realTimeData,
      icon: '📡'
    },
    {
      label: t('aiAnalysisReady'),
      status: status.aiAnalysisReady,
      icon: '🤖'
    }
  ];

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-6">
          {statusItems.map((item, index) => (
            <div key={index} className="flex items-center space-x-2">
              <span className="text-lg">{item.icon}</span>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${item.status ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span className={`text-sm ${item.status ? 'text-green-200' : 'text-red-200'}`}>
                  {item.label}
                </span>
              </div>
            </div>
          ))}
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-slate-400">
          <span>{t('systemTime')}: {currentTime ? currentTime.toLocaleTimeString('en-US', { hour12: false }) : '--:--:--'}</span>
          <span>|</span>
          <span>{t('market')}: {currentTime && (currentTime.getHours() >= 9 && currentTime.getHours() < 16) ? t('marketOpen') : t('marketClosed')}</span>
        </div>
      </div>
    </div>
  );
}