---
title: Vite Reference
category: references
tags: [vite, bundler, frontend, rolldown, oxc]
aliases: [Vite Core Reference]
sources: ["_raw/vite.md", "_raw/core-config.md", "_raw/core-features.md", "_raw/core-plugin-api.md", "_raw/build-and-ssr.md"]
summary: Referência consolidada do Vite: configuração (vite.config.ts), features (glob import, HMR API, asset queries), plugin API (hooks, virtual modules) e build/SSR (library mode, JS API, multi-page).
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
base_confidence: 0.75
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
updated: 2026-06-16
---
# Vite Reference

> Vite 8 beta (Rolldown-powered, Oxc transformer). Vite é um build tool frontend com dev server rápido (ESM nativo + HMR) e builds de produção otimizadas.

## Preferências

- Use TypeScript: prefira `vite.config.ts`
- Sempre use ESM, evite CommonJS

## CLI Commands

```bash
vite              # Start dev server
vite build        # Production build
vite preview      # Preview production build
vite build --ssr  # SSR build
```

## Configuração (`vite.config.ts`)

### Basic Setup

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  // config options
})
```

Vite auto-resolve `vite.config.ts` da raiz do projeto. Suporta ES modules independente do `type` do `package.json`.

### Conditional Config

```ts
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === 'serve') {
    return { /* dev config */ }
  } else {
    return { /* build config */ }
  }
})
```

- `command`: `'serve'` (dev) ou `'build'` (produção)
- `mode`: `'development'` ou `'production'` (ou custom via `--mode`)

### Async Config

```ts
export default defineConfig(async ({ command, mode }) => {
  const data = await fetchSomething()
  return { /* config */ }
})
```

### Usando Variáveis de Ambiente na Config

```ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    define: { __APP_ENV__: JSON.stringify(env.APP_ENV) },
    server: { port: env.APP_PORT ? Number(env.APP_PORT) : 5173 },
  }
})
```

### Key Options

**resolve.alias:**
```ts
resolve: { alias: { '@': '/src', '~': '/src' } }
```

**define (Global Constants):**
```ts
define: {
  __APP_VERSION__: JSON.stringify('1.0.0'),
  __API_URL__: 'window.__backend_api_url',
}
```

**server.proxy:**
```ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:3000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

**build.target:**
```ts
build: { target: 'esnext' }  // ou 'baseline-widely-available' (default)
```

## Features

### Glob Import

```ts
const modules = import.meta.glob('./dir/*.ts')
// { './dir/foo.ts': () => import('./dir/foo.ts'), ... }

// Eager loading
const modules = import.meta.glob('./dir/*.ts', { eager: true })

// Named imports
const modules = import.meta.glob('./dir/*.ts', { import: 'setup' })

// Multiple patterns
const modules = import.meta.glob(['./dir/*.ts', './another/*.ts'])

// Negative patterns
const modules = import.meta.glob(['./dir/*.ts', '!**/ignored.ts'])

// Custom queries
const svgRaw = import.meta.glob('./icons/*.svg', { query: '?raw', import: 'default' })
```

### Asset Import Queries

```ts
import imgUrl from './img.png'         // URL resolvida
import workletUrl from './worklet.js?url'
import shaderCode from './shader.glsl?raw'
import inlined from './small.png?inline'
import Worker from './worker.ts?worker'
```

### Environment Variables

Built-in:
```ts
import.meta.env.MODE      // 'development' | 'production' | custom
import.meta.env.BASE_URL  // Base URL from config
import.meta.env.PROD      // true in production
import.meta.env.DEV       // true in development
import.meta.env.SSR       // true when running in server
```

Custom (apenas `VITE_` prefix exposto ao client):
```
# .env
VITE_API_URL=https://api.example.com
DB_PASSWORD=secret  # NOT exposed to client
```

### CSS Modules

```ts
import styles from './component.module.css'
element.className = styles.button
```

### HMR API

```ts
if (import.meta.hot) {
  import.meta.hot.accept((newModule) => { /* Handle update */ })
  import.meta.hot.dispose((data) => { /* Cleanup */ })
  import.meta.hot.invalidate()  // Force full reload
}
```

