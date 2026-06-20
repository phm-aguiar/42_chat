---
title: "sdd-explore-tech"
category: skills
tags: [sdd, skill, tech, stack, mapeamento]
sources: [.hermes/skills/sdd/explore-tech/SKILL.md]
summary: "Mapeia a stack tecnologica do projeto: linguagens, frameworks, banco de dados, CI/CD. Preenche .github/memory/tech.md."
lifecycle: draft
created: "2026-06-13"
superseded_by: "[[skills/sdd|sdd]]"
updated: "2026-06-13"
---

# sdd-explore-tech

> Descobre e documenta a stack tecnologica do projeto.

## Localizacao
`.hermes/skills/sdd/explore-tech/SKILL.md`

## Quando usar
- Apos `sdd-init-repo`
- Quando adicionar nova dependencia ao projeto
- Antes de `sdd-generate-plan` (precisa da stack definida)

## O que faz
- Le `go.mod`, `package.json`, `pyproject.toml`, etc.
- Detecta CI/CD (GitHub Actions, GitLab CI)
- Atualiza `.github/memory/tech.md`

## Relacionado
- [[skills/sdd-init-repo]] — Roda antes
- [[skills/sdd-validate]] — Valida o que foi mapeado

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar stack ja mapeado, dependencias documentadas, ou decisoes sobre tecnologias no vault antes de agir. O vault documenta decisoes previas que evitam retrabalho no pipeline SDD.