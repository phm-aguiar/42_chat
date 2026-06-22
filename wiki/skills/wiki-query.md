---
title: "wiki-query"
category: skills
tags: [wiki, skill, busca, query, retrieval]
sources: [.hermes/skills/wiki/query/SKILL.md]
summary: "Busca híbrida (lexical + vetorial + semântica) no vault Obsidian. Modo index-only (barato, lê só frontmatter), full-read (profundo, lê corpos) ou --semantic (embedding + similaridade de cosseno). Usado pelo agente principal para recuperar conhecimento compilado."
lifecycle: draft
tier: core
created: "2026-06-13"
rag_score: 0.4892
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-20"
---

# wiki-query

> Busca conhecimento compilado no vault. "O que já decidimos sobre X?"

## Localização
`.hermes/skills/wiki/query/SKILL.md`

## Quando usar
- Antes de brainstorm (features similares já existem?)
- Durante implementação (decisões arquiteturais passadas?)
- Debugging (edge case já documentado?)

## Modos
| Modo | Custo | Quando |
|---|---|---|
| **Index-only** | Baixo | Lê só `summary:` do frontmatter — suficiente pra 80% das perguntas |
| **Full-read** | Alto | Lê corpos das páginas — para perguntas complexas |
| **--semantic** | Médio | Embedding + similaridade de cosseno no índice SQLite — para buscas conceituais ("como fazer X", "padrão de Y") |

## Como funciona
1. Busca lexical (grep) nos frontmatters
2. Busca vetorial (embeddings) se configurado
3. Busca semântica (`--semantic`) se explícito: embedda query com `all-MiniLM-L6-v2`, compara similaridade de cosseno no índice SQLite
4. Combina resultados com ranking
5. Sintetiza resposta ou retorna páginas relevantes

## Modo Semântico (--semantic)

Ativado com a flag explícita `--semantic`. Sem a flag, o comportamento padrão (modo textual) é mantido.

### Uso
```bash
hermes wiki query --semantic "texto da consulta" --top-k N
```

- `--semantic`: texto da consulta em linguagem natural (obrigatório no modo semântico)
- `--top-k N`: número máximo de resultados (padrão: 5)

### O que faz
1. **Embedda a query** com o modelo `all-MiniLM-L6-v2` (SentenceTransformer)
2. **Busca por similaridade de cosseno** no índice SQLite (`~/.hermes/wiki_index.db`), comparando o embedding da query com embeddings de todos os chunks indexados
3. **Retorna os top-k chunks** mais similares, ordenados por similaridade decrescente, exibindo `source`, `heading`, conteúdo truncado e `score` combinado

### Fallback: índice não existe
Se o banco de índice (`~/.hermes/wiki_index.db`) não existir ou estiver vazio (sem embeddings), o comando exibe:

> Índice não encontrado. Execute 'hermes wiki index --full' primeiro.

…e termina com código de saída 1. O agente deve então **sugerir ao usuário** que execute `hermes wiki index --full` para construir o índice antes de usar o modo semântico.

### Quando usar cada modo
| Modo | Ativar com | Ideal para |
|---|---|---|
| **Textual** (padrão) | *(sem flag)* | Buscas exatas: "nome exato de arquivo", "erro X", "classe Y", "função Z" |
| **Semântico** | `--semantic` | Buscas conceituais: "como fazer X", "padrão de Y", "estratégia para Z", "qual a abordagem para W" |

**Regra prática:** se a consulta contém verbos de ação ("como fazer", "implementar", "resolver") ou conceitos abstratos ("design pattern", "arquitetura", "estratégia"), prefira `--semantic`. Se a consulta contém nomes exatos de arquivos, classes, funções ou mensagens de erro, use o modo textual padrão.

### Exemplos
```bash
# Busca conceitual — semântica
hermes wiki query --semantic "como implementar caching distribuído" --top-k 5

# Busca conceitual — semântica com mais resultados
hermes wiki query --semantic "padrões de design para CLI tools" --top-k 10

# Fallback: índice não construído
hermes wiki query --semantic "estratégia de error handling"
# → Índice não encontrado. Execute 'hermes wiki index --full' primeiro.
```

## Exemplo (modo textual, sem --semantic)
```
Query: "Como o agent-dev lida com spec ambígua?"
→ wiki-query index-only
→ Encontra: feature-006-agent-dev.md (summary: "nunca infere, reporta BLOCKED")
→ Retorna: página + trecho relevante
```

## Relacionado
- [[skills/wiki-ingest|wiki-ingest]] — Alimenta o que a query busca
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica (query operation, compile-dont-retrieve)
- [[concepts/wiki-model|Wiki Model]] — Compile, don't retrieve
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Quando usar
- [[references/toolkits/wiki/experiential-memory|experiential-memory]] — Módulo de implementação (`cli_query.py`, `search.py`, `chunker.py`, `store.py`, `scoring.py`) — Feature 002
- [[projects/42_Framework/features/002-experiential-memory|Feature 002: Wiki Experiential Memory]] — Spec completa da memória experiencial
