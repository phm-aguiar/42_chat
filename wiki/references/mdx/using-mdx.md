---
title: Usando MDX
category: references
tags:
  - mdx
  - components
  - props
  - provider
  - layout
summary: Documentação oficial sobre como usar arquivos MDX — passar props, componentes, layouts e usar o MDXProvider para context-based component passing.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
---

# Usando MDX

> Como usar arquivos MDX no seu projeto: passar props, importar/definir/passar
> componentes e usar layouts.

## Como MDX Funciona

MDX é compilado para JavaScript. Um arquivo `example.mdx`:

```mdx
export function Thing() {
  return <>World</>
}

# Hello <Thing />
```

É transformado em JS que exporta um componente `MDXContent`.

## Props

Dados podem ser passados como props para `MDXContent`:

```mdx
# Hello {props.name.toUpperCase()}
The current year is {props.year}
```

Uso em React:

```jsx
<Example name="Mars" year={2022} />
```

## Components

O prop especial `components` mapeia nomes de componentes HTML ou customizados:

```jsx
<Example components={{
  h1: 'h2',                              // # heading → <h2>
  em(props) { return <i style={{color: 'goldenrod'}} {...props} /> },
  wrapper({components, ...rest}) { return <main {...rest} /> },
  Planet() { return 'Neptune' },
}} />
```

**Chaves suportadas em `components`:**
- HTML equivalents: `h1`, `p`, `a`, `em`, `strong`, `code`, `pre`, `blockquote`,
  `ol`, `ul`, `li`, `table`, `thead`, `tbody`, `tr`, `th`, `td`, `img`
- `wrapper` — define o layout
- Qualquer identificador JSX válido: `Foo`, `custom-element`, `_`, `$x`

### Regras para nomes JSX

- Se tem ponto: member expression (`<a.b>` → lookup `a.b`)
- Se não é identifier válido: literal (`<a-b>` → tag literal)
- Se começa com minúscula: literal (`<a>` → `<a>`)
- Se começa com maiúscula: referência (`<A>` → lookup componente)

## Layout

Definido via default export no próprio MDX:

```mdx
export default function Layout({children}) {
  return <main>{children}</main>
}
All the things.
```

Ou importado e re-exportado: `export {Layout as default} from './components.js'`

## MDXProvider

Para evitar passar `components` manualmente em MDX aninhados, use contexto:

1. Instale `@mdx-js/react` (ou preact/vue)
2. Configure `providerImportSource: '@mdx-js/react'`
3. Use `MDXProvider`:

```jsx
<MDXProvider components={components}>
  <Post />
</MDXProvider>
```

Providers aninhados fazem merge. Para merge customizado, passe função.

## Relacionado

- [[references/mdx/what-is-mdx|O que é MDX?]]
- [[references/mdx/getting-started|Getting Started com MDX]]
- [[references/mdx/extending-mdx|Estendendo MDX]]
- [[references/mdx/troubleshooting-mdx|Troubleshooting MDX]]
