---
title: What is MDX?
category: references
tags:
  - mdx
  - markdown
  - jsx
  - react
  - clippings
summary: Documentação oficial do MDX — formato que combina Markdown com JSX, permitindo usar componentes, expressões JavaScript e import/export ESM dentro de conteúdo markdown.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
---

# What is MDX?

> MDX allows you to use JSX in your markdown content. You can import components,
> such as interactive charts or alerts, and embed them within your content.

MDX é um formato que combina markdown com JSX. Exemplo:

```mdx
# Hello, world!

<div className="note">
  > Some notable things in a block quote!
</div>
```

O heading e o block quote são markdown; as tags HTML-like são JSX.

## Sintaxe MDX

### Markdown

MDX suporta markdown padrão ([CommonMark](https://commonmark.org/)): headings,
block quotes, listas, código, links, imagens, ênfase, strong, code inline.

**Limitações do markdown em MDX:**
- Código indentado **não funciona** — usar fenced code blocks
- Autolinks **não funcionam** — usar `[texto](url)`
- HTML **não funciona** — substituído por JSX (`<img>` → `<img />`)
- `<` e `{` não escapados precisam de escape: `\<` ou `\{`

### JSX

JSX é uma extensão do JavaScript que parece HTML mas permite usar componentes
reutilizáveis. MDX suporta JSX syntax:

```mdx
<h1>Heading!</h1>
<abbr title="HyperText Markup Language">HTML</abbr>
<MyComponent id="123" />
```

Componentes precisam ser definidos — importados, locais ou passados via props.

### Expressões

Expressões JavaScript dentro de chaves `{}`:

```mdx
Two 🍰 is: {Math.PI * 2}

{/* A comment! */}
```

### ESM (Import/Export)

MDX suporta `import` e `export` do JavaScript:

```mdx
import {External} from './some/place.js'
export const pi = 3.14
```

### Interleaving

Markdown inline funciona dentro de JSX se texto e tags estão na mesma linha.
Markdown blocks **não** funcionam se o par de tags abre/fecha em linhas
diferentes de blocos distintos.

## Relacionado

- [[references/mdx/getting-started|Getting Started com MDX]]
- [[references/mdx/using-mdx|Usando MDX]]
- [[references/mdx/extending-mdx|Estendendo MDX]]
- [[references/mdx/troubleshooting-mdx|Troubleshooting MDX]]
