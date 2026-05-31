import { test, expect, login, SEED } from "../fixtures/seed";

// Registering a patient with the same name+dob+gender surfaces a duplicate
// suggestion dialog; confirming "new" creates a second record.
test.fixme("dedup: similar patient shows suggestion, confirm-new creates", async ({
  page,
}) => {
  await login(page, SEED.clinician);

  async function register() {
    await page.goto("/patients/new");
    await page.getByLabel(/nama lengkap/i).fill("Siti Aminah");
    await page.getByLabel(/tanggal lahir/i).fill("1980-05-01");
    await page.getByLabel(/jenis kelamin/i).click();
    await page.getByRole("option", { name: /perempuan/i }).click();
    await page.getByLabel(/pasien menyetujui penggunaan data/i).check();
    await page.getByRole("button", { name: /daftar/i }).click();
  }

  // First registration succeeds
  await register();
  await expect(page.getByText(/detail pasien/i)).toBeVisible();

  // Second identical registration surfaces the dedup dialog
  await register();
  await expect(page.getByText(/pasien serupa ditemukan/i)).toBeVisible();

  // Confirm as a new patient
  await page
    .getByRole("button", { name: /daftarkan sebagai pasien baru/i })
    .click();
  await expect(page.getByText(/detail pasien/i)).toBeVisible();
});
