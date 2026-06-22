---
title: "Go Websocket Testing"
category: references
tags: [go, websocket, real-time, patterns]
sources:
  - "wiki/_raw/go-websocket-testing/SKILL.md"
summary: "Go Websocket Testing: padrões e boas práticas para WebSocket em Go com gorilla/websocket. Fontes: gorilla/websocket docs, Go testing docs."
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

# Go WebSocket Testing

## Testing Strategy

| Level | What | Tools |
|-------|------|-------|
| Unit | Message handlers, serialization, business logic | Standard `testing` |
| Integration | Client ↔ Server, upgrade, message exchange | `httptest.Server` + gorilla client |
| E2E | Full hub with multiple clients, race conditions | goroutine-based test with sync |

## Test Server Helper

```go
func newTestServer(t *testing.T, handler http.HandlerFunc) (*httptest.Server, string) {
    t.Helper()
    s := httptest.NewServer(handler)
    t.Cleanup(s.Close)

    wsURL := "ws" + strings.TrimPrefix(s.URL, "http")
    return s, wsURL
}
```

## Testing Connection Upgrade

```go
func TestWebSocketUpgrade(t *testing.T) {
    upgrader := websocket.Upgrader{
        CheckOrigin: func(r *http.Request) bool { return true },
    }

    handler := func(w http.ResponseWriter, r *http.Request) {
        conn, err := upgrader.Upgrade(w, r, nil)
        if err != nil {
            t.Errorf("upgrade failed: %v", err)
            return
        }
        defer conn.Close()
    }

    s := httptest.NewServer(http.HandlerFunc(handler))
    defer s.Close()

    url := "ws" + strings.TrimPrefix(s.URL, "http")
    conn, _, err := websocket.DefaultDialer.Dial(url, nil)
    if err != nil {
        t.Fatalf("dial failed: %v", err)
    }
    defer conn.Close()
}
```

## Testing Message Exchange

```go
func TestEchoServer(t *testing.T) {
    upgrader := websocket.Upgrader{
        CheckOrigin: func(r *http.Request) bool { return true },
    }

    handler := func(w http.ResponseWriter, r *http.Request) {
        conn, _ := upgrader.Upgrade(w, r, nil)
        defer conn.Close()

        for {
            mt, msg, err := conn.ReadMessage()
            if err != nil {
                return
            }
            conn.WriteMessage(mt, msg)
        }
    }

    s := httptest.NewServer(http.HandlerFunc(handler))
    defer s.Close()

    url := "ws" + strings.TrimPrefix(s.URL, "http")
    conn, _, _ := websocket.DefaultDialer.Dial(url, nil)
    defer conn.Close()

    // Send and verify echo
    testMessages := []struct {
        name string
        msg  string
    }{
        {"text", "hello world"},
        {"json", `{"type":"ping"}`},
        {"empty", ""},
        {"unicode", "こんにちは"},
    }

    for _, tc := range testMessages {
        t.Run(tc.name, func(t *testing.T) {
            err := conn.WriteMessage(websocket.TextMessage, []byte(tc.msg))
            if err != nil {
                t.Fatalf("write: %v", err)
            }

            _, reply, err := conn.ReadMessage()
            if err != nil {
                t.Fatalf("read: %v", err)
            }

            if string(reply) != tc.msg {
                t.Errorf("want %q, got %q", tc.msg, string(reply))
            }
        })
    }
}
```

## Testing Hub Pattern

```go
func TestHubBroadcast(t *testing.T) {
    hub := NewHub()
    go hub.Run()

    s, wsURL := newTestServer(t, func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    })

    // Connect 3 clients
    var conns []*websocket.Conn
    for i := 0; i < 3; i++ {
        conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
        if err != nil {
            t.Fatalf("client %d: %v", i, err)
        }
        defer conn.Close()
        conns = append(conns, conn)
    }

    // Wait for all to register
    time.Sleep(100 * time.Millisecond)

    if hub.Count() != 3 {
        t.Errorf("want 3 clients, got %d", hub.Count())
    }

    // Client 0 sends a message
    conns[0].WriteMessage(websocket.TextMessage, []byte("broadcast me"))

    // All other clients should receive it
    for i := 1; i < 3; i++ {
        conns[i].SetReadDeadline(time.Now().Add(time.Second))
        _, msg, err := conns[i].ReadMessage()
        if err != nil {
            t.Errorf("client %d: %v", i, err)
            continue
        }
        if string(msg) != "broadcast me" {
            t.Errorf("client %d: want %q, got %q", i, "broadcast me", string(msg))
        }
    }
}
```

## Testing with Context Cancellation

```go
func TestGracefulShutdown(t *testing.T) {
    hub := NewHub()
    go hub.Run()

    handler := func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    }

    s := httptest.NewServer(http.HandlerFunc(handler))
    defer s.Close()

    wsURL := "ws" + strings.TrimPrefix(s.URL, "http")
    conn, _, _ := websocket.DefaultDialer.Dial(wsURL, nil)
    defer conn.Close()

    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    err := hub.Shutdown(ctx)
    if err != nil {
        t.Errorf("shutdown: %v", err)
    }

    if hub.Count() != 0 {
        t.Errorf("hub still has %d clients after shutdown", hub.Count())
    }
}
```

## Testing Race Conditions

```go
func TestConcurrentClients(t *testing.T) {
    hub := NewHub()
    go hub.Run()

    handler := func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    }
    s := httptest.NewServer(http.HandlerFunc(handler))
    defer s.Close()

    wsURL := "ws" + strings.TrimPrefix(s.URL, "http")

    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            conn, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
            if err != nil {
                t.Errorf("client %d: dial: %v", id, err)
                return
            }
            defer conn.Close()

            for j := 0; j < 100; j++ {
                msg := fmt.Sprintf("client-%d-msg-%d", id, j)
                conn.WriteMessage(websocket.TextMessage, []byte(msg))
                time.Sleep(time.Millisecond)
            }
        }(i)
    }

    wg.Wait()
}
```

## Mock Connection for Unit Tests

```go
type MockWSConn struct {
    ReadMessages  [][]byte
    WrittenMessages [][]byte
    readIdx       int
}

func (m *MockWSConn) ReadMessage() (int, []byte, error) {
    if m.readIdx >= len(m.ReadMessages) {
        return 0, nil, io.EOF
    }
    msg := m.ReadMessages[m.readIdx]
    m.readIdx++
    return websocket.TextMessage, msg, nil
}

func (m *MockWSConn) WriteMessage(mt int, data []byte) error {
    m.WrittenMessages = append(m.WrittenMessages, data)
    return nil
}

// Usage in message handler tests
func TestMessageHandler(t *testing.T) {
    mock := &MockWSConn{
        ReadMessages: [][]byte{
            []byte(`{"type":"chat","body":"hello"}`),
            []byte(`{"type":"typing","user":"alice"}`),
        },
    }

    handler := NewMessageHandler(mock)
    handler.Process()

    if len(mock.WrittenMessages) != 2 {
        t.Errorf("want 2 responses, got %d", len(mock.WrittenMessages))
    }
}
```

## Related Skills

- **Core WebSocket**: See [[go-websocket-core]]
- **Go Testing**: See [[go-testing]]
- **Race Detection**: Run tests with `go test -race ./...`

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de padrões Go
- [[go-testing|Testing]]
- [[go-websocket-core|Websocket Core]]
