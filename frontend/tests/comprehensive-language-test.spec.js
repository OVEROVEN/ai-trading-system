const { test, expect } = require('@playwright/test');

test.describe('Comprehensive Language Switching Tests', () => {
  test.use({ 
    baseURL: 'http://localhost:3000',
    // Set viewport to capture full content
    viewport: { width: 1920, height: 1080 }
  });

  test('Comprehensive language switching and AI analysis test', async ({ page }) => {
    console.log('🚀 Starting comprehensive language switching test...');
    
    // Configure network monitoring
    let apiRequests = [];
    let analysisResults = {};
    
    page.on('request', request => {
      if (request.url().includes('/analyze/')) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          postData: request.postData(),
          timestamp: new Date().toISOString()
        });
      }
    });

    page.on('response', async response => {
      if (response.url().includes('/analyze/')) {
        try {
          const responseData = await response.json();
          analysisResults[response.url()] = {
            status: response.status(),
            data: responseData,
            timestamp: new Date().toISOString()
          };
        } catch (e) {
          console.log('Failed to parse analysis response:', e.message);
        }
      }
    });
    
    // Step 1: Navigate to the dashboard
    console.log('📊 Step 1: Opening the trading dashboard...');
    await page.goto('/', { timeout: 15000 });
    
    try {
      await page.waitForLoadState('domcontentloaded', { timeout: 10000 });
      await page.waitForTimeout(3000); // Allow for dynamic content to load
    } catch (error) {
      console.log('⚠️ Page loading timeout, continuing with test');
    }
    
    // Step 2: Take screenshot of default state
    console.log('📸 Step 2: Taking screenshot of default state...');
    await page.screenshot({ 
      path: 'test-results/01-default-state.png', 
      fullPage: true 
    });
    
    // Step 3: Identify language switcher elements
    console.log('🔍 Step 3: Identifying language switcher elements...');
    
    // Look for language switcher flags
    const flagButtons = await page.locator('button').filter({
      has: page.locator('text=/🇺🇸|🇹🇼|🇨🇳/')
    }).count();
    
    console.log(`Found ${flagButtons} flag-based language switcher buttons`);
    
    // Look for text-based language buttons
    const englishButton = page.locator('button:has-text("English")');
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    const simplifiedButton = page.locator('button:has-text("简体中文")');
    
    const englishCount = await englishButton.count();
    const traditionalCount = await traditionalButton.count();
    const simplifiedCount = await simplifiedButton.count();
    
    console.log(`Text-based buttons - English: ${englishCount}, Traditional: ${traditionalCount}, Simplified: ${simplifiedCount}`);
    
    // Step 4: Test English mode first
    console.log('🇺🇸 Step 4: Testing English language mode...');
    
    // Switch to English if flag-based switcher exists
    const usFlag = page.locator('button').filter({ hasText: '🇺🇸' });
    if (await usFlag.count() > 0) {
      await usFlag.click();
      await page.waitForTimeout(1500);
      console.log('✅ Switched to English via flag');
    } else if (await englishButton.count() > 0) {
      await englishButton.click();
      await page.waitForTimeout(1500);
      console.log('✅ Switched to English via text button');
    }
    
    await page.screenshot({ 
      path: 'test-results/02-english-interface.png', 
      fullPage: true 
    });
    
    // Input stock symbol and analyze
    console.log('📈 Testing AI analysis in English...');
    const stockInput = page.locator('input[type="text"]').first();
    await stockInput.fill('AAPL');
    
    // Find and click analyze button
    const analyzeButtons = [
      page.locator('button:has-text("Analyze")'),
      page.locator('button:has-text("分析")'), // fallback
      page.locator('button').filter({ hasText: /analyze|分析/i })
    ];
    
    let analyzeButtonClicked = false;
    for (const button of analyzeButtons) {
      if (await button.count() > 0) {
        await button.first().click();
        analyzeButtonClicked = true;
        console.log('✅ Clicked analyze button (English mode)');
        break;
      }
    }
    
    if (analyzeButtonClicked) {
      // Wait for analysis to complete
      console.log('⏳ Waiting for English AI analysis to complete...');
      await page.waitForTimeout(8000); // Allow time for AI analysis
      
      // Check for AI analysis content
      const aiAnalysisSection = await page.locator('text=AI Analysis').count();
      const aiAnalysisChinese = await page.locator('text=AI 分析').count();
      console.log(`AI Analysis sections: English: ${aiAnalysisSection}, Chinese: ${aiAnalysisChinese}`);
      
      // Take screenshot of English analysis
      await page.screenshot({ 
        path: 'test-results/03-english-ai-analysis.png', 
        fullPage: true 
      });
    }
    
    // Step 5: Test Traditional Chinese mode
    console.log('🇹🇼 Step 5: Testing Traditional Chinese language mode...');
    
    const twFlag = page.locator('button').filter({ hasText: '🇹🇼' });
    if (await twFlag.count() > 0) {
      await twFlag.click();
      await page.waitForTimeout(2000);
      console.log('✅ Switched to Traditional Chinese via flag');
    } else if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(2000);
      console.log('✅ Switched to Traditional Chinese via text button');
    }
    
    await page.screenshot({ 
      path: 'test-results/04-traditional-chinese-interface.png', 
      fullPage: true 
    });
    
    // Test analysis in Traditional Chinese
    console.log('📈 Testing AI analysis in Traditional Chinese...');
    
    // Clear and re-enter stock symbol 
    await stockInput.fill('');
    await stockInput.fill('TSLA');
    
    // Look for Chinese analyze button
    const chineseAnalyzeButtons = [
      page.locator('button:has-text("分析")'),
      page.locator('button:has-text("Analyze")'), // fallback
      page.locator('button').filter({ hasText: /analyze|分析/i })
    ];
    
    analyzeButtonClicked = false;
    for (const button of chineseAnalyzeButtons) {
      if (await button.count() > 0) {
        await button.first().click();
        analyzeButtonClicked = true;
        console.log('✅ Clicked analyze button (Traditional Chinese mode)');
        break;
      }
    }
    
    if (analyzeButtonClicked) {
      console.log('⏳ Waiting for Traditional Chinese AI analysis to complete...');
      await page.waitForTimeout(8000);
      
      // Check for Chinese analysis content
      const aiAnalysisChinese = await page.locator('text=AI 分析').count();
      const aiAnalysisEnglish = await page.locator('text=AI Analysis').count();
      console.log(`AI Analysis sections after Chinese switch: Chinese: ${aiAnalysisChinese}, English: ${aiAnalysisEnglish}`);
      
      await page.screenshot({ 
        path: 'test-results/05-traditional-chinese-ai-analysis.png', 
        fullPage: true 
      });
    }
    
    // Step 6: Test Simplified Chinese mode
    console.log('🇨🇳 Step 6: Testing Simplified Chinese language mode...');
    
    const cnFlag = page.locator('button').filter({ hasText: '🇨🇳' });
    if (await cnFlag.count() > 0) {
      await cnFlag.click();
      await page.waitForTimeout(2000);
      console.log('✅ Switched to Simplified Chinese via flag');
    } else if (await simplifiedButton.count() > 0) {
      await simplifiedButton.click();
      await page.waitForTimeout(2000);
      console.log('✅ Switched to Simplified Chinese via text button');
    }
    
    await page.screenshot({ 
      path: 'test-results/06-simplified-chinese-interface.png', 
      fullPage: true 
    });
    
    // Test analysis in Simplified Chinese
    console.log('📈 Testing AI analysis in Simplified Chinese...');
    
    await stockInput.fill('');
    await stockInput.fill('META');
    
    analyzeButtonClicked = false;
    for (const button of chineseAnalyzeButtons) {
      if (await button.count() > 0) {
        await button.first().click();
        analyzeButtonClicked = true;
        console.log('✅ Clicked analyze button (Simplified Chinese mode)');
        break;
      }
    }
    
    if (analyzeButtonClicked) {
      console.log('⏳ Waiting for Simplified Chinese AI analysis to complete...');
      await page.waitForTimeout(8000);
      
      await page.screenshot({ 
        path: 'test-results/07-simplified-chinese-ai-analysis.png', 
        fullPage: true 
      });
    }
    
    // Step 7: Analysis of results
    console.log('📊 Step 7: Analyzing test results...');
    
    console.log('\n=== LANGUAGE SWITCHING TEST RESULTS ===');
    console.log(`🔹 Flag-based language buttons found: ${flagButtons}`);
    console.log(`🔹 Text-based language buttons - EN: ${englishCount}, TW: ${traditionalCount}, CN: ${simplifiedCount}`);
    
    console.log('\n=== API REQUESTS ANALYSIS ===');
    console.log(`📡 Total analysis API requests captured: ${apiRequests.length}`);
    
    for (let i = 0; i < apiRequests.length; i++) {
      const request = apiRequests[i];
      console.log(`\nRequest ${i + 1}:`);
      console.log(`  URL: ${request.url}`);
      console.log(`  Method: ${request.method}`);
      console.log(`  Time: ${request.timestamp}`);
      
      if (request.postData) {
        try {
          const data = JSON.parse(request.postData);
          console.log(`  Language parameter: ${data.language || 'Not specified'}`);
          console.log(`  Other parameters: ${Object.keys(data).filter(k => k !== 'language').join(', ')}`);
        } catch (e) {
          console.log(`  POST Data (raw): ${request.postData.substring(0, 100)}...`);
        }
      } else {
        console.log('  No POST data');
      }
    }
    
    console.log('\n=== API RESPONSES ANALYSIS ===');
    for (const [url, response] of Object.entries(analysisResults)) {
      console.log(`\nResponse from ${url}:`);
      console.log(`  Status: ${response.status}`);
      console.log(`  Time: ${response.timestamp}`);
      
      if (response.data && response.data.ai_analysis) {
        const analysis = response.data.ai_analysis;
        if (analysis.reasoning) {
          const reasoning = analysis.reasoning.substring(0, 200);
          console.log(`  AI Reasoning (first 200 chars): "${reasoning}..."`);
          
          // Try to detect language in the response
          const hasChinese = /[\u4e00-\u9fff]/.test(reasoning);
          const hasEnglish = /[a-zA-Z]/.test(reasoning);
          console.log(`  Language detected - Chinese: ${hasChinese}, English: ${hasEnglish}`);
        }
        
        if (analysis.recommendation) {
          console.log(`  Recommendation: ${analysis.recommendation}`);
        }
      }
    }
    
    // Final comprehensive screenshot
    await page.screenshot({ 
      path: 'test-results/08-final-state.png', 
      fullPage: true 
    });
    
    console.log('\n✅ Comprehensive language switching test completed!');
    console.log('📸 Screenshots saved to test-results/ directory');
    
    // Verify essential functionality
    expect(flagButtons).toBeGreaterThan(0); // Should have language switcher
    expect(apiRequests.length).toBeGreaterThan(0); // Should have made API calls
  });
  
  test('Language persistence and content analysis', async ({ page }) => {
    console.log('🔄 Testing language persistence and content analysis...');
    
    await page.goto('/', { timeout: 15000 });
    await page.waitForTimeout(3000);
    
    // Test that language changes affect UI text
    const testLanguageText = async (languageButton, expectedTexts) => {
      if (await languageButton.count() > 0) {
        await languageButton.click();
        await page.waitForTimeout(2000);
        
        // Check for expected text in various UI elements
        for (const expectedText of expectedTexts) {
          const textCount = await page.locator(`text=${expectedText}`).count();
          console.log(`  Text "${expectedText}" found ${textCount} times`);
        }
      }
    };
    
    console.log('🇺🇸 Testing English UI text...');
    await testLanguageText(
      page.locator('button').filter({ hasText: '🇺🇸' }),
      ['AI Analysis', 'Market Data', 'Analyze', 'Real-time Analysis']
    );
    
    console.log('🇹🇼 Testing Traditional Chinese UI text...');
    await testLanguageText(
      page.locator('button').filter({ hasText: '🇹🇼' }),
      ['AI 分析', '市場資料', '分析', '即時分析']
    );
    
    console.log('🇨🇳 Testing Simplified Chinese UI text...');
    await testLanguageText(
      page.locator('button').filter({ hasText: '🇨🇳' }),
      ['AI 分析', '市场数据', '分析', '实时分析']
    );
    
    await page.screenshot({ 
      path: 'test-results/09-language-persistence-test.png', 
      fullPage: true 
    });
    
    console.log('✅ Language persistence test completed');
  });
});