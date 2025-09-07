const { test, expect } = require('@playwright/test');

test('Check if TradingView blocks login interface', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  console.log('=== 檢查TradingView是否阻擋登入介面 ===');
  
  // 開啟登入模態框
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(1000);
  
  // 檢查登入模態框
  const modal = page.locator('[style*="z-index: 99999"]');
  await expect(modal).toBeVisible();
  console.log('✅ 模態框顯示正常');
  
  // 檢查頁面上所有的iframe (TradingView通常用iframe)
  const iframes = await page.locator('iframe').all();
  console.log(`發現 ${iframes.length} 個iframe`);
  
  for (let i = 0; i < iframes.length; i++) {
    const iframe = iframes[i];
    const src = await iframe.getAttribute('src');
    const rect = await iframe.boundingBox();
    const zIndex = await iframe.evaluate(el => getComputedStyle(el).zIndex);
    
    console.log(`iframe ${i + 1}:`);
    console.log(`  - src: ${src?.substring(0, 60)}...`);
    console.log(`  - 位置: x=${rect?.x}, y=${rect?.y}, w=${rect?.width}, h=${rect?.height}`);
    console.log(`  - z-index: ${zIndex}`);
    
    if (src && (src.includes('tradingview') || src.includes('trading-view'))) {
      console.log('⚠️  發現TradingView iframe!');
      
      // 檢查是否與模態框重疊
      const modalRect = await modal.boundingBox();
      if (rect && modalRect) {
        const overlapping = !(rect.x + rect.width < modalRect.x || 
                             modalRect.x + modalRect.width < rect.x || 
                             rect.y + rect.height < modalRect.y || 
                             modalRect.y + modalRect.height < rect.y);
        
        if (overlapping) {
          console.log('❌ TradingView iframe與模態框重疊!');
          console.log('TradingView rect:', rect);
          console.log('Modal rect:', modalRect);
          console.log('TradingView z-index:', zIndex);
          console.log('Modal z-index: 99999');
          
          if (parseInt(zIndex) >= 99999) {
            console.log('🚨 TradingView z-index過高，可能阻擋模態框!');
          }
        } else {
          console.log('✅ TradingView iframe與模態框無重疊');
        }
      }
    }
  }
  
  // 檢查所有高z-index元素
  console.log('\n=== 檢查高z-index元素 ===');
  const highZIndexElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const highElements = [];
    
    elements.forEach(el => {
      const styles = getComputedStyle(el);
      const zIndex = styles.zIndex === 'auto' ? 0 : parseInt(styles.zIndex);
      const rect = el.getBoundingClientRect();
      
      if (zIndex >= 50000) {  // 檢查z-index >= 50000的元素
        highElements.push({
          tagName: el.tagName,
          className: el.className.substring(0, 40),
          zIndex: zIndex,
          rect: {
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
          },
          innerHTML: el.innerHTML.substring(0, 100)
        });
      }
    });
    
    return highElements.sort((a, b) => b.zIndex - a.zIndex);
  });
  
  console.log('高z-index元素 (>=50000):');
  highZIndexElements.forEach((el, index) => {
    console.log(`${index + 1}. ${el.tagName} (z-index: ${el.zIndex})`);
    console.log(`   class: ${el.className}`);
    console.log(`   位置: ${el.rect.x}, ${el.rect.y}, ${el.rect.width}x${el.rect.height}`);
    console.log(`   內容: ${el.innerHTML}...`);
  });
  
  // 測試點擊輸入框
  console.log('\n=== 測試輸入框點擊 ===');
  const emailInput = page.locator('input[type="email"]');
  const inputRect = await emailInput.boundingBox();
  
  if (inputRect) {
    const centerX = inputRect.x + inputRect.width / 2;
    const centerY = inputRect.y + inputRect.height / 2;
    
    const elementAtCenter = await page.evaluate(({x, y}) => {
      const el = document.elementFromPoint(x, y);
      return {
        tagName: el ? el.tagName : 'NULL',
        className: el ? el.className.substring(0, 50) : 'NULL',
        id: el ? el.id : 'NULL',
        src: el && el.tagName === 'IFRAME' ? el.src.substring(0, 60) : null
      };
    }, {x: centerX, y: centerY});
    
    console.log('輸入框中心點元素:', elementAtCenter);
    
    if (elementAtCenter.tagName === 'IFRAME' && elementAtCenter.src?.includes('tradingview')) {
      console.log('🚨 TradingView iframe阻擋了輸入框!');
    } else if (elementAtCenter.tagName === 'INPUT') {
      console.log('✅ 輸入框可正常點擊');
    }
  }
  
  await page.screenshot({ 
    path: 'test-results/tradingview-blocking-check.png',
    fullPage: true
  });
});