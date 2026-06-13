# 42_chat

> Squad autônoma de agentes de IA guiada por humanos in loop.
> Spec-Driven Development com orquestrador, agentes especializados e pipeline fully automated.

## Arquitetura

```mermaid
flowchart TB
    subgraph HUMAN["👤 Humano in Loop"]
        IDEA["💡 Ideia"]
        APPROVE["✅ Aprovação"]
        ESCALATE["🚨 Escalação"]
    end

    subgraph SDD["📋 Pipeline SDD"]
        BRAIN["sdd-brainstorm<br/>Entrevista interativa"]
        SPEC["spec.md<br/>Especificação funcional"]
        PLAN["sdd-generate-plan<br/>Plano arquitetural (ADR)"]
        TASKS["sdd-generate-tasks<br/>DAG de tasks com paralelismo"]
    end

    subgraph ORCH["🎯 Runtime Orchestrator"]
        DAG["Lê DAG do tasks.md"]
        GATE["Verifica Aprovado: true"]
        SPAWN["Spawna subagentes<br/>janela deslizante (máx 3)"]
        MONITOR["Monitora retries<br/>máx 3 tentativas"]
    end

    subgraph SQUAD["🤖 Squad Autônoma"]
        DEV["🛠️ Agent Dev<br/>Código + smoke-test"]
        QA["🧪 Agent QA<br/>Testes unitários<br/>Cenários Gherkin<br/>Build/lint/vet<br/>Watchdog"]
        OPS["🚀 Agent DevOps<br/>CI/CD + Docker<br/>Deploy"]
        PENTEST["🔒 Agent Pentester<br/>Vuln scan<br/>OWASP + segredos"]
    end

    IDEA --> BRAIN
    BRAIN --> SPEC
    SPEC --> APPROVE
    APPROVE -->|"Aprovado: true"| PLAN
    PLAN --> TASKS
    TASKS -->|tasks.md com DAG| DAG
    DAG --> GATE
    GATE -->|Aprovado: true| SPAWN
    SPAWN --> DEV
    SPAWN --> QA
    SPAWN --> OPS
    SPAWN --> PENTEST
    DEV --> MONITOR
    QA --> MONITOR
    OPS --> MONITOR
    PENTEST --> MONITOR
    MONITOR -->|"Falha 3x"| ESCALATE
    MONITOR -->|"DONE"| DONE["[x] tasks.md"]
    ESCALATE -->|"Usuário ajusta"| SPAWN
```

## Fluxo de Desenvolvimento

### 1. Brainstorm da Feature
```bash
# O agente conduz entrevista interativa e gera spec.md
/skill sdd-brainstorm
```

### 2. Geração de Artefatos SDD
```bash
# Gera plan.md (decisões arquiteturais)
/skill sdd-generate-plan

# Gera tasks.md com DAG (fases, dependências, paralelismo)
/skill sdd-generate-tasks
```

### 3. Aprovação Humana
Edite o `spec.md` da feature e altere:
```yaml
Aprovado: true   # ← false → true
```

### 4. Execução Autônoma
```bash
# O orquestrador spawna a squad e gerencia a execução
agent-run runtime-orchestrator "orquestra a feature <ID>"
```

### 5. Intervenção (se necessário)
O orquestrador só escala pro humano quando uma task falha 3 vezes.
Tasks paralelas continuam rodando — só a sub-árvore dependente é pausada.

---

## Setup do Ambiente

