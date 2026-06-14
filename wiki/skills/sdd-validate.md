---
title: "sdd-validate"
category: skills
tags: [sdd, skill, validacao, qualidade]
sources: [.hermes/skills/sdd/validate/SKILL.md]
summary: "Valida a conformidade SDD do repositorio: diretorios obrigatorios, artefatos por feature, AGENTS.md. Reporta PASS/FAIL/WARN."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# sdd-validate

> Auditor de conformidade SDD. Read-only — nunca modifica arquivos.

## Localizacao
`.hermes/skills/sdd/validate/SKILL.md`

## Quando usar
- Antes de commit (gate de qualidade)
- Apos criar nova feature (spec/plan/tasks existem?)
- Periodicamente

## Checks
- `.github/memory/` (constitution.md, tech.md)
- `specs/` (features, domain-events, infra)
- Cada feature: spec.md, plan.md, tasks.md
- `AGENTS.md`

## Relacionado
- [[skills/sdd-init-repo]] — Cria a estrutura que validate audita
- [[skills/wiki-lint]] — Equivalente para o vault
