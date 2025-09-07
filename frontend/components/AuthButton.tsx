'use client';

import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useModal } from '../contexts/ModalContext';

export function AuthButton() {
  const { user, logout, isAuthenticated } = useAuth();
  const { t } = useLanguage();
  const { isAuthModalOpen, openAuthModal, closeAuthModal } = useModal();

  if (isAuthenticated && user) {
    return (
      <div className="relative">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user.full_name?.charAt(0) || user.email?.charAt(0) || 'U'}
              </span>
            </div>
            <div className="flex flex-col text-sm">
              <span className="text-white font-medium">
                {user.full_name || user.email?.split('@')[0] || t('user')}
              </span>
              <span className="text-slate-400 text-xs">
                {user.subscription_tier || t('freeTier')}
              </span>
            </div>
          </div>
          
          <button
            onClick={logout}
            className="px-3 py-1 text-sm text-slate-400 hover:text-white transition-colors border border-slate-600 rounded-md hover:border-slate-400"
          >
            {t('logout')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <button
        onClick={openAuthModal}
        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
      >
        {t('login')}
      </button>
      
      {isAuthModalOpen && (
        <AuthModal 
          isOpen={isAuthModalOpen} 
          onClose={closeAuthModal} 
        />
      )}
    </>
  );
}

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const { login, register, loginWithGoogle } = useAuth();
  const { t } = useLanguage();
  const { closeAuthModal, openAuthModal } = useModal();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      let success = false;
      
      if (isLogin) {
        success = await login(formData.email, formData.password);
      } else {
        success = await register(formData.email, formData.password, formData.fullName);
      }

      if (success) {
        onClose();
      } else {
        setError(isLogin ? t('loginError') : t('registerError'));
      }
    } catch (err) {
      setError(t('networkError'));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  // 使用Portal將模態框渲染到body最頂層
  const modalContent = (
    <div 
      className="modal-overlay-portal"
      style={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 2147483647,  // 使用最大可能的z-index
        backgroundColor: 'rgba(0, 0, 0, 0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '4rem',
        paddingBottom: '1rem',
        paddingLeft: '1rem',
        paddingRight: '1rem',
        minHeight: '100vh',
        overflowY: 'auto',
        pointerEvents: 'auto',
        isolation: 'isolate'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bg-slate-800 rounded-xl max-w-md w-full p-6 border border-slate-700 shadow-2xl transform transition-all duration-300 ease-out animate-slideUp relative">
        <div className="flex items-center justify-between mb-6 relative z-10">
          <h2 className="text-xl font-bold text-white">
            {isLogin ? t('login') : t('register')}
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-slate-700 rounded-lg"
            aria-label="關閉登入視窗"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex mb-6 bg-slate-700 rounded-lg p-1">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              isLogin 
                ? 'bg-blue-600 text-white' 
                : 'text-slate-300 hover:text-white'
            }`}
          >
            {t('login')}
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              !isLogin 
                ? 'bg-blue-600 text-white' 
                : 'text-slate-300 hover:text-white'
            }`}
          >
            {t('register')}
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                {t('fullName')}
              </label>
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={t('enterFullName')}
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              {t('email')}
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={t('enterEmail')}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              {t('password')}
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={t('enterPassword')}
              required
              minLength={6}
            />
          </div>

          {error && (
            <div className="p-3 bg-red-900/50 border border-red-500/50 rounded-lg">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white rounded-lg font-medium transition-colors flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {isLogin ? t('loggingIn') : t('registering')}
              </>
            ) : (
              isLogin ? t('login') : t('register')
            )}
          </button>
        </form>

        {/* 分隔線 */}
        <div className="flex items-center my-4">
          <div className="flex-1 border-t border-slate-600"></div>
          <span className="px-3 text-sm text-slate-400">或</span>
          <div className="flex-1 border-t border-slate-600"></div>
        </div>

        {/* Google登入按鈕 */}
        <button
          type="button"
          onClick={async () => {
            try {
              setLoading(true);
              setError('');
              
              // Google登入會重定向頁面，所以先關閉模態框
              onClose();
              
              // 開始Google OAuth流程 (這會重定向到Google)
              await loginWithGoogle();
              
            } catch (error) {
              console.error('Google login failed:', error);
              // 如果在重定向前出錯，重新打開模態框並顯示錯誤
              openAuthModal();
              setError('Google登入初始化失敗，請稍後重試');
            } finally {
              setLoading(false);
            }
          }}
          disabled={loading}
          className="w-full py-2 px-4 bg-white hover:bg-gray-50 disabled:bg-gray-200 text-gray-800 rounded-lg font-medium transition-colors flex items-center justify-center border border-gray-300"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="#4285f4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34a853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#fbbc05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#ea4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          {loading ? '處理中...' : '使用 Google 登入'}
        </button>

        {/* 新增說明文字 */}
        <div className="mt-3 p-2 bg-slate-700/50 rounded-lg">
          <p className="text-xs text-slate-400 text-center">
            💡 如果您的Google帳戶郵箱已經註冊過，系統會自動綁定到您的現有帳戶
          </p>
        </div>

        <div className="mt-4 pt-4 border-t border-slate-700">
          <p className="text-slate-400 text-sm text-center">
            {isLogin ? t('noAccount') : t('haveAccount')}{' '}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-400 hover:text-blue-300 underline"
            >
              {isLogin ? t('register') : t('login')}
            </button>
          </p>
        </div>
      </div>
    </div>
  );

  // 使用createPortal將模態框渲染到document.body
  return typeof window !== 'undefined' 
    ? createPortal(modalContent, document.body)
    : null;
}

export default AuthButton;