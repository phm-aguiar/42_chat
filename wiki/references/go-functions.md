---
title: "Go Functions"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-functions/SKILL.md"
summary: "Go Functions: boas práticas e regras de estilo Go destiladas de Effective Go, Google Style Guide, Uber Style Guide."
provenance:
  extracted: 0.35
  inferred: 0.60
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: "2026-06-16T00:00:00Z"
updated: "2026-06-16T00:00:00Z"
---

# Go Function Design

> **When this skill does NOT apply**: For functional options constructors (`WithTimeout`, `WithLogger`), see [[go-functional-options]]. For error return conventions, see [[go-error-handling]]. For naming functions and methods, see [[go-naming]].

---

## Function Grouping and Ordering

Organize functions in a file by these rules:

1. Functions sorted in **rough call order**
2. Functions **grouped by receiver**
3. **Exported** functions appear first, after `struct`/`const`/`var` definitions
4. `NewXxx`/`newXxx` constructors appear right after the type definition
5. Plain utility functions appear toward the end of the file

```go
type something struct{ ... }

func newSomething() *something { return &something{} }

func (s *something) Cost() int { return calcCost(s.weights) }

func (s *something) Stop() { ... }

func calcCost(n []int) int { ... }
```

---

## Function Signatures

> *Consulte SIGNATURES para detalhes.*

Keep the signature on a single line when possible. When it must wrap, put **all
arguments on their own lines** with a trailing comma:

```go
func (r *SomeType) SomeLongFunctionName(
    foo1, foo2, foo3 string,
    foo4, foo5, foo6 int,
) {
    foo7 := bar(foo1)
}
```

Add `/* name */` comments for ambiguous arguments, or better yet, replace naked
`bool` parameters with custom types.

---

## Pointers to Interfaces

You almost never need a pointer to an interface. Pass interfaces as values — the
underlying data can still be a pointer.

```go
// Bad: pointer to interface
func process(r *io.Reader) { ... }

// Good: pass the interface value
func process(r io.Reader) { ... }
```

---

## Printf and Stringer

> *Consulte PRINTF-STRINGER para detalhes.*

### Printf-style Function Names

Functions that accept a format string should end in `f` for `go vet` support.
Declare format strings as `const` when used outside `Printf` calls.

Prefer `%q` over `%s` with manual quoting when formatting strings for logging
or error messages — it safely escapes special characters and wraps in quotes:

```go
return fmt.Errorf("unknown key %q", key) // produces: unknown key "foo\nbar"
```

See **go-functional-options** when designing a constructor with 3+ optional
parameters.

---

## Quick Reference

| Topic | Rule |
|-------|------|
| File ordering | Type -> constructor -> exported -> unexported -> utils |
| Signature wrapping | All args on own lines with trailing comma |
| Naked parameters | Add `/* name */` comments or use custom types |
| Pointers to interfaces | Almost never needed; pass interfaces by value |
| Printf function names | End with `f` for `go vet` support |

---

## Related Skills

- **Error returns**: See [[go-error-handling]] when designing error return patterns or wrapping errors in multi-return functions
- **Naming conventions**: See [[go-naming]] when naming functions, methods, or choosing getter/setter patterns
- **Functional options**: See [[go-functional-options]] when designing a constructor with 3+ optional parameters
- **Formatting principles**: See [[go-style-core]] when deciding line length, naked returns, or signature formatting

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-error-handling|Error Handling]]
- [[go-functional-options|Functional Options]]
- [[go-naming|Naming]]
- [[go-style-core|Style Core]]
