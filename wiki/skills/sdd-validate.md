---
title: "sdd-validate"
category: skills
tags: [sdd, skill, validacao, qualidade]
sources: [.hermes/skills/sdd/validate/SKILL.md]
summary: "Valida a conformidade SDD do repositorio: diretorios obrigatorios, artefatos por feature, AGENTS.md. Reporta PASS/FAIL/WARN."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.484
updated: "2026-06-19"
---

# sdd-validate

> Auditor de conformidade SDD. Read-only — nunca modifica arquivos.

## Localizacao
`.hermes/skills/sdd/validate/SKILL.md`

## Quando usar
- Antes de commit (gate de qualidade)
- Apos criar nova feature (spec/plan/tasks existem?)
- Periodicamente

## Checks
- `.github/memory/` (constitution.md, tech.md)
- `specs/` (features, domain-events, infra)
- Cada feature: spec.md, plan.md, tasks.md
- `AGENTS.md`

## Coordenação (LATTE)

> Feature 001: LATTE Coordination. Quando o modo LATTE está ativo (`graph-operators: enabled` no `tasks.md`), o `sdd-validate` extrai métricas do coordination graph final (`G_final`) e gera um relatório de eficiência da orquestração multi-agente.

### Como o validate extrai métricas do G_final

Após a execução LATTE, o `G_final` é persistido pelo módulo `graph_persistence.py` em `wiki/projects/<nome>/coordination-graph.md`. O `sdd-validate` lê esse artefato e computa as seguintes métricas:

| Métrica | Descrição | Origem |
|---|---|---|
| **overwrite_rate** | Número de sobrescritas de trabalho entre Workers | Contagem de `WriteConflict` nodes no `G_final` |
| **wasted_chars** | Caracteres escritos que não chegaram ao produto final | Soma de `wasted_output` por task (outputs descartados em Releases/Closes) |
| **idle_rounds** | Proporção de rounds com agente ocioso (%) | `rounds_idle / rounds_total` do heartbeat log |
| **straggler_p95** | Tempo no percentil 95 por task (segundos) | Distribuição de `wall_clock` por task; p95 calculado |
| **inter_agent_messages** | Total de mensagens trocadas entre Lead e Workers | Soma de operadores (Assign, Claim, Complete, Discover, Release, Close, Verify) |
| **tokens** | Tokens totais gastos na execução | Soma de `token_count` reportado por Worker |
| **wall_clock** | Tempo total de execução (segundos) | `end_time - start_time` do orchestrator |
| **rounds_total** | Total de rounds executados | Contagem de iterações do loop A4.5 |
| **tasks_discovered** | Tasks criadas dinamicamente via `Discover` | Contagem de nodes `discovered: true` no `G_final` |
| **verifications_spawned** | Verificações seletivas via `Verify` | Contagem de nodes `type: verify` no `G_final` |
| **releases** | Tasks reassinadas via `Release` | Contagem de operações `Release` no log |

### Thresholds de alerta

Cada métrica é comparada contra thresholds configuráveis. O resultado é reportado como `PASS`, `WARN`, ou `FAIL`:

| Métrica | Condição | Nível | Justificativa |
|---|---|---|---|
| **overwrite_rate** | ≤ 0.2 (até 20% das tasks com conflito) | PASS | Alvo LATTE paper: 4.3 conflitos/trial |
| | > 0.2 | **WARN** | Indica coordenação ineficiente; Workers estão pisando no trabalho uns dos outros |
| **wasted_chars** | ≤ 5000 | PASS | Alvo LATTE paper: ~5K chars desperdiçados |
| | > 5000 | **WARN** | Output descartado elevado; possível problema de context scoping |
| **idle_rounds** | ≥ 40% | PASS | Idle alto é esperado (Workers aguardam dependências); indica ausência de contenção |
| | < 40% | **WARN** | Possível contenção ou Workers sobrecarregados (idle baixo = sempre ocupado = possível gargalo) |
| **straggler_p95** | ≤ 130s | PASS | Alvo LATTE paper: p95 < 130s |
| | > 130s | **WARN** | Tail latency alta; possível Worker lento ou task muito complexa |
| **completion_rate** | = 1.0 (100% tasks concluídas) | PASS | Feature totalmente implementada |
| | < 1.0 | **FAIL** | Tasks pendentes no `G_final`; feature incompleta — requer intervenção |
| **inter_agent_messages** | < 50 | PASS | Overhead de comunicação dentro do esperado |
| | ≥ 50 | **WARN** | Overhead elevado pode indicar muitas rodadas de negociação ou disputa de tasks |
| **tokens** | Sem threshold fixo | INFO | Reportado para baseline comparison; não gera WARN/FAIL isoladamente |
| **wall_clock** | Sem threshold fixo | INFO | Reportado para baseline comparison; não gera WARN/FAIL isoladamente |

### Formato do relatório de coordenação no output

Quando o modo LATTE está ativo, o `sdd-validate` adiciona a seção `Coordenação (LATTE):` ao relatório padrão:

```
Coordenação (LATTE):
  Overwrite rate:        3 / 12 tasks (25%)    WARN
  Concurrent writes:     1                       PASS
  Wasted chars:          3,142                   PASS
  Idle rounds:           48.7%                   PASS
  Inter-agent messages:  15                      PASS
  Straggler p95:         87s                     PASS
  Rounds total:          12
  Tasks discovered:      3 (dinâmicas)
  Verifications spawned:  1
  Releases:              0
  Completion:            12/12 (100%)            PASS
  Tokens:                148,231
  Wall clock:            3m 42s
```

