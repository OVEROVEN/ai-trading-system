const { test, expect } = require('@playwright/test');

// 測試配置
const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8000';

test.describe('AI Trading Dashboard Comprehensive Tests', () => {
  
  // 設置每個測試前的初始化
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    // 等待頁面完全載入
    await page.waitForLoadState('networkidle');
  });

  // 1. 頁面基本載入和響應測試
  test('1. Page Basic Loading and Response', async ({ page }) => {
    // 檢查頁面標題
    await expect(page).toHaveTitle(/AI Trading Dashboard/i);
    
    // 檢查主要頁面元素是否存在
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    
    // 檢查副標題
    await expect(page.locator('text=Advanced Stock Analysis & AI-Powered Trading Insights')).toBeVisible();
    
    // 檢查狀態指示器
    await expect(page.locator('text=Real-time Analysis')).toBeVisible();
    await expect(page.locator('text=AI Recommendations')).toBeVisible();
    await expect(page.locator('text=TradingView Charts')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/01-page-loading.png', 
      fullPage: true 
    });
  });

  // 2. 股票搜尋功能測試
  test('2. Stock Search Functionality', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    const analyzeButton = page.locator('button:has-text("Analyze")');
    
    // 測試 AAPL
    await test.step('Search AAPL', async () => {
      await searchInput.fill('AAPL');
      await analyzeButton.click();
      
      // 等待載入完成
      await expect(page.locator('text=Analyzing')).toBeVisible();
      await expect(page.locator('text=Analyzing')).toBeHidden({ timeout: 15000 });
      
      // 驗證圖表更新
      await expect(page.locator('text=Chart Analysis - AAPL')).toBeVisible();
    });

    // 測試 TSLA
    await test.step('Search TSLA', async () => {
      await searchInput.fill('TSLA');
      await analyzeButton.click();
      
      await expect(page.locator('text=Analyzing')).toBeVisible();
      await expect(page.locator('text=Analyzing')).toBeHidden({ timeout: 15000 });
      
      await expect(page.locator('text=Chart Analysis - TSLA')).toBeVisible();
    });

    // 測試 2330.TW (台積電)
    await test.step('Search 2330.TW', async () => {
      await searchInput.fill('2330.TW');
      await analyzeButton.click();
      
      await expect(page.locator('text=Analyzing')).toBeVisible();
      await expect(page.locator('text=Analyzing')).toBeHidden({ timeout: 15000 });
      
      await expect(page.locator('text=Chart Analysis - 2330.TW')).toBeVisible();
    });

    await page.screenshot({ 
      path: 'test-results/02-stock-search.png', 
      fullPage: true 
    });
  });

  // 3. 流行股票按鈕功能測試
  test('3. Popular Stock Buttons', async ({ page }) => {
    const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', '2330.TW'];
    
    for (const stock of popularStocks.slice(0, 3)) { // 測試前3個以節省時間
      await test.step(`Test ${stock} button`, async () => {
        await page.locator(`button:has-text("${stock}")`).click();
        
        // 驗證按鈕狀態變更
        await expect(page.locator(`button:has-text("${stock}")`)).toHaveClass(/bg-blue-600/);
        
        // 等待分析完成
        await page.waitForTimeout(2000);
        
        // 驗證圖表更新
        await expect(page.locator(`text=Chart Analysis - ${stock}`)).toBeVisible();
      });
    }
    
    await page.screenshot({ 
      path: 'test-results/03-popular-buttons.png', 
      fullPage: true 
    });
  });

  // 4. 圖表載入狀態測試
  test('4. Chart Loading Status', async ({ page }) => {
    // 點擊搜尋觸發圖表載入
    await page.locator('button:has-text("AAPL")').click();
    
    // 檢查載入指示器
    await expect(page.locator('text=Loading chart for AAPL...')).toBeVisible();
    
    // 檢查圖表容器存在
    await expect(page.locator('text=Chart Analysis - AAPL')).toBeVisible();
    
    // 檢查圖表工具列按鈕
    await expect(page.locator('button:has-text("Save")')).toBeVisible();
    await expect(page.locator('button:has-text("Fullscreen")')).toBeVisible();
    
    // 等待TradingView腳本載入
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
      path: 'test-results/04-chart-loading.png', 
      fullPage: true 
    });
  });

  // 5. AI分析面板測試
  test('5. AI Analysis Panel', async ({ page }) => {
    // 觸發AI分析
    await page.locator('button:has-text("AAPL")').click();
    
    // 檢查AI分析面板存在
    await expect(page.locator('text=AI Analysis')).toBeVisible();
    await expect(page.locator('text=GPT-4 Powered')).toBeVisible();
    
    // 等待分析完成
    await expect(page.locator('text=AI is analyzing')).toBeVisible();
    await expect(page.locator('text=AI is analyzing')).toBeHidden({ timeout: 20000 });
    
    // 檢查分析結果元素
    await expect(page.locator('text=AI Recommendation')).toBeVisible();
    await expect(page.locator('text=Technical Score')).toBeVisible();
    
    await page.screenshot({ 
      path: 'test-results/05-ai-analysis.png', 
      fullPage: true 
    });
  });

  // 6. 市場數據顯示測試
  test('6. Market Data Display', async ({ page }) => {
    // 觸發數據載入
    await page.locator('button:has-text("AAPL")').click();
    
    // 檢查市場數據面板
    await expect(page.locator('text=Market Data')).toBeVisible();
    await expect(page.locator('text=Live Data')).toBeVisible();
    
    // 檢查數據項目
    await expect(page.locator('text=Symbol')).toBeVisible();
    await expect(page.locator('text=Status')).toBeVisible();
    await expect(page.locator('text=Period')).toBeVisible();
    
    // 等待實際數據載入
    await page.waitForTimeout(3000);
    
    await page.screenshot({ 
      path: 'test-results/06-market-data.png', 
      fullPage: true 
    });
  });

  // 7. 技術分析功能卡片測試
  test('7. Technical Analysis Feature Cards', async ({ page }) => {
    // 檢查功能卡片存在
    const featureCards = [
      'Technical Analysis',
      'Pattern Recognition', 
      'AI Insights',
      'Multi-Market'
    ];
    
    for (const card of featureCards) {
      await expect(page.locator(`text=${card}`)).toBeVisible();
    }
    
    // 檢查狀態指示器
    await expect(page.locator('text=Active').first()).toBeVisible();
    
    // 測試hover效果
    await page.locator('text=Technical Analysis').first().hover();
    await page.waitForTimeout(500);
    
    await page.screenshot({ 
      path: 'test-results/07-feature-cards.png', 
      fullPage: true 
    });
  });

  // 8. 系統狀態指示器測試
  test('8. System Status Indicators', async ({ page }) => {
    // 檢查狀態欄存在
    await expect(page.locator('text=API Connected')).toBeVisible();
    await expect(page.locator('text=Real-time Data')).toBeVisible();
    await expect(page.locator('text=AI Analysis Ready')).toBeVisible();
    
    // 檢查系統時間
    await expect(page.locator('text=System Time:')).toBeVisible();
    await expect(page.locator('text=Market:')).toBeVisible();
    
    await page.screenshot({ 
      path: 'test-results/08-status-indicators.png', 
      fullPage: true 
    });
  });

  // 9. 響應式設計測試
  test('9. Responsive Design Tests', async ({ page }) => {
    // 桌面視窗測試 (1920x1080)
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({ 
      path: 'test-results/09-desktop-1920x1080.png', 
      fullPage: true 
    });
    
    // 平板視窗測試 (768x1024)
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: 'test-results/09-tablet-768x1024.png', 
      fullPage: true 
    });
    
    // 手機視窗測試 (375x667)
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: 'test-results/09-mobile-375x667.png', 
      fullPage: true 
    });
    
    // 驗證響應式元素
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('input[placeholder*="Enter stock symbol"]')).toBeVisible();
  });

  // 10. JavaScript錯誤和API連接測試
  test('10. JavaScript Errors and API Connection', async ({ page }) => {
    const errors = [];
    
    // 監聽控制台錯誤
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // 監聽頁面錯誤
    page.on('pageerror', error => {
      errors.push(`Page Error: ${error.message}`);
    });
    
    // 執行各種操作來觸發潛在錯誤
    await page.locator('button:has-text("AAPL")').click();
    await page.waitForTimeout(5000);
    
    await page.locator('input[placeholder*="Enter stock symbol"]').fill('INVALID');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(3000);
    
    // 檢查API連接
    const response = await page.request.get(`${API_URL}/health`);
    console.log(`API Health Check Status: ${response.status()}`);
    
    // 記錄發現的錯誤
    console.log('JavaScript Errors Found:', errors);
    
    await page.screenshot({ 
      path: 'test-results/10-error-testing.png', 
      fullPage: true 
    });
  });

  // 11. 性能測試
  test('11. Performance Testing', async ({ page }) => {
    const startTime = Date.now();
    
    // 測量頁面載入時間
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    console.log(`Page Load Time: ${loadTime}ms`);
    
    // 測量股票搜尋響應時間
    const searchStart = Date.now();
    await page.locator('button:has-text("AAPL")').click();
    await expect(page.locator('text=Analyzing')).toBeVisible();
    await expect(page.locator('text=Analyzing')).toBeHidden({ timeout: 15000 });
    const searchTime = Date.now() - searchStart;
    console.log(`Stock Search Response Time: ${searchTime}ms`);
    
    await page.screenshot({ 
      path: 'test-results/11-performance.png', 
      fullPage: true 
    });
  });
});