---
title: "003: Forjar Nova Skill"
category: projects
tags: [sdd, skills, hermes-agent, tooling]
summary: "Skill forge-new-skill para criar skills Hermes Agent com scaffold, template e validação."
created: "2026-06-13"
updated: "2026-06-13"
sources:
  - repo:specs/features/003-forge-skill/
lifecycle: in-progress
lifecycle_changed: "2026-06-13"
base_confidence: 0.8
provenance:
  extracted: 0.8
  inferred: 0.2
  ambiguous: 0.0
---

# 003: Forjar Nova Skill

> Skill que automatiza criação de novas skills Hermes Agent com scaffold, template e validação SDD.

## Status

**Em progresso.** Tasks concluídas: 5/10. Metade da feature implementada.

## O que já funciona

- `scaffold-skill.sh`: gera árvore `.hermes/skills/<nome>/` com `assets/`, `scripts/`, `references/`
- `template-skill.md`: placeholders `{{skill_name}}`, `{{skill_description}}`, `{{skill_title}}`
- `skill-format.md`: documentação do formato SKILL.md (frontmatter, descrição, paths)
- `SKILL.md` da forge-new-skill: fluxo de 4 passos
- `spec.md` da feature 003 no formato canônico SDD

## Tasks pendentes

- **T006:** Adicionar ao [[skills/sdd-refactor-artifact|sdd-refactor-artifact]] suporte a plan.md + tasks.md
- **T007:** Testar skill dummy com forge-new-skill + [[skills/sdd-validate|sdd-validate]]
- **T008:** Escopo (projeto vs global) com confirmação do usuário
- **T009:** plan.md + tasks.md da própria feature 003
- **T010:** llms.txt na raiz

## Relacionado

- [[projects/42_chat/features/feature-002-sdd-templates|002: Templates]] — Formatos que a skill usa
- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] — Upgrade futuro do tasks.md
- `skill-forge` — Skill Hermes para criação de novas skills (`.hermes/skills/skill-forge/`)
