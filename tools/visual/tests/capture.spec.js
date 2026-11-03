const { test, expect } = require('@playwright/test');
const path = require('node:path');

test('capture source families at shared physical scale', async ({ page }) => {
  await page.setViewportSize({ width: 1600, height: 1100 });
  await page.goto('/');
  await page.waitForFunction(() => window.OVERSTEER_DATA);
  for (const source of ['Ford Racing 2', 'Gran Turismo 4', 'Midnight Club 3', 'Midnight Club Los Angeles']) {
    await page.locator('#group').selectOption(source);
    await page.waitForFunction(() => [...document.querySelectorAll('img')].every(i => i.complete && i.naturalWidth));
    await expect(page.locator('.card').first()).toBeVisible();
    await page.screenshot({ path: path.resolve(__dirname, '../../../artifacts/visual/' + source.replaceAll(' ', '-') + '.png') });
  }
});
