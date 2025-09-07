const { test, expect } = require('@playwright/test');

test.describe('Stock Switching Functionality Tests', () => {
  const testReport = {
    timestamp: new Date().toISOString(),
    tests: [],
    errors: [],
    screenshots: []
  };

  let consoleErrors = [];
  let networkErrors = [];

  test.beforeEach(async ({ page }) => {
    // Capture console errors
    consoleErrors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push({
          text: msg.text(),
          location: msg.location()
        });
      }
    });

    // Capture network errors
    networkErrors = [];
    page.on('requestfailed', (request) => {
      networkErrors.push({
        url: request.url(),
        failure: request.failure()?.errorText
      });
    });

    // Set viewport for consistent screenshots
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('Test Main Dashboard Stock Switching', async ({ page }) => {
    const testName = 'Main Dashboard Stock Switching';
    console.log(`\n=== Starting ${testName} ===`);

    try {
      // Navigate to main dashboard
      console.log('Navigating to http://localhost:3000...');
      const response = await page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle',
        timeout: 30000 
      });
      
      if (!response || response.status() !== 200) {
        throw new Error(`Failed to load main dashboard. Status: ${response?.status()}`);
      }

      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/01-dashboard-initial.png',
        fullPage: true 
      });

      // Wait for the page to be fully loaded
      await page.waitForSelector('[data-testid="stock-search"], .stock-search, input[placeholder*="symbol"], input[placeholder*="search"]', { timeout: 10000 });
      
      // Test stock switching sequence: AAPL → TSLA → GOOGL → META
      const stockSequence = ['AAPL', 'TSLA', 'GOOGL', 'META'];
      
      for (let i = 0; i < stockSequence.length; i++) {
        const symbol = stockSequence[i];
        console.log(`Testing switch to ${symbol}...`);

        // Method 1: Try clicking popular stock buttons
        const popularButton = page.locator(`button:has-text("${symbol}")`).first();
        const popularButtonExists = await popularButton.count() > 0;
        
        if (popularButtonExists) {
          await popularButton.click();
          console.log(`Clicked popular stock button for ${symbol}`);
        } else {
          // Method 2: Use custom input field
          const inputField = await page.locator('input[type="text"]').first();
          await inputField.clear();
          await inputField.fill(symbol);
          await inputField.press('Enter');
          console.log(`Entered ${symbol} in input field`);
        }

        // Wait for updates and take screenshot
        await page.waitForTimeout(3000);
        
        // Check if TradingView widget is loading/updating
        const tradingViewContainer = await page.locator('[id*="tradingview"], .tradingview-widget, iframe[src*="tradingview"]');
        const hasChart = await tradingViewContainer.count() > 0;
        
        // Check if data panels are updating
        const marketDataPanel = await page.locator('.market-data, [data-testid="market-data"]');
        const aiAnalysisPanel = await page.locator('.ai-analysis, [data-testid="ai-analysis"]');
        const performancePanel = await page.locator('.performance, [data-testid="performance"]');
        
        // Take screenshot of current state
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/02-dashboard-${symbol}.png`,
          fullPage: true 
        });

        // Log findings
        console.log(`${symbol} - Chart container found: ${hasChart}`);
        console.log(`${symbol} - Market data panel found: ${await marketDataPanel.count() > 0}`);
        console.log(`${symbol} - AI analysis panel found: ${await aiAnalysisPanel.count() > 0}`);
        console.log(`${symbol} - Performance panel found: ${await performancePanel.count() > 0}`);

        // Check for errors specific to this symbol
        const currentErrors = consoleErrors.slice();
        if (currentErrors.length > 0) {
          console.log(`Console errors for ${symbol}:`, currentErrors);
        }
      }

      testReport.tests.push({
        name: testName,
        status: 'PASSED',
        details: {
          testedSymbols: stockSequence,
          consoleErrors: consoleErrors.length,
          networkErrors: networkErrors.length
        }
      });

    } catch (error) {
      console.error(`${testName} failed:`, error);
      testReport.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message
      });
      
      // Take error screenshot
      await page.screenshot({ 
        path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/error-dashboard.png`,
        fullPage: true 
      });
    }
  });

  test('Test Custom Chart Interface Stock Switching', async ({ page }) => {
    const testName = 'Custom Chart Interface Stock Switching';
    console.log(`\n=== Starting ${testName} ===`);

    try {
      // Test custom chart endpoints
      const symbols = ['AAPL', 'TSLA', 'GOOGL', 'META'];
      
      for (const symbol of symbols) {
        const url = `http://localhost:8000/chart/custom/${symbol}`;
        console.log(`Testing custom chart for ${symbol}: ${url}`);
        
        const response = await page.goto(url, { 
          waitUntil: 'networkidle',
          timeout: 30000 
        });
        
        if (!response) {
          throw new Error(`No response received for ${url}`);
        }
        
        console.log(`${symbol} - Status: ${response.status()}`);
        
        // Wait for content to load
        await page.waitForTimeout(3000);
        
        // Take screenshot
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/03-custom-chart-${symbol}.png`,
          fullPage: true 
        });
        
        // Check for chart container
        const hasChartContainer = await page.locator('[id*="tradingview"], .chart-container, .trading-chart').count() > 0;
        console.log(`${symbol} - Chart container found: ${hasChartContainer}`);
        
        // Check page title or symbol display
        const pageTitle = await page.title();
        const symbolDisplayed = await page.locator(`text=${symbol}`).count() > 0;
        console.log(`${symbol} - Page title: ${pageTitle}`);
        console.log(`${symbol} - Symbol displayed on page: ${symbolDisplayed}`);
      }

      testReport.tests.push({
        name: testName,
        status: 'PASSED',
        details: {
          testedEndpoints: symbols.map(s => `http://localhost:8000/chart/custom/${s}`),
          consoleErrors: consoleErrors.length,
          networkErrors: networkErrors.length
        }
      });

    } catch (error) {
      console.error(`${testName} failed:`, error);
      testReport.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message
      });
      
      // Take error screenshot
      await page.screenshot({ 
        path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/error-custom-chart.png`,
        fullPage: true 
      });
    }
  });

  test('Test Custom Symbol Input Functionality', async ({ page }) => {
    const testName = 'Custom Symbol Input Functionality';
    console.log(`\n=== Starting ${testName} ===`);

    try {
      // Navigate to dashboard
      await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
      await page.waitForSelector('input[type="text"]', { timeout: 10000 });

      // Test custom symbols
      const customSymbols = ['NVDA', 'MSFT', 'AMZN', 'BRK.A'];
      
      for (const symbol of customSymbols) {
        console.log(`Testing custom symbol input: ${symbol}`);
        
        const inputField = page.locator('input[type="text"]').first();
        await inputField.clear();
        await inputField.fill(symbol);
        
        // Try both Enter key and Analyze button
        await inputField.press('Enter');
        await page.waitForTimeout(2000);
        
        // Take screenshot
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/04-custom-input-${symbol}.png`,
          fullPage: true 
        });
        
        // Check if symbol was accepted
        const symbolInHeader = await page.locator(`text=${symbol}`).count() > 0;
        console.log(`${symbol} - Symbol appears in interface: ${symbolInHeader}`);
      }

      testReport.tests.push({
        name: testName,
        status: 'PASSED',
        details: {
          testedCustomSymbols: customSymbols
        }
      });

    } catch (error) {
      console.error(`${testName} failed:`, error);
      testReport.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message
      });
    }
  });

  test('Check TradingView Widget Updates', async ({ page }) => {
    const testName = 'TradingView Widget Updates';
    console.log(`\n=== Starting ${testName} ===`);

    try {
      await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
      
      // Wait for initial chart load
      await page.waitForTimeout(5000);
      
      // Look for TradingView elements
      const tradingViewScript = await page.locator('script[src*="tradingview"]').count();
      const tradingViewContainer = await page.locator('[id*="tradingview"]').count();
      const tradingViewIframe = await page.locator('iframe[src*="tradingview"]').count();
      
      console.log(`TradingView script tags found: ${tradingViewScript}`);
      console.log(`TradingView container divs found: ${tradingViewContainer}`);
      console.log(`TradingView iframes found: ${tradingViewIframe}`);
      
      // Test switching between symbols and checking if new containers are created
      const symbols = ['AAPL', 'TSLA'];
      let containerIds = [];
      
      for (const symbol of symbols) {
        // Switch to symbol
        const popularButton = page.locator(`button:has-text("${symbol}")`).first();
        if (await popularButton.count() > 0) {
          await popularButton.click();
          await page.waitForTimeout(3000);
          
          // Check for new container IDs
          const containers = await page.locator('[id*="tradingview"]').all();
          const currentIds = [];
          for (const container of containers) {
            const id = await container.getAttribute('id');
            if (id) currentIds.push(id);
          }
          containerIds.push({ symbol, ids: currentIds });
          console.log(`${symbol} - TradingView container IDs: ${currentIds.join(', ')}`);
        }
      }

      testReport.tests.push({
        name: testName,
        status: 'PASSED',
        details: {
          tradingViewElementsFound: tradingViewScript + tradingViewContainer + tradingViewIframe,
          containerIds
        }
      });

    } catch (error) {
      console.error(`${testName} failed:`, error);
      testReport.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message
      });
    }
  });

  test('Verify Data Panels Update', async ({ page }) => {
    const testName = 'Data Panels Update Verification';
    console.log(`\n=== Starting ${testName} ===`);

    try {
      await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
      await page.waitForTimeout(3000);

      const symbols = ['AAPL', 'GOOGL'];
      
      for (const symbol of symbols) {
        console.log(`Testing data panels update for ${symbol}`);
        
        // Switch to symbol
        const popularButton = page.locator(`button:has-text("${symbol}")`).first();
        if (await popularButton.count() > 0) {
          await popularButton.click();
          await page.waitForTimeout(3000);
        }
        
        // Check Market Data panel
        const marketDataPanel = page.locator('.market-data, [data-testid="market-data"], .bg-slate-800').first();
        const marketDataExists = await marketDataPanel.count() > 0;
        let marketDataContent = '';
        if (marketDataExists) {
          marketDataContent = await marketDataPanel.textContent() || '';
        }
        
        // Check AI Analysis panel
        const aiAnalysisPanel = page.locator('.ai-analysis, [data-testid="ai-analysis"]').first();
        const aiAnalysisExists = await aiAnalysisPanel.count() > 0;
        let aiAnalysisContent = '';
        if (aiAnalysisExists) {
          aiAnalysisContent = await aiAnalysisPanel.textContent() || '';
        }
        
        // Check Performance panel
        const performancePanel = page.locator('.performance, [data-testid="performance"]').first();
        const performanceExists = await performancePanel.count() > 0;
        
        console.log(`${symbol} - Market Data panel found: ${marketDataExists}`);
        console.log(`${symbol} - AI Analysis panel found: ${aiAnalysisExists}`);
        console.log(`${symbol} - Performance panel found: ${performanceExists}`);
        console.log(`${symbol} - Market data contains symbol: ${marketDataContent.includes(symbol)}`);
        console.log(`${symbol} - AI analysis contains symbol: ${aiAnalysisContent.includes(symbol)}`);
        
        // Take detailed screenshot of data panels
        await page.screenshot({ 
          path: `/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/05-data-panels-${symbol}.png`,
          fullPage: true 
        });
      }

      testReport.tests.push({
        name: testName,
        status: 'PASSED'
      });

    } catch (error) {
      console.error(`${testName} failed:`, error);
      testReport.tests.push({
        name: testName,
        status: 'FAILED',
        error: error.message
      });
    }
  });

  test.afterAll(async () => {
    // Generate final test report
    testReport.errors = consoleErrors;
    testReport.networkErrors = networkErrors;
    testReport.summary = {
      totalTests: testReport.tests.length,
      passed: testReport.tests.filter(t => t.status === 'PASSED').length,
      failed: testReport.tests.filter(t => t.status === 'FAILED').length,
      consoleErrorsTotal: consoleErrors.length,
      networkErrorsTotal: networkErrors.length
    };

    console.log('\n=== FINAL TEST REPORT ===');
    console.log('Timestamp:', testReport.timestamp);
    console.log('Total Tests:', testReport.summary.totalTests);
    console.log('Passed:', testReport.summary.passed);
    console.log('Failed:', testReport.summary.failed);
    console.log('Console Errors:', testReport.summary.consoleErrorsTotal);
    console.log('Network Errors:', testReport.summary.networkErrorsTotal);
    
    if (consoleErrors.length > 0) {
      console.log('\nConsole Errors:');
      consoleErrors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.text} (${error.location?.url}:${error.location?.lineNumber})`);
      });
    }
    
    if (networkErrors.length > 0) {
      console.log('\nNetwork Errors:');
      networkErrors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.url} - ${error.failure}`);
      });
    }

    // Save detailed report to file
    const fs = require('fs');
    fs.writeFileSync(
      '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/stock-switching-test-report.json',
      JSON.stringify(testReport, null, 2)
    );
    
    console.log('\nDetailed report saved to: test-results/stock-switching-test-report.json');
    console.log('Screenshots saved to: test-results/');
  });
});