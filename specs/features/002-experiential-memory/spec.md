---
feature_id: "002"
title: "Wiki Experiential Memory — Memória Experiencial com Indexação Semântica"
status: draft
created: "2026-06-19"
author: phm-aguiar
tags: [sdd, wiki, memoria, embeddings, retrieval, hints, feedback-loop]
based_on:
  - "A-MapReduce: Executing Wide Search via Agentic MapReduce (Chen et al., 2026)"
  - "LATTE: Language Agent Teams for Task Evolution (Mieczkowski et al., 2026)"
depends_on: "001-latte-coordination"
---

**Aprovado:** true

# Wiki Experiential Memory — Memória Experiencial com Indexação Semântica

> Transforma a wiki Obsidian de documentação estática em **memória experiencial viva**:
> indexação semântica de chunks, retrieval contextual, hint scoring automático com
> feedback loop, e distillation periódica. Inspirado no Experiential Memory do
> A-MapReduce e alimentado pelas métricas de coordenação do LATTE.

## Propósito

O pipeline SDD atual consulta a wiki de forma textual e carrega documentos inteiros.
Isso é ineficiente: um paper de 100K tokens é lido por inteiro quando só 3 parágrafos
são relevantes. O `wiki-query` usa busca textual (grep-like), sem noção de similaridade
semântica. Padrões de decomposição bem-sucedidos em features anteriores não são
automaticamente recuperados e reutilizados — dependem da memória do agente ou de
consultas manuais.

O A-MapReduce demonstrou que uma **memória experiencial** com indexação por embeddings,
retrieval contextual, hint scoring com feedback, e distillation periódica:
- Reduz runtime em 34.7% (vs variante sem evolução)
- Reduz custo em 42.8% ($1.05 → $0.60)
- Sobe Item F1 em 5.15pp (vs sem memória)

**Esta feature aplica esse padrão à wiki do SDD**, criando uma camada de inteligência
que indexa semanticamente, recupera chunks relevantes, pontua conhecimento com base
em resultados reais de execução, e mantém a memória saudável via distillation.

## Escopo

### Dentro do escopo

