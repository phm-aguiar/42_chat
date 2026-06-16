---
name: react-implement
description: >
  Use when the agent-dev needs to implement React frontend code from a spec.
  Covers Vite + React project setup, Tailwind CSS configuration with the 42
  brutalist design system (colors, dot grid, border-radius:0), Shadcn/ui
  components (rounded-none), Zustand state management (authStore, chatStore),
  WebSocket hooks with JWT auth and reconnection backoff, and the 42 Chat
  visual identity. Trigger keywords: implementar React, React frontend, criar
  componente React, Vite React, frontend 42, Tailwind config, Shadcn, Zustand.
version: 0.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dev, react, frontend, tailwind, design-system, websocket]
    related_skills: [build-check, wiki-query]
    category: dev
    created: 2026-06-16
    resources:
      - SKILL.md
---

# react-implement — Implementar frontend React a partir de spec

> Categoria: `dev` — criada em 2026-06-16. Trilho do agent-dev para stack React.

## Propósito

Esta skill é carregada pelo agent-dev quando a task envolve implementar código
React (Vite + Tailwind + Shadcn/ui + Zustand). Ela cobre os padrões específicos
do 42 Chat definidos no spec/plan da feature 100: configuração do tema brutalista,
componentes de chat com WebSocket, stores de estado, e hooks de conexão.

Não substitui conhecimento geral de React — o agent-dev já sabe React. Esta skill
fornece as **convenções visuais e arquiteturais do projeto** para consistência.

## Pré-requisitos

- Node.js 20+ e npm instalados
- Vite + React scaffoldado no diretório `web/` (T012)
- Tailwind CSS instalado e configurado
- Shadcn/ui inicializado (`npx shadcn-ui@latest init`)
- Zustand instalado (`npm install zustand`)
- Acesso ao spec `specs/features/100-42chat-core/spec.md` (seção de frontend)
- Wiki vault com [[references/42-chat-design-system|Design System]]

## Quando usar (gatilhos)

- Task do agent-dev com stack React/frontend
- "criar componente", "configurar Tailwind", "implementar store"
- "ChatRoom", "MessageBubble", "LoginButton", "useWebSocket"
- Task que referencia arquivos `web/src/`

## Fluxo de Execução

### Passo 1: Configuração base (T012)

#### 1a. Tailwind config com cores 42

```js
// web/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "42-black":   "#000000",
        "42-white":   "#FFFFFF",
        "42-lime":    "#D4ED31",  // CTA, botão principal, bordas destaque
        "42-cyan":    "#00E5FF",  // Links, nomes, títulos, bordas balões
        "42-magenta": "#FF007A",  // Notificações, @mentions, alertas
        "42-blue":    "#304FFE",  // Sobreposições, fundos secundários
        "42-gray":    "#1A1A1A",  // Fundo secundário
      },
      fontFamily: {
        sans: ['Montserrat', 'Poppins', 'Gotham', 'sans-serif'],
      },
      borderRadius: {
        none: "0",  // nenhum componente terá arredondamento
      },
    },
  },
  plugins: [],
}
```

#### 1b. CSS global com dot grid e regras base

```css
/* web/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Dot grid background — padrão brutalista 42 */
body {
  background-color: #000000;
  background-image: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  color: #FFFFFF;
  font-family: 'Montserrat', 'Poppins', 'Gotham', sans-serif;
}

/* Títulos em CAIXA ALTA */
h1, h2 {
  text-transform: uppercase;
  font-weight: 900; /* Black */
  letter-spacing: 0.05em;
}

/* Zero border-radius global */
* {
  border-radius: 0 !important;
}
```

**Regra crítica:** `border-radius: 0` em TODOS os componentes. Shadcn/ui traz `rounded-md` por padrão — sobrescrever com `!important` no CSS global ou passar `className="rounded-none"` em cada componente.

### Passo 2: Componentes

#### 2a. App.jsx — Shell principal

```jsx
// web/src/App.jsx
import { ChatRoom } from './components/ChatRoom'
import { LoginButton } from './components/LoginButton'
import { useAuthStore } from './store/authStore'

export default function App() {
  const { user, jwt } = useAuthStore()

  if (!jwt) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-42-black">
        <LoginButton />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-42-black">
      <header className="border-b border-42-cyan p-4">
        <h1 className="text-42-cyan text-2xl">42 CHAT</h1>
        <span className="text-42-white text-sm">
          {user?.login} @ {user?.current_host || 'campus'}
        </span>
      </header>
      <ChatRoom />
    </div>
  )
}
```

