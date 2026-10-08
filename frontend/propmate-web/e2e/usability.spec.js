import { expect, test } from '@playwright/test';
import process from 'node:process';

const accounts = [
  {
    role: 'Owner',
    email: process.env.PLAYWRIGHT_OWNER_EMAIL,
    password: process.env.PLAYWRIGHT_OWNER_PASSWORD,
    path: '/owner',
    heading: 'Property overview',
  },
  {
    role: 'Admin',
    email: process.env.PLAYWRIGHT_ADMIN_EMAIL,
    password: process.env.PLAYWRIGHT_ADMIN_PASSWORD,
    path: '/admin',
    heading: 'Verification queue',
  },
  {
    role: 'Property Manager',
    email: process.env.PLAYWRIGHT_MANAGER_EMAIL,
    password: process.env.PLAYWRIGHT_MANAGER_PASSWORD,
    path: '/maintenance',
    heading: 'Maintenance overview',
  },
];

for (const account of accounts) {
  test(`login routes ${account.role} to the correct workspace`, async ({
    page,
  }) => {
    test.skip(
      !account.email || !account.password,
      `Set the Playwright environment variables for the ${account.role} test account.`,
    );

    await page.goto('/login');
    await page.getByLabel('Email address').fill(account.email);
    await page.getByLabel('Password').fill(account.password);
    await page.getByRole('button', { name: /sign in/i }).click();

    await expect(page).toHaveURL(new RegExp(`${account.path}/?$`));
    await expect(
      page.getByRole('heading', { name: account.heading }),
    ).toBeVisible();
  });
}

test('empty login submission is blocked by required-field validation', async ({
  page,
}) => {
  let loginRequests = 0;
  await page.route('**/api/Auth/login', async (route) => {
    loginRequests += 1;
    await route.continue();
  });

  await page.goto('/login');
  await page.getByRole('button', { name: /sign in/i }).click();

  await expect(page.getByLabel('Email address')).toBeFocused();
  expect(loginRequests).toBe(0);
});

test('searching properties opens details and viewing slots', async ({
  page,
}) => {
  await page.goto('/discover');
  await expect(
    page.getByRole('heading', { name: 'Discover Properties' }),
  ).toBeVisible();

  await page.getByLabel('Location').fill('Galle');
  await page.getByRole('button', { name: 'Search', exact: true }).click();

  const galleProperty = page
    .getByRole('article')
    .filter({ hasText: 'Galle' });
  await expect(galleProperty).toHaveCount(1);
  await galleProperty.getByRole('button', { name: 'View Details' }).click();

  await expect(page).toHaveURL(/\/discover\/\d+$/);
  await expect(
    page.getByRole('heading', { name: 'Two Bedroom Apartment in Galle' }),
  ).toBeVisible();

  await page.getByRole('button', { name: 'View Viewing Slots' }).click();
  await expect(page).toHaveURL(/\/discover\/\d+\/viewing-slots$/);
  await expect(
    page.getByRole('heading', { name: 'Viewing Slots' }),
  ).toBeVisible();
});

test('logged-out user receives feedback when attempting to book a viewing', async ({
  page,
}) => {
  await page.goto('/discover');
  await page.getByLabel('Location').fill('Galle');
  await page.getByRole('button', { name: 'Search', exact: true }).click();

  const galleProperty = page
    .getByRole('article')
    .filter({ hasText: 'Galle' });
  await galleProperty.getByRole('button', { name: 'View Details' }).click();
  await page.getByRole('button', { name: 'View Viewing Slots' }).click();
  await page.getByRole('button', { name: 'Book Viewing' }).first().click();

  await expect(page.getByRole('alert')).toHaveText(
    'Please log in to book a viewing.',
  );
});

test('maintenance sections navigate and empty request is not submitted', async ({
  page,
}) => {
  let createRequests = 0;
  await page.route('**/api/maintenance', async (route) => {
    if (route.request().method() === 'POST') {
      createRequests += 1;
    }
    await route.continue();
  });

  await page.goto('/maintenance');
  await expect(
    page.getByRole('heading', { name: 'Maintenance overview' }),
  ).toBeVisible();

  for (const [section, heading] of [
    ['Maintenance Requests', 'Maintenance requests'],
    ['Technicians', 'Technicians'],
    ['Expenses', 'Expenses'],
    ['History', 'History'],
    ['Overview', 'Maintenance overview'],
  ]) {
    await page.getByRole('button', { name: new RegExp(section) }).click();
    await expect(page.getByRole('heading', { name: heading })).toBeVisible();
  }

  await page.getByRole('button', { name: 'New request' }).click();
  await expect(
    page.getByRole('heading', { name: 'Create maintenance request' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Create request' }).click();

  await expect(page.getByLabel('Property')).toBeFocused();
  expect(createRequests).toBe(0);
});
