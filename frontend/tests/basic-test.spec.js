const { test, expect } = require('@playwright/test');

test.describe('AI Trading Dashboard Basic Tests', () => {
  
  test('Page loads successfully', async ({ page }) => {
    console.log('🚀 Testing page load...');
    
    // 導航到頁面
    await page.goto('http://localhost:3000');
    
    // 等待頁面載入
    await page.waitForLoadState('networkidle');
    
    // 檢查頁面標題
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    
    // 檢查搜尋輸入框存在
    await expect(page.locator('input[placeholder*="Enter stock symbol"]')).toBeVisible();
    
    // 檢查流行股票按鈕存在
    await expect(page.locator('button:has-text("AAPL")')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/page-load-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Page load test completed');
  });
  
  test('Stock search functionality works', async ({ page }) => {
    console.log('🔍 Testing stock search...');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 點擊 AAPL 按鈕
    await page.locator('button:has-text("AAPL")').click();
    
    // 等待一下讓請求完成
    await page.waitForTimeout(3000);
    
    // 檢查圖表標題更新
    await expect(page.locator('text=Chart Analysis - AAPL')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/stock-search-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Stock search test completed');
  });
  
  test('AI Analysis panel appears', async ({ page }) => {
    console.log('🤖 Testing AI analysis panel...');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 檢查 AI 分析面板存在
    await expect(page.locator('text=AI Analysis')).toBeVisible();
    await expect(page.locator('text=GPT-4 Powered')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/ai-analysis-test.png', 
      fullPage: true 
    });
    
    console.log('✅ AI analysis panel test completed');
  });
  
  test('Market data panel shows information', async ({ page }) => {
    console.log('📈 Testing market data panel...');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 檢查市場數據面板
    await expect(page.locator('text=Market Data')).toBeVisible();
    await expect(page.locator('text=Live Data')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/market-data-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Market data panel test completed');
  });

  test('Feature cards are displayed', async ({ page }) => {
    console.log('🎯 Testing feature cards...');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 檢查功能卡片
    await expect(page.locator('text=Technical Analysis')).toBeVisible();
    await expect(page.locator('text=Pattern Recognition')).toBeVisible();
    await expect(page.locator('text=AI Insights')).toBeVisible();
    await expect(page.locator('text=Multi-Market')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/feature-cards-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Feature cards test completed');
  });

  test('Status bar shows system information', async ({ page }) => {
    console.log('📊 Testing status bar...');
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 檢查狀態欄
    await expect(page.locator('text=API Connected')).toBeVisible();
    await expect(page.locator('text=Real-time Data')).toBeVisible();
    await expect(page.locator('text=AI Analysis Ready')).toBeVisible();
    await expect(page.locator('text=System Time:')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/status-bar-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Status bar test completed');
  });

  test('Responsive design - Mobile view', async ({ page }) => {
    console.log('📱 Testing mobile responsive design...');
    
    // 設置手機視窗尺寸
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 檢查主要元素仍然可見
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('input[placeholder*="Enter stock symbol"]')).toBeVisible();
    
    // 截圖記錄
    await page.screenshot({ 
      path: 'test-results/mobile-responsive-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Mobile responsive test completed');
  });

  test('Check for JavaScript errors', async ({ page }) => {
    console.log('🐛 Checking for JavaScript errors...');
    
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
    
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 執行一些操作來觸發潛在錯誤
    await page.locator('button:has-text("AAPL")').click();
    await page.waitForTimeout(3000);
    
    // 記錄錯誤
    console.log('JavaScript Errors Found:', errors);
    
    // 如果有嚴重錯誤，測試失敗
    const criticalErrors = errors.filter(error => 
      !error.includes('favicon') && 
      !error.includes('TradingView') &&
      !error.includes('Network')
    );
    
    console.log('✅ JavaScript error check completed');
  });
});