### Pré-requisitos
- [Hermes Agent](https://hermes-agent.nousresearch.com) instalado
- Go 1.21+ (para o projeto)
- Git

### 1. Clonar o repositório
```bash
git clone <repo-url>
cd 42_chat
```

### 2. Configurar skills

As skills do projeto vivem em `.hermes/skills/` versionadas no repositório.
O Hermes Agent descobre skills via symlinks planos em `~/.hermes/skills/<categoria>/`.

```bash
# Script automatizado (recomendado)
./scripts/setup-skills.sh

# Ou manualmente, uma por uma:
mkdir -p ~/.hermes/skills/sdd
ln -sf "$(pwd)/.hermes/skills/sdd/brainstorm" ~/.hermes/skills/sdd/brainstorm
ln -sf "$(pwd)/.hermes/skills/sdd/explore-tech" ~/.hermes/skills/sdd/explore-tech
ln -sf "$(pwd)/.hermes/skills/sdd/generate-plan" ~/.hermes/skills/sdd/generate-plan
ln -sf "$(pwd)/.hermes/skills/sdd/generate-tasks" ~/.hermes/skills/sdd/generate-tasks
ln -sf "$(pwd)/.hermes/skills/sdd/init-repo" ~/.hermes/skills/sdd/init-repo
ln -sf "$(pwd)/.hermes/skills/sdd/refactor-artifact" ~/.hermes/skills/sdd/refactor-artifact
ln -sf "$(pwd)/.hermes/skills/sdd/validate" ~/.hermes/skills/sdd/validate

mkdir -p ~/.hermes/skills/general
ln -sf "$(pwd)/.hermes/skills/general/skill-forge" ~/.hermes/skills/general/skill-forge

mkdir -p ~/.hermes/skills/agent
ln -sf "$(pwd)/.hermes/skills/agent/agent-run" ~/.hermes/skills/agent/agent-run

mkdir -p ~/.hermes/skills/doc
ln -sf "$(pwd)/.hermes/skills/doc/extract" ~/.hermes/skills/doc/extract
ln -sf "$(pwd)/.hermes/skills/doc/generate-toc" ~/.hermes/skills/doc/generate-toc
ln -sf "$(pwd)/.hermes/skills/doc/generate-llms-txt" ~/.hermes/skills/doc/generate-llms-txt
```

### 3. Verificar instalação
```bash
hermes skills list | grep sdd
# Deve listar: brainstorm, explore-tech, generate-plan, generate-tasks,
#              init-repo, refactor-artifact, validate
```

### 4. Agentes (futuro)
Quando os agentes da squad forem implementados (features 005-009), o mesmo padrão
de symlink se aplica em `~/.hermes/agents/`.

---

## Estrutura do Projeto

```
42_chat/
├── .github/
│   ├── memory/
│   │   ├── constitution.md    # Regras invioláveis do projeto
│   │   └── tech.md            # Stack homologado
│   └── workflows/             # CI/CD (GitHub Actions)
├── .hermes/
│   ├── skills/                # Skills versionadas
│   │   ├── sdd/               #   Pipeline SDD
│   │   ├── agent/             #   Runners de agente
│   │   ├── doc/               #   Documentação
│   │   └── general/           #   Tooling
│   └── agents/                # Definições de agentes
│       ├── sdd-orchestrator/  #   Gerador de artefatos SDD
│       └── runtime-orchestrator/ # Orquestrador de execução (005)
├── specs/
│   ├── BACKLOG.md             # Backlog de features
│   └── features/
│       ├── 001-start-repo/
│       ├── 002-sdd-templates/
│       ├── 003-forge-skill/
│       ├── 004-sdd-tasks-dag/ # DAG no tasks.md
│       └── 005-runtime-orchestrator/ # Orquestrador de execução
└── scripts/
    └── setup-skills.sh        # Script de setup para novos membros
```

---

## Squad (visão futura)

| Agente | Feature | Responsabilidade | Skills |
|--------|---------|-----------------|--------|
| **Dev** | 006 | Código + smoke-test. Nunca loga, nunca testa unitário | `go-implement`, `go-refactor`, `smoke-check` |
| **QA** | 007 | Multi-função: unit tests, Gherkin, build/lint, watchdog | `go-unit-tests`, `gherkin-scenarios`, `local-test-runner`, `test-watcher` |
| **DevOps** | 008 | Docker, CI/CD, deploy, monitoramento | `docker-build`, `ci-validate`, `deploy-staging` |
| **Pentester** | 009 | Segurança: vuln scan, OWASP, segredos | `dependency-scan`, `owasp-check`, `secret-scan` |

Cada agente é spawnado pelo runtime-orchestrator com um **subset de skills**
selecionado conforme o micro-contexto da task (campo `Papel` + `Arquivos` no tasks.md).

---

## Atualizado em
2026-06-12
