---
name: sdd-validate
description: >
  Use when the user asks to validate or audit the SDD structure of a repository. Checks for
  required directories (.github/memory/, specs/), required files (constitution.md, tech.md,
  spec.md, plan.md, tasks.md per feature), and reports missing or malformed artifacts. Trigger
  keywords: validar SDD, validate sdd, auditar estrutura, check sdd, verificar conformidade,
  audit structure.
version: 1.2.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Validate, Audit, Quality]
    related_skills: [wiki-query, sdd-init_repo, sdd-refactor_artifact, sdd-brainstorm]
    category: sdd
    resources:
      - SKILL.md
      - scripts/check-sdd.sh
---

# Validar Estrutura SDD

## Propósito

Audita o repositório para verificar conformidade com SDD. Detecta diretórios
ausentes, artefatos faltantes e inconsistências. **Somente leitura — nunca corrija.**

## Critérios de validação

### Nível 1: Memória de Contexto Global

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Diretório memory | `.github/memory/` | Sim |
| Constituição | `.github/memory/constitution.md` | Sim |
| Stack tecnológica | `.github/memory/tech.md` | Sim |

### Nível 2: Diretório de Especificações

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Raiz specs | `specs/` | Sim |
| Domain events | `specs/domain-events/` | Sim |
| Features | `specs/features/` | Sim |
| Infra | `specs/infra/` | Sim |

### Nível 3: Features (por feature numerada)

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Especificação | `specs/features/<id>-<nome>/spec.md` | Sim |
| Plano | `specs/features/<id>-<nome>/plan.md` | Sim |
| Tarefas | `specs/features/<id>-<nome>/tasks.md` | Sim |

## Fluxo de Execução

### Passo 1: Validar Memória de Contexto

Verifique `.github/memory/`, `constitution.md`, `tech.md`.
Reporte: PASS (existe e não vazio), FAIL (ausente), WARN (existe mas vazio).

### Passo 2: Validar specs/

Verifique `specs/` e subdiretórios. `features/` vazio = WARN (sem features ainda).

### Passo 3: Validar cada feature

Para cada `specs/features/<id>-<nome>/`:
- Nome segue `<id numérico>-<nome>`?
- `spec.md`, `plan.md`, `tasks.md`: existe? não vazio? conteúdo canônico?

### Passo 4: Validar AGENTS.md

Existe? Contém referência ao workflow SDD?

### Passo 5: Sumário

Apresente relatório no formato:

```
SDD Validation Report
=====================
.github/memory/            PASS
  constitution.md          PASS
  tech.md                  WARN (vazio — execute sdd-explore_tech)
...
Resultado: 8/9 checks passaram
Ação sugerida: ...
```

### Automação (opcional)

```bash
skill_view(name="sdd-validate", file_path="scripts/check-sdd.sh")
```

## Qualidade de Conteúdo

Além da validação estrutural, consulte `references/content-quality.md` para:
- Freshness scoring (tiers: fresh/aging/stale/dead)
- Métricas de cobertura com thresholds green/yellow/red
- Check de qualidade por artefato SDD (spec.md, plan.md, tasks.md)
- Scripts de automação para qualidade de conteúdo

## Coordenação (LATTE)

Se o repositório utiliza LATTE Coordination (Feature 001), valide também as
métricas de qualidade da coordenação consultando o módulo
`.hermes/skills/sdd/latte_coordination/metrics.py`.

### Passo 6: Extrair métricas de coordenação

Localize o coordination graph G_final:

1. **Novas execuções:** Se o orchestrator LATTE acabou de rodar, capture
   `G_final` diretamente do retorno de `Orchestrator.run()` (ou do objeto
   `CoordinationGraph` em memória).

2. **Execuções passadas:** Carregue o arquivo
   `wiki/projects/<feature_id>/coordination-graph.md` (gerado por
   `graph_persistence.save_graph_to_wiki()`) — parseie a seção de dados
   brutos ou carregue o JSON correspondente se disponível.

Com G_final em mãos, compute as métricas:

```python
from latte_coordination.metrics import compute_coordination_metrics

metrics = compute_coordination_metrics(G_final)
```

### Métricas exibidas no relatório

| Métrica | Campo | Descrição |
|---------|-------|-----------|
| **Overwrite Rate** | `overwrite.overwrite_rate` | Proporção de nós trabalhados por >1 Worker (sobrescrita) |
| **Wasted Chars** | `waste.wasted_chars` | Caracteres produzidos e descartados (output não final) |
| **Waste Ratio** | `waste.waste_ratio` | Razão entre caracteres desperdiçados e total |
| **Idle Rounds** | `idle.idle_ratio` | Proporção de rounds sem ação de Worker |
| **Straggler P95** | `straggler.p95_total` | Percentil 95 do tempo de completion (em rounds) |
| **Inter-Agent Messages** | `messages.total_messages` | Total de mensagens Lead↔Workers |
| **Tokens Consumed** | `tokens.estimated_tokens` | Estimativa de tokens totais consumidos |
| **Wall Clock Time** | `timing.wall_clock_seconds` | Tempo de parede em segundos |
| **Completion Rate** | `summary.completion_rate` | Taxa de tasks concluídas (done/verified) |
| **Graph Health** | `summary.graph_is_healthy` | Todas as tasks estão terminais? |

### Formato do relatório de coordenação

Inclua no relatório final uma subseção:

