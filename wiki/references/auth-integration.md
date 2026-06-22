---
title: "Integração de Auth — JWT + Chi + WebSocket"
tags: [auth, jwt, chi, websocket, integration]
created: 2026-06-21
rag_score: 0.5
category: references
summary: Arquitetura de autenticação do 42 Chat em 3 camadas — OAuth2 42 → JWT interno → WebSocket upgrade. Middleware Chi, claims, contexto e fluxo ponta a ponta.
provenance:
  extracted: 0.97
  inferred: 0.03
  ambiguous: 0.00
---

# Integração de Auth — JWT + Chi + WebSocket

Referência da arquitetura de autenticação do 42 Chat — como as três camadas (OAuth2 42, JWT interno, WebSocket) se conectam e como o token trafega do login até a conexão persistente.

---

## Arquitetura de Auth — 3 Camadas

```
┌─────────────────────────────────────────────────────────┐
│                   CAMADA 1: OAuth2 42                    │
│  POST /oauth/token  →  GET /v2/me  →  Upsert User       │
│  (code → access_token → perfil 42 → model.User)          │
├─────────────────────────────────────────────────────────┤
│                   CAMADA 2: JWT Interno                  │
│  HS256, 12h expiry, claims: {user_id, login}             │
│  Embutido em: Authorization header + WS query param      │
├─────────────────────────────────────────────────────────┤
│                   CAMADA 3: WebSocket                    │
│  Upgrade com token → Client{UserID, Login} → Hub         │
│  readPump / writePump goroutines com ping/pong            │
└─────────────────────────────────────────────────────────┘
```

O fluxo completo: **OAuth2 42 autentica o usuário real → servidor emite JWT interno → JWT é usado para autenticar requisições HTTP (REST) e upgrade WebSocket.**

---

## Camada 1: OAuth2 → JWT (Orquestração)

A transição da camada 1 para a 2 ocorre no callback `/api/auth/42/callback` (`cmd/server/main.go:67-94`):

```go
user, err := oauth2.ExchangeCode(code)       // Camada 1: OAuth2
token, err := jwtManager.GenerateToken(       // Camada 2: JWT
    user.ID, user.Login)
```

O JWT é gerado **imediatamente** após o upsert do usuário. O access token da 42 é descartado — daqui em diante, apenas o JWT interno importa.

### Inicialização no `main.go`

```go
oauth2     := auth.NewOAuth2(cfg, queries)       // Camada 1
jwtManager := auth.NewJWTManager(cfg.JWTSecret)   // Camada 2
wsHandler  := ws.NewHandler(hub, jwtManager, queries) // Camada 3
```

As três camadas são injetadas via constructor — sem globais, sem singletons.

---

## Camada 2: JWT — Criação e Validação

### Estrutura (`internal/auth/jwt.go`)

```go
type JWTManager struct {
    secret []byte
}

type Claims struct {
    jwt.RegisteredClaims
    UserID int    `json:"user_id"`
    Login  string `json:"login"`
}
```

### Algoritmo e Expiração

| Propriedade | Valor |
|---|---|
| Algoritmo | **HS256** (HMAC-SHA256) |
| Secret | `JWT_SECRET` env var (default dev: `"dev-secret-change-in-production"`) |
| Expiração | **12 horas** (`now.Add(12 * time.Hour)`) |
| Issuer | `"42chat"` |

```go
func (m *JWTManager) GenerateToken(userID int, login string) (string, error) {
    now := time.Now().UTC()
    claims := Claims{
        RegisteredClaims: jwt.RegisteredClaims{
            IssuedAt:  jwt.NewNumericDate(now),
            ExpiresAt: jwt.NewNumericDate(now.Add(12 * time.Hour)),
            Issuer:    "42chat",
        },
        UserID: userID,
        Login:  login,
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(m.secret)
}
```

### Validação

A validação (`ValidateToken`) faz três verificações:

1. **Assinatura válida** — verifica o HMAC com o secret
2. **Algoritmo HMAC** — rejeita tokens assinados com RSA, ECDSA, etc.
3. **Claims válidas** — expiração, issuer (feito pela biblioteca `golang-jwt/jwt/v5` automaticamente com `ParseWithClaims`)

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
    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, fmt.Errorf("token inválido")
    }
    return claims, nil
}
```

A proteção contra algorithm confusion (tentar usar `alg: none` ou RSA com chave pública conhecida) é explícita: apenas `SigningMethodHMAC` é aceito, e a chave de verificação é sempre o secret do servidor.

### Testes de Validação (`internal/auth/jwt_test.go`)

| Teste | O que cobre |
|---|---|
| `TestJWT_GenerateAndValidate` | Round-trip: gera token, valida, confere claims |
| `TestJWT_Expiration` | Expiração ~12h (delta tolerado: 11h-13h) |
| `TestJWT_InvalidToken` | Token assinado com chave diferente → erro |
| `TestJWT_WrongAlgorithm` | Token RS256 validado como HS256 → erro |
| `TestJWT_MalformedToken` | String `"not.a.jwt"` → erro |

---

## JWT Claims & Context

### Transporte das Claims

O middleware injeta as claims no `context.Context` da request usando uma chave privada:

```go
type contextKey string

const ClaimsKey contextKey = "claims"
```

Isso evita colisões com outras chaves de contexto (não é uma string exportada diretamente).

### Injeção no Contexto (`JWTMiddleware`)

```go
ctx := context.WithValue(r.Context(), ClaimsKey, claims)
next.ServeHTTP(w, r.WithContext(ctx))
```

### Extração (`GetClaims`)

```go
func GetClaims(ctx context.Context) *Claims {
    claims, ok := ctx.Value(ClaimsKey).(*Claims)
    if !ok {
        return nil
    }
    return claims
}
```

Qualquer handler downstream pode chamar `auth.GetClaims(r.Context())` para obter `UserID` e `Login` do usuário autenticado — sem re-parse do token.

---

## Chi Middleware Chain

O router Chi (`cmd/server/main.go:57-113`) organiza middlewares em camadas:

```
┌──────────────────────────────────────────────┐
│            GLOBAL MIDDLEWARES                │
│  Logger → Recoverer → RealIP → RequestID     │
│  → CORS (custom)                             │
├──────────────────────────────────────────────┤
│                                              │
│  ROTAS PÚBLICAS           ROTAS AUTENTICADAS │
│  /api/auth/42/callback    ┌────────────────┐ │
│  /api/auth/dev/login *    │ JWTMiddleware   │ │
│  /metrics                 │  ↓              │ │
│                           │ /api/messages   │ │
│                           │ /api/users/{id} │ │
│                           │ /api/users/{id} │ │
│                           │   /stats        │ │
│                           └────────────────┘ │
│                                              │
│  WEBSOCKET                                  │
│  /ws (auth própria no handler)              │
│                                              │
└──────────────────────────────────────────────┘

* /api/auth/dev/login só existe se DEV_MODE=true
```

### Middleware JWT — Detalhes

O `JWTMiddleware` (`internal/auth/middleware.go:19-45`) segue uma chain de validação rigorosa:

```
1. Header "Authorization" presente?
   ├─ NÃO → 401 {"error":"missing Authorization header"}
   └─ SIM → continua

2. Formato "Bearer <token>"?
   ├─ NÃO → 401 {"error":"invalid Authorization format"}
   └─ SIM → continua

3. Token válido (assinatura, expiry, algoritmo)?
   ├─ NÃO → 401 {"error":"invalid or expired token"}
   └─ SIM → injeta Claims no contexto, chama next handler
