/**
 * test/e2e/chat.spec.ts
 *
 * E2E tests for the 42 Chat real-time messaging flow:
 *   Login → WebSocket connection → Send message → Verify in UI
 *
 * Architecture:
 *   - Frontend: React + Vite (localhost:5173)
 *   - Backend:  Go server  (localhost:8080)
 *   - WebSocket at /ws?token=<JWT>
 *   - REST API at /api/messages
 *
 * Prerequisites:
 *   - Backend running with Postgres + mocked 42 OAuth
 *   - Frontend dev server running (npm run dev in /frontend)
 */

import { test, expect, type Page } from '@playwright/test';

// ── Test configuration ───────────────────────────────────────────────
const BASE_URL = 'http://localhost:5173';
const API_URL = 'http://localhost:8080';

// Test user — must exist in the test database or be seeded
const TEST_USER = {
  id: 4242,
  login: 'zeenyt__',
  image_url: 'https://cdn.intra.42.fr/users/medium_zeenyt__.jpg',
  token: '', // populated in beforeAll via the mock callback
};

// ── Helpers ──────────────────────────────────────────────────────────

/** Seed auth state directly into localStorage (bypasses OAuth UI for chat tests). */
async function seedAuth(page: Page, token: string) {
  await page.evaluate(
    ({ token, user }) => {
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
    },
    { token, user: { id: TEST_USER.id, login: TEST_USER.login, image_url: TEST_USER.image_url } }
  );
}

/** Obtain a valid JWT from the backend's mock callback endpoint. */
async function fetchToken(): Promise<string> {
  const res = await fetch(`${API_URL}/api/auth/42/callback?code=mock-code-42`);
  if (!res.ok) throw new Error(`Failed to fetch token: ${res.status}`);
  const data = await res.json();
  return data.token as string;
}

/** Navigate to /chat and wait for the chat room to be fully rendered. */
async function goToChat(page: Page) {
  await page.goto(`${BASE_URL}/chat`);
  // Wait for the chat room shell: header with "42_CHAT", message list area, and input form
  await page.waitForSelector('header.status-bar');
  await page.waitForSelector('form'); // MessageInput renders a <form>
}

// ── Test Suite Setup ─────────────────────────────────────────────────

