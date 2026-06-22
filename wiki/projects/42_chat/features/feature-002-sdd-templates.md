---
title: "002: Templates Canônicos SDD"
category: projects
tags: [sdd, templates, spec, plan, tasks]
summary: "Define os 4 templates canônicos SDD: spec.md, plan.md, tasks.md, AGENTS.md + llms.txt."
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-13"
sources:
  - repo:specs/features/002-sdd-templates/
lifecycle: draft
lifecycle_changed: "2026-06-13"
base_confidence: 0.85
provenance:
  extracted: 0.85
  inferred: 0.15
  ambiguous: 0.0
---

# 002: Templates Canônicos SDD

> Define formatos canônicos para spec.md, plan.md, tasks.md, AGENTS.md e llms.txt.

## Status

**Em progresso.** Tasks concluídas: 7/11.

## Formatos definidos

- **spec.md** — 4 seções: Visão Geral, BDD, Restrições, Checklist
- **plan.md** — 4 seções: Metadados, Contratos, Decisões, Auditoria
- **tasks.md** — Fases com T001-TNNN, dependências explícitas
- **AGENTS.md** — Seção SDD Workflow
- **llms.txt** — Navegação, camadas, links

## Tasks pendentes

- **T008:** Geração de plan.md + tasks.md a partir de spec.md
- **T009:** [[skills/sdd-validate|sdd-validate]] verifica conformidade dos templates
- **T010:** Testes de snapshot para refatorador
- **T011:** Exemplos antes/depois na spec

## Relacionado

- [[projects/42_chat/features/feature-001-start-repo|001: Estrutura]] — Base que esta feature refina
- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] — Consumidora dos templates
- [[sdd]] — Metodologia
