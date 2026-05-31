import { test, expect, login, SEED } from "../fixtures/seed";

// Opening a patient detail reveals plaintext identity (clinician role) and the
// backend records PHIAccessLog rows. The DB assertion is left as a TODO for the
// environment that wires a query helper.
test.fixme("PHI reveal: detail shows plaintext for clinician", async ({ page }) => {
  await login(page, SEED.clinician);

  await page.goto("/patients/new");
  await page.getByLabel(/nama lengkap/i).fill("Budi Santoso");
  await page.getByLabel(/tanggal lahir/i).fill("1965-03-12");
  await page.getByLabel(/telepon/i).fill("0812345678");
  await page.getByLabel(/pasien menyetujui penggunaan data/i).check();
  await page.getByRole("button", { name: /daftar/i }).click();

  // Detail view shows plaintext (not masked) for a treatment role
  await expect(page.getByText("Budi Santoso")).toBeVisible();
  await expect(page.getByText("0812345678")).toBeVisible();

  // TODO: assert 3 PHIAccessLog rows (name/phone/address) via a DB query helper
  // once the e2e environment exposes one.
});
