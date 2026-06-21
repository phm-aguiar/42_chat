# AGENTS.md — 42 Chat

Plataforma de chat em tempo real para a 42 São Paulo (~300 alunos simultâneos).
Substitui Slack/Discord com integração OAuth2 nativa à API da 42.

## Stack

- **Backend:** Go 1.21+ (Chi router, gorilla/websocket)
- **Frontend:** React 18 + Vite + Tailwind + Shadcn/ui (tema brutalista 42)
- **Database:** PostgreSQL 15
- **Infra:** Docker Compose, alvo AWS EC2 t2.micro
- **Auth:** OAuth2 42 + JWT interno (12h)

## Estrutura

```
backend/
  cmd/server/main.go       # Entry point
  internal/
    auth/                   # OAuth2 42, JWT
    ws/                     # WebSocket hub + client
    handler/                # HTTP handlers (Chi)
    middleware/              # Auth, rate-limit
    db/                     # PostgreSQL queries
  migrations/               # SQL migrations

frontend/
  src/
    components/             # React components
    pages/                  # Routes
    hooks/                  # useWebSocket, useAuth
    lib/                    # API client, utils

specs/features/             # Pipeline SDD do domínio
wiki/                       # Wiki específica do projeto
.hermes/                    # Skills + LATTE (herdados do 42_Framework)
```

## Features

### Domínio — Aplicativo

| ID | Nome | Status | Stack |
|----|------|--------|-------|
| 100 | 42 Chat Core | ✅ | Go, React, PostgreSQL, Docker, OAuth2 |
| 101 | Assinatura de Participação | ✅ | Go, React, WebSocket |

### Pipeline SDD — Infraestrutura

| ID | Nome | Status | Descrição |
|----|------|--------|-----------|
| 009 | Start Repo | draft | Inicialização de repositório SDD (constitution, tech, templates) |
| 010 | SDD Templates | draft | Templates canônicos (spec, plan, tasks) + refactor artifact |
| 011 | Forge Skill | draft | Skill para criar skills Hermes com template e validação |
| 012 | Tasks DAG | draft | sdd-generate-tasks com formato DAG, paralelismo, isolamento |
| 013 | Runtime Orchestrator | draft | Execução automática do DAG com agent-dev + agent-qa em paralelo |
| 006 | Agent Dev | draft | Subagente implementador: recebe task → gera código + smoke test |
| 007 | Agent QA | draft | Subagente QA: valida implementações contra spec, Gherkin, rejeição |
| 008 | Reavaliação Skills | approved | Consolidação de ~130 skills em toolkits unificados |

### Framework — 42_Framework (dependências)

| ID | Nome | Status | Módulos |
|----|------|--------|---------|
| 001 | LATTE Coordination | ✅ | orchestrator, heartbeat, frontier, dispatcher, lead/worker operators, graph_persistence, metrics (39 tests) |
| 002 | Wiki Experiential Memory | ✅ | chunker, store, search, scoring, feedback, decay, cluster, distill, summarizer, cli_index, cli_query |
| 003 | Hybrid Retrieval | ✅ | bm25, normalize_frontmatter, cli_query --hybrid |
| 004 | jschan Forum Manager | ✅ | wiki (3 págs) + skill scripts (5 bash) + docker-compose + smoke tests |
| 005 | LATTE Hardening | ✅ | budget, timeout, failure-propagation, verify-deterministic, summarization, merge, tool-ceiling (7 ADRs) |

## Dependências — 42_Framework

O 42_chat depende do meta-framework `42_Framework` (`/home/zeenyt__/Projetos/42_Framework`) para:

| Dependência | Feature | Uso |
|-------------|---------|-----|
| LATTE Coordination | 001 | Orquestração multi-agente (coordination graph, heartbeat, 7 operadores) |
| Wiki Experiential Memory | 002 | Índice SQLite + embeddings (all-MiniLM-L6-v2, 384d) |
| Hybrid Retrieval | 003 | Busca BM25 + cosine (α=0.7, ~500ms) |
| LATTE Hardening | 005 | Budget tracking, timeout, failure propagation, verify deterministic |

