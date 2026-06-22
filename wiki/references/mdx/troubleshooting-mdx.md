---
title: Troubleshooting MDX
category: references
tags:
  - mdx
  - troubleshooting
  - errors
  - esm
summary: "Documentação oficial de troubleshooting MDX — problemas comuns de integração, uso e escrita: ESM, erros de parsing JSX, expressões, interleaving e migração v1→v2."
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
---

# Troubleshooting MDX

> Problemas comuns e erros ao usar MDX, organizados por categoria.

## Problemas de Integração

### ESM

MDX v2 usa ESM nativamente. Se ferramentas não suportam ESM:

- Use um bundler para gerar CJS: `npx esbuild @mdx-js/mdx --bundle --platform=node --outfile=vendor/mdx.js`
- Ver o [gist de @sindresorhus sobre ESM](https://gist.github.com/sindresorhus/a39789f98801d908bbc7ff3ecc99d99c)

## Problemas de Uso (API)

### `options.renderer` is no longer supported

Removido no MDX v2. Use `jsxImportSource` para Preact, ou `recmaPlugins`
para injeção arbitrária.

### `format: 'detect'` errors

`createProcessor` não suporta `'detect'`. Use `compile` de `@mdx-js/mdx`.

### Classic JSX runtime warnings

Use automatic JSX runtime (padrão). Classic será removido no futuro.

### `evaluate` errors: Expected Fragment/jsx/jsxs

Framework não suporta automatic JSX runtime ou não está passando
corretamente. Ver exemplos em [`evaluate`](https://mdxjs.com/packages/mdx/#evaluatefile-options).

### `options.baseUrl` needed

Ocorre com `evaluate` ou `outputFormat: 'function-body'` quando usa
`import.meta.url`, `import` ou `export … from`. Passe `baseUrl: import.meta.url`.

## Problemas de Escrita (Sintaxe MDX)

### Categorias principais de erro

1. **Não escapar `<` e `{`** — use `\<`, `\{` para texto literal
2. **Interleaving incorreto** — ver regras de interleaving
3. **JavaScript quebrado** — verificar validade do JS

### Erros comuns de parsing

| Erro | Causa | Solução |
|------|-------|---------|
| `Could not parse import/exports with acorn` | `import`/`export` no início da linha seguido de JS inválido | Verificar sintaxe do import/export |
| `Unexpected $type in code: only import/exports` | Código após import/export | Só `import` e `export` são permitidos em ESM blocks |
| `Unexpected end of file in expression` | `{` sem fechamento | Fechar com `}` ou escapar `\{` |
| `Could not parse expression with acorn` | JS inválido dentro de `{}` | Usar expressão válida (não statement) ou IIFE |
| `Unexpected extra content in spread` | Múltiplos spreads em uma tag | Usar `{...a} {...b}` em vez de `{...a, ...b}` |
| `Unexpected closing tag` | Tag fechamento sem abertura | Verificar ordem das tags |
| `Cannot close $type: a different token is open` | Interleaving markdown/JSX incorreto | Fechar tags JSX antes de encerrar containers markdown |

### Interleaving

Markdown blocks dentro de JSX só funcionam se as tags abrem e fecham na
mesma linha (não produzem `<p>`). Em linhas separadas, produzem `<p>`.

## Relacionado

- [[references/mdx/what-is-mdx|O que é MDX?]]
- [[references/mdx/getting-started|Getting Started com MDX]]
- [[references/mdx/using-mdx|Usando MDX]]
- [[references/mdx/extending-mdx|Estendendo MDX]]
