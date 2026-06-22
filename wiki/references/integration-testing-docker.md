---
title: "Integration Testing with Docker"
tags: [testing, docker, integration]
created: 2026-06-21
rag_score: 0.5
category: references
summary: Smoke tests, Docker test lifecycle, WebSocket testing with gorilla/websocket, table-driven patterns, and CI/CD integration — based on real 42_chat patterns.
---

# Integration Testing with Docker

How the 42_chat project tests end-to-end flows — from in-memory smoke tests to full server integration with PostgreSQL, WebSocket clients, and graceful shutdown.

---

## Smoke Tests

Smoke tests verify that the system is *alive* — not that every feature works, but that the critical path (build → connect → message → shutdown) holds together.

### Pattern: `test/smoke_test.go`

The project has a dedicated `test/` package (outside `internal/`) with three smoke levels:

```go
package test

// Level 1: Build — go build ./... compila sem erros
func TestSmokeBuild(t *testing.T) {
    cmd := exec.Command("go", "build", "./...")
    cmd.Dir = ".." // relative to test/ directory
    output, err := cmd.CombinedOutput()
    if err != nil {
        t.Fatalf("go build ./... failed:\n%s", string(output))
    }
}
```

### Level 2: In-Memory Hub (no HTTP, no DB)

Tests the WebSocket Hub directly — creates `ws.Client` structs, connects them, broadcasts a message, and verifies every client received it:

```go
func TestSmokeHubInMemory(t *testing.T) {
    hub := ws.NewHub(nil)
    client1 := &ws.Client{
        UserID: 1, Login: "smoke_user_1",
        Send: make(chan []byte, 256), Hub: hub,
    }
    client2 := &ws.Client{
        UserID: 2, Login: "smoke_user_2",
        Send: make(chan []byte, 256), Hub: hub,
    }
    hub.Connect(client1)
    hub.Connect(client2)
    // drain join messages, then broadcast & verify
    hub.Broadcast(&model.WSMessage{
        Type: "message", Content: "hello from smoke test",
    })
    // verify both clients received the message
    // then hub.Shutdown() and verify shutdown notification
}
```

### Level 3: Server Integration (real HTTP + WebSocket + DB)

Full integration: build server binary, find free port, generate JWT, start server as subprocess, connect real WebSocket clients, exchange messages, send SIGTERM, verify graceful shutdown:

```go
func TestSmokeServerIntegration(t *testing.T) {
    // 1. Build server binary
    buildCmd := exec.Command("go", "build", "-o", "smoke_test_server", "./cmd/server/")

    // 2. Find free port
    port, _ := findFreePort()

    // 3. Generate JWT
    jwtManager := auth.NewJWTManager(jwtSecret)
    token, _ := jwtManager.GenerateToken(42, "smoke_tester")

    // 4. Start server as subprocess with env vars
    serverCmd := exec.Command(serverBinary)
    serverCmd.Env = append(os.Environ(),
        "PORT="+port,
        "DATABASE_URL="+dbURL,
        "JWT_SECRET="+jwtSecret,
    )
    serverCmd.Start()

    // 5. Wait for health check (polling GET /metrics)
    ready := waitForServer(t, port, 5*time.Second)

    // 6. Connect WebSocket clients
    wsURL := fmt.Sprintf("ws://127.0.0.1:%s/ws?token=%s", port, token)
    client1, _, _ := websocket.DefaultDialer.Dial(wsURL, nil)
    client2, _, _ := websocket.DefaultDialer.Dial(wsURL, nil)

    // 7. Exchange messages via WebSocket
    client1.WriteMessage(websocket.TextMessage, sendData)
    verifyWSMessage(t, client1, "message", "hello from smoke test", "client1")
    verifyWSMessage(t, client2, "message", "hello from smoke test", "client2")

    // 8. Graceful shutdown via SIGTERM
    serverCmd.Process.Signal(syscall.SIGTERM)
    verifyWSMessage(t, client1, "system", "shutdown", "client1")
    verifyWSMessage(t, client2, "system", "shutdown", "client2")

    // 9. Verify exit code 0
    serverCmd.Wait()
}
```

