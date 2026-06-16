---
title: "sdd-generate-tasks"
category: skills
tags: [sdd, skill, tasks, dag, execucao, planejamento]
sources: [.hermes/skills/sdd/generate-tasks/SKILL.md, .hermes/skills/sdd/generate-tasks/references/task-rules.md]
summary: "Gera tasks.md com DAG de tarefas atomicas a partir de spec.md e plan.md aprovados. Cada task tem Papel, Dependencias, flag de Paralelizavel e Arquivos. Validacao anti-ciclo e anti-conflito."
provenance:
  extracted: 0.82
  inferred: 0.13
  ambiguous: 0.05
base_confidence: 0.60
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
updated: "2026-06-15"
---

# sdd-generate-tasks

> Gera `tasks.md` com matriz de execucao DAG. Ultimo passo do pipeline SDD antes da execucao pelo orchestrator.

## Localizacao
`.hermes/skills/sdd/generate-tasks/SKILL.md`

## Quando usar
- Apos `spec.md` aprovado E `plan.md` gerado
- Usuario diz "gerar tasks", "criar tasks.md", "generate tasks", "criar tarefas"
- Precisa decompor feature em tarefas atomicas com metadados de paralelismo

## Fluxo (7 passos + HARD-GATE)
**Passo 0 — Approval Gate:** Verifica `Aprovado: true` no spec.md. Se `false`, ABORTA.

1. **Identificar feature** — usuario informa ou skill pergunta
2. **Ler spec.md + plan.md** — funcionalidade, cenarios BDD, stack, ADRs
3. **Carregar task-rules.md** — regras de atomicidade, DAG, fases canonicas
4. **Derivar tarefas atomicas** — uma acao por task, com metadados DAG:
   - `Papel:` Dev | QA
   - `Dependencias:` Txxx, Tyyy | Nenhuma
   - `Paralelizavel:` true | false
   - `Arquivos:` lista exaustiva de paths
5. **Interacao fase por fase** via `clarify()` — NUNCA gere todas de uma vez
6. **Validar DAG completo** — ciclos, deps quebradas, orfas, conflitos de arquivo
7. **Salvar** — pergunta antes de sobrescrever

## Regras de Atomicidade (de `references/task-rules.md`)
- **Uma acao por task:** "Criar X e testar Y" = 2 tarefas
- **Paralelismo = arquivos disjuntos:** tasks na mesma fase so sao paralelas se Arquivos nao se intersectam
- **Excecao inteligente:** `.feature` (QA) e `.go` (Dev) no mesmo diretorio = sem conflito
- **Numeracao global:** T001, T002... nao reinicia por fase

## Fases Canonicas
| Fase | Conteudo | Papel |
|---|---|---|
| 1: Fundacao | Contratos, schemas, configs, estrutura | Dev |
| 2: Implementacao | Logica de negocio, adapters, handlers | Dev + QA |
| 3: Validacao | Testes, CI, linting, smoke test | QA |
| 4: Documentacao | README, llms.txt, AGENTS.md | Dev |

## Validacao do DAG (Passo 6)
- **Ciclos:** DFS com deteccao de back-edge → reporta e corrige
- **Deps quebradas:** toda ref em `Dependencias:` deve existir
- **Orfas:** task sem deps e sem dependentes → pergunta se intencional
- **Conflito de arquivos:** tasks `Paralelizavel: true` com Arquivos sobrepostos → forcado sequencial

## Guardrails
- HARD RULE: tasks paralelas NUNCA compartilham paths
- Interacao fase por fase obrigatoria — nunca gere todas de uma vez
- Minimo 4 tarefas (1 por fase)
- Idempotente: pergunta se sobrescreve ou mescla tasks.md existente
- Tarefas ja feitas: verifica filesystem, marca `[x]` se codigo existe

## Relacionado
- [[skills/sdd-generate-plan]] — Passo anterior: gera plan.md
- [[skills/sdd-brainstorm]] — Inicio do pipeline: gera spec.md
- [[skills/agent-run]] — Executa o orchestrator que consome tasks.md
- [[skills/sdd-validate]] — Valida conformidade SDD

## Buscando conhecimento compilado
Use `[[skills/wiki-query|wiki-query]]` para consultar features similares ja documentadas, padroes de decomposicao de tasks, ou decisoes previas sobre atribuicao de papeis (Dev vs QA) antes de gerar tarefas.