| Milestone | Descrição |
|---|---|
| **M2.1: Indexação Semântica** | Script que percorre `wiki/`, quebra docs em chunks por seção (`##`), gera embeddings via `all-MiniLM-L6-v2`, armazena em índice local (SQLite + vetor float blob) |
| **M2.2: Retrieval Contextual** | API de query: dado texto (spec, tarefa), retorna top-k chunks por similaridade cosseno. Integração com `wiki-query` (modo semântico), `sdd-generate-tasks` (hints no G₀), `sdd-brainstorm` (contexto de features similares) |
| **M2.3: Hint Scoring + Feedback** | Cada chunk/index entry ganha score (inicial neutro). Métricas do `sdd-validate` pós-LATTE (overwrite rate, wasted chars, idle rounds) atualizam scores. Hints de features bem-sucedidas ganham peso; hints de features problemáticas perdem. Scores persistem entre sessões |
| **M2.4: Distillation** | Comando periódico (`wiki-distill`) que agrupa chunks similares, remove duplicatas, sintetiza padrão canônico por cluster. Similar ao `F_ψ` do A-MapReduce. Reduz entropia do hint pool sem perder conhecimento |
| **Sumarização de _raw/** | Papers e documentos longos em `wiki/_raw/` são automaticamente chunked e indexados. Primeira ingestão gera sumário estruturado (propósito, achados, métricas) como chunk adicional |
| **Integração com brain toolkit** | `wiki-query` ganha modo `--semantic`. `wiki-synthesize` e `wiki-dedup` são estendidos para operar sobre chunks + embeddings. `wiki-ingest` atualiza índice automaticamente |

### Fora do escopo

- Substituir Obsidian como vault — o índice é derivado, a wiki continua source of truth
- Modificar conteúdo da wiki automaticamente (scores e metadados sim, texto original não)
- Fine-tuning de modelos de embedding nos dados da wiki (v2)
- Busca híbrida (lexical + semântica) — v1 é só semântica
- Memória de conversas/sessões — foco em documentos da wiki
- Integração com APIs externas de embedding (OpenAI, Cohere) — só local

## Constraints

1. **Hermes nativo:** Tudo roda localmente. Embeddings via `all-MiniLM-L6-v2` (23MB, sem GPU, sem API key). Índice em SQLite.
2. **Wiki como source of truth:** O índice é sempre derivado da wiki. Re-indexação completa é possível a qualquer momento (idempotente).
3. **Modelo de embedding fixo:** `all-MiniLM-L6-v2` (384 dimensões). Trocar modelo = re-indexação completa (aceitável, index < 30s).
4. **Chunking por seção:** Docs são quebrados em headings `##`. Chunks têm metadados (source doc, heading path, tags).
5. **Scores persistem:** Hint scores sobrevivem a re-indexações (são stored por chunk hash, não por posição).
6. **Distillation não destrutiva:** Nunca deleta conteúdo original da wiki. Apenas ajusta scores e gera chunks sintetizados como novas entradas no índice.
7. **Depende da feature 001:** M2.3 (feedback loop) requer métricas do `sdd-validate` pós-LATTE implementado.

## Critérios de Sucesso

| Métrica | Baseline | Alvo | Método |
|---|---|---|---|
| **Retrieval quality** | N/A (não existe hoje) | ≥ 80% top-3 chunks julgados relevantes | LLM-judge em 20 consultas |
| **Index coverage** | 0% (sem índice) | 100% docs em `wiki/` indexados | `find wiki/ -name '*.md' | wc -l` vs `SELECT COUNT(DISTINCT source) FROM chunks` |
| **Token reduction** | Baseline: generate-tasks sem hints | -30% tokens na geração de G₀ | Contar tokens antes/depois em 5 features |
| **Score convergence** | Scores aleatórios (inicial) | Top-5 hints estáveis após 5 features (desvio padrão < 0.1) | Track scores ao longo de features consecutivas |
| **Distillation efficacy** | Pré-distillation | -30% chunks no índice pós-distillation (remove redundância) | `SELECT COUNT(*) FROM chunks` antes/depois |
| **Index speed** | N/A | Index completo < 30s | `time hermes wiki index --full` |
| **Query speed** | N/A | Retrieval top-5 < 1s | `time hermes wiki query --semantic "..."` |

## Funcionalidade

### Cenário 1: Primeira indexação da wiki

**Dado** que a wiki tem 80+ documentos em `wiki/`
**Quando** `hermes wiki index --full` é executado
**Então**:
1. Cada .md é lido e chunked por headings `##`
2. Embeddings são gerados para cada chunk (all-MiniLM-L6-v2, 384d)
3. Chunks + embeddings + metadados são armazenados em `~/.hermes/wiki_index.db`
4. Scores são inicializados como neutros (0.5)
5. Relatório: "Indexados 312 chunks de 84 documentos em 18.3s"

### Cenário 2: Retrieval contextual para sdd-generate-tasks

**Dado** que `spec.md` da feature 005 está aprovado e a wiki está indexada
**Quando** `sdd-generate-tasks` inicia a geração de G₀
**Então**:
1. Spec é embeddado e comparado com índice (cosseno)
2. Top-5 chunks similares são recuperados: "features de auth precisam de migration", "QA em handler HTTP usa .feature", ...
3. Chunks são injetados como `experiential_prior` no prompt do generate-tasks
4. G₀ gerado inclui tasks que o Lead teria que Discover (adiantando trabalho)
5. Tokens gastos: -30% vs baseline (menos Discover necessário)

### Cenário 3: Feedback loop após execução LATTE

**Dado** que feature 005 foi executada com LATTE e `sdd-validate` gerou métricas
**Quando** `sdd-validate` termina com relatório de coordenação
**Então**:
1. Métricas (overwrite=2, wasted=1200, idle=52%) são convertidas em utility signal
2. Chunks usados como hints na feature 005 recebem score update
3. Hints que levaram a boa execução (poucos overwrites) ganham +0.1
4. Hints de features problemáticas perdem -0.05
5. Scores persistem no índice para a próxima feature

### Cenário 4: Distillation periódica

**Dado** que 15 features foram executadas e o hint pool tem 200+ chunks
**Quando** `wiki-distill` é executado
**Então**:
1. Chunks são clusterizados por similaridade de embedding (FINCH ou KMeans)
2. Para cada cluster, chunks redundantes são identificados (cosseno > 0.95)
3. Um chunk canônico é gerado (síntese via LLM dos chunks do cluster)
4. Scores são agregados (média ponderada)
5. Chunks redundantes têm score zerado (não deletados — preservação)
6. Relatório: "Destilados 200 → 138 chunks (-31%). 8 padrões canônicos gerados."

### Cenário 5: Sumarização de paper ingerido

**Dado** que `wiki/_raw/ImprovingTheEfficiency...AdaptiveTaskGraphs.md` (100K tokens) foi ingerido
**Quando** `wiki-ingest` processa o arquivo
**Então**:
1. Documento é chunked por headings (≈ 15 chunks)
2. Embeddings gerados e indexados
3. Um chunk adicional "Summary" é gerado automaticamente: propósito, contribuições, métricas principais
4. Chunks são indexados com source=`_raw/LATTE_paper.md` e tags=`[paper, multi-agent, coordination]`

## Edge Cases

1. **Wiki vazia:** Índice vazio, retrieval retorna lista vazia. G₀ gerado sem hints (fallback gracioso).
2. **Documento muito grande (> 1M tokens):** Chunking em seções, limite de 4096 tokens por chunk. Excedente truncado com warning.
3. **Re-indexação:** Scores preservados por chunk hash (SHA256 do conteúdo). Chunks removidos da wiki têm scores arquivados (não perdidos).
4. **Modelo de embedding não instalado:** `pip install sentence-transformers` automático no primeiro uso. Se falhar, indexing aborta com mensagem clara.
5. **Colisão de hash:** Dois chunks idênticos em docs diferentes — tratados como entradas separadas (metadados diferentes), mas scores são shared.
6. **Cold start (poucas features):** Scores neutros (0.5) significam que todos os chunks têm peso igual. Sistema funciona como retrieval sem feedback até acumular 3+ features.
7. **Distillation sem massa crítica:** Se < 30 chunks, distillation é no-op com warning "insufficient data for distillation".
8. **Chunk muito curto (< 50 chars):** Ignorado na indexação (títulos soltos, linhas em branco).
9. **Encoding quebrado:** Documento com caracteres inválidos → chunk ignorado, warning logado, indexação continua.

## Relacionado

- Paper A-MapReduce: `wiki/_raw/A-MapReduce_ExecutingWideSearchviaAgenticMapReduce.md`
- Paper LATTE: `wiki/_raw/ImprovingtheEfficiencyofLanguageAgentTeamswithAdaptiveTaskGraphs.md`
- Feature 001: `specs/features/001-latte-coordination/` (dependência para feedback loop)
- [[concepts/sdd|SDD]] — Metodologia
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Integração wiki ↔ pipeline
- [[skills/brain|brain toolkit]] — wiki-query, wiki-ingest, wiki-synthesize, wiki-dedup
