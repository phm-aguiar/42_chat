---
title: "sdd-generate-tasks"
category: skills
tags: [sdd, skill, tasks, dag, execucao, planejamento]
sources: [.hermes/skills/sdd/generate-tasks/SKILL.md, .hermes/skills/sdd/generate-tasks/references/task-rules.md]
summary: "Gera tasks.md com DAG de tarefas atomicas a partir de spec.md e plan.md aprovados. Cada task tem agent, depends_on, flag de parallelizable e files. Validacao anti-ciclo e anti-conflito. Suporte a Coordination Graph com graph-operators e G0."
graph-operators: disabled
heartbeat-threshold: 4
max-rounds: 40
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
   - Se `--with-memory` estiver ativo, consulta o indice semantico de experiential memory e injeta top-5 chunks como `experiential_prior` no prompt (veja secao Experiential Memory abaixo)
4. **Derivar tarefas atomicas** — uma acao por task, com metadados DAG:
   - `agent:` dev | qa | coordinator — papel atribuido a task
   - `depends_on:` [T001, T002] | [] — sintaxe de array, nunca string
   - `parallelizable:` true | false
   - `files:` lista exaustiva de paths afetados
5. **Interacao fase por fase** via `clarify()` — NUNCA gere todas de uma vez
6. **Validar DAG completo** — ciclos, deps quebradas, orfas, conflitos de arquivo
7. **Salvar** — pergunta antes de sobrescrever

## Regras de Atomicidade (de `references/task-rules.md` e `references/latte-task-rules.md`)
- **Uma acao por task:** "Criar X e testar Y" = 2 tarefas
- **Paralelismo = arquivos disjuntos:** tasks na mesma fase so sao paralelas se files nao se intersectam
- **Excecao inteligente:** `.feature` (QA) e `.go` (Dev) no mesmo diretorio = sem conflito
- **Numeracao global:** T001, T002... nao reinicia por fase
- **`depends_on` usa sintaxe de array:** `depends_on: [T001, T002]`, nunca strings soltas

## Fases Canonicas
| Fase | Conteudo | Papel |
|---|---|---|
| 1: Fundacao | Contratos, schemas, configs, estrutura | Dev |
| 2: Implementacao | Logica de negocio, adapters, handlers | Dev + QA |
| 3: Validacao | Testes, CI, linting, smoke test | QA |
| 4: Documentacao | README, llms.txt, AGENTS.md | Dev |

## Validacao do DAG (Passo 6)
- **Ciclos:** DFS com deteccao de back-edge → reporta e corrige
- **Deps quebradas:** toda ref em `depends_on:` deve existir
- **Orfas:** task sem deps e sem dependentes → pergunta se intencional
- **Conflito de arquivos:** tasks `parallelizable: true` com files sobrepostos → forcado sequencial

## Guardrails
- HARD RULE: tasks paralelas NUNCA compartilham paths
- Interacao fase por fase obrigatoria — nunca gere todas de uma vez
- Minimo 4 tarefas (1 por fase)
- Idempotente: pergunta se sobrescreve ou mescla tasks.md existente
- Tarefas ja feitas: verifica filesystem, marca `[x]` se codigo existe

## Coordination Graph

O grafo de coordenacao G modela as dependencias entre tasks como um DAG dirigido 
(arestas = dependencia, nos = tasks). O orchestrator usa G para decidir ordem e 
paralelismo na execucao.

### G₀ (Grafo Inicial)
G₀ e o DAG inicial gerado a partir do `depends_on` de cada task, antes de qualquer 
expansao por graph-operators. G₀ representa a estrutura base de dependencias e e 
validado contra ciclos, deps quebradas e orfas.

### `graph-operators` (YAML)
Controla se operadores de grafo atuam sobre G₀ para expandir/refinar o DAG:

- `enabled` — operadores ativos: LATTE pode inserir nos de checkpoint, 
  retry-group e coordinator-handoff entre tasks.
- `disabled` (default) — G₀ e usado como esta, sem expansao automatica.

