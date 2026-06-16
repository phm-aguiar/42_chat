---
title: "SDD × Go"
category: synthesis
tags: [sdd, go, methodology, synthesis]
sources:
  - "references/go-style-guide.md"
  - "concepts/sdd.md"
  - "concepts/sdd-workflow.md"
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
summary: "Como o Spec-Driven Development se aplica a projetos Go: spec-first com padrões idiomáticos, testes como cidadãos de primeira classe, e o pipeline SDD como garantia de qualidade."
provenance:
  extracted: 0.1
  inferred: 0.8
  ambiguous: 0.1
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: core
---

# SDD × Go

## The Connection

SDD (Spec-Driven Development) e o ecossistema Go compartilham um valor fundamental:
**disciplina antes de implementação.** O SDD exige spec.md → plan.md → tasks.md antes
de qualquer linha de código. Go exige `gofmt`, convenções de nome, error handling
explícito — disciplina de código antes da lógica de negócio.

Ambos reduzem o "custo da interpretação": no SDD, a spec elimina ambiguidade entre
stakeholders; em Go, o tooling (`gofmt`, `go vet`, `golangci-lint`) elimina
ambiguidade entre desenvolvedores. ^[inferred]

## Onde se Encontram

O pipeline SDD tem afinidade natural com projetos Go:

1. **Fase Spec** — Define contratos de API, modelos de dados, e cenários BDD.
   Mapeia diretamente para interfaces Go, structs, e table-driven tests. ^[inferred]
2. **Fase Plan** — ADRs capturam decisões de arquitetura (padrão Repository,
   injeção de dependência, [[go-modular-architecture|modular architecture]]).
3. **Fase Tasks** — DAG de tasks atômicas espelha a filosofia Go de funções
   pequenas e focadas com responsabilidade única.
4. **Fase Implementação** — [[go-testing|table-driven tests]] e
   [[go-error-handling|error handling explícito]] são verificações naturais
   contra a spec original.

## Cross-cutting Insight

O [[go-style-guide|Go Style Guide]] e o pipeline [[concepts/sdd|SDD]] são
dois lados da mesma moeda: um padroniza o código, o outro padroniza o processo.
Projetos que adotam ambos ganham:

- **Rastreabilidade bidirecional**: spec → plan → task → commit → test. ^[inferred]
- **Revisão de código com contexto**: o revisor lê a spec linkada no PR,
  não adivinha intenção.
- **Refatoração segura**: a spec + testes Go garantem que o comportamento
  não muda.

## Tensions and Trade-offs

- **SDD é pesado para scripts simples.** Um script Go de 50 linhas não precisa
  de spec.md. O SDD brilha em features com superfície de API ou lógica de
  negócio. ^[inferred]
- **Go favorece documentation-in-code** (`godoc`), SDD favorece
  documentation-before-code. São complementares: a spec diz "o quê", o godoc
  diz "como usar". ^[ambiguous]

## Open Questions

- Como integrar `go vet` e `golangci-lint` como gates no pipeline SDD?
- O formato tasks.md com DAG é overkill para projetos Go pequenos?
- BDD com Gherkin + Godog se encaixa melhor que table-driven tests para specs?

## Related

- [[concepts/sdd|SDD]]
- [[concepts/sdd-workflow|SDD Workflow]]
- [[references/go-style-guide|Go Style Guide]]
- [[references/go-modular-architecture|Go Modular Architecture]]
- [[references/go-testing|Go Testing]]
