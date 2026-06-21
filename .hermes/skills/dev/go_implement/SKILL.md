---
name: go_implement
description: >
  Use when the agent-dev needs to implement Go code from a spec. Covers idiomatic
  Go patterns: package structure (cmd/internal/pkg), Chi router, gorilla/websocket
  Hub + Client, PostgreSQL with database/sql, graceful shutdown, OAuth2 flow,
  error handling, and project layout conventions for the 42 Chat framework.
  Trigger keywords: implementar Go, Go implement, criar modulo Go, Go backend,
  Go API, Chi router, gorilla websocket, PostgreSQL Go.
version: 0.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dev, go, implementation, backend, websocket, postgresql]
    related_skills: [build_check, wiki-query]
    category: dev
    created: 2026-06-16
    resources:
      - SKILL.md
---

# go_implement — Implementar código Go a partir de spec

> Categoria: `dev` — criada em 2026-06-16. Trilho do agent-dev para stack Go.

## Propósito

Esta skill é carregada pelo agent-dev quando a task envolve implementar código Go.
Ela cobre os padrões específicos do 42 Chat definidos no spec/plan da feature 100:
estrutura de projeto, Hub WebSocket híbrido (RWMutex + channels), OAuth2 42,
PostgreSQL com database/sql, graceful shutdown, e convenções idiomáticas de Go.

Não substitui o conhecimento geral de Go — o agent-dev já sabe Go. Esta skill
fornece os **padrões arquiteturais e convenções do projeto** para que o código
produzido seja consistente com o resto da codebase.

## Pré-requisitos

- Go 1.21+ instalado (`go version`)
- `go.mod` inicializado no projeto (T001)
- Acesso aos arquivos da spec: `specs/features/100-42chat-core/spec.md` (seções relevantes)
- Acesso ao plano: `specs/features/100-42chat-core/plan.md` (ADRs e contratos)
- Wiki vault disponível para consulta de referências Go

## Quando usar (gatilhos)

- Task do agent-dev com stack Go
- "implementar handler", "criar rota", "conectar banco"
- "WebSocket hub", "OAuth2 callback", "graceful shutdown"
- Task que referencia arquivos `internal/` ou `cmd/`

## Fluxo de Execução

### Passo 1: Ler o contexto da task

Antes de escrever qualquer código, leia do contexto injetado pelo orchestrator:

1. **Spec relevante** — seções do `spec.md` que se aplicam à task
2. **ADRs do plan** — decisões arquiteturais (ADR-1 a ADR-8)
3. **Task atômica** — ID, descrição, arquivos a modificar, dependências
4. **Arquivos existentes** — leia os arquivos já criados por tasks anteriores

Nunca comece a implementar sem entender o contrato (REST API, WebSocket, ou DB).

### Passo 2: Estrutura de diretórios

O projeto segue o layout Go padrão com `cmd/` e `internal/`:

```
cmd/
  server/
    main.go                 # Entry point único
internal/
  auth/
    oauth42.go              # OAuth2 42 (authorize, callback, JWT)
  chat/
    hub.go                  # WebSocket Hub (RWMutex + channels)
    client.go               # WebSocket Client (readPump, writePump)
    message.go              # Modelo Message (struct + JSON tags)
  api/
    routes.go               # Rotas Chi (mux)
    handler_auth.go         # Handlers de autenticação
    handler_messages.go     # Handlers de histórico
    middleware.go            # JWT, CORS, rate limit
  repository/
    db.go                   # Conexão PostgreSQL pool + migrations
    users.go                # Queries: users (upsert, find)
    messages.go             # Queries: messages (insert, fetch, soft delete)
  cache/
    user_cache.go           # Cache anti-rate-limit 3 camadas
  observability/
    metrics.go              # /metrics: goroutines, DB.Stats(), WS ativas
```

Regras:
- `cmd/` contém apenas o `main.go` (entry point). Nada de lógica aqui.
- `internal/` é inacessível de fora do módulo. Toda lógica de negócio vai aqui.
- Pacotes são agrupados por domínio (auth, chat, api, repository), não por tipo (models, handlers, utils).

