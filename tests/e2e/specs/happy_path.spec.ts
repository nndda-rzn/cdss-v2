import { test, expect, login, SEED } from "../fixtures/seed";

// Full clinical-context flow: login -> register patient -> create encounter
// -> capture clinical context + vitals -> close encounter.
// Marked fixme until the e2e environment provisions seeded data.
test.fixme("happy path: register -> encounter -> context -> vitals -> close", async ({
  page,
}) => {
  await login(page, SEED.clinician);

  // Register a patient
  await page.goto("/patients/new");
  await page.getByLabel(/nama lengkap/i).fill("Budi Santoso");
  await page.getByLabel(/tanggal lahir/i).fill("1965-03-12");
  await page.getByLabel(/pasien menyetujui penggunaan data/i).check();
  await page.getByRole("button", { name: /daftar/i }).click();

  // Land on patient detail
  await expect(page.getByText(/detail pasien/i)).toBeVisible();

  // Create an encounter
  await page.getByRole("link", { name: /kunjungan baru/i }).click();
  await page.getByLabel(/keluhan utama/i).fill("Nyeri dada 2 jam");
  await page.getByRole("button", { name: /buat kunjungan/i }).click();

  // Capture clinical context
  await page.getByLabel(/nyeri dada/i).check();
  await page.getByRole("button", { name: /simpan konteks/i }).click();

  // Capture vital signs
  await page.getByLabel(/sistolik/i).fill("140");
  await page.getByLabel(/diastolik/i).fill("90");
  await page.getByLabel(/nadi/i).fill("110");
  await page.getByRole("button", { name: /tambah pengukuran/i }).click();

  // Close the encounter
  await page.getByRole("button", { name: /tutup kunjungan/i }).click();
  await expect(page.getByText(/tertutup/i)).toBeVisible();
});
