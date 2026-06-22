---
title: "wiki-hermes-history-ingest"
category: skills
tags: [wiki, skill, hermes, historico, ingest]
sources: [.hermes/skills/wiki/hermes-history-ingest/SKILL.md]
summary: "Ingere historico de sessoes do Hermes Agent no vault. Converte conversas em paginas wiki estruturadas."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# wiki-hermes-history-ingest

> Transforma sessoes do Hermes em conhecimento compilado.

## Localizacao
`.hermes/skills/wiki/hermes-history-ingest/SKILL.md`

## Quando usar
- Apos sessoes importantes
- Periodicamente (cron job)
- Migrar historico acumulado

## Relacionado
- [[skills/wiki-capture]] — Captura sessao atual (online)
- [[skills/wiki-ingest]] — Ingest generico (offline)

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar sessoes ja ingeridas, padroes de conversa documentados, ou lacunas no historico antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.