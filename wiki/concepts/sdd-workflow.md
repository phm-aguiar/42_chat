---
title: "SDD Workflow — Pipeline Completo"
category: concepts
tags: [sdd, workflow, pipeline, tutorial]
aliases: [pipeline, fluxo-sdd]
sources: []
summary: Pipeline completo do Spec-Driven Development: brainstorm → spec → plan → tasks (DAG) → orchestrator → agentes. Cada etapa explicada com o exemplo real da feature 006 (agent-dev).
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# SDD Workflow — Pipeline Completo

> O framework SDD autônomo transforma ideias em código funcional através de um pipeline
> de 5 etapas. Humanos aprovam specs. Agentes implementam. O orchestrator coordena.

## Visão Geral

```
1. sdd-brainstorm → spec.md (O QUE)
2. sdd-generate-plan → plan.md (COMO — arquitetura)
3. sdd-generate-tasks → tasks.md (QUEM FAZ O QUÊ — DAG)
4. Aprovação humana: Aprovado: true
5. agent-orchestrator → spawna subagentes (Dev, QA, DevOps, Pentester)
```

## Etapa 1: Brainstorm → spec.md

**Skill:** `sdd-brainstorm`
**Objetivo:** Transformar uma ideia em especificação funcional.

O agente conduz uma entrevista interativa com `clarify()` — uma pergunta por vez.
Cobre 6 dimensões: propósito, escopo, comportamento, edge cases, constraints, critérios de sucesso.

**Exemplo real (feature 006):**
```
Usuário: "brainstorm do agent-dev"
Agente: "Qual o público-alvo e problema central?"
Usuário: "Braço executor do framework: pega spec aprovada + plan e gera código"
...
→ spec.md com 187 linhas, 10 critérios de sucesso
```

**Output:** `specs/features/006-agent-dev/spec.md`
**Gate:** Usuário muda `Aprovado: false` → `Aprovado: true`

## Etapa 2: Generate Plan → plan.md

**Skill:** `sdd-generate-plan`
**Objetivo:** Gerar plano arquitetural com ADRs (Architecture Decision Records).

Lê `spec.md` + `tech.md` + `constitution.md`. Gera 4 seções canônicas:
1. Metadados (stack, escopo)
2. Contratos e Fronteiras (entrada/saída)
3. ADRs (decisões arquiteturais justificadas)
4. Auditoria de Constituição (checklist contra regras)

**Exemplo real (feature 006):**
- 4 ADRs: Hermes nativo, skills plugáveis, comunicação textual, nunca inferir
- 14/14 regras da constituição auditadas

**Output:** `specs/features/006-agent-dev/plan.md`

## Etapa 3: Generate Tasks → tasks.md (DAG)

**Skill:** `sdd-generate-tasks` (v2.0.0)
**Objetivo:** Gerar matriz de execução com DAG (Directed Acyclic Graph).

Interage **fase por fase** com o usuário via `clarify()`. Cada task tem:
- **Papel:** Dev, QA, ou Test
- **Dependências:** quais tasks devem estar concluídas antes
- **Paralelizável:** true/false (baseado em isolamento de Arquivos)
- **Arquivos:** lista exaustiva de paths que a task modifica

**Validação automática:** ciclos (DFS), dependências quebradas, tasks órfãs, conflitos de arquivo.

**Exemplo real (feature 006):**
```
Fase 1: Criação (2 tasks paralelizáveis)
  T001: AGENT.md (Dev)
  T002: context.yaml (Dev)

Fase 2: Validação (2 tasks paralelizáveis)
  T003: Smoke-test happy path (QA, depende T001+T002)
  T004: Contrato BLOCKED (QA, depende T001)

Fase 3: Documentação (2 tasks paralelizáveis)
  T005: BACKLOG.md (Dev)
  T006: AGENTS.md (Dev)
```

**Output:** `specs/features/006-agent-dev/tasks.md`

## Etapa 4: Aprovação Humana

**Gate obrigatório.** O orchestrator NUNCA spawna sem `Aprovado: true`.

O usuário revisa spec.md, plan.md e tasks.md. Se tudo OK:
```markdown
- **Aprovado:** true
```

Se `Aprovado: false`, o orchestrator aborta: "Spec não aprovada. Altere `Aprovado: true` no spec.md e re-invoque."

## Etapa 5: Orchestrator → Execução

**Agente:** `agent-orchestrator`
**Comando:** `agent-run agent-orchestrator "orquestra a feature 006"`

O orchestrator:
1. Verifica `Aprovado: true` (gate)
2. Lê `tasks.md` e extrai DAG
3. Spawna subagentes com janela deslizante (máx 3 simultâneos)
4. Valida evidência de DONE (arquivos existem? smoke-test passou?)
5. Retry automático (máx 3 tentativas, contexto enriquecido)
6. Escala bloqueios para o humano após 3 falhas

**Subagentes spawnados pelo orchestrator:**
| Papel | Agente | Função |
|---|---|---|
| Dev | `agent-dev` | Implementa código, smoke-test |
| QA | `agent-qa` (007) | Testes, Gherkin, lint |
| DevOps | `agent-devops` (008) | CI/CD, Docker, deploy |
| Pentester | `agent-pentester` (009) | Segurança, OWASP, secrets |

> **Nota:** Apenas `agent-dev` (006) está implementado. QA, DevOps e Pentester são features 007-009.

## Exemplo Completo: Feature 006 (Agent Dev)

```
sdd-brainstorm (6 perguntas, 5 min)
     ↓
spec.md (187 linhas, Aprovado: true)
     ↓
sdd-generate-plan (4 ADRs, 14/14 auditoria)
     ↓
plan.md (64 linhas)
     ↓
sdd-generate-tasks (3 fases, 6 tasks, interação fase por fase)
     ↓
tasks.md (DAG validado: sem ciclos, arquivos disjuntos)
     ↓
agent-orchestrator → spawna agent-dev
     ↓
T001: AGENT.md ✅ | T002: context.yaml ✅
T003: Smoke-test DONE ✅ | T004: Contrato BLOCKED ✅
T005: BACKLOG.md ✅ | T006: AGENTS.md ✅
     ↓
Feature 006 implementada — 6/6 tasks concluídas
```

## Conceitos-Chave

- **DAG (Directed Acyclic Graph):** Grafo de dependências sem ciclos. Permite execução paralela segura
- **Isolamento de Arquivos:** Tasks paralelas nunca compartilham paths. Garantido pelo `sdd-generate-tasks`
- **Skills plugáveis:** Agentes recebem skills da stack (ex: `go-implement`) como trilhos, não jaulas
- **Nunca inferir:** Ambiguidade na spec = BLOCKED. O agente pergunta, não adivinha
- **Vault Obsidian:** Toda mudança estrutural é documentada no vault (`wiki/`)

## Relacionado

- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero
- [[concepts/constitution|Constituição]] — Regras arquiteturais
- [[concepts/tech|Stack Tecnológica]] — Stack homologada
- [[projects/42_chat/features/feature-006-agent-dev|Feature 006]] — Exemplo real usado neste documento
