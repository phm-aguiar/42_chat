---
title: "Getting Started com MDX"
category: references
tags:
  - mdx
  - markdown
  - jsx
  - bundler
  - react
  - vite
summary: >-
  Guia oficial de integração do MDX em projetos — configuração de bundlers
  (esbuild, Rollup, Vite, webpack), JSX runtimes (React, Preact, Vue, Solid,
  Svelte, Emotion), editores e types.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
sources:
  - https://mdxjs.com/docs/getting-started/
---

# Getting Started com MDX

> Guia de integração do MDX no seu projeto com bundler e JSX runtime.

## Quick Start

### Bundlers

- **esbuild (ou Bun):** [`@mdx-js/esbuild`](https://mdxjs.com/packages/esbuild/)
- **Rollup (ou Vite):** [`@mdx-js/rollup`](https://mdxjs.com/packages/rollup/)
- **webpack (ou Next.js):** [`@mdx-js/loader`](https://mdxjs.com/packages/loader/)
- **Node.js:** [`@mdx-js/node-loader`](https://mdxjs.com/packages/node-loader/)
- **Core:** [`@mdx-js/mdx`](https://mdxjs.com/packages/mdx/)

### JSX Runtimes

| Runtime | Configuração |
|---------|-------------|
| **React** | Padrão. Opcional: `@mdx-js/react` |
| **Preact** | `jsxImportSource: 'preact'` |
| **Vue** | `jsxImportSource: 'vue'` |
| **Solid** | `jsxImportSource: 'solid-js/h'` |
| **Svelte** | `jsxImportSource: 'svelte-jsx'` |
| **Emotion** | `jsxImportSource: '@emotion/react'` |

### Editores

- **VS Code:** [`mdx-js/mdx-analyzer`](https://github.com/mdx-js/mdx-analyzer)
- **Vim:** [`jxnblk/vim-mdx-js`](https://github.com/jxnblk/vim-mdx-js)
- **Sublime:** [`jonsuh/mdx-sublime`](https://github.com/jonsuh/mdx-sublime)
- **IntelliJ/WebStorm:** [`JetBrains/mdx-intellij-plugin`](https://github.com/JetBrains/intellij-plugins/tree/master/mdx)

### Types

```bash
npm install @types/mdx
```

```ts
import Post from './post.mdx' // Post é tipado
```

## Integrações

### Vite

```js
import mdx from '@mdx-js/rollup'
import {defineConfig} from 'vite'

const viteConfig = defineConfig({
  plugins: [mdx({/* jsxImportSource: …, otherOptions… */})]
})
```

> Se usar `@vitejs/plugin-react`, force `@mdx-js/rollup` a rodar em `pre`:
> `{enforce: 'pre', ...mdx({/* … */})}`

### Next.js

```js
import nextMdx from '@next/mdx'
const withMdx = nextMdx({extension: /\.mdx?$/, options: {/* … */}})
const nextConfig = withMdx({pageExtensions: ['md', 'mdx', 'tsx', 'ts', 'jsx', 'js']})
```

### Segurança

MDX é uma linguagem de programação. Não deixe pessoas aleatórias da internet
escreverem MDX. Use `<iframe>` com `sandbox`, Docker ou `vm2` para Node.js.

## Relacionado

- [[references/mdx/what-is-mdx|O que é MDX?]]
- [[references/mdx/using-mdx|Usando MDX]]
- [[references/mdx/extending-mdx|Estendendo MDX]]
- [[references/mdx/troubleshooting-mdx|Troubleshooting MDX]]
