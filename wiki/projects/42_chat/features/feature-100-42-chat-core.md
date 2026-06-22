---
title: "Feature 100 — 42 Chat Core (MVP)"
feature_id: 100
category: feature
status: implemented
tags: [42chat, core, backend, websocket, oauth2, api, go, chi]
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
summary: >-
  Núcleo do 42 Chat: servidor HTTP Go com Chi router, autenticação OAuth2 42 +
  JWT, WebSocket com modelo Hub/Client (gorilla/websocket), API REST de mensagens
  e usuários, e graceful shutdown. Feature base sobre a qual todas as demais
  features são construídas.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.0
base_confidence: 0.98
lifecycle: verified
lifecycle_changed: 2026-06-21
tier: core
---

# Feature 100 — 42 Chat Core (MVP)

## Overview

O **42 Chat Core** é o backbone do sistema de chat em tempo real para alunos
da 42. Implementa um servidor HTTP com roteador Chi, autenticação OAuth2 via
API da 42, tokens JWT para sessões, e comunicação em tempo real via WebSocket
com modelo Hub/Client. Também expõe endpoints REST para histórico de mensagens
e perfil de usuários, e inclui graceful shutdown com notificação aos clientes
conectados.

A feature está **✅ implementada** e serve como dependência fundamental para
todas as outras features do projeto (101 — Assinatura de Participação, e
futuras).

## Arquitetura

### Decisões de Design

1. **Chi Router**: Escolhido por ser idiomático Go, compatível com
   `net/http`, e oferecer middleware nativo (Logger, Recoverer, RealIP,
   RequestID).
2. **OAuth2 42 + JWT**: Autenticação via `GET /api/auth/42/callback`
   (Authorization Code flow contra a API da 42). Token JWT gerado com secret
   configurável, validado via middleware nas rotas protegidas.
3. **WebSocket Hub/Client**: Modelo clássico com mutex no mapa de clients
   e canais de saída (buffered, 256 slots). Mensagens inbound são validadas,
   persistidas e broadcast a todos os clients.
4. **Soft delete em mensagens**: Campo `deleted_at` permite recuperação;
   nunca se faz hard delete.
5. **Graceful shutdown**: Sinais SIGINT/SIGTERM disparam `Hub.Shutdown()`
   (broadcast de `system:shutdown`), espera de 500ms para entrega, e
   `http.Server.Shutdown` com timeout de 10s.
6. **Dev mode**: Quando `DEV_MODE=true`, rota `/api/auth/dev/login` permite
   login sem OAuth2 para desenvolvimento local.

### Stack

| Camada       | Tecnologia                                          |
|-------------|-----------------------------------------------------|
| Linguagem    | Go 1.21+                                            |
| Router       | `go-chi/chi/v5`                                     |
| WebSocket    | `gorilla/websocket`                                 |
| Banco        | PostgreSQL                                          |
| Auth         | OAuth2 (API 42) + JWT (HMAC-SHA256)                 |
| Middleware   | Logger, Recoverer, RealIP, RequestID, CORS custom   |

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                     main.go                              │
│  ┌─────────┐  ┌──────────┐  ┌───────────────────────┐  │
│  │ Config  │  │   Auth   │  │     Chi Router         │  │
│  │ (env)   │  │ OAuth2   │  │                        │  │
│  │         │  │ JWT      │  │  Middleware:            │  │
│  └─────────┘  └──────────┘  │  Logger, Recoverer,     │  │
│                              │  RealIP, RequestID,     │  │
│  ┌─────────┐  ┌──────────┐  │  CORS                   │  │
│  │   DB    │  │   WS     │  │                        │  │
│  │Postgres │  │  Hub     │  │  Rotas:                 │  │
│  │Queries  │  │ Handler  │  │  /api/auth/42/callback  │  │
│  └─────────┘  └──────────┘  │  /api/messages          │  │
│                              │  /api/users/{id}        │  │
│                              │  /api/users/{id}/stats  │  │
│                              │  /ws                    │  │
│                              │  /metrics               │  │
│                              └─────────────────────────┘  │
│                                                          │
│  Graceful Shutdown (SIGINT/SIGTERM)                      │
│  Hub.Shutdown() → broadcast → 500ms → srv.Shutdown(10s)  │
└─────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Config (`internal/config`)

