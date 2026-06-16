---
title: "Go Defensive"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-defensive/SKILL.md"
summary: "Go Defensive: boas práticas e regras de estilo Go destiladas de Effective Go, Uber Style Guide, Go Wiki CodeReviewComments."
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

# Go Defensive Programming Patterns

## Defensive Checklist Priority

When hardening code at API boundaries, check in this order:

```
Reviewing an API boundary?
├─ 1. Error handling     → Return errors; don't panic (see go-error-handling)
├─ 2. Input validation   → Copy slices/maps received from callers
├─ 3. Output safety      → Copy slices/maps before returning to callers
├─ 4. Resource cleanup   → Use defer for Close/Unlock/Cancel
├─ 5. Interface checks   → var _ Interface = (*Type)(nil) for compile-time verification
├─ 6. Time correctness   → Use time.Time and time.Duration, not int/float
├─ 7. Enum safety        → Start iota at 1 so zero-value is invalid
└─ 8. Crypto safety      → crypto/rand for keys, never math/rand
```

---

## Quick Reference

| Pattern | Rule | Details |
|---------|------|---------|
| Boundary copies | Copy slices/maps on receive and return | [BOUNDARY-COPYING.md](references/BOUNDARY-COPYING.md) |
| Defer cleanup | `defer f.Close()` right after `os.Open` | Below |
| Interface check | `var _ I = (*T)(nil)` | See go-interfaces |
| Time types | `time.Time` / `time.Duration`, never raw int | [TIME-ENUMS-TAGS.md](references/TIME-ENUMS-TAGS.md) |
| Enum start | `iota + 1` so zero = invalid | Below |
| Crypto rand | `crypto/rand` for keys, never `math/rand` | Below |
| Must functions | Only at init; panic on failure | [MUST-FUNCTIONS.md](references/MUST-FUNCTIONS.md) |
| Panic/recover | Never expose panics across packages | [PANIC-RECOVER.md](references/PANIC-RECOVER.md) |
| Mutable globals | Replace with dependency injection | Below |

---

## Verify Interface Compliance

Use compile-time checks to verify interface implementation. See **go-interfaces**: Interface Satisfaction Checks for the full pattern.

```go
var _ http.Handler = (*Handler)(nil)
```

## Copy Slices and Maps at Boundaries

Slices and maps contain pointers to underlying data. Copy at API boundaries to prevent unintended modifications.

```go
// Receiving: copy incoming slice
d.trips = make([]Trip, len(trips))
copy(d.trips, trips)

// Returning: copy map before returning
result := make(map[string]int, len(s.counters))
for k, v := range s.counters { result[k] = v }
```

> *Consulte BOUNDARY-COPYING para detalhes.*

## Defer to Clean Up

Use `defer` to clean up resources (files, locks). Avoids missed cleanup on multiple return paths.

```go
p.Lock()
defer p.Unlock()

if p.count < 10 {
  return p.count
}
p.count++
return p.count
```

Defer overhead is negligible. Place `defer f.Close()` immediately after
`os.Open` for clarity. Arguments to deferred functions are evaluated when
`defer` executes, not when the function runs. Multiple defers execute in
LIFO order.

## Struct Field Tags

> **Advisory**: Always add explicit field tags to structs that are marshaled or unmarshaled.

```go
type User struct {
    Name  string `json:"name"  yaml:"name"`
    Email string `json:"email" yaml:"email"`
}
```

Field tags are a **serialization contract** — renaming a struct field without
updating the tag silently breaks wire compatibility. Treat tags as part of
the public API for any type that crosses a serialization boundary.

## Start Enums at One

Start enums at non-zero to distinguish uninitialized from valid values.

```go
const (
  Add Operation = iota + 1  // Add=1, zero value = uninitialized
  Subtract
  Multiply
)
```

**Exception**: When zero is the sensible default (e.g., `LogToStdout = iota`).

## Time, Struct Tags, and Embedding

> *Consulte TIME-ENUMS-TAGS para detalhes.*

## Avoid Mutable Globals

Inject dependencies instead of mutating package-level variables. This makes
code testable without global save/restore.

```go
type signer struct {
  now func() time.Time  // injected; tests replace with fixed time
}

func newSigner() *signer {
  return &signer{now: time.Now}
}
```

> *Consulte GLOBAL-STATE para detalhes.*

## Crypto Rand

Do not use `math/rand` or `math/rand/v2` to generate keys — this is a
**security concern**. Time-seeded generators have predictable output.

```go
import "crypto/rand"

func Key() string { return rand.Text() }
```

For text output, use `crypto/rand.Text` directly, or encode random bytes
with `encoding/hex` or `encoding/base64`.

---

## Panic and Recover

Use `panic` only for truly unrecoverable situations. Library functions
should avoid panic.

```go
func safelyDo(work *Work) {
    defer func() {
        if err := recover(); err != nil {
            log.Println("work failed:", err)
        }
    }()
    do(work)
}
```

**Key rules:**
- Never expose panics across package boundaries — always convert to errors
- Acceptable to panic in `init()` if a library truly cannot set itself up
- Use recover to isolate panics in server goroutine handlers

> *Consulte PANIC-RECOVER para detalhes.*

## Must Functions

`Must` functions panic on error — use them **only** during program
initialization where failure means the program cannot run.

```go
var validID = regexp.MustCompile(`^[a-z][a-z0-9-]{0,62}$`)
var tmpl = template.Must(template.ParseFiles("index.html"))
```

> *Consulte MUST-FUNCTIONS para detalhes.*

---

## Related Skills

- **Error handling**: See [[go-error-handling]] when choosing between returning errors and panicking, or wrapping errors at boundaries
- **Concurrency safety**: See [[go-concurrency]] when protecting shared state with mutexes, atomics, or channels
- **Interface checks**: See [[go-interfaces]] when adding compile-time interface satisfaction checks (`var _ I = (*T)(nil)`)
- **Data structure copying**: See [[go-data-structures]] when working with slice/map internals or pointer aliasing

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-concurrency|Concurrency]]
- [[go-data-structures|Data Structures]]
- [[go-error-handling|Error Handling]]
- [[go-interfaces|Interfaces]]
