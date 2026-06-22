---
title: "Go Testing"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-testing/SKILL.md"
summary: "Go Testing: boas práticas e regras de estilo Go destiladas de Google Style Guide, Uber Style Guide."
provenance:
  extracted: 0.35
  inferred: 0.60
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-16"
tier: supporting
created: "2026-06-16T00:00:00Z"
rag_score: 0.48
updated: "2026-06-16T00:00:00Z"
---

# Go Testing

## Quick Reference

| Pattern | Use When |
|---------|----------|
| `t.Error` | Default — report failure, keep running |
| `t.Fatal` | Setup failed or continuing is meaningless |
| `cmp.Diff` | Comparing structs, slices, maps, protos |
| Table-driven | Many cases share identical logic |
| Subtests | Need filtering, parallel execution, or naming |
| `t.Helper()` | Any test helper function (call as first statement) |
| `t.Cleanup()` | Teardown in helpers instead of defer |

---

## Useful Test Failures

> **Normative**: Test failures must be diagnosable without reading the test
> source.

Every failure message must include: function name, inputs, actual (got), and
expected (want). Use the format `YourFunc(%v) = %v, want %v`.

```go
// Good:
t.Errorf("Add(2, 3) = %d, want %d", got, 5)

// Bad: Missing function name and inputs
t.Errorf("got %d, want %d", got, 5)
```

Always print got before want: `got %v, want %v` — never reversed.

---

## No Assertion Libraries

> **Normative**: Do not use assertion libraries. Use `cmp.Diff` for complex
> comparisons.

```go
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("GetPost() mismatch (-want +got):\n%s", diff)
}
```

For protocol buffers, add `protocmp.Transform()` as a cmp option. Always
include the direction key `(-want +got)` in diff messages. Avoid comparing
JSON/serialized output — compare semantically instead.

> *Consulte TEST-HELPERS para detalhes.*
> custom comparison helpers or domain-specific test utilities.

---

## t.Error vs t.Fatal

> **Normative**: Use `t.Error` by default to report all failures in one run.
> Use `t.Fatal` only when continuing is impossible.

**Choose `t.Fatal` when:**
- Setup fails (DB connection, file load)
- The next assertion depends on the previous one succeeding (e.g., decode after
  encode)

**Never call `t.Fatal`/`t.FailNow` from a goroutine** other than the test
goroutine — use `t.Error` instead.

> *Consulte TEST-HELPERS para detalhes.*
> helpers that need to choose between t.Error and t.Fatal, or for detailed
> examples of both.

---

## Table-Driven Tests

> See `assets/table-test-template.go` when scaffolding a new table-driven test and need the canonical struct, loop, and subtest layout.

> **Advisory**: Use table-driven tests when many cases share identical logic.

**Use table tests when:** all cases run the same code path with no conditional
setup, mocking, or assertions. A single `shouldErr` bool is acceptable.

**Don't use table tests when:** cases need complex setup, conditional mocking,
or multiple branches — write separate test functions instead.

**Key rules:**
- Use field names when cases span many lines or have same-type adjacent fields
- Include inputs in failure messages — never identify rows by index

> *Consulte TABLE-DRIVEN-TESTS para detalhes.*
> when writing table-driven tests, subtests, or parallel tests.

> **Validation**: After generating or modifying tests, run `go test -run TestXxx -v` to verify the tests compile and pass. Fix any compilation errors before proceeding.

---

## Test Helpers

> **Normative**: Test helpers must call `t.Helper()` first and use `t.Cleanup()`
> for teardown.

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("Could not open database: %v", err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

> *Consulte TEST-HELPERS para detalhes.*
> test helpers, cleanup functions, or custom comparison utilities.

---

## Test Error Semantics

> **Advisory**: Test error semantics, not error message strings.

```go
// Bad: Brittle string comparison
if err.Error() != "invalid input" { ... }

// Good: Semantic check
if !errors.Is(err, ErrInvalidInput) { ... }
```

For simple presence checks when specific semantics don't matter:

```go
if gotErr := err != nil; gotErr != tt.wantErr {
    t.Errorf("f(%v) error = %v, want error presence = %t", tt.input, err, tt.wantErr)
}
```

---

## Test Organization

> *Consulte TEST-ORGANIZATION para detalhes.*
> working with test doubles, choosing test package placement, or scoping test
> setup.

> *Consulte VALIDATION-APIS para detalhes.*
> designing reusable test validation functions.

---

## Integration Testing

> *Consulte INTEGRATION para detalhes.*
> TestMain, acceptance tests, or tests that need real HTTP/RPC transports.

---


---

## Related Skills

- **Error testing**: See [[go-error-handling]] when testing error semantics with `errors.Is`/`errors.As` or sentinel errors
- **Interface mocking**: See [[go-interfaces]] when creating test doubles by implementing interfaces at the consumer side
- **Naming test functions**: See [[go-naming]] when naming test functions, subtests, or test helper utilities
- **Linter integration**: See [[go-linting]] when running linters alongside tests in CI or pre-commit hooks

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-error-handling|Error Handling]]
- [[go-interfaces|Interfaces]]
- [[go-linting|Linting]]
- [[go-naming|Naming]]

## See Also
- [[references/go-unit-tests|Go Unit Tests]] — Unit testing patterns and practices
