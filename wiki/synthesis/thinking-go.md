---
title: "Thinking × Go"
category: synthesis
tags: [go, thinking, synthesis, code-review]
sources:
  - "references/socratic-questioning.md"
  - "references/cognitive-bias-inventory.md"
  - "references/go-code-review.md"
  - "references/go-style-guide.md"
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
summary: "Como aplicar ferramentas de reasoning (socrático, bias inventory, pre-mortem) no ciclo de desenvolvimento Go: code review, design decisions, debugging."
provenance:
  extracted: 0.1
  inferred: 0.85
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
---

# Thinking × Go

## The Connection

Go é uma linguagem que força disciplina — `gofmt` elimina debates de estilo,
error handling explícito expõe falhas, interfaces pequenas forçam design
minimalista. Ferramentas de thinking (socrático, bias inventory, pre-mortem)
são a mesma disciplina aplicada ao raciocínio, não ao código. ^[inferred]

Juntas, elas criam um ciclo de desenvolvimento onde tanto o código quanto as
decisões por trás dele sobrevivem ao escrutínio.

## Onde se Encontram

| Ferramenta de Thinking | Aplicação em Go |
|---|---|
| [[references/socratic-questioning|Socratic Questioning]] | "Por que essa interface tem 5 métodos? Quais premissas sobre o caller estamos assumindo?" |
| [[references/cognitive-bias-inventory|Cognitive Bias Inventory]] | "Estou escolhendo `sync.Mutex` por familiaridade ou porque `sync.RWMutex` não serve?" |
| [[references/pre-mortem-analysis|Pre-Mortem]] | "Se esse código vazar goroutines em produção, como vamos detectar?" |
| [[references/dialectic-synthesis|Dialectic Synthesis]] | "Qual é o argumento mais forte contra usar channels em vez de mutexes aqui?" |
| [[references/evidence-audit|Evidence Audit]] | "Esse benchmark realmente prova que a otimização funciona, ou o setup é viesado?" |

## Cross-cutting Insight

O [[references/go-code-review|Go Code Review]] tradicional foca em estilo e
correção. Adicionar uma camada de thinking tools transforma o review em uma
auditoria de decisões: não apenas "esse código está idiomático?", mas "essa
decisão de design sobrevive a um pre-mortem?" ^[inferred]

**Padrão: "Go Review ++"**

1. **Code review tradicional** — `gofmt`, `go vet`, idiomático, error handling
2. **Socratic pass** — questionar cada interface e decisão de design
3. **Bias pass** — identificar vieses: familiarity bias (usar o que conhece),
   over-engineering bias (preparar para escalar antes da hora)
4. **Pre-mortem pass** — "Se deployarmos na sexta às 18h, o que quebra?"

## Tensions and Trade-offs

- **Tempo:** Code review já é caro. Adicionar 3 passes de thinking dobra o
  tempo. Reserve para PRs de alto impacto (nova API, mudança de concorrência). ^[inferred]
- **Ferramenta certa:** Nem todo PR precisa dos 4 passes. Use o
  [[references/mode-selection-guide|Mode Selection Guide]] para calibrar.

## Open Questions

- Como integrar thinking tools em CI/CD? (ex: pre-mortem checklist como gate de merge)
- O `golangci-lint` pode ser estendido com regras de bias detection?
- Times Go adotariam "Socratic Review" como prática padrão?

## Related

- [[references/go-code-review|Go Code Review]]
- [[references/go-style-guide|Go Style Guide]]
- [[references/socratic-questioning|Socratic Questioning]]
- [[references/cognitive-bias-inventory|Cognitive Bias Inventory]]
- [[references/pre-mortem-analysis|Pre-Mortem Analysis]]
- [[synthesis/thinking-architecture|Thinking × Architecture]]
