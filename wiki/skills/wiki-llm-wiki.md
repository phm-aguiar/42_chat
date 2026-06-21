---
title: "llm-wiki — Fundação Teórica do Knowledge Management"
category: skills
tags: [wiki, skill, arquitetura, fundamentos, knowledge-management]
sources: [.hermes/skills/research/llm-wiki/SKILL.md]
summary: "Fundação teórica do modelo wiki: arquitetura de 3 camadas (raw → wiki → schema), padrão compile-dont-retrieve, frontmatter canônico, tag taxonomy, provenance, confidence, e operações core (ingest, query, lint)."
lifecycle: reviewed
base_confidence: 0.9
tier: core
created: "2026-06-13"
updated: "2026-06-16"
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
---

# llm-wiki — Fundação Teórica

> Baseado no [padrão LLM Wiki de Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
> "Compile, don't retrieve" — conhecimento é destilado uma vez e mantido atual,
> em vez de redescoberto a cada query.

**Localização:** `.hermes/skills/research/llm-wiki/SKILL.md`

## Arquitetura de 3 Camadas

```
Layer 1: Raw Sources (imutável)
  ↓  wiki-ingest
Layer 2: Wiki Compilado (interligado)
  ↓  governado por
Layer 3: Schema (SCHEMA.md + skills wiki)
```

### Layer 1 — Raw Sources
Fontes brutas: artigos, PDFs, transcrições, chat exports. **Nunca modificadas** pelo agente.
Contêm frontmatter próprio (`source_url`, `ingested`, `sha256`) para detecção de drift.

### Layer 2 — Wiki Compilado
Páginas markdown interligadas com `[[wikilinks]]`. Cada página tem frontmatter YAML completo,
provenance rastreável, e sinais de qualidade (`confidence`, `contested`).

### Layer 3 — Schema
`SCHEMA.md` define as regras: taxonomia de tags, convenções de nomenclatura, thresholds de
criação/arquivamento. As skills wiki (`ingest`, `lint`, `query`) implementam o schema.

## Frontmatter Canônico

Toda página wiki exige:

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy]
sources: [raw/source-name.md]
# Sinais de qualidade (opcionais mas recomendados):
confidence: high | medium | low
contested: true
contradictions: [other-page-slug]
---
```

Raw sources também têm frontmatter com `source_url`, `ingested`, `sha256` (do corpo, não do frontmatter).

## Operações Core

### Ingest
Fluxo: capturar raw source → discutir takeaways → checar duplicatas → escrever/atualizar páginas → atualizar index + log.
Uma fonte pode disparar 5–15 atualizações de páginas. Sempre orientar-se primeiro (SCHEMA + index + log).

### Query
Fluxo: ler index → search_files (wikis 100+ páginas) → ler páginas relevantes → sintetizar resposta → arquivar se valioso.
Respostas citam as páginas: `"Based on [[page-a]] and [[page-b]]..."`

### Lint
13 verificações: broken wikilinks, orphans, frontmatter, stale content, contradictions, index consistency,
source drift, page size, tag audit, log rotation, qualidade, arquivamento, cobertura.

## Taxonomia de Tags

Tags são definidas em SCHEMA.md. Regra: **novas tags só entram na taxonomia antes de serem usadas.**
Isso previne tag sprawl. Exemplo para domínio AI/ML:

| Categoria | Tags |
|---|---|
| Models | model, architecture, benchmark, training |
| People/Orgs | person, company, lab, open-source |
| Techniques | optimization, fine-tuning, inference, alignment |
| Meta | comparison, timeline, controversy, prediction |

## Page Thresholds

| Ação | Critério |
|---|---|
| Criar página | Entidade/conceito aparece em 2+ fontes OU é central a uma fonte |
| Atualizar existente | Fonte menciona algo já coberto |
| NÃO criar | Menção passageira, detalhe menor, fora do domínio |
| Split | Página >200 linhas → quebrar em sub-tópicos |
| Arquivar | Conteúdo totalmente superado → `_archive/` |

## Sinais de Qualidade

- **confidence: high/medium/low** — quão bem-suportadas são as claims. `low` para single-source ou opinião.
- **contested: true** — página tem contradições não-resolvidas. Aparece no lint.
- **contradictions: [slug]** — lista de páginas conflitantes.
- **Provenance:** `^[raw/articles/source.md]` ao final de parágrafos cujas claims vêm de fonte específica.
  Obrigatório em páginas que sintetizam 3+ fontes.

## Update Policy (Conflitos)

Quando nova informação contradiz conteúdo existente:
1. Verificar datas — fontes mais novas geralmente superam antigas
2. Se genuinamente contraditório, anotar ambas as posições com datas e fontes
3. Marcar `contradictions: [page-name]` no frontmatter
4. Sinalizar para revisão humana no lint

## Integração Obsidian

O diretório wiki funciona como vault Obsidian nativo:
- `[[wikilinks]]` renderizam como links clicáveis
- Graph View visualiza a rede de conhecimento
- YAML frontmatter alimenta queries Dataview
- `raw/assets/` para imagens referenciadas via `![[imagem.png]]`

Para máquinas headless, usar `obsidian-headless` com Obsidian Sync.

## Pitfalls do Modelo

- **Nunca modificar raw/** — fontes são imutáveis. Correções vão nas páginas wiki.
- **Sempre orientar primeiro** — SCHEMA + index + log antes de qualquer operação.
- **Nunca pular index.md e log.md** — são a espinha dorsal da navegação.
- **Não criar páginas para menções passageiras** — seguir os thresholds.
- **Nenhuma página sem cross-references** — mínimo 2 wikilinks outbound.
- **Frontmatter é obrigatório** — sem ele, search e staleness detection quebram.
- **Tags só da taxonomia** — tag livre vira ruído.
- **Páginas escaneáveis em 30s** — split se >200 linhas.
- **Perguntar antes de mass-update** — 10+ páginas afetadas = confirmação.
- **Rotacionar log** — >500 entradas → `log-YYYY.md`.

## Relacionado

- [[concepts/wiki-model|Wiki Model]] — Como o framework aplica este modelo
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Pipeline operacional do vault
- [[skills/wiki-ingest|wiki-ingest]] — Implementa a operação de ingest
- [[skills/wiki-lint|wiki-lint]] — Implementa a operação de lint
- [[skills/wiki-query|wiki-query]] — Implementa a operação de query
- [[skills/wiki-capture|wiki-capture]] — Salva sessões no vault
- [[skills/wiki-setup|wiki-setup]] — Inicialização de vault