### Passo 3: Padrões de código por domínio

#### 3a. Entry point (`cmd/server/main.go`)

```go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/go-chi/chi/v5"
)

func main() {
    // 1. Carregar configuração (env vars)
    cfg := loadConfig()

    // 2. Inicializar logger estruturado
    logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

    // 3. Conectar PostgreSQL
    db, err := connectDB(cfg.DatabaseURL)
    if err != nil {
        logger.Error("falha ao conectar banco", "error", err)
        os.Exit(1)
    }
    defer db.Close()

    // 4. Criar Hub WebSocket
    hub := chat.NewHub()
    go hub.Run()

    // 5. Criar router Chi
    r := chi.NewRouter()
    // ... middleware, rotas ...

    // 6. Iniciar servidor HTTP
    srv := &http.Server{Addr: ":8080", Handler: r}

    // 7. Graceful shutdown
    go func() {
        sigChan := make(chan os.Signal, 1)
        signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
        <-sigChan

        logger.Info("iniciando graceful shutdown...")
        ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
        defer cancel()

        hub.Shutdown()           // notificar clientes, drenar buffer
        srv.Shutdown(ctx)        // parar HTTP server
        db.Close()               // fechar pool PostgreSQL
    }()

    logger.Info("servidor iniciado", "addr", ":8080")
    if err := srv.ListenAndServe(); err != http.ErrServerClosed {
        logger.Error("servidor parou inesperadamente", "error", err)
        os.Exit(1)
    }
}
```

#### 3b. WebSocket Hub (`internal/chat/hub.go`) — Modelo Híbrido (ADR-5)

O Hub usa `sync.RWMutex` no mapa de clients + `send chan` como buffer de saída por client:

```go
package chat

import "sync"

type Hub struct {
    clients    map[*Client]bool
    register   chan *Client
    unregister chan *Client
    broadcast  chan []byte
    mu         sync.RWMutex  // protege clients (RLock em leitura, Lock em escrita)
}
```

Regras:
- **`register`/`unregister`**: channels. Operações de insert/remove passam pelo `select` no `Run()`.
- **`broadcast`**: itera `clients` com `RLock`, envia para `client.send` (não bloqueante com `select/default`).
- **`send chan`**: buffer de 256 mensagens por client. Se cheio, descarta (evita bloquear o Hub).
- **Ping/Pong**: servidor envia ping a cada 30s (ticker no `Run`). Read deadline = 60s. Write deadline = 10s.

#### 3c. WebSocket Client (`internal/chat/client.go`)

```go
type Client struct {
    hub  *Hub
    conn *websocket.Conn
    send chan []byte  // buffer elástico (256)
    user *User        // dados do usuário autenticado
}
```

Métodos:
- `readPump()`: lê mensagens do WebSocket, envia para `hub.broadcast`. Sai no primeiro erro.
- `writePump()`: lê do `send` chan e escreve no WebSocket. Gerencia ping/pong e write deadline.
- No `readPump()`, validar JSON recebido: `{"type": "message", "content": "..."}`.

#### 3d. Upgrade WebSocket com JWT (ADR-3)

```go
func ServeWs(hub *Hub, w http.ResponseWriter, r *http.Request) {
    // 1. Extrair token JWT do query param (?token=...)
    token := r.URL.Query().Get("token")

    // 2. Validar JWT
    claims, err := validateJWT(token)
    if err != nil {
        http.Error(w, "Unauthorized", 401)
        return
    }

    // 3. Upgrade para WebSocket
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }

    // 4. Criar Client e registrar no Hub
    client := &Client{
        hub:  hub,
        conn: conn,
        send: make(chan []byte, 256),
        user: &User{ID: claims.UserID, Login: claims.Login},
    }
    hub.register <- client

    // 5. Iniciar pumps
    go client.writePump()
    go client.readPump()
}
```

#### 3e. OAuth2 42 (`internal/auth/oauth42.go`) — ADR-4

