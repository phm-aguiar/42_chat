---
title: "Go Wiki: Code Review Comments"
category: references
tags: [go, code-review, wiki, reference, style-guide]
sources:
  - "wiki/_raw/Go Wiki Go Code Review Comments - The Go Programming Language.md"
summary: "Go Wiki CodeReviewComments — checklist oficial da comunidade Go com comentários comuns feitos durante revisões de código."
provenance:
  extracted: 1.00
  inferred: 0.00
  ambiguous: 0.00
base_confidence: 0.98
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: core
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
---

# Go Wiki: Code Review Comments

> [!tldr] Checklist oficial da comunidade Go com comentários comuns feitos durante revisões de código. Suplemento ao [Effective Go](https://go.dev/doc/effective_go).

**Fonte**: [go.dev/wiki/CodeReviewComments](https://go.dev/wiki/CodeReviewComments)

> **Nota**: Por favor [discuta mudanças](https://go.dev/issue/new?title=wiki%3A+CodeReviewComments+change&body=&labels=Documentation) antes de editar esta página, mesmo mudanças *menores*.

---

## Gofmt

Run [gofmt](https://pkg.go.dev/cmd/gofmt/) on your code to automatically fix the majority of mechanical style issues. Almost all Go code in the wild uses `gofmt`. The rest of this document addresses non-mechanical style points.

An alternative is to use [goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports), a superset of `gofmt` which additionally adds (and removes) import lines as necessary.

---

## Comment Sentences

Comments documenting declarations should be full sentences, even if that seems a little redundant. Comments should begin with the name of the thing being described and end in a period:

```go
// Request represents a request to run a command.
type Request struct { ... }

// Encode writes the JSON encoding of req to w.
func Encode(w io.Writer, req *Request) { ... }
```

---

## Contexts

Values of the `context.Context` type carry security credentials, tracing information, deadlines, and cancellation signals across API and process boundaries. Go programs pass Contexts explicitly along the entire function call chain.

Most functions that use a Context should accept it as their first parameter:

```go
func F(ctx context.Context, /* other arguments */) {}
```

Never store Contexts in struct types; pass them explicitly.

---

## Copying

Be careful about copying structs that contain pointer/slice fields, or have methods with pointer receivers. Use `go vet` to detect inadvertent copies.

---

## Crypto Rand

Use `crypto/rand` for cryptographic randomness, not `math/rand`. `math/rand` is deterministic and seeded.

---

## Declaring Empty Slices

Prefer `var t []string` over `t := []string{}`. The former declares a nil slice, while the latter is non-nil but zero-length. They are functionally equivalent — `len` and `cap` are both zero — but the nil slice is the preferred style.

---

## Doc Comments

All top-level, exported names should have doc comments. Unexported non-trivial types and functions should also have them. See [Comment Sentences](#comment-sentences).

---

## Don't Panic

Use error returns for normal error handling. Only panic for truly exceptional cases, like programmer error or unrecoverable state.

---

## Error Strings

Error strings should not be capitalized (unless beginning with proper nouns or acronyms) and should not end with punctuation:

```go
fmt.Errorf("something bad")        // good
fmt.Errorf("Something bad")        // bad
fmt.Errorf("something bad.")       // bad
```

---

## Examples

When adding a new package, include examples of intended usage: a runnable `Example` function or tests demonstrating a complete call sequence.

---

## Goroutine Lifetimes

When you spawn goroutines, make it clear when — or whether — they exit. Goroutine leaks can cause memory issues.

---

## Handle Errors

Do not discard errors with `_`. Handle them, return them, or (in truly exceptional situations) panic. The `errcheck` tool can help find discarded errors.

---

## Imports

Avoid renaming imports except to avoid a name collision. Good package names should not require renaming. Import groups: standard library first, then a blank line, then everything else.

---

## Import Blank

`import _ "pkg"` should only be used in `main` packages or in tests for side effects.

---

## Import Dot

`import . "pkg"` is discouraged except for generated code and circular dependency workarounds in tests.

---

## In-Band Errors

Don't use special values (-1, "", nil) to signal errors. Use multiple return values with an error or a boolean.

---

## Indent Error Flow

Try to keep the normal code path at a minimal indentation. Handle errors first and return early:

```go
// Good
f, err := os.Open(name)
if err != nil {
    return err
}
d, err := f.Stat()
if err != nil {
    f.Close()
    return err
}
// ... use f, d
```

---

## Initialisms

Words in names that are initialisms or acronyms (URL, HTTP, ID) should have consistent case: `ServeHTTP`, `xmlHTTPRequest`, `appID`.

---

## Interfaces

Define interfaces in the package that consumes values, not in the package that implements types. Return concrete types; accept interfaces.

---

## Line Length

There is no rigid line length limit, but avoid uncomfortably long lines. Break lines naturally.

---

## Mixed Caps

Use `MixedCaps` for exported names and `mixedCaps` for unexported. Do not use underscores.

---

## Named Result Parameters

Use named result parameters when they clarify meaning. Don't use them just to enable naked returns in long functions.

---

## Naked Returns

Naked returns are acceptable only in short functions. In functions of non-trivial length, explicitly return values.

---

## Package Comments

Package comments appear before the package clause. For `package main`, the comment can appear after the package line.

---

## Package Names

No underscores, no mixedCaps. Short, concise. No stuttering (`chubby.File`, not `chubby.ChubbyFile`). Avoid `util`, `common`, `misc`.

---

## Pass Values

Don't pass pointers as function arguments just to save a few bytes. If a function only reads its argument, pass by value.

---

## Receiver Names

Use one or two letter receiver names. Use the first letter of the type (`c` for `Client`). Don't use `this`, `self`, `me`. Be consistent.

---

## Receiver Type

Use pointer receivers if the method needs to mutate the receiver, or if the receiver is large. Use value receivers for small, immutable structs.

---

## Synchronous Functions

Prefer synchronous functions over asynchronous ones. Synchronous functions are easier to understand and test.

---

## Useful Test Failures

Test failure messages should include what was wrong, the inputs, what was actually got, and what was wanted:

```go
if got != tt.want {
    t.Errorf("Foo(%q) = %d; want %d", tt.in, got, tt.want)
}
```

---

## Variable Names

Variable names in Go should be short rather than long. The further a variable is from its declaration, the longer its name should be.

---

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-code-review|Go Code Review Checklist]] — Checklist sistemática
- [[go-documentation|Go Documentation]] — Doc comments e exemplos
- [[go-naming|Go Naming]] — Convenções de nomes
- [[go-error-handling|Go Error Handling]] — Tratamento de erros
- [[go-concurrency|Go Concurrency]] — Concorrência e goroutines
- [[go-interfaces|Go Interfaces]] — Interfaces e composição
- [[go-context|Go Context]] — Contextos e cancelamento
- [[references/go/effective-go|Effective Go]] — Guia canônico
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