### Health Check Helper

The smoke test waits for the server by polling `GET /metrics`:

```go
func waitForServer(t *testing.T, port string, timeout time.Duration) bool {
    deadline := time.Now().Add(timeout)
    url := fmt.Sprintf("http://127.0.0.1:%s/metrics", port)
    for time.Now().Before(deadline) {
        resp, err := http.Get(url)
        if err == nil {
            resp.Body.Close()
            if resp.StatusCode == http.StatusOK {
                return true
            }
        }
        time.Sleep(100 * time.Millisecond)
    }
    return false
}
```

### Graceful Skip Pattern

When PostgreSQL is unavailable, the test skips instead of failing:

```go
// Wait for server or detect early exit (DB unreachable)
ready := waitForServer(t, port, 5*time.Second)
if !ready {
    // Check if process already exited
    serverCmd.Wait() // don't block
    if serverCmd.ProcessState != nil {
        t.Skip("PostgreSQL não disponível — pulando integração com servidor real")
    }
}
```

---

## Docker Test Lifecycle

### Architecture

```
docker compose up    →  PostgreSQL + Server iniciam
     │
wait healthy         →  pg_isready + server health check
     │
go test ./...        →  testes rodam contra os containers
     │
docker compose down  →  limpeza (opcional: -v para resetar volumes)
```

### docker-compose.yml (Test Perspective)

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: 42chat-postgres
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chat -d chat"]
      interval: 5s
      timeout: 3s
      retries: 5
    volumes:
      - ./internal/db/migrations:/docker-entrypoint-initdb.d:ro,z

  server:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://chat:***@postgres:5432/chat?sslmode=disable
      JWT_SECRET: ${JWT_SECRET:-change-me-in-production-please}
```

Key points for testing:

- **`depends_on: condition: service_healthy`** — server only starts after PostgreSQL passes `pg_isready`.
- **Migrations mount** at `/docker-entrypoint-initdb.d` — PostgreSQL auto-executes `001_init.sql` on first startup. New containers get fresh schema automatically.
- **Named volume `pgdata`** — survives `docker compose down` (without `-v`). Use `-v` to reset database state between test runs.

### Typical Test Run Sequence

```bash
# 1. Start infrastructure
docker compose up --build -d

# 2. Wait for healthy (compose does this automatically via depends_on)
docker compose ps  # verify both services are "healthy" / "running"

# 3. Run tests (from project root)
DATABASE_URL="postgres://chat:banana42@localhost:5432/chat?sslmode=disable" \
JWT_SECRET="test-secret" \
  go test ./... -v -count=1

# 4. Optional: run only integration tests
go test ./test/ -v -run TestSmoke

# 5. Tear down
docker compose down        # keep data
docker compose down -v     # wipe database
```

### Subprocess Pattern (Alternative)

For tests that want full control over the server lifecycle, the smoke tests use `exec.Command` to build and run the server binary directly — no compose needed:

```go
// Build
buildCmd := exec.Command("go", "build", "-o", "smoke_test_server", "./cmd/server/")
buildCmd.Dir = ".."
buildCmd.Run()

// Start
serverCmd := exec.Command("../smoke_test_server")
serverCmd.Env = append(os.Environ(),
    "PORT="+port,
    "DATABASE_URL="+dbURL,
    "JWT_SECRET="+jwtSecret,
)
serverCmd.Start()
defer func() {
    serverCmd.Process.Signal(syscall.SIGTERM)
    serverCmd.Process.Kill()
}()
```

This approach avoids Docker entirely — just needs a running PostgreSQL (local or container). The test binary is built and cleaned up within the test function.

---

## Test Database

### Migration Strategy

Migrations live at `internal/db/migrations/001_init.sql` and are mounted into PostgreSQL's `docker-entrypoint-initdb.d`:

```sql
BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id          SERIAL          PRIMARY KEY,
    login       VARCHAR(50)     NOT NULL UNIQUE,
    image_url   TEXT,
    current_host VARCHAR(20),
    level       NUMERIC(4,2)    NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INT             NOT NULL,
    content     TEXT            NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ,

    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_content_length
        CHECK (char_length(content) <= 5000)
);