#### 2b. LoginButton.jsx — Botão "Entrar com a 42"

```jsx
// web/src/components/LoginButton.jsx
export function LoginButton() {
  const handleLogin = () => {
    // Redireciona para OAuth2 42
    window.location.href = `${import.meta.env.VITE_API_URL}/api/auth/login`
  }

  return (
    <button
      onClick={handleLogin}
      className="bg-42-lime text-42-black font-bold py-4 px-8 
                 text-lg uppercase tracking-wider
                 border-2 border-42-lime hover:bg-42-black hover:text-42-lime
                 transition-colors duration-200"
    >
      Entrar com a 42
    </button>
  )
}
```

#### 2c. ChatRoom.jsx — Sala de chat com WebSocket

```jsx
// web/src/components/ChatRoom.jsx
import { useState, useEffect } from 'react'
import { MessageBubble } from './MessageBubble'
import { useChatStore } from '../store/chatStore'
import { useWebSocket } from '../hooks/useWebSocket'
import { useAuthStore } from '../store/authStore'

export function ChatRoom() {
  const [input, setInput] = useState('')
  const { messages, addMessage } = useChatStore()
  const { jwt } = useAuthStore()
  const { sendMessage, status } = useWebSocket(jwt)

  // Carregar histórico (últimas 50 mensagens)
  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/api/messages?limit=50`, {
      headers: { Authorization: `Bearer ${jwt}` }
    })
      .then(r => r.json())
      .then(data => data.forEach(addMessage))
  }, [])

  const handleSend = (e) => {
    e.preventDefault()
    if (!input.trim()) return
    sendMessage(input)
    setInput('')
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)]">
      {status === 'reconnecting' && (
        <div className="bg-42-magenta text-42-white text-center py-1 text-sm uppercase">
          Reconectando...
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
      </div>

      <form onSubmit={handleSend} className="border-t border-42-cyan p-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          maxLength={5000}
          placeholder="Digite sua mensagem..."
          className="flex-1 bg-42-gray text-42-white border border-42-cyan p-3 
                     focus:outline-none focus:border-42-lime placeholder:text-gray-500"
        />
        <button
          type="submit"
          className="bg-42-lime text-42-black font-bold px-6 uppercase 
                     hover:bg-42-cyan transition-colors"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
```

#### 2d. MessageBubble.jsx — Bolha de mensagem brutalista

```jsx
// web/src/components/MessageBubble.jsx
export function MessageBubble({ message }) {
  const isSystem = message.type === 'system'

  if (isSystem) {
    return (
      <div className="text-center text-42-magenta text-sm italic py-1">
        {message.content}
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3 py-2 group">
      {/* Avatar */}
      <div className="w-10 h-10 flex-shrink-0 border-2 border-42-cyan overflow-hidden">
        {message.user.image_url ? (
          <img
            src={message.user.image_url}
            alt={message.user.login}
            className="w-full h-full object-cover grayscale contrast-125"
            // grayscale(100%) contrast(120%) — avatar estilizado
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-42-gray text-42-cyan font-bold text-sm">
            {message.user.login.substring(0, 2).toUpperCase()}
          </div>
        )}
      </div>

      {/* Conteúdo */}
      <div>
        <span className="text-42-cyan font-bold text-sm">
          {message.user.login}
        </span>
        <span className="text-gray-500 text-xs ml-2">
          {new Date(message.created_at).toLocaleTimeString('pt-BR', { 
            hour: '2-digit', minute: '2-digit' 
          })}
        </span>
        <p className="text-42-white mt-1">{message.content}</p>
      </div>
    </div>
  )
}
```

### Passo 3: Stores Zustand

#### 3a. authStore.js

```js
// web/src/store/authStore.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      jwt: null,
      user: null, // { id, login, image_url, current_host, level }

      setAuth: (jwt, user) => set({ jwt, user }),
      clearAuth: () => set({ jwt: null, user: null }),
    }),
    {
      name: '42chat-auth', // localStorage key
    }
  )
)
```

#### 3b. chatStore.js

```js
// web/src/store/chatStore.js
import { create } from 'zustand'

export const useChatStore = create((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({
    messages: [...state.messages, msg]
  })),
  setMessages: (msgs) => set({ messages: msgs }),
}))
```

### Passo 4: Hook useWebSocket

```js
// web/src/hooks/useWebSocket.js
import { useEffect, useRef, useCallback, useState } from 'react'
import { useChatStore } from '../store/chatStore'
import { useAuthStore } from '../store/authStore'

