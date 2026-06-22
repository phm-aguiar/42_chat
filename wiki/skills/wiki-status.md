---
title: "wiki-status"
category: skills
tags: [wiki, skill, status, delta, auditoria]
sources: [.hermes/skills/wiki/status/SKILL.md]
summary: "Mostra o estado atual do vault: paginas, delta desde ultimo ingest, fontes pendentes, recomendacao append vs rebuild."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# wiki-status

> Raio-X do vault. O que foi ingerido, o que mudou, o que falta.

## Localizacao
`.hermes/skills/wiki/status/SKILL.md`

## Quando usar
- Antes de `wiki-ingest` (avaliar delta)
- Diagnosticar vault desatualizado
- Ver cobertura de fontes

## Relacionado
- [[skills/wiki-lint]] — Lint audita saude, status audita cobertura
- [[skills/wiki-ingest]] — Ingest usa status para decidir append vs rebuild

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar deltas anteriores, metricas historicas do vault, ou recomendacoes de rebuild antes de agir. O vault e a memoria de longo prazo do framework — consultar evita retrabalho e inconsistencias.