Carrega configuração via variáveis de ambiente:

| Variável       | Descrição                           |
|---------------|-------------------------------------|
| `DATABASE_URL` | Connection string PostgreSQL        |
| `JWT_SECRET`   | Secret HMAC para assinatura JWT     |
| `PORT`         | Porta HTTP (default: 8080)          |
| `DEV_MODE`     | Habilita rota de dev login (bool)   |
| OAuth2 42     | Client ID, Client Secret, Redirect  |

### 2. Database (`internal/db`)

- **Postgres**: Pool de conexões (`database/sql` + `lib/pq`).
- **Queries**: Struct com métodos SQL para mensagens e usuários:
  - `InsertMessage(userID int, content string) (*model.Message, error)`
  - `SelectRecentMessages(before time.Time, limit int) ([]model.Message, error)`
  - `SelectUserByID(id int) (*model.User, error)`
  - `SelectUserStats(userID int)` — Feature 101

### 3. Auth (`internal/auth`)

#### OAuth2 (`auth/oauth2.go`)
- `ExchangeCode(code string)` — Troca authorization code por token 42,
  busca `/v2/me`, upsert do usuário no banco.

#### JWT (`auth/jwt.go`)
- `JWTManager` — Geração e validação de tokens HMAC-SHA256.
- `JWTMiddleware` — Middleware Chi que extrai token do header `Authorization:
  Bearer <token>`, valida, e injeta claims no contexto.
- Claims: `UserID` (int), `Login` (string).

#### Dev Login (`auth/dev_login.go`)
- `DevLoginHandler` — Gera JWT direto sem OAuth2 (apenas quando
  `DEV_MODE=true`).

### 4. WebSocket (`internal/ws`)

#### Estruturas

```go
// Client — conexão WebSocket ativa
type Client struct {
    UserID int
    Login  string
    Send   chan []byte   // buffer 256, canal de saída
    Hub    *Hub
}

// Hub — gerencia todas as conexões
type Hub struct {
    mu             sync.RWMutex
    clients        map[*Client]bool
    debounceTimers map[int]*time.Timer  // Feature 101
    debounceMu     sync.Mutex
    queries        *db.Queries
}
```

#### Operações do Hub

| Método                     | Descrição                                                    |
|---------------------------|--------------------------------------------------------------|
| `Connect(client)`         | Registra client, broadcast `system:join`                     |
| `Disconnect(client)`      | Remove client, fecha canal Send, broadcast `system:leave`    |
| `Broadcast(msg)`          | Envia WSMessage para todos os clients (RLock)                |
| `BroadcastSystem(type, login)` | Helper para mensagens de sistema                       |
| `Shutdown()`              | Broadcast `system:shutdown` para todos os clients            |
| `ConnectionCount()`       | Retorna número de conexões ativas (para /metrics)            |
| `BroadcastUserStatsChanged(userID)` | Debounce 2s + broadcast `user_stats_changed` (F101) |

#### Ciclo de Vida da Conexão

```
Client conecta → GET /ws?token=<jwt>
  ↓
Handler.ServeHTTP:
  1. Valida JWT (query param ou header Sec-WebSocket-Protocol)
  2. Upgrade HTTP → WebSocket (gorilla/websocket)
  3. Cria Client, registra no Hub (Connect)
  4. Dispara goroutines readPump + writePump
  ↓
readPump (loop):
  - Lê mensagens do WebSocket
  - Valida type="message", content não-vazio, ≤5000 bytes
  - Persiste no banco (InsertMessage)
  - Dispara BroadcastUserStatsChanged (debounce)
  - Envia broadcast enriquecido (ID, UserID, Login, Content, CreatedAt)
  ↓
writePump (loop):
  - Lê do canal Client.Send
  - Escreve no WebSocket (TextMessage)
  - Ping periódico (30s)
  ↓
Desconexão (readPump defer):
  - Hub.Disconnect(client)
  - conn.Close()
```

