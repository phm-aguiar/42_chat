---
title: "Go WebSocket Core"
category: references
tags: [go, websocket, real-time, patterns]
sources:
  - "wiki/_raw/go-websocket-core/SKILL.md"
summary: "Go WebSocket Core: padrões e boas práticas para WebSocket em Go com gorilla/websocket. Fontes: gorilla/websocket official docs, websocket.org Go guide, gorilla/websocket GitHub."
provenance:
  extracted: 0.40
  inferred: 0.55
  ambiguous: 0.05
base_confidence: 0.62
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: core
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
---

# Go WebSocket Core (gorilla/websocket)

> **Package:** `github.com/gorilla/websocket` — The de facto WebSocket library for Go.
> Fast, well-tested, RFC 6455 compliant. Used in production by Docker, Kubernetes, and thousands of Go services.

## Quick Reference

| Operation | Method | Thread-safe? |
|-----------|--------|--------------|
| Upgrade HTTP → WS | `upgrader.Upgrade(w, r, nil)` | Per-connection |
| Dial server | `websocket.DefaultDialer.Dial(url, nil)` | Per-connection |
| Read message | `conn.ReadMessage()` | One goroutine only |
| Write message | `conn.WriteMessage(mt, data)` | One goroutine only |
| Write JSON | `conn.WriteJSON(v)` | One goroutine only |
| Read JSON | `conn.ReadJSON(&v)` | One goroutine only |
| Close connection | `conn.WriteMessage(CloseMessage, ...)` | Write goroutine |
| Set read deadline | `conn.SetReadDeadline(t)` | Read goroutine |
| Set write deadline | `conn.SetWriteDeadline(t)` | Write goroutine |
| Ping handler | `conn.SetPingHandler(fn)` | Before read loop |

## Installation and Setup

```go
import "github.com/gorilla/websocket"

// go get github.com/gorilla/websocket
```

### Upgrader Configuration

The `Upgrader` converts HTTP connections to WebSocket. **Always specify CheckOrigin in production.**

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,  // 1 KB for chat/notifications
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        // Production: validate against allowed origins
        origin := r.Header.Get("Origin")
        return origin == "https://myapp.com" || origin == "https://dev.myapp.com"
    },
    EnableCompression: false, // Enable for large text messages
    HandshakeTimeout:  10 * time.Second,
    // Subprotocol negotiation
    Subprotocols: []string{"chat-v1", "chat-v2"},
}
```

**Buffer size guide:**

| Message size | ReadBufferSize | WriteBufferSize |
|---|---|---|
| Chat, notifications (< 1 KB) | 1024 | 1024 |
| JSON API payloads (1–64 KB) | 4096 | 4096 |
| File transfers, media (> 64 KB) | 32768 | 32768 |

## Connection Lifecycle

```
HTTP Request → Upgrader.Upgrade() → *websocket.Conn
                                          │
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                     ReadMessage()   WriteMessage()   Set*Deadline()
                          │               │               │
                          └───────────────┼───────────────┘
                                          ▼
                              Close(CloseNormalClosure)
```

### Server-Side Upgrade

```go
func serveWs(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Printf("upgrade error: %v", err)
        return
    }
    defer conn.Close()

    // Set initial deadlines
    conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    conn.SetPongHandler(func(string) error {
        conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        return nil
    })

    for {
        messageType, message, err := conn.ReadMessage()
        if err != nil {
            if websocket.IsUnexpectedCloseError(err,
                websocket.CloseGoingAway, websocket.CloseNormalClosure) {
                log.Printf("error: %v", err)
            }
            break
        }
        // Process message
        _ = messageType
        _ = message
    }
}
```

### Client-Side Dial

```go
func connectWebSocket(urlStr string) (*websocket.Conn, error) {
    dialer := websocket.DefaultDialer
    dialer.HandshakeTimeout = 10 * time.Second

    conn, _, err := dialer.Dial(urlStr, nil)
    if err != nil {
        return nil, fmt.Errorf("dial: %w", err)
    }
    return conn, nil
}

