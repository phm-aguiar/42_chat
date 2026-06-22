---
title: "Go Websocket Hub"
category: references
tags: [go, websocket, real-time, patterns]
sources:
  - "wiki/_raw/go-websocket-hub/SKILL.md"
summary: "Go Websocket Hub: padrões e boas práticas para WebSocket em Go com gorilla/websocket. Fontes: gorilla/websocket examples, gorilla/websocket chat example, websocket.org Go guide."
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

# Go WebSocket Hub Pattern

The Hub pattern is **the** production pattern for multi-client WebSocket servers.
One central goroutine serializes all client operations (register, unregister,
broadcast), avoiding concurrent write panics.

## Hub Architecture

```
                    ┌──────────┐
                    │   Hub    │
                    │  (1 goroutine)  │
                    └────┬─────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
      ┌─────────┐  ┌─────────┐  ┌─────────┐
      │ Client A│  │ Client B│  │ Client C│
      │ read    │  │ read    │  │ read    │
      │ write   │  │ write   │  │ write   │
      └─────────┘  └─────────┘  └─────────┘
```

## Full Implementation

```go
package main

import (
    "log"
    "net/http"
    "sync"
    "time"

    "github.com/gorilla/websocket"
)

// ============================================================
// Hub
// ============================================================

type Hub struct {
    clients    map[*Client]bool
    broadcast  chan []byte
    register   chan *Client
    unregister chan *Client
    mu         sync.RWMutex // For read-only operations like Count()
}

func NewHub() *Hub {
    return &Hub{
        clients:    make(map[*Client]bool),
        broadcast:  make(chan []byte, 256),
        register:   make(chan *Client),
        unregister: make(chan *Client),
    }
}

func (h *Hub) Run() {
    for {
        select {
        case client := <-h.register:
            h.mu.Lock()
            h.clients[client] = true
            h.mu.Unlock()
            log.Printf("client connected: %d total", len(h.clients))

        case client := <-h.unregister:
            h.mu.Lock()
            if _, ok := h.clients[client]; ok {
                delete(h.clients, client)
                close(client.send)
            }
            h.mu.Unlock()
            log.Printf("client disconnected: %d total", len(h.clients))

        case message := <-h.broadcast:
            h.mu.RLock()
            for client := range h.clients {
                select {
                case client.send <- message:
                default:
                    // Client buffer full — slow consumer
                    close(client.send)
                    delete(h.clients, client)
                }
            }
            h.mu.RUnlock()
        }
    }
}

func (h *Hub) Count() int {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return len(h.clients)
}

// ============================================================
// Client
// ============================================================

type Client struct {
    hub  *Hub
    conn *websocket.Conn
    send chan []byte
}

const (
    writeWait      = 10 * time.Second
    pongWait       = 60 * time.Second
    pingPeriod     = (pongWait * 9) / 10
    maxMessageSize = 4096
)

func (c *Client) readPump() {
    defer func() {
        c.hub.unregister <- c
        c.conn.Close()
    }()

    c.conn.SetReadLimit(maxMessageSize)
    c.conn.SetReadDeadline(time.Now().Add(pongWait))
    c.conn.SetPongHandler(func(string) error {
        c.conn.SetReadDeadline(time.Now().Add(pongWait))
        return nil
    })

    for {
        _, message, err := c.conn.ReadMessage()
        if err != nil {
            break
        }
        // Broadcast received message to all clients
        c.hub.broadcast <- message
    }
}

func (c *Client) writePump() {
    ticker := time.NewTicker(pingPeriod)
    defer func() {
        ticker.Stop()
        c.conn.Close()
    }()

    for {
        select {
        case message, ok := <-c.send:
            c.conn.SetWriteDeadline(time.Now().Add(writeWait))
            if !ok {
                c.conn.WriteMessage(websocket.CloseMessage, []byte{})
                return
            }
            if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
                return
            }
        case <-ticker.C:
            c.conn.SetWriteDeadline(time.Now().Add(writeWait))
            if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
                return
            }
        }
    }
}

// ============================================================
// HTTP Handler
// ============================================================

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // Configure for production
    },
}

func serveWs(hub *Hub, w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Printf("upgrade error: %v", err)
        return
    }

    client := &Client{
        hub:  hub,
        conn: conn,
        send: make(chan []byte, 256),
    }
    hub.register <- client

    go client.writePump()
    go client.readPump()
}

// ============================================================
// Main
// ============================================================

func main() {
    hub := NewHub()
    go hub.Run()

    http.HandleFunc("/ws", func(w http.ResponseWriter, r *http.Request) {
        serveWs(hub, w, r)
    })

    log.Fatal(http.ListenAndServe(":8080", nil))
}
```

## Rooms Pattern

Extend Hub with room support:

```go
type Room struct {
    name    string
    clients map[*Client]bool
}

type Hub struct {
    rooms      map[string]*Room
    broadcast  chan *Message
    register   chan *Subscription
    unregister chan *Subscription
}

type Message struct {
    Room string
    Data []byte
}

type Subscription struct {
    Room   string
    Client *Client
}

func (h *Hub) Run() {
    for {
        select {
        case sub := <-h.register:
            room := h.rooms[sub.Room]
            if room == nil {
                room = &Room{name: sub.Room, clients: make(map[*Client]bool)}
                h.rooms[sub.Room] = room
            }
            room.clients[sub.Client] = true

        case sub := <-h.unregister:
            if room, ok := h.rooms[sub.Room]; ok {
                delete(room.clients, sub.Client)
                close(sub.Client.send)
            }

        case msg := <-h.broadcast:
            if room, ok := h.rooms[msg.Room]; ok {
                for client := range room.clients {
                    select {
                    case client.send <- msg.Data:
                    default:
                        delete(room.clients, client)
                        close(client.send)
                    }
                }
            }
        }
    }
}
```

## Direct Messaging

```go
func (h *Hub) SendToUser(userID string, message []byte) error {
    h.mu.RLock()
    defer h.mu.RUnlock()

    for client := range h.clients {
        if client.userID == userID {
            select {
            case client.send <- message:
                return nil
            default:
                return fmt.Errorf("client buffer full")
            }
        }
    }
    return fmt.Errorf("user not connected: %s", userID)
}
```

## Metrics

```go
type HubMetrics struct {
    Connections    int64
    MessagesSent   int64
    MessagesRecv   int64
    BroadcastCount int64
}

func (h *Hub) Metrics() HubMetrics {
    h.mu.RLock()
    defer h.mu.RUnlock()
    return HubMetrics{
        Connections: int64(len(h.clients)),
    }
}
```

## Related Skills

- **Core WebSocket**: See [[go-websocket-core]] for connection lifecycle and message handling
- **Graceful shutdown**: See [[go-websocket-server]] for server integration patterns
- **Concurrency**: See [[go-concurrency]] for goroutine and channel patterns

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de padrões Go
- [[go-concurrency|Concurrency]]
- [[go-websocket-core|Websocket Core]]
- [[go-websocket-server|Websocket Server]]
