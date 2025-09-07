const { test, expect } = require('@playwright/test');

test.describe('Quick Dashboard Functionality Test', () => {
  test('Basic functionality works', async ({ page }) => {
    console.log('🚀 Quick test starting...');
    
    // 訪問dashboard
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000); // 等待3秒載入
    
    console.log('✅ Page loaded');
    
    // 測試股票切換
    console.log('📈 Testing AAPL...');
    await page.click('button:has-text("AAPL")');
    await page.waitForTimeout(2000);
    
    console.log('📈 Testing GOOGL...');
    await page.click('button:has-text("GOOGL")');
    await page.waitForTimeout(2000);
    
    console.log('📈 Testing Taiwan stock 2330.TW...');
    await page.click('button:has-text("2330.TW")');
    await page.waitForTimeout(2000);
    
    // 測試搜尋功能
    console.log('🔍 Testing search...');
    const searchInput = page.locator('input[type="text"]').first();
    await searchInput.fill('TSLA');
    await page.click('button:has-text("Analyze")');
    await page.waitForTimeout(3000);
    
    console.log('❌ Testing invalid symbol...');
    await searchInput.fill('INVALID123');
    await page.click('button:has-text("Analyze")');
    await page.waitForTimeout(3000);
    
    // 截圖保存結果
    await page.screenshot({ path: 'test-results/quick-test-final.png', fullPage: true });
    
    console.log('✅ Quick test completed successfully!');
  });
});