Fluxo:
1. `GET /api/auth/login` → redireciona para `https://api.intra.42.fr/oauth/authorize?client_id=...&redirect_uri=...&response_type=code`
2. Callback recebe `?code=...` → troca code por token (POST `/oauth/token`)
3. Com access token, busca `/v2/me` (inclui `cursus_users[].level`, `campus_users[].host`)
4. Upsert no PostgreSQL (id, login, image_url, current_host, level)
5. Gera JWT interno (12h, claims: `user_id`, `login`) → retorna pro frontend

Cache anti-rate-limit 3 camadas (ADR-4):
1. **JWT 12h** — elimina revalidação contínua
2. **Perfil em PostgreSQL** — cache no primeiro login (upsert)
3. **Batch ingest** — mapeamento de laboratório a cada 30s

```go
func generateJWT(userID int, login string, secret []byte) (string, error) {
    claims := jwt.MapClaims{
        "user_id": userID,
        "login":   login,
        "exp":     time.Now().Add(12 * time.Hour).Unix(),
        "iat":     time.Now().Unix(),
    }
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(secret)
}
```

#### 3f. Chi Router + Middleware (`internal/api/`)

```go
// routes.go
func NewRouter(hub *chat.Hub, db *sql.DB, jwtSecret []byte) chi.Router {
    r := chi.NewRouter()

    // Middleware global
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(corsMiddleware())
    r.Use(rateLimitMiddleware())

    // Rotas públicas (sem JWT)
    r.Get("/api/auth/login", handleOAuthLogin)
    r.Get("/api/auth/callback", handleOAuthCallback)

    // Rotas protegidas (com JWT)
    r.Group(func(r chi.Router) {
        r.Use(jwtMiddleware(jwtSecret))
        r.Get("/api/me", handleMe)
        r.Get("/api/messages", handleGetMessages)
    })

    // WebSocket (JWT validado no upgrade)
    r.Get("/ws", func(w http.ResponseWriter, r *http.Request) {
        chat.ServeWs(hub, w, r)
    })

    // Métricas (interno)
    r.Get("/metrics", handleMetrics)

    return r
}
```

Middleware JWT: extrai token do header `Authorization: Bearer <token>`, valida, injeta claims no `context`.

#### 3g. PostgreSQL (`internal/repository/`)

```go
// db.go — conexão com pool
func Connect(databaseURL string) (*sql.DB, error) {
    db, err := sql.Open("postgres", databaseURL)
    if err != nil {
        return nil, fmt.Errorf("sql.Open: %w", err)
    }

    // Pool config (alinhado ao PostgreSQL tuning do plan)
    db.SetMaxOpenConns(100)    // max_connections
    db.SetMaxIdleConns(25)
    db.SetConnMaxLifetime(5 * time.Minute)

    if err := db.Ping(); err != nil {
        return nil, fmt.Errorf("db.Ping: %w", err)
    }

    // Rodar migrations
    if err := runMigrations(db); err != nil {
        return nil, fmt.Errorf("migrations: %w", err)
    }

    return db, nil
}
```

```go
// users.go — upsert com current_host
func UpsertUser(db *sql.DB, u *User) error {
    query := `
        INSERT INTO users (id, login, image_url, current_host, level)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            login = EXCLUDED.login,
            image_url = EXCLUDED.image_url,
            current_host = EXCLUDED.current_host,
            level = EXCLUDED.level
    `
    _, err := db.Exec(query, u.ID, u.Login, u.ImageURL, u.CurrentHost, u.Level)
    return err
}
```

```go
// messages.go — insert com CHECK, fetch recent, soft delete
func InsertMessage(db *sql.DB, msg *Message) error {
    query := `
        INSERT INTO messages (user_id, content)
        VALUES ($1, $2)
        RETURNING id, created_at
    `
    return db.QueryRow(query, msg.UserID, msg.Content).Scan(&msg.ID, &msg.CreatedAt)
}

func FetchRecentMessages(db *sql.DB, before time.Time, limit int) ([]Message, error) {
    query := `
        SELECT id, user_id, content, created_at
        FROM messages
        WHERE created_at < $1 AND deleted_at IS NULL
        ORDER BY created_at DESC
        LIMIT $2
    `
    // ...
}
```

