const { test, expect } = require('@playwright/test');

test('Check modal visual display and overlay issues', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  console.log('=== 檢查模態框視覺顯示問題 ===');
  
  // 截圖：開啟模態框之前
  await page.screenshot({ 
    path: 'test-results/before-modal.png',
    fullPage: true
  });
  console.log('✅ 已保存開啟前截圖');
  
  // 開啟登入模態框
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(2000); // 等待動畫完成
  
  // 截圖：模態框開啟後
  await page.screenshot({ 
    path: 'test-results/after-modal.png',
    fullPage: true
  });
  console.log('✅ 已保存開啟後截圖');
  
  // 檢查模態框是否可見
  const modal = page.locator('[style*="z-index: 999999"]');
  await expect(modal).toBeVisible();
  
  // 獲取模態框的詳細信息
  const modalInfo = await modal.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const styles = getComputedStyle(el);
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
        transform: styles.transform,
        backgroundColor: styles.backgroundColor,
        backdropFilter: styles.backdropFilter,
        position: styles.position
      }
    };
  });
  
  console.log('模態框信息:');
  console.log('位置:', modalInfo.rect);
  console.log('樣式:', modalInfo.styles);
  
  // 檢查模態框內容（實際的對話框）
  const modalDialog = page.locator('.bg-slate-800.rounded-xl');
  const dialogInfo = await modalDialog.evaluate(el => {
    const rect = el.getBoundingClientRect();
    const styles = getComputedStyle(el);
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
        backgroundColor: styles.backgroundColor,
        transform: styles.transform,
        boxShadow: styles.boxShadow
      },
      isVisible: rect.width > 0 && rect.height > 0 && styles.opacity !== '0'
    };
  });
  
  console.log('\n對話框信息:');
  console.log('位置:', dialogInfo.rect);
  console.log('樣式:', dialogInfo.styles);
  console.log('可見性:', dialogInfo.isVisible ? '✅ 可見' : '❌ 不可見');
  
  // 檢查可能覆蓋模態框的元素
  console.log('\n=== 檢查覆蓋元素 ===');
  
  const overlappingElements = await page.evaluate(() => {
    const modal = document.querySelector('[style*="z-index: 999999"]');
    const modalRect = modal ? modal.getBoundingClientRect() : null;
    
    if (!modalRect) return [];
    
    const elements = document.querySelectorAll('*');
    const overlapping = [];
    
    elements.forEach(el => {
      if (el === modal || modal.contains(el)) return;
      
      const rect = el.getBoundingClientRect();
      const styles = getComputedStyle(el);
      const zIndex = styles.zIndex === 'auto' ? 0 : parseInt(styles.zIndex);
      
      // 檢查是否與模態框重疊
      const isOverlapping = !(rect.right < modalRect.left || 
                              rect.left > modalRect.right || 
                              rect.bottom < modalRect.top || 
                              rect.top > modalRect.bottom);
      
      if (isOverlapping && rect.width > 50 && rect.height > 50) {
        overlapping.push({
          tagName: el.tagName,
          className: el.className.substring(0, 40),
          id: el.id,
          zIndex: zIndex,
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          },
          styles: {
            position: styles.position,
            opacity: styles.opacity,
            visibility: styles.visibility,
            backgroundColor: styles.backgroundColor,
            pointerEvents: styles.pointerEvents
          }
        });
      }
    });
    
    return overlapping.sort((a, b) => b.zIndex - a.zIndex);
  });
  
  console.log(`發現 ${overlappingElements.length} 個可能覆蓋的元素:`);
  overlappingElements.forEach((el, index) => {
    console.log(`${index + 1}. ${el.tagName} (z-index: ${el.zIndex})`);
    console.log(`   class: ${el.className}`);
    console.log(`   位置: ${el.rect.x}, ${el.rect.y}, ${el.rect.width}x${el.rect.height}`);
    console.log(`   opacity: ${el.styles.opacity}, visibility: ${el.styles.visibility}`);
    console.log(`   pointerEvents: ${el.styles.pointerEvents}`);
    
    if (el.zIndex >= 999999) {
      console.log('🚨 此元素z-index等於或高於模態框!');
    }
  });
  
  // 檢查模糊效果
  console.log('\n=== 檢查模糊效果 ===');
  const blurElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const blurred = [];
    
    elements.forEach(el => {
      const styles = getComputedStyle(el);
      if (styles.filter && (styles.filter.includes('blur') || styles.backdropFilter.includes('blur'))) {
        const rect = el.getBoundingClientRect();
        blurred.push({
          tagName: el.tagName,
          className: el.className.substring(0, 30),
          filter: styles.filter,
          backdropFilter: styles.backdropFilter,
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          }
        });
      }
    });
    
    return blurred;
  });
  
  console.log(`發現 ${blurElements.length} 個模糊元素:`);
  blurElements.forEach((el, index) => {
    console.log(`${index + 1}. ${el.tagName}`);
    console.log(`   class: ${el.className}`);
    console.log(`   filter: ${el.filter}`);
    console.log(`   backdrop-filter: ${el.backdropFilter}`);
    console.log(`   位置: ${el.rect.x}, ${el.rect.y}, ${el.rect.width}x${el.rect.height}`);
  });
  
  // 測試模態框內容的可讀性
  console.log('\n=== 測試內容可讀性 ===');
  const titleVisible = await page.locator('h2:has-text("Login")').isVisible();
  const emailInputVisible = await page.locator('input[type="email"]').isVisible();
  const passwordInputVisible = await page.locator('input[type="password"]').isVisible();
  const submitButtonVisible = await page.locator('button[type="submit"]').isVisible();
  
  console.log('標題可見:', titleVisible ? '✅' : '❌');
  console.log('Email輸入框可見:', emailInputVisible ? '✅' : '❌');
  console.log('密碼輸入框可見:', passwordInputVisible ? '✅' : '❌');
  console.log('提交按鈕可見:', submitButtonVisible ? '✅' : '❌');
  
  // 最終截圖，聚焦在模態框區域
  await page.locator('.bg-slate-800.rounded-xl').screenshot({
    path: 'test-results/modal-focused.png'
  });
  console.log('✅ 已保存模態框特寫截圖');
  
  console.log('\n=== 視覺檢查總結 ===');
  const hasHighZIndexOverlays = overlappingElements.some(el => el.zIndex >= 999999);
  const hasVisibilityIssues = !titleVisible || !emailInputVisible || !passwordInputVisible;
  
  if (hasHighZIndexOverlays) {
    console.log('🚨 發現高z-index覆蓋元素，可能影響顯示');
  }
  if (hasVisibilityIssues) {
    console.log('🚨 發現內容可見性問題');
  }
  if (!hasHighZIndexOverlays && !hasVisibilityIssues) {
    console.log('✅ 視覺顯示正常，無覆蓋問題');
  }
});