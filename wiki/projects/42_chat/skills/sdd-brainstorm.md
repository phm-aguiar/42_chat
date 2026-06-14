---
title: "sdd-brainstorm"
category: projects
tags: [sdd, skill, brainstorm, spec]
sources: []
summary: Skill SDD que conduz entrevista interativa via clarify() para gerar spec.md
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# sdd-brainstorm

> Entry point do pipeline SDD. Transforma ideias em `spec.md` via entrevista interativa.

## Localização
Skill Hermes: `.hermes/skills/sdd/brainstorm/SKILL.md`

## Função
- Conduz entrevista com `clarify()` — uma pergunta por vez
- Gera `spec.md` com template canônico
- Gate de aprovação antes de prosseguir

## Pipeline
`sdd-brainstorm` → `spec.md` → `sdd-generate-plan` → `plan.md` → `sdd-generate-tasks` → `tasks.md`

## Relacionado
- [[concepts/sdd]] — Metodologia completa
- [[projects/42_chat/skills/sdd-generate-plan]] — Próximo passo
- [[projects/42_chat/features/feature-001-start-repo]] — Feature que iniciou o repo