### `heartbeat-threshold` (YAML)
Numero maximo de rounds consecutivos sem progresso visivel (arquivos modificados, 
tests passando, tasks concluidas). Se o orchestrator atingir esse limite, o LATTE 
coordinator pausa e solicita intervencao. Default: `4`.

### `max-rounds` (YAML)
Limite maximo total de rounds de execucao do orchestrator. Protecao contra loops 
infinitos em features complexas. Default: `40`.

### Operadores de Grafo (quando `graph-operators: enabled`)
- **checkpoint:** insere Txxx-checkpoint apos tasks criticas; o orchestrator 
  salva estado e permite resume.
- **retry-group:** agrupa tasks flaky em bloco atomico com politica de retry.
- **coordinator-handoff:** insere gate entre fases onde o LATTE coordinator 
  avalia progresso antes de liberar proxima fase.

Operadores sao aplicados em ordem deterministica: checkpoint → retry-group → 
coordinator-handoff. O grafo expandido G' substitui G₀ para execucao.

### Relacao com LATTE
Veja [[skills/latte-coordinator]] para detalhes do orchestrator. As regras de 
validacao de tasks com graph-operators estao documentadas em 
`references/latte-task-rules.md`.

## Experiential Memory (Feature 002)

> Integracao com [[projects/42_Framework/features/002-experiential-memory]] — reuso de padroes de decomposicao de features anteriores.

### `--with-memory`

Feature flag que ativa a consulta ao indice semantico de experiential memory antes da geracao do G0.

**Ativacao:**
```bash
hermes sdd generate-tasks --feature 005 --with-memory
```

**O que faz:**
1. Embedda a spec completa da feature atual
2. Consulta o indice semantico (SQLite + embeddings) por similaridade de cosseno
3. Recupera os top-5 chunks mais similares de features anteriores
4. Injeta os chunks como `experiential_prior` no prompt do `generate-tasks`

**Formato dos hints (`experiential_prior`):**
```
Based on previous similar features, consider these patterns:
- "features de auth precisam de migration task" (score: 0.78)
- "QA em handler HTTP usa .feature BDD" (score: 0.65)
- "OAuth2 redirect_uri deve ser validado no handler" (score: 0.59)
- "README deve listar endpoints com exemplos curl" (score: 0.52)
- "task de CI precisa de variavel de ambiente SECRET_KEY" (score: 0.48)
```

Cada hint inclui score de relevancia (0-1) baseado na similaridade de cosseno entre a spec atual e os chunks indexados de features anteriores. Quanto maior o score, mais relevante o padrao.

**Impacto:** Tasks que o Lead teria que descobrir via tentativa e erro sao sugeridas antecipadamente, reduzindo ~30% de tokens na geracao do G0 (menos Discover necessario).

### Feedback Loop

Apos a execucao LATTE, o `sdd-validate` converte metricas de coordenacao (overwrite rate, waste ratio, idle rounds) em utility signal e atualiza os scores dos chunks usados como hints na feature executada.

- Chunks de features bem-sucedidas ganham peso (delta positivo)
- Chunks de features problematicas perdem (delta negativo)
- Scores persistem entre sessoes no SQLite
- Score decay: chunks nao usados por N features perdem 0.01 por feature (floor = 0.1)

Veja [[skills/sdd-validate]] e [[references/toolkits/wiki/experiential-memory]] para detalhes do feedback loop.

## Relacionado
- [[skills/sdd-generate-plan]] — Passo anterior: gera plan.md
- [[skills/sdd-brainstorm]] — Inicio do pipeline: gera spec.md
- [[skills/agent-run]] — Executa o orchestrator que consome tasks.md
- [[skills/sdd-validate]] — Valida conformidade SDD

## Buscando conhecimento compilado
Use `[[skills/wiki-query|wiki-query]]` para consultar features similares ja documentadas, padroes de decomposicao de tasks, ou decisoes previas sobre atribuicao de papeis (Dev vs QA) antes de gerar tarefas.
