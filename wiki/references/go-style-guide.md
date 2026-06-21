---
title: "Go Style Guide Reference"
category: references
tags: [go, style-guide, coding-standards, reference]
sources:
  - "wiki/_raw/go-style-core/SKILL.md"
  - "wiki/_raw/go-naming/SKILL.md"
  - "wiki/_raw/go-error-handling/SKILL.md"
  - "wiki/_raw/go-concurrency/SKILL.md"
  - "wiki/_raw/go-testing/SKILL.md"
  - "wiki/_raw/go-functions/SKILL.md"
  - "wiki/_raw/go-interfaces/SKILL.md"
  - "wiki/_raw/go-packages/SKILL.md"
  - "wiki/_raw/go-declarations/SKILL.md"
  - "wiki/_raw/go-control-flow/SKILL.md"
  - "wiki/_raw/go-context/SKILL.md"
  - "wiki/_raw/go-data-structures/SKILL.md"
  - "wiki/_raw/go-defensive/SKILL.md"
  - "wiki/_raw/go-documentation/SKILL.md"
  - "wiki/_raw/go-functional-options/SKILL.md"
  - "wiki/_raw/go-generics/SKILL.md"
  - "wiki/_raw/go-linting/SKILL.md"
  - "wiki/_raw/go-logging/SKILL.md"
  - "wiki/_raw/go-performance/SKILL.md"
  - "wiki/_raw/go-code-review/SKILL.md"
summary: Catálogo de 20 tópicos de estilo e boas práticas Go destilados dos guias oficiais (Google, Uber, Effective Go, CodeReviewComments).
provenance:
  extracted: 0.15
  inferred: 0.82
  ambiguous: 0.03
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: core
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
---

# Go Style Guide Reference

> [!tldr] Catálogo de 20 tópicos cobrindo boas práticas de Go, destilados dos
> guias oficiais: [Google Go Style Guide](https://google.github.io/styleguide/go/),
> [Uber Go Style Guide](https://github.com/uber-go/guide), [Effective Go](https://go.dev/doc/effective_go),
> e [Go Wiki CodeReviewComments](https://go.dev/wiki/CodeReviewComments).

## Princípios Fundamentais

Os 5 princípios do [[go-style-core|Go Style Core]], em ordem de prioridade:

1. **Clareza** — O leitor entende sem contexto extra?
2. **Simplicidade** — É a abordagem mais simples?
3. **Concisão** — Cada linha se justifica?
4. **Manutenibilidade** — Fácil de modificar depois?
5. **Consistência** — Combina com o código ao redor?

## Catálogo de Tópicos

### Fundamentos

| Página | Foco |
|--------|------|
| [[go-style-core]] | Princípios, formatação (`gofmt`), nesting, naked returns, semicolons |
| [[go-naming]] | Nomes de pacotes, tipos, funções, variáveis, convenções MixedCaps |
| [[go-declarations]] | `var` vs `:=`, escopo, shadowing, inicialização, iota, literais |
| [[go-control-flow]] | If com init, early returns, switch patterns, blank identifier |

### Funções e Interfaces

| Página | Foco |
|--------|------|
| [[go-functions]] | Assinaturas, Printf/Stringer, organização, named returns, `defer` |
| [[go-interfaces]] | Definição, receiver types, embedding, verificação de conformidade |
| [[go-functional-options]] | Padrão Functional Options: construtores com parâmetros opcionais |
| [[go-generics]] | Quando usar, constraints, type inference, boas práticas |

### Dados e Estruturas

| Página | Foco |
|--------|------|
| [[go-data-structures]] | Slices, maps, arrays, `new` vs `make`, `append`, declaração nil/empty |
| [[go-packages]] | Organização, imports, tamanho de pacote, dependências |

### Robustez

| Página | Foco |
|--------|------|
| [[go-error-handling]] | Estratégia, wrapping (`%w`/`%v`), sentinelas, custom types, `errors.Is`/`As` |
| [[go-context]] | `context.Context`: assinaturas, cancelamento, timeouts, valores |
| [[go-defensive]] | Cópia em boundaries, interface compliance, `defer`, panics, time enums |
| [[go-concurrency]] | Goroutines, channels, mutexes, sync primitives, buffer pooling |

### Qualidade

| Página | Foco |
|--------|------|
| [[go-testing]] | Table-driven tests, subtests, `cmp.Diff`, helpers, `t.Cleanup()` |
| [[go-documentation]] | Doc comments, exemplos, convenções, pacote-level docs |
| [[go-linting]] | `golangci-lint`, configuração, CI/CD |
|| [[go-logging]] | `slog`, níveis, structured logging, contexto |
|| [[go-performance]] | Benchmarks, otimização de strings, alocação, profiling |
|| [[go-code-review]] | Checklist sistemática, web servers, PR review |

### Implementação e Arquitetura

| Página | Foco |
|--------|------|
| [[go-modular-architecture]] | Arquitetura modular Go: camadas, injeção, ciclo de vida |
| [[go-repository]] | Padrão Repository: abstração de persistência |
| [[go-service]] | Camada de serviço: regras de negócio, orquestração |
| [[go-usecase]] | Padrão Use Case: lógica de aplicação |
| [[go-chi-router]] | Roteamento HTTP com `go-chi` |
| [[go-chi-handler]] | Handlers HTTP idiomáticos |
| [[go-gorm-model]] | Models com GORM: mapeamento objeto-relacional |
| [[go-mapper]] | Mapeamento entre camadas (DTO, domain, entity) |
| [[go-validator]] | Validação de entrada e domínio |
| [[go-cache]] | Estratégias de cache em Go |
| [[go-enum]] | Enums type-safe em Go |
| [[go-error]] | Tipos de erro customizados |
| [[go-unit-tests]] | Testes unitários: mocks, asserts, cobertura |
| [[go-integration-tests]] | Testes de integração: banco, HTTP, mensageria |
| [[ai-brag-document]] | Documentação de conquistas e impacto com IA |

### WebSocket (gorilla/websocket)

| Página | Foco |
|--------|------|
| [[go-websocket-core]] | Core: upgrade, read/write, ping/pong, close, anti-patterns |
| [[go-websocket-server]] | Server: HTTP routers, auth, CORS, graceful shutdown |
| [[go-websocket-client]] | Client: dial, reconnect, heartbeat, offline buffer, TLS |
| [[go-websocket-hub]] | Hub pattern: broadcast, rooms, direct messaging, metrics |
| [[go-websocket-testing]] | Testing: httptest, table-driven, race detection, mocks |

### Fontes Canônicas

As regras são derivadas destes documentos (consulte os originais para detalhes completos):

- [Google Go Style Guide](https://google.github.io/styleguide/go/) — Guia completo com decisions e best practices
- [Uber Go Style Guide](https://github.com/uber-go/guide) — Regras pragmáticas usadas em produção na Uber
- [Effective Go](https://go.dev/doc/effective_go) — Documento canônico da linguagem
- [Go Wiki: CodeReviewComments](https://go.dev/wiki/CodeReviewComments) — Checklist da comunidade Go

## Ver Também

- [[synthesis/sdd-go|SDD × Go]] — Spec-Driven Development aplicado a Go

- [[go-style-core]] — Princípios centrais
- [[go-naming]] — Convenções de nomes
- [[go-error-handling]] — Tratamento de erros
- [[references/go-enum|Go Enum]]
