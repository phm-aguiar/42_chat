---
title: "Spec-Driven Development (SDD)"
category: concepts
tags: [sdd, metodologia, pipeline]
summary: "Metodologia onde specs são a fonte primária; código deriva delas."
created: "2026-06-13"
updated: "2026-06-13"
lifecycle: reviewed
lifecycle_changed: "2026-06-15"
lifecycle_reason: "auto-promoted by wiki-lint: well-established reference page"
sources: []
---

# Spec-Driven Development (SDD)

> Specs deixam de servir ao código; código passa a servir às specs.

## Pipeline no 42_chat

1. [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
2. [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
3. [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md
4. Aprovação humana (`Aprovado: true`)
5. [[projects/42_chat/agents/agent-orchestrator]] — Execução paralela com subagentes

## Regras

- Nunca implementar sem spec.md + plan.md aprovados
- Consultar constituição antes de qualquer código
- Validar estrutura periodicamente com `sdd-validate`

## Fontes Canônicas

As regras arquiteturais e a stack tecnológica vivem em `.github/memory/` (versionadas no repo):

| Fonte | Arquivo |
|---|---|
| Constituição (regras, portões, anti-padrões) | `.github/memory/constitution.md` |
| Stack tecnológica (linguagens, frameworks, CI) | `.github/memory/tech.md` |

> O vault referencia essas fontes, mas **não as duplica**. A fonte da verdade é o arquivo no repo.
> Para navegar: abra `.github/memory/constitution.md` e `.github/memory/tech.md` no editor.

## Relacionado

- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo com exemplo real
- [[concepts/onboarding|Onboarding]] — Como começar
- [[concepts/wiki-model|Wiki Model]] — Knowledge management
- [[synthesis/sdd-go|SDD × Go]] — Aplicação do SDD em projetos Go
