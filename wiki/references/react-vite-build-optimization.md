---
title: React + Vite Build Optimization
category: references
tags: [react, vite, build, bundling, optimization]
sources: ["_raw/build-manual-chunks.md", "_raw/build-minification.md", "_raw/build-target-modern.md", "_raw/build-sourcemaps.md", "_raw/build-tree-shaking.md", "_raw/build-compression.md", "_raw/build-asset-hashing.md"]
summary: 7 regras CRITICAL de build do React+Vite: manual chunks, minification (OXC/Terser), modern target, sourcemaps, tree shaking, compression (gzip+Brotli) e asset hashing.
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
updated: 2026-06-16
---
# React + Vite Build Optimization

7 regras de otimização de build para React + Vite. Todas com impacto **CRITICAL**.

## 1. Manual Chunks for Vendor Separation {#manual-chunks}

**Impacto: CRITICAL (Optimal caching and parallel loading)**

Sem manual chunks, Vite empacota todas as dependências vendor num chunk único ou mistura com código da aplicação.

**Incorreto:**
```ts
export default defineConfig({
  plugins: [react()],
  build: { /* no manual chunks */ },
})
```

**Correto:**
```ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react': ['react', 'react-dom'],
          'vendor-router': ['react-router-dom'],
        },
      },
    },
  },
})
```

Ou via função dinâmica:
```ts
manualChunks(id) {
  if (id.includes('node_modules')) {
    if (id.includes('react-dom')) return 'vendor-react-dom'
    if (id.includes('react')) return 'vendor-react'
    return 'vendor'
  }
}
```

> Nota: Quando Rolldown estiver totalmente integrado, `advancedChunks` será o substituto recomendado para `manualChunks`. ^[inferred]

## 2. Optimal Minification {#minification}

**Impacto: CRITICAL (30-50% smaller bundles)**

**OXC (default, recomendado):**
```ts
build: {
  // OXC is default — fastest, no config needed
  esbuild: {
    drop: ['console', 'debugger'],
    legalComments: 'none',
  },
}
```

**Terser (compressão máxima, build mais lento):**
```ts
build: {
  minify: 'terser',
  terserOptions: {
    compress: {
      drop_console: true, drop_debugger: true,
      inline: 2, dead_code: true, booleans_as_integers: true, passes: 2,
    },
    mangle: { properties: { regex: /^_/ } },
    format: { comments: false, ascii_only: true },
  },
}
```

Padrões de código que ajudam minificação: private class fields (`#`) permitem melhor property mangling.

## 3. Target Modern Browsers {#modern-target}

**Impacto: CRITICAL (10-15% smaller bundles)**

```ts
build: {
  target: 'esnext',  // Smallest bundle if you control the browser env
}
```

| Target | Uso |
|--------|-----|
| `esnext` | Menor bundle, funcionalidades mais recentes |
| `baseline-widely-available` | Default — amplo suporte |
| `es2022` | Bom balanço |
| Custom array | Versões específicas de browsers |

Para suporte legacy:
```ts
import legacy from '@vitejs/plugin-legacy'
plugins: [legacy({ targets: ['defaults', 'not IE 11'] })]
build: { target: 'esnext' }  // Modern build, legacy chunks só carregam em browsers antigos
```

## 4. Source Maps Configuration {#sourcemaps}

**Impacto: CRITICAL (Better error tracking without exposing source)**

```ts
export default defineConfig(({ mode }) => ({
  build: {
    sourcemap: mode === 'production' ? 'hidden' : true,
    rollupOptions: { output: { sourcemapExcludeSources: mode === 'production' } },
  },
  css: { devSourcemap: true },
}))
```

| Opção | Descrição | Uso |
|-------|-----------|-----|
| `false` | Sem source maps | Não recomendado |
| `true` | Gera e linka .map files | Dev/Staging |
| `'inline'` | Embebe maps nos bundles | Dev only |
| `'hidden'` | Gera .map sem link | Produção |

Integração Sentry:
```ts
import { sentryVitePlugin } from '@sentry/vite-plugin'

plugins: [
  sentryVitePlugin({
    org: process.env.SENTRY_ORG,
    project: process.env.SENTRY_PROJECT,
    authToken: process.env.SENTRY_AUTH_TOKEN,
    sourcemaps: {
      assets: './dist/**',
      filesToDeleteAfterUpload: './dist/**/*.map',
    },
  }),
]
build: { sourcemap: true }  // Required for Sentry
```

## 5. Tree Shaking {#tree-shaking}

**Impacto: CRITICAL (15-30% smaller bundles)**

**Incorreto:** Barrel exports com `export *`, namespace imports (`import *`), libs CJS não tree-shakeable (lodash, moment), sem `sideEffects` no package.json.

**Correto:**
```ts
// Named exports
export { formatString, capitalize } from './strings'
import { formatDate } from './utils'

// Tree-shakeable libraries
import uniqBy from 'lodash-es/uniqBy'
import { format } from 'date-fns'
```

```json
{ "sideEffects": ["*.css", "*.scss", "./src/polyfills.ts"] }
```

```ts
build: {
  rollupOptions: {
    treeshake: {
      moduleSideEffects: 'no-external',
      propertyReadSideEffects: false,
      tryCatchDeoptimization: false,
    },
  },
}
```

## 6. Build-Time Compression {#compression}

**Impacto: CRITICAL (60-80% smaller asset size)**

Pre-compress assets durante o build (evita overhead de runtime):

```ts
import viteCompression from 'vite-plugin-compression'

plugins: [
  viteCompression({ algorithm: 'gzip', ext: '.gz', threshold: 1024 }),
  viteCompression({ algorithm: 'brotliCompress', ext: '.br', threshold: 1024 }),
]
```

| Formato | Suporte | Compressão | Melhor para |
|---------|---------|------------|-------------|
| Gzip | 95%+ | 70-80% | Fallback universal |
| Brotli | 90%+ | 80-90% | Browsers modernos |

Nginx para servir pre-compressed:
```nginx
gzip_static on;
brotli_static on;
```

## 7. Asset Hashing for Cache Busting {#asset-hashing}

**Impacto: CRITICAL (Ensures latest version delivery)**

```ts
build: {
  rollupOptions: {
    output: {
      entryFileNames: 'assets/js/[name]-[hash].js',
      chunkFileNames: 'assets/js/[name]-[hash].js',
      assetFileNames: (assetInfo) => {
        const ext = assetInfo.name?.split('.').pop()
        if (/png|jpe?g|gif|svg|webp|avif/i.test(ext)) return 'assets/images/[name]-[hash][extname]'
        if (/woff2?|eot|ttf|otf/i.test(ext)) return 'assets/fonts/[name]-[hash][extname]'
        if (/css/i.test(ext)) return 'assets/css/[name]-[hash][extname]'
        return 'assets/[name]-[hash][extname]'
      },
    },
  },
}
```

Estratégia de cache:
| Cache-Control | Target |
|---------------|--------|
| `public, max-age=31536000, immutable` | Hashed assets |
| `no-cache, must-revalidate` | HTML files, service workers |

---

← Back to [[references/react-vite-performance|React + Vite Performance MoC]]

## Sources

- [Vite Build Options](https://vitejs.dev/config/build-options.html)
- [Rollup Tree Shaking](https://rollupjs.org/configuration-options/#treeshake)
- [vite-plugin-compression](https://github.com/vbenjs/vite-plugin-compression)
