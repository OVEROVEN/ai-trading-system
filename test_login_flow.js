const { chromium } = require('playwright');

async function testLoginFlow() {
    console.log('🔐 Testing Login Flow with Playwright');
    console.log('=' + '='.repeat(39));
    
    const browser = await chromium.launch({ 
        headless: false,  // Show browser for debugging
        slowMo: 1500      // Slow down actions for visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Listen for network requests
    page.on('response', response => {
        if (response.url().includes('auth') || response.url().includes('login') || response.url().includes('google')) {
            console.log(`🔗 Auth request: ${response.url()} - Status: ${response.status()}`);
        }
    });
    
    // Listen for console errors
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log(`🐛 Console Error: ${msg.text()}`);
        }
    });
    
    try {
        console.log('\n1. 🌐 Loading frontend page...');
        await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded', timeout: 10000 });
        console.log('✅ Frontend page loaded');
        
        console.log('\n2. 🔍 Looking for login button...');
        
        // Look for login button
        const loginButtons = await page.locator('button:has-text("Login"), button:has-text("登入"), button:has-text("Sign In"), button:has-text("登錄")');
        const loginButtonCount = await loginButtons.count();
        
        console.log(`Found ${loginButtonCount} potential login buttons`);
        
        if (loginButtonCount > 0) {
            for (let i = 0; i < loginButtonCount; i++) {
                const button = loginButtons.nth(i);
                const text = await button.textContent();
                console.log(`   Button ${i + 1}: "${text}"`);
            }
            
            console.log('\n3. 🖱️ Clicking login button...');
            const firstLoginButton = loginButtons.first();
            await firstLoginButton.click();
            
            // Wait for any modal or redirect
            await page.waitForTimeout(2000);
            
            console.log('\n4. 🔍 Checking for login modal or redirect...');
            
            // Check if modal appeared
            const modals = await page.locator('[role="dialog"], .modal, [class*="modal"]').count();
            if (modals > 0) {
                console.log('✅ Login modal detected');
                
                // Look for Google login option
                const googleButtons = await page.locator('button:has-text("Google"), a:has-text("Google"), [class*="google"]').count();
                console.log(`Found ${googleButtons} Google login options`);
                
                if (googleButtons > 0) {
                    console.log('✅ Google login option available');
                } else {
                    console.log('❌ No Google login option found');
                }
            } else {
                console.log('❌ No login modal detected');
                
                // Check if redirected to auth page
                const currentUrl = page.url();
                console.log(`Current URL: ${currentUrl}`);
                
                if (currentUrl.includes('auth') || currentUrl.includes('login')) {
                    console.log('✅ Redirected to auth page');
                } else {
                    console.log('❌ No redirect detected');
                }
            }
            
            console.log('\n5. 📱 Checking localStorage for existing token...');
            const authToken = await page.evaluate(() => {
                return localStorage.getItem('auth_token');
            });
            
            if (authToken) {
                console.log(`✅ Found auth token in localStorage: ${authToken.substring(0, 20)}...`);
            } else {
                console.log('❌ No auth token found in localStorage');
            }
            
            // Take screenshot after login attempt
            await page.screenshot({ path: 'login_attempt.png', fullPage: true });
            console.log('📸 Screenshot saved: login_attempt.png');
            
        } else {
            console.log('❌ No login button found');
            
            // Check all buttons on the page
            const allButtons = await page.locator('button').all();
            console.log(`\n   Found ${allButtons.length} total buttons on page:`);
            
            for (let i = 0; i < Math.min(allButtons.length, 10); i++) {
                const text = await allButtons[i].textContent();
                console.log(`   Button ${i + 1}: "${text}"`);
            }
        }
        
        console.log('\n6. 🔍 Final authentication state check...');
        
        // Try to access redemption API to see authentication status
        const response = await page.evaluate(async () => {
            try {
                const res = await fetch('http://localhost:8000/api/redemption/credits');
                return {
                    status: res.status,
                    ok: res.ok,
                    text: await res.text()
                };
            } catch (error) {
                return {
                    error: error.message
                };
            }
        });
        
        console.log('API Test Result:', response);
        
        if (response.status === 403 || response.status === 401) {
            console.log('✅ User is not authenticated (expected behavior)');
        } else if (response.status === 200) {
            console.log('✅ User is authenticated');
        } else {
            console.log(`⚠️ Unexpected API response: ${response.status}`);
        }
        
    } catch (error) {
        console.log(`❌ Test failed: ${error.message}`);
    }
    
    console.log('\n🔐 Login flow test complete');
    console.log('\n📋 Summary:');
    console.log('- This test checks if the login button works correctly');
    console.log('- If no auth token is found, users will see "網路錯誤請重試"');
    console.log('- The solution is to implement proper Google OAuth login');
    
    await browser.close();
}

// Run the test
testLoginFlow().catch(console.error);