const { test, expect } = require('@playwright/test');

test.describe('多語言 AI 分析測試', () => {
  test.use({ 
    baseURL: 'http://localhost:3000',
  });

  test('AI 分析應該根據語言設定回應', async ({ page }) => {
    console.log('🤖 測試多語言 AI 分析...');
    
    // 訪問主頁
    await page.goto('/', { timeout: 10000 });
    
    // 等待頁面載入
    try {
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
      await page.waitForTimeout(2000);
    } catch (error) {
      console.log('⚠️  DOM載入超時，繼續執行測試');
    }
    
    console.log('📊 測試英文分析...');
    
    // 確保當前是英文模式
    const englishButton = page.locator('button:has-text("English")');
    if (await englishButton.count() > 0) {
      await englishButton.click();
      await page.waitForTimeout(1000);
    }
    
    // 輸入股票代碼並點擊分析
    await page.fill('input[type="text"]', 'AAPL');
    
    // 找到分析按鈕並點擊
    const analyzeButton = page.locator('button:has-text("Analyze")').first();
    if (await analyzeButton.count() > 0) {
      await analyzeButton.click();
      console.log('✅ 點擊分析按鈕 (英文)');
      
      // 等待分析完成
      await page.waitForTimeout(5000);
      
      // 檢查是否有 AI 分析區塊
      const aiAnalysis = await page.locator('text=AI Analysis').count();
      console.log(`AI 分析區塊: ${aiAnalysis} 個`);
    }
    
    console.log('🇹🇼 測試繁體中文分析...');
    
    // 切換到繁體中文
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(2000);
      console.log('✅ 切換到繁體中文');
      
      // 再次點擊分析按鈕（現在應該是中文）
      const chineseAnalyzeButton = page.locator('button:has-text("分析")').first();
      if (await chineseAnalyzeButton.count() > 0) {
        await chineseAnalyzeButton.click();
        console.log('✅ 點擊分析按鈕 (繁體中文)');
        
        // 等待分析完成
        await page.waitForTimeout(5000);
        
        // 檢查是否有中文的 AI 分析標題
        const aiAnalysisChinese = await page.locator('text=AI 分析').count();
        console.log(`AI 分析區塊 (中文): ${aiAnalysisChinese} 個`);
      }
    }
    
    // 截圖記錄最終狀態
    await page.screenshot({ path: 'test-results/multilingual-ai-analysis.png', fullPage: true });
    
    console.log('✅ 多語言 AI 測試完成');
  });
  
  test('檢查不同語言下的 API 請求', async ({ page }) => {
    console.log('🔍 監控 API 請求語言參數...');
    
    // 監聽網路請求
    let apiRequests = [];
    page.on('request', request => {
      if (request.url().includes('/analyze/')) {
        apiRequests.push({
          url: request.url(),
          method: request.method(),
          postData: request.postData()
        });
      }
    });
    
    await page.goto('/', { timeout: 10000 });
    await page.waitForTimeout(3000);
    
    // 英文模式測試
    const englishButton = page.locator('button:has-text("English")');
    if (await englishButton.count() > 0) {
      await englishButton.click();
      await page.waitForTimeout(1000);
    }
    
    await page.fill('input[type="text"]', 'AAPL');
    const analyzeButton = page.locator('button:has-text("Analyze")').first();
    if (await analyzeButton.count() > 0) {
      await analyzeButton.click();
      await page.waitForTimeout(3000);
    }
    
    // 繁體中文模式測試
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(1000);
      
      const chineseAnalyzeButton = page.locator('button:has-text("分析")').first();
      if (await chineseAnalyzeButton.count() > 0) {
        await chineseAnalyzeButton.click();
        await page.waitForTimeout(3000);
      }
    }
    
    // 檢查 API 請求
    console.log(`📡 捕獲到 ${apiRequests.length} 個分析請求`);
    
    for (let i = 0; i < apiRequests.length; i++) {
      const request = apiRequests[i];
      console.log(`請求 ${i + 1}:`);
      console.log(`  URL: ${request.url}`);
      console.log(`  POST Data: ${request.postData || 'No data'}`);
      
      if (request.postData) {
        try {
          const data = JSON.parse(request.postData);
          console.log(`  語言參數: ${data.language || '未設定'}`);
        } catch (e) {
          console.log('  無法解析 POST 數據');
        }
      }
    }
    
    console.log('✅ API 請求監控完成');
  });
});