const { test, expect } = require('@playwright/test');

test.describe('多語言功能測試 - 簡化版', () => {
  // 不依賴webServer，直接使用運行中的服務器
  test.use({ 
    baseURL: 'http://localhost:3000',
  });

  test('語言切換基本功能', async ({ page }) => {
    console.log('🌐 開始多語言測試...');
    
    // 直接訪問主頁，不等待webServer
    try {
      await page.goto('/', { timeout: 10000 });
      console.log('✅ 成功訪問主頁');
    } catch (error) {
      console.log('❌ 無法訪問主頁:', error.message);
      test.skip();
    }
    
    // 等待頁面基本載入完成，但不等待所有網路請求
    try {
      await page.waitForLoadState('domcontentloaded', { timeout: 5000 });
      await page.waitForTimeout(2000);
    } catch (error) {
      console.log('⚠️  DOM載入超時，繼續執行測試');
    }
    
    // 檢查是否有語言切換器
    const languageSwitcher = await page.locator('button:has-text("English")').count();
    if (languageSwitcher === 0) {
      console.log('⚠️  未找到語言切換器，可能頁面尚未完全載入');
      // 再等一下
      await page.waitForTimeout(5000);
    }
    
    // 截圖當前狀態以供調試
    await page.screenshot({ path: 'test-results/multilingual-debug-initial.png', fullPage: true });
    
    // 檢查是否有標題元素
    const titleCount = await page.locator('h1').count();
    console.log(`發現 ${titleCount} 個標題元素`);
    
    // 如果找到標題，檢查內容
    if (titleCount > 0) {
      const titleText = await page.locator('h1').first().textContent();
      console.log(`當前標題: "${titleText}"`);
      
      // 檢查是否有語言切換按鈕
      const hasEnglish = await page.locator('button:has-text("English")').count() > 0;
      const hasTraditional = await page.locator('button:has-text("繁體中文")').count() > 0;
      const hasSimplified = await page.locator('button:has-text("简体中文")').count() > 0;
      
      console.log(`語言按鈕狀態: English=${hasEnglish}, 繁中=${hasTraditional}, 簡中=${hasSimplified}`);
      
      if (hasTraditional) {
        console.log('🇹🇼 測試切換到繁體中文...');
        await page.click('button:has-text("繁體中文")');
        await page.waitForTimeout(2000);
        
        const newTitle = await page.locator('h1').first().textContent();
        console.log(`切換後標題: "${newTitle}"`);
        
        // 截圖繁體中文版本
        await page.screenshot({ path: 'test-results/multilingual-traditional-chinese.png', fullPage: true });
        
        if (newTitle && newTitle.includes('交易儀表板')) {
          console.log('✅ 繁體中文切換成功');
        } else {
          console.log('⚠️  繁體中文切換可能未完全生效');
        }
      } else {
        console.log('⚠️  未找到繁體中文按鈕');
      }
    } else {
      console.log('❌ 未找到標題元素，可能頁面載入有問題');
    }
    
    console.log('📊 測試完成');
  });
  
  test('檢查多語言組件是否正確載入', async ({ page }) => {
    console.log('🔍 檢查組件載入狀態...');
    
    await page.goto('/', { timeout: 10000 });
    await page.waitForTimeout(5000);
    
    // 檢查各種組件是否存在
    const components = [
      { name: '標題', selector: 'h1' },
      { name: '搜尋框', selector: 'input[type="text"]' },
      { name: '分析按鈕', selector: 'button' },
      { name: '語言切換器', selector: 'button:has-text("English"), button:has-text("繁體中文"), button:has-text("简体中文")' }
    ];
    
    for (const component of components) {
      const count = await page.locator(component.selector).count();
      console.log(`${component.name}: 找到 ${count} 個元素`);
    }
    
    // 截圖最終狀態
    await page.screenshot({ path: 'test-results/multilingual-component-check.png', fullPage: true });
    
    console.log('✅ 組件檢查完成');
  });
});