const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('🔧 測試最終修復版本...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    console.log('✅ 頁面載入成功');
    
    // 點擊登入按鈕
    const loginButton = page.locator('button:has-text("登入")').first();
    console.log('🖱️ 點擊登入按鈕...');
    await loginButton.click();
    await page.waitForTimeout(2000);
    
    // 檢查模態框
    const modal = page.locator('.fixed.inset-0.bg-black').first();
    const modalVisible = await modal.isVisible();
    console.log('模態框可見:', modalVisible ? '✅' : '❌');
    
    if (modalVisible) {
      // 檢查模態框尺寸
      const modalInfo = await modal.evaluate((element) => {
        const rect = element.getBoundingClientRect();
        return {
          x: rect.x,
          y: rect.y,
          width: rect.width,
          height: rect.height
        };
      });
      
      console.log('模態框尺寸:', modalInfo);
      
      // 檢查是否有輸入框
      const emailInput = await modal.locator('input[type="email"]').count();
      const passwordInput = await modal.locator('input[type="password"]').count();
      console.log('輸入框數量 - Email:', emailInput, 'Password:', passwordInput);
      
      if (emailInput > 0 && passwordInput > 0) {
        console.log('🎉 登入模態框完全正常！');
      }
    }
    
    await page.waitForTimeout(3000);
    
  } catch (error) {
    console.error('❌ 錯誤:', error);
  } finally {
    await browser.close();
  }
})();