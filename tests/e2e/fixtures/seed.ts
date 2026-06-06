import { test as base, type Page } from "@playwright/test";

/**
 * Shared e2e helpers. Provisioning a seeded facility + users is expected to run
 * via the backend seed scripts (scripts/seed_facility.py, seed_admin.py) before
 * these specs execute. See playwright.config.ts.
 */

export const SEED = {
  clinical: { email: "clinician@demo.id", password: "StrongPass1" },
  admin: { email: "admin@demo.id", password: "StrongPass1" },
};

export async function login(
  page: Page,
  creds: { email: string; password: string },
): Promise<void> {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(creds.email);
  await page.getByLabel(/password/i).fill(creds.password);
  await page.getByRole("button", { name: /masuk/i }).click();
  await page.waitForURL("**/dashboard");
}

export const test = base;
export { expect } from "@playwright/test";