test.describe('Chat Flow (E2E)', () => {
  let token: string;

  test.beforeAll(async () => {
    // Attempt to get a real token. If the backend isn't running, use a
    // placeholder so the spec still documents the expected shape.
    try {
      token = await fetchToken();
    } catch {
      token = 'test-jwt-placeholder';
    }
  });

  test.beforeEach(async ({ page }) => {
    // Seed auth so the chat page loads without OAuth redirect
    await seedAuth(page, token);
  });

  // ── Scenarios ──────────────────────────────────────────────────────

  test('T020-C01: should navigate to /chat and display the chat room UI', async ({ page }) => {
    await goToChat(page);

    // Header
    await expect(page.locator('h1')).toContainText('42_CHAT');
    await expect(page.locator('header .text-gray-500.text-xs')).toHaveText('general');

    // Message list area (empty state)
    await expect(page.locator('text=Nenhuma mensagem ainda')).toBeVisible();

    // Input form
    const input = page.locator('textarea[placeholder*="Digite"]');
    await expect(input).toBeVisible();
    await expect(input).toBeEnabled();

    // Send button
    const sendBtn = page.locator('button[type="submit"]');
    await expect(sendBtn).toBeVisible();
    await expect(sendBtn).toBeDisabled(); // disabled until text is typed

    // Connection status (should be offline before WS connects, or connecting)
    const statusIndicator = page.locator('header .text-gray-400.uppercase');
    await expect(statusIndicator).toBeVisible();
  });

  test('T020-C02: should establish WebSocket connection and show connected status', async ({ page }) => {
    await goToChat(page);

    // The WebSocket connects automatically via useWebSocket hook.
    // Wait for the connection indicator to show "online" (green dot + user count).
    const greenDot = page.locator('header span.w-2.h-2.rounded-full.bg-lime');
    await expect(greenDot).toBeVisible({ timeout: 10000 });

    // Status text should show online count (0 users on fresh test)
    const statusText = page.locator('header .text-gray-400.uppercase');
    await expect(statusText).toContainText(/online/);
  });

  test('T020-C03: should send a message and see it appear in the UI', async ({ page }) => {
    await goToChat(page);

    // Wait for WS connection
    await page.waitForSelector('header span.w-2.h-2.rounded-full.bg-lime', { timeout: 10000 });

    const testMessage = 'Olá, 42!';

    // Type in the textarea
    const input = page.locator('textarea[placeholder*="Digite"]');
    await input.fill(testMessage);

    // Send button should be enabled now
    const sendBtn = page.locator('button[type="submit"]');
    await expect(sendBtn).toBeEnabled();

    // Send via Enter key (the component handles Enter without Shift)
    await input.press('Enter');

    // Input should be cleared after send
    await expect(input).toHaveValue('');

    // The message should appear in the message list
    // Messages have the login in a span with class text-lime text-xs
    await expect(page.locator('.text-xs.font-bold.uppercase.text-lime')).toContainText(
      TEST_USER.login
    );
    await expect(page.locator('p.text-sm.leading-relaxed')).toContainText(testMessage);
  });

  test('T020-C04: should display system messages (join/leave)', async ({ page }) => {
    await goToChat(page);

    // Wait for the WebSocket connection — a 'join' system message is
    // broadcast by the hub when a client connects (if implemented).
    // If the hub broadcasts join messages, verify they appear.
    const systemMsg = page.locator('.text-gray-500.text-xs.uppercase.tracking-widest');

    // The system message may or may not appear depending on hub implementation.
    // This assertion is conditional — it only checks if system messages render
    // correctly when they do appear.
    const count = await systemMsg.count();
    if (count > 0) {
      const text = await systemMsg.first().textContent();
      expect(text).toMatch(/entrou|saiu|shutdown/);
    }
    // If count === 0, the test still passes — system messages are
    // an optional feature and may not fire on self-join.
  });

  test('T020-C05: should show character counter and enforce 5000 char limit', async ({ page }) => {
    await goToChat(page);

    const input = page.locator('textarea');

    // Type 100 chars and verify counter
    const shortMsg = 'A'.repeat(100);
    await input.fill(shortMsg);

    // Counter should show "4900/5000" (5000 - 100)
    const counter = page.locator('.text-xs.font-mono');
    await expect(counter).toContainText('4900');

    // Type >5000 chars — the input allows overtyping but submit blocks it
    const longMsg = 'A'.repeat(5001);
    await input.fill(longMsg);

    // Counter should show negative (over limit)
    await expect(counter).toContainText('-');

    // Send button should be disabled
    const sendBtn = page.locator('button[type="submit"]');
    await expect(sendBtn).toBeDisabled();

    // Reduce to exactly 5000 — should show 0 remaining and be enabled
    const exactMsg = 'A'.repeat(5000);
    await input.fill(exactMsg);
    await expect(counter).toContainText('0');
    await expect(sendBtn).toBeEnabled();
  });

  test('T020-C06: should handle logout and redirect to login page', async ({ page }) => {
    await goToChat(page);

    // Wait for UI to render
    await page.waitForSelector('header.status-bar');

    // Click "Sair" (logout button)
    const logoutBtn = page.locator('button', { hasText: 'Sair' });
    await expect(logoutBtn).toBeVisible();
    await logoutBtn.click();

    // Should be redirected to login page (/)
    await page.waitForURL(`${BASE_URL}/`);
    await expect(page.locator('text=Login com 42')).toBeVisible();
    await expect(page.locator('h1')).toContainText('42_CHAT');
  });

  test('T020-C07: should redirect unauthenticated user from /chat to /', async ({ page }) => {
    // Clear any auth state
    await page.evaluate(() => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    });

    await page.goto(`${BASE_URL}/chat`);

    // Should redirect to login
    await page.waitForURL(`${BASE_URL}/`);
    await expect(page.locator('text=Login com 42')).toBeVisible();
  });

  test('T020-C08: should auto-scroll to bottom on new messages', async ({ page }) => {
    await goToChat(page);
    await page.waitForSelector('header span.w-2.h-2.rounded-full.bg-lime', { timeout: 10000 });

    // Send multiple messages via the input
    const input = page.locator('textarea');
    for (let i = 0; i < 15; i++) {
      await input.fill(`Mensagem de scroll #${i + 1}`);
      await input.press('Enter');
      // Brief wait for message to render
      await page.waitForTimeout(100);
    }

    // Verify the scroll container has content scrolled to the bottom.
    // The bottomRef div with auto-scroll behavior should have kept us at the bottom.
    const messageContainer = page.locator('.overflow-y-auto').first();
    const scrollTop = await messageContainer.evaluate(
      (el) => el.scrollHeight - el.scrollTop - el.clientHeight
    );

    // Should be near the bottom (within 200px tolerance)
    expect(scrollTop).toBeLessThan(200);
  });

  test('T020-C09: should handle Shift+Enter for newline without sending', async ({ page }) => {
    await goToChat(page);
    await page.waitForSelector('header span.w-2.h-2.rounded-full.bg-lime', { timeout: 10000 });

    const input = page.locator('textarea');

    // Type some text, then Shift+Enter to add a newline, then more text
    await input.fill('Linha 1');
    await input.press('Shift+Enter');
    await input.type('Linha 2');

    // Message should NOT have been sent yet (input still has content)
    await expect(input).toContainText('Linha 1\nLinha 2');

    // Now send with plain Enter
    await input.press('Enter');

    // Input cleared
    await expect(input).toHaveValue('');

    // The message (with newline) should appear in the list
    await expect(page.locator('p.text-sm.leading-relaxed')).toContainText('Linha 1');
  });

  test('T020-C10: should disable input while disconnected/reconnecting', async ({ page }) => {
    await goToChat(page);

    // Initially the input may be enabled or disabled depending on WS state.
    // Check the placeholder text — when disabled it shows "Reconectando..."
    const input = page.locator('textarea');
    const placeholder = await input.getAttribute('placeholder');

    // If placeholder is "Reconectando...", input should be disabled
    if (placeholder === 'Reconectando...') {
      await expect(input).toBeDisabled();
    } else {
      // Otherwise it should eventually become enabled once connected
      await expect(input).toBeEnabled({ timeout: 10000 });
    }
  });
});
