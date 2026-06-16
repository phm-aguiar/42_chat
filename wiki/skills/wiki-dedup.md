1|---
2|title: "wiki-dedup"
3|category: skills
4|tags: [wiki, skill, deduplicacao, limpeza]
5|sources: [.hermes/skills/wiki/dedup/SKILL.md]
6|summary: "Detecta paginas duplicadas ou com sobreposicao significativa no vault. Sugere merge ou arquivamento."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# wiki-dedup
13|
14|> Encontra e resolve duplicatas no vault.
15|
16|## Localizacao
17|`.hermes/skills/wiki/dedup/SKILL.md`
18|
19|## Quando usar
20|- Vault cresceu e tem sobreposicao
21|- Multiplos ingests da mesma fonte
22|- Antes de `wiki-lint --consolidate`
23|
24|## Relacionado
25|- [[skills/wiki-lint]] — Lint detecta contradicoes, dedup detecta duplicatas
26|- [[skills/wiki-cross-linker]] — Apos merge, cross-linker reconecta
27|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar paginas candidatas a merge, verificar similaridade entre conceitos, ou identificar duplicatas antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.