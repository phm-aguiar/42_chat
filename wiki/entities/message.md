---
title: "Message (Modelo de Mensagem)"
tags: [entity, glossary]
aliases: [model.Message, WSMessage, mensagem, chat message]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: Message é o modelo de dados de uma mensagem no chat — ID UUID v4, conteúdo com limite de 5000 caracteres, soft delete via DeletedAt, e o payload WSMessage usado na comunicação WebSocket.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# Message (Modelo de Mensagem)

## Definição

**Message** é o modelo de dados que representa uma mensagem no chat do 42 Chat. O pacote `model` define duas structs relacionadas:

- **`Message`**: modelo de persistência com ID UUID v4 gerado pelo PostgreSQL, UserID, Login (preenchido via JOIN), Content com CHECK constraint ≤5000 no banco, CreatedAt com timezone, e DeletedAt para soft delete (nunca hard delete).
- **`WSMessage`**: payload JSON trafegado no protocolo [`WebSocket`](websocket.md) — usado tanto inbound (mensagens do cliente) quanto outbound (broadcasts para todos os clients). Campos incluem Type (`"message"` ou `"system"`), ID, UserID, Login, ImageURL, Content, Token (JWT no connect inicial) e CreatedAt em ISO8601.

## No Projeto

### Fluxo de uma mensagem

1. **Inbound**: O [`Client`](client.md) lê JSON do WebSocket → decodifica como `WSMessage` → valida `Type == "message"` e `len(Content) ≤ 5000` → persiste via `InsertMessage` no PostgreSQL → dispara broadcast de estatísticas.
2. **Enriquecimento**: O readPump cria um `WSMessage` outbound com metadados do autor (`ID`, `UserID`, `Login`, `CreatedAt` formatado como RFC3339).
3. **Broadcast**: O [`Hub`](hub.md) serializa o `WSMessage` outbound via `json.Marshal` e envia para todos os clients.
4. **Soft delete**: Mensagens deletadas têm `DeletedAt` populado — nunca são removidas fisicamente do banco (hard delete não existe no modelo).

### WSMessage — Campos

| Campo | JSON | Direção | Descrição |
|-------|------|---------|-----------|
| Type | `"type"` | ambos | `"message"` para chat, `"system"` para eventos |
| ID | `"id"` | outbound | UUID v4 da mensagem persistida |
| UserID | `"user_id"` | outbound | ID do autor (da API 42) |
| Login | `"login"` | outbound | Login do autor |
| ImageURL | `"image_url"` | outbound | URL da foto de perfil da 42 |
| Content | `"content"` | ambos | Texto da mensagem (inbound) ou payload do sistema (outbound) |
| Token | `"token"` | inbound | JWT no connect inicial |
| CreatedAt | `"created_at"` | outbound | Timestamp ISO8601 |

## Arquivo(s)

| Arquivo | Descrição |
|---------|-----------|
| [`internal/model/message.go`](../../internal/model/message.go) | Definição das structs Message e WSMessage (29 linhas) |

## Relacionado

- [[hub]] — Responsável pelo broadcast de WSMessage
- [[client]] — readPump persiste e enriquece mensagens
- [[user]] — Autor da mensagem (UserID, Login, ImageURL)
- [[websocket]] — Protocolo de transporte do WSMessage
