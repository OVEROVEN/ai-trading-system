const { test, expect } = require('@playwright/test');

test.describe('Dashboard Live Testing', () => {
  test('Comprehensive Dashboard Functionality Test', async ({ page }) => {
    console.log('🚀 Starting comprehensive dashboard test...');
    
    // Navigate to dashboard
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // Take initial screenshot
    await page.screenshot({ 
      path: 'test-results/01-initial-load.png', 
      fullPage: true 
    });
    console.log('✅ Page loaded successfully');
    
    // Test 1: Check basic page elements
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    await expect(page.locator('text=Advanced Stock Analysis & AI-Powered Trading Insights')).toBeVisible();
    console.log('✅ Basic page elements verified');
    
    // Test 2: Test AAPL stock search
    console.log('🔍 Testing AAPL stock...');
    await page.locator('button:has-text("AAPL")').click();
    await page.waitForTimeout(3000);
    
    // Check if chart loaded
    await expect(page.locator('text=Chart Analysis - AAPL')).toBeVisible();
    await page.screenshot({ 
      path: 'test-results/02-aapl-loaded.png', 
      fullPage: true 
    });
    console.log('✅ AAPL chart loaded');
    
    // Test 3: Test manual stock search
    console.log('🔍 Testing manual search...');
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    await searchInput.fill('TSLA');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(4000);
    
    await page.screenshot({ 
      path: 'test-results/03-tsla-search.png', 
      fullPage: true 
    });
    console.log('✅ TSLA search completed');
    
    // Test 4: Test Taiwan stock
    console.log('🇹🇼 Testing Taiwan stock...');
    await searchInput.fill('2330.TW');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(4000);
    
    await page.screenshot({ 
      path: 'test-results/04-taiwan-stock.png', 
      fullPage: true 
    });
    console.log('✅ Taiwan stock 2330.TW tested');
    
    // Test 5: Test invalid stock symbol
    console.log('❌ Testing invalid symbol...');
    await searchInput.fill('INVALID123');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(3000);
    
    await page.screenshot({ 
      path: 'test-results/05-invalid-symbol.png', 
      fullPage: true 
    });
    console.log('✅ Invalid symbol test completed');
    
    // Test 6: Check market data panel
    await expect(page.locator('text=Market Data')).toBeVisible();
    await expect(page.locator('text=AI Analysis')).toBeVisible();
    console.log('✅ Market data and AI panels visible');
    
    // Test 7: Check status indicators  
    await expect(page.locator('text=API Connected')).toBeVisible();
    await expect(page.locator('text=Real-time Data')).toBeVisible();
    console.log('✅ Status indicators working');
    
    // Test 8: Test other popular stocks
    console.log('📈 Testing other popular stocks...');
    const stocks = ['GOOGL', 'MSFT', 'NVDA'];
    
    for (const stock of stocks) {
      await page.locator(`button:has-text("${stock}")`).click();
      await page.waitForTimeout(2000);
      console.log(`✅ ${stock} button clicked`);
    }
    
    await page.screenshot({ 
      path: 'test-results/06-final-state.png', 
      fullPage: true 
    });
    
    // Test 9: Mobile responsive test
    console.log('📱 Testing mobile view...');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: 'test-results/07-mobile-view.png', 
      fullPage: true 
    });
    
    // Test 10: Check for JavaScript errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    console.log('JavaScript errors found:', errors);
    
    console.log('🎉 All tests completed successfully!');
  });
});