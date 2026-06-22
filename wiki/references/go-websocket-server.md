---
title: "Go Websocket Server"
category: references
tags: [go, websocket, real-time, patterns]
sources:
  - "wiki/_raw/go-websocket-server/SKILL.md"
summary: "Go Websocket Server: padrões e boas práticas para WebSocket em Go com gorilla/websocket. Fontes: gorilla/websocket docs, Go net/http docs, websocket.org."
provenance:
  extracted: 0.40
  inferred: 0.55
  ambiguous: 0.05
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: "2026-06-16T00:00:00Z"
rag_score: 0.48
updated: "2026-06-16T00:00:00Z"
---

# Go WebSocket Server Integration

## Framework Integration

### net/http (stdlib)

```go
func main() {
    hub := NewHub()
    go hub.Run()

    mux := http.NewServeMux()
    mux.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    })
    mux.HandleFunc("/health", healthHandler)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  15 * time.Second,
        WriteTimeout: 15 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    go func() {
        log.Printf("listening on %s", srv.Addr)
        if err := srv.ListenAndServe(); err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // Graceful shutdown
    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit
    log.Println("shutting down...")

    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()
    srv.Shutdown(ctx)
}
```

### go-chi

```go
func main() {
    hub := NewHub()
    go hub.Run()

    r := chi.NewRouter()
    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Timeout(60 * time.Second))

    r.Get("/ws", func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    })

    srv := &http.Server{Addr: ":8080", Handler: r}
    srv.ListenAndServe()
}
```

### gin

```go
func serveWsGin(hub *Hub, c *gin.Context) {
    conn, err := upgrader.Upgrade(c.Writer, c.Request, nil)
    if err != nil {
        log.Printf("upgrade error: %v", err)
        return
    }
    client := &Client{hub: hub, conn: conn, send: make(chan []byte, 256)}
    hub.register <- client
    go client.writePump()
    go client.readPump()
}

func main() {
    hub := NewHub()
    go hub.Run()

    r := gin.Default()
    r.GET("/ws", func(c *gin.Context) {
        serveWsGin(hub, c)
    })
    r.Run(":8080")
}
```

## Authentication

### Token in Query Parameter

```go
func serveWsWithAuth(hub *Hub, w http.ResponseWriter, r *http.Request) {
    token := r.URL.Query().Get("token")
    userID, err := validateToken(token)
    if err != nil {
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }

    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }

    client := &Client{
        hub:    hub,
        conn:   conn,
        send:   make(chan []byte, 256),
        userID: userID,
    }
    hub.register <- client
    go client.writePump()
    go client.readPump()
}
```

### Cookie-Based (Same Origin)

```go
func serveWsWithCookie(hub *Hub, w http.ResponseWriter, r *http.Request) {
    cookie, err := r.Cookie("session")
    if err != nil {
        http.Error(w, "unauthorized", http.StatusUnauthorized)
        return
    }
    // Validate session cookie
    _ = cookie
    // ... continue with upgrade
}
```

### Token in Protocol Header (during Dial)

```go
// Client side
header := http.Header{}
header.Set("Sec-WebSocket-Protocol", "access_token,"+token)
conn, _, err := dialer.Dial(url, header)

// Server side — use Subprotocols
var upgrader = websocket.Upgrader{
    Subprotocols: []string{"access_token"},
}
```

## CORS Configuration

```go
func corsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Access-Control-Allow-Origin", "https://myapp.com")
        w.Header().Set("Access-Control-Allow-Credentials", "true")

        if r.Method == http.MethodOptions {
            w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
            w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
            w.WriteHeader(http.StatusOK)
            return
        }
        next.ServeHTTP(w, r)
    })
}
```

## Graceful Shutdown Sequence

```
SIGTERM/SIGINT received
    │
    ▼
Stop accepting new HTTP connections
    │
    ▼
Close Hub register channel → stop new WS upgrades
    │
    ▼
For each connected Client:
    ├── Send Close frame (1001 Going Away)
    ├── Close client.send channel
    └── Wait for readPump to exit
    │
    ▼
http.Server.Shutdown(ctx) with timeout
    │
    ▼
Process exits
```

```go
func (h *Hub) Shutdown(ctx context.Context) error {
    // Stop accepting new clients
    close(h.register)

    // Close all existing clients
    h.mu.Lock()
    for client := range h.clients {
        msg := websocket.FormatCloseMessage(
            websocket.CloseGoingAway,
            "server shutting down",
        )
        client.conn.WriteControl(
            websocket.CloseMessage, msg,
            time.Now().Add(time.Second),
        )
        close(client.send)
    }
    h.mu.Unlock()

    // Wait for all writePumps to finish
    deadline := time.After(ctx.Deadline().Sub(time.Now()))
    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-deadline:
            return ctx.Err()
        case <-ticker.C:
            if h.Count() == 0 {
                return nil
            }
        }
    }
}
```

## Rate Limiting

```go
type RateLimiter struct {
    mu       sync.Mutex
    attempts map[string]*rateData
}

type rateData struct {
    count    int
    resetAt  time.Time
}

func (rl *RateLimiter) Allow(ip string) bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()

    data, exists := rl.attempts[ip]
    now := time.Now()

    if !exists || now.After(data.resetAt) {
        rl.attempts[ip] = &rateData{count: 1, resetAt: now.Add(time.Minute)}
        return true
    }

    if data.count >= 60 { // Max 60 connections/minute per IP
        return false
    }

    data.count++
    return true
}
```

## Related Skills

- **Core WebSocket**: See [[go-websocket-core]]
- **Hub Pattern**: See [[go-websocket-hub]]
- **Client Pattern**: See [[go-websocket-client]]

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de padrões Go
- [[go-websocket-client|Websocket Client]]
- [[go-websocket-core|Websocket Core]]
- [[go-websocket-hub|Websocket Hub]]
