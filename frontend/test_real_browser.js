const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true // 打開開發者工具
  });
  const page = await browser.newPage();
  
  // 監聽所有 console 訊息 (包括我們的調試訊息)
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('AuthButton') || text.includes('點擊') || text.includes('showModal')) {
      console.log('🎯 AuthButton 調試:', text);
    }
  });
  
  try {
    console.log('🌐 開啟瀏覽器並監聽登入按鈕...');
    await page.goto('http://localhost:3000');
    console.log('✅ 頁面已載入，請手動點擊登入按鈕');
    console.log('💡 同時觀察瀏覽器 Console 和這個終端的輸出');
    console.log('');
    console.log('📝 如果看到調試訊息，說明 React 事件正常');
    console.log('📝 如果沒看到調試訊息，說明事件沒有觸發');
    console.log('');
    
    // 等待用戶測試
    await page.waitForTimeout(30000); // 等待30秒讓用戶測試
    
  } catch (error) {
    console.error('錯誤:', error);
  }
  
  console.log('測試結束，關閉瀏覽器');
  await browser.close();
})();