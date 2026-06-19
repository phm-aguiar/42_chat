# Plan: 42 Chat Core (MVP)

## 1. Metadados do Plano

- **Stack Tecnológico:** Go (gorilla/websocket, Chi, golang-jwt, lib/pq), PostgreSQL (Docker), React + Vite + Tailwind + Shadcn/ui, Zustand, Docker Compose
- **Feature Fonte:** `specs/features/100-42chat-core/spec.md`
- **Escopo:** Chat em tempo real para campus 42 SP (~300 alunos). Backend Go monolítico com WebSocket Hub + REST API, PostgreSQL, frontend React brutalista. Login OAuth2 42 + JWT 12h.

## 2. Design de Contratos e Fronteiras

**Contratos REST:**
| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/auth/42/callback?code=` | Callback OAuth2 — troca code por token + busca `/v2/me` — upsert user — retorna JWT |
| `GET` | `/api/messages?before=&limit=50` | Histórico recente (autenticado) |
| `GET` | `/api/users/:id` | Perfil público do aluno |
| `GET` | `/metrics` | Prometheus: goroutines, memória, DB.Stats(), conexões WS |
| `GET` | `/api/auth/dev/login?login=` | **(DEV_MODE apenas)** Mock user + JWT para testes locais |

**Contrato WebSocket:**
| Direção | Tipo | Payload |
|---|---|---|
| Client → Server | `message` | `{ "content": "string", "token": "***" }` |
| Server → Client | `message` | `{ "id": "uuid", "user_id": int, "login": "string", "image_url": "string", "content": "string", "created_at": "ISO8601" }` |
| Server → Client | `system` | `{ "type": "join"|"leave"|"shutdown", "login": "string" }` |

**Schema PostgreSQL:**
```sql
users (id INT PK, login VARCHAR(50) UNIQUE, image_url TEXT, current_host VARCHAR(20), level NUMERIC(4,2), created_at TIMESTAMP)
messages (id UUID PK DEFAULT gen_random_uuid(), user_id INT FK—users, content TEXT CHECK(length—5000), created_at TIMESTAMP INDEX, deleted_at TIMESTAMP)
```

**Convenções:**
- Diretórios Go: `cmd/server/`, `internal/{auth,ws,api,db,config}/`
- Diretórios React: `src/{components,pages,hooks,stores,lib}/`
- Naming: idiomatic Go (mixedCaps), React (PascalCase components, camelCase hooks)
- Mensagens: JSON sobre WebSocket, campo `type` para routing

## 3. Decisões Arquiteturais e Justificativas (ADR)

**ADR-1: Modular Monolith (Go único processo)**
- **Justificativa:** 1 processo Go serve REST + WebSocket + DB pool. <300 conexões não justifica microservices. Deploy simplificado (1 binário + PostgreSQL).
- **Alternativa rejeitada:** Serviço WS separado (overhead de rede interna, complexidade de deploy desnecessária pra escala do campus).

**ADR-2: Modelo híbrido de concorrência no Hub (`sync.RWMutex` + send chan)**
- **Justificativa:** `RWMutex` no mapa de clients permite leituras simultâneas no broadcast. `send chan` como buffer de saída evita bloqueio do remetente se o receptor estiver lento. Evita round-trip via goroutine por mensagem (custaria latência extra).
- **Alternativa rejeitada:** Channels puros (Go idiomático, mas cada mensagem spawna goroutine — custo de scheduling). Mutex exclusivo (simples, mas estrangula leituras no broadcast).

**ADR-3: JWT 12h + OAuth2 42 (sem refresh token)**
- **Justificativa:** JWT longo (12h) evita complexidade de refresh token no MVP. Expiração cobre um dia de aula. Revalidação transparente via cookie de sessão 42.
- **Alternativa rejeitada:** JWT curto + refresh token (mais seguro, mas adiciona endpoint `/refresh` e lógica de rotação — overengineering pro MVP de 300 alunos).

**ADR-4: PostgreSQL com soft delete (sem hard delete)**
- **Justificativa:** `deleted_at` mantém audit trail (LGPD: retenção de 6 meses). Cron job expurga `deleted_at < NOW() - INTERVAL '6 months'`. Hard delete eliminaria capacidade de auditoria.
- **Alternativa rejeitada:** SQLite (sem concorrência real, sem soft delete nativo). Tabela de audit separada (complexidade extra sem ganho no MVP).

**ADR-5: Cache anti-rate-limit em 3 camadas**
- **Justificativa:** JWT 12h evita revalidação OAuth2 a cada request. Perfil em PostgreSQL com upsert no login evita chamada à API 42 por mensagem. Ingestão batch (30s) para mapeamento de locations. API 42 tem limite de 2 req/s e 1200 req/h.
- **O que NÃO construir:** Cache Redis. PostgreSQL como cache é suficiente pra 300 usuários. Redis seria mais uma dependência pra gerenciar.

**ADR-6: React + Vite + Shadcn/ui (Tailwind) com tema brutalista 42**
- **Justificativa:** Vite é mais leve e rápido que Next.js. Shadcn/ui dá componentes copy-paste customizáveis (rounded-none, cores exatas 42). Tema documentado em `[[references/42-chat-design-system]]`.
- **Alternativa rejeitada:** Next.js (overengineering — SSR/SSG desnecessários pra SPA de chat). CSS modules (mais trabalho manual que Tailwind).

**ADR-7: redirect_uri unificado via env vars (`FORTYTWO_REDIRECT_URI` + `VITE_42_REDIRECT_URI`)**
- **Justificativa:** OAuth2 da 42 exige que o redirect_uri seja idêntico em 3 lugares (frontend authorize URL, backend token exchange, cadastro do app). Centralizar em variáveis de ambiente elimina divergências. Default `http://localhost:5173` cobre o dev loop com Vite.
- **Alternativa rejeitada:** Hardcoded no código (quebra ao trocar de ambiente — local vs Docker vs produção). Path com `/callback` fixo (não permite customização no app 42).

