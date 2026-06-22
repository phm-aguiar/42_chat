---
title: "doc-generate-llms-txt"
category: skills
tags: [doc, skill, llms-txt, navegacao]
sources: [.hermes/skills/doc/generate-llms-txt/SKILL.md]
summary: "Gera llms.txt na raiz do repo seguindo o protocolo llmstxt.org. Guia de navegacao otimizado para LLMs com links para specs, constitution e skills."
lifecycle: draft
created: "2026-06-13"
rag_score: 0.48
superseded_by: "[[skills/brain|brain]]"
updated: "2026-06-13"
---

# doc-generate-llms-txt

> Gera `llms.txt` — indice navegavel para LLMs.

## Localizacao
`.hermes/skills/doc/generate-llms-txt/SKILL.md`

## Quando usar
- Setup inicial do repo
- Apos adicionar novas features
- Apos mudancas estruturais significativas

## Formato
Segue o protocolo https://llmstxt.org/:
- `/llms.txt` — indice com links
- `/llms-full.txt` — documentacao completa (opcional)

## Relacionado
- [[skills/doc-extract]] — Extrai secoes referenciadas
- [[skills/doc-generate-toc]] — TOC dos documentos

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar llms.txt existentes, estrutura documentada do repositorio, ou dependencias entre arquivos antes de agir.