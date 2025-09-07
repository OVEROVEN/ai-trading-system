const { test, expect } = require('@playwright/test');

test.describe('Trading Price Display Functionality Tests', () => {
  let testReport = {
    timestamp: new Date().toISOString(),
    tests: [],
    errors: [],
    screenshots: [],
    tradingPriceResults: []
  };

  test.beforeEach(async ({ page }) => {
    // Set timeouts and viewport
    page.setDefaultTimeout(30000); // Longer timeout for AI analysis
    page.setDefaultNavigationTimeout(20000);
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Listen for console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log(`Console Error: ${msg.text()}`);
        testReport.errors.push({
          type: 'console',
          message: msg.text(),
          location: msg.location(),
          timestamp: new Date().toISOString()
        });
      }
    });

    // Listen for network failures
    page.on('requestfailed', (request) => {
      console.log(`Network Error: ${request.failure()?.errorText} - ${request.url()}`);
      testReport.errors.push({
        type: 'network',
        message: `${request.failure()?.errorText} - ${request.url()}`,
        timestamp: new Date().toISOString()
      });
    });
  });

  test('Trading Price Display - TSLA Stock Analysis', async ({ page }) => {
    console.log('\\n=== Testing Trading Price Display for TSLA ===');
    
    try {
      // 1. Navigate to the application
      console.log('1. Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });

      // Wait for initial load
      await page.waitForTimeout(3000);
      
      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-01-initial.png',
        fullPage: false 
      });
      console.log('✓ Initial page loaded and screenshot taken');

      // 2. Search for TSLA stock
      console.log('\\n2. Searching for TSLA stock...');
      const result = await searchStock(page, 'TSLA');
      
      if (!result.success) {
        throw new Error(`Failed to search for TSLA: ${result.error}`);
      }
      console.log('✓ TSLA search completed successfully');

      // 3. Wait for AI analysis to complete and check for trading price display
      console.log('\\n3. Waiting for AI analysis and checking trading price display...');
      const tradingPriceResult = await waitAndCheckTradingPriceDisplay(page, 'TSLA');
      
      testReport.tradingPriceResults.push({
        stock: 'TSLA',
        ...tradingPriceResult,
        timestamp: new Date().toISOString()
      });

      // Take screenshot after AI analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-02-tsla-analysis.png',
        fullPage: true 
      });
      console.log('✓ TSLA analysis screenshot taken');

      testReport.tests.push({
        name: 'TSLA Trading Price Display',
        status: 'COMPLETED',
        result: tradingPriceResult
      });

    } catch (error) {
      console.error('TSLA test failed:', error);
      testReport.tests.push({
        name: 'TSLA Trading Price Display',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-error-tsla.png',
        fullPage: true
      });
    }
  });

  test('Trading Price Display - AAPL Stock Analysis', async ({ page }) => {
    console.log('\\n=== Testing Trading Price Display for AAPL ===');
    
    try {
      // Navigate to the application
      console.log('1. Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });

      await page.waitForTimeout(3000);

      // Search for AAPL stock
      console.log('\\n2. Searching for AAPL stock...');
      const result = await searchStock(page, 'AAPL');
      
      if (!result.success) {
        throw new Error(`Failed to search for AAPL: ${result.error}`);
      }
      console.log('✓ AAPL search completed successfully');

      // Wait for AI analysis and check trading price display
      console.log('\\n3. Waiting for AI analysis and checking trading price display...');
      const tradingPriceResult = await waitAndCheckTradingPriceDisplay(page, 'AAPL');
      
      testReport.tradingPriceResults.push({
        stock: 'AAPL',
        ...tradingPriceResult,
        timestamp: new Date().toISOString()
      });

      // Take screenshot after AI analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-03-aapl-analysis.png',
        fullPage: true 
      });
      console.log('✓ AAPL analysis screenshot taken');

      testReport.tests.push({
        name: 'AAPL Trading Price Display',
        status: 'COMPLETED',
        result: tradingPriceResult
      });

    } catch (error) {
      console.error('AAPL test failed:', error);
      testReport.tests.push({
        name: 'AAPL Trading Price Display',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-error-aapl.png',
        fullPage: true
      });
    }
  });

  test('Trading Price Display - Multiple Stock Validation', async ({ page }) => {
    console.log('\\n=== Testing Trading Price Display for Multiple Stocks ===');
    
    const testStocks = ['GOOGL', 'META', 'NVDA'];
    
    try {
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });

      for (const stock of testStocks) {
        console.log(`\\n--- Testing ${stock} ---`);
        
        try {
          // Search for stock
          const result = await searchStock(page, stock);
          if (!result.success) {
            console.log(`⚠️ Failed to search for ${stock}: ${result.error}`);
            continue;
          }

          // Check trading price display
          const tradingPriceResult = await waitAndCheckTradingPriceDisplay(page, stock, 20000); // Shorter timeout for multiple tests
          
          testReport.tradingPriceResults.push({
            stock: stock,
            ...tradingPriceResult,
            timestamp: new Date().toISOString()
          });

          // Take screenshot
          await page.screenshot({ 
            path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-04-${stock.toLowerCase()}-analysis.png`,
            fullPage: true 
          });
          
          console.log(`✓ ${stock} analysis completed`);
          
          // Short delay between stocks
          await page.waitForTimeout(2000);
          
        } catch (error) {
          console.log(`❌ ${stock} test failed: ${error.message}`);
          testReport.tradingPriceResults.push({
            stock: stock,
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
          });
        }
      }

      testReport.tests.push({
        name: 'Multiple Stock Trading Price Display',
        status: 'COMPLETED',
        testedStocks: testStocks.length,
        successfulStocks: testReport.tradingPriceResults.filter(r => r.success).length
      });

    } catch (error) {
      console.error('Multiple stock test failed:', error);
      testReport.tests.push({
        name: 'Multiple Stock Trading Price Display',
        status: 'FAILED',
        error: error.message
      });
    }
  });

  // Helper function to search for a stock
  async function searchStock(page, symbol) {
    try {
      // Look for popular stock button first
      const stockButton = page.locator(`button:has-text("${symbol}")`).first();
      if (await stockButton.count() > 0) {
        await stockButton.click();
        return { success: true, method: 'popular button' };
      }

      // Look for search input with multiple selectors
      const searchSelectors = [
        'input[placeholder*="symbol" i]',
        'input[placeholder*="search" i]', 
        'input[type="text"]',
        '.stock-search input',
        '[data-testid="stock-search"] input'
      ];
      
      let searchInput = null;
      for (const selector of searchSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 3000 });
          searchInput = page.locator(selector).first();
          break;
        } catch (e) {
          // Try next selector
        }
      }

      if (searchInput) {
        await searchInput.clear();
        await searchInput.fill(symbol);
        await searchInput.press('Enter');
        return { success: true, method: 'search input' };
      }

      return { success: false, error: 'No search method found' };
      
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Helper function to wait for AI analysis and check trading price display
  async function waitAndCheckTradingPriceDisplay(page, symbol, timeout = 45000) {
    console.log(`Waiting for AI analysis to complete for ${symbol}...`);
    
    const result = {
      success: false,
      aiAnalysisCompleted: false,
      tradingPriceDisplayed: false,
      tradingPriceElements: {
        entryPrice: null,
        targetPrice: null,
        stopLoss: null,
        potentialReturn: null
      },
      elementCounts: {
        aiAnalysisPanel: 0,
        tradingPriceSection: 0,
        entryPriceElements: 0,
        targetPriceElements: 0,
        stopLossElements: 0,
        potentialReturnElements: 0
      }
    };

    try {
      // Wait for AI analysis panel to be visible
      console.log(`Checking for AI analysis panel...`);
      await page.waitForSelector('.bg-slate-800\\/50', { timeout: 10000 });
      result.elementCounts.aiAnalysisPanel = await page.locator('.bg-slate-800\\/50').count();
      
      // Look for loading state completion
      console.log(`Waiting for analysis completion...`);
      let analysisCompleted = false;
      const startTime = Date.now();
      
      while (!analysisCompleted && (Date.now() - startTime) < timeout) {
        // Check if loading spinner is gone
        const loadingSpinner = page.locator('.animate-spin');
        const spinnerCount = await loadingSpinner.count();
        
        // Check if we have analysis results (not just loading)
        const analysisPanel = page.locator('[data-testid="ai-analysis"], .bg-slate-800\\/50').first();
        const panelText = await analysisPanel.textContent().catch(() => '');
        
        // Check for completion indicators
        const hasRecommendation = panelText.includes('推薦') || panelText.includes('recommendation') || panelText.includes('BUY') || panelText.includes('SELL') || panelText.includes('HOLD');
        const hasAnalysisContent = panelText.length > 200; // Substantial content
        const noSpinner = spinnerCount === 0;
        
        if (hasRecommendation && hasAnalysisContent && noSpinner) {
          analysisCompleted = true;
          result.aiAnalysisCompleted = true;
          console.log(`✓ AI analysis completed for ${symbol}`);
          break;
        }
        
        await page.waitForTimeout(2000); // Check every 2 seconds
      }
      
      if (!analysisCompleted) {
        console.log(`⚠️ AI analysis may not have completed within timeout for ${symbol}`);
      }

      // Now check for trading price display elements
      console.log(`Checking for trading price display elements...`);
      
      // Look for the trading price section
      const tradingPriceSection = page.locator('h4:has-text("交易價位建議"), h4:has-text("Trading Price Levels")').locator('..');
      result.elementCounts.tradingPriceSection = await tradingPriceSection.count();
      
      if (result.elementCounts.tradingPriceSection > 0) {
        result.tradingPriceDisplayed = true;
        console.log(`✓ Trading price section found for ${symbol}`);
        
        // Check for specific trading price elements
        const entryPriceElements = page.locator('span:has-text("🎯"), span:has-text("建議進場價"), span:has-text("Entry Price")');
        result.elementCounts.entryPriceElements = await entryPriceElements.count();
        
        if (result.elementCounts.entryPriceElements > 0) {
          const entryPriceText = await entryPriceElements.first().locator('..').textContent();
          result.tradingPriceElements.entryPrice = entryPriceText;
          console.log(`✓ Entry price element found: ${entryPriceText}`);
        }
        
        const targetPriceElements = page.locator('span:has-text("🚀"), span:has-text("目標價位"), span:has-text("Target Price")');
        result.elementCounts.targetPriceElements = await targetPriceElements.count();
        
        if (result.elementCounts.targetPriceElements > 0) {
          const targetPriceText = await targetPriceElements.first().locator('..').textContent();
          result.tradingPriceElements.targetPrice = targetPriceText;
          console.log(`✓ Target price element found: ${targetPriceText}`);
        }
        
        const stopLossElements = page.locator('span:has-text("🛑"), span:has-text("停損價位"), span:has-text("Stop Loss")');
        result.elementCounts.stopLossElements = await stopLossElements.count();
        
        if (result.elementCounts.stopLossElements > 0) {
          const stopLossText = await stopLossElements.first().locator('..').textContent();
          result.tradingPriceElements.stopLoss = stopLossText;
          console.log(`✓ Stop loss element found: ${stopLossText}`);
        }
        
        const potentialReturnElements = page.locator('span:has-text("📈"), span:has-text("潛在報酬"), span:has-text("Potential Return")');
        result.elementCounts.potentialReturnElements = await potentialReturnElements.count();
        
        if (result.elementCounts.potentialReturnElements > 0) {
          const potentialReturnText = await potentialReturnElements.first().locator('..').textContent();
          result.tradingPriceElements.potentialReturn = potentialReturnText;
          console.log(`✓ Potential return element found: ${potentialReturnText}`);
        }
        
        // Check if we have at least 2 of the 4 key elements
        const keyElementsFound = [
          result.elementCounts.entryPriceElements > 0,
          result.elementCounts.targetPriceElements > 0,
          result.elementCounts.stopLossElements > 0,
          result.elementCounts.potentialReturnElements > 0
        ].filter(Boolean).length;
        
        if (keyElementsFound >= 2) {
          result.success = true;
          console.log(`✅ Trading price display validation successful for ${symbol} (${keyElementsFound}/4 key elements found)`);
        } else {
          console.log(`⚠️ Trading price display incomplete for ${symbol} (${keyElementsFound}/4 key elements found)`);
        }
        
      } else {
        console.log(`❌ Trading price section not found for ${symbol}`);
      }
      
    } catch (error) {
      console.error(`Error checking trading price display for ${symbol}:`, error);
      result.error = error.message;
    }
    
    return result;
  }

  test.afterAll(async () => {
    // Generate comprehensive test report
    const summary = {
      timestamp: testReport.timestamp,
      totalTests: testReport.tests.length,
      completedTests: testReport.tests.filter(t => t.status === 'COMPLETED').length,
      failedTests: testReport.tests.filter(t => t.status === 'FAILED').length,
      totalErrors: testReport.errors.length,
      tradingPriceTestResults: {
        totalStocksTested: testReport.tradingPriceResults.length,
        successfulTradingPriceDisplays: testReport.tradingPriceResults.filter(r => r.success).length,
        stocksWithAIAnalysis: testReport.tradingPriceResults.filter(r => r.aiAnalysisCompleted).length,
        stocksWithTradingPriceSection: testReport.tradingPriceResults.filter(r => r.tradingPriceDisplayed).length
      }
    };

    console.log('\\n=== TRADING PRICE DISPLAY TEST REPORT ===');
    console.log(`Timestamp: ${summary.timestamp}`);
    console.log(`Total Tests: ${summary.totalTests}`);
    console.log(`Completed: ${summary.completedTests}`);
    console.log(`Failed: ${summary.failedTests}`);
    console.log(`Total Errors: ${summary.totalErrors}`);
    
    console.log('\\n=== TRADING PRICE DISPLAY RESULTS ===');
    console.log(`Total Stocks Tested: ${summary.tradingPriceTestResults.totalStocksTested}`);
    console.log(`Successful Trading Price Displays: ${summary.tradingPriceTestResults.successfulTradingPriceDisplays}`);
    console.log(`Stocks with AI Analysis: ${summary.tradingPriceTestResults.stocksWithAIAnalysis}`);
    console.log(`Stocks with Trading Price Section: ${summary.tradingPriceTestResults.stocksWithTradingPriceSection}`);

    if (testReport.errors.length > 0) {
      console.log('\\n=== ERRORS FOUND ===');
      testReport.errors.forEach((error, i) => {
        console.log(`${i + 1}. [${error.type.toUpperCase()}] ${error.message}`);
      });
    }

    // Detailed stock-by-stock results
    console.log('\\n=== DETAILED STOCK RESULTS ===');
    testReport.tradingPriceResults.forEach(result => {
      console.log(`\\n${result.stock}:`);
      console.log(`  - Success: ${result.success ? '✅' : '❌'}`);
      console.log(`  - AI Analysis Completed: ${result.aiAnalysisCompleted ? '✅' : '❌'}`);
      console.log(`  - Trading Price Displayed: ${result.tradingPriceDisplayed ? '✅' : '❌'}`);
      
      if (result.elementCounts) {
        console.log(`  - Element Counts:`);
        console.log(`    * AI Analysis Panel: ${result.elementCounts.aiAnalysisPanel}`);
        console.log(`    * Trading Price Section: ${result.elementCounts.tradingPriceSection}`);
        console.log(`    * Entry Price Elements: ${result.elementCounts.entryPriceElements}`);
        console.log(`    * Target Price Elements: ${result.elementCounts.targetPriceElements}`);
        console.log(`    * Stop Loss Elements: ${result.elementCounts.stopLossElements}`);
        console.log(`    * Potential Return Elements: ${result.elementCounts.potentialReturnElements}`);
      }
      
      if (result.tradingPriceElements) {
        console.log(`  - Trading Price Values:`);
        if (result.tradingPriceElements.entryPrice) {
          console.log(`    * Entry Price: ${result.tradingPriceElements.entryPrice.replace(/\\n/g, ' ').trim()}`);
        }
        if (result.tradingPriceElements.targetPrice) {
          console.log(`    * Target Price: ${result.tradingPriceElements.targetPrice.replace(/\\n/g, ' ').trim()}`);
        }
        if (result.tradingPriceElements.stopLoss) {
          console.log(`    * Stop Loss: ${result.tradingPriceElements.stopLoss.replace(/\\n/g, ' ').trim()}`);
        }
        if (result.tradingPriceElements.potentialReturn) {
          console.log(`    * Potential Return: ${result.tradingPriceElements.potentialReturn.replace(/\\n/g, ' ').trim()}`);
        }
      }
      
      if (result.error) {
        console.log(`  - Error: ${result.error}`);
      }
    });

    // Save detailed report
    const fs = require('fs');
    const detailedReport = {
      summary,
      tests: testReport.tests,
      errors: testReport.errors,
      tradingPriceResults: testReport.tradingPriceResults,
      generatedAt: new Date().toISOString()
    };

    fs.writeFileSync(
      '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/trading-price-display-report.json',
      JSON.stringify(detailedReport, null, 2)
    );

    console.log('\\n📊 Detailed report saved to: test-results/trading-price-display-report.json');
    console.log('📸 Screenshots available in: test-results/');
    console.log('\\n=== TEST COMPLETED ===');
  });
});