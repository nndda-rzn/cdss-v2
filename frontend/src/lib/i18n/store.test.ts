import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { useI18nStore } from "./store";

describe("i18n store", () => {
  beforeEach(() => {
    window.localStorage.clear();
    // Reset store to default for isolation between tests.
    useI18nStore.setState({ lang: "id" });
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it("defaults to Indonesian", () => {
    expect(useI18nStore.getState().lang).toBe("id");
  });

  it("translates with t() based on current lang", () => {
    const { t } = useI18nStore.getState();
    expect(t("Pasien", "Patients")).toBe("Pasien");
    useI18nStore.getState().setLang("en");
    expect(useI18nStore.getState().t("Pasien", "Patients")).toBe("Patients");
  });

  it("toggle flips the language", () => {
    useI18nStore.getState().toggle();
    expect(useI18nStore.getState().lang).toBe("en");
    useI18nStore.getState().toggle();
    expect(useI18nStore.getState().lang).toBe("id");
  });

  it("persists the choice to localStorage", () => {
    useI18nStore.getState().setLang("en");
    expect(window.localStorage.getItem("ekg.lang")).toBe("en");
  });
});
