1|---
2|title: "wiki-hermes-history-ingest"
3|category: skills
4|tags: [wiki, skill, hermes, historico, ingest]
5|sources: [.hermes/skills/wiki/hermes-history-ingest/SKILL.md]
6|summary: "Ingere historico de sessoes do Hermes Agent no vault. Converte conversas em paginas wiki estruturadas."
7|lifecycle: draft
8|created: "2026-06-13"
9|updated: "2026-06-13"
10|---
11|
12|# wiki-hermes-history-ingest
13|
14|> Transforma sessoes do Hermes em conhecimento compilado.
15|
16|## Localizacao
17|`.hermes/skills/wiki/hermes-history-ingest/SKILL.md`
18|
19|## Quando usar
20|- Apos sessoes importantes
21|- Periodicamente (cron job)
22|- Migrar historico acumulado
23|
24|## Relacionado
25|- [[skills/wiki-capture]] — Captura sessao atual (online)
26|- [[skills/wiki-ingest]] — Ingest generico (offline)
27|
## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar sessoes ja ingeridas, padroes de conversa documentados, ou lacunas no historico antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.