COMMIT;
```

### In-Test Schema Setup

For API integration tests that need a dedicated test database, `setupAPITestDB` in `internal/api/messages_test.go` creates tables directly:

```go
func setupAPITestDB(t *testing.T) (*db.Queries, func()) {
    databaseURL := os.Getenv("DATABASE_URL")
    if databaseURL == "" {
        databaseURL = "postgres://postgres:postgres@localhost:5432/42chat_test?sslmode=disable"
    }

    conn, err := sql.Open("postgres", databaseURL)
    if err != nil {
        t.Skipf("PostgreSQL não disponível: %v", err)
    }
    if err := conn.Ping(); err != nil {
        t.Skipf("PostgreSQL não acessível: %v", err)
    }

    // Create schema inline (matches migration structure)
    conn.Exec(`
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            login VARCHAR(50) UNIQUE NOT NULL,
            image_url TEXT NOT NULL DEFAULT '',
            current_host VARCHAR(20) NOT NULL DEFAULT '',
            level NUMERIC(4,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id INT NOT NULL REFERENCES users(id),
            content TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            deleted_at TIMESTAMP WITH TIME ZONE,
            CONSTRAINT chk_content_length CHECK (length(content) <= 5000)
        );
        TRUNCATE users, messages;
    `)

    queries := db.NewQueries(conn)

    cleanup := func() {
        conn.Exec("TRUNCATE users, messages")
        conn.Close()
    }

    return queries, cleanup
}
```

### Seed Data Pattern

After creating tables, seed data using the project's own query methods:

```go
// Seed a user
user := &model.User{
    ID: 1, Login: "marvin",
    ImageURL: "https://cdn.42.fr/marvin.jpg",
    Level: 9.87, CreatedAt: time.Now().UTC(),
}
queries.UpsertUser(user)

// Seed messages
for i := 0; i < 3; i++ {
    queries.InsertMessage(1, "test message")
}
```

### Cleanup Pattern

Every test that touches the database returns a `cleanup` function:

```go
func setupAPITestServer(t *testing.T, jwtSecret string) (
    *httptest.Server, *auth.JWTManager, func(),
) {
    queries, dbCleanup := setupAPITestDB(t)
    // ... setup router, handlers ...

    cleanup := func() {
        srv.Close()
        dbCleanup()
    }
    return srv, jwtMgr, cleanup
}

