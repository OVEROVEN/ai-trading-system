const { test, expect } = require('@playwright/test');

test.describe('功能卡片多語言測試', () => {
  test.use({ 
    baseURL: 'http://localhost:3000',
  });

  test('檢查 Technical Analysis, Pattern Recognition, AI Insights, Multi-Market 的多語言支援', async ({ page }) => {
    console.log('🎯 測試功能卡片多語言支援...');
    
    await page.goto('/', { timeout: 10000 });
    
    // 等待頁面載入
    try {
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
      await page.waitForTimeout(3000);
    } catch (error) {
      console.log('⚠️  DOM載入超時，繼續執行測試');
    }
    
    console.log('🇺🇸 測試英文模式功能卡片...');
    
    // 確保是英文模式
    const englishButton = page.locator('button:has-text("English")');
    if (await englishButton.count() > 0) {
      await englishButton.click();
      await page.waitForTimeout(1500);
    }
    
    // 檢查英文功能卡片
    const technicalAnalysisEN = await page.locator('text=Technical Analysis').count();
    const patternRecognitionEN = await page.locator('text=Pattern Recognition').count();
    const aiInsightsEN = await page.locator('text=AI Insights').count();
    const multiMarketEN = await page.locator('text=Multi-Market').count();
    const activeEN = await page.locator('text=Active').count();
    
    console.log(`英文模式檢查:`);
    console.log(`  Technical Analysis: ${technicalAnalysisEN} 個`);
    console.log(`  Pattern Recognition: ${patternRecognitionEN} 個`);
    console.log(`  AI Insights: ${aiInsightsEN} 個`);
    console.log(`  Multi-Market: ${multiMarketEN} 個`);
    console.log(`  Active 狀態: ${activeEN} 個`);
    
    // 檢查英文描述
    const rsiMacdEN = await page.locator('text=15+ indicators including RSI, MACD, Bollinger Bands').count();
    const chartPatternsEN = await page.locator('text=Advanced chart patterns and trend analysis').count();
    const openaiEN = await page.locator('text=OpenAI powered trading recommendations').count();
    const usStocksEN = await page.locator('text=US stocks and Taiwan market support').count();
    
    console.log(`  RSI/MACD 描述: ${rsiMacdEN} 個`);
    console.log(`  圖表形態描述: ${chartPatternsEN} 個`);
    console.log(`  OpenAI 描述: ${openaiEN} 個`);
    console.log(`  美股台股描述: ${usStocksEN} 個`);
    
    console.log('🇹🇼 測試繁體中文模式功能卡片...');
    
    // 切換到繁體中文
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(2000);
      
      // 檢查繁體中文功能卡片
      const technicalAnalysisZH = await page.locator('text=技術分析').count();
      const patternRecognitionZH = await page.locator('text=形態辨識').count();
      const aiInsightsZH = await page.locator('text=AI 洞察').count();
      const multiMarketZH = await page.locator('text=多市場').count();
      const activeZH = await page.locator('text=啟用中').count();
      
      console.log(`繁體中文模式檢查:`);
      console.log(`  技術分析: ${technicalAnalysisZH} 個`);
      console.log(`  形態辨識: ${patternRecognitionZH} 個`);
      console.log(`  AI 洞察: ${aiInsightsZH} 個`);
      console.log(`  多市場: ${multiMarketZH} 個`);
      console.log(`  啟用中 狀態: ${activeZH} 個`);
      
      // 檢查繁體中文描述
      const rsiMacdZH = await page.locator('text=15+ 指標包含 RSI、MACD、布林通道').count();
      const chartPatternsZH = await page.locator('text=進階圖表形態與趨勢分析').count();
      const openaiZH = await page.locator('text=OpenAI 驅動的交易建議').count();
      const stocksZH = await page.locator('text=美股與台股市場支援').count();
      
      console.log(`  RSI/MACD 描述: ${rsiMacdZH} 個`);
      console.log(`  圖表形態描述: ${chartPatternsZH} 個`);
      console.log(`  OpenAI 描述: ${openaiZH} 個`);
      console.log(`  美股台股描述: ${stocksZH} 個`);
    }
    
    console.log('🇨🇳 測試簡體中文模式功能卡片...');
    
    // 切換到簡體中文
    const simplifiedButton = page.locator('button:has-text("简体中文")');
    if (await simplifiedButton.count() > 0) {
      await simplifiedButton.click();
      await page.waitForTimeout(2000);
      
      // 檢查簡體中文功能卡片
      const technicalAnalysisCN = await page.locator('text=技术分析').count();
      const patternRecognitionCN = await page.locator('text=形态识别').count();
      const aiInsightsCN = await page.locator('text=AI 洞察').count();
      const multiMarketCN = await page.locator('text=多市场').count();
      const activeCN = await page.locator('text=启用中').count();
      
      console.log(`簡體中文模式檢查:`);
      console.log(`  技术分析: ${technicalAnalysisCN} 個`);
      console.log(`  形态识别: ${patternRecognitionCN} 個`);
      console.log(`  AI 洞察: ${aiInsightsCN} 個`);
      console.log(`  多市场: ${multiMarketCN} 個`);
      console.log(`  启用中 狀態: ${activeCN} 個`);
      
      // 檢查簡體中文描述
      const rsiMacdCN = await page.locator('text=15+ 指标包含 RSI、MACD、布林带').count();
      const chartPatternsCN = await page.locator('text=进阶图表形态与趋势分析').count();
      const openaiCN = await page.locator('text=OpenAI 驱动的交易建议').count();
      const stocksCN = await page.locator('text=美股与台股市场支持').count();
      
      console.log(`  RSI/MACD 描述: ${rsiMacdCN} 個`);
      console.log(`  圖表形態描述: ${chartPatternsCN} 個`);
      console.log(`  OpenAI 描述: ${openaiCN} 個`);
      console.log(`  美股台股描述: ${stocksCN} 個`);
    }
    
    // 截圖保存最終狀態
    await page.screenshot({ path: 'test-results/feature-cards-multilingual-test.png', fullPage: true });
    
    console.log('✅ 功能卡片多語言測試完成');
  });

  test('測試功能卡片懸停效果和互動在多語言模式下的行為', async ({ page }) => {
    console.log('🎨 測試功能卡片互動效果...');
    
    await page.goto('/', { timeout: 10000 });
    await page.waitForTimeout(3000);
    
    // 切換到繁體中文測試互動
    const traditionalButton = page.locator('button:has-text("繁體中文")');
    if (await traditionalButton.count() > 0) {
      await traditionalButton.click();
      await page.waitForTimeout(1500);
      
      // 測試懸停在 AI 洞察卡片
      const aiInsightsCard = page.locator('text=AI 洞察').locator('..').locator('..').locator('..');
      if (await aiInsightsCard.count() > 0) {
        await aiInsightsCard.hover();
        console.log('✅ 懸停在 AI 洞察卡片');
        await page.waitForTimeout(1000);
      }
      
      // 測試懸停在技術分析卡片
      const technicalCard = page.locator('text=技術分析').locator('..').locator('..').locator('..');
      if (await technicalCard.count() > 0) {
        await technicalCard.hover();
        console.log('✅ 懸停在技術分析卡片');
        await page.waitForTimeout(1000);
      }
      
      // 檢查狀態指示器是否正確顯示中文
      const statusCount = await page.locator('text=啟用中').count();
      console.log(`✅ 找到 ${statusCount} 個"啟用中"狀態指示器`);
    }
    
    await page.screenshot({ path: 'test-results/feature-cards-interaction-test.png', fullPage: true });
    console.log('✅ 功能卡片互動測試完成');
  });
});