**ADR-8: Dev Mode (`DEV_MODE=true`) com endpoint `/api/auth/dev/login`**
- **Justificativa:** Permite testar o chat sem credenciais OAuth2 42 reais. O endpoint faz upsert de mock user e retorna JWT válido. Isolado por feature flag — nunca disponível em produção (`DEV_MODE=false`).
- **Alternativa rejeitada:** Mock no frontend (não testa o fluxo real de auth, WS, DB). Stub de OAuth2 (complexidade desnecessária — o endpoint dev cobre todo o pipeline).

## 4. Auditoria de Constituição

- [x] **Validação SDD:** spec.md existe e está aprovado. plan.md sendo gerado. tasks.md virá em seguida.
- [x] **Aprovação humana:** `Aprovado: true` no spec.md desde 2026-06-14.
- [x] **Smoke test:** Será definido em tasks.md como task dedicada — servidor sobe, WS conecta, mensagem broadcast, graceful shutdown sem perda.
- [x] **Vault fiel:** Wiki já contém referências de Go, WebSocket, JWT, React+Vite, design system, arquitetura 42 Chat. Atualizado após implementação.
- [x] **Framework primeiro:** Feature 100 é o smoke-test do framework SDD. A implementação valida que agent-dev + agent-qa conseguem construir um app real usando o pipeline SDD.
- [x] **Isolamento:** agent-dev e agent-qa serão spawnados como leaf pelo orchestrator. Sem delegação aninhada.
- [x] **Credenciais hardcoded (regra #7):** Todas as credenciais vêm de `os.Getenv` / `envOrDefault`. Nenhum secret no código fonte. `JWT_SECRET` tem default sentinela `change-me-in-production` apenas para dev mode detection. Smoke test lê `JWT_SECRET` e `DATABASE_URL` do ambiente.
