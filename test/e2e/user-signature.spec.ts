/**
 * test/e2e/user-signature.spec.ts
 *
 * E2E tests for Feature 101: Assinatura de Participação (UserSignature).
 *
 * Cobre os 17 cenários do Gherkin em
 *   specs/features/101-assinatura-participacao/acceptance/user-signature.feature
 *
 * Estratégia:
 *   - Mock da API REST: page.route() intercepta GET /api/users/:id/stats.
 *   - Mock WebSocket: addInitScript substitui window.WebSocket; eventos são
 *     disparados via page.evaluate chamando __dispatchWSMessage().
 *   - Navega para /chat com mensagens mockadas contendo userIds alvo.
 *
 * Pré-requisitos:
 *   - Frontend dev server rodando (npm run dev em /frontend)
 *   - Playwright instalado (npx playwright install chromium)
 */

import { test, expect, type Page } from '@playwright/test';

// ── Constantes ────────────────────────────────────────────────────────
const BASE_URL = 'http://localhost:5173';

const TEST_USER = {
  id: 4242,
  login: 'zeenyt__',
  image_url: 'https://cdn.intra.42.fr/users/medium_zeenyt__.jpg',
};

// ── Helpers ───────────────────────────────────────────────────────────

/** Injeta token + user no localStorage e mock do WebSocket. */
async function seedAuth(page: Page) {
  await page.addInitScript(() => {
    // 1. Auth state
    localStorage.setItem('token', 'test-jwt-token');
    localStorage.setItem('user', JSON.stringify({
      id: 4242,
      login: 'zeenyt__',
      image_url: 'https://cdn.intra.42.fr/users/medium_zeenyt__.jpg',
    }));

    // 2. Mock do WebSocket para capturar handlers e permitir dispatch de eventos
    const mockSockets: Array<{
      url: string;
      readyState: number;
      onopen: (() => void) | null;
      onmessage: ((e: MessageEvent) => void) | null;
      onclose: ((e: CloseEvent) => void) | null;
      onerror: (() => void) | null;
      send: () => void;
      close: () => void;
    }> = [];

    (window as any).__mockSockets = mockSockets;

    // Função global para disparar mensagens WS simuladas
    (window as any).__dispatchWSMessage = (msg: object) => {
      const event = new MessageEvent('message', { data: JSON.stringify(msg) });
      mockSockets.forEach((s) => {
        if (s.onmessage) s.onmessage(event);
      });
    };

    // Substitui o construtor WebSocket
    const OrigWS = (window as any).__OrigWebSocket || WebSocket;
    (window as any).WebSocket = function (this: any, url: string) {
      const socket = {
        url,
        readyState: 0,
        onopen: null as (() => void) | null,
        onmessage: null as ((e: MessageEvent) => void) | null,
        onclose: null as ((e: CloseEvent) => void) | null,
        onerror: null as (() => void) | null,
        send: () => {},
        close: () => {
          socket.readyState = 3;
          if (socket.onclose) {
            socket.onclose(new CloseEvent('close', { code: 1000, reason: 'test' }));
          }
        },
      };
      mockSockets.push(socket);

      // Simula abertura assíncrona
      setTimeout(() => {
        socket.readyState = 1;
        if (socket.onopen) socket.onopen();
      }, 50);

      return socket;
    } as any;
  });
}

/** Payload UserStats completo conforme a interface do componente. */
function makeStats(overrides: {
  user_id: number;
  login: string;
  avatar_url?: string;
  total_messages: number;
  active_rooms: number;
  tier: 'novato' | 'iniciante' | 'participante' | 'veterano';
}) {
  return {
    user_id: overrides.user_id,
    login: overrides.login,
    avatar_url: overrides.avatar_url ?? '',
    total_messages: overrides.total_messages,
    active_rooms: overrides.active_rooms,
    tier: overrides.tier,
    member_since: '2024-01-15T00:00:00Z',
  };
}

/** Retorna um locator para o container UserSignature de um usuário pelo login. */
function signatureCard(page: Page, login: string) {
  return page.locator(`[title*="${login} —"]`).first();
}

