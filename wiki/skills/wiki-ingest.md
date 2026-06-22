---
title: "wiki-ingest"
category: skills
tags: [wiki, skill, ingest, destilacao]
sources: [.hermes/skills/wiki/ingest/SKILL.md]
summary: "Destila raw sources (specs, docs, logs) em páginas wiki interligadas. É o entry point do pipeline wiki — transforma artefatos do framework em conhecimento navegável."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.4891
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-20"
---

# wiki-ingest

> Destila raw sources em páginas wiki. Entry point do pipeline de knowledge management.

## Localização
`.hermes/skills/wiki/ingest/SKILL.md`

## Quando usar
- Após feature implementada (destilar spec/plan/tasks em página wiki)
- Após nova decisão arquitetural (atualizar concepts/)
- Após importar documentos externos

## O que faz
1. Lê a source (spec.md, plan.md, conversa, URL)
2. Extrai conceitos, decisões, relações
3. Cria/atualiza página wiki com frontmatter completo
4. Adiciona `[[skills/obsidian-markdown|wikilinks]]` para páginas relacionadas
5. Registra no `.manifest.json`
6. Atualiza `index.md` e `log.md`
7. **Auto-Summarize de `_raw/`:** Detecta documentos em `wiki/_raw/`, gera um chunk `Summary` automático (propósito, contribuições, métricas) e o indexa no banco de memória experiencial junto com os demais chunks

## Exemplo
```
Source: specs/features/006-agent-dev/spec.md
Output: wiki/projects/42_chat/features/feature-006-agent-dev.md
```

## Auto-Summarize de `_raw/`

> Durante a ingestão de documentos em `wiki/_raw/`, o `wiki-ingest` gera automaticamente um chunk de sumário indexável via `summarizer.py` (Feature 002).

### Fluxo

1. **Detecção:** Durante o passo de indexação (`hermes wiki index --full`), o pipeline varre `wiki/_raw/` junto com o restante da wiki. Arquivos `.md` com frontmatter YAML — tipicamente papers acadêmicos e artigos longos — são candidatos à sumarização automática.

2. **Extração:** O módulo `[[references/toolkits/wiki/experiential-memory|experiential-memory/summarizer.py]]` processa cada documento:
   - **Frontmatter YAML:** Extrai `title` e `description` do bloco `--- ... ---`.
   - **Abstract:** Localiza a seção *Abstract* (ou *Resumo*, *TL;DR*) e extrai até 40 linhas.
   - **Contribuições:** Localiza a seção *Contributions* (ou lista numerada pós-abstract) e extrai itens formatados com `•`.
   - **Métricas:** Detecta valores numéricos em contexto de melhoria/redução (ex: `-34.7%`, `2.3x faster`, `accuracy 89.5%`) via regex em padrões EN/PT.

3. **Geração do chunk Summary:** O `summarizer.py` monta um sumário Markdown estruturado com três seções:
   - `### Propósito` — description do frontmatter ou primeira frase do abstract.
   - `### Principais Contribuições / Achados` — itens extraídos das contribuições, ou o abstract truncado como fallback.
   - `### Métricas-Chave` — lista das métricas numéricas detectadas.
   
   O chunk usa `heading_path = 'Summary'`, `source` = caminho do arquivo `_raw/`, e `tags = ['summary', 'auto-generated']`. O conteúdo é truncado em 2000 caracteres.

4. **Indexação:** O chunk `Summary` é inserido no índice SQLite da memória experiencial (`wiki_index.db`) **junto com os demais chunks** do documento. Ele recebe embedding via `all-MiniLM-L6-v2` e fica disponível para busca semântica (`wiki-query --semantic`) — permitindo que o resumo de um paper seja recuperado contextualmente durante brainstorming e geração de tasks.

### Exemplo de saída

```markdown
## LATTE: Adaptive Task Graphs

### Propósito
LATTE: coordination graph dinâmico para times de LLM. Implementado como Feature 001.

### Principais Contribuições / Achados
  • A shared coordination graph encodes sub-task dependencies and agent assignment.
  • Agents dynamically allocate work, adapt coordination, and discover new tasks.
  • LATTE reduces token usage, wall-clock time, and coordination failures.

### Métricas-Chave
  • 2.3x faster
  • 34.7% runtime
  • 42.8% cost
```

### Estrutura do chunk retornado

```python
{
    'content': str,          # Sumário Markdown com 3 seções
    'heading_path': 'Summary',
    'source': str,           # Caminho relativo (ex: '_raw/LATTE_Paper.md')
    'content_hash': str,     # SHA256 do conteúdo
    'char_count': int,       # ≤ 2000
    'tags': ['summary', 'auto-generated'],
}
```

### Fallbacks

- **Sem frontmatter:** Usa o nome do arquivo como título.
- **Sem abstract:** Usa a `description` do frontmatter como propósito; contribuições ficam vazias.
- **Sem contribuições:** Usa o abstract truncado como fallback na seção de achados.
- **Sem métricas:** Exibe `(Nenhuma métrica numérica detectada automaticamente.)`.
- **Arquivo inválido/inexistente:** Retorna chunk vazio (`content=''`).

## Relacionado
- [[skills/wiki-lint|wiki-lint]] — Audita o que foi ingerido
- [[skills/wiki-query|wiki-query]] — Busca o que foi ingerido (inclui modo `--semantic` que recupera chunks do índice experiencial)
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica (arquitetura 3 camadas, schema, pitfalls)
- [[references/toolkits/wiki/experiential-memory|experiential-memory]] — Módulo da Feature 002: `summarizer.py`, `chunker.py`, `store.py` e pipeline de indexação semântica
- [[obsidian-flow|Fluxo Obsidian]] — Onde se encaixa
