---
feature_id: "005"
plan_for: "LATTE Hardening — Budget, Timeout, Failure Propagation & Quality Gates"
spec: "specs/features/005-latte-hardening/spec.md"
created: "2026-06-20"
author: phm-aguiar
stack: "Hermes Agent (Python 3.10+) + LATTE coordination modules"
---

# Plano Arquitetural — LATTE Hardening

## Metadados

| Campo | Valor |
|---|---|
| **Stack** | Hermes Agent (runtime Python), LATTE modules (orchestrator, dispatcher, heartbeat, lead_operators, worker_operators, metrics, graph_persistence) |
| **Feature fonte** | `specs/features/005-latte-hardening/spec.md` |
| **Escopo (1 frase)** | Adicionar budget tracking, timeout/falback, partial failure propagation, verify determinístico, context summarization, equal-weight merge e tool ceiling ao coordination graph LATTE — 7 patches de hardening com benchmark comparativo |

## Contratos e Fronteiras

### Entrada

| Artefato | Formato | Fonte |
|---|---|---|
| `G_t` (coordination graph) | `CoordinationGraph` em memória | `orchestrator.py` |
| `tasks.md` com `graph-operators: enabled` | YAML frontmatter + DAG | Feature sendo orquestrada |
| Config de hardening (opcional) | flags/parâmetros no `tasks.md` ou CLI | Usuário |

### Saída

| Artefato | Formato | Destino |
|---|---|---|
| `G_final` com budget/timeout/errors | `coordination-graph.md` (estendido) | Wiki da feature |
| Métricas estendidas | Seção `LATTE Hardening` no validate | stdout |
| Código dos módulos LATTE | `.hermes/skills/sdd/latte_coordination/*.py` | Repo |

### Novos Campos no CoordinationGraph State

```
CoordinationGraph:
  + llm_calls_made: int = 0
  + max_llm_calls: int = 25
  + errors: list[dict] = []          # Annotated[list, add]
  + completed_summary: str = ""
  + round_since_summary: int = 0
  + operator_timeout: int = 45        # segundos
  + verify_mode: "llm" | "deterministic" = "deterministic"
```

### Operadores (sem mudança nas preconditions)

Os 7 operadores (Assign, Claim, Complete, Release, Close, Verify, Discover) mantêm pre/post conditions. Mudanças são internas:
- **Verify**: adiciona checks determinísticos antes do LLM
- **Complete**: reporta `llm_calls_made` do worker
- **Release/Close**: registram em `errors` quando acionados

### Fronteiras (o que NÃO muda)

- Workers NÃO acessam `errors` diretamente — o dispatcher injeta no context scoping
- O grafo continua em memória (ADR-002 original mantido)
- `delegate_task` como mecanismo de spawn (ADR-003 original mantido)
- Modo legacy (tasks.md sem `graph-operators`) inalterado

## ADRs (Architecture Decision Records)

### ADR-006: Budget tracking no state, não em sistema separado

**Decisão:** `llm_calls_made` e `max_llm_calls` são campos do `CoordinationGraph`, incrementados a cada spawn de worker + calls reportadas. O enforce é no orchestrator: se `llm_calls_made >= max_llm_calls` → `force_finalize()`.

**Justificativa:** O paper Multi-Agent Systems mostra `BudgetedState` como padrão: *"Set the limit before each run based on task complexity. Cap LLM calls at the state level."* Manter no state (não em métricas ou config global) permite que o budget seja específico por feature — uma feature simples pode ter cap=15, uma complexa cap=40. O enforce no orchestrator é deterministic e visível no G_final.

**Alternativa rejeitada:** Budget global no `config.yaml` do Hermes. Rejeitado porque features têm complexidade heterogênea — um cap fixo seria muito restritivo pra features complexas ou muito permissivo pra simples. Budget por feature no `tasks.md` é mais granular.

### ADR-007: Timeout como decorator no dispatcher, heartbeat como safety net

**Decisão:** Timeout é aplicado no `dispatcher.py` via `asyncio.wait_for` com `operator_timeout` segundos (default 45). Se timeout, executa `fallback_fn` registrado por task. Heartbeat (H=4) permanece como safety net reativa para casos que o timeout não pegou.

**Justificativa:** O paper mostra `with_timeout` decorator: *"For some agents, a timeout means 'skip this step and continue with partial results.' For others, it means 'abort the entire workflow.'"* Timeout preventivo + heartbeat reativo = duas camadas. Timeout corta em 45s (antes dos 48s do heartbeat), mas heartbeat ainda pega workers que respondem mas não produzem (ex: loop infinito sem timeout de rede).

**Alternativa rejeitada:** Timeout via `signal.SIGALRM`. Rejeitado porque (a) SIGALRM é Unix-only, (b) não funciona com `asyncio`, (c) `delegate_task` já é async-compatible. `asyncio.wait_for` é cross-platform e testável.

### ADR-008: Partial failure como state field (agent_errors), não como exceção

**Decisão:** Falhas de worker são registradas em `errors: list[dict]` no CoordinationGraph (campo com reducer `add`). Workers downstream recebem `upstream_errors` no context scoping e decidem: continuar com fallback ou pular. Nenhuma exceção é lançada no orchestrator — o grafo absorve falhas.

**Justificativa:** O paper é taxativo: *"Never silently drop a failure and continue, because the final output will look complete but the user has no way to know that a step was skipped."* O campo `errors` resolve isso: (a) downstream workers sabem que input é degradado, (b) G_final mostra quais tasks falharam, (c) o usuário vê `errors: ["T003: timeout"]` no output final. Padrão similar ao `error_count` do LangGraph-in-Production.

