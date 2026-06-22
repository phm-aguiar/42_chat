---
title: "Go Websocket Client"
category: references
tags: [go, websocket, real-time, patterns]
sources:
  - "wiki/_raw/go-websocket-client/SKILL.md"
summary: "Go Websocket Client: padrões e boas práticas para WebSocket em Go com gorilla/websocket. Fontes: gorilla/websocket docs, gorilla/websocket examples."
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

# Go WebSocket Client

## Basic Client

```go
func connect(url string) (*websocket.Conn, *http.Response, error) {
    dialer := websocket.DefaultDialer
    dialer.HandshakeTimeout = 10 * time.Second
    return dialer.Dial(url, nil)
}
```

## Reconnecting Client (Production)

```go
type ReconnectingClient struct {
    url        string
    conn       *websocket.Conn
    mu         sync.Mutex
    done       chan struct{}
    onMessage  func([]byte)
    onError    func(error)
    maxBackoff time.Duration
}

func NewReconnectingClient(url string) *ReconnectingClient {
    return &ReconnectingClient{
        url:        url,
        done:       make(chan struct{}),
        maxBackoff: 30 * time.Second,
    }
}

func (c *ReconnectingClient) Connect(ctx context.Context) error {
    backoff := time.Second

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
        }

        conn, _, err := websocket.DefaultDialer.Dial(c.url, nil)
        if err != nil {
            c.onError(fmt.Errorf("dial: %w (retry in %v)", err, backoff))
            select {
            case <-time.After(backoff):
                backoff *= 2
                if backoff > c.maxBackoff {
                    backoff = c.maxBackoff
                }
                continue
            case <-ctx.Done():
                return ctx.Err()
            }
        }

        c.mu.Lock()
        c.conn = conn
        c.mu.Unlock()

        backoff = time.Second // Reset on successful connection
        c.readLoop()

        // readLoop exited — connection lost
        select {
        case <-time.After(backoff):
            backoff *= 2
            if backoff > c.maxBackoff {
                backoff = c.maxBackoff
            }
        case <-ctx.Done():
            return ctx.Err()
        }
    }
}

func (c *ReconnectingClient) readLoop() {
    defer c.conn.Close()

    c.conn.SetPongHandler(func(string) error {
        c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        return nil
    })

    for {
        c.conn.SetReadDeadline(time.Now().Add(60 * time.Second))
        _, msg, err := c.conn.ReadMessage()
        if err != nil {
            if c.onError != nil {
                c.onError(err)
            }
            return
        }
        if c.onMessage != nil {
            c.onMessage(msg)
        }
    }
}

func (c *ReconnectingClient) Send(msg []byte) error {
    c.mu.Lock()
    defer c.mu.Unlock()

    if c.conn == nil {
        return fmt.Errorf("not connected")
    }
    c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
    return c.conn.WriteMessage(websocket.TextMessage, msg)
}

func (c *ReconnectingClient) SendJSON(v interface{}) error {
    c.mu.Lock()
    defer c.mu.Unlock()

    if c.conn == nil {
        return fmt.Errorf("not connected")
    }
    c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
    return c.conn.WriteJSON(v)
}

func (c *ReconnectingClient) Close() error {
    close(c.done)

    c.mu.Lock()
    defer c.mu.Unlock()

    if c.conn != nil {
        msg := websocket.FormatCloseMessage(websocket.CloseNormalClosure, "client closing")
        c.conn.WriteControl(websocket.CloseMessage, msg, time.Now().Add(time.Second))
        return c.conn.Close()
    }
    return nil
}
```

## Client with Heartbeat

```go
func (c *ReconnectingClient) heartbeat() {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            c.mu.Lock()
            if c.conn != nil {
                c.conn.SetWriteDeadline(time.Now().Add(10 * time.Second))
                c.conn.WriteMessage(websocket.PingMessage, nil)
            }
            c.mu.Unlock()
        case <-c.done:
            return
        }
    }
}
```

## Client with Message Queue (Offline Buffer)

```go
type BufferedClient struct {
    *ReconnectingClient
    buffer    [][]byte
    bufferMu  sync.Mutex
    maxBuffer int
}

func (c *BufferedClient) Send(msg []byte) error {
    c.bufferMu.Lock()
    defer c.bufferMu.Unlock()

    err := c.ReconnectingClient.Send(msg)
    if err != nil {
        // Queue message for when reconnected
        if len(c.buffer) < c.maxBuffer {
            c.buffer = append(c.buffer, msg)
        }
    }
    return err
}

func (c *BufferedClient) drainBuffer() {
    c.bufferMu.Lock()
    msgs := c.buffer
    c.buffer = nil
    c.bufferMu.Unlock()

    for _, msg := range msgs {
        c.ReconnectingClient.Send(msg)
    }
}
```

## TLS Configuration

```go
func createTLSClient(url string) (*websocket.Conn, error) {
    dialer := websocket.Dialer{
        HandshakeTimeout: 10 * time.Second,
        TLSClientConfig: &tls.Config{
            MinVersion: tls.VersionTLS12,
            // Custom CA for internal services
            RootCAs: customCAPool,
            // Skip verification for development only
            // InsecureSkipVerify: true, // NEVER in production
        },
    }
    return dialer.Dial(url, nil)
}
```

## Proxy Support

```go
func createProxiedClient(proxyURL, wsURL string) (*websocket.Conn, error) {
    proxy, err := url.Parse(proxyURL)
    if err != nil {
        return nil, err
    }

    dialer := websocket.Dialer{
        Proxy:            http.ProxyURL(proxy),
        HandshakeTimeout: 10 * time.Second,
    }
    return dialer.Dial(wsURL, nil)
}
```

## Related Skills

- **Core WebSocket**: See [[go-websocket-core]]
- **Error handling**: See [[go-error-handling]]
- **Concurrency**: See [[go-concurrency]]

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de padrões Go
- [[go-concurrency|Concurrency]]
- [[go-error-handling|Error Handling]]
- [[go-websocket-core|Websocket Core]]
