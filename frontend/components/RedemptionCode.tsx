'use client';

import { useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import API_URL from '../lib/api';

interface UserCredits {
  bonus_credits: number;
  free_credits: number;
  daily_credits: number;
  total_credits: number;
  can_use_ai: boolean;
}

interface RedemptionHistoryItem {
  code: string;
  credits_added: number;
  redeemed_at: string;
  description?: string;
}

export function RedemptionCode() {
  const { t } = useLanguage();
  const [redemptionCode, setRedemptionCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [userCredits, setUserCredits] = useState<UserCredits | null>(null);
  const [redemptionHistory, setRedemptionHistory] = useState<RedemptionHistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load user credits and history on component mount
  useEffect(() => {
    loadUserCredits();
    loadRedemptionHistory();
  }, []);

  const loadUserCredits = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const response = await fetch(`${API_URL}/api/redemption/credits`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUserCredits(data);
      }
    } catch (error) {
      console.error('Failed to load user credits:', error);
    }
  };

  const loadRedemptionHistory = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      const response = await fetch(`${API_URL}/api/redemption/history`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setRedemptionHistory(data);
      }
    } catch (error) {
      console.error('Failed to load redemption history:', error);
    }
  };

  const handleRedeem = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!redemptionCode.trim()) {
      setMessage(t('enterRedemptionCode'));
      setMessageType('error');
      return;
    }

    const token = localStorage.getItem('auth_token');
    if (!token) {
      setMessage(t('loginError'));
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_URL}/api/redemption/redeem`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ code: redemptionCode.trim() })
      });

      const data = await response.json();

      if (data.success) {
        setMessage(`${t('redemptionSuccess')} ${t('creditsAdded')}: ${data.credits_added}`);
        setMessageType('success');
        setRedemptionCode('');
        
        // Reload credits and history
        await loadUserCredits();
        await loadRedemptionHistory();
      } else {
        // Handle specific error messages
        let errorMessage = t('redemptionError');
        if (data.message.includes('不存在') || data.message.includes('失效')) {
          errorMessage = t('invalidCode');
        } else if (data.message.includes('已被使用') || data.message.includes('已經使用')) {
          errorMessage = t('codeAlreadyUsed');
        } else if (data.message.includes('過期')) {
          errorMessage = t('codeExpired');
        }
        
        setMessage(errorMessage);
        setMessageType('error');
      }
    } catch (error) {
      console.error('Redemption failed:', error);
      setMessage(t('networkError'));
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="text-2xl">🎫</div>
        <div>
          <h2 className="text-xl font-bold text-white">{t('redemptionCode')}</h2>
          <p className="text-sm text-slate-300">{t('redeemCode')}</p>
        </div>
      </div>

      {/* Current Credits Display */}
      {userCredits && (
        <div className="mb-6 p-4 bg-slate-700/50 rounded-lg">
          <h3 className="text-lg font-semibold text-white mb-3">{t('yourCredits')}</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="bg-blue-500/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-blue-300">{userCredits.bonus_credits}</div>
              <div className="text-sm text-blue-200">{t('bonusCredits')}</div>
            </div>
            <div className="bg-green-500/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-green-300">{userCredits.free_credits}</div>
              <div className="text-sm text-green-200">{t('freeCredits')}</div>
            </div>
            <div className="bg-purple-500/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-purple-300">{userCredits.daily_credits}</div>
              <div className="text-sm text-purple-200">{t('dailyCredits')}</div>
            </div>
            <div className="bg-yellow-500/20 rounded-lg p-3">
              <div className="text-2xl font-bold text-yellow-300">{userCredits.total_credits}</div>
              <div className="text-sm text-yellow-200">{t('totalCredits')}</div>
            </div>
          </div>
        </div>
      )}

      {/* Redemption Form */}
      <form onSubmit={handleRedeem} className="mb-6">
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={redemptionCode}
            onChange={(e) => setRedemptionCode(e.target.value)}
            placeholder={t('enterRedemptionCode')}
            className="flex-1 px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t('processing')}
              </>
            ) : (
              t('redeemNow')
            )}
          </button>
        </div>
      </form>

      {/* Message Display */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          messageType === 'success' 
            ? 'bg-green-500/20 border border-green-500/50 text-green-300' 
            : 'bg-red-500/20 border border-red-500/50 text-red-300'
        }`}>
          {message}
        </div>
      )}

      {/* Redemption History Toggle */}
      <div className="border-t border-slate-600 pt-6">
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center justify-between w-full text-left text-white hover:text-blue-300 transition-colors"
        >
          <span className="font-semibold">{t('redemptionHistory')}</span>
          <svg
            className={`w-5 h-5 transition-transform ${showHistory ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* Redemption History List */}
        {showHistory && (
          <div className="mt-4">
            {redemptionHistory.length === 0 ? (
              <p className="text-slate-400 text-center py-8">{t('noRedemptionHistory')}</p>
            ) : (
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {redemptionHistory.map((item, index) => (
                  <div key={index} className="bg-slate-700/30 rounded-lg p-4 border border-slate-600/50">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-mono text-sm text-blue-300">{item.code}</div>
                        {item.description && (
                          <div className="text-sm text-slate-400 mt-1">{item.description}</div>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-green-300 font-semibold">+{item.credits_added}</div>
                        <div className="text-sm text-slate-400">{formatDate(item.redeemed_at)}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}