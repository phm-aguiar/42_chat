---
title: "skill-forge"
category: skills
tags: [general, skill, scaffold, criacao]
sources: [.hermes/skills/general/skill-forge/SKILL.md]
summary: "Cria novas skills Hermes com scaffold padronizado: SKILL.md com frontmatter YAML, diretorios references/ scripts/ assets/."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# skill-forge

> Forja novas skills. Scaffold + template + validacao.

## Localizacao
`.hermes/skills/general/skill-forge/SKILL.md`

## Quando usar
- Criar nova skill Hermes
- Garantir que a skill segue o padrao (SKILL.md + frontmatter)

## O que cria
```
.hermes/skills/categoria/nome/
├── SKILL.md          ← Frontmatter YAML + corpo markdown
├── references/       ← Documentos de referencia
├── scripts/          ← Scripts auxiliares
└── assets/           ← Templates e assets
```

## Relacionado
- [[skills/agent-run]] — Skills sao usadas por agentes
- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] — Feature que originou esta skill

## Buscando conhecimento compilado
Use [[skills/wiki-query|wiki-query]] para buscar skills existentes com nomes similares, templates de SKILL.md, ou dependencias entre skills antes de agir.