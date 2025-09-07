const { chromium } = require('playwright');

async function testRedemptionWithToken() {
    console.log('🔑 Testing Redemption with Valid Auth Token');
    console.log('=' + '='.repeat(43));
    
    const browser = await chromium.launch({ 
        headless: false,  // Show browser for debugging
        slowMo: 1000      // Slow down actions for visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Test token from the create_test_user script
    const testToken = 'eyJ1c2VyX2lkIjogIjAyM2FmZTAxLWFlNWUtNDdjYy05ZWRkLWIwYWNmZmQyMjU4NiIsICJlbWFpbCI6ICJ0ZXN0dXNlckBleGFtcGxlLmNvbSIsICJjcmVhdGVkX2F0IjogIjIwMjUtMDktMDFUMDg6MDk6MTMuMDcwODc3In0=';
    
    // Listen for network requests
    page.on('response', response => {
        if (response.url().includes('redemption') || response.url().includes('credits')) {
            console.log(`📡 API Request: ${response.url()} - Status: ${response.status()}`);
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
        
        console.log('\n2. 🔑 Setting auth token in localStorage...');
        await page.evaluate((token) => {
            localStorage.setItem('auth_token', token);
            console.log('Auth token set in localStorage');
        }, testToken);
        console.log('✅ Auth token set successfully');
        
        console.log('\n3. 🔄 Reloading page to apply token...');
        await page.reload({ waitUntil: 'domcontentloaded' });
        console.log('✅ Page reloaded');
        
        // Wait a bit for the page to settle
        await page.waitForTimeout(2000);
        
        console.log('\n4. 🎫 Testing redemption code input...');
        
        // Find the redemption code input field
        const redemptionInput = await page.locator('input[placeholder*="兌換碼"]').first();
        
        if (await redemptionInput.count() > 0) {
            console.log('✅ Found redemption code input field');
            
            // Enter a test redemption code
            await redemptionInput.fill('WEILIANG10');
            console.log('✅ Entered redemption code: WEILIANG10');
            
            // Find and click the redeem button
            const redeemButton = await page.locator('button:has-text("兌換"), button:has-text("立即兌換"), button:has-text("Redeem")').first();
            
            if (await redeemButton.count() > 0) {
                console.log('✅ Found redeem button');
                
                console.log('\n5. 🚀 Clicking redeem button (with auth token)...');
                
                // Listen specifically for the redemption API call
                let apiCalled = false;
                let apiResponse = null;
                
                page.on('response', async response => {
                    if (response.url().includes('/api/redemption/redeem')) {
                        apiCalled = true;
                        apiResponse = response;
                        console.log(`📡 Redemption API called: ${response.status()}`);
                        try {
                            const responseText = await response.text();
                            console.log(`📄 API Response: ${responseText}`);
                        } catch (e) {
                            console.log('   Could not read response body');
                        }
                    }
                });
                
                // Click the button
                await redeemButton.click();
                
                // Wait for API response
                console.log('⏳ Waiting for API response...');
                await page.waitForTimeout(5000);
                
                if (apiCalled) {
                    console.log('✅ API call was made successfully!');
                    if (apiResponse && apiResponse.status() === 200) {
                        console.log('🎊 Redemption might have succeeded!');
                    } else if (apiResponse && apiResponse.status() === 403) {
                        console.log('🔒 Still getting 403 - token might not be working correctly');
                    } else {
                        console.log(`⚠️ Unexpected response status: ${apiResponse?.status()}`);
                    }
                } else {
                    console.log('❌ No API call was made - still an issue');
                }
                
                // Check for success/error messages on the page
                const messages = await page.locator('.bg-green-500, .bg-red-500, [class*="success"], [class*="error"]').allTextContents();
                if (messages.length > 0) {
                    console.log('\n📝 Page Messages:');
                    messages.forEach(msg => console.log(`   - ${msg}`));
                } else {
                    console.log('\n📝 No success/error messages found on page');
                }
                
                // Take final screenshot
                await page.screenshot({ path: 'redemption_with_token.png', fullPage: true });
                console.log('📸 Screenshot saved: redemption_with_token.png');
                
            } else {
                console.log('❌ Could not find redeem button');
            }
        } else {
            console.log('❌ Could not find redemption code input field');
        }
        
        console.log('\n6. 🔍 Checking user authentication state...');
        const tokenInStorage = await page.evaluate(() => {
            return localStorage.getItem('auth_token');
        });
        
        if (tokenInStorage) {
            console.log(`✅ Auth token present: ${tokenInStorage.substring(0, 30)}...`);
        } else {
            console.log('❌ No auth token found in localStorage');
        }
        
    } catch (error) {
        console.log(`❌ Test failed: ${error.message}`);
    }
    
    console.log('\n🔑 Token-based redemption test complete');
    console.log('\n📋 Results Summary:');
    console.log('- This test simulates a logged-in user');
    console.log('- If API call is made, the authentication is working');
    console.log('- Check the response status to see if redemption succeeds');
    
    await browser.close();
}

// Run the test
testRedemptionWithToken().catch(console.error);