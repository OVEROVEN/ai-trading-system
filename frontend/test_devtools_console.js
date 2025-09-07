const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // 收集所有 console 訊息
  const consoleMessages = [];
  const errors = [];
  
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    
    consoleMessages.push({ type, text, timestamp: new Date().toLocaleTimeString() });
    
    // 實時顯示重要訊息
    if (text.includes('AuthButton') || text.includes('點擊') || text.includes('showModal')) {
      console.log(`[${type.toUpperCase()}] ${text}`);
    } else if (type === 'error') {
      console.log(`❌ [ERROR] ${text}`);
      errors.push(text);
    }
  });
  
  page.on('pageerror', error => {
    console.log(`🚨 PAGE ERROR: ${error.message}`);
    errors.push(error.message);
  });
  
  try {
    console.log('🔍 開啟開發者工具並測試登入按鈕...');
    
    // 開啟頁面
    await page.goto('http://localhost:3000');
    await page.waitForTimeout(3000);
    
    console.log('\n=== 頁面載入完成，檢查初始狀態 ===');
    console.log(`總 console 訊息數: ${consoleMessages.length}`);
    console.log(`錯誤數: ${errors.length}`);
    
    // 顯示最近的 console 訊息
    console.log('\n最近的 Console 訊息:');
    consoleMessages.slice(-5).forEach(msg => {
      console.log(`  [${msg.type}] ${msg.timestamp}: ${msg.text.substring(0, 80)}...`);
    });
    
    console.log('\n=== 查找並點擊登入按鈕 ===');
    
    // 找到登入按鈕
    const loginButton = page.locator('button:has-text("登入")').first();
    const buttonExists = await loginButton.isVisible();
    console.log(`登入按鈕存在: ${buttonExists}`);
    
    if (!buttonExists) {
      console.log('❌ 登入按鈕不存在，終止測試');
      return;
    }
    
    // 檢查按鈕屬性
    const buttonText = await loginButton.textContent();
    const buttonClasses = await loginButton.getAttribute('class');
    const buttonStyle = await loginButton.getAttribute('style');
    
    console.log(`按鈕文字: "${buttonText}"`);
    console.log(`按鈕樣式: ${buttonClasses?.substring(0, 60)}...`);
    console.log(`內聯樣式: ${buttonStyle || '無'}`);
    
    // 記錄點擊前的 console 訊息數量
    const messagesBeforeClick = consoleMessages.length;
    
    console.log('\n⏰ 準備點擊按鈕...');
    await page.waitForTimeout(1000);
    
    // 點擊按鈕
    console.log('🖱️ 執行點擊...');
    await loginButton.click();
    
    // 等待反應
    await page.waitForTimeout(2000);
    
    console.log('\n=== 點擊後檢查 ===');
    const messagesAfterClick = consoleMessages.length;
    const newMessages = messagesAfterClick - messagesBeforeClick;
    
    console.log(`點擊後新增 console 訊息數: ${newMessages}`);
    
    // 顯示點擊後的新訊息
    if (newMessages > 0) {
      console.log('\n點擊後的新 Console 訊息:');
      consoleMessages.slice(-newMessages).forEach((msg, index) => {
        console.log(`  ${index + 1}. [${msg.type}] ${msg.text}`);
      });
    } else {
      console.log('⚠️ 點擊後沒有新的 console 訊息！');
    }
    
    // 檢查模態框
    console.log('\n=== 檢查模態框狀態 ===');
    const modalSelectors = [
      '.fixed.inset-0.bg-black',
      '[class*="fixed"][class*="inset-0"]',
      'div:has(input[type="email"])'
    ];
    
    let modalFound = false;
    for (const selector of modalSelectors) {
      try {
        const modal = page.locator(selector).first();
        const isVisible = await modal.isVisible();
        if (isVisible) {
          console.log(`✅ 找到模態框: ${selector}`);
          modalFound = true;
          break;
        }
      } catch (e) {
        // 繼續檢查
      }
    }
    
    if (!modalFound) {
      console.log('❌ 沒有找到模態框');
    }
    
    // 檢查 React 狀態
    console.log('\n=== React 狀態檢查 ===');
    const reactState = await page.evaluate(() => {
      // 檢查 React 是否正常載入
      const hasReact = typeof window.React !== 'undefined' || document.querySelector('[data-reactroot]') !== null;
      
      // 檢查登入按鈕的 React fiber
      const loginBtn = document.querySelector('button:has-text("登入")') || 
                     Array.from(document.querySelectorAll('button')).find(btn => btn.textContent?.includes('登入'));
      
      const hasFiber = loginBtn && (loginBtn._reactInternalFiber || loginBtn._reactInternalInstance || loginBtn._reactInternals);
      
      return {
        hasReact,
        buttonElement: !!loginBtn,
        hasFiber: !!hasFiber,
        buttonText: loginBtn?.textContent
      };
    });
    
    console.log('React 狀態:', reactState);
    
    // 最終狀態報告
    console.log('\n=== 診斷結果 ===');
    if (newMessages === 0) {
      console.log('🚨 問題：點擊沒有觸發任何 console 訊息');
      console.log('可能原因：');
      console.log('  1. React 事件監聽器沒有掛載');
      console.log('  2. 按鈕被其他元素遮擋');
      console.log('  3. onClick 函數有語法錯誤');
    } else if (!modalFound) {
      console.log('🚨 問題：點擊觸發了事件但模態框沒出現');
      console.log('可能原因：');
      console.log('  1. setState 沒有正確執行');
      console.log('  2. 模態框渲染邏輯有問題');
      console.log('  3. CSS 導致模態框隱藏');
    } else {
      console.log('✅ 登入功能正常工作');
    }
    
    await page.waitForTimeout(3000);
    
  } catch (error) {
    console.error('🚨 測試錯誤:', error);
  } finally {
    await browser.close();
  }
})();