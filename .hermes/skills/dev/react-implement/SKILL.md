---
name: react-implement
description: >
  Use when implementing React frontend code. Covers Vite + React, Tailwind 42 brutalist
  design system, Shadcn/ui, Zustand, WebSocket hooks with JWT auth and reconnection,
  and common pitfalls (WebSocket render cascade, inline handler accumulation).
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [React, Vite, Tailwind, Shadcn, Zustand, WebSocket, Frontend]
    related_skills: [go-implement, build-check]
    category: dev
    resources:
      - SKILL.md
      - references/websocket-cascade-pitfall.md
---

# React Frontend Implementation

Covers the 42 Chat frontend stack: Vite + React + Tailwind + Shadcn/ui + Zustand.
Includes the 42 brutalist design system and WebSocket integration patterns.

## Stack

- Vite + React 18 + TypeScript
- Tailwind CSS v4 com tema brutalista 42
- Shadcn/ui (rounded-none, cores exatas 42)
- Zustand para estado (authStore, chatStore)
- WebSocket nativo com JWT auth + reconexão com backoff

## Pitfalls

### WebSocket Render Cascade (CRÍTICO)

**Sintoma:** servidor registra centenas de `[ws] client conectado` em segundos.

**Causa:** chamar `connect()` no corpo do render em vez de `useEffect`. Cada re-render
durante `CONNECTING` cria novo WebSocket, orfanando o anterior. `onclose` do órfão
dispara state update → re-render → mais um `connect()` → cascata.

**Correção:** ver `references/websocket-cascade-pitfall.md` — usar guard `connecting`
+ verificar `readyState === CONNECTING`, não só `OPEN`.

**Padrão canônico:** mover criação do WebSocket para `useEffect` com cleanup no return.

### Inline Handlers no JSX

`onOpen={() => setConnected(true)}` gera nova referência a cada render. Sets de
handlers deduplicam por referência — ineficaz com closures frescas. Prefira
`useCallback` ou aceite o acúmulo (os Sets são limpados no cleanup).

## Design System 42

- Cores: Preto #000000, Branco #FFFFFF, Lime #D4ED31, Ciano #00E5FF, Magenta #FF007A
- Tipografia: Montserrat/Poppins, títulos Black/Extra-Bold em CAIXA ALTA
- border-radius: 0 em todos os componentes
- Dot grid background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)
- Avatar: grayscale(100%) contrast(120%), borda 2px cor de acento

## Verificação

- [ ] `npx tsc --noEmit` passa sem erros
- [ ] `npm run build` compila sem warnings
- [ ] WebSocket conecta uma única vez (verificar Network tab)
- [ ] Tema brutalista aplicado: cores exatas, dot grid, border-radius 0