// Usage:
func TestSomething(t *testing.T) {
    srv, jwtMgr, cleanup := setupAPITestServer(t, "secret")
    defer cleanup()
    // tests here
}
```

### Skip When Unavailable

Tests that need PostgreSQL skip gracefully instead of failing:

```go
conn, err := sql.Open("postgres", databaseURL)
if err != nil {
    t.Skipf("PostgreSQL não disponível: %v (pulando testes de integração)", err)
}
if err := conn.Ping(); err != nil {
    t.Skipf("PostgreSQL não acessível: %v (pulando testes de integração)", err)
}
```

This allows `go test ./...` to pass even without a running database — unit tests run, integration tests skip.

### Fake DB for Unit Tests

For tests that need a `*db.Queries` but never actually execute SQL (e.g., WebSocket handler tests that don't call `InsertMessage`), use a "fake" connection:

```go
func testQueries(t *testing.T) *db.Queries {
    // sql.Open does not connect immediately — only on first Ping/Query.
    // Tests that never call InsertMessage don't need a real database.
    testDB, err := sql.Open("postgres",
        "host=localhost port=5432 dbname=42chat_test sslmode=disable")
    if err != nil {
        t.Fatalf("sql.Open: %v", err)
    }
    t.Cleanup(func() { testDB.Close() })
    return db.NewQueries(testDB)
}
```

---

## WebSocket Testing

### Server Setup with `httptest`

The WebSocket handler tests in `internal/ws/handler_test.go` use `httptest.NewServer` — a real HTTP server that listens on `127.0.0.1:0` (random port):

```go
func setupWSServer(t *testing.T) (*httptest.Server, *Hub, *auth.JWTManager) {
    hub := NewHub(nil)
    jwt := testJWTManager(t)       // auth.NewJWTManager("test-secret")
    queries := testQueries(t)      // fake *db.Queries (no real DB)
    handler := NewHandler(hub, jwt, queries)

    server := httptest.NewServer(http.HandlerFunc(handler.ServeHTTP))
    t.Cleanup(func() { server.Close() })

    return server, hub, jwt
}
```

### Connecting Clients

```go
func connectWSClient(t *testing.T, serverURL string, token string) *websocket.Conn {
    url := wsURL(serverURL) + "?token=" + token
    conn, resp, err := websocket.DefaultDialer.Dial(url, nil)
    if err != nil {
        if resp != nil {
            t.Fatalf("dial: %v (status=%d)", err, resp.StatusCode)
        }
        t.Fatalf("dial: %v", err)
    }
    t.Cleanup(func() { conn.Close() })
    return conn
}
```

### Reading and Verifying Messages

```go
func readWSMessage(t *testing.T, conn *websocket.Conn,
    timeout time.Duration) *model.WSMessage {

    conn.SetReadDeadline(time.Now().Add(timeout))
    _, data, err := conn.ReadMessage()
    if err != nil {
        t.Fatalf("ReadMessage: %v", err)
    }

    var msg model.WSMessage
    if err := json.Unmarshal(data, &msg); err != nil {
        t.Fatalf("unmarshal: %v (raw=%s)", err, string(data))
    }
    return &msg
}
```

### Writing Messages

```go
sendMsg := model.WSMessage{
    Type:    "message",
    Content: "hello from smoke test",
}
sendData, _ := json.Marshal(sendMsg)
conn.WriteMessage(websocket.TextMessage, sendData)
```

### Draining Join Messages

Every connect triggers a "join" system message broadcast to existing clients. Tests drain them before verifying:

```go
// Drain n messages from a WebSocket connection
func skipWSMessage(t *testing.T, conn *websocket.Conn, timeout time.Duration) {
    conn.SetReadDeadline(time.Now().Add(timeout))
    _, _, err := conn.ReadMessage()
    if err != nil {
        t.Fatalf("skip ReadMessage: %v", err)
    }
}

