---
title: "Recipe Step Executor — Executor de Workflows Multi-Step"
summary: "Implementação de referência (Python) de um executor de passos de receita com suporte a condições, dependências (DAG), retry com backoff exponencial, timeout, captura de output via templates e delegação de sub-recipes. Cobertura de testes completa com 6 features e interações cross-feature."
tags:
  - qa
  - bdd
  - testing
  - python
  - reference
category: references
sources:
  - "wiki/_raw/qa/code/recipe_step_executor.py"
  - "wiki/_raw/qa/code/test_recipe_step_executor.py"
  - "wiki/_raw/qa/code/test_gherkin_expert_deliverables.py"
base_confidence: 0.75
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
provenance:
  extracted: 0.15
  inferred: 0.85
  ambiguous: 0.0
created: "2026-06-15"
updated: "2026-06-15"
---

# Recipe Step Executor — Executor de Workflows Multi-Step

Implementação de referência em Python de um executor de passos de receita usado como smoke-test para validação de especificações Gherkin. O executor foi o alvo do experimento controlado que demonstrou a eficácia de Gherkin (+26% sobre English-only) para requisitos comportamentais.

## Features Implementadas

O executor suporta 6 features, cada uma com cobertura completa de testes:

### F1: Conditional Step Execution

Passos podem ter uma condição (`condition`) que determina se executam ou são pulados (SKIPPED). Condições são expressões Python avaliadas no contexto atual.

```python
{"id": "step_a", "command": "echo deploying", "condition": "env == 'prod'"}
```

### F2: Step Dependencies (DAG)

Passos declaram dependências via `blockedBy`, formando um DAG. O executor resolve a ordem topológica automaticamente. Dependências com falha ou timeout propagam `FAILED` com `failure_reason=dependency_failed`.

### F3: Retry com Backoff Exponencial

Passos com `max_retries` > 0 são reexecutados em caso de falha. O backoff é exponencial: 1s, 2s, 4s... Timeouts **nunca** são retentados. Comandos simulados como `fail_then_succeed(N)` permitem testar o mecanismo.

### F4: Timeout Handling

Passos com `timeout_seconds` são executados em thread separada. Se excederem o timeout, são marcados como `TIMED_OUT` (não retentável) e propagam falha para dependentes.

### F5: Output Capture via Templates

O output de cada passo é armazenado no contexto com a chave `step_id`. Steps downstream podem referenciar outputs anteriores usando templates `{{step_id}}`.

### F6: Sub-recipe Delegation

Um passo pode conter `sub_recipe` — uma lista de passos filhos executados em contexto isolado. O parâmetro `propagate_outputs` controla se outputs dos filhos são visíveis no contexto pai.

## Cross-Feature Interactions

Os testes cobrem 7 interações entre features:
- Retry que muda o output entre tentativas (contexto sempre contém o output final)
- Timeout bloqueia passos condicionais (falha por dependência, não skip)
- Sub-recipe filho falha → pai falha sem retry
- Template referenciando passo skipped (literal permanece)
- Diamante com um branch retentado e outro com timeout
- Sub-recipe com outputs propagados alimentando condição do pai

## Estrutura do Código

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `recipe_step_executor.py` | 394 | Executor principal: `RecipeStepExecutor`, `StepResult`, `StepStatus` |
| `test_recipe_step_executor.py` | 616 | Testes unitários cobrindo 6 features + 7 cross-feature |
| `test_gherkin_expert_deliverables.py` | 356 | Validação TDD dos 5 deliverables do Gherkin Expert (SKILL.md, agente, prompt-writer, PATTERNS.md, workflow) |

## Padrões de Design

- **DAG com resolução topológica**: passos são ordenados dinamicamente, sem necessidade de declarar ordem sequencial
- **Exponential backoff puro**: sem jitter, para previsibilidade nos testes
- **Timeout via ThreadPoolExecutor**: permite cancelamento cooperativo via `threading.Event`
- **Contexto imutável entre tentativas**: cada retry parte do contexto original, só o output final persiste
- **Comandos simulados**: `echo`, `exit N`, `sleep N`, `fail_then_succeed(N)`, `increment_counter()` para teste determinístico

## Relação com BDD/Gherkin

Este executor foi o **alvo do experimento Gherkin v2** (`experiments/hive_mind/gherkin_v2_recipe_executor/`). As especificações Gherkin para estas 6 features produziram código com score médio de 0.898 (vs 0.713 English-only), validando empiricamente que especificações formais melhoram a qualidade do código gerado para requisitos comportamentais.

## Fontes

Os arquivos originais estavam em `wiki/_raw/qa/code/` e foram promovidos para esta página de referência durante o ingest raw mode de 2026-06-15.

## Ver Também

- [[references/tdd-methodology|TDD Methodology]] — O executor foi construído com TDD
- [[references/bdd-specification-process|BDD Spec Process]] — Especificações Gherkin guiaram os testes
- [[references/qa-overview|QA Overview]] — Onde o executor se encaixa no pipeline SDD
