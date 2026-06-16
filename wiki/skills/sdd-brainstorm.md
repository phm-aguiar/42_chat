---
title: "sdd-brainstorm"
category: skills
tags: [sdd, skill, brainstorm, spec, discovery]
sources: [.hermes/skills/sdd/brainstorm/SKILL.md, .hermes/skills/sdd/brainstorm/references/interview-dimensions.md]
summary: "Entrevista interativa com clarify() para extrair requisitos e gerar spec.md. Entry point do pipeline SDD — cobre proposito, escopo, happy path, edge cases, constraints e criterios de sucesso."
provenance:
  extracted: 0.85
  inferred: 0.10
  ambiguous: 0.05
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
updated: "2026-06-15"
---

# sdd-brainstorm

> Entry point do pipeline SDD. Transforma ideias em `spec.md` via entrevista interativa com `clarify()`.

## Localizacao
`.hermes/skills/sdd/brainstorm/SKILL.md`

## Quando usar
- Antes de escrever qualquer spec — feature nova, por mais simples que pareca
- Quando o usuario diz "brainstorm", "discutir ideia", "nova feature", "pensar feature", "entrevista", "discovery", "bora pensar"
- **HARD-GATE:** Nunca implemente antes do spec aprovado

## Fluxo (8 passos)
1. **Explorar contexto** — le `tech.md`, `constitution.md`, features existentes
2. **Avaliar escopo** — decompoe se necessario (varios subsistemas = features separadas)
3. **Entrevista interativa** — 7 dimensoes com `clarify()`, uma pergunta por vez:
   - Proposito (problema, publico, urgencia)
   - Escopo (dentro/fora explicito)
   - Happy Path (fluxo principal passo a passo)
   - Edge Cases (minimo 2)
   - Constraints (performance, tech, prazo, compliance)
   - Criterios de Sucesso (metricas mensuraveis)
   - Trade-offs (abordagens tecnicas)
4. **Propor 2-3 abordagens** — com trade-offs e recomendacao
5. **Gerar spec.md** — template canonico em `specs/features/<id>-<slug>/`
6. **Self-review** — placeholders? contradicoes? YAGNI?
7. **Gate de aprovacao** — `clarify()` para aprovacao explicita
8. **Transicao** → `sdd-generate-plan`

## Guardrails
- Uma pergunta por `clarify()`, multipla escolha sempre que possivel
- YAGNI implacavel: spec com minimo viavel
- Respeita `constitution.md` — se inevitavel violar, alerta e pede autorizacao
- Idempotente: detecta spec existente e pergunta se refina ou comeca do zero
- ID incremental derivado de `specs/features/`

## Dimensoes da Entrevista (detalhadas em `references/interview-dimensions.md`)
Cada dimensao tem criterio de "pronto":
- **Proposito:** "resolve problema X para publico Y porque motivo Z" em 2 frases
- **Escopo:** 2-5 itens dentro + pelo menos 1 fora explicito
- **Happy Path:** fluxo inicio→fim sem saltos, minimo 3 passos
- **Edge Cases:** minimo 2 com comportamento definido
- **Constraints:** explicitas ou "nenhuma alem de constitution.md"
- **Sucesso:** minimo 2 criterios mensuraveis
- **Trade-offs:** abordagem clara ou agente propoe 2-3 opcoes

Atalhos: "Nao sei" → sugestoes; "Confio em voce" → defaults + validacao; "Pula" → registra "Nao especificado".

## Relacionado
- [[skills/sdd-generate-plan]] — Proximo passo: gera plan.md arquitetural
- [[skills/sdd-generate-tasks]] — Fim do pipeline: gera tasks.md com DAG
- [[skills/sdd-init-repo]] — Inicializa estrutura que o brainstorm usa
- [[skills/sdd-validate]] — Valida conformidade SDD apos spec gerado

## Buscando conhecimento compilado
Use `[[skills/wiki-query|wiki-query]]` para buscar decisoes previas, ADRs existentes, ou padroes ja documentados no vault antes de gerar uma nova spec. O vault contem conhecimento cross-cutting que pode evitar reinventar decisoes.
