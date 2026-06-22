---
title: "Hub (WebSocket Hub)"
tags: [entity, glossary]
aliases: [WebSocket Hub, Connection Hub, ws.Hub]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: Hub é o gerenciador central de conexões WebSocket do 42 Chat — registra, desconecta e faz broadcast de mensagens para todos os clients conectados.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# Hub (WebSocket Hub)

## Definição

O **Hub** é o componente central que gerencia todas as conexões WebSocket ativas no 42 Chat. Ele mantém um registro de todos os [`Client`](client.md)s conectados, coordena broadcast de mensagens e gerencia notificações de sistema (join/leave/shutdown). Utiliza um modelo híbrido de concorrência: `sync.RWMutex` para leitura concorrente do mapa de clients + canais `Send` como buffer de saída por client.

## No Projeto

No 42 Chat, o Hub é instanciado em [`cmd/server/main.go`](../../cmd/server/main.go) durante a inicialização do servidor:

```go
hub := ws.NewHub(queries)
```

Ele é injetado no [`Handler`](client.md) WebSocket, que o utiliza para:

- **Connect**: registrar novos clients quando uma conexão WebSocket é estabelecida, emitindo broadcast de sistema `"join"` com o login do usuário.
- **Disconnect**: remover clients ao fechar conexão, fechando o canal `Send` e emitindo broadcast `"leave"`.
- **Broadcast**: enviar uma [`Message`](message.md) para todos os clients simultaneamente, com descarte silencioso (não-bloqueante) para buffers cheios.
- **BroadcastSystem**: enviar mensagens de sistema tipadas (`"join"`, `"leave"`, `"shutdown"`).
- **Shutdown**: notificar todos os clients sobre shutdown iminente durante graceful shutdown.
- **BroadcastUserStatsChanged**: disparar broadcast de `user_stats_changed` com debounce de 2 segundos — Feature 101, múltiplas chamadas para o mesmo `userID` em 2s geram um único broadcast.
- **ConnectionCount**: expor número de conexões ativas para o endpoint `/metrics`.

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/ws/hub.go`](../../internal/ws/hub.go) | Implementação do Hub (196 linhas) |
| [`internal/ws/hub_test.go`](../../internal/ws/hub_test.go) | Testes unitários do Hub |

## Relacionado

- [[client]] — Client WebSocket gerenciado pelo Hub
- [[message]] — Payload trafegado nos broadcasts
- [[websocket]] — Protocolo de comunicação subjacente
- [[chi]] — Roteador HTTP que expõe o endpoint `/ws`
- [[jwt]] — Autenticação no Connect
- [[user]] — Tracks connected users via UserID