// Example: 3 clients, client[i] receives n-i join messages
for i, conn := range conns {
    for j := 0; j < n-i; j++ {
        skipWSMessage(t, conn, 2*time.Second)
    }
}
```

### Ping/Pong Testing

Test that the server sends pings and the connection stays alive:

```go
func TestWSHandlerPingPong(t *testing.T) {
    if testing.Short() {
        t.Skip("test requires ~35s — use -short=false")
    }
    server, _, jwt := setupWSServer(t)
    token := testToken(t, jwt, 42, "pinguser")
    conn := connectWSClient(t, server.URL, token)
    defer conn.Close()

    // Drain join
    skipWSMessage(t, conn, 2*time.Second)

    // Intercept pings from server
    pingReceived := make(chan struct{}, 2)
    conn.SetPingHandler(func(appData string) error {
        pingReceived <- struct{}{}
        conn.SetWriteDeadline(time.Now().Add(writeWait))
        return conn.WriteMessage(websocket.PongMessage, []byte(appData))
    })

    // Wait for at least one ping
    ctx, cancel := context.WithTimeout(context.Background(), 35*time.Second)
    defer cancel()
    select {
    case <-pingReceived:
        t.Log("ping received from server")
    case <-ctx.Done():
        t.Error("timeout: no ping received in 35s")
    }
}
```

### Graceful Shutdown Test

Verify that `hub.Shutdown()` notifies all connected clients:

```go
func TestWSHandlerGracefulShutdown(t *testing.T) {
    server, hub, jwt := setupWSServer(t)
    n := 2
    conns := make([]*websocket.Conn, n)

    for i := 0; i < n; i++ {
        login := "sduser" + string(rune('A'+i))
        token := testToken(t, jwt, i+10, login)
        conns[i] = connectWSClient(t, server.URL, token)
    }

    // Drain joins
    for i, conn := range conns {
        for j := 0; j < n-i; j++ {
            skipWSMessage(t, conn, 2*time.Second)
        }
    }

    // Trigger shutdown
    hub.Shutdown()

    // Verify all clients received shutdown message
    var wg sync.WaitGroup
    for i, conn := range conns {
        wg.Add(1)
        go func(idx int, c *websocket.Conn) {
            defer wg.Done()
            msg := readWSMessage(t, c, 3*time.Second)
            if msg.Type != "system" || msg.Content != "shutdown" {
                t.Errorf("client %d: bad shutdown msg", idx)
            }
        }(i, conn)
    }
    wg.Wait()
}
```

### Auth Rejection Tests

```go
// Invalid token → 401
func TestWSHandlerAuthRejection(t *testing.T) {
    server, _, _ := setupWSServer(t)
    url := wsURL(server.URL) + "?token=invalid-token"
    _, resp, err := websocket.DefaultDialer.Dial(url, nil)
    if err == nil {
        t.Error("expected auth error, but connection succeeded")
    }
    if resp != nil && resp.StatusCode != http.StatusUnauthorized {
        t.Errorf("status = %d, want %d", resp.StatusCode, http.StatusUnauthorized)
    }
}

