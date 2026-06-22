---
title: "JWT (JSON Web Token)"
tags: [entity, glossary]
aliases: [auth.JWTManager, token JWT, JSON Web Token, HS256]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: JWTManager gerencia a geração e validação de tokens JWT internos do 42 Chat — algoritmo HS256, expiração de 12 horas, claims com UserID e Login do usuário autenticado.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# JWT (JSON Web Token)

## Definição

**JWT** (JSON Web Token) é o mecanismo de autenticação interna do 42 Chat. O `JWTManager` (pacote `auth`) gera tokens assinados com **HMAC-SHA256 (HS256)** e expiração de **12 horas**. Cada token carrega claims customizadas com `UserID` e `Login` do usuário, mais os claims padrão `iss` (issuer: `"42chat"`), `iat` (issued at) e `exp` (expiration).

## No Projeto

### Geração

O token é gerado após autenticação bem-sucedida via [`OAuth2`](oauth2.md) (callback `/api/auth/42/callback`):

```go
// cmd/server/main.go — callback OAuth2
user, err := oauth2.ExchangeCode(code)
token, err := jwtManager.GenerateToken(user.ID, user.Login)
// Retorna JSON: {"token": "...", "user": {"id":..., "login":..., "image_url":...}}
```

O frontend armazena o token e o envia em requests subsequentes:

- **HTTP**: header `Authorization: Bearer <token>` → validado pelo middleware `JWTMiddleware`.
- **WebSocket**: query param `?token=<jwt>` ou header `Sec-WebSocket-Protocol` → validado no `Handler.ServeHTTP` antes do upgrade.

### Validação

O `ValidateToken` usa `jwt.ParseWithClaims` com verificação de algoritmo (`SigningMethodHMAC`) para prevenir ataques de algorithm confusion:

```go
func (m *JWTManager) ValidateToken(tokenStr string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenStr, &Claims{},
        func(t *jwt.Token) (interface{}, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("método de assinatura inesperado: %v", t.Header["alg"])
            }
            return m.secret, nil
        })
    // ...
}
```

### Claims

| Claim | JSON | Descrição |
|-------|------|-----------|
| `iss` | `"iss"` | Issuer fixo: `"42chat"` |
| `iat` | `"iat"` | Timestamp de emissão (UTC) |
| `exp` | `"exp"` | Expiração: `iat + 12h` |
| `user_id` | `"user_id"` | ID do usuário na API 42 |
| `login` | `"login"` | Login do usuário |

### Middleware

O `JWTMiddleware` (em [`internal/auth/middleware.go`](../../internal/auth/middleware.go)) extrai o token do header `Authorization`, valida, e injeta `UserID` e `Login` no contexto da request. Rotas autenticadas (`/api/messages`, `/api/users/*`) são protegidas por esse middleware via `chi.Group`.

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/auth/jwt.go`](../../internal/auth/jwt.go) | JWTManager: GenerateToken e ValidateToken (63 linhas) |
| [`internal/auth/jwt_test.go`](../../internal/auth/jwt_test.go) | Testes unitários de geração e validação |
| [`internal/auth/middleware.go`](../../internal/auth/middleware.go) | Middleware HTTP que valida JWT nas requests |

## Relacionado

- [[oauth2]] — Fluxo que antecede a geração do JWT
- [[user]] — Dados embutidos nas claims do token
- [[client]] — Client WebSocket autenticado via JWT
- [[chi]] — Router onde o middleware JWT é aplicado
