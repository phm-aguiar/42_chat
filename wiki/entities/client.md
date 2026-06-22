---
title: "Client (WebSocket Client)"
tags: [entity, glossary]
aliases: [WebSocket Client, ws.Client, readPump, writePump]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: Client representa uma conexão WebSocket ativa — identifica o usuário autenticado, mantém um canal de saída e executa goroutines de leitura (readPump) e escrita (writePump).
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# Client (WebSocket Client)

## Definição

O **Client** é uma struct que representa uma conexão WebSocket ativa no 42 Chat. Cada client carrega o `UserID` e `Login` do usuário autenticado, um canal `Send` (buffer de 256 mensagens) para comunicação outbound, e uma referência ao [`Hub`](hub.md) ao qual pertence. O ciclo de vida do client é gerenciado por duas goroutines — `readPump` (leitura de mensagens inbound) e `writePump` (envio de mensagens outbound + keepalive).

## No Projeto

O Client é criado no `Handler.ServeHTTP` após validação do [`JWT`](jwt.md) e upgrade HTTP → [`WebSocket`](websocket.md):

```go
client := &Client{
    UserID: claims.UserID,
    Login:  claims.Login,
    Send:   make(chan []byte, 256),
    Hub:    h.hub,
}
h.hub.Connect(client)
go h.writePump(client, conn)
go h.readPump(client, conn)
```

### readPump

A goroutine `readPump` é responsável por:

1. **Ler mensagens** do WebSocket (limite de 6KB).
2. **Decodificar** JSON inbound como `model.WSMessage`.
3. **Validar** tipo (`"message"`) e tamanho do conteúdo (≤5000).
4. **Persistir** a mensagem no PostgreSQL via `InsertMessage`.
5. **Disparar broadcast** de estatísticas com debounce (`BroadcastUserStatsChanged`).
6. **Enriquecer** a mensagem com metadados do autor (ID, login, timestamp) e fazer broadcast para todos os clients.

Quando a conexão fecha (erro de leitura, close normal, going away), o `readPump` chama `Hub.Disconnect(client)` e fecha a conexão TCP.

### writePump

A goroutine `writePump` é responsável por:

1. **Escutar** o canal `client.Send` e escrever mensagens no WebSocket.
2. **Ping keepalive** a cada 30 segundos (com pong handler no readPump resetando deadline a 60s).
3. **Deadlines**: `writeWait` de 10s por mensagem, `pingPeriod` de 30s, `pongWait` de 60s.
4. **Fechar** a conexão quando o Hub fecha o canal `Send` (envia CloseMessage).

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/ws/handler.go`](../../internal/ws/handler.go) | Handler com readPump, writePump e upgrade HTTP→WS (186 linhas) |
| [`internal/ws/handler_test.go`](../../internal/ws/handler_test.go) | Testes de integração do handler |

## Relacionado

- [[hub]] — Hub que gerencia e faz broadcast entre clients
- [[message]] — Modelo de mensagem lido e persistido pelo readPump
- [[websocket]] — Protocolo de comunicação subjacente
- [[jwt]] — Token validado antes da criação do client