```

```go
func JWTMiddleware(jwtManager *JWTManager) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            authHeader := r.Header.Get("Authorization")
            // ... validações
            claims, err := jwtManager.ValidateToken(tokenStr)
            // ...
            ctx := context.WithValue(r.Context(), ClaimsKey, claims)
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}
```

O middleware é aplicado via `chi.Router.Group()` — apenas às rotas REST autenticadas:

```go
r.Group(func(r chi.Router) {
    r.Use(auth.JWTMiddleware(jwtManager))
    r.Get("/api/messages", messagesHandler.ServeHTTP)
    r.Get("/api/users/{id}/stats", statsHandler.ServeHTTP)
    r.Get("/api/users/{id}", usersHandler.ServeHTTP)
})
```

A rota `/ws` **não** usa o `JWTMiddleware` — a validação é feita internamente no `ws.Handler.ServeHTTP()`.

---

## WebSocket Upgrade com Token

O endpoint `/ws` (`internal/ws/handler.go:52-90`) faz sua própria validação de token **antes** do upgrade HTTP → WebSocket.

### Estratégia de Token — Duas Fontes

```go
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // 1. Query param (prioritário)
    tokenStr := r.URL.Query().Get("token")
    if tokenStr == "" {
        // 2. Fallback: header Sec-WebSocket-Protocol
        tokenStr = r.Header.Get("Sec-WebSocket-Protocol")
    }
    // ...
}
```

| Fonte | Exemplo | Uso |
|---|---|---|
| Query param `?token=` | `ws://host/ws?token=eyJ...` | Conexão direta do browser (`new WebSocket(url)`) |
| `Sec-WebSocket-Protocol` | Header HTTP | Client que não quer expor token na URL |

> **Nota de segurança:** tokens em query params ficam em logs de servidor e histórico do browser. O header `Sec-WebSocket-Protocol` é preferível em produção, mas o query param é mantido para conveniência no desenvolvimento.

### Validação e Criação do Client

Após validar o JWT (mesmo `jwtManager.ValidateToken` usado pelo middleware REST):

```go
claims, err := h.jwtManager.ValidateToken(tokenStr)
// ... erro → 401

client := &Client{
    UserID: claims.UserID,   // Do JWT
    Login:  claims.Login,     // Do JWT
    Send:   make(chan []byte, 256),
    Hub:    h.hub,
}

h.hub.Connect(client)            // Registra no Hub, broadcast "join"
go h.writePump(client, conn)     // Goroutine de escrita (ping + broadcast)
go h.readPump(client, conn)      // Goroutine de leitura (mensagens do client)
```

### Client WebSocket

```go
type Client struct {
    UserID int
    Login  string
    Send   chan []byte    // Buffer 256 mensagens
    Hub    *Hub
}
```

O `UserID` e `Login` vêm **diretamente do JWT** — não há consulta ao banco no upgrade. Isso mantém o upgrade rápido e evita round-trip extra.

### WebSocket Upgrader

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true  // MVP: aceita qualquer origem
    },
}
```

**Atenção:** `CheckOrigin` retornando `true` é seguro apenas para dev local. Em produção, valide a origem contra uma whitelist.

### Constantes de Tempo

| Constante | Valor | Propósito |
|---|---|---|
| `writeWait` | 10s | Timeout para escrever uma mensagem |
| `pongWait` | 60s | Tempo máximo aguardando pong do client |
| `pingPeriod` | 30s | Intervalo de envio de ping (deve ser < pongWait) |
| `maxMessageSize` | 6144 | 6KB máximo por mensagem lida |

### Ciclo de Vida da Conexão

```
Upgrade → Connect(Hub) → readPump (loop) + writePump (loop)
                              │                    │
                         mensagens dos       ping a cada 30s
                         clients → broadcast  broadcast para client
                              │                    │
                         Disconnect(Hub) ←── conexão cai/erra
                         broadcast "leave"