/** Mock da API de mensagens. */
async function mockMessagesAPI(
  page: Page,
  messages: Array<{
    id: number;
    user_id: number;
    login: string;
    content: string;
    created_at: string;
  }>,
) {
  await page.route('**/api/messages**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(messages),
    });
  });
}

/** Mock genérico: mapa userId → stats. */
async function mockStatsMap(page: Page, map: Map<number, ReturnType<typeof makeStats>>) {
  await page.route('**/api/users/*/stats', async (route, request) => {
    const url = request.url();
    const match = url.match(/\/api\/users\/(\d+)\/stats/);
    if (match) {
      const uid = parseInt(match[1], 10);
      const stats = map.get(uid);
      if (stats) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(stats),
        });
        return;
      }
    }
    await route.continue();
  });
}

/**
 * Simula atualização via WebSocket:
 * 1. Atualiza o mock da API de stats
 * 2. Dispara evento user_stats_changed no WebSocket mockado
 */
async function simulateWSStatsUpdate(
  page: Page,
  userId: number,
  newStats: ReturnType<typeof makeStats>,
) {
  // Atualiza o mock da API
  await page.unroute('**/api/users/*/stats');
  const map = new Map<number, ReturnType<typeof makeStats>>();
  map.set(userId, newStats);
  await mockStatsMap(page, map);

  // Dispara evento via WebSocket mockado
  await page.evaluate((uid) => {
    const dispatch = (window as any).__dispatchWSMessage;
    if (dispatch) {
      dispatch({
        type: 'user_stats_changed',
        user_id: uid,
        total_messages: undefined,
        active_rooms: undefined,
        tier: undefined,
      });
    }
  }, userId);

  // Aguarda o re-fetch da API (o componente incrementa refreshKey e refetch)
  await page.waitForTimeout(500);
}

/** Navega para /chat e espera o header carregar. */
async function goToChat(page: Page) {
  await page.goto(`${BASE_URL}/chat`);
  await page.waitForSelector('header.status-bar', { timeout: 10000 });
}

// ═══════════════════════════════════════════════════════════════════════
// SUÍTES DE TESTE
// ═══════════════════════════════════════════════════════════════════════