#### 3h. Modelos (`internal/chat/message.go`)

```go
type Message struct {
    ID        string    `json:"id"`
    UserID    int       `json:"user_id"`
    Content   string    `json:"content"`
    CreatedAt time.Time `json:"created_at"`
}
```

### Passo 4: Convenções idiomáticas Go

Siga estas regras extraídas do [[references/go-style-guide|Go Style Guide]]:

1. **Error handling**: sempre retorne `error` como último valor. Use `fmt.Errorf("context: %w", err)` para wrapping.
2. **Naming**: MixedCaps (exportado) / mixedCaps (não exportado). Sem underscores.
3. **Context**: todo handler e operação de DB recebe `context.Context` como primeiro parâmetro.
4. **Goroutines**: toda goroutine precisa de um stop mechanism claro. Use `context.Context` para cancelamento.
5. **Interfaces**: defina interfaces onde são consumidas (não onde são implementadas).
6. **Pacotes**: mantenha pacotes pequenos e focados. Evite `util` ou `common`.
7. **Logging**: use `log/slog` com structured logging. Sempre inclua chaves relevantes.
8. **Testes**: table-driven tests com `t.Run()` para subtests. Consulte [[references/go-testing]].

Consulte o [[references/go-style-guide|catálogo completo]] para detalhes por tópico.

### Passo 5: Integrar com o restante do projeto

- **Dependências Go**: execute `go get <pacote>` para adicionar ao `go.mod`. Não edite o arquivo manualmente.
- **Compatibilidade**: o código deve compilar com `go build ./...` antes de reportar DONE.
- **Tags JSON**: use `json:"nome_campo"` (snake_case) em todos os modelos expostos na API.

## Guardrails

- **Nunca implemente sem spec**: se a task não tem contexto claro (spec + ADR), reporte BLOCKED.
- **Nunca infira schema SQL**: o schema está definido no `plan.md` (ADR-2). Se a task pedir migration, use exatamente o SQL do plano.
- **JWT secret via env var**: nunca hardcode o segredo. Use `os.Getenv("JWT_SECRET")`.
- **Pool de conexões**: `db.SetMaxOpenConns(100)` alinhado ao `max_connections` do PostgreSQL (plan, seção 2).
- **CORS explícito**: não use `*` wildcard. A origem permitida é `https://chat.42sp.org.br`.
- **Graceful shutdown é obrigatório**: todo `main.go` deve interceptar SIGINT/SIGTERM e drenar buffers.
- **Ping/Pong**: read deadline = 60s, ping interval = 30s. Sem ping/pong, o load balancer mata conexões idle.
- **Erros idiomáticos**: sempre wrap errors com contexto (`fmt.Errorf("auth: %w", err)`). Nunca use `panic` para erros recuperáveis.

## Referências

- [[references/42-chat-platform-architecture|Platform Architecture]] — Stack completa e schema
- [[references/42-chat-engineering-requirements|Engineering Requirements]] — Concorrência, graceful shutdown, tuning
- [[references/go-style-guide|Go Style Guide]] — Catálogo de 20 tópicos de estilo Go
- [[references/go-concurrency|Go Concurrency]] — Goroutines, channels, mutexes
- [[references/go-error-handling|Go Error Handling]] — Wrapping, sentinelas, patterns
- [[references/go-context|Go Context]] — Cancelamento, timeouts, valores

## Verificação

- [ ] `go build ./...` compila sem erros (exit code 0)
- [ ] Estrutura de diretórios segue `cmd/` + `internal/` (sem lógica em `cmd/`)
- [ ] Código usa `log/slog` para logging (sem `fmt.Println` não estruturado)
- [ ] Erros são wrapped com `fmt.Errorf("context: %w", err)`
- [ ] JWT secret é lido de env var, nunca hardcoded
- [ ] Graceful shutdown implementado no `main.go` (SIGINT/SIGTERM)
- [ ] WebSocket Hub tem Ping/Pong a cada 30s + deadlines configurados
- [ ] CORS middleware especifica origem exata, não wildcard
