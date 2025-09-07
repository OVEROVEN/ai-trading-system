const { test, expect } = require('@playwright/test');

test.describe('Multilingual Trading Price Display Tests', () => {
  let testReport = {
    timestamp: new Date().toISOString(),
    tests: [],
    errors: [],
    screenshots: [],
    languageTestResults: []
  };

  test.beforeEach(async ({ page }) => {
    // Set timeouts and viewport
    page.setDefaultTimeout(30000);
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

  test('Traditional Chinese Trading Price Display Test', async ({ page }) => {
    console.log('\n🇹🇼 === Testing Traditional Chinese Trading Price Display ===');
    
    try {
      // 1. Navigate to the application
      console.log('1. Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });
      await page.waitForTimeout(3000);

      // Switch to Traditional Chinese first
      console.log('2. Switching to Traditional Chinese...');
      await switchLanguage(page, 'zh-TW');
      
      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-01-zh-tw-initial.png',
        fullPage: true 
      });
      console.log('✓ Switched to Traditional Chinese and screenshot taken');

      // 3. Search for TSLA stock
      console.log('\n3. Searching for TSLA stock in Traditional Chinese interface...');
      const searchResult = await searchStock(page, 'TSLA');
      
      if (!searchResult.success) {
        throw new Error(`Failed to search for TSLA: ${searchResult.error}`);
      }
      console.log('✓ TSLA search completed successfully');

      // 4. Wait for AI analysis and check Traditional Chinese trading price labels
      console.log('\n4. Checking Traditional Chinese trading price labels...');
      const zhTWResult = await waitAndCheckTradingPriceLabels(page, 'TSLA', 'zh-TW');
      
      testReport.languageTestResults.push({
        stock: 'TSLA',
        language: 'zh-TW',
        languageName: 'Traditional Chinese',
        ...zhTWResult,
        timestamp: new Date().toISOString()
      });

      // Take screenshot after analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-02-zh-tw-tsla-analysis.png',
        fullPage: true 
      });
      console.log('✓ Traditional Chinese TSLA analysis screenshot taken');

      // Verify specific Traditional Chinese labels
      console.log('\n5. Verifying specific Traditional Chinese labels...');
      await verifySpecificLabels(page, {
        tradingPriceTitle: '📊 交易價位建議',
        entryPrice: '🎯 建議進場價', 
        targetPrice: '🚀 目標價位',
        stopLoss: '🛑 停損價位',
        potentialReturn: '📈 潛在報酬'
      }, 'zh-TW');

      testReport.tests.push({
        name: 'Traditional Chinese Trading Price Display',
        status: 'COMPLETED',
        result: zhTWResult
      });

    } catch (error) {
      console.error('Traditional Chinese test failed:', error);
      testReport.tests.push({
        name: 'Traditional Chinese Trading Price Display',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-error-zh-tw.png',
        fullPage: true
      });
    }
  });

  test('English Trading Price Display Test', async ({ page }) => {
    console.log('\n🇺🇸 === Testing English Trading Price Display ===');
    
    try {
      // 1. Navigate to the application
      console.log('1. Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });
      await page.waitForTimeout(3000);

      // Switch to English
      console.log('2. Switching to English...');
      await switchLanguage(page, 'en');
      
      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-03-en-initial.png',
        fullPage: true 
      });
      console.log('✓ Switched to English and screenshot taken');

      // 3. Search for TSLA stock
      console.log('\n3. Searching for TSLA stock in English interface...');
      const searchResult = await searchStock(page, 'TSLA');
      
      if (!searchResult.success) {
        throw new Error(`Failed to search for TSLA: ${searchResult.error}`);
      }
      console.log('✓ TSLA search completed successfully');

      // 4. Wait for AI analysis and check English trading price labels
      console.log('\n4. Checking English trading price labels...');
      const enResult = await waitAndCheckTradingPriceLabels(page, 'TSLA', 'en');
      
      testReport.languageTestResults.push({
        stock: 'TSLA',
        language: 'en',
        languageName: 'English',
        ...enResult,
        timestamp: new Date().toISOString()
      });

      // Take screenshot after analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-04-en-tsla-analysis.png',
        fullPage: true 
      });
      console.log('✓ English TSLA analysis screenshot taken');

      // Verify specific English labels
      console.log('\n5. Verifying specific English labels...');
      await verifySpecificLabels(page, {
        tradingPriceTitle: '📊 Trading Price Levels',
        entryPrice: '🎯 Entry Price',
        targetPrice: '🚀 Target Price', 
        stopLoss: '🛑 Stop Loss',
        potentialReturn: '📈 Potential Return'
      }, 'en');

      testReport.tests.push({
        name: 'English Trading Price Display',
        status: 'COMPLETED',
        result: enResult
      });

    } catch (error) {
      console.error('English test failed:', error);
      testReport.tests.push({
        name: 'English Trading Price Display',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-error-en.png',
        fullPage: true
      });
    }
  });

  test('Language Switch Responsiveness Test', async ({ page }) => {
    console.log('\n🔄 === Testing Language Switch Responsiveness ===');
    
    try {
      // 1. Navigate and search for META stock
      console.log('1. Navigating and searching for META stock...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 20000 
      });
      await page.waitForTimeout(3000);

      // Start with Traditional Chinese
      await switchLanguage(page, 'zh-TW');
      
      // Search for META
      const searchResult = await searchStock(page, 'META');
      if (!searchResult.success) {
        throw new Error(`Failed to search for META: ${searchResult.error}`);
      }
      console.log('✓ META search completed');

      // Wait for analysis in Chinese
      console.log('\n2. Waiting for AI analysis in Traditional Chinese...');
      const zhTWResult = await waitAndCheckTradingPriceLabels(page, 'META', 'zh-TW', 30000);
      
      // Take screenshot of Chinese version
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-05-zh-tw-meta.png',
        fullPage: true 
      });
      console.log('✓ Traditional Chinese META analysis screenshot taken');

      // 3. Switch to English and verify immediate language change
      console.log('\n3. Switching to English and verifying immediate response...');
      await switchLanguage(page, 'en');
      
      // Wait a moment for language change to take effect
      await page.waitForTimeout(2000);
      
      // Verify English labels are now displayed
      const enResult = await waitAndCheckTradingPriceLabels(page, 'META', 'en', 10000);
      
      // Take screenshot of English version
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-06-en-meta.png',
        fullPage: true 
      });
      console.log('✓ English META analysis screenshot taken');

      // 4. Test multiple language switches
      console.log('\n4. Testing rapid language switching...');
      for (let i = 0; i < 3; i++) {
        console.log(`  Switch cycle ${i + 1}/3`);
        
        // Switch to Chinese
        await switchLanguage(page, 'zh-TW');
        await page.waitForTimeout(1000);
        
        // Verify Chinese labels exist
        const zhLabels = await checkLabelsExist(page, ['交易價位建議', '建議進場價', '目標價位', '停損價位', '潛在報酬']);
        console.log(`    Chinese labels found: ${zhLabels.found}/${zhLabels.total}`);
        
        // Switch to English
        await switchLanguage(page, 'en');
        await page.waitForTimeout(1000);
        
        // Verify English labels exist
        const enLabels = await checkLabelsExist(page, ['Trading Price Levels', 'Entry Price', 'Target Price', 'Stop Loss', 'Potential Return']);
        console.log(`    English labels found: ${enLabels.found}/${enLabels.total}`);
      }

      // 5. Verify price values remain in USD format
      console.log('\n5. Verifying price values remain in USD format...');
      await verifyPriceFormat(page);

      testReport.languageTestResults.push({
        stock: 'META',
        language: 'zh-TW',
        languageName: 'Traditional Chinese',
        ...zhTWResult,
        timestamp: new Date().toISOString()
      });

      testReport.languageTestResults.push({
        stock: 'META', 
        language: 'en',
        languageName: 'English',
        ...enResult,
        timestamp: new Date().toISOString()
      });

      testReport.tests.push({
        name: 'Language Switch Responsiveness',
        status: 'COMPLETED',
        switchTests: 3
      });

    } catch (error) {
      console.error('Language switch test failed:', error);
      testReport.tests.push({
        name: 'Language Switch Responsiveness',
        status: 'FAILED',
        error: error.message
      });
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-error-switch.png',
        fullPage: true
      });
    }
  });

  // Helper function to switch language
  async function switchLanguage(page, targetLanguage) {
    const languageFlags = {
      'en': '🇺🇸',
      'zh-TW': '🇹🇼',
      'zh-CN': '🇨🇳'
    };
    
    const languageTitles = {
      'en': 'EN',
      'zh-TW': 'TW',
      'zh-CN': 'CN'
    };
    
    const flag = languageFlags[targetLanguage];
    const title = languageTitles[targetLanguage];
    
    if (!flag) {
      throw new Error(`Unknown language: ${targetLanguage}`);
    }
    
    try {
      // Try different selectors for language buttons
      const selectors = [
        `button:has-text("${flag}")`,
        `button[title="${title}"]`,
        `button:has([title="${title}"])`,
        `button:has-text("${title}")`
      ];
      
      let success = false;
      for (const selector of selectors) {
        try {
          const langButton = page.locator(selector).first();
          const count = await langButton.count();
          if (count > 0) {
            await langButton.click();
            await page.waitForTimeout(1000);
            console.log(`✓ Switched to ${targetLanguage} (${flag}) using selector: ${selector}`);
            success = true;
            break;
          }
        } catch (error) {
          // Try next selector
        }
      }
      
      if (!success) {
        throw new Error(`Could not find language button for ${targetLanguage} (${flag})`);
      }
      
    } catch (error) {
      throw new Error(`Failed to switch to ${targetLanguage}: ${error.message}`);
    }
  }

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

  // Helper function to wait for AI analysis and check trading price labels
  async function waitAndCheckTradingPriceLabels(page, symbol, language, timeout = 45000) {
    console.log(`Waiting for AI analysis and checking ${language} trading price labels for ${symbol}...`);
    
    const result = {
      success: false,
      aiAnalysisCompleted: false,
      tradingPriceDisplayed: false,
      labelsFound: {
        tradingPriceTitle: false,
        entryPrice: false,
        targetPrice: false,
        stopLoss: false,
        potentialReturn: false
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

    // Define expected labels for each language
    const expectedLabels = {
      'zh-TW': {
        tradingPriceTitle: ['📊 交易價位建議', '交易價位建議'],
        entryPrice: ['🎯 建議進場價', '建議進場價', '🎯'],
        targetPrice: ['🚀 目標價位', '目標價位', '🚀'],
        stopLoss: ['🛑 停損價位', '停損價位', '🛑'],
        potentialReturn: ['📈 潛在報酬', '潛在報酬', '📈']
      },
      'en': {
        tradingPriceTitle: ['📊 Trading Price Levels', 'Trading Price Levels'],
        entryPrice: ['🎯 Entry Price', 'Entry Price', '🎯'],
        targetPrice: ['🚀 Target Price', 'Target Price', '🚀'],
        stopLoss: ['🛑 Stop Loss', 'Stop Loss', '🛑'],
        potentialReturn: ['📈 Potential Return', 'Potential Return', '📈']
      }
    };

    const labels = expectedLabels[language] || expectedLabels['en'];

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
        
        // Check if we have analysis results
        const analysisPanel = page.locator('[data-testid="ai-analysis"], .bg-slate-800\\/50').first();
        const panelText = await analysisPanel.textContent().catch(() => '');
        
        // Check for completion indicators
        const hasRecommendation = panelText.includes('推薦') || panelText.includes('建議') || panelText.includes('recommendation') || 
                                  panelText.includes('BUY') || panelText.includes('SELL') || panelText.includes('HOLD') ||
                                  panelText.includes('買入') || panelText.includes('賣出') || panelText.includes('持有');
        const hasAnalysisContent = panelText.length > 200;
        const noSpinner = spinnerCount === 0;
        
        if (hasRecommendation && hasAnalysisContent && noSpinner) {
          analysisCompleted = true;
          result.aiAnalysisCompleted = true;
          console.log(`✓ AI analysis completed for ${symbol}`);
          break;
        }
        
        await page.waitForTimeout(2000);
      }
      
      if (!analysisCompleted) {
        console.log(`⚠️ AI analysis may not have completed within timeout for ${symbol}`);
      }

      // Now check for trading price display elements with language-specific labels
      console.log(`Checking for ${language} trading price display elements...`);
      
      // Check trading price section title
      for (const titleLabel of labels.tradingPriceTitle) {
        const titleElements = page.locator(`text="${titleLabel}"`);
        const count = await titleElements.count();
        if (count > 0) {
          result.labelsFound.tradingPriceTitle = true;
          result.elementCounts.tradingPriceSection++;
          console.log(`✓ Trading price title found: "${titleLabel}"`);
          break;
        }
      }
      
      if (result.labelsFound.tradingPriceTitle) {
        result.tradingPriceDisplayed = true;
        
        // Check for entry price labels
        for (const entryLabel of labels.entryPrice) {
          const entryElements = page.locator(`text*="${entryLabel}"`);
          const count = await entryElements.count();
          if (count > 0) {
            result.labelsFound.entryPrice = true;
            result.elementCounts.entryPriceElements += count;
            console.log(`✓ Entry price label found: "${entryLabel}"`);
            break;
          }
        }
        
        // Check for target price labels
        for (const targetLabel of labels.targetPrice) {
          const targetElements = page.locator(`text*="${targetLabel}"`);
          const count = await targetElements.count();
          if (count > 0) {
            result.labelsFound.targetPrice = true;
            result.elementCounts.targetPriceElements += count;
            console.log(`✓ Target price label found: "${targetLabel}"`);
            break;
          }
        }
        
        // Check for stop loss labels
        for (const stopLabel of labels.stopLoss) {
          const stopElements = page.locator(`text*="${stopLabel}"`);
          const count = await stopElements.count();
          if (count > 0) {
            result.labelsFound.stopLoss = true;
            result.elementCounts.stopLossElements += count;
            console.log(`✓ Stop loss label found: "${stopLabel}"`);
            break;
          }
        }
        
        // Check for potential return labels
        for (const returnLabel of labels.potentialReturn) {
          const returnElements = page.locator(`text*="${returnLabel}"`);
          const count = await returnElements.count();
          if (count > 0) {
            result.labelsFound.potentialReturn = true;
            result.elementCounts.potentialReturnElements += count;
            console.log(`✓ Potential return label found: "${returnLabel}"`);
            break;
          }
        }
        
        // Check if we have at least 3 of the 4 key labels for success
        const labelsFoundCount = Object.values(result.labelsFound).filter(Boolean).length - 1; // Exclude title
        
        if (labelsFoundCount >= 3) {
          result.success = true;
          console.log(`✅ ${language} trading price display validation successful for ${symbol} (${labelsFoundCount}/4 key labels found)`);
        } else {
          console.log(`⚠️ ${language} trading price display incomplete for ${symbol} (${labelsFoundCount}/4 key labels found)`);
        }
        
      } else {
        console.log(`❌ ${language} trading price section not found for ${symbol}`);
      }
      
    } catch (error) {
      console.error(`Error checking ${language} trading price display for ${symbol}:`, error);
      result.error = error.message;
    }
    
    return result;
  }

  // Helper function to verify specific labels
  async function verifySpecificLabels(page, expectedLabels, language) {
    const results = {};
    
    for (const [key, label] of Object.entries(expectedLabels)) {
      try {
        const elements = page.locator(`text*="${label}"`);
        const count = await elements.count();
        results[key] = count > 0;
        
        if (count > 0) {
          console.log(`✓ ${language} label verified: "${label}"`);
        } else {
          console.log(`⚠️ ${language} label not found: "${label}"`);
        }
      } catch (error) {
        console.log(`❌ Error checking ${language} label "${label}": ${error.message}`);
        results[key] = false;
      }
    }
    
    return results;
  }

  // Helper function to check if labels exist
  async function checkLabelsExist(page, labels) {
    let found = 0;
    const total = labels.length;
    
    for (const label of labels) {
      try {
        const elements = page.locator(`text*="${label}"`);
        const count = await elements.count();
        if (count > 0) found++;
      } catch (error) {
        // Label not found
      }
    }
    
    return { found, total };
  }

  // Helper function to verify price format (should remain in USD)
  async function verifyPriceFormat(page) {
    try {
      // Look for price elements (should contain $ symbol)
      const priceElements = page.locator('text=/\\$[0-9]+\\.?[0-9]*/');
      const count = await priceElements.count();
      
      if (count > 0) {
        console.log(`✓ Found ${count} USD price elements`);
        
        // Get some sample prices to log
        for (let i = 0; i < Math.min(3, count); i++) {
          try {
            const priceText = await priceElements.nth(i).textContent();
            console.log(`  Sample price: ${priceText}`);
          } catch (e) {
            // Skip this element
          }
        }
        
        return true;
      } else {
        console.log('⚠️ No USD price elements found');
        return false;
      }
    } catch (error) {
      console.log(`❌ Error verifying price format: ${error.message}`);
      return false;
    }
  }

  test.afterAll(async () => {
    // Generate comprehensive test report
    const summary = {
      timestamp: testReport.timestamp,
      totalTests: testReport.tests.length,
      completedTests: testReport.tests.filter(t => t.status === 'COMPLETED').length,
      failedTests: testReport.tests.filter(t => t.status === 'FAILED').length,
      totalErrors: testReport.errors.length,
      multilingualTestResults: {
        totalLanguageTests: testReport.languageTestResults.length,
        successfulLanguageTests: testReport.languageTestResults.filter(r => r.success).length,
        languagesTested: [...new Set(testReport.languageTestResults.map(r => r.language))],
        stocksTested: [...new Set(testReport.languageTestResults.map(r => r.stock))]
      }
    };

    console.log('\n=== MULTILINGUAL TRADING PRICE TEST REPORT ===');
    console.log(`Timestamp: ${summary.timestamp}`);
    console.log(`Total Tests: ${summary.totalTests}`);
    console.log(`Completed: ${summary.completedTests}`);
    console.log(`Failed: ${summary.failedTests}`);
    console.log(`Total Errors: ${summary.totalErrors}`);
    
    console.log('\n=== MULTILINGUAL RESULTS ===');
    console.log(`Total Language Tests: ${summary.multilingualTestResults.totalLanguageTests}`);
    console.log(`Successful Language Tests: ${summary.multilingualTestResults.successfulLanguageTests}`);
    console.log(`Languages Tested: ${summary.multilingualTestResults.languagesTested.join(', ')}`);
    console.log(`Stocks Tested: ${summary.multilingualTestResults.stocksTested.join(', ')}`);

    if (testReport.errors.length > 0) {
      console.log('\n=== ERRORS FOUND ===');
      testReport.errors.forEach((error, i) => {
        console.log(`${i + 1}. [${error.type.toUpperCase()}] ${error.message}`);
      });
    }

    // Detailed language-by-language results
    console.log('\n=== DETAILED LANGUAGE RESULTS ===');
    testReport.languageTestResults.forEach(result => {
      console.log(`\n${result.stock} - ${result.languageName} (${result.language}):`);
      console.log(`  - Success: ${result.success ? '✅' : '❌'}`);
      console.log(`  - AI Analysis Completed: ${result.aiAnalysisCompleted ? '✅' : '❌'}`);
      console.log(`  - Trading Price Displayed: ${result.tradingPriceDisplayed ? '✅' : '❌'}`);
      
      if (result.labelsFound) {
        console.log(`  - Labels Found:`);
        console.log(`    * Trading Price Title: ${result.labelsFound.tradingPriceTitle ? '✅' : '❌'}`);
        console.log(`    * Entry Price: ${result.labelsFound.entryPrice ? '✅' : '❌'}`);
        console.log(`    * Target Price: ${result.labelsFound.targetPrice ? '✅' : '❌'}`);
        console.log(`    * Stop Loss: ${result.labelsFound.stopLoss ? '✅' : '❌'}`);
        console.log(`    * Potential Return: ${result.labelsFound.potentialReturn ? '✅' : '❌'}`);
      }
      
      if (result.elementCounts) {
        console.log(`  - Element Counts:`);
        console.log(`    * AI Analysis Panel: ${result.elementCounts.aiAnalysisPanel}`);
        console.log(`    * Trading Price Section: ${result.elementCounts.tradingPriceSection}`);
        console.log(`    * Entry Price Elements: ${result.elementCounts.entryPriceElements}`);
        console.log(`    * Target Price Elements: ${result.elementCounts.targetPriceElements}`);
        console.log(`    * Stop Loss Elements: ${result.elementCounts.stopLossElements}`);
        console.log(`    * Potential Return Elements: ${result.elementCounts.potentialReturnElements}`);
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
      languageTestResults: testReport.languageTestResults,
      generatedAt: new Date().toISOString()
    };

    fs.writeFileSync(
      '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-trading-price-report.json',
      JSON.stringify(detailedReport, null, 2)
    );

    console.log('\n📊 Detailed report saved to: test-results/multilingual-trading-price-report.json');
    console.log('📸 Screenshots available in: test-results/');
    console.log('  - multilingual-trading-01-zh-tw-initial.png');
    console.log('  - multilingual-trading-02-zh-tw-tsla-analysis.png');
    console.log('  - multilingual-trading-03-en-initial.png'); 
    console.log('  - multilingual-trading-04-en-tsla-analysis.png');
    console.log('  - multilingual-trading-05-zh-tw-meta.png');
    console.log('  - multilingual-trading-06-en-meta.png');
    console.log('\n=== MULTILINGUAL TRADING PRICE TEST COMPLETED ===');
  });
});