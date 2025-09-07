const { test, expect } = require('@playwright/test');

test('Test for click interception on modal', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  // 開啟模態框
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(1000);
  
  console.log('=== 測試點擊攔截問題 ===');
  
  // 獲取郵箱輸入框
  const emailInput = page.locator('input[type="email"]');
  const inputRect = await emailInput.boundingBox();
  
  if (!inputRect) {
    console.log('❌ 找不到輸入框');
    return;
  }
  
  console.log('輸入框位置:', inputRect);
  
  // 測試輸入框四個角落和中心的點擊
  const testPoints = [
    { name: '左上', x: inputRect.x + 5, y: inputRect.y + 5 },
    { name: '右上', x: inputRect.x + inputRect.width - 5, y: inputRect.y + 5 },
    { name: '中心', x: inputRect.x + inputRect.width/2, y: inputRect.y + inputRect.height/2 },
    { name: '左下', x: inputRect.x + 5, y: inputRect.y + inputRect.height - 5 },
    { name: '右下', x: inputRect.x + inputRect.width - 5, y: inputRect.y + inputRect.height - 5 }
  ];
  
  for (const point of testPoints) {
    const element = await page.evaluate(({x, y}) => {
      const el = document.elementFromPoint(x, y);
      return {
        tagName: el ? el.tagName : 'NULL',
        className: el ? el.className.substring(0, 40) : 'NULL',
        id: el ? el.id : 'NULL',
        isInput: el ? el.tagName === 'INPUT' : false,
        isClickable: el ? (el.tagName === 'INPUT' || el.tagName === 'BUTTON' || el.onclick !== null) : false
      };
    }, {x: point.x, y: point.y});
    
    console.log(`${point.name} (${Math.round(point.x)}, ${Math.round(point.y)}):`, element);
  }
  
  // 檢查是否有透明或不可見的覆蓋層
  console.log('\n=== 檢查覆蓋層 ===');
  
  const overlayElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const overlays = [];
    
    elements.forEach(el => {
      const styles = getComputedStyle(el);
      const rect = el.getBoundingClientRect();
      
      // 尋找可能覆蓋在模態框上的元素
      if (styles.position === 'fixed' || styles.position === 'absolute') {
        const zIndex = styles.zIndex === 'auto' ? 0 : parseInt(styles.zIndex);
        if (rect.width > 100 && rect.height > 100 && zIndex >= 0) {
          overlays.push({
            tagName: el.tagName,
            className: el.className.substring(0, 30),
            zIndex: zIndex,
            position: styles.position,
            pointerEvents: styles.pointerEvents,
            opacity: styles.opacity,
            visibility: styles.visibility,
            rect: {
              x: Math.round(rect.x),
              y: Math.round(rect.y), 
              width: Math.round(rect.width),
              height: Math.round(rect.height)
            }
          });
        }
      }
    });
    
    return overlays.sort((a, b) => b.zIndex - a.zIndex);
  });
  
  console.log('可能的覆蓋元素:', overlayElements);
  
  // 嘗試不同的輸入方法
  console.log('\n=== 測試不同輸入方法 ===');
  
  // 方法1: 直接click + fill
  try {
    await emailInput.click();
    await emailInput.fill('direct@test.com');
    const value1 = await emailInput.inputValue();
    console.log('方法1 (直接click):', value1 === 'direct@test.com' ? '✅ 成功' : '❌ 失敗');
  } catch (e) {
    console.log('方法1失敗:', e.message);
  }
  
  // 方法2: 使用坐標點擊
  try {
    await page.mouse.click(inputRect.x + inputRect.width/2, inputRect.y + inputRect.height/2);
    await page.keyboard.selectAll();
    await page.keyboard.type('mouse@test.com');
    const value2 = await emailInput.inputValue();
    console.log('方法2 (坐標點擊):', value2 === 'mouse@test.com' ? '✅ 成功' : '❌ 失敗');
  } catch (e) {
    console.log('方法2失敗:', e.message);
  }
  
  // 方法3: JavaScript直接操作
  try {
    await page.evaluate(() => {
      const input = document.querySelector('input[type="email"]');
      if (input) {
        input.focus();
        input.value = 'js@test.com';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    const value3 = await emailInput.inputValue();
    console.log('方法3 (JavaScript):', value3 === 'js@test.com' ? '✅ 成功' : '❌ 失敗');
  } catch (e) {
    console.log('方法3失敗:', e.message);
  }
  
  // 方法4: 強制點擊
  try {
    await emailInput.click({ force: true });
    await emailInput.fill('force@test.com');
    const value4 = await emailInput.inputValue();
    console.log('方法4 (強制點擊):', value4 === 'force@test.com' ? '✅ 成功' : '❌ 失敗');
  } catch (e) {
    console.log('方法4失敗:', e.message);
  }
  
  // 檢查最終狀態
  const finalValue = await emailInput.inputValue();
  console.log('\n最終輸入框值:', finalValue);
  
  // 檢查輸入框是否真的獲得焦點
  const hasFocus = await page.evaluate(() => {
    const input = document.querySelector('input[type="email"]');
    return document.activeElement === input;
  });
  
  console.log('輸入框是否有焦點:', hasFocus);
  
  await page.screenshot({ 
    path: 'test-results/click-intercept-final.png',
    fullPage: true
  });
});