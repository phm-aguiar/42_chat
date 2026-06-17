/**
 * Playwright configuration for 42 Chat E2E tests.
 *
 * Run from the frontend/ directory:
 *   cd frontend && npx playwright test
 *
 * Test files live in ../test/e2e/*.spec.ts (project root).
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Test directory — points to root-level test/e2e/
  testDir: '../test/e2e',

  // Test file pattern
  testMatch: '**/*.spec.ts',

  // Global timeout per test
  timeout: 30_000,

  // Retry on CI
  retries: process.env.CI ? 1 : 0,

  // Parallel workers (1 for local, more on CI)
  workers: process.env.CI ? 2 : 1,

  // Reporter — list for CI, HTML for local
  reporter: [
    ['list'],
    ['html', { outputFolder: '../test/e2e/reports' }],
  ],

  // Global setup / teardown (optional — for seeding test data)
  // globalSetup: './test/global-setup.ts',

  use: {
    // Base URL for all page.goto() calls — set in specs explicitly
    // baseURL: 'http://localhost:5173',

    // Screenshot on failure
    screenshot: 'only-on-failure',

    // Trace for debugging failures (on-first-retry to save disk)
    trace: 'on-first-retry',

    // Video recording (off by default, enable with --video flag)
    // video: 'on-first-retry',
  },

  // Supported browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
      },
    },
  ],

  // Web server config — automatically starts frontend dev server for testing.
  // Commented out by default; run the server manually or uncomment for CI.
  //
  // webServer: {
  //   command: 'npm run dev',
  //   port: 5173,
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 30_000,
  // },
});
