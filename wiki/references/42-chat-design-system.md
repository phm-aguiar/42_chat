---
title: "42 Chat — Design System"
category: references
tags: [42_chat, design, frontend, css, tailwind]
sources:
  - wiki/_raw/42-chat-research.md
summary: "Sistema de design brutalista/cyberpunk para o chat da 42: paleta preto/branco com neon (amarelo #D4ED31, ciano #00E5FF, magenta #FF007A, azul #304FFE), tipografia geométrica (Montserrat/Poppins/Gotham), border-radius zero, e filtros CSS para fotos de perfil."
provenance:
  extracted: 0.90
  inferred: 0.08
  ambiguous: 0.02
base_confidence: 0.82
lifecycle: draft
lifecycle_changed: "2026-06-14"
tier: supporting
created: "2026-06-14"
updated: "2026-06-14"
---

# 42 Chat — Design System

> Estética que combina **minimalismo funcional** com elementos **cyberpunk, pop-art e tech**. Inspirada na identidade visual da 42 São Paulo (https://www.42sp.org.br/).

## Filosofia

Design como engenharia, não como arte. Sistema de regras e padrões matemáticos aplicados consistentemente via Tailwind CSS e Shadcn/ui. Zero esforço criativo — componentes importados com variáveis de cor da 42 injetadas.

## Paleta de Cores

Cores extraídas diretamente da análise visual dos materiais institucionais da 42 SP.

| Cor | Hex | Uso |
|---|---|---|
| **Fundo Principal** | `#000000` | Background do modo escuro (Dark Mode nativo) |
| **Fundo Secundário** | Cinza muito escuro | Áreas de leitura longa, listas |
| **Texto Principal** | `#FFFFFF` | Texto em fundo escuro |
| **Accent 1 (CTA/Primária)** | `#D4ED31` / `#CFFF04` | Botão principal ("CONHEÇA A 42"), contornos de destaque, botão Enviar |
| **Accent 2 (Ciano)** | `#00E5FF` | Links, nomes de usuário, títulos, bordas de balões |
| **Accent 3 (Magenta)** | `#FF007A` | Notificações, menções `@usuario`, alertas |
| **Accent 4 (Azul Royal)** | `#304FFE` | Blocos de sobreposição, fundos secundários, máscaras |

## Tipografia

### Família
Fontes *Sans-serif* geométricas, limpas e modernas. Preferência por **Montserrat**, **Poppins** ou **Gotham**.

### Hierarquia

| Nível | Peso | Estilo | Cor |
|---|---|---|---|
| **Títulos (H1-H2)** | Black / Extra-Bold | CAIXA ALTA, alinhamento à esquerda | Branco, ou misto (ex: Branco + Ciano na mesma frase) |
| **Subtítulos (H3-H4)** | Bold | Title Case | Branco ou cor de acento |
| **Corpo** | Regular / Light | Sentence case | Branco com contraste suave |

## Regras de Estilo (CSS/Tailwind)

### Bordas

```css
/* ZERO arredondamento — tudo retangular e afiado */
border-radius: 0;
```

No Tailwind: usar `rounded-none` em todos os componentes. Botões, inputs, modais, balões de mensagem — todos retangulares com cantos secos.

### Background

```css
/* Padrão de pontos (dot grid / halftone) no fundo */
background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
background-size: 20px 20px;
```

Textura hacker/tech inspirada nos materiais institucionais da 42.

### Grafismos Tech

- **Dot grids/halftones** — padrão de pontos no background
- **Estrelas/faíscas** (✨) — detalhes vetorizados em cores neon
- **Redes de nós/partículas** — mapas e gráficos decorativos

### Espaçamento

Uso generoso de margens (padding/margin). Elementos não se amontoam — o "vazio" é usado para destacar o conteúdo.

### Botões

Flat design, sem sombras. Retangulares com cantos secos (sharp). Preenchidos com Amarelo-limão (`#D4ED31`), texto preto bold.

### Tratamento de Fotos de Perfil

Fotos puxadas da API da 42. Dois níveis de tratamento:

```css
/* Nível 1: Filtro base */
.avatar {
  filter: grayscale(100%) contrast(120%);
  border: 2px solid var(--accent-2); /* Ciano ou cor de sotaque */
  background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 10px 10px;
}

/* Nível 2: Máscara de recorte (clipping mask) */
.avatar-masked {
  clip-path: polygon(/* formato geométrico ou logo "42" */);
}
```

### Iconografia

Ícones minimalistas formados por linhas finas (line-art) ou formas geométricas simples, com discretos gradientes nas cores de acento.

## Aplicação no Chat (UI Components)

### Tela Principal
- **Fundo:** Preto ou cinza muito escuro
- **Dark Mode:** Nativo por padrão, remetendo ao ambiente de terminal da 42

### Balões de Mensagem

| Tipo | Fundo | Borda | Texto |
|---|---|---|---|
| **Usuário** | Preto `#000000` | Fina Ciano `#00E5FF` ou Rosa `#FF007A` | Branco `#FFFFFF` |
| **Sistema/IA** | Cinza escuro | — | Branco `#FFFFFF` |

### Botão de Enviar
- Fundo Amarelo/Verde-limão (`#D4ED31`)
- Texto preto bold
- Flat, cantos secos

### Avatar
- Imagem em preto e branco (grayscale + alto contraste)
- Fundo com padrão pontilhado (dot grid)
- Borda sólida na cor de acento (Ciano, Rosa ou Azul)

### Títulos com Cor Mista
Títulos podem misturar duas cores na mesma frase para ênfase:
```html
<h1>
  <span class="text-white">BEM-VINDO À</span>
  <span class="text-42-cyan">42 CHAT</span>
</h1>
```

## Tailwind Config

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Montserrat', 'Poppins', 'Gotham', 'sans-serif'],
      },
      colors: {
        '42-black': '#000000',
        '42-white': '#FFFFFF',
        '42-lime': '#D4ED31',     // Amarelo/Verde-limão — CTA
        '42-cyan': '#00E5FF',      // Ciano — destaques, links
        '42-magenta': '#FF007A',   // Rosa Pink — notificações
        '42-blue': '#304FFE',      // Azul Royal — sobreposições
      },
      borderRadius: {
        'none': '0',
        'DEFAULT': '0',
      },
    },
  },
};
```

## Máscaras de Recorte (Clipping Masks)

Imagens e avatares podem ser cortados em formatos geométricos ou formando a logo "42" sobreposta a elementos coloridos. Exemplo:

```css
.clip-42 {
  clip-path: polygon(/* coordenadas da logo 42 */);
}
```

O bloco azul (`#304FFE`) sobreposto ao olho na foto de perfil é um exemplo desse padrão — combina grayscale com elemento colorido por cima.

## Ver Também

- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Stack e arquitetura
- [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — Requisitos de engenharia
- [[references/42-chat-architecture-diagram|42 Chat Architecture Diagram]] — Diagramas Mermaid