#### Constantes do WebSocket

| Constante       | Valor  | Descrição                          |
|----------------|--------|------------------------------------|
| `writeWait`    | 10s    | Timeout de escrita                 |
| `pongWait`     | 60s    | Timeout para receber pong          |
| `pingPeriod`   | 30s    | Intervalo de ping                  |
| `maxMessageSize` | 6144 | Tamanho máximo de mensagem (bytes) |

### 5. HTTP Server

```go
srv := &http.Server{
    Addr:         ":" + cfg.Port,
    Handler:      chiRouter,
    ReadTimeout:  10 * time.Second,
    WriteTimeout: 10 * time.Second,
    IdleTimeout:  60 * time.Second,
}
```

## Rotas API

### Rotas Públicas

| Método | Rota                       | Descrição                                  |
|--------|---------------------------|--------------------------------------------|
| GET    | `/api/auth/42/callback?code=` | OAuth2 callback — troca code por JWT  |
| GET    | `/metrics`                 | Métricas Prometheus (conexões WS, DB pool) |
| GET    | `/api/auth/dev/login`     | Dev login (apenas `DEV_MODE=true`)         |

### Rotas Autenticadas (JWT via `Authorization: Bearer <token>`)

| Método | Rota                       | Query Params              | Descrição                          |
|--------|---------------------------|---------------------------|------------------------------------|
| GET    | `/api/messages`            | `?before=<RFC3339>&limit=1-100` | Histórico paginado (cursor) |
| GET    | `/api/users/{id}`          | —                         | Perfil público do usuário          |
| GET    | `/api/users/{id}/stats`    | —                         | Estatísticas (Feature 101)         |

### WebSocket

| Método | Rota  | Auth                          | Descrição                    |
|--------|-------|-------------------------------|------------------------------|
| GET    | `/ws` | `?token=<jwt>` ou header `Sec-WebSocket-Protocol` | Conexão WebSocket |

### CORS

Middleware custom permite qualquer origem (`*`), métodos `GET, POST, OPTIONS`,
headers `Authorization, Content-Type`. Requisições `OPTIONS` retornam
`204 No Content`.

## Fluxo WebSocket

### Mensagem Inbound (cliente → servidor)

```json
{
  "type": "message",
  "content": "texto da mensagem (≤ 5000 chars)"
}
```

Validações no servidor:
- `type` deve ser `"message"`
- `content` não pode ser vazio
- `content` limitado a 5000 bytes (servidor) + 6144 bytes (raw WebSocket frame)

### Mensagem Outbound (servidor → todos os clients)

```json
{
  "type": "message",
  "id": "uuid-v4",
  "user_id": 42,
  "login": "zeca",
  "content": "texto da mensagem",
  "created_at": "2026-06-21T00:00:00Z"
}
```

### Mensagens de Sistema

```json
// Usuário entrou
{"type": "system", "login": "zeca", "content": "join"}

// Usuário saiu
{"type": "system", "login": "zeca", "content": "leave"}

// Servidor desligando
{"type": "system", "content": "shutdown"}
```

### Evento user_stats_changed (Feature 101)

```json
{
  "type": "user_stats_changed",
  "user_id": 42,
  "login": "zeca",
  "content": "{\"user_id\":42,\"total_messages\":150,\"active_rooms\":3,\"tier\":\"participante\"}"
}
```

Enviado com debounce de 2 segundos após cada mensagem postada.

## Modelo de Dados

### User (`internal/model/user.go`)

```go
type User struct {
    ID          int       `json:"id"`           // ID fixo da API 42
    Login       string    `json:"login"`        // Login intra 42
    ImageURL    string    `json:"image_url"`    // Avatar da 42
    CurrentHost string    `json:"current_host"` // Host atual (campus)
    Level       float64   `json:"level"`        // Nível 42
    CreatedAt   time.Time `json:"created_at"`
}
```

### Message (`internal/model/message.go`)

