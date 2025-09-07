'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

// Expanded translations to cover all components
const simpleTranslations = {
  en: {
    appTitle: 'AI Trading Dashboard',
    subtitle: 'Powered by Gemini',
    user: 'User',
    freeTier: 'Free Tier',
    logout: 'Logout',
    login: 'Login',
    register: 'Register',
    loginError: 'Login failed. Please check your credentials.',
    registerError: 'Registration failed. The email might already be in use.',
    networkError: 'A network error occurred. Please try again.',
    fullName: 'Full Name',
    enterFullName: 'Enter your full name',
    email: 'Email',
    enterEmail: 'Enter your email',
    password: 'Password',
    enterPassword: 'Enter your password (min. 6 characters)',
    loggingIn: 'Logging in...',
    registering: 'Registering...',
    noAccount: "Don't have an account?",
    haveAccount: 'Already have an account?',
    // AIAnalysis.tsx keys
    ai_analysis: 'AI Analysis',
    analyzing: 'Analyzing',
    generating_analysis: 'Generating Analysis...',
    ai_recommendation: 'AI Recommendation',
    key_insights: 'Key Insights',
    trading_price_levels: 'Trading Price Levels',
    entry_price: 'Entry Price',
    target_price: 'Target Price',
    stop_loss: 'Stop Loss',
    potential_return: 'Potential Return',
    ai_confidence: 'AI Confidence',
    risk_level: 'Risk Level',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    technical_score: 'Technical Score',
    ai_powered_description: 'AI analysis is experimental and for informational purposes only.',
    // FeatureCards.tsx keys
    technicalAnalysis: 'Technical Analysis',
    technicalAnalysisDesc: 'Real-time data streams and custom indicators.',
    active: 'Active',
    patternRecognition: 'Pattern Recognition',
    patternRecognitionDesc: 'Automatic detection of chart patterns.',
    aiInsights: 'AI-Powered Insights',
    aiInsightsDesc: 'Actionable advice from GPT-4 analysis.',
    multiMarket: 'Multi-Market Support',
    multiMarketDesc: 'US stocks and Taiwan stocks supported.',
    // MarketData.tsx keys
    liveData: 'Live Data',
    threeMonths: '3 Months',
    marketData: 'Market Data',
    symbol: 'Symbol',
    status: 'Status',
    period: 'Period',
    currentPrice: 'Current Price',
    keyMetrics: 'Key Metrics',
    volume: 'Volume',
    marketCap: 'Market Cap',
    lastUpdated: 'Last Updated',
    // PerformancePanel.tsx keys
    performance: 'Performance',
    accuracy: 'Accuracy',
    winRate: 'Win Rate',
    riskScore: 'Risk Score',
    stable: 'Stable',
    // RedemptionCode.tsx keys
    enterRedemptionCode: 'Enter redemption code',
    redemptionSuccess: 'Success!',
    creditsAdded: 'credits added',
    redemptionError: 'Redemption failed.',
    invalidCode: 'Invalid or expired code.',
    codeAlreadyUsed: 'Code has already been used.',
    codeExpired: 'This code has expired.',
    redemptionCode: 'Redemption Code',
    redeemCode: 'Have a code? Redeem it here for credits.',
    yourCredits: 'Your Credits',
    bonusCredits: 'Bonus',
    freeCredits: 'Free',
    dailyCredits: 'Daily',
    totalCredits: 'Total',
    processing: 'Processing...',
    redeemNow: 'Redeem Now',
    redemptionHistory: 'Redemption History',
    noRedemptionHistory: 'You have no redemption history.',
    // StatusBar.tsx keys
    apiConnected: 'API Connected',
    realTimeData: 'Real-time Data',
    aiAnalysisReady: 'AI Analysis Ready',
    systemTime: 'System Time',
    market: 'Market',
    marketOpen: 'Open',
    marketClosed: 'Closed',
    // StockSearch.tsx keys
    searchPlaceholder: 'Search symbol (e.g., AAPL, 2330.TW)',
    analyzeButton: 'Analyze',
    popular: 'Popular:',
    // TradingChart.tsx keys
    chartAnalysis: 'Chart Analysis',
    chartDescription: 'Interactive chart with technical indicators.',
    saveButton: 'Save',
    fullscreenButton: 'Fullscreen',
  },
  'zh-TW': {
    appTitle: 'AI 交易儀表板',
    subtitle: '由 Gemini 驅動',
    user: '使用者',
    freeTier: '免費方案',
    logout: '登出',
    login: '登入',
    register: '註冊',
    loginError: '登入失敗，請檢查您的帳號密碼。',
    registerError: '註冊失敗，這個信箱可能已經被使用了。',
    networkError: '網路錯誤，請稍後再試。',
    fullName: '全名',
    enterFullName: '輸入您的全名',
    email: '電子郵件',
    enterEmail: '輸入您的電子郵件',
    password: '密碼',
    enterPassword: '輸入您的密碼 (最少6個字元)',
    loggingIn: '登入中...',
    registering: '註冊中...',
    noAccount: '還沒有帳號嗎？',
    haveAccount: '已經有帳號了？',
    // AIAnalysis.tsx keys
    ai_analysis: 'AI 分析',
    analyzing: '分析中',
    generating_analysis: '正在生成分析...',
    ai_recommendation: 'AI 建議',
    key_insights: '關鍵洞察',
    trading_price_levels: '交易價位參考',
    entry_price: '進場價',
    target_price: '目標價',
    stop_loss: '停損價',
    potential_return: '潛在回報',
    ai_confidence: 'AI信心指數',
    risk_level: '風險等級',
    low: '低',
    medium: '中',
    high: '高',
    technical_score: '技術分數',
    ai_powered_description: 'AI分析為實驗性功能，僅供參考。',
    // FeatureCards.tsx keys
    technicalAnalysis: '技術分析',
    technicalAnalysisDesc: '實時數據流和自定義指標。',
    active: '啟用中',
    patternRecognition: '型態識別',
    patternRecognitionDesc: '自動偵測圖表模式。',
    aiInsights: 'AI 智能洞察',
    aiInsightsDesc: '來自 GPT-4 分析的可行建議。',
    multiMarket: '多市場支援',
    multiMarketDesc: '支援美國股市與台灣股市。',
    // MarketData.tsx keys
    liveData: '即時數據',
    threeMonths: '3 個月',
    marketData: '市場數據',
    symbol: '代碼',
    status: '狀態',
    period: '期間',
    currentPrice: '目前價格',
    keyMetrics: '關鍵指標',
    volume: '成交量',
    marketCap: '市值',
    lastUpdated: '最後更新',
    // PerformancePanel.tsx keys
    performance: '表現',
    accuracy: '準確度',
    winRate: '勝率',
    riskScore: '風險分數',
    stable: '穩定',
    // RedemptionCode.tsx keys
    enterRedemptionCode: '輸入兌換碼',
    redemptionSuccess: '成功!',
    creditsAdded: '點數已加入',
    redemptionError: '兌換失敗。',
    invalidCode: '無效或過期的兌換碼。',
    codeAlreadyUsed: '此兌換碼已被使用。',
    codeExpired: '此兌換碼已過期。',
    redemptionCode: '點數兌換',
    redeemCode: '有兌換碼嗎？在此兌換點數。',
    yourCredits: '您的點數',
    bonusCredits: '獎勵點數',
    freeCredits: '免費點數',
    dailyCredits: '每日點數',
    totalCredits: '總點數',
    processing: '處理中...',
    redeemNow: '立即兌換',
    redemptionHistory: '兌換紀錄',
    noRedemptionHistory: '您沒有任何兌換紀錄。',
    // StatusBar.tsx keys
    apiConnected: 'API 已連線',
    realTimeData: '即時數據',
    aiAnalysisReady: 'AI 分析就緒',
    systemTime: '系統時間',
    market: '市場',
    marketOpen: '開市',
    marketClosed: '休市',
    // StockSearch.tsx keys
    searchPlaceholder: '搜尋代碼 (例如 AAPL, 2330.TW)',
    analyzeButton: '分析',
    popular: '熱門：',
    // TradingChart.tsx keys
    chartAnalysis: '圖表分析',
    chartDescription: '包含技術指標的互動式圖表。',
    saveButton: '儲存',
    fullscreenButton: '全螢幕',
  },
};

export type Language = keyof typeof simpleTranslations;

interface LanguageContextType {
  language: Language;
  setLanguage: (language: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  useEffect(() => {
    const savedLang = localStorage.getItem('language') as Language;
    if (savedLang && simpleTranslations[savedLang]) {
      setLanguage(savedLang);
    }
  }, []);

  const handleSetLanguage = (lang: Language) => {
    setLanguage(lang);
    localStorage.setItem('language', lang);
  };

  const t = (key: string): string => {
    // @ts-ignore
    return simpleTranslations[language][key] || key;
  };

  const value = {
    language,
    setLanguage: handleSetLanguage,
    t,
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within an AuthProvider');
  }
  return context;
}
