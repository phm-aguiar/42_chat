---
title: "OAuth2 × JWT"
category: synthesis
tags: [oauth2, jwt, auth, security, synthesis]
sources:
  - "entities/oauth2.md"
  - "entities/jwt.md"
  - "references/auth-integration.md"
  - "references/42-oauth2-flow.md"
  - "references/oauth2-42-pitfalls.md"
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
summary: "A dupla de autenticação do 42 Chat: OAuth2 externo (API 42) para identidade e JWT interno para sessão. Duas camadas com responsabilidades distintas que, juntas, formam a espinha dorsal de segurança do sistema."
provenance:
  extracted: 0.35
  inferred: 0.60
  ambiguous: 0.05
base_confidence: 0.68
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: core
---

# OAuth2 × JWT

## The Connection

OAuth2 e JWT são frequentemente confundidos — "OAuth2 usa JWT", "JWT é OAuth2". No 42 Chat, a
separação de responsabilidades é cristalina: **OAuth2 é o protocolo de delegação de identidade
externa (API 42) e JWT é o mecanismo de sessão interna (42 Chat).** ^[extracted]

O OAuth2 resolve "quem é você?" perguntando à API 42. O JWT resolve "você ainda é você?"
em cada request subsequente sem precisar perguntar de novo. O OAuth2 access token da 42 vive
segundos (só o suficiente para chamar `/v2/me`). O JWT interno vive 12 horas. ^[extracted]

## Onde se Encontram

A transição OAuth2 → JWT acontece em um único ponto: o callback `/api/auth/42/callback`.

```
OAuth2 (externo)                    JWT (interno)
     │                                   │
     ├─ POST /oauth/token                │
     │  (code → access_token 42)         │
     ├─ GET /v2/me                       │
     │  (user profile)                   │
     ├─ UpsertUser(user) ────────────────┤
     │                                   ├─ GenerateToken(userID, login)
     │                                   │  HS256, 12h exp, claims custom
     │                                   ├─ Authorization: Bearer <jwt>
     │                                   │  (HTTP requests)
     │                                   ├─ ?token=<jwt>
     │                                   │  (WebSocket upgrade)
     │                                   ├─ JWTMiddleware → context
     │                                   │  (UserID + Login injetados)
```

## Cross-cutting Insight

A separação OAuth2↔JWT cria uma propriedade arquitetural poderosa: **independência do IDP**.
Se a 42 mudar seu protocolo OAuth2, adicionar PKCE, ou migrar para OIDC, apenas o `ExchangeCode`
precisa mudar. O resto do sistema — middleware, WebSocket, queries — só conhece JWT. ^[inferred]

Essa mesma separação permite o **modo dev** (`DEV_MODE=true`): o endpoint `/api/auth/dev/login`
injeta um JWT sem passar pelo OAuth2, mas todo o resto do sistema funciona identicamente — o
middleware não sabe (nem precisa saber) se o JWT veio do fluxo OAuth2 real ou do bypass dev. ^[extracted]

**Padrão: "Identity Façade"**

O `oauth2.ExchangeCode` é um façade que traduz identidade externa (42) para identidade interna
(JWT). Esse padrão permite:

1. **Mock de identidade em testes** — gere um JWT direto, sem mockar OAuth2.
2. **Múltiplos IDPs no futuro** — GitHub OAuth, Google OAuth, cada um com seu façade.
3. **Rotação de credenciais**: o `JWT_SECRET` pode rotacionar sem afetar o fluxo OAuth2.
   Clientes com tokens antigos são rejeitados, mas o fluxo de login permanece idêntico.

## Tensions and Trade-offs

- **12h de expiração é longo**: Um token JWT roubado é válido por 12 horas. Não há refresh token,
  não há revogação no servidor. O trade-off é simplicidade operacional (sem Redis, sem blacklist).
  Em produção multi-tenant, considere JWTs de 1h com refresh token. ^[inferred]
- **HS256 vs RS256**: HS256 usa secret simétrico — o mesmo secret assina e valida. RS256 (asymmetric)
  permitiria que outros serviços validassem tokens sem conhecer o secret, mas adiciona complexidade
  de key management. Para um monolito como o 42 Chat, HS256 é suficiente. ^[ambiguous]
- **Token em query param**: Para WebSocket, o JWT vai como `?token=...` na URL. Isso é menos seguro
  que header (HTTP) porque URLs podem ser logadas. O trade-off é que o WebSocket API do browser não
  permite headers customizados no handshake. A mitigação: `Sec-WebSocket-Protocol` como alternativa,
  já implementada no `ws.Handler`. ^[extracted]
- **Algorithm confusion**: O `ValidateToken` verifica `SigningMethodHMAC` explicitamente, prevenindo
  ataques onde um atacante envia um token assinado com `alg: none`. Essa defesa é crítica quando o
  JWT_SECRET é configurável (ex: `change-me-in-production-please`). ^[extracted]

## Open Questions

- Como implementar refresh token sem adicionar Redis? (JWT de curta duração + cookie httpOnly com refresh?)
- O algoritmo HS256 é adequado para produção ou devemos migrar para RS256/Ed25519?
- Como lidar com revogação de token em caso de comprometimento de conta?
- O bypass dev (`DEV_MODE=true`) deveria ter um warning explícito no log de startup?

## Related

- [[oauth2]] — Fluxo OAuth2 com API 42
- [[jwt]] — JWT Manager interno
- [[entities/user|User]] — Modelo populado pelo OAuth2, carregado nas claims JWT
- [[entities/chi|Chi]] — Router onde o middleware JWT é aplicado
- [[entities/websocket|WebSocket]] — Upgrade autenticado via JWT
- [[references/auth-integration|Auth Integration]] — Arquitetura das 3 camadas
- [[references/42-oauth2-flow|42 OAuth2 Flow]] — Fluxo específico da API 42
- [[references/oauth2-42-pitfalls|OAuth2 42 Pitfalls]] — Armadilhas comuns
