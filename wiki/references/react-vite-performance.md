---
title: React + Vite Performance Rules
category: references
tags: [react, vite, performance, bundling, optimization]
sources: ["_raw/react.md", "_raw/_sections.md"]
summary: Guia de otimização de performance para apps React com Vite — 23 regras em 6 categorias cobrindo build, code splitting, dev, assets, env e bundle analysis.
provenance:
  extracted: 0.80
  inferred: 0.15
  ambiguous: 0.05
base_confidence: 0.48
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: core
created: 2026-06-16
updated: 2026-06-16
---
# React + Vite Performance Rules

Guia completo de otimização de performance para aplicações React com Vite. 23 regras em 6 categorias, da configuração de build até análise de bundle.

> Versão: 2.0.0 — Baseado em Vite 8 beta (Rolldown-powered, Oxc transformer).

## Quando Aplicar

- Configurando Vite para projetos React
- Implementando code splitting e lazy loading
- Otimizando output de build e tamanho de bundle
- Configurando ambiente de dev e HMR
- Gerenciando imagens, fontes, SVGs e assets estáticos
- Gerenciando variáveis de ambiente entre ambientes
- Analisando tamanho de bundle e dependências

## Categorias (por prioridade)

| # | Categoria | Impacto | Prefixo | Regras |
|---|-----------|---------|---------|--------|
| 1 | Build Optimization | **CRITICAL** | `build-` | 7 |
| 2 | Code Splitting | **CRITICAL** | `split-` | 5 |
| 3 | Development | HIGH | `dev-` | 3 |
| 4 | Asset Handling | HIGH | `asset-` | 4 |
| 5 | Environment Config | MEDIUM | `env-` | 3 |
| 6 | Bundle Analysis | MEDIUM | `bundle-` | 1 |

## Catálogo de Regras

### 1. Build Optimization (CRITICAL)

- [[references/react-vite-build-optimization#manual-chunks|Manual Chunks]] — Separação de vendors para caching ótimo
- [[references/react-vite-build-optimization#minification|Minification]] — OXC (default) ou Terser para compressão máxima
- [[references/react-vite-build-optimization#modern-target|Modern Target]] — `baseline-widely-available` ou `esnext` para bundles menores
- [[references/react-vite-build-optimization#sourcemaps|Sourcemaps]] — Configuração por ambiente com integração Sentry
- [[references/react-vite-build-optimization#tree-shaking|Tree Shaking]] — Eliminação de dead code com ESM e named exports
- [[references/react-vite-build-optimization#compression|Compression]] — Gzip + Brotli pre-compressed no build
- [[references/react-vite-build-optimization#asset-hashing|Asset Hashing]] — Content-based hashing para cache busting

### 2. Code Splitting (CRITICAL)

- [[references/react-vite-code-splitting#route-lazy|Route Lazy]] — `React.lazy()` para rotas (50-80% menor)
- [[references/react-vite-code-splitting#suspense-boundaries|Suspense Boundaries]] — Posicionamento estratégico para carregamento progressivo
- [[references/react-vite-code-splitting#dynamic-imports|Dynamic Imports]] — Bibliotecas pesadas sob demanda (30-50% menor)
- [[references/react-vite-code-splitting#component-lazy|Component Lazy]] — Modais e drawers lazy (20-40% menor)
- [[references/react-vite-code-splitting#prefetch-hints|Prefetch Hints]] — Prefetch em hover/idle/viewport

### 3. Development (HIGH)

- [[references/react-vite-development#dependency-prebundling|Dependency Pre-bundling]] — `optimizeDeps` (2-5x faster cold start)
- [[references/react-vite-development#fast-refresh|Fast Refresh]] — Estrutura de componentes compatível
- [[references/react-vite-development#hmr-config|HMR Config]] — WebSocket, Docker/WSL, polling

### 4. Asset Handling (HIGH)

- [[references/react-vite-asset-handling#image-optimization|Image Optimization]] — WebP/AVIF, lazy loading, dimensões explícitas
- [[references/react-vite-asset-handling#svg-components|SVG Components]] — SVGR para styling CSS e `currentColor`
- [[references/react-vite-asset-handling#fonts|Font Loading]] — Self-hosted, `font-display: swap`, subset
- [[references/react-vite-asset-handling#public-dir|Public Dir vs Import]] — Quando usar cada um

### 5. Environment Config (MEDIUM)

- [[references/react-vite-environment-config#vite-prefix|VITE_ Prefix]] — Segurança: só `VITE_` chega ao client
- [[references/react-vite-environment-config#modes|Mode Files]] — `.env.development`, `.env.production`, `--mode staging`
- [[references/react-vite-environment-config#sensitive-data|Sensitive Data]] — Secrets nunca no client

### 6. Bundle Analysis (MEDIUM)

- [[references/react-vite-environment-config#bundle-visualizer|Bundle Visualizer]] — `rollup-plugin-visualizer` com treemap interativo

## Configuração Recomendada

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],

  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },

  build: {
    target: 'baseline-widely-available',
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
        },
      },
    },
  },

  optimizeDeps: {
    include: ['react', 'react-dom'],
  },

  server: {
    port: 3000,
    hmr: { overlay: true },
  },
})
```

## Outras Referências Vite

- [[references/vite-reference|Vite Reference]] — Config, features, plugins, build/SSR
- [[references/vite-environment-api|Vite Environment API]] — Multi-environment (Vite 6+)
- [[references/vite-rolldown-migration|Vite Rolldown Migration]] — Migração Vite 7 → 8

## Sources

- [Vite Documentation](https://vite.dev)
- [React Documentation](https://react.dev)
- [Rollup Documentation](https://rollupjs.org)