```go
type Message struct {
    ID        string     `json:"id"`          // UUID v4 (PostgreSQL)
    UserID    int        `json:"user_id"`     // FK → users.id
    Login     string     `json:"login,omitempty"`       // JOIN, não persiste
    ImageURL  string     `json:"image_url,omitempty"`   // JOIN, não persiste
    Content   string     `json:"content"`     // ≤ 5000 chars (CHECK constraint)
    CreatedAt time.Time  `json:"created_at"`
    DeletedAt *time.Time `json:"deleted_at,omitempty"` // Soft delete
}
```

Constraints no banco:
- `id` — UUID v4 gerado pelo PostgreSQL
- `content` — `CHECK (length(content) <= 5000)`
- `deleted_at` — soft delete, nunca hard delete

### WSMessage (envelope WebSocket)

```go
type WSMessage struct {
    Type      string `json:"type"`                // "message" | "system" | "user_stats_changed"
    ID        string `json:"id,omitempty"`        // UUID (outbound apenas)
    UserID    int    `json:"user_id,omitempty"`   // ID do autor (outbound)
    Login     string `json:"login,omitempty"`     // Login do autor (outbound)
    ImageURL  string `json:"image_url,omitempty"` // Avatar (outbound)
    Content   string `json:"content,omitempty"`   // Texto ou payload JSON
    Token     string `json:"token,omitempty"`     // JWT (inbound)
    CreatedAt string `json:"created_at,omitempty"` // ISO8601 (outbound)
}
```

## Fluxo de Autenticação

```
Usuário → GET /api/auth/42/callback?code=<code>
  ↓
oauth2.ExchangeCode(code):
  1. POST https://api.intra.42.fr/oauth/token → access_token
  2. GET https://api.intra.42.fr/v2/me (Bearer access_token)
  3. Upsert usuário no PostgreSQL
  4. Retorna *model.User
  ↓
jwtManager.GenerateToken(user.ID, user.Login):
  1. Cria JWT com claims {user_id, login, exp}
  2. Assina com HMAC-SHA256 (cfg.JWTSecret)
  ↓
Resposta: {"token":"<jwt>","user":{"id":42,"login":"zeca","image_url":"..."}}
  ↓
Frontend armazena JWT → usa em Authorization: Bearer <token> nas rotas protegidas
  ↓
Frontend conecta WebSocket → GET /ws?token=<jwt>
  ↓
ws.Handler valida JWT → upgrade → Client registrado no Hub
```

## Graceful Shutdown

```
SIGINT / SIGTERM
  ↓
hub.Shutdown()            → broadcast "system:shutdown" para todos os clients
  ↓
time.Sleep(500ms)         → janela para mensagens de shutdown chegarem
  ↓
srv.Shutdown(10s timeout) → drena requisições pendentes, fecha listener
  ↓
pg.Close()                → fecha pool PostgreSQL (defer no main)
```

## Arquivos Principais

| Arquivo                     | Função                                                |
|----------------------------|-------------------------------------------------------|
| `cmd/server/main.go`       | Entry point, wiring, rotas, graceful shutdown         |
| `internal/ws/hub.go`       | Hub (Connect, Disconnect, Broadcast, Shutdown)        |
| `internal/ws/handler.go`   | Upgrade HTTP→WS, readPump, writePump, ping/pong       |
| `internal/api/messages.go` | GET /api/messages com paginação por cursor            |
| `internal/api/users.go`    | GET /api/users/{id}                                   |
| `internal/model/message.go`| Model Message + WSMessage                             |
| `internal/model/user.go`   | Model User                                            |
| `internal/config/`         | Carregamento de config via env                        |
| `internal/db/`             | PostgreSQL pool + queries SQL                         |
| `internal/auth/`           | OAuth2 42, JWT manager, middleware, dev login         |

## Status

✅ **Implementado** — Feature core funcional, servindo como base para Feature
101 (Assinatura de Participação) e features futuras.

## Relacionado

- [[feature-101-assinatura-participacao]] — Feature 101, dependente desta
- Todas as futuras features dependem do Core para WebSocket, auth e API REST
