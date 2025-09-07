const { test, expect } = require('@playwright/test');

test('Quick modal interaction test', async ({ page }) => {
  // 訪問首頁 - 移除networkidle等待
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000); // 簡單等待載入
  
  // 點擊登入按鈕
  await page.locator('button:has-text("Login")').click();
  await page.waitForTimeout(1000);
  
  // 檢查模態框是否可見
  const modal = page.locator('.fixed.inset-0');
  const isModalVisible = await modal.isVisible();
  console.log('模態框可見:', isModalVisible);
  
  if (!isModalVisible) {
    console.log('❌ 模態框不可見，測試結束');
    return;
  }
  
  // 檢查z-index
  const modalStyles = await modal.evaluate(el => {
    const styles = getComputedStyle(el);
    return {
      zIndex: styles.zIndex,
      position: styles.position,
      display: styles.display
    };
  });
  console.log('模態框樣式:', modalStyles);
  
  // 檢查輸入框
  const emailInput = page.locator('input[type="email"]');
  const inputVisible = await emailInput.isVisible();
  console.log('輸入框可見:', inputVisible);
  
  if (inputVisible) {
    // 檢查輸入框中心點被什麼元素占據
    const inputRect = await emailInput.boundingBox();
    const centerX = inputRect.x + inputRect.width / 2;
    const centerY = inputRect.y + inputRect.height / 2;
    
    const elementAtInput = await page.evaluate(({x, y}) => {
      const el = document.elementFromPoint(x, y);
      return {
        tagName: el ? el.tagName : 'NULL',
        className: el ? el.className.substring(0, 30) : 'NULL',
        isInput: el ? el.tagName === 'INPUT' : false
      };
    }, {x: centerX, y: centerY});
    
    console.log('輸入框中心的元素:', elementAtInput);
    
    // 嘗試強制點擊並輸入
    try {
      await emailInput.click({ force: true });
      await emailInput.fill('test@example.com');
      const value = await emailInput.inputValue();
      console.log('輸入測試結果:', value === 'test@example.com' ? '✅ 成功' : '❌ 失敗');
    } catch (error) {
      console.log('❌ 輸入失敗:', error.message);
    }
  }
  
  // 檢查是否有其他元素在更高層
  const allHighZElements = await page.evaluate(() => {
    const elements = document.querySelectorAll('*');
    const highZ = [];
    elements.forEach(el => {
      const z = getComputedStyle(el).zIndex;
      if (z !== 'auto' && parseInt(z) > 1000) {
        highZ.push({
          tag: el.tagName,
          class: el.className.substring(0, 20),
          zIndex: parseInt(z)
        });
      }
    });
    return highZ.sort((a,b) => b.zIndex - a.zIndex);
  });
  
  console.log('高z-index元素:', allHighZElements);
});