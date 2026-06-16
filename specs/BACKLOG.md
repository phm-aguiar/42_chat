# Backlog — Framework SDD Autônomo

> **Produto:** Framework SDD autônomo com agentes IA e humanos in loop.
> **42_chat:** Smoke-test futuro pra validar o framework — **não é o produto.**
>
> Agentes: `onboard` (inicialização) + `agent-orchestrator` (execução runtime).
> Pipeline: `brainstorm → spec → plan → tasks (DAG) → orchestrator → subagentes`.

## Em Progresso

| ID | Feature | Status |
|----|---------|--------|
| — | — | — |

## Concluído

| ID | Feature | Status |
|----|---------|--------|
| 001 | start-repo (estrutura base + templates) | ✅ Aprendizado — templates de constitution, tech, CI |
| 002 | sdd-templates (formato spec/plan/tasks) | ✅ Aprendizado — formato canônico estabilizado |
| 003 | forge-skill (scaffold de skills) | 🔄 Parcial — scaffold + template, útil mas não prioritário |
| 004 | sdd-tasks-dag (DAG no tasks.md) | ✅ Implementado — `sdd-generate-tasks` v2.0.0 |
| 005 | agent-orchestrator (runtime SDD) | ✅ Implementado — agente em `.hermes/agents/agent-orchestrator/` |
| 006 | agent-dev (persona implementadora) | ✅ Implementado — agente em `.hermes/agents/agent-dev/`, spec/plan/tasks em `specs/features/006-agent-dev/` |
| 007 | agent-qa (guardião da qualidade) | ✅ Implementado — agente em `.hermes/agents/agent-qa/`, spec/plan/tasks em `specs/features/007-agent-qa/` |

## Pipeline Ativo

```
sdd-brainstorm → spec.md → Aprovado: true
     ↓
sdd-generate-plan → plan.md
     ↓
sdd-generate-tasks (DAG) → tasks.md
     ↓
agent-run agent-orchestrator → execução paralela (Dev, QA)
```

## Próximas Features (agentes do squad)

> O orchestrator está pronto. Agentes Dev (006) e QA (007) implementados.
> Features 008-009 em standby até fundamentação.

| ID | Feature | O quê | Depende de |
|----|---------|-------|------------|
| 008 | agent-devops | Agente DevOps: CI/CD, Docker, deploy, integração, performance | 005 |
| 009 | agent-pentester | Agente Pentester: segurança, OWASP, secrets, dependências | 005 |

> ⚠️ **Standby:** Features 008 (DevOps) e 009 (Pentester) em backlog até fundamentação.

## Próximas Features (skills de agente)

> Skills plugáveis que os agentes Dev e QA carregam durante o ciclo de trabalho.

| ID | Skill | Agente | Status |
|----|-------|--------|--------|
| 010 | gherkin-scenarios | QA | ✅ Implementado |
| 011 | go-unit-tests | QA | ✅ Implementado |
| 012 | local-test-runner | QA | ✅ Implementado |
| 013 | tdd-workflow | QA | ✅ Implementado |
| 014 | cucumber-step-definitions | QA | ✅ Implementado |
| 015 | bdd-spec-process | QA | ✅ Implementado |
| 016 | playwright-bdd-e2e | QA | ✅ Implementado |
| 017 | go-implement | Dev | ✅ Implementado |
| 018 | python-implement | Dev | ❌ Pendente |
| 019 | build-check (smoke-test) | Dev | ✅ Implementado |
| 020 | react-implement | Dev | ✅ Implementado |

## Próximas Features (aplicação)

> O framework SDD está funcional. O próximo passo é usar o framework para
> construir o 42_chat — a aplicação de chat que serve como smoke-test real.

| ID | Feature | O quê | Status |
|----|---------|-------|--------|
| 100 | 42_chat core | Aplicação de chat (Go): HTTP, WebSocket, mensagens | ❌ Backlog |
| 101 | 42_chat deploy | Deploy no homelab (RPi 5, Docker, Tailscale) | ❌ Backlog |

## Pipeline Completo (após 006-009)

```
onboard (init + brainstorm)
     ↓
spec.md → Aprovado: true
     ↓
sdd-generate-plan → plan.md
     ↓
sdd-generate-tasks (DAG) → tasks.md
     ↓
agent-orchestrator
  ├─ spawna agent-dev   (implementa código)
  ├─ spawna agent-qa    (testa)
  ├─ spawna agent-devops (CI/CD, deploy)
  └─ spawna agent-pentester (security scan)
```

## Skills por Feature

### Dev Skills (feature 006)
| Skill | O que faz |
|-------|-----------|
| `go-implement` | Implementa código Go a partir de spec + contratos (Chi, gorilla/websocket, PostgreSQL) |
| `react-implement` | Implementa frontend React (Vite, Tailwind 42, Shadcn/ui, Zustand, WebSocket hooks) |
| `build-check` | Smoke test: `go build ./...`, `go vet`, `npm run build`. Portão DONE obrigatório |
| `python-implement` | ❌ Pendente — Implementa código Python |
| `go-refactor` | ❌ Pendente — Refatora código sem quebrar testes |

### QA Skills (feature 007)
| Skill | O que faz |
|-------|-----------|
| `go-unit-tests` | Gera/executa `go test ./...` com cobertura |
| `gherkin-scenarios` | Lê spec.md → gera `.feature` files |
| `local-test-runner` | Build, lint, vet, smoke-test |

### DevOps Skills (feature 008)
| Skill | O que faz |
|-------|-----------|
| `docker-build` | Build e push de imagens Docker |
| `ci-validate` | Valida pipeline, verifica workflows |
| `deploy-staging` | Deploy em staging |

### Pentester Skills (feature 009)
| Skill | O que faz |
|-------|-----------|
| `dependency-scan` | `go vet`, `govulncheck`, CVEs |
| `owasp-check` | OWASP Top 10 em código Go |
| `secret-scan` | Secrets hardcoded, `.env` exposto |

---

## Skills Importadas — Wiki + Obsidian + Visual

> 21 skills importadas em 2026-06-13. Vault `wiki/` versionado no repo.
> Adaptação ao padrão do framework pendente para skills wiki; `mermaid-visualizer` funciona standalone.

---

## Atualizado em
2026-06-13
