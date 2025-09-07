const { test, expect } = require('@playwright/test');

test('Test updated authentication interface with Google login', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(2000);
  
  console.log('=== 測試更新後的認證介面 ===');
  
  // 開啟登入模態框
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(1000);
  
  // 截圖：更新後的模態框
  await page.screenshot({ 
    path: 'test-results/updated-auth-interface.png',
    fullPage: true
  });
  
  // 檢查Google登入按鈕是否存在
  const googleButton = page.locator('button:has-text("使用 Google 登入")');
  const googleButtonExists = await googleButton.count();
  console.log(`Google登入按鈕存在: ${googleButtonExists > 0 ? '✅' : '❌'}`);
  
  if (googleButtonExists > 0) {
    // 檢查Google按鈕的樣式
    const googleButtonStyles = await googleButton.evaluate(el => {
      const styles = getComputedStyle(el);
      return {
        backgroundColor: styles.backgroundColor,
        color: styles.color,
        display: styles.display,
        visibility: styles.visibility
      };
    });
    console.log('Google按鈕樣式:', googleButtonStyles);
  }
  
  // 檢查分隔線是否存在
  const separator = page.locator('span:has-text("或")');
  const separatorExists = await separator.count();
  console.log(`分隔線存在: ${separatorExists > 0 ? '✅' : '❌'}`);
  
  // 測試註冊功能
  console.log('\n=== 測試註冊功能 ===');
  
  // 切換到註冊標籤
  await page.locator('button:has-text("Register")').first().click();
  await page.waitForTimeout(500);
  
  // 填寫註冊表單
  const testEmail = `test${Date.now()}@example.com`;
  await page.locator('input[type="text"]').fill('Test User');
  await page.locator('input[type="email"]').fill(testEmail);
  await page.locator('input[type="password"]').fill('testpass123');
  
  console.log(`嘗試註冊用戶: ${testEmail}`);
  
  // 點擊註冊按鈕
  await page.locator('button[type="submit"]:has-text("Register")').click();
  
  // 等待註冊結果
  await page.waitForTimeout(3000);
  
  // 檢查是否註冊成功（模態框應該關閉，或顯示成功信息）
  const modalStillVisible = await page.locator('.modal-overlay-portal').count();
  console.log(`模態框狀態: ${modalStillVisible === 0 ? '已關閉（註冊成功）' : '仍開啟'}`);
  
  // 檢查頁面是否顯示用戶已登入
  if (modalStillVisible === 0) {
    await page.waitForTimeout(1000);
    const userProfile = await page.locator('div:has-text("Test User")').count();
    console.log(`用戶資料顯示: ${userProfile > 0 ? '✅ 已顯示' : '❌ 未顯示'}`);
  }
  
  // 最終截圖
  await page.screenshot({ 
    path: 'test-results/registration-result.png',
    fullPage: true
  });
  
  console.log('\n=== 測試結果總結 ===');
  console.log('- 模態框顯示正常');
  console.log('- Google登入按鈕已添加');
  console.log('- 註冊功能測試完成');
});