import { expect, test } from '@playwright/test';
import process from 'node:process';

const ownerEmail = process.env.PLAYWRIGHT_OWNER_EMAIL;
const ownerPassword = process.env.PLAYWRIGHT_OWNER_PASSWORD;

async function signInAsOwner(page) {
  await page.goto('/login');
  await page.getByLabel('Email address').fill(ownerEmail);
  await page.getByLabel('Password').fill(ownerPassword);
  await page.getByRole('button', { name: /sign in/i }).click();
  await expect(page).toHaveURL(/\/owner\/?$/);
}

test('owner dashboard reports a temporary API outage and recovers on reload', async ({
  page,
}) => {
  test.skip(
    !ownerEmail || !ownerPassword,
    'Set PLAYWRIGHT_OWNER_EMAIL and PLAYWRIGHT_OWNER_PASSWORD to run this test.',
  );

  let listingRequests = 0;
  let failedListingRequests = 0;
  await page.route('**/api/PropertyListings/owner', async (route) => {
    listingRequests += 1;

    if (failedListingRequests === 0) {
      failedListingRequests += 1;
      await route.fulfill({
        status: 503,
        contentType: 'text/plain',
        body: 'Service temporarily unavailable.',
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    });
  });

  await signInAsOwner(page);
  await expect(page.locator('.dashboard-error')).toHaveText(
    'Service temporarily unavailable.',
  );
  await expect(
    page.getByRole('heading', { name: 'Property overview' }),
  ).toBeVisible();

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('.dashboard-error')).toHaveCount(0);
  await expect(page.getByText('Total listings')).toBeVisible();
  await expect(page.getByText('Your property portfolio starts here.')).toBeVisible();
  expect(failedListingRequests).toBe(1);
  expect(listingRequests).toBeGreaterThanOrEqual(2);
});

test('maintenance dashboard reports an API outage and recovers on reload', async ({
  page,
}) => {
  let maintenanceRequests = 0;
  let failedMaintenanceRequests = 0;
  await page.route('**/api/maintenance', async (route) => {
    maintenanceRequests += 1;

    if (failedMaintenanceRequests === 0) {
      failedMaintenanceRequests += 1;
      await route.fulfill({
        status: 503,
        contentType: 'text/plain',
        body: 'Service temporarily unavailable.',
      });
      return;
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    });
  });
  await page.route('**/api/technician', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  );
  await page.route('**/api/PropertyListings', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: '[]',
    }),
  );

  await page.goto('/maintenance');
  await expect(page.locator('.alert.error')).toContainText(
    'Service temporarily unavailable.',
  );
  await expect(
    page.getByRole('heading', { name: 'Maintenance overview' }),
  ).toBeVisible();

  await page.reload({ waitUntil: 'domcontentloaded' });
  await expect(page.locator('.alert.error')).toHaveCount(0);
  await expect(
    page.getByRole('heading', { name: 'Maintenance overview' }),
  ).toBeVisible();
  await page.getByRole('button', { name: /Maintenance Requests/ }).click();
  await expect(
    page.getByText('No maintenance requests match this view.'),
  ).toBeVisible();
  expect(failedMaintenanceRequests).toBe(1);
  expect(maintenanceRequests).toBeGreaterThanOrEqual(2);
});