Se o modo LATTE **não** estiver ativo (`graph-operators` ausente ou `disabled`), a seção é omitida e o validate opera em modo legacy (apenas checks estruturais).

### Módulos relacionados

- **`metrics.py`** (em `.hermes/skills/sdd/validate/`): Implementa a extração e cálculo das métricas a partir do `G_final`. Funções: `extract_coordination_metrics(g_final_path) -> dict`, `evaluate_thresholds(metrics: dict) -> list[Alert]`, `format_coordination_report(metrics, alerts) -> str`.
- **`graph_persistence.py`** (em `.hermes/skills/sdd/latte-coordination/`): Persiste o `G_final` como artefato Markdown após a execução LATTE. Formato: tabela de nodes + grafo ASCII + log de operadores. O `sdd-validate` lê este artefato como entrada primária para as métricas de coordenação.

### Utility Score e Feedback Loop

> Feature 002: Wiki Experiential Memory. O `sdd-validate` computa um **utility score** a partir das métricas de coordenação, alimentando um **feedback loop** que atualiza scores de estratégias no vault de memória experiencial.

#### Cálculo do Utility Score

O utility score `u` consolida as três métricas principais de eficiência em um valor normalizado entre 0 e 1:

```
u = 1.0 - (overwrite * 0.4 + waste * 0.3 + idle * 0.3)
```

Onde:
- **overwrite** = `overwrite_rate` (proporção de tasks com conflito, 0–1)
- **waste** = `wasted_chars_normalized` = `min(wasted_chars / 10000, 1.0)` (output descartado normalizado)
- **idle** = `1.0 - idle_rounds` (inverso da proporção de rounds ociosos; idle alto reduz penalidade)

Quanto menor a penalidade `(overwrite*0.4 + waste*0.3 + idle*0.3)`, maior o utility score — indicando execução mais eficiente.

#### Mapeamento Qualitativo

| Utility (u) | Classificação | Interpretação |
|---|---|---|
| **u ≥ 0.80** | 🟢 **Excelente** | Coordenação altamente eficiente; Workers bem orquestrados, pouco desperdício. Estratégia candidata a reforço positivo. |
| **0.60 ≤ u < 0.80** | 🟡 **Bom** | Execução dentro do esperado; pontos de melhoria identificáveis mas não críticos. |
| **0.40 ≤ u < 0.60** | 🟠 **Regular** | Sinais de ineficiência; contenção ou desperdício acima do tolerável. Dispara revisão de estratégia. |
| **u < 0.40** | 🔴 **Ruim** | Coordenação problemática; possível necessidade de redesign da distribuição de tasks ou scoping. |

#### Feedback Loop: Utility → Score Update

O utility score alimenta um **ciclo de feedback experiencial**:

1. **Coleta**: `sdd-validate` extrai métricas do `G_final` e computa `u` usando a fórmula acima.
2. **Registro**: O score `u` e sua classificação qualitativa são persistidos no vault de memória experiencial (`wiki/experiential/`) via `feedback.py`.
3. **Atualização de Scores**: `scoring.py` lê o histórico de utility scores por estratégia e ajusta os pesos (scores) das estratégias de coordenação no vault:
   - Utility consistentemente **Excelente** → score da estratégia **sobe** (reforço)
   - Utility consistentemente **Ruim** → score da estratégia **desce** (depreciação)
4. **Influência em Execuções Futuras**: Scores atualizados guiam a seleção de estratégias de coordenação em features subsequentes, fechando o loop de melhoria contínua.

##### Diagrama do Fluxo

```
G_final ──► metrics.py ──► u = 1.0 - (overwrite*0.4 + waste*0.3 + idle*0.3)
                              │
                              ▼
                    ┌─────────────────────┐
                    │   feedback.py        │
                    │   record_utility()   │
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │   scoring.py         │
                    │   update_scores()    │
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │  Vault Experiencial  │
                    │  (scores atualizados)│
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │  Próxima feature    │
                    │  (estratégias        │
                    │   ranqueadas)        │
                    └─────────────────────┘
```

#### Módulos Relacionados ao Feedback

- **`scoring.py`** (em `.hermes/skills/sdd/validate/`): Mantém e atualiza scores de estratégias com base no histórico de utility. Funções: `update_strategy_scores(utility: float, strategy_id: str) -> None`, `get_top_strategies(limit: int) -> list[dict]`.
- **`feedback.py`** (em `wiki/experiential/`): Interface de persistência do feedback loop experiencial. Funções: `record_utility(feature_id: str, utility: float, classification: str, metrics: dict) -> None`, `get_utility_history(strategy_id: str) -> list[dict]`.

## Relacionado
- [[skills/sdd-init-repo]] — Cria a estrutura que validate audita
- [[skills/wiki-lint]] — Equivalente para o vault
- [[concepts/coordination-graph]] — Estrutura do G_final e operadores LATTE
- [[projects/42_chat/features/feature-001-latte-coordination|Feature 001 — LATTE Coordination]] — Feature que implementa o modo LATTE

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar validacoes anteriores, problemas recorrentes de conformidade, ou excecoes documentadas antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.