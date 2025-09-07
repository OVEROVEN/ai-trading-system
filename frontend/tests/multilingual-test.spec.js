const { test, expect } = require('@playwright/test');

test.describe('多語言功能測試', () => {
  test('語言切換功能測試', async ({ page }) => {
    console.log('🌐 開始多語言測試...');
    
    // 訪問主頁
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    console.log('✅ 頁面載入完成');
    
    // 檢查預設語言（應該是英文）
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    console.log('✅ 預設英文顯示正常');
    
    // 截圖英文版本
    await page.screenshot({ path: 'test-results/multilingual-english.png', fullPage: true });
    
    // 切換到繁體中文
    console.log('🇹🇼 切換到繁體中文...');
    await page.click('button:has-text("繁體中文")');
    await page.waitForTimeout(2000);
    
    // 驗證繁體中文
    await expect(page.locator('h1')).toContainText('AI 交易儀表板');
    await expect(page.locator('text=即時分析')).toBeVisible();
    await expect(page.locator('text=AI 建議')).toBeVisible();
    await expect(page.locator('text=市場資料')).toBeVisible();
    await expect(page.locator('text=AI 分析')).toBeVisible();
    console.log('✅ 繁體中文顯示正常');
    
    // 截圖繁體中文版本
    await page.screenshot({ path: 'test-results/multilingual-traditional-chinese.png', fullPage: true });
    
    // 切換到簡體中文
    console.log('🇨🇳 切換到簡体中文...');
    await page.click('button:has-text("简体中文")');
    await page.waitForTimeout(2000);
    
    // 驗證簡體中文
    await expect(page.locator('h1')).toContainText('AI 交易仪表板');
    await expect(page.locator('text=实时分析')).toBeVisible();
    await expect(page.locator('text=AI 建议')).toBeVisible();
    await expect(page.locator('text=市场数据')).toBeVisible();
    await expect(page.locator('text=AI 分析')).toBeVisible();
    console.log('✅ 簡體中文顯示正常');
    
    // 截圖簡體中文版本
    await page.screenshot({ path: 'test-results/multilingual-simplified-chinese.png', fullPage: true });
    
    // 切換回英文
    console.log('🇺🇸 切換回英文...');
    await page.click('button:has-text("English")');
    await page.waitForTimeout(2000);
    
    // 驗證英文
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    await expect(page.locator('text=Real-time Analysis')).toBeVisible();
    await expect(page.locator('text=AI Recommendations')).toBeVisible();
    await expect(page.locator('text=Market Data')).toBeVisible();
    await expect(page.locator('text=AI Analysis')).toBeVisible();
    console.log('✅ 切換回英文成功');
    
    // 測試語言持久化（重新載入頁面）
    console.log('🔄 測試語言持久化...');
    await page.reload();
    await page.waitForTimeout(2000);
    
    // 應該仍然是英文
    await expect(page.locator('h1')).toContainText('AI Trading Dashboard');
    console.log('✅ 語言設定持久化正常');
    
    // 測試搜尋欄placeholder翻譯
    console.log('🔍 測試搜尋功能翻譯...');
    await page.click('button:has-text("繁體中文")');
    await page.waitForTimeout(1000);
    
    const searchInput = page.locator('input[type="text"]').first();
    const placeholder = await searchInput.getAttribute('placeholder');
    expect(placeholder).toContain('股票代號');
    console.log('✅ 搜尋欄翻譯正常');
    
    // 測試按鈕翻譯
    await expect(page.locator('button:has-text("分析")')).toBeVisible();
    await expect(page.locator('text=熱門')).toBeVisible();
    console.log('✅ 按鈕翻譯正常');
    
    // 最終截圖
    await page.screenshot({ path: 'test-results/multilingual-final.png', fullPage: true });
    
    console.log('🎉 多語言測試全部完成！');
  });
  
  test('語言切換器響應式測試', async ({ page }) => {
    console.log('📱 開始響應式測試...');
    
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(2000);
    
    // 測試桌面版語言切換器
    console.log('🖥️ 測試桌面版語言切換器...');
    await expect(page.locator('button:has-text("English")')).toBeVisible();
    await expect(page.locator('button:has-text("繁體中文")')).toBeVisible();
    await expect(page.locator('button:has-text("简体中文")')).toBeVisible();
    
    // 切換到手機版
    console.log('📱 切換到手機版...');
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(1000);
    
    // 在手機版上語言切換器應該仍然可見（但可能只顯示國旗）
    await expect(page.locator('button:has([title="English"])')).toBeVisible();
    await expect(page.locator('button:has([title="繁體中文"])')).toBeVisible();
    await expect(page.locator('button:has([title="简体中文"])')).toBeVisible();
    
    // 測試手機版語言切換功能
    await page.click('button:has([title="繁體中文"])');
    await page.waitForTimeout(1000);
    await expect(page.locator('h1')).toContainText('AI 交易儀表板');
    
    // 截圖手機版
    await page.screenshot({ path: 'test-results/multilingual-mobile.png', fullPage: true });
    
    console.log('✅ 響應式測試完成');
  });
});