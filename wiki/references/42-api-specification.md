---
title: 42 Intra API v2 — Specification
category: references
tags: [42, api, oauth2, reference]
sources: [_raw/42_api_raw]
summary: "Guia de uso da API Intra 42 v2: OAuth2, escopos, paginação, filtros, ordenação, rate limiting (2 req/s, 1200 req/h) e token info."
provenance:
  extracted: 0.88
  inferred: 0.10
  ambiguous: 0.02
base_confidence: 0.68
lifecycle: draft
lifecycle_changed: 2026-06-16
tier: supporting
created: "2026-06-16T00:00:00Z"
rag_score: 0.4818
updated: "2026-06-16T00:00:00Z"
---

# 42 Intra API v2 — Specification

> Base URL: `https://api.intra.42.fr/v2`
> Versão: 2.0 | Formato: JSON | Auth: OAuth 2.0 sobre HTTPS

A API 42 fornece acesso programático aos dados da intranet: perfis de usuários, projetos, campus, events, forum, e mais.

## Autenticação (OAuth 2.0)

Autenticação via [OAuth 2.0](http://oauth.net/2/). Tokens têm escopos limitados e podem ser revogados pelo usuário.

**Registro da aplicação:** https://profile.intra.42.fr/oauth/applications/new

Cada app recebe `Client ID` e `Client Secret` (mantenha o secret privado).

**Uso do token:**

- Query param: `?access_token=XXX`
- Header: `Authorization: Bearer XXX`

**Token info:** `GET https://api.intra.42.fr/oauth/token/info`

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.intra.42.fr/oauth/token/info
# {"resource_owner_id":74,"scopes":["public"],"expires_in_seconds":7174,"application":{...},"created_at":1439460680}
```

## Erros

| HTTP | Significado |
|------|-------------|
| 400 | Request malformado |
| 401 | Não autenticado |
| 403 | Proibido / Escopo insuficiente |
| 404 | Recurso não encontrado |
| 422 | Entidade não-processável |
| 500 | Erro interno do servidor |
| Connection refused | Provável causa: não usar HTTPS |

Erro 403 por escopo insuficiente retorna detalhes no header `WWW-Authenticate`:

```http
WWW-Authenticate: Bearer realm="42 API", error="insufficient scope",
  error_description="The action need the following scopes: [forum]"
```

## Scopes

App pode ter diferentes escopos de acesso. O usuário aprova os escopos no momento da autorização.

Acessar recurso com escopo errado → `403 Forbidden` com detalhes no `WWW-Authenticate`.

## Paginação

Todas as collections são paginadas com **30 itens por página** (default). Máximo: 100 por página (nem todos os endpoints).

**Parâmetros:**

- `page` + `per_page` (legado)
- `page[number]` + `page[size]` (recomendado)

**Headers de resposta:**

| Header | Conteúdo |
|--------|----------|
| `Link` | Links `first`, `prev`, `next`, `last` |
| `X-Page` | Página atual |
| `X-Per-Page` | Tamanho da página |
| `X-Total` | Total de páginas |

```
Link: <https://api.intra.42.fr/v2/users?page=2>; rel="next",
      <https://api.intra.42.fr/v2/users?page=1>; rel="first",
      <https://api.intra.42.fr/v2/users?page=42>; rel="last"
```

## Filtragem

Parâmetro `filter` com chave=valor. Múltiplos valores separados por vírgula.

```
GET /v2/users?filter[pool_year]=2013&filter[pool_month]=september,july
```

## Ordenação

Parâmetro `sort` com campos separados por vírgula. Prefixo `-` = descendente.

```
GET /v2/users?sort=kind,-login
```

## Rate Limiting

| Limite | Valor |
|--------|-------|
| Por segundo | 2 requests |
| Por hora | 1200 requests |

> Exceder os limites resulta em erros HTTP. Implemente backoff e caching. ^[inferred]

## Boas Práticas

- **Sempre use HTTPS** — HTTP é recusado (connection refused)
- **Cache agressivo** — dados mudam pouco, 1200 req/h é apertado
- **Trate paginação** — itere sobre `Link` headers, não assuma contagem fixa
- **Implemente retry com backoff** — `429 Too Many Requests` é comum em horários de pico ^[inferred]

## Ver Também

- [[references/42-api-endpoints|42 API Endpoints]] — Catálogo completo de endpoints (96 recursos, 739 endpoints)
- [[references/42-chat-sec5-api-42-rate-limits|42 Chat — Sec 5: API 42 & Rate Limits]] — Estratégia de rate limiting no 42 Chat
- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Stack do chat
- [[references/go-jwt|Go JWT]] — Biblioteca Go para tokens JWT
