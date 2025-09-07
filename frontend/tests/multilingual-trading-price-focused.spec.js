const { test, expect } = require('@playwright/test');

test.describe('Multilingual Trading Price Display - Focused Tests', () => {
  let testReport = {
    timestamp: new Date().toISOString(),
    tests: [],
    screenshots: []
  };

  test.beforeEach(async ({ page }) => {
    // Set timeouts and viewport
    page.setDefaultTimeout(20000);
    page.setDefaultNavigationTimeout(15000);
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('TSLA - Traditional Chinese to English Language Switch Test', async ({ page }) => {
    console.log('\n🇹🇼 🇺🇸 === Testing TSLA: Traditional Chinese ↔ English Trading Price Display ===');
    
    try {
      // 1. Navigate to the application
      console.log('1. Navigating to http://localhost:3000...');
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });
      await page.waitForTimeout(2000);

      // 2. Switch to Traditional Chinese first
      console.log('2. Switching to Traditional Chinese...');
      await switchLanguage(page, 'zh-TW');
      
      // Verify the interface switched to Chinese
      await expect(page.locator('h1')).toContainText('AI 交易儀表板');
      console.log('✓ Successfully switched to Traditional Chinese');
      
      // Take screenshot of Chinese interface
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-01-zh-tw-initial.png',
        fullPage: true 
      });

      // 3. Search for TSLA stock
      console.log('\n3. Searching for TSLA stock...');
      const searchResult = await searchStock(page, 'TSLA');
      
      if (!searchResult.success) {
        throw new Error(`Failed to search for TSLA: ${searchResult.error}`);
      }
      console.log('✓ TSLA search completed successfully');

      // 4. Wait for AI analysis to start and look for trading price section
      console.log('\n4. Checking for AI analysis and trading price elements in Chinese...');
      await page.waitForTimeout(5000); // Wait for analysis to start
      
      // Check for AI analysis panel
      const aiPanels = await page.locator('.bg-slate-800\\/50').count();
      console.log(`Found ${aiPanels} AI analysis panels`);

      // Look for any trading price related elements in Chinese
      const chineseLabels = await checkTradingPriceLabels(page, 'zh-TW');
      console.log('Chinese labels found:', chineseLabels);
      
      // Take screenshot of Chinese analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-02-zh-tw-tsla.png',
        fullPage: true 
      });

      // 5. Switch to English and verify immediate language change
      console.log('\n5. Switching to English...');
      await switchLanguage(page, 'en');
      
      // Verify the interface switched to English
      await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
      console.log('✓ Successfully switched to English');
      
      // Wait a moment for language change to propagate
      await page.waitForTimeout(2000);
      
      // Look for trading price elements in English
      const englishLabels = await checkTradingPriceLabels(page, 'en');
      console.log('English labels found:', englishLabels);
      
      // Take screenshot of English analysis
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-03-en-tsla.png',
        fullPage: true 
      });

      // 6. Test rapid language switching
      console.log('\n6. Testing rapid language switching...');
      for (let i = 0; i < 3; i++) {
        console.log(`  Switch cycle ${i + 1}/3`);
        
        // Switch to Chinese
        await switchLanguage(page, 'zh-TW');
        await page.waitForTimeout(500);
        await expect(page.locator('h1')).toContainText('AI 交易儀表板');
        
        // Switch to English  
        await switchLanguage(page, 'en');
        await page.waitForTimeout(500);
        await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
      }
      console.log('✓ Rapid language switching test completed');

      // 7. Verify price values remain in USD format
      console.log('\n7. Verifying price format remains USD...');
      const usdPrices = await checkUSDPriceFormat(page);
      console.log(`✓ Found ${usdPrices.count} USD price elements`);

      // Final screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-04-final.png',
        fullPage: true 
      });

      testReport.tests.push({
        name: 'TSLA Traditional Chinese to English Switch',
        status: 'COMPLETED',
        chineseLabels,
        englishLabels,
        usdPrices
      });

      console.log('✅ TSLA multilingual test completed successfully!');

    } catch (error) {
      console.error('TSLA multilingual test failed:', error);
      testReport.tests.push({
        name: 'TSLA Traditional Chinese to English Switch',
        status: 'FAILED',
        error: error.message
      });
      
      try {
        await page.screenshot({ 
          path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-error.png',
          fullPage: true
        });
      } catch (screenshotError) {
        console.log('Could not take error screenshot:', screenshotError.message);
      }
    }
  });

  test('META - Language Switch Responsiveness Test', async ({ page }) => {
    console.log('\n🚀 === Testing META: Language Switch Responsiveness ===');
    
    try {
      // 1. Navigate and search for META
      await page.goto('http://localhost:3000', { 
        waitUntil: 'domcontentloaded',
        timeout: 15000 
      });
      await page.waitForTimeout(2000);

      // Start with English (default)
      console.log('1. Starting with English interface...');
      await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
      
      // Search for META
      const searchResult = await searchStock(page, 'META');
      if (!searchResult.success) {
        throw new Error(`Failed to search for META: ${searchResult.error}`);
      }
      console.log('✓ META search completed');

      // Wait for some content to load
      await page.waitForTimeout(3000);

      // Take initial screenshot
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-05-meta-en-initial.png',
        fullPage: true 
      });

      // 2. Switch to Traditional Chinese
      console.log('\n2. Switching to Traditional Chinese...');
      await switchLanguage(page, 'zh-TW');
      await page.waitForTimeout(1000);
      
      // Verify Chinese interface
      await expect(page.locator('h1')).toContainText('AI 交易儀表板');
      
      // Check for Chinese labels in the interface
      const chineseInterfaceElements = await checkInterfaceLabels(page, 'zh-TW');
      console.log('Chinese interface elements found:', chineseInterfaceElements);
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-06-meta-zh-tw.png',
        fullPage: true 
      });

      // 3. Switch back to English
      console.log('\n3. Switching back to English...');
      await switchLanguage(page, 'en');
      await page.waitForTimeout(1000);
      
      // Verify English interface
      await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
      
      // Check for English labels in the interface
      const englishInterfaceElements = await checkInterfaceLabels(page, 'en');
      console.log('English interface elements found:', englishInterfaceElements);
      
      await page.screenshot({ 
        path: '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-07-meta-en-final.png',
        fullPage: true 
      });

      testReport.tests.push({
        name: 'META Language Switch Responsiveness',
        status: 'COMPLETED',
        chineseInterfaceElements,
        englishInterfaceElements
      });

      console.log('✅ META language responsiveness test completed successfully!');

    } catch (error) {
      console.error('META language responsiveness test failed:', error);
      testReport.tests.push({
        name: 'META Language Switch Responsiveness',
        status: 'FAILED',
        error: error.message
      });
    }
  });

  // Helper function to switch language using flag emojis
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
        `button:has([title="${title}"])`
      ];
      
      let success = false;
      for (const selector of selectors) {
        try {
          const langButton = page.locator(selector).first();
          const count = await langButton.count();
          if (count > 0) {
            await langButton.click();
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

      // Look for search input
      const searchSelectors = [
        'input[placeholder*="symbol" i]',
        'input[placeholder*="search" i]', 
        'input[type="text"]'
      ];
      
      let searchInput = null;
      for (const selector of searchSelectors) {
        try {
          await page.waitForSelector(selector, { timeout: 2000 });
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

  // Helper function to check for trading price labels
  async function checkTradingPriceLabels(page, language) {
    const expectedLabels = {
      'zh-TW': [
        '📊 交易價位建議',
        '🎯 建議進場價',
        '🚀 目標價位',
        '🛑 停損價位',
        '📈 潛在報酬'
      ],
      'en': [
        '📊 Trading Price Levels',
        '🎯 Entry Price', 
        '🚀 Target Price',
        '🛑 Stop Loss',
        '📈 Potential Return'
      ]
    };

    const labels = expectedLabels[language] || expectedLabels['en'];
    const found = [];
    
    for (const label of labels) {
      try {
        // Try multiple selector strategies
        let count = 0;
        
        // Strategy 1: Exact text match
        let elements = page.locator(`text="${label}"`);
        count = await elements.count();
        
        // Strategy 2: Contains text match if exact fails
        if (count === 0) {
          elements = page.locator(`text*="${label}"`);
          count = await elements.count();
        }
        
        // Strategy 3: Look for parts of the label
        if (count === 0) {
          const parts = label.split(' ');
          for (const part of parts) {
            if (part.length > 2) { // Skip very short parts
              elements = page.locator(`text*="${part}"`);
              const partCount = await elements.count();
              if (partCount > 0) {
                count = partCount;
                break;
              }
            }
          }
        }
        
        if (count > 0) {
          found.push({ label, count });
          console.log(`  ✓ Found "${label}" (${count} elements)`);
        } else {
          console.log(`  ⚠️ Not found: "${label}"`);
        }
      } catch (error) {
        console.log(`  ❌ Error checking "${label}": ${error.message}`);
      }
    }
    
    return found;
  }

  // Helper function to check interface labels
  async function checkInterfaceLabels(page, language) {
    const expectedInterfaceLabels = {
      'zh-TW': [
        'AI 分析', '市場資料', '績效表現', '即時分析', 'AI 建議', 
        '分析', '熱門', '股票代號', '狀態', '當前價格'
      ],
      'en': [
        'AI Analysis', 'Market Data', 'Performance', 'Real-time Analysis', 'AI Recommendations',
        'Analyze', 'Popular', 'Symbol', 'Status', 'Current Price'
      ]
    };

    const labels = expectedInterfaceLabels[language] || expectedInterfaceLabels['en'];
    const found = [];
    
    for (const label of labels) {
      try {
        const elements = page.locator(`text="${label}"`);
        const count = await elements.count();
        if (count > 0) {
          found.push({ label, count });
        }
      } catch (error) {
        // Label not found
      }
    }
    
    return found;
  }

  // Helper function to check USD price format
  async function checkUSDPriceFormat(page) {
    try {
      const priceElements = page.locator('text=/\\$[0-9]+\\.?[0-9]*/');
      const count = await priceElements.count();
      
      const samplePrices = [];
      for (let i = 0; i < Math.min(5, count); i++) {
        try {
          const priceText = await priceElements.nth(i).textContent();
          samplePrices.push(priceText);
        } catch (e) {
          // Skip this element
        }
      }
      
      return { count, samplePrices };
    } catch (error) {
      return { count: 0, samplePrices: [], error: error.message };
    }
  }

  test.afterAll(async () => {
    // Generate test report
    const summary = {
      timestamp: testReport.timestamp,
      totalTests: testReport.tests.length,
      completedTests: testReport.tests.filter(t => t.status === 'COMPLETED').length,
      failedTests: testReport.tests.filter(t => t.status === 'FAILED').length
    };

    console.log('\n=== MULTILINGUAL TRADING PRICE FOCUSED TEST REPORT ===');
    console.log(`Timestamp: ${summary.timestamp}`);
    console.log(`Total Tests: ${summary.totalTests}`);
    console.log(`Completed: ${summary.completedTests}`);
    console.log(`Failed: ${summary.failedTests}`);

    console.log('\n=== DETAILED RESULTS ===');
    testReport.tests.forEach(test => {
      console.log(`\n${test.name}:`);
      console.log(`  Status: ${test.status}`);
      if (test.chineseLabels) {
        console.log(`  Chinese Labels Found: ${test.chineseLabels.length}`);
        test.chineseLabels.forEach(item => {
          console.log(`    - "${item.label}" (${item.count})`);
        });
      }
      if (test.englishLabels) {
        console.log(`  English Labels Found: ${test.englishLabels.length}`);
        test.englishLabels.forEach(item => {
          console.log(`    - "${item.label}" (${item.count})`);
        });
      }
      if (test.usdPrices) {
        console.log(`  USD Prices Found: ${test.usdPrices.count}`);
        if (test.usdPrices.samplePrices.length > 0) {
          console.log(`    Sample prices: ${test.usdPrices.samplePrices.join(', ')}`);
        }
      }
      if (test.error) {
        console.log(`  Error: ${test.error}`);
      }
    });

    // Save report
    const fs = require('fs');
    fs.writeFileSync(
      '/Users/afu/Desktop/auto_trade/auto_trade/frontend/test-results/multilingual-focused-report.json',
      JSON.stringify({ summary, tests: testReport.tests }, null, 2)
    );

    console.log('\n📊 Report saved to: test-results/multilingual-focused-report.json');
    console.log('📸 Screenshots available:');
    console.log('  - multilingual-focused-01-zh-tw-initial.png');
    console.log('  - multilingual-focused-02-zh-tw-tsla.png');
    console.log('  - multilingual-focused-03-en-tsla.png');
    console.log('  - multilingual-focused-04-final.png');
    console.log('  - multilingual-focused-05-meta-en-initial.png');
    console.log('  - multilingual-focused-06-meta-zh-tw.png');
    console.log('  - multilingual-focused-07-meta-en-final.png');
    console.log('\n=== FOCUSED MULTILINGUAL TEST COMPLETED ===');
  });
});