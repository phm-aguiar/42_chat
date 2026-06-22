---
title: "OAuth2 42 — Fluxo Completo"
tags: 
- oauth2 
- 42_school 
- auth 
- security
created: 2026-06-21
rag_score: 0.5
category: references
summary: Implementação do Authorization Code Flow da API 42 no 42 Chat — token exchange, upsert de usuário, DEV_MODE bypass e pitfalls de rate limit / expiração.
provenance:
  extracted: 0.96
  inferred: 0.04
  ambiguous: 0.00
---

# OAuth2 42 — Fluxo Completo

Referência da integração OAuth2 com a API da 42 — do redirect à persistência do usuário, com bypass para desenvolvimento local.

---

## Arquitetura

O fluxo de autenticação reside em três arquivos:

| Arquivo | Responsabilidade |
|---|---|
| `internal/auth/oauth.go` | Troca `code` → `access_token` → dados do usuário 42 |
| `internal/auth/dev_login.go` | Mock user + JWT direto (bypass OAuth2 em dev) |
| `internal/config/config.go` | Configuração de client ID/secret, redirect URI, API URL |

A struct `OAuth2` encapsula o `*http.Client` (timeout 10s) e as dependências de config e banco:

```go
type OAuth2 struct {
    cfg     *config.Config
    queries *db.Queries
    client  *http.Client  // Timeout: 10s
}
```

---

## Endpoints da API 42

Dois endpoints são usados no fluxo:

### `POST https://api.intra.42.fr/oauth/token`

Troca o authorization code por um access token.

**Request** (`application/x-www-form-urlencoded`):

| Parâmetro | Valor |
|---|---|
| `grant_type` | `authorization_code` |
| `client_id` | `FORTYTWO_CLIENT_ID` (env) |
| `client_secret` | `FORTYTWO_CLIENT_SECRET` (env) |
| `code` | Código recebido no callback |
| `redirect_uri` | `FORTYTWO_REDIRECT_URI` (env, default: `http://localhost:8080/api/auth/42/callback`) |

**Response** (200 OK):

```json
{
  "access_token": "xxxxx...",
  "token_type": "bearer",
  "expires_in": 7200
}
```

> **Nota:** O projeto só lê os campos `access_token`, `token_type` e `expires_in`. O `refresh_token` **não é usado** — a API 42 não fornece refresh token no fluxo de authorization code padrão; a re-autenticação é feita redirecionando o usuário novamente.

### `GET https://api.intra.42.fr/v2/me`

Busca os dados do usuário autenticado.

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK) — campos relevantes mapeados:

| Campo 42 | Campo `userResponse` | Campo `model.User` |
|---|---|---|
| `id` | `ID int` | `ID` |
| `login` | `Login string` | `Login` |
| `image_url` | `ImageURL string` | `ImageURL` |
| `location` | `Location string` | `CurrentHost` (pode ser `null`) |
| `level` | `Level float64` | `Level` |

```go
type userResponse struct {
    ID       int     `json:"id"`
    Login    string  `json:"login"`
    ImageURL string  `json:"image_url"`
    Location string  `json:"location"` // pode ser null
    Level    float64 `json:"level"`
}
```

---

## Authorization Code Flow — Passo a Passo

O fluxo completo está implementado em `ExchangeCode()` (`internal/auth/oauth.go:51-79`):

```
[Browser]                    [42 Chat Server]                 [42 API]
    |                              |                               |
    |-- GET /api/auth/42?redirect  |                               |
    |   (redireciona p/ 42)       |                               |
    |----------------------------->|                               |
    |                              |                               |
    |-- 302 → api.intra.42.fr/oauth/authorize                      |
    |<-----------------------------|                               |
    |                              |                               |
    |-- Usuário autoriza na 42 --->|                               |
    |                              |                               |
    |-- GET /api/auth/42/callback?code=XXXX                         |
    |----------------------------->|                               |
    |                              |                               |
    |                              | 1. fetchToken(code)           |
    |                              |-- POST /oauth/token -------->|
    |                              |<--- access_token -------------|
    |                              |                               |
    |                              | 2. fetchUser(access_token)    |
    |                              |-- GET /v2/me --------------->|
    |                              |<--- {id, login, ...} ---------|
    |                              |                               |
    |                              | 3. UpsertUser(user)           |
    |                              |-- INSERT/UPDATE PostgreSQL    |
    |                              |                               |
    |                              | 4. GenerateToken JWT          |
    |                              |                               |
    |<-- {token, user} ------------|                               |
```