// With custom headers (auth token)
func connectWithAuth(urlStr, token string) (*websocket.Conn, error) {
    header := http.Header{}
    header.Set("Authorization", "Bearer "+token)

    conn, _, err := websocket.DefaultDialer.Dial(urlStr, header)
    if err != nil {
        return nil, fmt.Errorf("dial: %w", err)
    }
    return conn, nil
}
```

## Message Types

```go
const (
    TextMessage   = 1  // UTF-8 text (JSON, chat messages)
    BinaryMessage = 2  // Raw bytes (protobuf, images, compressed data)
    CloseMessage  = 8  // Control: close handshake
    PingMessage   = 9  // Control: keepalive request
    PongMessage   = 10 // Control: keepalive response
)
```

### Reading Messages

```go
// Simple read — blocks until message or error
messageType, payload, err := conn.ReadMessage()
if err != nil {
    // Handle error
}

// Advanced: streaming reader for large messages
messageType, reader, err := conn.NextReader()
if err != nil {
    return err
}
// Read from reader incrementally
```

### Writing Messages

```go
// Write text
err := conn.WriteMessage(websocket.TextMessage, []byte("hello"))

// Write JSON struct
type Event struct {
    Type string `json:"type"`
    Data string `json:"data"`
}
err := conn.WriteJSON(Event{Type: "chat", Data: "hello"})

// Write multiple message types atomically (single write lock)
writer, err := conn.NextWriter(websocket.TextMessage)
if err != nil {
    return err
}
writer.Write([]byte("part1"))
writer.Write([]byte("part2"))
writer.Close() // Flushes the frame
```

## Concurrent Safety — The Golden Rule

> **One goroutine reads, one goroutine writes. Never two goroutines writing.**

gorilla/websocket **panics** if two goroutines call `WriteMessage` concurrently.
This is the #1 production bug.

```go
// CORRECT: Separate goroutines
go readLoop(conn)   // Only this goroutine calls ReadMessage
go writeLoop(conn)  // Only this goroutine calls WriteMessage

// WRONG: Will panic!
go func() { conn.WriteMessage(...) }()
go func() { conn.WriteMessage(...) }() // PANIC: concurrent write

// SOLUTION: Channel-based write pump
func writeLoop(conn *websocket.Conn, send chan []byte) {
    defer conn.Close()
    for msg := range send {
        if err := conn.WriteMessage(websocket.TextMessage, msg); err != nil {
            return
        }
    }
}
```

## Ping/Pong Keepalive

WebSocket connections can silently die (proxies, NAT, network issues). Ping/Pong detects dead connections.

```go
const (
    pongWait   = 60 * time.Second
    pingPeriod = (pongWait * 9) / 10 // 54s — send ping before pong deadline
    maxMessageSize = 512
)

func readLoop(conn *websocket.Conn) {
    defer conn.Close()
    conn.SetReadLimit(maxMessageSize)
    conn.SetReadDeadline(time.Now().Add(pongWait))
    conn.SetPongHandler(func(string) error {
        conn.SetReadDeadline(time.Now().Add(pongWait))
        return nil
    })

    for {
        _, message, err := conn.ReadMessage()
        if err != nil {
            break
        }
        handle(message)
    }
}

