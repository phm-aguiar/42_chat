---
title: React + Vite Environment & Bundle Analysis
category: references
tags: [react, vite, environment, security, bundle, visualizer]
aliases: [React Vite Env Config]
sources: ["_raw/env-vite-prefix.md", "_raw/env-modes.md", "_raw/env-sensitive-data.md", "_raw/bundle-visualizer.md"]
summary: "4 regras MEDIUM de env config + bundle analysis React+Vite: prefixo VITE_ para segurança, mode-specific env files (.env.development/.production/staging), proteção de secrets e bundle visualizer com rollup-plugin-visualizer."
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
rag_score: 0.4829
updated: 2026-06-16
---
# React + Vite Environment & Bundle Analysis

3 regras de environment config + 1 de bundle analysis. Todas com impacto **MEDIUM**.

## 1. VITE_ Prefix for Client Variables {#vite-prefix}

**Impacto: MEDIUM (Security and proper configuration)**

Apenas variáveis com prefixo `VITE_` são expostas ao client-side.

**Incorreto:**
```env
API_KEY=secret123       # NOT exposed — retorna undefined
DATABASE_URL=postgres://...
VITE_DATABASE_URL=postgres://...  # EXPOSTO no bundle! ⚠️
```

**Correto:**
```env
# Client-side (exposto ao browser)
VITE_API_URL=https://api.example.com
VITE_APP_TITLE=My App
VITE_ENABLE_ANALYTICS=true

# Server-side only (NÃO exposto)
DATABASE_URL=postgres://...
API_SECRET=secret123
```

**TypeScript types:**
```ts
// src/vite-env.d.ts
/// <reference types="vite/client" />
interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_ENABLE_ANALYTICS: string
}
interface ImportMeta { readonly env: ImportMetaEnv }
```

Built-in variables (sempre disponíveis):
```ts
import.meta.env.DEV    // true em dev
import.meta.env.PROD   // true em produção
import.meta.env.MODE   // 'development' | 'production' | custom
import.meta.env.BASE_URL
```

## 2. Mode-Specific Environment Files {#modes}

**Impacto: MEDIUM (Wrong env config leaks secrets or uses wrong API URLs)**

Priority order (maior sobrepõe menor):
```
1. .env.[mode].local   (gitignored)
2. .env.[mode]
3. .env.local          (gitignored)
4. .env                (shared defaults)
```

```env
# .env — shared defaults, loaded in ALL modes
VITE_APP_NAME=MyApp

# .env.development — vite dev
VITE_API_URL=http://localhost:8000/api
VITE_FEATURE_DEBUG=true

# .env.production — vite build
VITE_API_URL=https://api.example.com
VITE_FEATURE_DEBUG=false
VITE_SENTRY_DSN=https://abc@sentry.io/123

# .env.staging — vite build --mode staging
VITE_API_URL=https://staging-api.example.com
VITE_FEATURE_DEBUG=true
VITE_SENTRY_DSN=https://abc@sentry.io/456
```

```bash
npx vite dev                    # .env + .env.development
npx vite build                  # .env + .env.production
npx vite build --mode staging   # .env + .env.staging
```

**Type-safe config:**
```ts
export const config = {
  appName: import.meta.env.VITE_APP_NAME,
  apiUrl: import.meta.env.VITE_API_URL,
  isDebug: import.meta.env.VITE_FEATURE_DEBUG === 'true',
  sentryDsn: import.meta.env.VITE_SENTRY_DSN ?? null,
  mode: import.meta.env.MODE,
} as const
```

## 3. Never Expose Secrets in Client Code {#sensitive-data}

**Impacto: MEDIUM (VITE_ variables are embedded in the client bundle — visible to anyone)**

Qualquer variável com prefixo `VITE_` é estaticamente substituída no bundle e visível em DevTools > Sources.

**Incorreto:**
```env
VITE_STRIPE_SECRET_KEY=sk_live_...   # EXPOSTA no JS do browser
VITE_AWS_SECRET_ACCESS_KEY=...       # EXPOSTA
```

```ts
// NUNCA faça isso — chama API externa direto do client com secret
fetch('https://api.stripe.com/v1/charges', {
  headers: { Authorization: `Bearer ${import.meta.env.VITE_STRIPE_SECRET_KEY}` },
})
```

**Correto — Backend proxy pattern:**
```env
# Só valores públicos com VITE_
VITE_API_URL=https://api.example.com
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_abc123

# Secrets sem VITE_ = NÃO expostos
STRIPE_SECRET_KEY=sk_live_...
DB_PASSWORD=super-secret
```

```ts
// Client chama SEU backend, que detém os secrets
export async function createCharge(amount: number) {
  const response = await fetch(`${import.meta.env.VITE_API_URL}/payments/charge`, {
    method: 'POST', body: JSON.stringify({ amount }),
  })
  return response.json()
}
```

**Dev-time leak detection:**
```ts
if (import.meta.env.DEV) {
  const suspicious = Object.keys(import.meta.env).filter(
    key => key.startsWith('VITE_') && /secret|password|private|token/i.test(key)
  )
  if (suspicious.length > 0) {
    console.warn(`Potentially sensitive VITE_ variables: ${suspicious.join(', ')}`)
  }
}
```

## 4. Bundle Analysis with Visualizer {#bundle-visualizer}

**Impacto: MEDIUM (Can't optimize what you can't measure)**

```bash
npm install -D rollup-plugin-visualizer
```

```ts
import { visualizer } from 'rollup-plugin-visualizer'

plugins: [
  // Only enable when ANALYZE env var is set
  process.env.ANALYZE === 'true' && visualizer({
    filename: 'stats.html',
    open: true,
    gzipSize: true,
    brotliSize: true,
    template: 'treemap',  // 'treemap' | 'sunburst' | 'network'
  }),
].filter(Boolean)
```

```json
{ "scripts": { "analyze": "ANALYZE=true vite build" } }
```

**Como ler o output:**
1. Retângulos grandes = módulos grandes — foque otimização aqui
2. Verifique: dependências inesperadamente grandes, pacotes duplicados, código que deveria ser lazy-loaded
3. Ações comuns: substituir moment.js (330KB) por date-fns/dayjs (2-7KB), usar named imports (`import { debounce } from 'lodash-es'`), lazy-load rotas pesadas, split vendor chunks

---

← Back to [[references/react-vite-performance|React + Vite Performance MoC]]