### Etapa 1: `fetchToken(code)` — Troca do código

```go
func (o *OAuth2) fetchToken(code string) (*tokenResponse, error) {
    data := url.Values{
        "grant_type":    {"authorization_code"},
        "client_id":     {o.cfg.FortyTwoClientID},
        "client_secret": {o.cfg.FortyTwoClientSecret},
        "code":          {code},
        "redirect_uri":  {o.cfg.FortyTwoRedirectURI},
    }

    req, err := http.NewRequest("POST",
        fmt.Sprintf("%s/oauth/token", o.cfg.FortyTwoAPIURL),
        strings.NewReader(data.Encode()))
    req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

    resp, err := o.client.Do(req)
    // ... validação de status != 200
    var token tokenResponse
    json.NewDecoder(resp.Body).Decode(&token)
    return &token, nil
}
```

**Comportamento de erro:** Se a API 42 retornar status ≠ 200, o corpo inteiro é lido e incluído na mensagem de erro:

```go
if resp.StatusCode != http.StatusOK {
    body, _ := io.ReadAll(resp.Body)
    return nil, fmt.Errorf("oauth/token: status %d: %s", resp.StatusCode, string(body))
}
```

### Etapa 2: `fetchUser(accessToken)` — Dados do usuário

```go
func (o *OAuth2) fetchUser(accessToken string) (*userResponse, error) {
    req, _ := http.NewRequest("GET",
        fmt.Sprintf("%s/v2/me", o.cfg.FortyTwoAPIURL), nil)
    req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", accessToken))
    // ... mesmo padrão de erro da etapa 1
}
```

### Etapa 3: Upsert no PostgreSQL

O `model.User` é construído a partir da resposta da API 42 e persistido via `queries.UpsertUser()`. O campo `CreatedAt` é sempre `time.Now().UTC()` — ou seja, atualiza a cada login.

```go
user := &model.User{
    ID:          fortyTwoUser.ID,
    Login:       fortyTwoUser.Login,
    ImageURL:    fortyTwoUser.ImageURL,
    CurrentHost: fortyTwoUser.Location,
    Level:       fortyTwoUser.Level,
    CreatedAt:   time.Now().UTC(),
}
```

---

## Token Exchange — Detalhes

### Formato da resposta

```go
type tokenResponse struct {
    AccessToken string `json:"access_token"`
    TokenType   string `json:"token_type"`
    ExpiresIn   int    `json:"expires_in"`
}
```

- `access_token`: Token de acesso da API 42 (OAuth2 Bearer)
- `token_type`: Sempre `"bearer"`
- `expires_in`: Segundos até expiração (tipicamente 7200 = 2 horas)

### Timeout HTTP

O `http.Client` usado em todo o fluxo tem **timeout de 10 segundos**:

```go
client: &http.Client{Timeout: 10 * time.Second}
```

Isso cobre tanto a chamada a `/oauth/token` quanto a `/v2/me`. Se qualquer uma das chamadas exceder 10s, um erro de rede é retornado.

---

## Callback HTTP — O Ponto de Entrada

O endpoint `/api/auth/42/callback` em `cmd/server/main.go:67-94` orquestra o fluxo:

```go
r.Get("/api/auth/42/callback", func(w http.ResponseWriter, r *http.Request) {
    code := r.URL.Query().Get("code")
    // Valida code presente

    user, err := oauth2.ExchangeCode(code)   // OAuth2 → User
    token, err := jwtManager.GenerateToken(user.ID, user.Login)  // JWT

    // Resposta JSON: {token, user: {id, login, image_url}}
})
```

