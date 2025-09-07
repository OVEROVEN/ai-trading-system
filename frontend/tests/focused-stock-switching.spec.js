const { test, expect } = require('@playwright/test');

test.describe('Stock Switching Functionality - Focused Tests', () => {
  let testReport = {
    timestamp: new Date().toISOString(),
    tests: [],
    errors: [],
    screenshots: []
  };

  test.beforeEach(async ({ page }) => {
    // Set shorter timeouts and less strict waiting
    page.setDefaultTimeout(15000);
    page.setDefaultNavigationTimeout(15000);
    
    // Set viewport for consistent screenshots
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Listen for console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        console.log(`Console Error: ${msg.text()}`);
        testReport.errors.push({
          type: 'console',
          message: msg.text(),
          location: msg.location()
        });
      }
    });
  });

  test('Main Dashboard Stock Switching Test', async ({ page }) => {
    console.log('\n=== Testing Main Dashboard Stock Switching ===');
    
    try {
      // Navigate with less strict waiting
      console.log('Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });

      // Wait a bit for initial load
      await page.waitForTimeout(3000);
      
      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/01-initial-dashboard.png',
        fullPage: false 
      });

      // Look for stock search components with multiple selectors
      const stockSearchSelectors = [
        'input[placeholder*="symbol" i]',
        'input[placeholder*="search" i]', 
        'input[type="text"]',
        '.stock-search input',
        '[data-testid="stock-search"] input'
      ];
      
      let searchInput = null;
      for (const selector of stockSearchSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 3000 });
          searchInput = page.locator(selector).first();
          console.log(`Found search input with selector: ${selector}`);
          break;
        } catch (e) {
          console.log(`Selector ${selector} not found, trying next...`);
        }
      }

      if (!searchInput) {
        console.log('No search input found, looking for popular stock buttons...');
      }

      // Test switching between stocks: AAPL → TSLA → GOOGL → META
      const stocks = ['AAPL', 'TSLA', 'GOOGL', 'META'];
      let switchingResults = [];

      for (const stock of stocks) {
        console.log(`\\nTesting switch to ${stock}...`);
        let switched = false;
        let method = '';

        // Method 1: Try clicking popular stock button
        const stockButton = page.locator(`button:has-text("${stock}")`).first();
        try {
          await stockButton.waitFor({ state: 'visible', timeout: 2000 });
          await stockButton.click();
          method = 'popular button';
          switched = true;
          console.log(`Clicked ${stock} popular button`);
        } catch (e) {
          console.log(`No popular button found for ${stock}`);
        }

        // Method 2: Try using search input
        if (!switched && searchInput) {
          try {
            await searchInput.clear();
            await searchInput.fill(stock);
            await searchInput.press('Enter');
            method = 'search input';
            switched = true;
            console.log(`Entered ${stock} in search input`);
          } catch (e) {
            console.log(`Failed to use search input for ${stock}: ${e.message}`);
          }
        }

        // Wait for potential updates
        await page.waitForTimeout(2000);

        // Check what updated
        const results = {
          stock: stock,
          switched: switched,
          method: method,
          checks: {}
        };

        // Check for TradingView components
        try {
          const tradingViewElements = await page.locator('[id*="tradingview"], script[src*="tradingview"], iframe[src*="tradingview"]').count();
          results.checks.tradingViewElements = tradingViewElements;
          console.log(`${stock} - TradingView elements found: ${tradingViewElements}`);
        } catch (e) {
          results.checks.tradingViewElements = 0;
        }

        // Check for stock symbol in page
        try {
          const symbolInPage = await page.locator(`text=${stock}`).count();
          results.checks.symbolDisplayed = symbolInPage > 0;
          console.log(`${stock} - Symbol appears on page: ${symbolInPage > 0}`);
        } catch (e) {
          results.checks.symbolDisplayed = false;
        }

        // Check for data panels
        const panelSelectors = [
          '.market-data, [data-testid="market-data"]',
          '.ai-analysis, [data-testid="ai-analysis"]',
          '.performance, [data-testid="performance"]',
          '.bg-slate-800'
        ];
        
        let panelsFound = 0;
        for (const selector of panelSelectors) {
          try {
            const count = await page.locator(selector).count();
            panelsFound += count;
          } catch (e) {
            // Ignore
          }
        }
        results.checks.dataPanelsFound = panelsFound;
        console.log(`${stock} - Data panels found: ${panelsFound}`);

        // Take screenshot for this stock
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/02-stock-${stock}.png`,
          fullPage: false
        });

        switchingResults.push(results);
      }

      testReport.tests.push({
        name: 'Main Dashboard Stock Switching',
        status: 'COMPLETED',
        results: switchingResults,
        summary: {
          totalStocks: stocks.length,
          successfulSwitches: switchingResults.filter(r => r.switched).length,
          stocksWithTradingView: switchingResults.filter(r => r.checks.tradingViewElements > 0).length,
          stocksWithSymbolDisplayed: switchingResults.filter(r => r.checks.symbolDisplayed).length
        }
      });

      console.log('\\n=== Main Dashboard Test Summary ===');
      console.log(`Total stocks tested: ${stocks.length}`);
      console.log(`Successful switches: ${switchingResults.filter(r => r.switched).length}`);
      console.log(`Stocks with TradingView: ${switchingResults.filter(r => r.checks.tradingViewElements > 0).length}`);

    } catch (error) {
      console.error('Main dashboard test failed:', error);
      testReport.tests.push({
        name: 'Main Dashboard Stock Switching',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/error-main-dashboard.png'
      });
    }
  });

  test('Custom Chart Interface Test', async ({ page }) => {
    console.log('\\n=== Testing Custom Chart Interface ===');
    
    const stocks = ['AAPL', 'TSLA', 'GOOGL', 'META'];
    let customChartResults = [];

    for (const stock of stocks) {
      console.log(`Testing custom chart for ${stock}...`);
      const url = `http://localhost:8000/chart/custom/${stock}`;
      
      try {
        const response = await page.goto(url, { 
          waitUntil: 'domcontentloaded',
          timeout: 10000 
        });
        
        await page.waitForTimeout(2000);
        
        const result = {
          stock: stock,
          url: url,
          status: response?.status() || 'unknown',
          loaded: response?.ok() || false
        };

        // Check page content
        try {
          const pageText = await page.textContent('body');
          result.hasSymbol = pageText?.includes(stock) || false;
          result.hasChart = pageText?.includes('chart') || pageText?.includes('trading') || false;
        } catch (e) {
          result.hasSymbol = false;
          result.hasChart = false;
        }

        // Take screenshot
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/03-custom-${stock}.png`
        });

        customChartResults.push(result);
        console.log(`${stock} - Status: ${result.status}, Symbol shown: ${result.hasSymbol}`);

      } catch (error) {
        console.error(`Custom chart test failed for ${stock}:`, error.message);
        customChartResults.push({
          stock: stock,
          url: url,
          status: 'error',
          error: error.message,
          loaded: false
        });
      }
    }

    testReport.tests.push({
      name: 'Custom Chart Interface',
      status: 'COMPLETED', 
      results: customChartResults,
      summary: {
        totalTests: stocks.length,
        successfulLoads: customChartResults.filter(r => r.loaded).length,
        chartsWithSymbol: customChartResults.filter(r => r.hasSymbol).length
      }
    });

    console.log('\\n=== Custom Chart Test Summary ===');
    console.log(`Total endpoints tested: ${stocks.length}`);
    console.log(`Successfully loaded: ${customChartResults.filter(r => r.loaded).length}`);
  });

  test('TradingView Widget Analysis', async ({ page }) => {
    console.log('\\n=== Testing TradingView Widget Behavior ===');
    
    try {
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });

      await page.waitForTimeout(5000); // Wait for TradingView to potentially load

      // Analyze TradingView integration
      const tradingViewAnalysis = {
        scriptTags: 0,
        containers: 0,
        iframes: 0,
        errors: []
      };

      // Check for TradingView script tags
      try {
        tradingViewAnalysis.scriptTags = await page.locator('script[src*="tradingview"]').count();
        console.log(`TradingView script tags: ${tradingViewAnalysis.scriptTags}`);
      } catch (e) {
        tradingViewAnalysis.errors.push(`Script check failed: ${e.message}`);
      }

      // Check for TradingView containers
      try {
        tradingViewAnalysis.containers = await page.locator('[id*="tradingview"]').count();
        console.log(`TradingView containers: ${tradingViewAnalysis.containers}`);
        
        // Get container IDs if any
        const containers = await page.locator('[id*="tradingview"]').all();
        const containerIds = [];
        for (const container of containers) {
          const id = await container.getAttribute('id');
          if (id) containerIds.push(id);
        }
        tradingViewAnalysis.containerIds = containerIds;
        console.log(`Container IDs: ${containerIds.join(', ')}`);
      } catch (e) {
        tradingViewAnalysis.errors.push(`Container check failed: ${e.message}`);
      }

      // Check for TradingView iframes  
      try {
        tradingViewAnalysis.iframes = await page.locator('iframe[src*="tradingview"]').count();
        console.log(`TradingView iframes: ${tradingViewAnalysis.iframes}`);
      } catch (e) {
        tradingViewAnalysis.errors.push(`Iframe check failed: ${e.message}`);
      }

      // Test symbol switching impact on TradingView
      const switchTest = [];
      try {
        const testStocks = ['AAPL', 'TSLA'];
        for (const stock of testStocks) {
          const stockButton = page.locator(`button:has-text("${stock}")`).first();
          if (await stockButton.count() > 0) {
            await stockButton.click();
            await page.waitForTimeout(3000);
            
            const containersAfterSwitch = await page.locator('[id*="tradingview"]').count();
            switchTest.push({
              stock: stock,
              containersAfter: containersAfterSwitch,
              timestamp: Date.now()
            });
            console.log(`After switching to ${stock}: ${containersAfterSwitch} containers`);
          }
        }
      } catch (e) {
        tradingViewAnalysis.errors.push(`Switch test failed: ${e.message}`);
      }

      tradingViewAnalysis.switchTest = switchTest;

      testReport.tests.push({
        name: 'TradingView Widget Analysis',
        status: 'COMPLETED',
        results: tradingViewAnalysis
      });

    } catch (error) {
      console.error('TradingView analysis failed:', error);
      testReport.tests.push({
        name: 'TradingView Widget Analysis',
        status: 'FAILED',
        error: error.message
      });
    }
  });

  test.afterAll(async () => {
    // Generate final report
    const summary = {
      timestamp: testReport.timestamp,
      totalTests: testReport.tests.length,
      completedTests: testReport.tests.filter(t => t.status === 'COMPLETED').length,
      failedTests: testReport.tests.filter(t => t.status === 'FAILED').length,
      totalErrors: testReport.errors.length
    };

    console.log('\\n=== STOCK SWITCHING TEST REPORT ===');
    console.log(`Timestamp: ${summary.timestamp}`);
    console.log(`Total Tests: ${summary.totalTests}`);
    console.log(`Completed: ${summary.completedTests}`);
    console.log(`Failed: ${summary.failedTests}`);
    console.log(`Total Errors: ${summary.totalErrors}`);

    if (testReport.errors.length > 0) {
      console.log('\\nErrors Found:');
      testReport.errors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.message}`);
      });
    }

    // Detailed findings
    const mainDashboardTest = testReport.tests.find(t => t.name === 'Main Dashboard Stock Switching');
    if (mainDashboardTest && mainDashboardTest.results) {
      console.log('\\n=== MAIN DASHBOARD FINDINGS ===');
      mainDashboardTest.results.forEach(result => {
        console.log(`${result.stock}:`);
        console.log(`  - Switched successfully: ${result.switched} (via ${result.method})`);
        console.log(`  - TradingView elements: ${result.checks.tradingViewElements}`);
        console.log(`  - Symbol displayed: ${result.checks.symbolDisplayed}`);
        console.log(`  - Data panels: ${result.checks.dataPanelsFound}`);
      });
    }

    const customChartTest = testReport.tests.find(t => t.name === 'Custom Chart Interface');
    if (customChartTest && customChartTest.results) {
      console.log('\\n=== CUSTOM CHART FINDINGS ===');
      customChartTest.results.forEach(result => {
        console.log(`${result.stock}: Status ${result.status}, Symbol shown: ${result.hasSymbol}`);
      });
    }

    // Save detailed report
    const fs = require('fs');
    const detailedReport = {
      summary,
      tests: testReport.tests,
      errors: testReport.errors,
      generatedAt: new Date().toISOString()
    };

    fs.writeFileSync(
      '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/focused-stock-switching-report.json',
      JSON.stringify(detailedReport, null, 2)
    );

    console.log('\\nDetailed report saved to: test-results/focused-stock-switching-report.json');
    console.log('Screenshots available in: test-results/');
  });
});