test.describe('Feature 101 — Assinatura de Participação (UserSignature)', () => {

  test.beforeEach(async ({ page }) => {
    await seedAuth(page);
  });

  // ──────────────────────────────────────────────────────────────────
  // HAPPY PATH
  // ──────────────────────────────────────────────────────────────────

  test.describe('Happy Path', () => {

    test('T101-H01: deve exibir assinatura completa abaixo de cada mensagem', async ({ page }) => {
      const statsMaria = makeStats({
        user_id: 1001, login: 'maria_dev',
        total_messages: 42, active_rooms: 3, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 1001, login: 'maria_dev', content: 'Olá, mundo!', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(1001, statsMaria);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, 'maria_dev');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
      await expect(card.locator('text=42 mensagens')).toBeVisible();
      await expect(card.locator('text=3 salas ativas')).toBeVisible();
    });

    test('T101-H02: assinatura não deve quebrar o layout do chat', async ({ page }) => {
      // Mock: 30 mensagens de usuários variados (suficiente para overflow em viewport 1280x720)
      const messages = Array.from({ length: 30 }, (_, i) => ({
        id: i + 1,
        user_id: 2000 + (i % 5),
        login: `user_${i % 5}`,
        content: `Mensagem de teste número ${i + 1} com texto adicional para aumentar altura.`.repeat(3),
        created_at: new Date(Date.now() + i * 60000).toISOString(),
      }));

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      for (let u = 0; u < 5; u++) {
        statsMap.set(2000 + u, makeStats({
          user_id: 2000 + u, login: `user_${u}`,
          total_messages: 10 + u * 5, active_rooms: 2, tier: 'iniciante',
        }));
      }

      await mockMessagesAPI(page, messages);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      // Aguarda pelo menos uma assinatura (usa .first() para evitar strict mode)
      await expect(signatureCard(page, 'user_0')).toBeVisible({ timeout: 5000 });
      // Verifica que não há overflow horizontal no container de mensagens
      const msgContainer = page.locator('.overflow-y-auto').first();
      await expect(msgContainer).toBeVisible();

      const hasHorizontalScroll = await msgContainer.evaluate(
        (el) => el.scrollWidth > el.clientWidth + 5,
      );
      expect(hasHorizontalScroll).toBe(false);

      // Verifica que o container tem overflow-y configurado (rolagem vertical possível)
      const overflowY = await msgContainer.evaluate(
        (el) => window.getComputedStyle(el).overflowY,
      );
      expect(overflowY).toBe('auto');

      // Verifica que há conteúdo renderizado (scrollHeight > 0)
      const hasContent = await msgContainer.evaluate((el) => el.scrollHeight > 0);
      expect(hasContent).toBe(true);
    });

    test('T101-H03: usuário logado vê a própria assinatura sem distinção visual', async ({ page }) => {
      const statsSelf = makeStats({
        user_id: TEST_USER.id, login: TEST_USER.login,
        total_messages: 15, active_rooms: 2, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: TEST_USER.id, login: TEST_USER.login, content: 'Minha mensagem', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(TEST_USER.id, statsSelf);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, TEST_USER.login);
      await expect(card).toBeVisible({ timeout: 5000 });

      const hasSelfClass = await card.evaluate((el) =>
        el.classList.contains('self') || el.classList.contains('you') || el.classList.contains('own'),
      );
      expect(hasSelfClass).toBe(false);
    });

    test('T101-H04: canal sem mensagens não renderiza assinatura', async ({ page }) => {
      await mockMessagesAPI(page, []);
      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      await expect(page.locator('text=Nenhuma mensagem ainda')).toBeVisible({ timeout: 5000 });
      const signatureEls = page.locator('[title*="—"]');
      await expect(signatureEls).toHaveCount(0);
    });
  });

  // ──────────────────────────────────────────────────────────────────
  // TIERS DE PARTICIPAÇÃO
  // ──────────────────────────────────────────────────────────────────

  test.describe('Tiers de Participação', () => {

    test('T101-T01: novato (0 mensagens) exibe placeholder reduzido', async ({ page }) => {
      const stats = makeStats({
        user_id: 3001, login: 'novato_42', avatar_url: '',
        total_messages: 0, active_rooms: 0, tier: 'novato',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3001, login: 'novato_42', content: 'msg', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3001, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'novato_42');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🌱 Novato')).toBeVisible();
      await expect(card).not.toHaveClass(/items-start/);
    });

    test('T101-T02: iniciante — 1 mensagem', async ({ page }) => {
      const stats = makeStats({
        user_id: 3002, login: 'joao_dev',
        total_messages: 1, active_rooms: 1, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3002, login: 'joao_dev', content: 'teste', created_at: '2025-01-01T10:00:00Z' },
      ]);
      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3002, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'joao_dev');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
      await expect(card.locator('text=1 mensagem')).toBeVisible();
    });

    test('T101-T03: iniciante — 50 mensagens (limite superior)', async ({ page }) => {
      const stats = makeStats({
        user_id: 3003, login: 'joao_dev_50',
        total_messages: 50, active_rooms: 4, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3003, login: 'joao_dev_50', content: 'limite', created_at: '2025-01-01T10:00:00Z' },
      ]);
      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3003, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'joao_dev_50');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
      await expect(card.locator('text=50 mensagens')).toBeVisible();
    });

    test('T101-T04: participante — 51 mensagens (limite inferior)', async ({ page }) => {
      const stats = makeStats({
        user_id: 3004, login: 'ana_silva',
        total_messages: 51, active_rooms: 3, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3004, login: 'ana_silva', content: 'msg', created_at: '2025-01-01T10:00:00Z' },
      ]);
      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3004, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'ana_silva');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible();
      await expect(card.locator('text=51 mensagens')).toBeVisible();
    });

    test('T101-T05: participante — 200 mensagens (limite superior)', async ({ page }) => {
      const stats = makeStats({
        user_id: 3005, login: 'ana_silva_200',
        total_messages: 200, active_rooms: 5, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3005, login: 'ana_silva_200', content: 'limite', created_at: '2025-01-01T10:00:00Z' },
      ]);
      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3005, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'ana_silva_200');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible();
      await expect(card.locator('text=200 mensagens')).toBeVisible();
    });

    test('T101-T06: veterano — 201+ mensagens', async ({ page }) => {
      const stats = makeStats({
        user_id: 3006, login: 'pedro_lider',
        total_messages: 201, active_rooms: 8, tier: 'veterano',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: 3006, login: 'pedro_lider', content: 'veterano', created_at: '2025-01-01T10:00:00Z' },
      ]);
      const map = new Map<number, ReturnType<typeof makeStats>>();
      map.set(3006, stats);
      await mockStatsMap(page, map);
      await goToChat(page);

      const card = signatureCard(page, 'pedro_lider');
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=👑 VETERANO')).toBeVisible();
      await expect(card.locator('text=201 mensagens')).toBeVisible();
    });
  });

  // ──────────────────────────────────────────────────────────────────
  // TRANSIÇÃO DE TIER
  // ──────────────────────────────────────────────────────────────────

  test.describe('Transição de Tier', () => {

    test('T101-TR01: transição iniciante → participante ao atingir 51 msgs', async ({ page }) => {
      const userId = 4001;
      const login = 'carlos_souza';

      const statsInicial = makeStats({
        user_id: userId, login, total_messages: 50, active_rooms: 2, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg 50', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, statsInicial);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
      await expect(card.locator('text=50 mensagens')).toBeVisible();

      // Transição
      const statsNovo = makeStats({
        user_id: userId, login, total_messages: 51, active_rooms: 2, tier: 'participante',
      });
      await simulateWSStatsUpdate(page, userId, statsNovo);

      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=51 mensagens')).toBeVisible();
    });

    test('T101-TR02: transição novato → iniciante na primeira mensagem', async ({ page }) => {
      const userId = 4002;
      const login = 'novato_user';

      const statsInicial = makeStats({
        user_id: userId, login, total_messages: 0, active_rooms: 0, tier: 'novato',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: '...', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, statsInicial);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      let card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🌱 Novato')).toBeVisible();
      await expect(card).not.toHaveClass(/items-start/);

      // Transição
      const statsNovo = makeStats({
        user_id: userId, login, total_messages: 1, active_rooms: 1, tier: 'iniciante',
      });
      await simulateWSStatsUpdate(page, userId, statsNovo);

      // Após transição, o card muda para o modo completo com title atualizado
      card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
      await expect(card.locator('text=1 mensagem')).toBeVisible();
    });

    test('T101-TR03: transição participante → veterano ao atingir 201 msgs', async ({ page }) => {
      const userId = 4003;
      const login = 'ana_silva_vet';

      const statsInicial = makeStats({
        user_id: userId, login, total_messages: 200, active_rooms: 6, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg 200', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, statsInicial);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      let card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible();

      // Transição
      const statsNovo = makeStats({
        user_id: userId, login, total_messages: 201, active_rooms: 6, tier: 'veterano',
      });
      await simulateWSStatsUpdate(page, userId, statsNovo);

      card = signatureCard(page, login);
      await expect(card.locator('text=👑 VETERANO')).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=201 mensagens')).toBeVisible();
    });
  });

  // ──────────────────────────────────────────────────────────────────
  // ATUALIZAÇÃO EM TEMPO REAL (WebSocket)
  // ──────────────────────────────────────────────────────────────────

  test.describe('Atualização em Tempo Real (WebSocket)', () => {

    test('T101-WS01: assinatura atualiza após evento user_stats_changed', async ({ page }) => {
      const userId = 5001;
      const login = 'joao_silva';

      const statsInicial = makeStats({
        user_id: userId, login, total_messages: 49, active_rooms: 2, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'antes da 50ª', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, statsInicial);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=49 mensagens')).toBeVisible();
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();

      // Simula nova mensagem → servidor emite user_stats_changed
      const statsAtualizado = makeStats({
        user_id: userId, login, total_messages: 50, active_rooms: 2, tier: 'iniciante',
      });
      await simulateWSStatsUpdate(page, userId, statsAtualizado);

      await expect(card.locator('text=50 mensagens')).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
    });

    test('T101-WS02: múltiplas instâncias do mesmo autor atualizam simultaneamente', async ({ page }) => {
      const userId = 5002;
      const login = 'pedro_lider';

      const statsInicial = makeStats({
        user_id: userId, login, total_messages: 200, active_rooms: 4, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg A', created_at: '2025-01-01T10:00:00Z' },
        { id: 2, user_id: userId, login, content: 'msg B', created_at: '2025-01-01T10:01:00Z' },
        { id: 3, user_id: userId, login, content: 'msg C', created_at: '2025-01-01T10:02:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, statsInicial);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      // 3 cards do mesmo autor
      const cards = page.locator(`[title*="${login} —"]`);
      await expect(cards).toHaveCount(3, { timeout: 5000 });

      // Todas mostram 200 msgs, tier participante
      await expect(page.locator('text=200 mensagens')).toHaveCount(3);
      await expect(page.locator('text=⭐ PARTICIPANTE')).toHaveCount(3);

      // Transição
      const statsNovo = makeStats({
        user_id: userId, login, total_messages: 201, active_rooms: 4, tier: 'veterano',
      });
      await simulateWSStatsUpdate(page, userId, statsNovo);

      await expect(page.locator('text=201 mensagens')).toHaveCount(3, { timeout: 5000 });
      await expect(page.locator('text=👑 VETERANO')).toHaveCount(3);
    });
  });

  // ──────────────────────────────────────────────────────────────────
  // STATS GLOBAIS (CROSS-CHANNEL)
  // ──────────────────────────────────────────────────────────────────

  test.describe('Stats Globais (Cross-Channel)', () => {

    test('T101-GL01: stats refletem agregado global, não apenas o canal atual', async ({ page }) => {
      const userId = 6001;
      const login = 'global_user';

      const stats = makeStats({
        user_id: userId, login, total_messages: 55, active_rooms: 2, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg no canal geral', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, stats);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=55 mensagens')).toBeVisible();
      await expect(card.locator('text=2 salas ativas')).toBeVisible();
      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible();
    });

    test('T101-GL02: usuário com mensagens só em outro canal tem stats completos', async ({ page }) => {
      const userId = 6002;
      const login = 'maria_dev_cross';

      const stats = makeStats({
        user_id: userId, login, total_messages: 100, active_rooms: 1, tier: 'participante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg antiga', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, stats);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=100 mensagens')).toBeVisible();
      await expect(card.locator('text=1 sala ativa')).toBeVisible();
      await expect(card.locator('text=⭐ PARTICIPANTE')).toBeVisible();

      // "0 mensagens" não deve estar visível — usamos regex para evitar match parcial em "100"
      await expect(card.locator('text=/^0 mensagens/')).not.toBeVisible();
    });
  });

  // ──────────────────────────────────────────────────────────────────
  // RESILIÊNCIA E EDGE CASES
  // ──────────────────────────────────────────────────────────────────

  test.describe('Resiliência e Edge Cases', () => {

    test('T101-RS01: API de stats falha → exibe fallback "stats indisponíveis"', async ({ page }) => {
      await mockMessagesAPI(page, [
        { id: 1, user_id: 9999, login: 'user_error', content: 'msg', created_at: '2025-01-01T10:00:00Z' },
      ]);

      await page.route('**/api/users/*/stats', async (route) => {
        await route.fulfill({ status: 500, contentType: 'application/json', body: '{"error":"fail"}' });
      });

      await goToChat(page);

      await expect(page.locator('text=stats indisponíveis')).toBeVisible({ timeout: 5000 });
      await expect(page.locator('text=[?]')).toBeVisible();
    });

    test('T101-RS02: API retorna 404 para usuário inexistente', async ({ page }) => {
      await mockMessagesAPI(page, [
        { id: 1, user_id: 7777, login: 'fake_user_999', content: 'msg', created_at: '2025-01-01T10:00:00Z' },
      ]);

      await page.route('**/api/users/*/stats', async (route) => {
        await route.fulfill({ status: 404, contentType: 'application/json', body: '{"error":"not found"}' });
      });

      await goToChat(page);

      await expect(page.locator('text=stats indisponíveis')).toBeVisible({ timeout: 5000 });
    });

    test('T101-RS03: usuário sem avatar exibe iniciais', async ({ page }) => {
      const userId = 7003;
      const login = 'new_user';

      const stats = makeStats({
        user_id: userId, login, avatar_url: '',
        total_messages: 5, active_rooms: 1, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'oi', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, stats);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });

      // O avatar placeholder é uma div com as iniciais. Verificamos que existe
      // um elemento com texto "NE" DENTRO do card que é uma div (não span).
      const initialsEl = card.locator('div.w-8.h-8');
      await expect(initialsEl).toBeVisible();
      await expect(initialsEl).toContainText('NE');
    });

    test('T101-RS04: assinatura mantém último estado após perda de conexão', async ({ page }) => {
      const userId = 7004;
      const login = 'maria_dev_ws';

      const stats = makeStats({
        user_id: userId, login, total_messages: 42, active_rooms: 3, tier: 'iniciante',
      });

      await mockMessagesAPI(page, [
        { id: 1, user_id: userId, login, content: 'msg com stats', created_at: '2025-01-01T10:00:00Z' },
      ]);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      statsMap.set(userId, stats);
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      const card = signatureCard(page, login);
      await expect(card).toBeVisible({ timeout: 5000 });
      await expect(card.locator('text=42 mensagens')).toBeVisible();

      // Simula desconexão do WebSocket mockado
      await page.evaluate(() => {
        const sockets: any[] = (window as any).__mockSockets || [];
        sockets.forEach((s: any) => {
          if (s.onclose) s.onclose(new CloseEvent('close', { code: 1006, reason: 'connection lost' }));
        });
      });

      await page.waitForTimeout(1000);

      // Stats devem continuar visíveis (estado React preservado)
      await expect(card.locator('text=42 mensagens')).toBeVisible();
      await expect(card.locator('text=🔰 INICIANTE')).toBeVisible();
    });

    test('T101-RS05: thresholds de tier corretos (0, 1-50, 51-200, 201+)', async ({ page }) => {
      const testCases = [
        { userId: 8001, login: 't0', total_messages: 0, tier: 'novato' as const, icon: '🌱', label: 'Novato' },
        { userId: 8002, login: 't1', total_messages: 1, tier: 'iniciante' as const, icon: '🔰', label: 'Iniciante' },
        { userId: 8003, login: 't50', total_messages: 50, tier: 'iniciante' as const, icon: '🔰', label: 'Iniciante' },
        { userId: 8004, login: 't51', total_messages: 51, tier: 'participante' as const, icon: '⭐', label: 'Participante' },
        { userId: 8005, login: 't200', total_messages: 200, tier: 'participante' as const, icon: '⭐', label: 'Participante' },
        { userId: 8006, login: 't201', total_messages: 201, tier: 'veterano' as const, icon: '👑', label: 'Veterano' },
      ];

      const messages = testCases.map((tc, i) => ({
        id: i + 1,
        user_id: tc.userId,
        login: tc.login,
        content: `msg de ${tc.login}`,
        created_at: new Date(Date.now() + i * 60000).toISOString(),
      }));

      await mockMessagesAPI(page, messages);

      const statsMap = new Map<number, ReturnType<typeof makeStats>>();
      for (const tc of testCases) {
        statsMap.set(tc.userId, makeStats({
          user_id: tc.userId, login: tc.login,
          total_messages: tc.total_messages, active_rooms: 1, tier: tc.tier,
        }));
      }
      await mockStatsMap(page, statsMap);
      await goToChat(page);

      for (const tc of testCases) {
        const card = signatureCard(page, tc.login);
        await expect(card).toBeVisible({ timeout: 5000 });
        await expect(card.locator(`text=${tc.icon} ${tc.label}`)).toBeVisible();
      }
    });
  });
});
