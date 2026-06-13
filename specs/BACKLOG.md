# Backlog — 42_chat

> Squad autônoma guiada por humanos in loop.
> Cada agente é um especialista munido de skills. O orchestrator seleciona
> agente + skills conforme o micro-contexto da task.

## Em Progresso

| ID | Feature | Status | Dependência |
|----|---------|--------|-------------|
| — | — | — | — |

## Specs Prontos (aguardando plan.md)

| ID | Feature | Spec | Pipeline |
|----|---------|------|----------|
| 004 | sdd-tasks-dag (DAG no tasks.md) | [spec.md](features/004-sdd-tasks-dag/spec.md) | Aguardando `Aprovado: true` → `sdd-generate-plan` |
| 005 | runtime-orchestrator (orquestrador de execução) | [spec.md](features/005-runtime-orchestrator/spec.md) | Aguardando feature 004 + `Aprovado: true` |

## Brainstorms Pendentes

| ID | Feature | O quê | Por quê |
|----|---------|-------|---------|
| 006 | agent-dev | Agente Desenvolvedor: escreve código, smoke-test. **Nunca** loga, **nunca** testa unitário. Rastreável à spec | Runtime-orchestrator precisa spawnar subagentes especializados |
| 007 | agent-qa | Agente QA multi-função. Conforme contexto: (1) testes unitários, (2) cenários Gherkin/Cucumber, (3) testes locais (build/lint), (4) acompanhar testes em dev. Munido de skills por micro-contexto | QA não é monolítico — cada task exige um subset diferente de skills |
| 008 | agent-devops | Agente DevOps: CI/CD, Docker, deploy, monitoramento de ambiente | Infraestrutura como código, consistência entre ambientes |
| 009 | agent-pentester | Agente Pentester: análise de segurança, vulnerabilidades, OWASP, scan de dependências | Segurança contínua integrada ao pipeline SDD |

## Skills Necessárias (visão preliminar)

### QA Skills (feature 007)
| Skill | Micro-contexto | O que faz |
|-------|---------------|-----------|
| `go-unit-tests` | Testes unitários | Gera/executa `go test ./...` com cobertura |
| `gherkin-scenarios` | Cenários de aceitação | Lê spec.md → gera `.feature` files (Gherkin/Cucumber) |
| `local-test-runner` | Testes locais | Build, lint, vet, smoke-test local |
| `test-watcher` | Acompanhamento | Monitora output de testes em ambiente dev, reporta falhas |

### Dev Skills (feature 006)
| Skill | Micro-contexto | O que faz |
|-------|---------------|-----------|
| `go-implement` | Escrita de código | Implementa feature a partir de spec + contratos |
| `go-refactor` | Refatoração | Refatora código existente sem quebrar testes |
| `smoke-check` | Verificação rápida | `go build`, checagem de sintaxe, verificação de imports |

### DevOps Skills (feature 008)
| Skill | Micro-contexto | O que faz |
|-------|---------------|-----------|
| `docker-build` | Containerização | Build e push de imagens Docker |
| `ci-validate` | CI/CD | Valida pipeline, verifica workflows |
| `deploy-staging` | Deploy | Deploy em ambiente de staging |

### Pentester Skills (feature 009)
| Skill | Micro-contexto | O que faz |
|-------|---------------|-----------|
| `dependency-scan` | Dependências | `go vet`, `govulncheck`, scan de CVEs |
| `owasp-check` | OWASP Top 10 | Verifica vulnerabilidades comuns em código Go |
| `secret-scan` | Segredos | Detecta secrets hardcoded, `.env` exposto |

---

## Fluxo Completo (visão)

```
sdd-brainstorm → spec.md
       ↓
sdd-generate-plan → plan.md
       ↓
sdd-generate-tasks (004) → tasks.md com DAG
       ↓
[Aprovado: true]
       ↓
agent-run runtime-orchestrator (005)
       ↓
   ┌─────┬──────────┬──────────┬──────────┐
   │ Dev │ QA       │ DevOps   │ Pentester│
   │(006)│  (007)   │  (008)   │  (009)   │
   └─────┴──────────┴──────────┴──────────┘
       ↓
   tasks.md [x] [x] [x] → feature implementada
```

---

## Atualizado em
2026-06-12