func writeLoop(conn *websocket.Conn, send chan []byte) {
    ticker := time.NewTicker(pingPeriod)
    defer func() {
        ticker.Stop()
        conn.Close()
    }()

    for {
        select {
        case message, ok := <-send:
            if !ok {
                conn.WriteMessage(websocket.CloseMessage, []byte{})
                return
            }
            if err := conn.WriteMessage(websocket.TextMessage, message); err != nil {
                return
            }
        case <-ticker.C:
            if err := conn.WriteMessage(websocket.PingMessage, nil); err != nil {
                return
            }
        }
    }
}
```

## Graceful Shutdown

```go
func shutdown(conn *websocket.Conn) error {
    // Send close frame to peer
    deadline := time.Now().Add(5 * time.Second)
    msg := websocket.FormatCloseMessage(websocket.CloseNormalClosure, "server shutting down")
    conn.WriteControl(websocket.CloseMessage, msg, deadline)

    // Wait for peer's close frame
    conn.SetReadDeadline(time.Now().Add(5 * time.Second))
    for {
        if _, _, err := conn.ReadMessage(); err != nil {
            return err // Expected: close error
        }
    }
}

// Drain: close send channel, wait for read loop to finish
func drainClient(client *Client) {
    close(client.send)
    // readLoop will detect channel close and return
}
```

## Error Handling

```go
// Classify close errors
if websocket.IsCloseError(err,
    websocket.CloseNormalClosure,    // 1000: normal
    websocket.CloseGoingAway,        // 1001: navigating away
    websocket.CloseNoStatusReceived, // 1005: no status
) {
    // Expected disconnection — no log needed
    return
}

// Unexpected close — log for debugging
if websocket.IsUnexpectedCloseError(err,
    websocket.CloseGoingAway,
    websocket.CloseNormalClosure,
) {
    log.Printf("unexpected close: %v", err)
}
```

## Origin Validation (Critical for Security)

```go
var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        origin := r.Header.Get("Origin")
        switch origin {
        case "https://myapp.com",
             "https://staging.myapp.com":
            return true
        }
        // Development
        if strings.HasPrefix(r.Host, "localhost") {
            return true
        }
        return false
    },
}

// NEVER in production:
// CheckOrigin: func(r *http.Request) bool { return true }
```

## Production Checklist

- [ ] `CheckOrigin` validates against allowed domains (not `return true`)
- [ ] Read and write happen in separate goroutines
- [ ] Ping/Pong keepalive configured (pongWait, pingPeriod)
- [ ] `SetReadLimit` prevents memory exhaustion from large messages
- [ ] Read/Write deadlines prevent hanging connections
- [ ] Graceful shutdown sends close frame before `conn.Close()`
- [ ] Buffer sizes tuned for message sizes
- [ ] Error handling classifies close codes (expected vs unexpected)
- [ ] TLS termination at reverse proxy (nginx/Caddy) for wss://
- [ ] Metrics exported: connection count, message rate, error rate

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| `CheckOrigin: return true` | CSRF — any website can connect | Validate origin list |
| Concurrent writes | `panic: concurrent write to websocket connection` | Channel-based write pump |
| No ping/pong | Dead connections leak forever | pongWait + pingPeriod |
| No read deadline | Slow/malicious clients consume goroutines | `SetReadDeadline` with pong reset |
| `conn.Close()` without close frame | Peer sees abrupt TCP close, not clean shutdown | `WriteMessage(CloseMessage, ...)` first |
| Blocking read loop | Cannot send close message | Use select with done channel |
| Ignoring message type | Binary treated as text causes corruption | Check `messageType` |

## Related Skills

- **Hub pattern**: See [[go-websocket-hub]] when broadcasting to multiple clients
- **Server setup**: See [[go-websocket-server]] when integrating with HTTP routers
- **Client patterns**: See [[go-websocket-client]] for client-side reconnection and resilience
- **Testing**: See [[go-websocket-testing]] for WebSocket test strategies
- **Error handling**: See [[go-error-handling]] for general Go error patterns
- **Concurrency**: See [[go-concurrency]] for goroutine and channel patterns

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de padrões Go
- [[go-concurrency|Concurrency]]
- [[go-error-handling|Error Handling]]
- [[go-websocket-client|Websocket Client]]
- [[go-websocket-hub|Websocket Hub]]
- [[go-websocket-server|Websocket Server]]
- [[go-websocket-testing|Websocket Testing]]
