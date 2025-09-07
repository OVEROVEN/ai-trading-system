const { test, expect } = require('@playwright/test');

test.describe('Dashboard Functionality Verification', () => {
  test('Complete Dashboard Testing', async ({ page }) => {
    console.log('🚀 Starting Dashboard Functionality Test...');
    
    // Navigate to dashboard
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000); // Give it time to load
    
    // Take initial screenshot
    await page.screenshot({ 
      path: 'test-results/dashboard-initial.png', 
      fullPage: true 
    });
    console.log('✅ Page loaded');
    
    // Test 1: Verify basic elements
    console.log('1️⃣ Testing basic page elements...');
    await expect(page.locator('h1:has-text("AI Trading Dashboard")')).toBeVisible();
    await expect(page.locator('text=Advanced Stock Analysis')).toBeVisible();
    
    // Test 2: Test AAPL stock
    console.log('2️⃣ Testing AAPL stock...');
    await page.locator('button:has-text("AAPL")').click();
    await page.waitForTimeout(4000);
    
    // Check if chart section exists
    await expect(page.locator('h2:has-text("Chart Analysis")')).toBeVisible();
    await page.screenshot({ 
      path: 'test-results/dashboard-aapl.png', 
      fullPage: true 
    });
    
    // Test 3: Test Taiwan stock
    console.log('3️⃣ Testing Taiwan stock 2330.TW...');
    const searchInput = page.locator('input[placeholder*="Enter stock symbol"]');
    await searchInput.fill('2330.TW');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(4000);
    
    await page.screenshot({ 
      path: 'test-results/dashboard-taiwan.png', 
      fullPage: true 
    });
    
    // Test 4: Test TSLA
    console.log('4️⃣ Testing TSLA stock...');
    await searchInput.fill('TSLA');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(4000);
    
    await page.screenshot({ 
      path: 'test-results/dashboard-tsla.png', 
      fullPage: true 
    });
    
    // Test 5: Test invalid symbol
    console.log('5️⃣ Testing invalid symbol...');
    await searchInput.fill('INVALID123');
    await page.locator('button:has-text("Analyze")').click();
    await page.waitForTimeout(3000);
    
    await page.screenshot({ 
      path: 'test-results/dashboard-invalid.png', 
      fullPage: true 
    });
    
    // Test 6: Test other popular stocks
    console.log('6️⃣ Testing other stocks...');
    const stocks = ['GOOGL', 'MSFT', 'NVDA'];
    
    for (const stock of stocks) {
      console.log(`   Testing ${stock}...`);
      await page.locator(`button:has-text("${stock}")`).click();
      await page.waitForTimeout(3000);
      
      await page.screenshot({ 
        path: `test-results/dashboard-${stock.toLowerCase()}.png`, 
        fullPage: true 
      });
    }
    
    // Test 7: Check panels
    console.log('7️⃣ Checking dashboard panels...');
    await expect(page.locator('h3:has-text("Market Data")')).toBeVisible();
    await expect(page.locator('h3:has-text("AI Analysis")')).toBeVisible();
    await expect(page.locator('h3:has-text("Performance")')).toBeVisible();
    
    // Test 8: Check status indicators
    console.log('8️⃣ Checking status indicators...');
    await expect(page.locator('text=API Connected')).toBeVisible();
    await expect(page.locator('text=Real-time Data').first()).toBeVisible();
    
    // Test 9: Mobile view
    console.log('9️⃣ Testing mobile responsive...');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    await page.screenshot({ 
      path: 'test-results/dashboard-mobile.png', 
      fullPage: true 
    });
    
    // Reset viewport
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(1000);
    
    console.log('🎉 All tests completed successfully!');
  });
});