export function useWebSocket(jwt) {
  const wsRef = useRef(null)
  const [status, setStatus] = useState('connecting') // connecting | connected | reconnecting
  const { addMessage } = useChatStore()
  const { clearAuth } = useAuthStore()
  const reconnectAttempt = useRef(0)
  const maxReconnectDelay = 30000 // 30s max

  const connect = useCallback(() => {
    if (!jwt) return

    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8080'}/ws?token=${jwt}`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setStatus('connected')
      reconnectAttempt.current = 0
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'message' || data.type === 'system') {
        addMessage(data)
      }
    }

    ws.onclose = (event) => {
      if (event.code === 4001) {
        // JWT inválido → redirecionar para login
        clearAuth()
        return
      }

      // Reconexão com backoff exponencial
      setStatus('reconnecting')
      const delay = Math.min(1000 * 2 ** reconnectAttempt.current, maxReconnectDelay)
      reconnectAttempt.current++
      setTimeout(connect, delay)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [jwt])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [connect])

  const sendMessage = useCallback((content) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'message', content }))
    }
  }, [])

  return { sendMessage, status }
}
```

**Regras da reconexão:**
- Backoff exponencial: 1s → 2s → 4s → 8s → ... → max 30s
- JWT inválido (close code 4001): não reconectar, redirecionar para login
- Exibir indicador "Reconectando..." no topo da sala

### Passo 5: Contrato WebSocket

#### Mensagem cliente → servidor
```json
{"type": "message", "content": "texto da mensagem"}
```

#### Mensagem servidor → cliente (chat)
```json
{
  "type": "message",
  "id": "uuid",
  "user": {"login": "marvin", "image_url": "https://..."},
  "content": "texto",
  "created_at": "2026-06-16T14:30:00Z"
}
```

#### Mensagem servidor → cliente (sistema)
```json
{"type": "system", "content": "marvin entrou na sala"}
```

### Passo 6: Vite config

```js
// web/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8080',
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
})
```

## Guardrails

- **border-radius: 0 em tudo**: Shadcn/ui componentes vêm com `rounded-md`. Sobrescrever com `!important` no CSS global ou `rounded-none` em cada instância.
- **Cores exatas do design system**: nunca invente cores. Use as classes `42-*` definidas no Tailwind config: `42-lime`, `42-cyan`, `42-magenta`, `42-blue`.
- **Tipografia CAIXA ALTA em títulos**: H1 e H2 são sempre uppercase com Black/Extra-Bold.
- **Dot grid background**: o CSS do `index.css` deve incluir `radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)` com `background-size: 20px 20px`.
- **Avatar em grayscale**: `filter: grayscale(100%) contrast(120%)` nas fotos de perfil da 42.
- **JWT no WebSocket**: token vai como query param `?token=<JWT>`. O hook `useWebSocket` gerencia isso.
- **Reconexão**: backoff exponencial com max 30s. Sempre tratar close code 4001 como "token inválido" (redirecionar login).
- **Stores Zustand**: `authStore` usa `persist` (localStorage). `chatStore` é volátil (reseta ao recarregar).
- **API URL via env var**: `VITE_API_URL` e `VITE_WS_URL` no `.env`. Nunca hardcode URLs.
- **5000 char limit**: o input de mensagem tem `maxLength={5000}`. Mesmo limite do CHECK constraint no PostgreSQL.

## Referências

- [[references/42-chat-design-system|42 Chat Design System]] — Paleta, tipografia, regras CSS/Tailwind
- [[references/42-chat-platform-architecture|Platform Architecture]] — Stack frontend e arquitetura microfrontends
- [[references/42-chat-architecture-diagram|Architecture Diagram]] — Fluxo de autenticação e WebSocket

## Verificação

- [ ] `npm run build` compila sem erros
- [ ] Tailwind config inclui todas as cores `42-*` (#000000, #FFFFFF, #D4ED31, #00E5FF, #FF007A, #304FFE)
- [ ] CSS global tem `border-radius: 0 !important` + dot grid background
- [ ] `authStore` persiste JWT em localStorage (via `zustand/middleware/persist`)
- [ ] `useWebSocket` tem reconexão com backoff exponencial e trata close code 4001
- [ ] `LoginButton` redireciona para `/api/auth/login` (OAuth2 42)
- [ ] `ChatRoom` carrega histórico REST antes de conectar WebSocket
- [ ] `MessageBubble` renderiza avatar com `grayscale contrast-125` e fallback de iniciais
- [ ] `vite.config.js` tem proxy para `/api` e `/ws` (dev mode)
