const { test, expect } = require('@playwright/test');

test.describe('組件多語言測試', () => {
  test.use({ 
    baseURL: 'http://localhost:3000',
  });

  test('檢查 Chart Analysis、Performance、AI 組件的多語言支援', async ({ page }) => {
    console.log('🔧 測試組件多語言支援...');
    
    await page.goto('/', { timeout: 10000 });
    
    // 等待頁面載入
    try {
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
      await page.waitForTimeout(3000);
    } catch (error) {
      console.log('⚠️  DOM載入超時，繼續執行測試');
    }
    
    console.log('📊 測試英文模式組件...');
    
    // 確保是英文模式
    const englishButton = page.locator('button:has-text("English")');
    if (await englishButton.count() > 0) {
      await englishButton.click();
      await page.waitForTimeout(1500);
    }
    
    // 檢查英文組件
    const chartAnalysisEN = await page.locator('text=Chart Analysis').count();
    const performanceEN = await page.locator('text=Performance').count();
    const aiAnalysisEN = await page.locator('text=AI Analysis').count();
    const aiConfidenceEN = await page.locator('text=AI Confidence').count();
    const riskLevelEN = await page.locator('text=Risk Level').count();
    
    console.log(`英文模式檢查:`);
    console.log(`  Chart Analysis: ${chartAnalysisEN} 個`);
    console.log(`  Performance: ${performanceEN} 個`);
    console.log(`  AI Analysis: ${aiAnalysisEN} 個`);
    console.log(`  AI Confidence: ${aiConfidenceEN} 個`);
    console.log(`  Risk Level: ${riskLevelEN} 個`);
    
    console.log('🇹🇼 測試繁體中文模式組件...');
    
    // 切換到繁體中文
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(2000);
      
      // 檢查繁體中文組件
      const chartAnalysisZH = await page.locator('text=圖表分析').count();
      const performanceZH = await page.locator('text=績效表現').count();
      const aiAnalysisZH = await page.locator('text=AI 分析').count();
      const aiConfidenceZH = await page.locator('text=AI 信心度').count();
      const riskLevelZH = await page.locator('text=風險等級').count();
      
      console.log(`繁體中文模式檢查:`);
      console.log(`  圖表分析: ${chartAnalysisZH} 個`);
      console.log(`  績效表現: ${performanceZH} 個`);
      console.log(`  AI 分析: ${aiAnalysisZH} 個`);
      console.log(`  AI 信心度: ${aiConfidenceZH} 個`);
      console.log(`  風險等級: ${riskLevelZH} 個`);
      
      // 檢查 Performance 組件內的項目
      const accuracyZH = await page.locator('text=準確度').count();
      const winRateZH = await page.locator('text=勝率').count();
      const riskScoreZH = await page.locator('text=風險評分').count();
      
      console.log(`  準確度: ${accuracyZH} 個`);
      console.log(`  勝率: ${winRateZH} 個`);
      console.log(`  風險評分: ${riskScoreZH} 個`);
    }
    
    console.log('🇨🇳 測試簡體中文模式組件...');
    
    // 切換到簡體中文
    const simplifiedButton = page.locator('button:has-text("简体中文")');
    if (await simplifiedButton.count() > 0) {
      await simplifiedButton.click();
      await page.waitForTimeout(2000);
      
      // 檢查簡體中文組件
      const chartAnalysisCN = await page.locator('text=图表分析').count();
      const performanceCN = await page.locator('text=绩效表现').count();
      const aiAnalysisCN = await page.locator('text=AI 分析').count();
      const aiConfidenceCN = await page.locator('text=AI 信心度').count();
      const riskLevelCN = await page.locator('text=风险等级').count();
      
      console.log(`簡體中文模式檢查:`);
      console.log(`  图表分析: ${chartAnalysisCN} 個`);
      console.log(`  绩效表现: ${performanceCN} 個`);
      console.log(`  AI 分析: ${aiAnalysisCN} 個`);
      console.log(`  AI 信心度: ${aiConfidenceCN} 個`);
      console.log(`  风险等级: ${riskLevelCN} 個`);
    }
    
    // 截圖保存最終狀態
    await page.screenshot({ path: 'test-results/components-multilingual-test.png', fullPage: true });
    
    console.log('✅ 組件多語言測試完成');
  });

  test('測試分析後的 AI 評估項目多語言顯示', async ({ page }) => {
    console.log('🤖 測試分析後的 AI 評估多語言...');
    
    await page.goto('/', { timeout: 10000 });
    await page.waitForTimeout(3000);
    
    // 切換到繁體中文並進行分析
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(1500);
      
      // 輸入股票代碼並分析
      await page.fill('input[type=\"text\"]', 'AAPL');
      const analyzeButton = page.locator('button:has-text("分析")').first();
      if (await analyzeButton.count() > 0) {
        await analyzeButton.click();
        console.log('✅ 點擊分析按鈕');
        
        // 等待分析完成
        await page.waitForTimeout(5000);
        
        // 檢查 AI 相關的中文標籤是否出現
        const labels = [
          'AI 信心度',
          '風險等級', 
          '技術評分',
          '低',
          '中等',
          '高',
          '準確度',
          '勝率',
          '風險評分'
        ];
        
        console.log('📊 檢查 AI 評估標籤:');
        for (const label of labels) {
          const count = await page.locator(`text=${label}`).count();
          console.log(`  ${label}: ${count} 個`);
        }
      }
    }
    
    await page.screenshot({ path: 'test-results/ai-assessment-multilingual.png', fullPage: true });
    console.log('✅ AI 評估多語言測試完成');
  });
});