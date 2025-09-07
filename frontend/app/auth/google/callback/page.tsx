'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '../../../../contexts/AuthContext';

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUserInfo } = useAuth();
  const [status, setStatus] = useState<'processing' | 'success' | 'error'>('processing');
  const [error, setError] = useState<string>('');
  const [hasProcessed, setHasProcessed] = useState(false);

  // 穩定 URL 參數以避免重複觸發
  const urlParams = useMemo(() => ({
    code: searchParams.get('code'),
    state: searchParams.get('state')
  }), [searchParams]);

  const handleCallback = useCallback(async () => {
    // 防止重複處理
    if (hasProcessed) return;
    
    // 標記為已處理，防止重複執行
    setHasProcessed(true);
      
    const { code, state } = urlParams;
    
    if (!code || !state) {
      setStatus('error');
      setError('缺少必要的授權參數');
      return;
    }

    try {
      // 發送授權碼到後端
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          state,
          redirect_uri: window.location.origin + '/auth/google/callback'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // 保存token到localStorage
        localStorage.setItem('auth_token', data.access_token);
        
        // 刷新用戶信息，refreshUserInfo現在會強制讀取localStorage
        await refreshUserInfo();
        
        setStatus('success');
        
        // 2秒後跳轉到主頁
        setTimeout(() => {
          router.push('/');
        }, 2000);
      } else {
        const errorData = await response.json();
        setStatus('error');
        setError(errorData.detail || 'Google登入失敗');
      }
    } catch (error) {
      console.error('Google callback error:', error);
      setStatus('error');
      setError('處理Google登入回調時發生錯誤');
    }
  }, [hasProcessed, urlParams, refreshUserInfo, router]);

  useEffect(() => {
    handleCallback();
  }, [handleCallback]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-xl max-w-md w-full p-8 border border-slate-700 shadow-2xl text-center">
        {status === 'processing' && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <h2 className="text-xl font-bold text-white mb-2">處理Google登入中...</h2>
            <p className="text-slate-400">請稍等片刻</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">登入成功！</h2>
            <p className="text-slate-400">正在跳轉到主頁...</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">登入失敗</h2>
            <p className="text-red-300 text-sm mb-4">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              返回首頁
            </button>
          </>
        )}
      </div>
    </div>
  );
}