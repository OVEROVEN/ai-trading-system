'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
  full_name: string;
  is_premium: boolean;
  subscription_tier?: string; // Added this line
  remaining_initial_quota: number;
  remaining_daily_quota: number;
  can_use_ai_analysis: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, fullName: string) => Promise<boolean>;
  loginWithGoogle: () => Promise<void>;
  logout: () => void;
  refreshUserInfo: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // 檢查本地存儲的 token
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setToken(savedToken);
      fetchUserInfo(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async (authToken: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser({
          id: userData.id,
          email: userData.email,
          full_name: userData.full_name,
          is_premium: userData.is_premium || false,
          remaining_initial_quota: userData.remaining_initial_quota || 0,
          remaining_daily_quota: userData.remaining_daily_quota || 0,
          can_use_ai_analysis: userData.can_use_ai_analysis || false
        });
      } else {
        // Token 無效，清除
        localStorage.removeItem('auth_token');
        setToken(null);
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const data = await response.json();
        const authToken = data.access_token;
        
        localStorage.setItem('auth_token', authToken);
        setToken(authToken);
        setUser({
          id: data.user.id,
          email: data.user.email,
          full_name: data.user.full_name,
          is_premium: data.user.is_premium || false,
          remaining_initial_quota: data.user.remaining_initial_quota || 0,
          remaining_daily_quota: data.user.remaining_daily_quota || 0,
          can_use_ai_analysis: data.user.can_use_ai_analysis || false
        });
        
        return true;
      } else {
        const errorData = await response.json();
        console.error('Login failed:', errorData);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (email: string, password: string, fullName: string): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName
        }),
      });

      if (response.ok) {
        // 註冊成功後自動登入
        return await login(email, password);
      } else {
        const errorData = await response.json();
        console.error('Registration failed:', errorData);
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
  };

  const loginWithGoogle = async (): Promise<void> => {
    try {
      // 獲取Google授權URL
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/google/login`, {
        method: 'GET',
      });

      if (response.ok) {
        const data = await response.json();
        // 重定向到Google授權頁面
        window.location.href = data.authorization_url;
      } else {
        throw new Error('Failed to initiate Google login');
      }
    } catch (error) {
      console.error('Google login error:', error);
      throw error;
    }
  };

  const refreshUserInfo = async () => {
    // 強制重新讀取localStorage中的token
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setToken(savedToken);
      await fetchUserInfo(savedToken);
    } else if (token) {
      await fetchUserInfo(token);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    loginWithGoogle,
    logout,
    refreshUserInfo,
    isAuthenticated: !!token && !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}