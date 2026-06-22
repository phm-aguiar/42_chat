---
title: "exhaustive — Enum Switch Exhaustiveness Checker"
category: tools
tags: [go, linter, golangci-lint, enum, switch, exhaustive]
sources:
  - "wiki/_raw/nishanthsexhaustive Check exhaustiveness of switch statements of enum-like constants in Go source code..md"
summary: "exhaustive checks exhaustiveness of enum switch statements in Go source code. Ensures all iota constants are covered."
provenance:
  extracted: 1.00
  inferred: 0.00
  ambiguous: 0.00
base_confidence: 0.98
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: supporting
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
---

# exhaustive

> [!tldr] Checks exhaustiveness of enum switch statements in Go source code. Ensures all `iota` constants are covered in switch cases.

**Repo**: [github.com/nishanths/exhaustive](https://github.com/nishanths/exhaustive)

---

## Install

```bash
go install github.com/nishanths/exhaustive/cmd/exhaustive@latest
```

---

## Usage

```bash
exhaustive [flags] [packages]
```

Package integration:
```go
import "github.com/nishanths/exhaustive"
```

The `exhaustive.Analyzer` variable follows the [`golang.org/x/tools/go/analysis`](https://pkg.go.dev/golang.org/x/tools/go/analysis) interface.

---

## Example

Given an enum:
```go
package token

type Token int

const (
    Add Token = iota
    Subtract
    Multiply
    Quotient
    Remainder
)
```

And code that switches on the enum:
```go
package calc

import "example.org/token"

func x(t token.Token) {
    switch t {
    case token.Add:
    case token.Subtract:
    case token.Remainder:
    default:
    }
}
```

Running `exhaustive` produces:
```
calc.go:6:2: missing cases in switch of type token.Token: token.Multiply, token.Quotient
```

---

## Map Key Checking

Specify `-check=switch,map` to also check exhaustiveness of keys in map literals:

```go
var m = map[token.Token]rune{
    token.Add:      '+',
    token.Subtract: '-',
    token.Multiply: '*',
    token.Quotient: '/',
}
```

```
calc.go:14:9: missing keys in map of key type token.Token: token.Remainder
```

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[references/go/go-enum|Go Enum]] — Enums type-safe em Go
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
