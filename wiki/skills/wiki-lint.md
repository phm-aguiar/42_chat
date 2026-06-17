1|---
2|title: "wiki-lint"
3|category: skills
4|tags: [wiki, skill, lint, auditoria, qualidade]
5|sources: [.hermes/skills/wiki/lint/SKILL.md]
6|summary: "Audita a saúde do vault Obsidian: broken links, páginas órfãs, frontmatter faltante, contradições, stale content. Com --consolidate, corrige automaticamente."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-15"
10|---
11|
12|# wiki-lint
13|
14|> Auditor de saúde do vault. Encontra problemas antes que virem débito técnico.
15|
16|## Localização
17|
18|`.hermes/skills/wiki/lint/SKILL.md`
19|
20|## Quando usar
21|
22|- Após múltiplos ingests (mover/renomear páginas quebra links)
23|- Antes de commit (gate de qualidade)
24|- Periodicamente (cron job semanal)
25|
26|## Checks (13 no total)
27|
28|- **Broken wikilinks:** wikilink apontando pra página que não existe
29|- **Orphaned pages:** páginas sem incoming links
30|- **Missing frontmatter:** campos obrigatórios faltando
31|- **Stale content:** páginas desatualizadas vs sources
32|- **Contradictions:** claims conflitantes entre páginas
33|- **Index consistency:** `index.md` vs disco
34|- **Fragmented tags:** clusters de tags sem cross-links
35|
36|## Modo --consolidate
37|
38|Além de reportar, **corrige** automaticamente:
39|- Conserta broken links (fuzzy match)
40|- Adiciona cross-references pra órfãos
41|- Promove drafts antigos → reviewed
42|- Normaliza aliases de tags
43|
44|## Exemplo real
45|
46|Na feature 006, o `wiki-lint` encontrou 18 broken links (renomeações de
47|`runtime-orchestrator` → `agent-orchestrator`). Todos corrigidos em 1 commit.
48|
## Relacionado

- [[skills/wiki-cross-linker|cross-linker]] — Adiciona wikilinks faltantes
- [[skills/wiki-dedup|wiki-dedup]] — Resolve páginas duplicadas
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica (checks de lint, page thresholds, pitfalls)
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Pipeline de manutenção do vault
54|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas com problemas recorrentes, padroes de broken links, ou auditorias anteriores antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.