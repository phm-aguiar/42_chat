---
title: Estendendo MDX
category: references
tags:
  - mdx
  - plugins
  - remark
  - rehype
  - recma
summary: Documentação oficial sobre como estender MDX com plugins — remark, rehype e recma plugins para transformar conteúdo em diferentes estágios da compilação.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
---

# Estendendo MDX

> Como transformar conteúdo MDX com plugins nos três estágios de compilação:
> remark (markdown AST), rehype (HTML AST) e recma (JS AST).

## Pontos de Extensão

1. **Opções do compilador** — ver API em `@mdx-js/mdx`
2. **Plugins** em três estágios:
   - `remarkPlugins` — transformam a árvore markdown (MD AST)
   - `rehypePlugins` — transformam a árvore HTML (HAST)
   - `recmaPlugins` — transformam a árvore JavaScript (ESTree)
3. **Componentes** — passados, definidos ou importados em runtime

## Plugins MDX-specific

### Remark

- [`remark-directive-mdx`](https://github.com/re-xyr/remark-directive-mdx) — directives → JSX
- [`remark-mdx-chartjs`](https://github.com/pangelani/remark-mdx-chartjs) — code blocks → charts
- [`remark-mdx-frontmatter`](https://github.com/remcohaszing/remark-mdx-frontmatter) — frontmatter → exports
- [`remark-mdx-math-enhanced`](https://github.com/goodproblems/remark-mdx-math-enhanced) — math com JS
- [`remark-mdx-remove-esm`](https://github.com/ipikuka/remark-mdx-remove-esm) — remove import/export
- [`remark-mdx-remove-expressions`](https://github.com/ipikuka/remark-mdx-remove-expressions) — remove expressões

### Rehype

- [`rehype-mdx-code-props`](https://github.com/remcohaszing/rehype-mdx-code-props) — code meta → JSX props
- [`rehype-mdx-import-media`](https://github.com/remcohaszing/rehype-mdx-import-media) — media sources → imports
- [`rehype-mdx-title`](https://github.com/remcohaszing/rehype-mdx-title) — expõe title como string
- [`rehype-mdx-toc`](https://github.com/boning-w/rehype-mdx-toc) — exporta TOC como dado

### Recma

- [`recma-export-filepath`](https://github.com/remcohaszing/recma-export-filepath) — exporta filepath
- [`recma-mdx-change-props`](https://github.com/ipikuka/recma-mdx-change-props) — `_props` param
- [`recma-mdx-displayname`](https://github.com/domdomegg/recma-mdx-displayname) — displayName pra MDXContent
- [`recma-mdx-escape-missing-components`](https://github.com/ipikuka/recma-mdx-escape-missing-components) — default null pra missing
- [`recma-mdx-is-mdx-component`](https://github.com/remcohaszing/recma-mdx-is-mdx-component) — flag isMdxComponent
- [`recma-nextjs-static-props`](https://github.com/remcohaszing/recma-nextjs-static-props) — getStaticProps
- [`recma-module-to-function`](https://github.com/remcohaszing/recma-module-to-function) — module → function body

## Usando Plugins

```ts
import {compile} from '@mdx-js/mdx'
import remarkGfm from 'remark-gfm'
import rehypeKatex from 'rehype-katex'

// Um plugin:
await compile(file, {remarkPlugins: [remarkGfm]})

// Plugin com options:
await compile(file, {remarkPlugins: [[remarkGfm, {singleTilde: false}]]})

// remark + rehype:
await compile(file, {rehypePlugins: [rehypeKatex], remarkPlugins: [remarkMath]})
```

## Criando Plugins

Criar plugins para MDX é similar a criar plugins remark/rehype/recma.
Ver [unifiedjs.com/learn/](https://unifiedjs.com/learn/). Para partes MDX-specific,
ler a [Arquitetura do `@mdx-js/mdx`](https://mdxjs.com/packages/mdx/#architecture).

## Relacionado

- [[references/mdx/what-is-mdx|O que é MDX?]]
- [[references/mdx/getting-started|Getting Started com MDX]]
- [[references/mdx/using-mdx|Usando MDX]]
- [[references/mdx/troubleshooting-mdx|Troubleshooting MDX]]
