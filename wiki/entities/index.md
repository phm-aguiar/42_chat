---
title: "Entities — Glossário do 42 Chat"
tags: [entity, glossary, index]
created: 2026-06-21
rag_score: 0.5
category: entities
summary: Índice do glossário de entidades e conceitos do 42 Chat Core — Hub, Client, Message, User, JWT, OAuth2, WebSocket e Chi.
---

# Entities — Glossário do 42 Chat

Catálogo das entidades e conceitos centrais do projeto **42 Chat Core MVP**. Cada termo descreve um componente da stack real: Go + Chi + PostgreSQL + WebSocket + OAuth2 + JWT + Docker.

## Entidades

| Termo | Slug | Descrição |
|-------|------|-----------|
| [[hub]] | `hub` | Gerenciador central de conexões WebSocket — registra, desconecta e faz broadcast |
| [[client]] | `client` | Conexão WebSocket ativa — readPump (leitura) e writePump (envio + keepalive) |
| [[message]] | `message` | Modelo de mensagem com soft delete e payload WSMessage para WebSocket |
| [[user]] | `user` | Modelo de usuário — ID da API 42, login único, sincronizado via OAuth2 |
| [[jwt]] | `jwt` | JSON Web Token interno — HS256, 12h de expiração, claims com UserID e Login |
| [[oauth2]] | `oauth2` | Fluxo authorization code da API 42 — troca code por token e dados do usuário |
| [[websocket]] | `websocket` | Protocolo full-duplex em tempo real — upgrade HTTP, ping/pong, mensagens JSON |
| [[chi]] | `chi` | Roteador HTTP Go idiomático — middleware stacking, grupos autenticados, compatível com net/http |

## Stack

```
Frontend (React/Vite) ──HTTP/WS──▶ Chi Router
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                  ▼
              OAuth2 Handler    JWT Middleware     WebSocket Handler
              (callback 42)     (Authorization)   (/ws upgrade)
                    │                 │                  │
                    ▼                 ▼                  ▼
              API 42 (intra)    JWTManager          Hub + Client
                    │                                  │
                    └──────────┬───────────────────────┘
                               ▼
                          PostgreSQL
                    (users, messages, stats)
```

## Navegação

- [[hub]] — Ponto de partida para entender o sistema de conexões
- [[oauth2]] — Ponto de partida para o fluxo de autenticação
- [[chi]] — Ponto de partida para a estrutura HTTP do servidor
