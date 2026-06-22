---
title: "OAuth2 (Autenticação 42)"
tags: [entity, glossary]
aliases: [auth.OAuth2, OAuth 2.0, 42 OAuth, authorization code flow]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: OAuth2 implementa o fluxo authorization code da API 42 — troca o código de autorização por access_token, busca dados do usuário em /v2/me e faz upsert no PostgreSQL.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# OAuth2 (Autenticação 42)

## Definição

**OAuth2** é o handler de autenticação que implementa o fluxo **authorization code** da [API 42](https://api.intra.42.fr). O componente (`auth.OAuth2`) gerencia a troca do código de autorização (recebido via query param `?code=...`) por um `access_token`, busca os dados do usuário autenticado em `/v2/me`, converte para o modelo [`User`](user.md) e faz upsert no PostgreSQL.

## No Projeto

### Fluxo completo

```
Frontend (localhost:5173)               42 Chat Server                   API 42 (api.intra.42.fr)
       |                                      |                                |
       |-- GET /authorize?client_id=... ----->|                                |
       |                                      |-- redirect ------------------>|
       |       (usuário faz login na 42)      |                                |
       |<-------- redirect com ?code= ------|                                |
       |                                      |                                |
       |-- GET /api/auth/42/callback?code= -->|                                |
       |                                      |-- POST /oauth/token --------->|
       |                                      |   (code → access_token)       |
       |                                      |<-- {access_token} ------------|
       |                                      |                                |
       |                                      |-- GET /v2/me ---------------->|
       |                                      |   (Authorization: Bearer)     |
       |                                      |<-- {id, login, image_url...} -|
       |                                      |                                |
       |                                      |-- UpsertUser(user) -> PostgreSQL
       |                                      |-- GenerateToken(user) -> JWT  |
       |                                      |                                |
       |<-- {"token":"...", "user":{...}} ---|                                |
```

### ExchangeCode — Etapas

1. **fetchToken**: `POST {FORTYTWO_API_URL}/oauth/token` com `grant_type=authorization_code`, `client_id`, `client_secret`, `code`, `redirect_uri`.
2. **fetchUser**: `GET {FORTYTWO_API_URL}/v2/me` com header `Authorization: Bearer {access_token}`.
3. **Upsert**: Converte `userResponse` em `model.User` e chama `queries.UpsertUser(user)`.

### Configuração

As credenciais vêm de variáveis de ambiente (carregadas via `config.Load()`):

| Variável | Fallback | Descrição |
|----------|----------|-----------|
| `FORTYTWO_CLIENT_ID` | `""` | Client ID registrado na API 42 |
| `FORTYTWO_CLIENT_SECRET` | `""` | Client Secret |
| `FORTYTWO_REDIRECT_URI` | `http://localhost:5173` | URI de callback após login |
| `FORTYTWO_API_URL` | `https://api.intra.42.fr` | Base URL da API 42 |

### Modo Dev

Quando `DEV_MODE=true`, o endpoint `/api/auth/dev/login` contorna o fluxo OAuth2, permitindo login com um usuário fixo (`DEV_USER`, default `"marvin"`) para desenvolvimento local sem acesso à API 42.

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/auth/oauth.go`](../../internal/auth/oauth.go) | Implementação do fluxo OAuth2 (144 linhas) |
| [`internal/auth/dev_login.go`](../../internal/auth/dev_login.go) | Bypass de OAuth2 para dev local |
| [`cmd/server/main.go`](../../cmd/server/main.go) | Callback `/api/auth/42/callback` |

## Relacionado

- [[user]] — Modelo populado pelo ExchangeCode
- [[jwt]] — Token gerado após autenticação OAuth2 bem-sucedida
- [[chi]] — Roteador que expõe o endpoint de callback
- [[client]] — Resultado do fluxo
- [[hub]] — Destino após auth
- [[websocket]] — Upgrade após token