```

---

## Fluxo Completo: Login → Token → WS Connect

```
┌──────────┐     ┌──────────────────┐     ┌──────────┐     ┌───────────┐
│  Browser │     │  42 Chat Server  │     │  42 API  │     │ PostgreSQL│
└────┬─────┘     └────────┬─────────┘     └────┬─────┘     └─────┬─────┘
     │                     │                   │                 │
     │ 1. GET /api/auth/42 │                   │                 │
     │    /callback?code=X │                   │                 │
     │────────────────────>│                   │                 │
     │                     │ 2. POST /oauth/token                │
     │                     │──────────────────>│                 │
     │                     │ 3. access_token   │                 │
     │                     │<──────────────────│                 │
     │                     │                   │                 │
     │                     │ 4. GET /v2/me (Bearer)              │
     │                     │──────────────────>│                 │
     │                     │ 5. {id, login, …} │                 │
     │                     │<──────────────────│                 │
     │                     │                   │                 │
     │                     │ 6. UPSERT user                     │
     │                     │────────────────────────────────────>│
     │                     │                   │                 │
     │                     │ 7. GenerateToken(user_id, login)    │
     │                     │    HS256, 12h expiry                │
     │                     │                   │                 │
     │ 8. {token, user}   │                   │                 │
     │<────────────────────│                   │                 │
     │                     │                   │                 │
     │ 9. Armazena JWT     │                   │                 │
     │    (localStorage)   │                   │                 │
     │                     │                   │                 │
     │ 10. ws = new        │                   │                 │
     │   WebSocket(        │                   │                 │
     │   "/ws?token=eyJ…") │                   │                 │
     │────────────────────>│                   │                 │
     │                     │ 11. ValidateToken │                 │
     │                     │     (claims OK)   │                 │
     │                     │                   │                 │
     │                     │ 12. Upgrade 101   │                 │
     │<────────────────────│                   │                 │
     │                     │                   │                 │
     │ 13. WS aberto —     │                   │                 │
     │   Client conectado  │                   │                 │
     │   ao Hub            │                   │                 │
```

### Resumo dos Tokens

| Token | Emissor | Destinatário | Expiração | Uso |
|---|---|---|---|---|
| 42 `access_token` | API 42 | 42 Chat Server | ~2h | Buscar `/v2/me` (descartado após login) |
| 42 Chat JWT | 42 Chat Server | Browser/Client | 12h | Autenticar REST + WebSocket |

---

## Rotas e Auth — Tabela Resumo

| Rota | Auth | Método |
|---|---|---|
| `/api/auth/42/callback` | Nenhuma (troca code por JWT) | GET |
| `/api/auth/dev/login` | Nenhuma (só existe com `DEV_MODE=true`) | GET |
| `/metrics` | Nenhuma | GET |
| `/api/messages` | `JWTMiddleware` → `Authorization: Bearer <jwt>` | GET |
| `/api/users/{id}` | `JWTMiddleware` → `Authorization: Bearer <jwt>` | GET |
| `/api/users/{id}/stats` | `JWTMiddleware` → `Authorization: Bearer <jwt>` | GET |
| `/ws` | Validação interna: `?token=<jwt>` ou `Sec-WebSocket-Protocol` | GET (Upgrade) |

---

## Padrões de Segurança

### 1. Secret em Produção

O default `"dev-secret-change-in-production"` deve ser substituído em produção:

```bash
export JWT_SECRET="$(openssl rand -base64 64)"
```

### 2. Sem Refresh Token

O JWT tem 12h de expiração e **não há endpoint de refresh**. Quando expirar, o client deve redirecionar para re-autenticação OAuth2. Isso simplifica o backend e evita a complexidade de token rotation.

### 3. Proteção contra Algorithm Confusion

A função de key lookup rejeita qualquer algoritmo que não seja HMAC:

```go
if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
    return nil, fmt.Errorf("método de assinatura inesperado: %v", t.Header["alg"])
}
```

### 4. Context Key Privada

```go
type contextKey string
const ClaimsKey contextKey = "claims"
```

O tipo `contextKey` é não-exportado — handlers de outros pacotes não conseguem forjar claims no contexto.

### 5. WebSocket CheckOrigin

Atualmente aberto (`return true`). Em produção:

```go
CheckOrigin: func(r *http.Request) bool {
    origin := r.Header.Get("Origin")
    return origin == "https://meu-frontend.com"
}
```

---

## Dependências

```go
// go.mod
github.com/go-chi/chi/v5 v5.3.0       // Router + middleware chain
github.com/golang-jwt/jwt/v5 v5.3.1    // JWT criação/validação
github.com/gorilla/websocket v1.5.3     // WebSocket upgrade + pumps
```

Nenhuma dependência externa de OAuth2 — implementação manual com `net/http`.