**IMPORTANTE:** As features 001-003 e 005 do 42_Framework NÃO estão duplicadas no 42_chat.
O 42_chat referencia os módulos diretamente de `/home/zeenyt__/Projetos/42_Framework/.hermes/skills/`.

## Modo de Trabalho

### Pipeline SDD (para features do 42_chat)
1. `brainstorm` → interativo com `clarify()`
2. `spec` → spec.md com `Aprovado: false`. Gate humano
3. `plan` → plan.md com ADRs
4. `tasks` → tasks.md com DAG (formato feature 004)
5. `implement` → Runtime Orchestrator (feature 005) com agent-dev + agent-qa
6. `validate` → smoke tests com infra real (Docker, Postgres, WebSocket)
7. `wiki` → atualizar wiki + reindexar

### Padrões
- **Batch de 3:** paralelizáveis → sequenciais → [x] → avançar
- **Subagentes:** paths absolutos + snippets + constraints
- **Nunca inferir:** ambiguidade = clarify(). Decisões irreversíveis = confirmar
- **Verificar sempre:** exit code, smoke test real, Docker health check
- **Stack Go:** Chi routes específicas antes de parametrizadas; SQL verificar schema com `\d`
- **Docker:** `env -u KEY docker compose up -d --build` (rebuild obrigatório)
- **DEV_MODE:** `DEV_MODE=true` + login dev em `/api/auth/dev/login`

### Wiki
- `wiki/` é source of truth. Nunca modificar sem confirmação
- Índice SQLite via 42_Framework:
  `python3 /home/zeenyt__/Projetos/42_Framework/.hermes/skills/wiki/experiential_memory/cli_index.py --full --wiki-dir wiki/`
- Consultar:
  `python3 /home/zeenyt__/Projetos/42_Framework/.hermes/skills/wiki/experiential_memory/cli_query.py --semantic "termos" --hybrid --top-k 5`
- Papers em `wiki/_raw/` → ingerir com brain ingest

## Constraints

1. **Hermes nativo:** sem APIs externas, sem cloud. Tudo local
2. **PYTHONPATH:** usar path absoluto pro 42_Framework: `/home/zeenyt__/Projetos/42_Framework/.hermes/skills/`
3. **Git:** author = phm-aguiar
4. **Go imports:** Chi router, gorilla/websocket, lib/pq
5. **Dev login:** `DEV_MODE=true` ativa rota `/api/auth/dev/login` sem OAuth2
6. **Docker rebuild:** `env -u KEY` pra evitar env vars vazando
7. **SDD obrigatório:** PROIBIDO implementar código sem spec aprovado. Todo código novo deve passar pelo pipeline SDD: brainstorm → spec (Aprovado: true) → plan → tasks → implement. Sem rastreabilidade de feature, zero código.

## Gatilhos

| Gatilho | Ação |
|---------|------|
| "brainstorm" / "nova feature" | sdd-brainstorm → spec → plan → tasks |
| "implementar feature X" | Runtime Orchestrator (feature 005) |
| "rodar 42chat" / "subir chat" | `docker compose up -d --build` |
| "testar 42chat" | `curl localhost:8080/api/health` → WebSocket test |
| "wiki status" / "como está a wiki" | brain report status |
| "indexar" / "reindexar" | python3 ...cli_index.py --full --wiki-dir wiki/ |
| "pesquisar X" | python3 ...cli_query.py --semantic "X" --hybrid |
| "orquestrar" / "LATTE" | PYTHONPATH=... pytest ...latte_coordination/tests/ -q |
| "lint" / "auditar wiki" | brain lint |

## Backlog

| ID | Nome | Prioridade |
|----|------|-----------|
| 102 | 42 Forum | alta |
| 018 | (próxima feature SDD) | — |
