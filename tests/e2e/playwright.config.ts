import { defineConfig } from "@playwright/test";

/**
 * Sprint 2A e2e config. Boots the Flask API (port 5055) and the Vite dev
 * server (port 5173); the Vite proxy forwards /api to Flask.
 *
 * Specs are currently authored as test.fixme placeholders (committed source,
 * not yet executed) per the Sprint 2A plan. Remove .fixme and provision a
 * seeded facility + users to run them.
 */
export default defineConfig({
  testDir: "./specs",
  timeout: 30_000,
  fullyParallel: false,
  use: {
    baseURL: "http://localhost:5173",
    headless: true,
    trace: "on-first-retry",
  },
  webServer: [
    {
      command:
        "python -m flask --app wsgi run --port 5055",
      cwd: "../../backend",
      port: 5055,
      reuseExistingServer: true,
      env: { FLASK_ENV: "development" },
    },
    {
      command: "npm run dev",
      cwd: "../../frontend",
      port: 5173,
      reuseExistingServer: true,
    },
  ],
});
