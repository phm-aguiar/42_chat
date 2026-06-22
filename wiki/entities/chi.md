---
title: "Chi (HTTP Router)"
tags: [entity, glossary]
aliases: [go-chi, chi/v5, router, HTTP router]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: Chi é o roteador HTTP Go usado no 42 Chat — roteamento idiomático com middleware stacking, grupos de rotas autenticadas, e compatibilidade total com net/http.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# Chi (HTTP Router)

## Definição

**[Chi](https://github.com/go-chi/chi)** (`github.com/go-chi/chi/v5` v5.3.0) é um roteador HTTP leve, idiomático e composable para Go, 100% compatível com `net/http`. No 42 Chat, o Chi é o router principal do servidor — gerencia middleware global, grupos de rotas autenticadas, e o endpoint WebSocket.

## No Projeto

### Inicialização

Em [`cmd/server/main.go`](../../cmd/server/main.go), o router é criado e configurado com middleware global:

```go
r := chi.NewRouter()

r.Use(middleware.Logger)      // Log de todas as requests
r.Use(middleware.Recoverer)   // Recovery de panics
r.Use(middleware.RealIP)      // Extrai IP real (atrás de proxy)
r.Use(middleware.RequestID)   // Gera X-Request-Id
r.Use(corsMiddleware)         // CORS para dev local
```

### Estrutura de rotas

| Rota | Auth | Descrição |
|------|------|-----------|
| `GET /api/auth/42/callback` | pública | Callback OAuth2 — troca `?code=` por JWT |
| `GET /metrics` | pública | Métricas do servidor (conexões, DB stats) |
| `GET /api/auth/dev/login` | pública (dev) | Bypass OAuth2 — só com `DEV_MODE=true` |
| `GET /ws` | JWT (query) | Upgrade WebSocket |
| `GET /api/messages` | JWT (header) | Listar mensagens |
| `GET /api/users/{id}/stats` | JWT (header) | Estatísticas do usuário |
| `GET /api/users/{id}` | JWT (header) | Dados do usuário |

### Middleware de autenticação

Rotas autenticadas usam `chi.Group` com `auth.JWTMiddleware`:

```go
r.Group(func(r chi.Router) {
    r.Use(auth.JWTMiddleware(jwtManager))
    r.Get("/api/messages", messagesHandler.ServeHTTP)
    r.Get("/api/users/{id}/stats", statsHandler.ServeHTTP)
    r.Get("/api/users/{id}", usersHandler.ServeHTTP)
})
```

O middleware extrai o [`JWT`](jwt.md) do header `Authorization: Bearer <token>`, valida, e injeta `UserID` e `Login` no `context.Context`. Rotas sem o grupo não são afetadas.

### Por que Chi?

| Característica | Benefício no 42 Chat |
|---------------|---------------------|
| 100% `net/http` | Handlers padrão, sem adaptadores |
| Middleware stacking | Logger, Recoverer, RealIP, RequestID, CORS, JWT — composto limpo |
| `chi.Group` | Rotas autenticadas vs públicas com separação clara |
| `chi.URLParam` | Parâmetros de rota como `{id}` em `/api/users/{id}` |
| Leve (~1000 LOC) | Sem overhead de framework pesado |

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`cmd/server/main.go`](../../cmd/server/main.go) | Inicialização do router Chi com todas as rotas |
| [`internal/auth/middleware.go`](../../internal/auth/middleware.go) | Middleware JWT aplicado via chi.Group |

## Relacionado

- [[websocket]] — Rota `/ws` servida pelo Chi
- [[jwt]] — Middleware de autenticação aplicado nos grupos
- [[oauth2]] — Callback `/api/auth/42/callback` registrado no router
- [[client]] — Servido via WS upgrade
- [[hub]] — Rotas levam ao hub
- [[user]] — Contexto de usuário
