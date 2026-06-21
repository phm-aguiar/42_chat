---
title: Vite Environment API
category: references
tags: [vite, environment, ssr, multi-runtime]
aliases: [Vite 6 Environment API]
sources: ["_raw/environment-api.md"]
summary: API de múltiplos ambientes do Vite 6+: configuração de runtimes client/server/edge com herança de config e custom environment providers.
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
base_confidence: 0.65
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: 2026-06-16
updated: 2026-06-16
---
# Vite Environment API (Vite 6+)

A Environment API formaliza múltiplos ambientes de runtime além da divisão tradicional client/SSR.

## Conceito

- **Antes do Vite 6:** Dois ambientes implícitos (`client` e `ssr`)
- **Vite 6+:** Configure quantos ambientes precisar (browser, node server, edge server, etc.)

## Basic Configuration

Para SPA/MPA, nada muda — opções se aplicam ao ambiente `client` implícito:

```ts
export default defineConfig({
  build: { sourcemap: false },
  optimizeDeps: { include: ['lib'] },
})
```

## Multiple Environments

```ts
export default defineConfig({
  build: { sourcemap: false },  // Inherited by all environments
  optimizeDeps: { include: ['lib'] },  // Client only
  environments: {
    server: {},  // SSR environment
    edge: {
      resolve: { noExternal: true },  // Edge runtime
    },
  },
})
```

Environments herdam config top-level. Algumas opções (`optimizeDeps`) só se aplicam ao `client` por padrão.

## Environment Options

```ts
interface EnvironmentOptions {
  define?: Record<string, any>
  resolve?: EnvironmentResolveOptions
  optimizeDeps: DepOptimizationOptions
  consumer?: 'client' | 'server'
  dev: DevOptions
  build: BuildOptions
}
```

## Custom Environment Instances

Runtime providers podem definir custom environments:

```ts
import { customEnvironment } from 'vite-environment-provider'

export default defineConfig({
  environments: {
    ssr: customEnvironment({
      build: { outDir: '/dist/ssr' },
    }),
  },
})
```

Exemplo: o plugin Vite da Cloudflare roda código no runtime `workerd` durante desenvolvimento.

## Backward Compatibility

- `server.moduleGraph` retorna visão mista client/SSR
- `ssrLoadModule` ainda funciona
- Apps SSR existentes funcionam sem mudanças

## Quando Usar

| Perfil | Ação |
|--------|------|
| End users | Normalmente não precisa configurar — frameworks cuidam |
| Plugin authors | Transformações environment-aware |
| Framework authors | Custom environments para necessidades de runtime |

## Plugin Environment Access

```ts
{
  name: 'env-aware',
  transform(code, id, options) {
    if (options?.ssr) { /* SSR-specific transform */ }
  },
}
```

## Sources

- [Vite Environment API](https://vite.dev/guide/api-environment)
- [Announcing Vite 6](https://vite.dev/blog/announcing-vite6)
