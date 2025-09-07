const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // 監聽所有錯誤
  page.on('pageerror', error => {
    console.log('🚨 Page Error:', error.message);
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🚨 Console Error:', msg.text());
    } else if (msg.type() === 'log') {
      console.log('📝 Console Log:', msg.text());
    }
  });
  
  try {
    console.log('🔍 實時診斷登入按鈕問題...');
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    console.log('\n=== 步驟1：檢查頁面載入狀態 ===');
    const pageTitle = await page.title();
    console.log('頁面標題:', pageTitle);
    
    // 截圖當前頁面狀態
    await page.screenshot({ path: 'current_page_state.png', fullPage: true });
    console.log('📸 已保存頁面截圖: current_page_state.png');
    
    console.log('\n=== 步驟2：尋找登入按鈕 ===');
    
    // 列出所有可能的登入相關按鈕
    const allButtons = await page.locator('button').all();
    console.log(`總按鈕數: ${allButtons.length}`);
    
    for (let i = 0; i < Math.min(allButtons.length, 10); i++) {
      const btn = allButtons[i];
      const text = await btn.textContent();
      const isVisible = await btn.isVisible();
      const classes = await btn.getAttribute('class');
      
      console.log(`按鈕 ${i+1}: "${text}" - 可見: ${isVisible}`);
      if (text && (text.includes('登入') || text.includes('Login'))) {
        console.log(`  🎯 找到登入按鈕! Classes: ${classes?.substring(0, 60)}...`);
      }
    }
    
    console.log('\n=== 步驟3：測試登入按鈕點擊 ===');
    
    // 嘗試多種方式找到登入按鈕
    const selectors = [
      'button:has-text("登入")',
      'button:has-text("Login")', 
      '[class*="gradient"]:has-text("登入")',
      '[class*="gradient"]:has-text("Login")',
      'button[class*="bg-gradient-to-r from-blue-600 to-purple-600"]'
    ];
    
    let loginButton = null;
    let usedSelector = '';
    
    for (const selector of selectors) {
      try {
        const buttons = await page.locator(selector).all();
        if (buttons.length > 0 && await buttons[0].isVisible()) {
          loginButton = buttons[0];
          usedSelector = selector;
          console.log(`✅ 使用選擇器找到登入按鈕: ${selector}`);
          break;
        }
      } catch (e) {
        // 繼續嘗試下一個選擇器
      }
    }
    
    if (!loginButton) {
      console.log('❌ 無法找到登入按鈕!');
      return;
    }
    
    // 檢查按鈕詳細狀態
    const buttonText = await loginButton.textContent();
    const buttonBox = await loginButton.boundingBox();
    const isEnabled = await loginButton.isEnabled();
    
    console.log('按鈕文字:', buttonText);
    console.log('按鈕位置:', buttonBox);
    console.log('按鈕啟用:', isEnabled);
    
    // 檢查是否有元素遮擋
    if (buttonBox) {
      const centerX = buttonBox.x + buttonBox.width / 2;
      const centerY = buttonBox.y + buttonBox.height / 2;
      
      const topElement = await page.evaluate(({ x, y }) => {
        const el = document.elementFromPoint(x, y);
        return {
          tagName: el?.tagName,
          className: el?.className,
          textContent: el?.textContent?.substring(0, 20)
        };
      }, { x: centerX, y: centerY });
      
      console.log(`按鈕中心點元素:`, topElement);
      
      if (topElement.textContent !== buttonText) {
        console.log('⚠️ 按鈕可能被其他元素遮擋！');
      }
    }
    
    console.log('\n=== 步驟4：執行點擊測試 ===');
    
    // 滾動到按鈕位置
    await loginButton.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    
    console.log('⏰ 點擊前等待...');
    await page.waitForTimeout(1000);
    
    let modalFound = false;
    
    // 點擊按鈕
    console.log('🖱️ 執行點擊...');
    try {
      await loginButton.click();
      console.log('✅ 點擊執行完成');
      
      // 等待模態框出現
      await page.waitForTimeout(2000);
      
      // 檢查模態框
      const modalSelectors = [
        '.fixed.inset-0.bg-black',
        '[class*="fixed"][class*="inset-0"]',
        '[class*="modal"]',
        'div:has(input[type="email"])'
      ];
      
      for (const selector of modalSelectors) {
        try {
          const modal = page.locator(selector).first();
          const isVisible = await modal.isVisible();
          if (isVisible) {
            console.log(`✅ 找到模態框 (${selector})`);
            modalFound = true;
            
            // 檢查模態框內容
            const hasEmail = await modal.locator('input[type="email"]').count() > 0;
            const hasPassword = await modal.locator('input[type="password"]').count() > 0;
            
            console.log('  - Email 輸入框:', hasEmail ? '✅' : '❌');
            console.log('  - 密碼輸入框:', hasPassword ? '✅' : '❌');
            
            break;
          }
        } catch (e) {
          // 繼續檢查下一個選擇器
        }
      }
      
    } catch (clickError) {
      console.log('❌ 點擊失敗:', clickError.message);
    }
    
    if (!modalFound) {
      console.log('❌ 模態框未出現！');
      
      // 檢查是否有 React 錯誤
      const reactErrors = await page.evaluate(() => {
        const errors = [];
        if (window.console && window.console.error) {
          // 檢查是否有未處理的錯誤
        }
        return window.location.href;
      });
      
      console.log('當前頁面 URL:', reactErrors);
      
      // 再次截圖
      await page.screenshot({ path: 'after_click_state.png', fullPage: true });
      console.log('📸 點擊後頁面截圖: after_click_state.png');
    } else {
      console.log('🎉 登入模態框正常出現！');
    }
    
    await page.waitForTimeout(5000);
    
  } catch (error) {
    console.error('🚨 測試執行錯誤:', error);
  } finally {
    await browser.close();
  }
})();