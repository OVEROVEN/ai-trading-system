const { test, expect } = require('@playwright/test');

test.describe('Fixed Login Modal', () => {
  test('Login modal should appear in center-top position and be fully interactive', async ({ page }) => {
    // 訪問首頁
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 截取初始狀態
    await page.screenshot({ 
      path: 'test-results/fixed-01-homepage.png',
      fullPage: true
    });
    
    // 點擊登入按鈕
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible();
    await loginButton.click();
    
    // 等待模態框動畫完成
    await page.waitForTimeout(500);
    
    // 截取模態框出現狀態
    await page.screenshot({ 
      path: 'test-results/fixed-02-modal-visible.png',
      fullPage: true
    });
    
    // 驗證模態框位置和可見性
    const modal = page.locator('.fixed.inset-0');
    const modalDialog = page.locator('.bg-slate-800.rounded-xl');
    
    await expect(modal).toBeVisible();
    await expect(modalDialog).toBeVisible();
    
    // 檢查模態框是否在正確位置
    const modalRect = await modalDialog.boundingBox();
    const viewportSize = page.viewportSize();
    
    console.log('修復後的模態框位置:', {
      position: modalRect,
      viewport: viewportSize,
      isVisible: modalRect.y >= 0 && modalRect.x >= 0,
      isInTopCenter: modalRect.y >= 50 && modalRect.y <= 200,
      isCenteredHorizontally: Math.abs((modalRect.x + modalRect.width / 2) - (viewportSize.width / 2)) < 100
    });
    
    // 驗證模態框在視口內且位置正確
    expect(modalRect.y).toBeGreaterThanOrEqual(0);
    expect(modalRect.x).toBeGreaterThanOrEqual(0);
    expect(modalRect.y).toBeLessThan(300); // 應該在上半部
    
    // 測試互動功能
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    await emailInput.fill('test@example.com');
    
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible();
    await passwordInput.fill('password123');
    
    // 截取填入資料後的狀態
    await page.screenshot({ 
      path: 'test-results/fixed-03-form-filled.png',
      fullPage: true
    });
    
    // 測試關閉按鈕（現在應該可以點擊）
    const closeButton = page.locator('button[aria-label="關閉登入視窗"]');
    await expect(closeButton).toBeVisible();
    await closeButton.click();
    
    // 驗證模態框已關閉
    await expect(modal).not.toBeVisible();
    
    // 截取關閉後狀態
    await page.screenshot({ 
      path: 'test-results/fixed-04-modal-closed.png',
      fullPage: true
    });
    
    console.log('✅ 登入模態框修復驗證通過');
  });
  
  test('Login modal should work on different screen sizes', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080, name: 'large-desktop' },
      { width: 1024, height: 768, name: 'tablet-landscape' },
      { width: 768, height: 1024, name: 'tablet-portrait' },
      { width: 375, height: 667, name: 'mobile' }
    ];
    
    for (const viewport of viewports) {
      console.log(`測試視口: ${viewport.name} (${viewport.width}x${viewport.height})`);
      
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      // 點擊登入按鈕
      const loginButton = page.locator('button:has-text("Login")');
      await loginButton.click();
      await page.waitForTimeout(300);
      
      // 截圖
      await page.screenshot({ 
        path: `test-results/fixed-${viewport.name}-${viewport.width}x${viewport.height}.png`,
        fullPage: true
      });
      
      // 驗證模態框可見性和位置
      const modalDialog = page.locator('.bg-slate-800.rounded-xl');
      const isVisible = await modalDialog.isVisible();
      
      if (isVisible) {
        const rect = await modalDialog.boundingBox();
        const isInViewport = rect && 
                            rect.x >= 0 && 
                            rect.y >= 0 && 
                            rect.x + rect.width <= viewport.width && 
                            rect.y + rect.height <= viewport.height;
        
        console.log(`${viewport.name}: 可見=${isVisible}, 在視口內=${isInViewport}`);
        expect(isInViewport).toBeTruthy();
        
        // 測試表單是否可以互動
        const emailInput = page.locator('input[type="email"]');
        await emailInput.fill('test@example.com');
        
        // 關閉模態框
        const closeButton = page.locator('button[aria-label="關閉登入視窗"]');
        await closeButton.click();
        await page.waitForTimeout(200);
      } else {
        console.log(`❌ ${viewport.name}: 模態框不可見`);
        expect(isVisible).toBeTruthy();
      }
    }
    
    console.log('✅ 所有視口尺寸測試通過');
  });
  
  test('Background click should close modal', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 開啟模態框
    const loginButton = page.locator('button:has-text("Login")');
    await loginButton.click();
    await page.waitForTimeout(300);
    
    const modal = page.locator('.fixed.inset-0');
    await expect(modal).toBeVisible();
    
    // 點擊背景關閉模態框
    await page.locator('.modal-overlay').click({
      position: { x: 100, y: 100 } // 點擊左上角背景
    });
    
    // 驗證模態框已關閉
    await expect(modal).not.toBeVisible();
    
    console.log('✅ 背景點擊關閉功能正常');
  });
});