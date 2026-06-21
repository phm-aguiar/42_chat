---
title: "sdd-generate-plan"
category: skills
tags: [sdd, skill, arquitetura, adr, plano]
sources: [.hermes/skills/sdd/generate-plan/SKILL.md, .hermes/skills/sdd/generate-plan/references/architecture-patterns.md]
summary: "Gera plan.md arquitetural a partir do spec.md, tech.md e constitution.md. Produz 4 secoes canonicas: Metadados, Contratos, ADRs e Auditoria de Constituicao."
provenance:
  extracted: 0.80
  inferred: 0.15
  ambiguous: 0.05
base_confidence: 0.60
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
updated: "2026-06-15"
---

# sdd-generate-plan

> Gera `plan.md` arquitetural com ADRs a partir do spec aprovado. Segundo passo do pipeline SDD.

## Localizacao
`.hermes/skills/sdd/generate-plan/SKILL.md`

## Quando usar
- Apos spec.md aprovado (brainstorm concluido)
- Usuario diz "gerar plan", "criar plan.md", "generate architectural plan", "criar plano"
- Precisa formalizar decisoes tecnicas antes de gerar tasks

## Fluxo (4 passos)
1. **Identificar feature** — usuario informa ou skill pergunta
2. **Ler fontes** — `spec.md` (funcionalidade), `tech.md` (stack), `constitution.md` (portoes)
3. **Gerar 4 secoes canonicas:**
   - **Metadados:** stack tecnologico, feature fonte, escopo (1 frase)
   - **Contratos e Fronteiras:** APIs, eventos, schemas ou "Nenhum contrato formal"
   - **ADRs:** mini-registros com Decisao + Justificativa + Alternativa Rejeitada. Minimo 1 ADR
   - **Auditoria de Constituicao:** checklist contra cada regra do `constitution.md`
4. **Apresentar e salvar** — stack, numero de ADRs, itens da auditoria. Pergunta antes de salvar.

## Decision Tree de Arquitetura (de `references/architecture-patterns.md`)
- **Time unico (<10 devs), dominio em evolucao** → Modular Monolith
- **Multiplos times, bounded contexts** → Microservices (se deploy independente) ou Modular Monolith com service modules
- **Workflows orientados a eventos** → Event-Driven (Kafka, NATS, RabbitMQ)
- **Carga variavel** → Serverless (Lambda, Workers)
- **Consistencia forte** → Monolith ou Modular Monolith

Fatores: tamanho do time, Lei de Conway, independencia de deploy, CAP theorem, maturidade operacional.

## Padroes Go (do `tech.md` quando Go e a stack)
- **APIs:** Layered (simples) → Hexagonal (dominio rico) → CQRS (demandas diferentes)
- **Comunicacao:** REST+JSON (simples) → gRPC (perf) → NATS/Kafka (assincrono) → WebSocket (real-time)
- **Dados:** Repository → Unit of Work → Event Sourcing

## Guardrails
- Nao inventa stack: usa apenas `tech.md`. Vazio = placeholders `{{...}}`
- ADR minimo: 1 ADR estrutural se spec nao sugerir decisoes
- Preserva placeholders `{{...}}` do spec
- Idempotente: pergunta se sobrescreve ou mescla plan.md existente
- Anti-padroes: microservices prematuro, overengineering, tecnologia por hype

## Relacionado
- [[skills/sdd-brainstorm]] — Passo anterior: gera spec.md
- [[skills/sdd-generate-tasks]] — Proximo passo: gera tasks.md com DAG
- [[skills/sdd-validate]] — Valida conformidade do plano gerado
- [[skills/sdd-refactor-artifact]] — Normaliza artefatos SDD

## Buscando conhecimento compilado
Use `[[skills/wiki-query|wiki-query]]` para consultar ADRs existentes, padroes arquiteturais ja documentados, ou decisoes previas sobre stack antes de gerar um novo plano. O vault evita reinventar escolhas arquiteturais.
