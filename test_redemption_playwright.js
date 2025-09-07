const { chromium } = require('playwright');

async function testRedemptionSystem() {
    console.log('🎭 Testing Redemption System with Playwright');
    console.log('=' + '='.repeat(49));
    
    const browser = await chromium.launch({ 
        headless: false,  // Show browser for debugging
        slowMo: 1000      // Slow down actions for visibility
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Listen for network errors
    page.on('response', response => {
        if (!response.ok()) {
            console.log(`❌ Failed request: ${response.url()} - Status: ${response.status()}`);
        }
    });
    
    // Listen for console errors
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log(`🐛 Console Error: ${msg.text()}`);
        }
    });
    
    // Listen for page errors
    page.on('pageerror', error => {
        console.log(`💥 Page Error: ${error.message}`);
    });
    
    try {
        console.log('\n1. 🌐 Loading frontend page...');
        await page.goto('http://localhost:3000', { waitUntil: 'domcontentloaded', timeout: 10000 });
        
        console.log('✅ Frontend page loaded successfully');
        
        // Take screenshot
        await page.screenshot({ path: 'frontend_loaded.png', fullPage: true });
        console.log('📸 Screenshot saved: frontend_loaded.png');
        
        console.log('\n2. 🔍 Looking for redemption code input...');
        
        // Find the redemption code input field
        const redemptionInput = await page.locator('input[placeholder*="兌換碼"]').first();
        
        if (await redemptionInput.count() > 0) {
            console.log('✅ Found redemption code input field');
            
            console.log('\n3. 🎫 Testing redemption code input...');
            // Enter a test redemption code
            await redemptionInput.fill('WEILIANG10');
            console.log('✅ Entered redemption code: WEILIANG10');
            
            // Find and click the redeem button (looking for Chinese text)
            const redeemButton = await page.locator('button:has-text("兌換"), button:has-text("Redeem")').first();
            
            if (await redeemButton.count() > 0) {
                console.log('✅ Found redeem button');
                
                console.log('\n4. 🚀 Clicking redeem button...');
                
                // Listen for network requests during redemption
                let apiCallMade = false;
                let apiResponse = null;
                
                page.on('response', async response => {
                    if (response.url().includes('/api/redemption/redeem')) {
                        apiCallMade = true;
                        apiResponse = response;
                        console.log(`📡 API Call detected: ${response.url()}`);
                        console.log(`   Status: ${response.status()}`);
                        try {
                            const responseBody = await response.text();
                            console.log(`   Response: ${responseBody}`);
                        } catch (e) {
                            console.log('   Could not read response body');
                        }
                    }
                });
                
                // Click the button
                await redeemButton.click();
                
                // Wait a bit to see what happens
                console.log('⏳ Waiting for response...');
                await page.waitForTimeout(3000);
                
                // Check for any error messages on the page
                const errorMessages = await page.locator('.error, [class*="error"], .alert, [class*="alert"]').allTextContents();
                if (errorMessages.length > 0) {
                    console.log('🚨 Error messages found on page:');
                    errorMessages.forEach(msg => console.log(`   - ${msg}`));
                }
                
                // Check for success messages
                const successMessages = await page.locator('.success, [class*="success"], .confirmation').allTextContents();
                if (successMessages.length > 0) {
                    console.log('✅ Success messages found on page:');
                    successMessages.forEach(msg => console.log(`   - ${msg}`));
                }
                
                if (!apiCallMade) {
                    console.log('❌ No API call was made - this suggests a frontend issue');
                    
                    // Check if user is logged in
                    const loginButton = await page.locator('button:has-text("Login")').count();
                    if (loginButton > 0) {
                        console.log('🔒 User appears to be not logged in');
                        console.log('   This might be why the redemption is not working');
                    }
                }
                
                // Take final screenshot
                await page.screenshot({ path: 'after_redemption_attempt.png', fullPage: true });
                console.log('📸 Screenshot saved: after_redemption_attempt.png');
                
            } else {
                console.log('❌ Could not find redeem button');
            }
        } else {
            console.log('❌ Could not find redemption code input field');
            
            // Try to find any input fields
            const allInputs = await page.locator('input').all();
            console.log(`   Found ${allInputs.length} input fields on page`);
            
            for (let i = 0; i < allInputs.length; i++) {
                const placeholder = await allInputs[i].getAttribute('placeholder');
                const type = await allInputs[i].getAttribute('type');
                console.log(`   Input ${i + 1}: type="${type}", placeholder="${placeholder}"`);
            }
        }
        
        console.log('\n5. 🔍 Analyzing page structure...');
        
        // Check current URL
        console.log(`   Current URL: ${page.url()}`);
        
        // Check if page has loaded correctly
        const title = await page.title();
        console.log(`   Page Title: ${title}`);
        
        // Check for any JavaScript errors in console
        console.log('\n6. 📋 Page Analysis Complete');
        
    } catch (error) {
        console.log(`❌ Test failed with error: ${error.message}`);
    }
    
    console.log('\n🎭 Playwright test complete');
    console.log('Check the screenshots for visual debugging');
    
    await browser.close();
}

// Run the test
testRedemptionSystem().catch(console.error);