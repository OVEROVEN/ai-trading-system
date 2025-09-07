const { chromium } = require('playwright');

async function testRedemptionWithJWT() {
    console.log('🎯 Testing Redemption with Valid JWT Token');
    console.log('=' + '='.repeat(43));
    
    const browser = await chromium.launch({ 
        headless: false,  // Show browser for debugging
        slowMo: 1000      // Slow down actions for visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Valid JWT token from create_jwt_token.py
    const jwtToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDIzYWZlMDEtYWU1ZS00N2NjLTllZGQtYjBhY2ZmZDIyNTg2IiwiZW1haWwiOiJ0ZXN0dXNlckBleGFtcGxlLmNvbSIsInN1YnNjcmlwdGlvbl9zdGF0dXMiOiJmcmVlIiwiZXhwIjoxNzU2ODAwNjk2LCJpYXQiOjE3NTY3MTQyOTZ9.92Dv8HJo3j_DgD-vgXpduGQa65fNn3FJ0XGYWKWJWKA';
    
    // Listen for network requests
    page.on('response', async response => {
        if (response.url().includes('redemption') || response.url().includes('credits')) {
            console.log(`📡 API Request: ${response.url()} - Status: ${response.status()}`);
            if (response.status() !== 200) {
                try {
                    const text = await response.text();
                    console.log(`   Error Response: ${text}`);
                } catch (e) {
                    console.log('   Could not read error response');
                }
            }
        }
    });
    
    // Listen for console messages
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log(`🐛 Console Error: ${msg.text()}`);
        } else if (msg.text().includes('Token') || msg.text().includes('API')) {
            console.log(`📝 Console Info: ${msg.text()}`);
        }
    });
    
    try {
        console.log('\n1. 🌐 Loading frontend page...');
        await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded', timeout: 10000 });
        console.log('✅ Frontend page loaded');
        
        console.log('\n2. 🔑 Setting JWT token in localStorage...');
        await page.evaluate((token) => {
            localStorage.setItem('auth_token', token);
            console.log('JWT token set in localStorage');
        }, jwtToken);
        console.log('✅ JWT token set successfully');
        
        console.log('\n3. 🔄 Reloading page to apply JWT token...');
        await page.reload({ waitUntil: 'domcontentloaded' });
        console.log('✅ Page reloaded');
        
        // Wait for page to settle and load user data
        await page.waitForTimeout(3000);
        
        console.log('\n4. ✅ Checking if user is authenticated...');
        const tokenExists = await page.evaluate(() => {
            return localStorage.getItem('auth_token') !== null;
        });
        
        if (tokenExists) {
            console.log('✅ JWT token persists after reload');
        } else {
            console.log('❌ JWT token was cleared - might be an issue');
        }
        
        console.log('\n5. 🎫 Testing redemption code input...');
        
        // Find the redemption code input field
        const redemptionInput = await page.locator('input[placeholder*="兌換碼"], input[placeholder*="redemption"]').first();
        
        if (await redemptionInput.count() > 0) {
            console.log('✅ Found redemption code input field');
            
            // Clear any existing value and enter the test code
            await redemptionInput.clear();
            await redemptionInput.fill('WEILIANG10');
            console.log('✅ Entered redemption code: WEILIANG10');
            
            // Find and click the redeem button
            const redeemButton = await page.locator('button:has-text("兌換"), button:has-text("立即兌換"), button:has-text("Redeem")').first();
            
            if (await redeemButton.count() > 0) {
                console.log('✅ Found redeem button');
                
                console.log('\n6. 🚀 Clicking redeem button with JWT authentication...');
                
                // Listen for the redemption API call
                let redemptionApiCalled = false;
                let redemptionResponse = null;
                
                page.on('response', async response => {
                    if (response.url().includes('/api/redemption/redeem')) {
                        redemptionApiCalled = true;
                        redemptionResponse = response;
                        console.log(`🎯 REDEMPTION API CALLED: Status ${response.status()}`);
                        try {
                            const responseText = await response.text();
                            console.log(`📋 Response Body: ${responseText}`);
                        } catch (e) {
                            console.log('   Could not read response body');
                        }
                    }
                });
                
                // Click the redeem button
                await redeemButton.click();
                
                // Wait for API response and page updates
                console.log('⏳ Waiting for redemption response...');
                await page.waitForTimeout(5000);
                
                if (redemptionApiCalled) {
                    console.log('🎉 SUCCESS! Redemption API was called!');
                    
                    if (redemptionResponse.status() === 200) {
                        console.log('🎊 REDEMPTION SUCCESSFUL!');
                    } else {
                        console.log(`⚠️ Redemption API returned: ${redemptionResponse.status()}`);
                    }
                } else {
                    console.log('❌ Redemption API was not called - authentication still failing');
                }
                
                // Check for success/error messages on the page
                const successMessages = await page.locator('.bg-green-500, [class*="success"]').allTextContents();
                const errorMessages = await page.locator('.bg-red-500, [class*="error"]').allTextContents();
                
                if (successMessages.length > 0) {
                    console.log('\n🎊 Success Messages Found:');
                    successMessages.forEach(msg => console.log(`   ✅ ${msg}`));
                } else if (errorMessages.length > 0) {
                    console.log('\n❌ Error Messages Found:');
                    errorMessages.forEach(msg => console.log(`   ❌ ${msg}`));
                } else {
                    console.log('\n📝 No success/error messages found on page');
                }
                
                // Take final screenshot
                await page.screenshot({ path: 'redemption_jwt_test.png', fullPage: true });
                console.log('📸 Screenshot saved: redemption_jwt_test.png');
                
            } else {
                console.log('❌ Could not find redeem button');
            }
        } else {
            console.log('❌ Could not find redemption code input field');
        }
        
        console.log('\n7. 📊 Final Authentication State Check...');
        
        // Test API directly to verify token works
        const apiTest = await page.evaluate(async (token) => {
            try {
                const response = await fetch('http://localhost:8000/api/redemption/credits', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
                
                return {
                    status: response.status,
                    ok: response.ok,
                    text: await response.text()
                };
            } catch (error) {
                return {
                    error: error.message
                };
            }
        }, jwtToken);
        
        console.log('🧪 Direct API Test Result:', apiTest);
        
        if (apiTest.status === 200) {
            console.log('✅ JWT token is valid and working!');
        } else if (apiTest.status === 401) {
            console.log('🔒 JWT token is being rejected by server');
        } else {
            console.log(`⚠️ Unexpected API response: ${apiTest.status}`);
        }
        
    } catch (error) {
        console.log(`❌ Test failed: ${error.message}`);
    }
    
    console.log('\n🎯 JWT Redemption Test Complete!');
    console.log('\n📋 Summary:');
    console.log('- Used valid JWT token generated by the system');
    console.log('- If API calls are made, authentication is working');
    console.log('- Check response status to determine redemption success');
    
    await browser.close();
}

// Run the test
testRedemptionWithJWT().catch(console.error);