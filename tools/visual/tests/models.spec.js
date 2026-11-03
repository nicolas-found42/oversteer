const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.OVERSTEER_DATA);
});

test('retained source catalog loads and renders actual sprite images', async ({ page }) => {
  const data = await page.evaluate(() => window.OVERSTEER_DATA);
  expect(data.cars).toHaveLength(904);
  expect(data.cars.every(c => c.appearance_model === c.id && c.frame_count === 13)).toBe(true);
  expect(data.cars.some(c => /REDLINE|GT_SIMULATION|MCLA_VA_/.test(c.id))).toBe(false);
  await expect(page.locator('.card')).toHaveCount(24);
  await page.waitForFunction(() => [...document.querySelectorAll('img')].every(i => i.complete && i.naturalWidth === 256));
});

test('source filters and pagination reach model names independently of physics', async ({ page }) => {
  await page.locator('#group').selectOption('Midnight Club Los Angeles');
  await expect(page.locator('#shown')).toHaveText('60 / 904 vehicles');
  await page.locator('#next').click();
  await expect(page.locator('#page')).toHaveText('2 / 3');
  await page.locator('#group').selectOption('');
  await page.locator('#search').fill('GT4_DODG0005');
  await expect(page.locator('.card')).toHaveCount(1);
  await expect(page.locator('.card h2')).toContainText(/viper/i);
  await expect(page.locator('#page')).toHaveText('1 / 1');
});

test('magnification scales image and retains inspectable physics evidence', async ({ page }) => {
  await page.locator('#search').fill('FOCUS_SVT');
  const before = await page.locator('.card img').getAttribute('width');
  await page.locator('#zoom').fill('2');
  const after = await page.locator('.card img').getAttribute('width');
  expect(Math.abs(Number(after) - Number(before) * 2)).toBeLessThanOrEqual(1);
  await page.locator('summary').click();
  await expect(page.locator('table')).toContainText('drive.gear1');
  await page.screenshot({ path: '../../artifacts/carmodels-research/sprites/browser-inspector.png', fullPage: true });
});
