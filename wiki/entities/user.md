---
title: "User (Modelo de Usuário)"
tags: [entity, glossary]
aliases: [model.User, usuário, 42 user, aluno 42]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: User é o modelo de dados de um aluno da 42 autenticado no chat — ID fixo da API 42, login único, dados de perfil (image_url, host, level) sincronizados via OAuth2 e upserted no PostgreSQL.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# User (Modelo de Usuário)

## Definição

**User** é o modelo de dados que representa um aluno da 42 autenticado no 42 Chat. O `ID` é um inteiro fixo proveniente da **API 42** (não é auto-incremento local). O login é único por usuário. Dados de perfil como `ImageURL` (foto), `CurrentHost` (localização) e `Level` (nível na 42) são sincronizados durante o fluxo [`OAuth2`](oauth2.md) e persistidos via `UpsertUser`.

## No Projeto

### Criação/Atualização (Upsert)

O User é criado ou atualizado durante o callback OAuth2 em [`cmd/server/main.go`](../../cmd/server/main.go):

```go
user, err := oauth2.ExchangeCode(code)
// ExchangeCode internamente:
//   1. Troca code por access_token (POST /oauth/token)
//   2. Busca /v2/me com o token
//   3. Converte resposta da API para model.User
//   4. Chama queries.UpsertUser(user)
```

O `UpsertUser` usa `INSERT ... ON CONFLICT (id) DO UPDATE` — se o usuário já existe (mesmo ID da 42), atualiza `login`, `image_url`, `current_host` e `level`; se não existe, insere.

### Dados sincronizados

| Campo | Fonte | Descrição |
|-------|-------|-----------|
| ID | `/v2/me` → `id` | ID fixo do aluno na intra.42.fr |
| Login | `/v2/me` → `login` | Login único (ex: `zeenyt__`) |
| ImageURL | `/v2/me` → `image_url` | URL da foto de perfil |
| CurrentHost | `/v2/me` → `location` | Host atual (pode ser null) |
| Level | `/v2/me` → `level` | Nível do aluno (float) |
| CreatedAt | `time.Now().UTC()` | Timestamp do primeiro upsert |

### Login único

O login é tratado como identificador único no protocolo — usado como chave de exibição em mensagens, broadcasts de sistema (join/leave) e no [`Client`](client.md) WebSocket. Não há suporte para múltiplos logins por ID.

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/model/user.go`](../../internal/model/user.go) | Definição da struct User (14 linhas) |
| [`internal/auth/oauth.go`](../../internal/auth/oauth.go) | Lógica de ExchangeCode que popula User |
| [`internal/db/queries.go`](../../internal/db/queries.go) | UpsertUser e queries relacionadas |

## Relacionado

- [[oauth2]] — Fluxo que sincroniza dados do usuário da API 42
- [[jwt]] — Token gerado com UserID e Login após autenticação
- [[message]] — Mensagens associadas ao UserID do autor
- [[client]] — Client WebSocket identificado por UserID e Login