// Missing token → 401
func TestWSHandlerMissingToken(t *testing.T) {
    server, _, _ := setupWSServer(t)
    url := wsURL(server.URL)  // no ?token=
    _, resp, err := websocket.DefaultDialer.Dial(url, nil)
    if err == nil {
        t.Error("expected error, but connection succeeded")
    }
    if resp != nil && resp.StatusCode != http.StatusUnauthorized {
        t.Errorf("status = %d, want %d", resp.StatusCode, http.StatusUnauthorized)
    }
}
```

---

## Table-Driven Tests

Go's idiomatic pattern for testing multiple input/output pairs. Used extensively in `internal/api/auth_test.go`.

### Basic Pattern

```go
func TestAuthMiddleware_InvalidFormat(t *testing.T) {
    srv, _ := setupAuthTestRouter(t, "test-secret")
    defer srv.Close()

    tests := []struct {
        name  string
        value string
    }{
        {"Basic auth", "Basic dXNlcjpwYXNz"},
        {"No prefix", "just-a-token-without-bearer"},
        {"Empty bearer", "Bearer "},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            req, _ := http.NewRequest("GET", srv.URL+"/api/protected", nil)
            req.Header.Set("Authorization", tt.value)

            resp, _ := http.DefaultClient.Do(req)
            defer resp.Body.Close()

            if resp.StatusCode != http.StatusUnauthorized {
                t.Errorf("%s: status = %d, want %d",
                    tt.name, resp.StatusCode, http.StatusUnauthorized)
            }
        })
    }
}
```

### With Multiple Fields

```go
tests := []struct {
    name       string
    userID     int
    login      string
    wantStatus int
    wantBody   string
}{
    {"valid user", 42, "marvin", http.StatusOK, `{"status":"ok"}`},
    {"zero ID", 0, "zero", http.StatusUnauthorized, ""},
    {"empty login", 99, "", http.StatusUnauthorized, ""},
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        // setup, execute, verify
    })
}
```

### Benefits

| Benefit | Explanation |
|---------|-------------|
| **Readability** | All cases visible in one data structure |
| **Additive** | Adding a new case = adding a struct literal, no new function |
| **Parallel-ready** | `t.Parallel()` inside each `t.Run` |
| **Subtests** | Each case runs as a named subtest — `go test -run "TestName/CaseName"` |
| **No boilerplate** | Same setup logic used for all cases |

---

## Hub Unit Testing (In-Memory)

The Hub (`internal/ws/hub.go`) is tested **without any network I/O** — clients are structs with `chan []byte` buffers:

### Broadcast Test

```go
func TestHubBroadcast(t *testing.T) {
    hub := NewHub(nil)
    n := 5
    clients := make([]*Client, n)

    for i := 0; i < n; i++ {
        clients[i] = &Client{
            UserID: i + 1,
            Login:  fmt.Sprintf("user%d", i+1),
            Send:   make(chan []byte, 256),
            Hub:    hub,
        }
        hub.Connect(clients[i])
    }

    // Drain join messages (client i receives n-i joins)
    for i, c := range clients {
        for j := 0; j < n-i; j++ {
            <-c.Send
        }
    }

    // Broadcast
    hub.Broadcast(&model.WSMessage{
        Type: "message", Content: "hello everyone",
    })

    // Verify all clients received
    for i, c := range clients {
        select {
        case data := <-c.Send:
            var msg model.WSMessage
            json.Unmarshal(data, &msg)
            if msg.Content != "hello everyone" {
                t.Errorf("client %d: wrong content", i)
            }
        default:
            t.Errorf("client %d: no message received", i)
        }
    }
}
```

### Concurrent Broadcast Test

Tests thread-safety with parallel broadcasters and consumers:

```go
func TestHubBroadcastConcurrent(t *testing.T) {
    hub := NewHub(nil)
    n := 10           // 10 clients
    broadcasters := 4  // 4 goroutines broadcasting
    iterations := 100  // 100 messages each

    // ... connect n clients, drain joins ...

    var wg sync.WaitGroup

    // Consumers
    received := make([]int, n)
    for i := 0; i < n; i++ {
        wg.Add(1)
        go func(idx int) {
            defer wg.Done()
            for range clients[idx].Send {
                received[idx]++
                if received[idx] >= totalMessages {
                    return
                }
            }
        }(i)
    }

    // Broadcasters
    for k := 0; k < broadcasters; k++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            for i := 0; i < iterations; i++ {
                hub.Broadcast(&model.WSMessage{
                    Type: "message",
                    Content: fmt.Sprintf("msg-%d-%d", id, i),
                })
            }
        }(k)
    }

    wg.Wait()

    for i := 0; i < n; i++ {
        if received[i] < totalMessages {
            t.Errorf("client %d: received %d, want >= %d",
                i, received[i], totalMessages)
        }
    }
}
```

---

## CI/CD Integration

### GitHub Actions Workflow (recommended)

```yaml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  integration:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: chat
          POSTGRES_PASSWORD: banana42
          POSTGRES_DB: chat
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U chat -d chat"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5
        volumes:
          - ./internal/db/migrations:/docker-entrypoint-initdb.d:ro

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version: "1.25"

      - name: Wait for PostgreSQL
        run: |
          for i in $(seq 1 30); do
            pg_isready -h localhost -U chat -d chat && break
            sleep 1
          done

      - name: Run tests
        env:
          DATABASE_URL: postgres://chat:banana42@localhost:5432/chat?sslmode=disable
          JWT_SECRET: ci-test-secret-do-not-use-in-production
        run: go test ./... -v -count=1 -timeout 5m

      - name: Run race detector
        env:
          DATABASE_URL: postgres://chat:banana42@localhost:5432/chat?sslmode=disable
          JWT_SECRET: ci-race-secret
        run: go test -race ./internal/ws/ ./internal/api/ -count=1 -timeout 5m
