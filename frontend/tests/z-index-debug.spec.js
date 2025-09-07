const { test, expect } = require('@playwright/test');

test.describe('Login Modal Z-Index and Interaction Debug', () => {
  test('Check if login modal is truly on top and interactive', async ({ page }) => {
    // 訪問首頁
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    console.log('=== 檢查頁面初始狀態 ===');
    
    // 截取初始狀態
    await page.screenshot({ 
      path: 'test-results/z-index-01-initial.png',
      fullPage: true
    });
    
    // 獲取所有元素的z-index
    const initialZIndexElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const zIndexElements = [];
      
      elements.forEach((el, index) => {
        const styles = getComputedStyle(el);
        const zIndex = styles.zIndex;
        const position = styles.position;
        
        if (zIndex !== 'auto' && (position === 'fixed' || position === 'absolute' || position === 'relative')) {
          zIndexElements.push({
            tagName: el.tagName,
            className: el.className,
            id: el.id,
            zIndex: parseInt(zIndex) || 0,
            position: position,
            isVisible: el.offsetWidth > 0 && el.offsetHeight > 0
          });
        }
      });
      
      return zIndexElements.sort((a, b) => b.zIndex - a.zIndex);
    });
    
    console.log('初始頁面高z-index元素:', initialZIndexElements.slice(0, 10));
    
    // 點擊登入按鈕
    const loginButton = page.locator('button:has-text("Login")');
    await expect(loginButton).toBeVisible();
    
    console.log('=== 點擊登入按鈕 ===');
    await loginButton.click();
    await page.waitForTimeout(500);
    
    // 截取模態框打開狀態
    await page.screenshot({ 
      path: 'test-results/z-index-02-modal-opened.png',
      fullPage: true
    });
    
    // 檢查模態框是否存在
    const modal = page.locator('.fixed.inset-0');
    const modalDialog = page.locator('.bg-slate-800.rounded-xl');
    
    const isModalVisible = await modal.isVisible();
    const isDialogVisible = await modalDialog.isVisible();
    
    console.log('模態框可見性:', { modal: isModalVisible, dialog: isDialogVisible });
    
    if (!isModalVisible) {
      console.log('❌ 模態框不可見！');
      return;
    }
    
    // 檢查模態框打開後的z-index狀況
    const modalZIndexElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const zIndexElements = [];
      
      elements.forEach((el) => {
        const styles = getComputedStyle(el);
        const zIndex = styles.zIndex;
        const position = styles.position;
        
        if (zIndex !== 'auto' && parseInt(zIndex) > 0) {
          const rect = el.getBoundingClientRect();
          zIndexElements.push({
            tagName: el.tagName,
            className: el.className.substring(0, 50),
            id: el.id,
            zIndex: parseInt(zIndex),
            position: position,
            isVisible: rect.width > 0 && rect.height > 0,
            rect: {
              top: Math.round(rect.top),
              left: Math.round(rect.left),
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            }
          });
        }
      });
      
      return zIndexElements.sort((a, b) => b.zIndex - a.zIndex);
    });
    
    console.log('=== 模態框打開後的z-index狀況 ===');
    console.log('所有高z-index元素:', modalZIndexElements);
    
    // 檢查模態框的具體z-index
    const modalZIndex = await modal.evaluate(el => {
      const styles = getComputedStyle(el);
      return {
        zIndex: styles.zIndex,
        position: styles.position,
        display: styles.display
      };
    });
    
    console.log('模態框z-index:', modalZIndex);
    
    // 檢查在模態框中心點擊會命中什麼元素
    const viewportSize = page.viewportSize();
    const centerX = viewportSize.width / 2;
    const centerY = viewportSize.height / 2;
    
    const elementAtCenter = await page.evaluate((x, y) => {
      const el = document.elementFromPoint(x, y);
      if (!el) return null;
      
      const styles = getComputedStyle(el);
      return {
        tagName: el.tagName,
        className: el.className,
        id: el.id,
        zIndex: styles.zIndex,
        position: styles.position,
        isModal: el.closest('.fixed.inset-0') !== null,
        isDialog: el.closest('.bg-slate-800.rounded-xl') !== null
      };
    }, centerX, centerY);
    
    console.log(`視口中心 (${centerX}, ${centerY}) 的元素:`, elementAtCenter);
    
    // 嘗試點擊郵箱輸入框
    console.log('=== 測試表單互動 ===');
    const emailInput = page.locator('input[type="email"]');
    
    try {
      await expect(emailInput).toBeVisible({ timeout: 5000 });
      console.log('✅ 郵箱輸入框可見');
      
      // 檢查輸入框的位置和遮擋情況
      const inputRect = await emailInput.boundingBox();
      console.log('輸入框位置:', inputRect);
      
      // 檢查輸入框中心是否被遮擋
      const inputCenterX = inputRect.x + inputRect.width / 2;
      const inputCenterY = inputRect.y + inputRect.height / 2;
      
      const elementAtInput = await page.evaluate((x, y) => {
        const el = document.elementFromPoint(x, y);
        return {
          tagName: el.tagName,
          className: el.className,
          id: el.id,
          isInputElement: el.tagName === 'INPUT',
          isInModal: el.closest('.bg-slate-800.rounded-xl') !== null
        };
      }, inputCenterX, inputCenterY);
      
      console.log('輸入框中心位置的元素:', elementAtInput);
      
      if (elementAtInput.isInputElement) {
        console.log('✅ 輸入框沒有被遮擋');
      } else {
        console.log('❌ 輸入框被其他元素遮擋:', elementAtInput);
      }
      
      // 嘗試輸入文字
      await emailInput.click({ timeout: 5000 });
      await emailInput.fill('test@example.com');
      
      const inputValue = await emailInput.inputValue();
      if (inputValue === 'test@example.com') {
        console.log('✅ 輸入功能正常');
      } else {
        console.log('❌ 輸入功能異常，值為:', inputValue);
      }
      
    } catch (error) {
      console.log('❌ 郵箱輸入框互動失敗:', error.message);
      
      // 詳細檢查輸入框狀態
      const inputExists = await page.locator('input[type="email"]').count();
      console.log('郵箱輸入框數量:', inputExists);
      
      if (inputExists > 0) {
        const inputVisible = await page.locator('input[type="email"]').first().isVisible();
        const inputEnabled = await page.locator('input[type="email"]').first().isEnabled();
        console.log('輸入框狀態:', { visible: inputVisible, enabled: inputEnabled });
      }
    }
    
    // 截取最終測試狀態
    await page.screenshot({ 
      path: 'test-results/z-index-03-interaction-test.png',
      fullPage: true
    });
    
    // 總結報告
    console.log('=== 測試總結 ===');
    console.log('模態框最高z-index應該是:', Math.max(...modalZIndexElements.map(el => el.zIndex)));
    console.log('是否有元素z-index高於模態框:', modalZIndexElements.some(el => 
      el.zIndex > (modalZIndex.zIndex === 'auto' ? 0 : parseInt(modalZIndex.zIndex))
    ));
  });
  
  test('Force interaction test with different methods', async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 打開模態框
    await page.locator('button:has-text("Login")').click();
    await page.waitForTimeout(500);
    
    console.log('=== 嘗試不同的互動方法 ===');
    
    const emailInput = page.locator('input[type="email"]');
    
    // 方法1: 直接點擊
    try {
      await emailInput.click({ timeout: 3000 });
      await emailInput.fill('method1@test.com');
      console.log('✅ 方法1成功: 直接點擊');
    } catch (error) {
      console.log('❌ 方法1失敗:', error.message);
    }
    
    // 方法2: 強制點擊
    try {
      await emailInput.click({ force: true, timeout: 3000 });
      await emailInput.fill('method2@test.com');
      console.log('✅ 方法2成功: 強制點擊');
    } catch (error) {
      console.log('❌ 方法2失敗:', error.message);
    }
    
    // 方法3: 使用JavaScript直接設值
    try {
      await page.evaluate(() => {
        const input = document.querySelector('input[type="email"]');
        if (input) {
          input.value = 'method3@test.com';
          input.dispatchEvent(new Event('input', { bubbles: true }));
          input.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
      console.log('✅ 方法3成功: JavaScript設值');
    } catch (error) {
      console.log('❌ 方法3失敗:', error.message);
    }
    
    // 檢查最終值
    const finalValue = await emailInput.inputValue();
    console.log('最終輸入框值:', finalValue);
  });
});