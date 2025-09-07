const { test, expect } = require('@playwright/test');

test.describe('Login Modal Position Debug', () => {
  test('Debug login modal position and visibility', async ({ page }) => {
    // 訪問首頁
    await page.goto('http://localhost:3000');
    
    // 等待頁面完全加載
    await page.waitForLoadState('networkidle');
    
    // 截取初始頁面狀態
    await page.screenshot({ 
      path: 'test-results/01-homepage-initial.png',
      fullPage: true
    });
    
    // 查找登入按鈕
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible();
    
    // 點擊登入按鈕
    await loginButton.click();
    
    // 等待模態框出現
    await page.waitForTimeout(500);
    
    // 截取登入模態框狀態
    await page.screenshot({ 
      path: 'test-results/02-modal-opened.png',
      fullPage: true
    });
    
    // 檢查登入模態框的位置和屬性
    const modal = page.locator('.fixed.inset-0');
    const modalDialog = page.locator('.bg-slate-800.rounded-xl');
    
    // 驗證模態框可見性
    await expect(modal).toBeVisible();
    await expect(modalDialog).toBeVisible();
    
    // 獲取模態框的樣式資訊
    const modalStyles = await modal.evaluate(el => {
      const styles = getComputedStyle(el);
      return {
        position: styles.position,
        zIndex: styles.zIndex,
        display: styles.display,
        top: styles.top,
        left: styles.left,
        right: styles.right,
        bottom: styles.bottom,
        background: styles.backgroundColor
      };
    });
    
    const dialogStyles = await modalDialog.evaluate(el => {
      const styles = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return {
        position: styles.position,
        maxWidth: styles.maxWidth,
        width: styles.width,
        top: rect.top,
        left: rect.left,
        centerX: rect.left + rect.width / 2,
        centerY: rect.top + rect.height / 2,
        height: rect.height,
        width: rect.width
      };
    });
    
    // 獲取視口尺寸
    const viewportSize = page.viewportSize();
    
    console.log('=== 登入模態框調試資訊 ===');
    console.log('視口尺寸:', viewportSize);
    console.log('模態框背景樣式:', modalStyles);
    console.log('對話框樣式和位置:', dialogStyles);
    console.log('對話框是否在視口中央:', {
      horizontalCenter: Math.abs(dialogStyles.centerX - viewportSize.width / 2) < 50,
      verticalCenter: Math.abs(dialogStyles.centerY - viewportSize.height / 2) < 100
    });
    
    // 測試是否被其他元素遮擋
    const elementsAtCenter = await page.evaluate(() => {
      const centerX = window.innerWidth / 2;
      const centerY = window.innerHeight / 2;
      const elementAtCenter = document.elementFromPoint(centerX, centerY);
      return {
        tagName: elementAtCenter?.tagName,
        className: elementAtCenter?.className,
        id: elementAtCenter?.id
      };
    });
    
    console.log('視口中央的元素:', elementsAtCenter);
    
    // 檢查是否有其他元素的z-index更高
    const highZIndexElements = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      const highZElements = [];
      
      allElements.forEach(el => {
        const zIndex = getComputedStyle(el).zIndex;
        if (zIndex !== 'auto' && parseInt(zIndex) > 50) {
          highZElements.push({
            tagName: el.tagName,
            className: el.className,
            zIndex: zIndex,
            id: el.id
          });
        }
      });
      
      return highZElements.sort((a, b) => parseInt(b.zIndex) - parseInt(a.zIndex));
    });
    
    console.log('高z-index元素:', highZIndexElements);
    
    // 測試模態框互動性
    await expect(modalDialog).toBeVisible();
    
    // 嘗試在模態框內輸入
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible();
    await emailInput.fill('test@example.com');
    
    // 截取最終狀態
    await page.screenshot({ 
      path: 'test-results/03-modal-interaction.png',
      fullPage: true
    });
    
    // 測試關閉按鈕
    const closeButton = page.locator('button:has-text("✕")');
    await expect(closeButton).toBeVisible();
    await closeButton.click();
    
    // 驗證模態框已關閉
    await expect(modal).not.toBeVisible();
    
    // 截取關閉後狀態
    await page.screenshot({ 
      path: 'test-results/04-modal-closed.png',
      fullPage: true
    });
  });
  
  test('Test modal on different viewport sizes', async ({ page }) => {
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop' },
      { width: 1024, height: 768, name: 'tablet' },
      { width: 375, height: 667, name: 'mobile' }
    ];
    
    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await page.goto('http://localhost:3000');
      await page.waitForLoadState('networkidle');
      
      const loginButton = page.locator('button:has-text("Login")');
      await loginButton.click();
      await page.waitForTimeout(500);
      
      await page.screenshot({ 
        path: `test-results/modal-${viewport.name}-${viewport.width}x${viewport.height}.png`,
        fullPage: true
      });
      
      const modalDialog = page.locator('.bg-slate-800.rounded-xl');
      const rect = await modalDialog.boundingBox();
      
      console.log(`${viewport.name} (${viewport.width}x${viewport.height}):`, {
        modalVisible: await modalDialog.isVisible(),
        modalPosition: rect,
        isInViewport: rect && rect.x >= 0 && rect.y >= 0 && 
                     rect.x + rect.width <= viewport.width && 
                     rect.y + rect.height <= viewport.height
      });
      
      const closeButton = page.locator('button:has-text("✕")');
      await closeButton.click();
      await page.waitForTimeout(200);
    }
  });
});