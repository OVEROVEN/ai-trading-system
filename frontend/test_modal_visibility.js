const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('🔍 檢查模態框可見性問題...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    console.log('\n=== 點擊登入按鈕 ===');
    const loginButton = page.locator('button:has-text("登入")').first();
    await loginButton.click();
    await page.waitForTimeout(1000);
    
    console.log('\n=== 檢查模態框詳細狀態 ===');
    
    // 檢查模態框元素
    const modal = page.locator('.fixed.inset-0.bg-black').first();
    const modalExists = await modal.count() > 0;
    console.log(`模態框元素存在: ${modalExists}`);
    
    if (modalExists) {
      // 檢查模態框的詳細屬性
      const modalInfo = await modal.evaluate((element) => {
        const computedStyle = window.getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        
        return {
          // 位置和尺寸
          boundingBox: {
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height
          },
          // CSS 屬性
          display: computedStyle.display,
          visibility: computedStyle.visibility,
          opacity: computedStyle.opacity,
          zIndex: computedStyle.zIndex,
          position: computedStyle.position,
          top: computedStyle.top,
          left: computedStyle.left,
          right: computedStyle.right,
          bottom: computedStyle.bottom,
          // 背景
          backgroundColor: computedStyle.backgroundColor,
          // 元素狀態
          offsetParent: !!element.offsetParent,
          innerHTML: element.innerHTML.substring(0, 200) + '...'
        };
      });
      
      console.log('模態框詳細信息:');
      console.log('  位置尺寸:', modalInfo.boundingBox);
      console.log('  display:', modalInfo.display);
      console.log('  visibility:', modalInfo.visibility);
      console.log('  opacity:', modalInfo.opacity);
      console.log('  zIndex:', modalInfo.zIndex);
      console.log('  position:', modalInfo.position);
      console.log('  offsetParent:', modalInfo.offsetParent);
      console.log('  backgroundColor:', modalInfo.backgroundColor);
      
      // 檢查是否在視窗內
      const viewport = page.viewportSize();
      const isInViewport = modalInfo.boundingBox.x >= 0 && 
                          modalInfo.boundingBox.y >= 0 &&
                          modalInfo.boundingBox.x < viewport.width &&
                          modalInfo.boundingBox.y < viewport.height;
      
      console.log('  在視窗內:', isInViewport);
      console.log('  視窗尺寸:', viewport);
      
      // 檢查模態框內容
      const modalContent = page.locator('.fixed.inset-0.bg-black .bg-slate-800').first();
      const contentExists = await modalContent.count() > 0;
      console.log('  內容區域存在:', contentExists);
      
      if (contentExists) {
        const contentInfo = await modalContent.evaluate((element) => {
          const rect = element.getBoundingClientRect();
          const computedStyle = window.getComputedStyle(element);
          
          return {
            boundingBox: {
              x: rect.x,
              y: rect.y,
              width: rect.width,
              height: rect.height
            },
            display: computedStyle.display,
            opacity: computedStyle.opacity,
            zIndex: computedStyle.zIndex
          };
        });
        
        console.log('  內容區域位置:', contentInfo.boundingBox);
        console.log('  內容區域 display:', contentInfo.display);
        console.log('  內容區域 opacity:', contentInfo.opacity);
      }
      
      // 檢查是否有其他元素遮擋
      const centerX = modalInfo.boundingBox.x + modalInfo.boundingBox.width / 2;
      const centerY = modalInfo.boundingBox.y + modalInfo.boundingBox.height / 2;
      
      if (centerX > 0 && centerY > 0 && centerX < viewport.width && centerY < viewport.height) {
        const topElement = await page.evaluate(({ x, y }) => {
          const el = document.elementFromPoint(x, y);
          return {
            tagName: el?.tagName,
            className: el?.className,
            id: el?.id
          };
        }, { x: centerX, y: centerY });
        
        console.log(`  中心點 (${centerX}, ${centerY}) 的頂層元素:`, topElement);
      }
      
      // 截圖保存
      await page.screenshot({ path: 'modal_debug.png', fullPage: true });
      console.log('📸 已保存調試截圖: modal_debug.png');
      
    } else {
      console.log('❌ 模態框元素不存在');
    }
    
    await page.waitForTimeout(3000);
    
  } catch (error) {
    console.error('🚨 測試錯誤:', error);
  } finally {
    await browser.close();
  }
})();