```

### Docker Compose in CI

Alternatively, use `docker compose` for a more realistic environment:

```yaml
jobs:
  integration-docker:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Start services
        run: |
          echo "JWT_SECRET=ci-test-secret" > .env
          docker compose up --build -d
          # Wait for health
          for i in $(seq 1 30); do
            health=$(docker inspect --format='{{.State.Health.Status}}' 42chat-server 2>/dev/null || true)
            [ "$health" = "healthy" ] && break
            sleep 2
          done
          docker compose ps

      - name: Run smoke tests
        env:
          DATABASE_URL: postgres://chat:banana42@localhost:5432/chat?sslmode=disable
          JWT_SECRET: ci-test-secret
        run: go test ./test/ -v -run TestSmoke -timeout 2m

      - name: Run all tests
        env:
          DATABASE_URL: postgres://chat:banana42@localhost:5432/chat?sslmode=disable
          JWT_SECRET: ci-test-secret
        run: go test ./... -v -count=1 -timeout 5m

      - name: Collect logs on failure
        if: failure()
        run: docker compose logs

      - name: Tear down
        if: always()
        run: docker compose down -v
```

### Test Categorization

| Tag | Command | Purpose |
|-----|---------|---------|
| **Short** | `go test -short ./...` | Skip slow tests (ping/pong, deadlines) |
| **Unit** | `go test ./internal/ws/ ./internal/auth/ ./internal/model/` | No external dependencies |
| **Integration** | `go test ./internal/api/ ./test/` | Needs PostgreSQL |
| **Race** | `go test -race ./internal/ws/` | Concurrency safety |
| **Smoke** | `go test ./test/ -run TestSmoke` | End-to-end sanity check |

### `testing.Short()` Usage

Long-running tests gate on `testing.Short()`:

```go
func TestWSHandlerPingPong(t *testing.T) {
    if testing.Short() {
        t.Skip("test requires ~35s — use -short=false")
    }
    // actual test...
}

func TestWSHandlerPongResetsDeadline(t *testing.T) {
    if testing.Short() {
        t.Skip("test requires multiple ping cycles — use -short=false")
    }
    // actual test...
}
```

---

## Test File Inventory

| File | Type | Dependencies |
|------|------|-------------|
| `test/smoke_test.go` | Smoke (3 levels) | PostgreSQL, server binary |
| `internal/ws/hub_test.go` | Unit (in-memory) | None |
| `internal/ws/handler_test.go` | Integration (httptest) | Fake DB, JWT |
| `internal/api/auth_test.go` | Unit (table-driven) | None |
| `internal/api/messages_test.go` | Integration | PostgreSQL |
| `internal/api/stats_test.go` | Integration | PostgreSQL |
| `internal/auth/middleware_test.go` | Unit | None |
| `internal/auth/jwt_test.go` | Unit | None |
| `internal/db/queries_test.go` | Integration | PostgreSQL |
| `internal/db/stats_test.go` | Integration | PostgreSQL |
| `internal/model/model_test.go` | Unit | None |
| `internal/config/config_test.go` | Unit | None |

---

## Key Principles

1. **Skip, don't fail** — tests that require external services skip gracefully when unavailable.
2. **Cleanup functions** — every setup returns a cleanup function; `defer cleanup()` in the test.
3. **Real connections for integration** — use `httptest.Server` + `gorilla/websocket` for WebSocket tests, not mocks.
4. **In-memory for unit** — Hub tests use channel-based clients, no network.
5. **Table-driven for coverage** — parameterize edge cases in a `[]struct` + `t.Run` loop.
6. **Graceful shutdown always verified** — every integration test checks that shutdown notifies clients and exits cleanly.
7. **`testing.Short()` for slow tests** — ping/pong and deadline tests skip in CI fast mode.