A resposta entregue ao frontend:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 12345,
    "login": "marvin",
    "image_url": "https://cdn.intra.42.fr/users/marvin.jpg"
  }
}
```

---

## Refresh de Token

**O 42 Chat não implementa refresh token.** A API 42 não fornece refresh token no fluxo `authorization_code`. Quando o access token da 42 expira (tipicamente 2h), o frontend deve redirecionar o usuário para re-autenticar.

O JWT interno do 42 Chat, por outro lado, tem expiração de **12 horas** (ver [auth-integration.md](auth-integration.md)). Enquanto o JWT for válido, a conexão WebSocket permanece ativa sem necessidade de re-autenticação 42.

---

## DEV_MODE Bypass

Em desenvolvimento local (`DEV_MODE=true`), o endpoint `/api/auth/dev/login` permite autenticação sem OAuth2 real.

### Como funciona

```go
// cmd/server/main.go:99-102
if cfg.DevMode {
    r.Get("/api/auth/dev/login", devLoginHandler.ServeHTTP)
}
```

O handler (`internal/auth/dev_login.go`) cria um mock user fixo:

```go
user := &model.User{
    ID:          42,                                          // ID fixo
    Login:       login,                                       // ?login=marvin ou DEV_USER env
    ImageURL:    "https://cdn.intra.42.fr/users/default.png", // Avatar padrão
    CurrentHost: "e1z2m3",                                   // Host fixo
    Level:       8.42,                                       // Nível de mentira
}
```

### Parâmetros

| Fonte | Descrição |
|---|---|
| `?login=marvin` | Query param (prioritário) |
| `DEV_USER` env var | Fallback se query param vazio |
| Default `"marvin"` | Hardcoded se nenhum dos anteriores |

### Resposta (idêntica ao fluxo real)

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 42,
    "login": "marvin",
    "image_url": "https://cdn.intra.42.fr/users/default.png"
  }
}
```

> **Segurança:** O endpoint `/api/auth/dev/login` **só é registrado** se `DEV_MODE=true`. Em produção, a rota simplesmente não existe.

---

## Configuração

Todas as variáveis de ambiente relevantes (`internal/config/config.go`):

| Variável | Default | Uso |
|---|---|---|
| `FORTYTWO_CLIENT_ID` | *(obrigatório)* | Client ID da app registrada na 42 |
| `FORTYTWO_CLIENT_SECRET` | *(obrigatório)* | Client Secret |
| `FORTYTWO_API_URL` | `https://api.intra.42.fr` | Base URL da API 42 |
| `FORTYTWO_REDIRECT_URI` | `http://localhost:<PORT>/api/auth/42/callback` | Callback OAuth2 |
| `DEV_MODE` | `false` | Habilita `/api/auth/dev/login` |

**Validação:** Em produção, `FORTYTWO_CLIENT_ID` e `FORTYTWO_CLIENT_SECRET` vazios causam erro fatal. Em dev (detectado via `JWT_SECRET == "dev-secret-change-in-production"`), credenciais vazias são toleradas.

---

## Pitfalls & Rate Limits

### 1. Rate Limits da API 42

A API 42 impõe **rate limits por token**. O comportamento padrão:

- **2 requisições/segundo** por token
- **1200 requisições/hora** por token

O 42 Chat faz 2 chamadas por login (`/oauth/token` + `/v2/me`). Para usuários logando simultaneamente em prod, o rate limit não deve ser problema — cada usuário tem seu próprio token.

### 2. Expiração do Token 42

O `access_token` da 42 expira em **~2 horas** (`expires_in: 7200`). O 42 Chat **não armazena** o access token — ele é usado apenas durante o fluxo de login e descartado. O sistema depende exclusivamente do JWT interno após o login.

### 3. Timeout HTTP (10s)

Se a API 42 estiver lenta ou inacessível, a chamada falha após **10 segundos**. Não há retry automático. O frontend recebe um erro 500 com `{"error":"oauth exchange failed"}`.

### 4. Token de Autorização de Uso Único

O `code` recebido no callback é **single-use**. Se o callback for chamado duas vezes com o mesmo código, a segunda chamada falha com erro da API 42.

### 5. Redirect URI Mismatch

A `redirect_uri` enviada no `POST /oauth/token` deve ser **exatamente igual** à registrada na app 42. O default é `http://localhost:8080/api/auth/42/callback` — em staging/produção, sobrescreva com `FORTYTWO_REDIRECT_URI`.

### 6. CORS em Desenvolvimento

O middleware CORS (`cmd/server/main.go:157-169`) permite qualquer origem (`Access-Control-Allow-Origin: *`). Isso é seguro apenas para dev local — em produção, restrinja à origem do frontend.

---

## Fluxo Alternativo: Erro de OAuth

Se o usuário negar autorização na 42 ou ocorrer erro na API:

```
Browser → GET /api/auth/42/callback?error=access_denied
Server  → verifica code == ""
        → 400 {"error":"missing code"}
```

O frontend deve tratar HTTP 400 e redirecionar para login novamente.

---

## Dependências

Nenhuma biblioteca externa de OAuth2 — implementação manual com `net/http`:

```go
import (
    "encoding/json"
    "io"
    "net/http"
    "net/url"
    "strings"
)
```

A escolha é deliberada: evita a complexidade de bibliotecas como `golang.org/x/oauth2` para um fluxo que são apenas duas chamadas HTTP.
