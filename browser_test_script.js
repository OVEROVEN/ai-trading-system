
// 在瀏覽器開發者工具 Console 中執行以下代碼

// 1. 設置 JWT Token
localStorage.setItem('auth_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDIzYWZlMDEtYWU1ZS00N2NjLTllZGQtYjBhY2ZmZDIyNTg2IiwiZW1haWwiOiJ0ZXN0dXNlckBleGFtcGxlLmNvbSIsInN1YnNjcmlwdGlvbl9zdGF0dXMiOiJmcmVlIiwiZXhwIjoxNzU2ODAwNjk2LCJpYXQiOjE3NTY3MTQyOTZ9.92Dv8HJo3j_DgD-vgXpduGQa65fNn3FJ0XGYWKWJWKA');
console.log('✅ JWT Token 已設置');

// 2. 重新載入頁面
location.reload();

// 3. 檢查認證狀態
setTimeout(() => {
    console.log('🔍 檢查認證狀態...');
    console.log('Token:', localStorage.getItem('auth_token'));
    
    // 測試 API 調用
    fetch('http://localhost:8000/api/redemption/credits', {
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('auth_token'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('📡 API 響應狀態:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 用戶配額:', data);
    })
    .catch(error => {
        console.error('❌ API 錯誤:', error);
    });
}, 2000);
