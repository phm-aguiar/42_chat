---
title: "SDD Workflow — Pipeline Completo"
category: concepts
tags: [sdd, workflow, pipeline, tutorial]
aliases: [pipeline, fluxo-sdd]
sources: []
summary: "Pipeline completo do Spec-Driven Development: brainstorm → spec → plan → tasks (DAG) → orchestrator → agentes. Cada etapa explicada com o exemplo real da feature 006 (agent-dev)."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-19"
---

# SDD Workflow — Pipeline Completo

> O framework SDD autônomo transforma ideias em código funcional através de um pipeline
> de 5 etapas. Humanos aprovam specs. Agentes implementam. O orchestrator coordena.
> O **modo LATTE** (habilitado via `graph-operators: enabled` no `tasks.md`) ativa um
> coordination graph dinâmico com 7 operadores para execução descentralizada e resiliência
> a falhas via rounds, heartbeat e frontier dispatch (Algorithm A4.5).

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

## Modo LATTE — Coordenação Dinâmica

> **Feature 001: LATTE Coordination.** O modo LATTE é uma extensão do orchestrator
> que substitui a janela deslizante centralizada por um **coordination graph dinâmico**
> com execução descentralizada. Habilitado via `graph-operators: enabled` no `tasks.md`.

### Ativação

```yaml
# tasks.md — configuração LATTE
graph-operators: enabled   # ativa coordination graph dinâmico
max-rounds: 20             # limite de rounds (opcional, default 20)
heartbeat-sec: 30          # heartbeat entre operadores (opcional, default 30)
```

Quando `graph-operators` está `disabled` ou ausente, o orchestrator usa o modo
padrão de janela deslizante (Etapa 5).

### Pipeline Estendido

```
1. sdd-brainstorm → spec.md
2. sdd-generate-plan → plan.md
3. sdd-generate-tasks → tasks.md (DAG + graph-operators: enabled)
4. Aprovação humana
5. agent-orchestrator → LATTE Coordination Engine
   ├── Algorithm A4.5 (rounds, heartbeat, frontier, dispatch)
   ├── 7 operadores (Discover, Assign, Claim, Complete, Release, Close, Verify)
   └── G_final salvo como coordination-graph.md no wiki/
```

### Algorithm A4.5 — Execução por Rounds

O orchestrator segue o **Algorithm A4.5** com execução baseada em rounds:

| Mecanismo | Descrição |
|---|---|
| **Rounds** | Cada round avalia o estado do grafo, despacha tasks prontas e coleta resultados. O processo termina quando `G_final` tem todas as tasks `Closed` + `Verified` ou `max-rounds` é atingido. |
| **Heartbeat** | A cada `heartbeat-sec` segundos, o orchestrator faz ping nos operadores ativos. Se um operador não responde, sua task volta para `Ready` e entra na frontier do próximo round. |
| **Frontier** | Conjunto de tasks prontas para dispatch no round atual — tasks cujas dependências estão todas `Closed` e que ainda não estão atribuídas. |
| **Dispatch** | O orchestrator seleciona tasks da frontier e as despacha para subagentes. O dispatch respeita `max-parallel` e isolamento de arquivos (tasks paralelas nunca compartilham paths). |

### Os 7 Operadores do Coordination Graph

Cada task no DAG transita por estados gerenciados por **7 operadores**:

| Operador | Estado | Gatilho | Ação |
|---|---|---|---|
| **Discover** | `Ready` | Dependências satisfeitas | Task entra na frontier do round |
| **Assign** | `Assigned` | Dispatch pelo orchestrator | Task atribuída a um subagente (Dev/QA/DevOps) |
| **Claim** | `Claimed` | Subagente aceita a task | Agente confirma que iniciará a execução |
| **Complete** | `Completed` | Subagente finaliza implementação | Evidências registradas (arquivos, smoke-test) |
| **Release** | `Released` | Subagente entrega para verificação | Task disponível para validação cruzada |
| **Close** | `Closed` | Verificação interna ok | Task marcada como concluída no grafo |
| **Verify** | `Verified` | Validação externa (outro agente/QA) | Verificação cruzada aprovada — task imutável |

**Transições de estado no grafo:**

```
Ready → Assigned → Claimed → Completed → Released → Closed → Verified
  ↑        │          │          │                                   
  └────────┴──────────┴──────────┘ (heartbeat timeout → retry)
```

Se um heartbeat timeout ocorre em qualquer estado após `Assigned`, a task
volta para `Ready` e é re-despachada no próximo round (máx 3 tentativas;
após 3 falhas, escala para o humano).

### G_final: coordination-graph.md

Ao final da execução (todas as tasks `Verified` ou `max-rounds` atingido),
o grafo completo é salvo como:

```
wiki/concepts/coordination-graph.md
```

O arquivo contém:

- **Snapshot do grafo:** tasks, estados finais, dependências resolvidas
- **Métricas de execução:** rounds utilizados, timeouts, retries, tempo total
- **Rastreabilidade:** qual agente executou cada task, com timestamps
- **Template de referência:** [[references/toolkits/sdd/coordination-graph-template]] (T023)

> **Nota:** O template `coordination-graph-template.md` será criado na T023 e
> define o schema exato do `coordination-graph.md`. Consulte-o para o formato
> canônico de saída.

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

- [[skills/sdd|sdd toolkit]] — Pipeline SDD consolidado
- [[concepts/sdd|SDD]] — Metodologia Spec-Driven Development
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Integração wiki ↔ pipeline
- [[concepts/onboarding|Onboarding]] — Como começar

- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero
- [[concepts/sdd|SDD]] — Regras arquiteturais
- [[concepts/sdd|SDD]] — Stack homologada
- [[concepts/coordination-graph|Coordination Graph]] — G_final gerado pelo modo LATTE
- [[references/toolkits/sdd/coordination-graph-template|Template Coordination Graph]] — Schema do coordination-graph.md (T023)
- [[projects/42_chat/features/feature-001-latte-coordination|Feature 001 — LATTE Coordination]] — Feature que implementa o modo LATTE
- [[projects/42_chat/features/feature-006-agent-dev|Feature 006]] — Exemplo real usado neste documento