## Plugin API

### Basic Structure

```ts
function myPlugin(): Plugin {
  return { name: 'my-plugin', /* hooks... */ }
}
```

### Vite-Specific Hooks

**config** — Modify config before resolution. ^[extracted]

**configResolved** — Access final resolved config:
```ts
configResolved(resolvedConfig) { config = resolvedConfig }
```

**configureServer** — Add custom middleware. Return function to run after internal middlewares.

**transformIndexHtml** — Transform HTML entry files or inject tags.

**handleHotUpdate** — Custom HMR handling.

### Virtual Modules

Serve virtual content without files on disk:
```ts
const virtualModuleId = 'virtual:my-module'
const resolvedId = '\0' + virtualModuleId

return {
  name: 'virtual-module',
  resolveId(id) { if (id === virtualModuleId) return resolvedId },
  load(id) { if (id === resolvedId) return `export const msg = "from virtual module"` },
}
```

Convention: prefix user-facing path with `virtual:`, resolved id with `\0`.

### Plugin Ordering

```ts
{ name: 'pre-plugin',  enforce: 'pre'  }  // before core plugins
{ name: 'post-plugin', enforce: 'post' }  // after build plugins
```

Order: Alias → `enforce: 'pre'` → Core → User → Build → `enforce: 'post'` → Post-build

### Conditional Application

```ts
{ name: 'build-only', apply: 'build' }  // or 'serve'
// Function form:
{ apply(config, { command }) { return command === 'build' && !config.build.ssr } }
```

### Universal Hooks (from Rolldown)

Work in both dev and build: `resolveId`, `load`, `transform`.

### Client-Server Communication

```ts
// Server → Client
server.ws.send('my:event', { msg: 'hello' })
// Client: import.meta.hot.on('my:event', (data) => { ... })

// Client → Server
import.meta.hot.send('my:from-client', { msg: 'Hey!' })
server.ws.on('my:from-client', (data, client) => { client.send('my:ack', ...) })
```

## Build e SSR

### Library Mode

```ts
build: {
  lib: {
    entry: resolve(import.meta.dirname, 'lib/main.ts'),
    name: 'MyLib',
    fileName: 'my-lib',
  },
  rolldownOptions: {
    external: ['vue', 'react'],
    output: { globals: { vue: 'Vue', react: 'React' } },
  },
}
```

Single entry → `es` e `umd`; multiple entries → `es` e `cjs`.

### Multi-Page App

```ts
build: {
  rolldownOptions: {
    input: {
      main: resolve(import.meta.dirname, 'index.html'),
      nested: resolve(import.meta.dirname, 'nested/index.html'),
    },
  },
}
```

### SSR

O suporte SSR do Vite é **low-level** — feito para autores de meta-frameworks. Para apps, use meta-frameworks como Nuxt (Vue), SvelteKit, SolidStart ou TanStack Start (React).

Para servidor standalone: [Nitro](https://nitro.build) — file-based API routing, auto-imports, deploy presets para dezenas de plataformas.

### JavaScript API

```ts
import { createServer, build, preview, resolveConfig, loadEnv } from 'vite'

// Dev server
const server = await createServer({ configFile: false, root: import.meta.dirname, server: { port: 1337 } })
await server.listen()

// Build
await build({ root: './project', build: { outDir: 'dist' } })

// Preview
const previewServer = await preview({ preview: { port: 8080, open: true } })

// Env loading
const env = loadEnv('development', process.cwd(), '')
```

### Official Plugins

- `@vitejs/plugin-vue` — Vue 3 SFC
- `@vitejs/plugin-react` — React com Oxc/Babel
- `@vitejs/plugin-react-swc` — React com SWC
- `@vitejs/plugin-legacy` — Legacy browser support

## Sources

- [Vite Config](https://vite.dev/config/)
- [Vite Features](https://vite.dev/guide/features)
- [Vite Plugin API](https://vite.dev/guide/api-plugin)
- [Vite Build Guide](https://vite.dev/guide/build)
- [Vite JavaScript API](https://vite.dev/guide/api-javascript)
