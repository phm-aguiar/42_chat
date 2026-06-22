---
title: "WebSocket (Protocolo)"
tags: [entity, glossary]
aliases: [WS, gorilla/websocket, real-time, Protocolo WebSocket, RFC 6455]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: WebSocket é o protocolo de comunicação full-duplex em tempo real do 42 Chat — upgrade HTTP → WS, mensagens JSON, ping/pong keepalive, implementado com a biblioteca gorilla/websocket.
provenance:
  extracted: 0.90
  inferred: 0.10
  ambiguous: 0.00
---

# WebSocket (Protocolo)

## Definição

**WebSocket** (RFC 6455) é o protocolo de comunicação full-duplex sobre TCP que permite troca de mensagens em tempo real entre cliente e servidor. No 42 Chat, é implementado com a biblioteca [`gorilla/websocket`](https://github.com/gorilla/websocket) (v1.5.3). A conexão é estabelecida via upgrade HTTP e mantida com ping/pong keepalive.

## No Projeto

### Upgrade HTTP → WebSocket

O endpoint `/ws` exposto pelo router [`Chi`](chi.md) é servido pelo `ws.Handler`:

```go
r.Get("/ws", wsHandler.ServeHTTP)
```

O `ServeHTTP` realiza as seguintes etapas:

1. **Validação JWT**: extrai token do query param `?token=` ou header `Sec-WebSocket-Protocol`.
2. **Upgrade**: chama `upgrader.Upgrade(w, r, nil)` — configura ReadBufferSize/WriteBufferSize de 1024 bytes, CheckOrigin sempre `true` (MVP local).
3. **Criação do Client**: instancia `ws.Client` com UserID, Login, canal `Send` (buffer 256), e referência ao Hub.
4. **Registro + Pumps**: conecta ao Hub e dispara goroutines `readPump` / `writePump`.

### Keepalive (Ping/Pong)

| Constante | Valor | Descrição |
|-----------|-------|-----------|
| `writeWait` | 10s | Deadline para escrita de uma mensagem |
| `pongWait` | 60s | Tempo máximo aguardando pong do cliente |
| `pingPeriod` | 30s | Intervalo entre pings enviados pelo servidor |

O servidor envia **ping** a cada 30s. O cliente responde com **pong**, que reseta o deadline de leitura para +60s. Se o cliente não responder em 60s, a conexão é fechada.

### Upgrader

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // MVP: aceita qualquer origem
    },
}
```

### Formato das mensagens

Todas as mensagens são **JSON** codificadas como [`WSMessage`](message.md). O tipo é identificado pelo campo `"type"`:

| Type | Direção | Descrição |
|------|---------|-----------|
| `"message"` | ambos | Mensagem de chat (inbound do cliente, outbound broadcast) |
| `"system"` | outbound | Eventos: `"join"`, `"leave"`, `"shutdown"` |
| `"user_stats_changed"` | outbound | Estatísticas do usuário atualizadas |

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/ws/handler.go`](../../internal/ws/handler.go) | Upgrade, upgrader, keepalive constants |
| [`internal/ws/hub.go`](../../internal/ws/hub.go) | Broadcast e gerenciamento de conexões |

## Relacionado

- [[hub]] — Gerencia as conexões WebSocket
- [[client]] — Representação de uma conexão WebSocket ativa
- [[message]] — Payload JSON trafegado no protocolo
- [[jwt]] — Autenticação antes do upgrade
- [[chi]] — Roteador HTTP que expõe o endpoint `/ws`
- [[oauth2]] — Auth pré-upgrade
- [[user]] — Identidade do Client
