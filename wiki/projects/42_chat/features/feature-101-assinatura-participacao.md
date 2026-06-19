---
title: "Feature 101 — Assinatura de Participação"
category: feature
tags: [sdd, 42chat, feature, backend, frontend, websocket]
sources:
  - specs/features/101-assinatura-participacao/spec.md
  - specs/features/101-assinatura-participacao/plan.md
  - specs/features/101-assinatura-participacao/tasks.md
created: 2026-06-18T04:00:00Z
updated: 2026-06-18T04:00:00Z
summary: >-
  Componente UserSignature inline abaixo de mensagens exibindo stats de engajamento
  (total de mensagens, salas ativas, tier de participação), alimentado por API on-demand
  + WebSocket push. Tiers: novato (0) → iniciante (1-50) → participante (51-200) → veterano (201+).
provenance:
  extracted: 0.9
  inferred: 0.1
  ambiguous: 0.0
base_confidence: 0.95
lifecycle: verified
lifecycle_changed: 2026-06-18
tier: core
---

# Feature 101 — Assinatura de Participação

## Visão Geral

Componente `UserSignature` reutilizável exibido inline abaixo de cada mensagem no chat,
mostrando avatar, login, tier de participação, total de mensagens e salas ativas.
Stats são globais (cross-channel) e atualizam em tempo real via WebSocket.

## Artefatos SDD

- `specs/features/101-assinatura-participacao/spec.md` (Spec)
- `specs/features/101-assinatura-participacao/plan.md` (Plan)
- `specs/features/101-assinatura-participacao/tasks.md` (Tasks)

## Arquitetura

### Decisões (ADRs)

1. **API on-demand + WebSocket push:** Sem tabela materializada — stats computados via query agregada
2. **Stats globais, não por canal:** `total_messages` e `active_rooms` contam todas as salas
3. **Debounce 2s no WebSocket:** Evita rajadas de updates
4. **Componente autossuficiente:** `UserSignature` recebe apenas `userId`, busca e escuta seus dados internamente

### Stack

- **Backend:** Go + Chi router, `internal/api/stats.go` (handler), `internal/db/stats.go` (query)
- **WebSocket:** Hub estendido com `BroadcastUserStatsChanged` + debounce
- **Frontend:** React 19 + TypeScript, `UserSignature.tsx`, WebSocket listener
- **Testes:** 10 unitários (Go), 17 cenários E2E (Playwright)

### Tiers de Participação

| Tier | Threshold | Visual |
|------|-----------|--------|
| novato | 0 mensagens | Placeholder reduzido 🌱 |
| iniciante | 1-50 | 🔰 cyan |
| participante | 51-200 | ⭐ blue |
| veterano | 201+ | 👑 lime |

## Endpoints

```
GET /api/users/{id}/stats (autenticado)
→ { user_id, login, avatar_url, total_messages, active_rooms, tier, member_since }
```

## Evento WebSocket

```
user_stats_changed → { user_id, total_messages, active_rooms, tier }
```

## Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `internal/db/stats.go` | Query SQL + ComputeTier |
| `internal/api/stats.go` | Handler HTTP |
| `internal/ws/hub.go` | BroadcastUserStatsChanged + debounce |
| `cmd/server/main.go` | Registro da rota |
| `frontend/src/components/UserSignature.tsx` | Componente React |
| `frontend/src/components/MessageList.tsx` | Integração |
| `frontend/src/lib/ws.ts` | Tipo user_stats_changed |
| `test/e2e/user-signature.spec.ts` | 825 linhas, 17+ cenários E2E |

## Status

✅ Implementado — 11/11 tasks concluídas, smoke test passou (go build + npm run build + curl 200)

## Relacionado

- Feature 100 (42 Chat Core) — Dependência (mensagens, WebSocket hub). Página wiki pendente.
- [[journal/2026-06-17-brainstorm-feature-101]] — Sessão de brainstorm
