---
title: "sdd-generate-plan"
category: projects
tags: [sdd, skill, plan, architecture, ADR]
sources: []
summary: Skill SDD que gera plan.md com decisões arquiteturais (ADR) a partir do spec.md
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# sdd-generate-plan

> Gera `plan.md` a partir do `spec.md`, `tech.md` e `constitution.md`.

## Localização
Skill Hermes: `.hermes/skills/sdd/generate-plan/SKILL.md`

## Função
- Lê spec.md, tech.md e constitution.md
- Gera 4 seções canônicas: Metadados, Contratos, ADRs, Auditoria de Constituição
- Pelo menos 1 ADR gerada
- Auditoria contra todas as regras do constitution.md

## Pipeline
`sdd-brainstorm` → `spec.md` → **`sdd-generate-plan`** → `plan.md` → `sdd-generate-tasks` → `tasks.md`

## Relacionado
- [[sdd-brainstorm]] — Passo anterior
- [[sdd-generate-tasks]] — Próximo passo
- [[concepts/constitution]] — Auditado pelo plan
- [[concepts/tech]] — Stack usada no plano
