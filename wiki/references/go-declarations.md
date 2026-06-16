---
title: "Go Declarations"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-declarations/SKILL.md"
summary: "Go Declarations: boas práticas e regras de estilo Go destiladas de Google Style Guide, Uber Style Guide."
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

# Go Declarations and Initialization

---

## Quick Reference: var vs :=

| Context | Use | Example |
|---------|-----|---------|
| Top-level | `var` (always) | `var _s = F()` |
| Local with value | `:=` | `s := "foo"` |
| Local zero-value (intentional) | `var` | `var filtered []int` |
| Type differs from expression | `var` with type | `var _e error = F()` |

> *Consulte SCOPE para detalhes.*

---

## Group Similar Declarations

Group related `var`, `const`, `type` in parenthesized blocks. Separate
**unrelated** declarations into distinct blocks.

```go
// Bad
const a = 1
const b = 2

// Good
const (
    a = 1
    b = 2
)
```

Inside functions, group adjacent vars even if unrelated:

```go
var (
    caller  = c.name
    format  = "json"
    timeout = 5 * time.Second
)
```

---

## Constants and iota

Start enums at one so the zero value represents invalid/unset:

```go
const (
    Add Operation = iota + 1
    Subtract
    Multiply
)
```

Use zero when the default behavior is desirable (e.g., `LogToStdout`).

> *Consulte IOTA para detalhes.*

---

## Variable Scope

Use if-init to limit scope when the result is only needed for the error check:

```go
if err := os.WriteFile(name, data, 0644); err != nil {
    return err
}
```

Don't reduce scope if it forces deeper nesting or you need the result outside
the `if`. Move constants into functions when only used there.

> *Consulte SCOPE para detalhes.*

---

## Initializing Structs

- **Always use field names** (enforced by `go vet`). Exception: test tables
  with ≤3 fields.
- **Omit zero-value fields** — let Go set defaults.
- **Use `var` for zero-value structs**: `var user User` not `user := User{}`
- **Use `&T{}` over `new(T)`**: `sptr := &T{Name: "bar"}`

> *Consulte STRUCTS para detalhes.*

---

## Composite Literal Formatting

Use field names for external package types. Match closing brace indentation
with the opening line. Omit repeated type names in slice/map literals
(`gofmt -s`).

> *Consulte INITIALIZATION para detalhes.*

> *Consulte LITERALS para detalhes.*

---

## Initializing Maps

| Scenario | Use | Example |
|----------|-----|---------|
| Empty, populated later | `make(map[K]V)` | `m := make(map[string]int)` |
| Nil declaration | `var` | `var m map[string]int` |
| Fixed entries at init | Literal | `m := map[string]int{"a": 1}` |

`make()` visually distinguishes empty-but-initialized from nil. Use size hints
when the count is known.

---

## Raw String Literals

Use backtick strings to avoid hand-escaped characters:

```go
// Bad
wantError := "unknown name:\"test\""

// Good
wantError := `unknown name:"test"`
```

Ideal for regex, SQL, JSON, and multi-line text.

---

## Prefer `any` Over `interface{}`

Go 1.18+: use `any` instead of `interface{}` in all new code.

---

## Avoid Shadowing Built-In Names

Never use predeclared identifiers (`error`, `string`, `len`, `cap`, `append`,
`copy`, `new`, `make`, `close`, `delete`, `panic`, `recover`, `any`, `true`,
`false`, `nil`, `iota`) as names. Use `go vet` to detect.

```go
// Bad — shadows the builtin
var error string

// Good
var errorMessage string
```

> *Consulte SHADOWING para detalhes.*

---

## Related Skills

- **Naming conventions**: See [[go-naming]] when choosing variable names, constant names, or deciding name length by scope
- **Data structures**: See [[go-data-structures]] when choosing between `new` and `make`, or initializing slices and maps
- **Control flow scoping**: See [[go-control-flow]] when using if-init, `:=` redeclaration, or avoiding variable shadowing
- **Capacity hints**: See [[go-performance]] when pre-allocating maps or slices with known sizes

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-control-flow|Control Flow]]
- [[go-data-structures|Data Structures]]
- [[go-naming|Naming]]
- [[go-performance|Performance]]
