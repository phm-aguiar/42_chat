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

## Pipeline Ativo

```
sdd-brainstorm → spec.md → Aprovado: true
     ↓
sdd-generate-plan → plan.md
     ↓
sdd-generate-tasks (DAG) → tasks.md
     ↓
agent-run agent-orchestrator → execução paralela (Dev, QA, Test)
```

## Próximas Features (agentes do squad)

> O orchestrator está pronto, mas os subagentes que ele spawna ainda não existem.
> Features 006-009 implementam os agentes especializados.

| ID | Feature | O quê | Depende de |
|----|---------|-------|------------|
| 007 | agent-qa | Agente QA: testes unitários, Gherkin/Cucumber, lint, cobertura | 005 |
| 008 | agent-devops | Agente DevOps: CI/CD, Docker, deploy, validação de pipeline | 005 |
| 009 | agent-pentester | Agente Pentester: segurança, OWASP, secrets, dependências | 005 |

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
| `go-implement` | Implementa feature a partir de spec + contratos |
| `go-refactor` | Refatora código sem quebrar testes |
| `smoke-check` | `go build`, checagem de sintaxe, imports |

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
