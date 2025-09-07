// AI Trading System API Library

const API_BASE = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000';

export interface StockAnalysisRequest {
  period: string;
  include_ai: boolean;
  include_patterns?: boolean;
  language?: string;
}

export interface TechnicalIndicators {
  rsi?: number;
  macd?: number;
  macd_signal?: number;
  bb_upper?: number;
  bb_lower?: number;
  sma_20?: number;
  sma_50?: number;
  volume_ratio?: number;
  atr?: number;
}

export interface AIAnalysisResult {
  recommendation?: string;
  confidence?: number;
  reasoning?: string;
  key_factors?: string[];
  price_target?: number;
  stop_loss?: number;
  risk_score?: number;
  entry_price?: number;
  error?: string;
  login_required?: boolean;
  quota_exceeded?: boolean;
  remaining_quota?: number;
}

export interface PatternResult {
  type: string;
  confidence: number;
  description: string;
}

export interface SupportResistanceLevel {
  level: number;
  strength: string;
  type: string;
}

export interface TradingSignal {
  symbol: string;
  signal_type: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
}

export interface AnalysisResponse {
  symbol: string;
  current_price: number;
  price_change: number;
  price_change_percent: number;
  technical_indicators: TechnicalIndicators;
  ai_analysis: AIAnalysisResult | null;
  patterns: {
    support_resistance?: SupportResistanceLevel[];
    candlestick?: PatternResult[];
    chart_patterns?: PatternResult[];
  };
  signals: TradingSignal[];
  timestamp: string;
}

export async function analyzeStock(
  symbol: string,
  options: StockAnalysisRequest
): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE}/analyze/${symbol}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Add authorization header if available
        ...(getAuthHeaders())
      },
      body: JSON.stringify({
        symbol: symbol,
        period: options.period || '3mo',
        include_ai: options.include_ai || false,
        include_patterns: options.include_patterns !== false, // default true
        language: options.language || 'en'
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error ${response.status}:`, errorText);
      throw new Error(`Analysis failed: ${response.status} ${errorText}`);
    }

    const data = await response.json();
    console.log('📊 Analysis API Response:', data);
    return data;

  } catch (error) {
    console.error('💥 Analysis API Error:', error);
    throw error;
  }
}

export async function getStockData(symbol: string, period: string = '3mo') {
  try {
    const response = await fetch(`${API_BASE}/api/stocks/${symbol}?period=${period}`, {
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch stock data: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Stock data fetch error:', error);
    throw error;
  }
}

export async function getChartData(symbol: string, period: string = '3mo') {
  try {
    const response = await fetch(`${API_BASE}/api/charts/${symbol}?period=${period}`, {
      headers: getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch chart data: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chart data fetch error:', error);
    throw error;
  }
}

export async function testApiConnection(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/api/health`);
    return response.ok;
  } catch (error) {
    console.error('API connection test failed:', error);
    return false;
  }
}

// Helper function to get authorization headers
function getAuthHeaders(): HeadersInit {
  const headers: HeadersInit = {
    'Content-Type': 'application/json'
  };
  
  // Try to get token from localStorage
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('🔑 Using auth token for API request');
    } else {
      console.log('⚠️ No auth token found - AI analysis may require login');
    }
  }

  return headers;
}

// AI specific endpoints
export async function askAI(question: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE}/ai/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        question: question,
        context: 'trading'
      })
    });

    if (!response.ok) {
      throw new Error(`AI query failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('AI query error:', error);
    throw error;
  }
}

export async function startStrategyChat(symbol: string): Promise<any> {
  try {
    const response = await fetch(`${API_BASE}/api/ai/strategy-chat/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        symbol: symbol,
        analysis_type: 'comprehensive'
      })
    });

    if (!response.ok) {
      throw new Error(`Strategy chat failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Strategy chat error:', error);
    throw error;
  }
}

// Export API base URL for debugging
export { API_BASE };