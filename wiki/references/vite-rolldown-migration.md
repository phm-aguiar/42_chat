---
title: Vite Rolldown Migration
category: references
tags: [vite, rolldown, oxc, migration, bundler]
aliases: [Vite 8 Rolldown]
sources: ["_raw/rolldown-migration.md"]
summary: Guia de migração Vite 7 → 8: Rolldown substitui esbuild+Rollup, Oxc substitui esbuild transformer, `rollupOptions` → `rolldownOptions`, `esbuild` → `oxc`.
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
updated: 2026-06-16
---
# Rolldown Migration (Vite 8)

Vite 8 substitui esbuild+Rollup pelo Rolldown, um bundler unificado Rust-based.

## O Que Mudou

| Antes (Vite 7) | Depois (Vite 8) |
|-----------------|-----------------|
| esbuild (dev transform) | Oxc Transformer |
| esbuild (dep pre-bundling) | Rolldown |
| Rollup (production build) | Rolldown |
| `rollupOptions` | `rolldownOptions` |
| `esbuild` option | `oxc` option |

## Performance

- 10-30x mais rápido que Rollup para builds de produção
- Empata com performance dev do esbuild
- Comportamento unificado entre dev e build

## Migração de Config

### rollupOptions → rolldownOptions

```ts
// Vite 7
build: { rollupOptions: { external: ['vue'], output: { globals: { vue: 'Vue' } } } }

// Vite 8
build: { rolldownOptions: { external: ['vue'], output: { globals: { vue: 'Vue' } } } }
```

### esbuild → oxc

```ts
// Vite 7
esbuild: { jsxFactory: 'h', jsxFragment: 'Fragment' }

// Vite 8
oxc: { jsx: { runtime: 'classic', pragma: 'h', pragmaFrag: 'Fragment' } }
```

### JSX Configuration

```ts
oxc: {
  jsx: {
    runtime: 'automatic',  // or 'classic'
    importSource: 'react',
  },
  jsxInject: `import React from 'react'`,
}
```

## Plugin Compatibility

A maioria dos plugins Vite funciona sem mudanças. Rolldown suporta a plugin API do Rollup.

Se um plugin só funciona durante build:
```ts
{ ...rollupPlugin(), enforce: 'post', apply: 'build' }
```

## Novas Capacidades (Rolldown)

- Full bundle mode (experimental)
- Module-level persistent cache
- Chunk splitting mais flexível
- Module Federation support

## Migração Gradual

```bash
# Step 1: Test with rolldown-vite
pnpm add -D rolldown-vite
# Replace vite import in config
import { defineConfig } from 'rolldown-vite'

# Step 2: Once stable, upgrade to Vite 8
pnpm add -D vite@8
```

## Override em Frameworks

```json
{ "pnpm": { "overrides": { "vite": "8.0.0" } } }
```
