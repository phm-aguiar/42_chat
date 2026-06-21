---
title: "Wiki Gap Fill Tasks"
category: tasks
tags: [wiki, gap-analysis, tasks]
summary: "Tasks para preencher gaps identificados na wiki do 42_chat. 336 páginas, 10 gaps mapeados."
lifecycle: draft
created: "2026-06-21"
---

# Wiki Gap Fill — Tasks

> 10 gaps identificados após wiki-ingest de 159 raw files.
> Prioridade: P0 (bloqueia referência) → P1 (alto valor) → P2 (desejável).

## P0 — Bloqueia referência imediata

### GAP-01: Feature 100 — 42 Chat Core
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/projects/42_chat/features/feature-100-42-chat-core.md` (416 linhas, 16KB)
- **Fonte:** `cmd/server/main.go`, `internal/ws/`, `internal/api/`, `internal/auth/`
- **Escopo:** spec da feature core — WebSocket chat, OAuth2, mensagens, salas

### GAP-02: PostgreSQL na Prática
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/postgresql.md` (270 linhas, 11KB)
- **Fonte:** `internal/db/postgres.go`, `internal/db/queries.go`, `migrations/`
- **Escopo:** connection pool, migrations, query patterns, schema design, lib/pq vs pgx

### GAP-03: Docker + Compose
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/docker-compose.md` (328 linhas, 10KB)
- **Fonte:** `Dockerfile`, `docker-compose.yml`
- **Escopo:** multistage build Go, dev vs prod, env vars, health checks

## P1 — Alto valor

### GAP-04: OAuth2 42 — Fluxo Profundo
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/42-oauth2-flow.md` (390 linhas, 13KB)
- **Fonte:** `internal/auth/oauth.go`, `internal/auth/dev_login.go`
- **Escopo:** authorization code flow, token exchange, DEV_MODE bypass, pitfalls

### GAP-05: JWT + Chi Middleware + WebSocket Auth
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/auth-integration.md` (481 linhas, 19KB)
- **Fonte:** `internal/auth/middleware.go`, `internal/auth/jwt.go`, `internal/ws/handler.go`
- **Escopo:** 3 camadas de auth, middleware chain, WS upgrade com token

### GAP-06: WebSocket em Produção
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/websocket-production.md` (627 linhas, 24KB)
- **Fonte:** `internal/ws/hub.go`, `internal/ws/handler.go`
- **Escopo:** ping/pong keepalive, reconnect, scaling multi-instance, rate limiting

### GAP-07: Glossário entities/
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/entities/*.md` (9 arquivos + index)
- **Escopo:** Hub, Client, Message, User, JWT, OAuth2, WebSocket, Chi

## P2 — Desejável

### GAP-08: Monitoramento/Observabilidade
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/observability.md` (705 linhas, 21KB)
- **Escopo:** health checks, logging estruturado (slog), métricas (expvar), Datadog APM, checklist produção

### GAP-09: Testes de Integração com Docker
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/integration-testing-docker.md` (961 linhas, 27KB)
- **Fonte:** `test/smoke_test.go`, `internal/**/*_test.go` (12 arquivos)
- **Escopo:** smoke tests 3 níveis, Docker lifecycle, WebSocket testing, table-driven, CI/CD

### GAP-10: ADRs (7 decisões do 42_Framework)
- **Status:** `[x]` ✅ 2026-06-21
- **Target:** `wiki/references/adr/ADR-001.md` até `ADR-007.md`
- **Fonte:** 42_Framework feature 005 plan.md (ADRs 006-012 originais)
- **Escopo:** budget tracking, timeout, failure propagation, verify deterministic, summarization, merge, tool ceiling

---

**Resultado: 10/10 gaps preenchidos. Wiki: 336 → 361 páginas (+25 nesta sessão).**

---

## Ordem de Execução

1. GAP-01 (Feature 100) — ausência mais gritante
2. GAP-02 (PostgreSQL) — stack de dados sem doc
3. GAP-03 (Docker) — infra sem doc
4. GAP-04 (OAuth2) — auth crítico
5. GAP-05 (Auth Integration) — orquestração
6. GAP-06 (WS Produção) — scaling
7. GAP-07 (entities) — glossário
