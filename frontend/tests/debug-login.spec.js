const { test, expect } = require('@playwright/test');

test.describe('Login and Registration', () => {
  test('should be able to register a new user and log in', async ({ page }) => {
    await page.goto('https://auto-trade-frontend-610357573971.asia-northeast1.run.app/');

    // Open the login modal
    await page.click('button:has-text("登入")');

    // Switch to registration
    await page.click('button:has-text("註冊")');

    // Fill out the registration form
    const email = `testuser-${Date.now()}@example.com`;
    await page.fill('input[type="text"]', 'Test User');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');

    // Click the register button
    await page.click('button[type="submit"]:has-text("註冊")');

    // After registration, it should automatically log in.
    // Let's check if the user is logged in.
    await expect(page.locator('text=Test User')).toBeVisible();

    // Now, log out
    await page.click('button:has-text("登出")');

    // And log back in
    await page.click('button:has-text("登入")');
    await page.fill('input[type="email"]', email);
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]:has-text("登入")');

    // Check if logged in again
    await expect(page.locator('text=Test User')).toBeVisible();
  });

  test('should initiate Google login', async ({ page }) => {
    // Listen for the request to the backend's Google login endpoint
    const [request] = await Promise.all([
      page.waitForRequest(req => req.url().includes('/api/auth/google/login')),
      page.goto('https://auto-trade-frontend-610357573971.asia-northeast1.run.app/'),
      page.click('button:has-text("登入")'),
      page.click('button:has-text("使用 Google 登入")'),
    ]);

    // Check that the request was made to the correct URL
    expect(request.url()).toBe('https://auto-trade-ai-610357573971.asia-northeast1.run.app/api/auth/google/login');
  });
});
