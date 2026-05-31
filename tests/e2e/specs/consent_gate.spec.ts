import { test, expect, login, SEED } from "../fixtures/seed";

// Creating an encounter is blocked when the patient's data_use consent has been
// revoked (AC-8). The UI surfaces the CONSENT_REQUIRED error.
test.fixme("consent gate: encounter blocked after data_use revoked", async ({
  page,
}) => {
  await login(page, SEED.clinician);

  // Register (auto-captures data_use consent)
  await page.goto("/patients/new");
  await page.getByLabel(/nama lengkap/i).fill("Budi Santoso");
  await page.getByLabel(/tanggal lahir/i).fill("1965-03-12");
  await page.getByLabel(/pasien menyetujui penggunaan data/i).check();
  await page.getByRole("button", { name: /daftar/i }).click();
  await expect(page.getByText(/detail pasien/i)).toBeVisible();

  // Revoke data_use consent from the consent panel
  await page
    .getByText(/penggunaan data/i)
    .locator("..")
    .getByRole("button", { name: /cabut/i })
    .click();

  // Attempt to create an encounter -> blocked with CONSENT_REQUIRED
  await page.getByRole("link", { name: /kunjungan baru/i }).click();
  await page.getByRole("button", { name: /buat kunjungan/i }).click();
  await expect(page.getByRole("alert")).toContainText(/persetujuan/i);
});