**Alternativa rejeitada:** Lançar exceção e abortar pipeline. Rejeitado porque (a) perde trabalho já feito, (b) viola o princípio de resiliência do paper, (c) DAGs com 5+ tasks raramente justificam abort completo por 1 falha.

### ADR-009: Verify determinístico primeiro, LLM como fallback

**Decisão:** `Verify(v)` primeiro executa 5 checks determinísticos (formato, artefato, exit code, tamanho, anti-padrões). Se todos passam → approved sem LLM. Se algum falha → escala pro LLM (comportamento atual). Modo configurável: `verify_mode: "deterministic"` (default) ou `"llm"` (skip checks).

**Justificativa:** O paper Multi-Agent: *"We use deterministic checks (output format validation, citation existence checks, length constraints) instead of LLM evaluation at agent boundaries."* LLM-as-judge é mal calibrado (leniente com mesmo modelo, crítico com modelos diferentes). Checks determinísticos são objetivos, custam zero tokens, e pegam falhas estruturais que o LLM ignoraria.

**Alternativa rejeitada:** Verify só determinístico (sem fallback LLM). Rejeitado porque checks determinísticos não avaliam qualidade semântica — um worker pode gerar código que compila mas não implementa o que foi pedido. O LLM fallback cobre esse gap.

### ADR-010: Context summarization a cada 4 rounds (do paper, não arbitrário)

**Decisão:** A cada 4 rounds (`round_since_summary >= 4`), o Lead sumariza `completed_tasks` em 1-2 linhas no campo `completed_summary`. O Lead vê `completed_summary` + últimos 4 rounds (não histórico completo). Intervalo de 4 rounds é fixo (paper source).

**Justificativa:** O paper: *"By turn 8 in a supervisor pattern, the 'completed tasks' context can be 3,000 tokens. We now summarize completed tasks every 4 turns."* O número 4 não é arbitrário — vem dos experimentos do Kalvium Labs com 8 projetos. Sumarizar com mais frequência gasta LLM calls desnecessárias; com menos frequência, o contexto já saturou.

**Alternativa rejeitada:** Sumarização adaptativa (baseada em tokens, não rounds). Rejeitado porque (a) contar tokens de `completed_tasks` é frágil (depende do tokenizer do modelo), (b) rounds são determinísticos, (c) paper já testou 4 rounds como sweet spot.

### ADR-011: Toolsets por task via delegate_task (API existente)

**Decisão:** O `dispatcher.py` passa `toolsets` no spawn do worker baseado no tipo da task (Dev, QA, DevOps). Mapeamento default: Dev → `[terminal, file, patch]`, QA → `[terminal, file]`, DevOps → `[terminal, file, docker]`. Configurável por task no `tasks.md`.

**Justificativa:** O paper: *"Specializing agents means each one sees 4-6 relevant tools instead of the full library."* O `delegate_task` já suporta `toolsets` nativamente — não precisamos reinventar. A redução de 20+ tools para 4-6 reduz ~2K tokens no system prompt por worker.

**Alternativa rejeitada:** Tool filtering no context scoping (pós-spawn). Rejeitado porque (a) tools são definidas no system prompt antes do spawn, (b) filtrar pós-spawn não reduz tokens, (c) `delegate_task` já tem o parâmetro certo.

### ADR-012: Merge equal-weighting como prompt engineering (não como lógica de merge)

**Decisão:** O prompt de merge no dispatcher inclui constraint explícita: "Weight each input equally regardless of length. Note when a domain was under-researched (< 100 words)." Nenhuma lógica de merge é alterada — é puro prompt engineering.

**Justificativa:** O paper: *"We now explicitly instruct the synthesis agent to weight inputs equally."* Adicionar uma constraint no prompt custa zero em complexidade de código e ~20 tokens. O ganho é evitar que outputs de 800 palavras dominem outputs de 200 palavras no merge.

**Alternativa rejeitada:** Lógica de truncamento/padding para equalizar tamanhos. Rejeitado porque (a) perderia informação, (b) o problema é de atenção do modelo, não de tamanho de input, (c) prompt engineering resolve com custo zero.

## Auditoria de Constituição

> Repositório `42_Framework` é meta-framework sem `constitution.md` formal. Portões derivados do pipeline SDD em `wiki/concepts/sdd.md`.

| Regra | Status | Evidência |
|---|---|---|
| **Spec aprovado antes de implementar** | ✅ PASS | `spec.md` com `Aprovado: true` |
| **Vault wiki atualizado após feature** | ✅ PLAN | Atualizar `wiki/projects/42_Framework/features/001-latte-coordination.md` com novos campos; atualizar `wiki/references/papers/LangGraph-in-Production.md` (status: analyzed → partially_addressed) |
| **Nunca inferir — ambiguidade = pergunta** | ✅ PASS | ADRs 006-012 documentam decisões com alternativas rejeitadas |
| **Tasks paralelas com arquivos disjuntos** | ✅ PASS | Mudanças 1-5 tocam arquivos diferentes (orchestrator.py, dispatcher.py, lead_operators.py, worker_operators.py, metrics.py, heartbeat.py) |
| **Hermes nativo — sem dependências externas** | ✅ PASS | `asyncio` (stdlib), `delegate_task` (nativo). Sem novas dependências pip |
| **Retrocompatibilidade** | ✅ PASS | Modo legacy inalterado; novos campos com defaults preservam comportamento atual; 39 testes existentes como gate |
