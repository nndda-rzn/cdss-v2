# SaaS Register Form Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement task-by-task.

**Goal:** Restructure the patient register form (`/patients/new`) into a Card + 2-column grid layout that matches the rest of the SaaS-polished surfaces, with bilingual labels and a clean footer-aligned action row.

**Architecture:** Single component edit (`RegisterForm.tsx`). Wrap the existing `<form>` in a Card; rearrange the existing `FormField` blocks into a `grid grid-cols-1 sm:grid-cols-2` layout with section labels, a Separator, and a flex-end action row. Replace the raw `<input type="checkbox">` with the shadcn `<Checkbox>` primitive. The tests, schema, mutation logic, and DedupDialog integration stay untouched.

**Tech Stack:** React, react-hook-form, Tailwind, shadcn/ui (Card, Checkbox, Separator, Button), Zustand i18n store.

---

## Task 1: Refactor RegisterForm.tsx

**Files:**
- Modify: `frontend/src/features/patient/components/RegisterForm.tsx`

- [ ] **Step 1: Read existing file**

Inspect `RegisterForm.tsx` to confirm props, mutation logic, and DedupDialog wiring.

- [ ] **Step 2: Add new imports**

```ts
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { useI18nStore } from "@/lib/i18n/store";
import { ArrowLeft } from "lucide-react";
```

- [ ] **Step 3: Add the i18n hook + Cancel handler inside `RegisterForm`**

```ts
const t = useI18nStore((s) => s.t);
```

- [ ] **Step 4: Replace the JSX returned from `RegisterForm`**

```tsx
return (
  <div className="flex justify-center pb-8">
    <Card className="w-full max-w-3xl">
      <CardHeader className="space-y-1">
        <CardTitle className="text-2xl">{t("Pasien Baru", "New Patient")}</CardTitle>
        <p className="text-sm text-muted-foreground">
          {t(
            "Daftarkan pasien baru ke fasilitas Anda.",
            "Register a new patient to your facility.",
          )}
        </p>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((v) => submit(v))} className="space-y-6">
            <section className="space-y-3">
              <h2 className="section-label">{t("Identitas Pasien", "Patient Identity")}</h2>
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("Nama Lengkap", "Full Name")}</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="dob"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("Tanggal Lahir", "Date of Birth")}</FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="gender"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("Jenis Kelamin", "Gender")}</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="male">{t("Laki-laki", "Male")}</SelectItem>
                          <SelectItem value="female">{t("Perempuan", "Female")}</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
              <FormField
                control={form.control}
                name="nik"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("NIK (opsional)", "NIK (optional)")}</FormLabel>
                    <FormControl>
                      <Input inputMode="numeric" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </section>

            <Separator />

            <section className="space-y-3">
              <h2 className="section-label">{t("Kontak Opsional", "Optional Contact")}</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("Telepon", "Phone")}</FormLabel>
                      <FormControl>
                        <Input inputMode="tel" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="address"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("Alamat", "Address")}</FormLabel>
                      <FormControl>
                        <Input {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </section>

            <Separator />

            <FormField
              control={form.control}
              name="consent_data_use"
              render={({ field }) => (
                <FormItem>
                  <label className="flex items-start gap-2 text-sm">
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={(v) => field.onChange(v === true)}
                      className="mt-0.5"
                    />
                    <span>
                      {t(
                        "Pasien menyetujui penggunaan data untuk pelayanan",
                        "Patient consents to data use for clinical services",
                      )}
                    </span>
                  </label>
                  <FormMessage />
                </FormItem>
              )}
            />

            {serverError && (
              <p role="alert" className="text-sm text-destructive">
                {serverError}
              </p>
            )}

            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate(-1)}
                className="cursor-pointer"
              >
                <ArrowLeft className="mr-1.5 h-4 w-4" aria-hidden="true" />
                {t("Batal", "Cancel")}
              </Button>
              <Button
                type="submit"
                disabled={form.formState.isSubmitting}
                className="cursor-pointer"
              >
                {t("Daftar", "Register")}
              </Button>
            </div>
          </form>
        </Form>

        <DedupDialog
          duplicates={duplicates}
          onClose={() => setDuplicates(null)}
          onConfirmNew={() => {
            setDuplicates(null);
            void submit(form.getValues(), true);
          }}
        />
      </CardContent>
    </Card>
  </div>
);
```

- [ ] **Step 5: Remove the now-unused `<h1>` heading and `max-w-lg` wrapper from the old return.**

The replacement above already drops them.

---

## Task 2: Verify

- [ ] **Step 1: Format**

```bash
npx prettier --write src/features/patient/components/RegisterForm.tsx
```

- [ ] **Step 2: Typecheck + lint + test + build**

```bash
npm run typecheck
npm run lint
npm run test -- --run src/features/patient
npm run build
```

Expected: typecheck silent, lint 0 errors, all 4 RegisterForm tests pass, build OK.

- [ ] **Step 3: File-size guard**

```bash
backend/.venv/Scripts/python.exe scripts/check_file_size.py
```

Expected: EXIT 0. If RegisterForm crosses ~200 code lines, split into `IdentitySection.tsx` + `ContactSection.tsx` (deferred to follow-up if needed).

---

## Task 3: Commit + push + PR

- [ ] **Step 1: Stage + commit**

```bash
git add docs/superpowers/specs/2026-06-01-saas-register-form-design.md \
        docs/superpowers/plans/2026-06-01-saas-register-form.md \
        frontend/src/features/patient/components/RegisterForm.tsx
git commit -m "feat(patient): saas-style card + grid register form" \
  -m "Wrap the form in a Card (max-w-3xl, shadow-elev-sm). Group fields:" \
  -m "Nama (full), DOB+Gender (grid), NIK (full) under Identitas Pasien;" \
  -m "Phone+Address (grid) under Kontak Opsional. Footer action row aligns" \
  -m "Batal + Daftar to the right at sm+. Native checkbox replaced with" \
  -m "shadcn Checkbox. All copy bilingual via useI18nStore."
```

- [ ] **Step 2: Push + open PR**

```bash
git push -u origin feat/saas-register-form
gh pr create --base main --head feat/saas-register-form \
  --title "feat(patient): saas-style card + grid register form" \
  --body "..."
```

---

## Acceptance Criteria

Mirrors the spec — see `2026-06-01-saas-register-form-design.md`.