```
Coordenação (LATTE)
===================
Overwrite Rate:      0.00  (0/3 nós com >1 Worker)
Wasted Chars:        0     (waste ratio: 0.00)
Idle Rounds:         0/3   (0.0%)
Straggler P95:       3.00 rounds
Inter-Agent Messages: 12  (Lead: 6, Workers: 6)
Tokens Estimados:    24,000
Wall Clock:           1.23s
Completion Rate:      100% (3/3) — gráfo saudável
```

### Thresholds e alertas

- **Overwrite Rate > 0.2:** WARN — muitas tasks sendo reatribuídas (possível
  straggler crônico ou DAG mal particionado).
- **Waste Ratio > 0.3:** WARN — mais de 30% dos caracteres produzidos foram
  descartados (retrabalho excessivo).
- **Idle Ratio > 0.5:** WARN — Workers ociosos na maior parte dos rounds
  (DAG muito sequencial ou frontier pequeno).
- **Straggler P95 > 10 rounds:** WARN — tasks levando >10 rounds para
  completar (possível complexidade excessiva ou Worker lento).
- **Completion Rate < 1.0:** FAIL se alguma task não chegou a done/verified
  (grafo não atingiu estado terminal).

### Automação (opcional)

```bash
python .hermes/skills/sdd/latte_coordination/metrics.py <graph.json>
```

> **Nota:** Esta seção é executada apenas se houver um coordination graph
> disponível. Em projetos sem LATTE, pule este passo.

### Passo 7: Feedback Loop — Métricas → Utility Signal → Score Update

Após computar as métricas de coordenação, converta-as em um **utility signal**
que alimenta o scoring da memória experiencial (Feature 002). Isso fecha o ciclo:
a qualidade da execução LATTE informa quais hints da wiki são bons ou ruins.

#### 7.1 Cálculo do Utility Signal

Converta as três métricas principais em um sinal de utilidade normalizado no
intervalo [0, 1]:

```
u = 1.0 - (overwrite_rate × 0.4 + waste_ratio × 0.3 + idle_ratio × 0.3)
```

Onde:
- `overwrite_rate` = `metrics["overwrite"]["overwrite_rate"]`
- `waste_ratio`   = `metrics["waste"]["waste_ratio"]`
- `idle_ratio`    = `metrics["idle"]["idle_ratio"]`

Os pesos refletem o impacto relativo na qualidade:
- **Overwrite (0.4):** peso mais alto — sobrescrita indica retrabalho que
  compromete a qualidade do output.
- **Waste (0.3):** caracteres descartados indicam esforço mal direcionado.
- **Idle (0.3):** Workers ociosos indicam DAG mal particionado ou frontier pequeno.

#### 7.2 Mapeamento Qualitativo

| Utility Signal | Classificação | Delta por chunk |
||---|---|
| **u > 0.7** | Boa execução — hints contribuíram positivamente | **+0.04** |
| **0.4 ≤ u ≤ 0.7** | Execução neutra — hints não fizeram diferença significativa | **0.00** (neutro) |
| **u < 0.4** | Execução ruim — hints podem ter induzido a erro ou foram irrelevantes | **−0.04** |

#### 7.3 Atualização dos Scores

Para cada chunk da wiki que foi usado como **hint** durante a feature:

```python
from wiki.experiential_memory.scoring import update_score

# O delta é proporcional ao desvio da neutralidade, com ajuste fino
delta = (u - 0.5) * 0.2

for chunk_hash in chunk_hashes_usados_como_hint:
    update_score(chunk_hash, delta)
```

O fator `0.2` mantém os ajustes pequenos e graduais (máximo ±0.10 por feature),
evitando oscilações bruscas. Scores convergem ao longo de múltiplas features
(conforme critério de sucesso: top-5 hints estáveis após 5 features).

#### 7.4 Formato do Relatório de Feedback

Inclua no relatório final uma subseção:

```
Feedback Loop (Memória Experiencial)
====================================
Utility Signal:       0.72  (boa execução)
  Overwrite Rate:     0.00  (peso 0.4 → 0.000)
  Waste Ratio:        0.15  (peso 0.3 → 0.045)
  Idle Ratio:         0.10  (peso 0.3 → 0.030)
  Fórmula: u = 1.0 - (0.000 + 0.045 + 0.030) = 0.925

Chunks usados como hints: 5
  chunk_a1b2c3... → score 0.54 (+0.08)
  chunk_d4e5f6... → score 0.46 (+0.08)
  chunk_g7h8i9... → score 0.62 (+0.08)
  ...

Ação: 5 chunks atualizados. Próxima feature usará scores ajustados.
```

#### 7.5 Automação

```python
from wiki.experiential_memory.feedback import compute_utility_signal, apply_feedback

u = compute_utility_signal(metrics)
apply_feedback(u, chunk_hashes)
```

> **Nota:** Este passo requer que o índice da memória experiencial esteja
> populado (Feature 002, M2.1 concluído) e que os chunks usados como hints
> tenham sido registrados. Em features sem hints (cold start), pule.

## Guardrails

- **Read-only:** apenas reporte, nunca crie ou modifique arquivos.
- **Features sem numeração:** WARN para diretórios fora do padrão `<id>-<nome>`.
- **Arquivos vazios:** diferencie FAIL (ausente) de WARN (vazio/em progresso).
- **Projetos novos:** repo recém-inicializado sem features = WARNs aceitáveis.

## Verificação

- [ ] Relatório segue formato PASS/FAIL/WARN com resumo e ações sugeridas
- [ ] Cada FAIL tem ação sugerida
- [ ] Nenhum arquivo foi criado/modificado (read-only)
- [ ] Feedback loop: utility signal computado e scores atualizados (se houver LATTE + índice)
