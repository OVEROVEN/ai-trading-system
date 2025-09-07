const { test, expect } = require('@playwright/test');

test('Test Portal modal solution', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  console.log('=== 測試Portal模態框解決方案 ===');
  
  // 截圖：開啟前
  await page.screenshot({ 
    path: 'test-results/portal-before.png',
    fullPage: true
  });
  
  // 開啟登入模態框
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(2000);
  
  // 截圖：開啟後
  await page.screenshot({ 
    path: 'test-results/portal-after.png',
    fullPage: true
  });
  
  // 檢查Portal是否正確創建
  const portalOverlay = page.locator('.modal-overlay-portal');
  const portalExists = await portalOverlay.count();
  console.log(`Portal overlay 存在: ${portalExists > 0 ? '✅' : '❌'} (數量: ${portalExists})`);
  
  if (portalExists > 0) {
    // 檢查Portal的樣式
    const portalStyles = await portalOverlay.evaluate(el => {
      const styles = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      return {
        zIndex: styles.zIndex,
        position: styles.position,
        display: styles.display,
        visibility: styles.visibility,
        opacity: styles.opacity,
        pointerEvents: styles.pointerEvents,
        rect: {
          x: Math.round(rect.x),
          y: Math.round(rect.y),
          width: Math.round(rect.width),
          height: Math.round(rect.height)
        }
      };
    });
    
    console.log('Portal樣式:', portalStyles);
    
    // 檢查模態框內容是否在Portal中
    const modalDialog = portalOverlay.locator('.bg-slate-800');
    const dialogExists = await modalDialog.count();
    console.log(`模態框對話框存在: ${dialogExists > 0 ? '✅' : '❌'}`);
    
    if (dialogExists > 0) {
      const dialogInfo = await modalDialog.evaluate(el => {
        const styles = getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return {
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          },
          styles: {
            zIndex: styles.zIndex,
            opacity: styles.opacity,
            visibility: styles.visibility,
            display: styles.display
          },
          isVisible: rect.width > 0 && rect.height > 0 && styles.opacity !== '0' && styles.visibility === 'visible'
        };
      });
      
      console.log('對話框信息:', dialogInfo);
      console.log(`對話框可見性: ${dialogInfo.isVisible ? '✅ 可見' : '❌ 不可見'}`);
      
      // 測試內容元素
      const titleVisible = await modalDialog.locator('h2').isVisible();
      const emailVisible = await modalDialog.locator('input[type="email"]').isVisible();
      const passwordVisible = await modalDialog.locator('input[type="password"]').isVisible();
      
      console.log('內容元素可見性:');
      console.log(`- 標題: ${titleVisible ? '✅' : '❌'}`);
      console.log(`- Email輸入框: ${emailVisible ? '✅' : '❌'}`);
      console.log(`- 密碼輸入框: ${passwordVisible ? '✅' : '❌'}`);
      
      // 測試輸入功能
      if (emailVisible) {
        const emailInput = modalDialog.locator('input[type="email"]');
        await emailInput.fill('portal-test@example.com');
        const inputValue = await emailInput.inputValue();
        console.log(`輸入測試: ${inputValue === 'portal-test@example.com' ? '✅ 成功' : '❌ 失敗'}`);
      }
    }
  }
  
  // 檢查模態框是否真的在頁面最上層
  console.log('\n=== 檢查視覺層級 ===');
  
  // 找出頁面中z-index最高的元素
  const highestZIndexElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const zIndexElements = [];
    
    elements.forEach(el => {
      const styles = getComputedStyle(el);
      const zIndex = styles.zIndex === 'auto' ? 0 : parseInt(styles.zIndex);
      const rect = el.getBoundingClientRect();
      
      if (zIndex > 1000000) {  // 只查看極高z-index
        zIndexElements.push({
          tagName: el.tagName,
          className: el.className.substring(0, 30),
          zIndex: zIndex,
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          }
        });
      }
    });
    
    return zIndexElements.sort((a, b) => b.zIndex - a.zIndex);
  });
  
  console.log('極高z-index元素:');
  highestZIndexElements.forEach((el, index) => {
    console.log(`${index + 1}. ${el.tagName} (${el.className}) - z-index: ${el.zIndex}`);
    console.log(`   位置: ${el.rect.x}, ${el.rect.y}, ${el.rect.width}x${el.rect.height}`);
  });
  
  // 模態框特寫截圖
  if (portalExists > 0) {
    await portalOverlay.screenshot({
      path: 'test-results/portal-modal-focused.png'
    });
    console.log('✅ 已保存Portal模態框特寫');
  }
  
  // 測試關閉功能
  console.log('\n=== 測試關閉功能 ===');
  const closeButton = page.locator('.modal-overlay-portal button[aria-label="關閉登入視窗"]');
  if (await closeButton.count() > 0) {
    await closeButton.click();
    await page.waitForTimeout(1000);
    
    const portalAfterClose = await page.locator('.modal-overlay-portal').count();
    console.log(`關閉後Portal存在: ${portalAfterClose === 0 ? '✅ 已移除' : '❌ 仍存在'}`);
  }
  
  console.log('\n=== Portal解決方案測試完成 ===');
});