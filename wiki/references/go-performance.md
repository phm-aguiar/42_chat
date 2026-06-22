---
title: "Go Performance"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-performance/SKILL.md"
summary: "Go Performance: boas práticas e regras de estilo Go destiladas de Uber Style Guide, Google Style Guide, Go Wiki CodeReviewComments."
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

# Go Performance Patterns


---

## Prefer strconv over fmt

When converting primitives to/from strings, `strconv` is faster than `fmt`:

```go
s := strconv.Itoa(rand.Int()) // ~2x faster than fmt.Sprint()
```

| Approach | Speed | Allocations |
|----------|-------|-------------|
| `fmt.Sprint` | 143 ns/op | 2 allocs/op |
| `strconv.Itoa` | 64.2 ns/op | 1 allocs/op |

> *Consulte STRING-OPTIMIZATION para detalhes.*

---

## Avoid Repeated String-to-Byte Conversions

Convert a fixed string to `[]byte` once outside the loop:

```go
data := []byte("Hello world")
for i := 0; i < b.N; i++ {
    w.Write(data) // ~7x faster than []byte("...") each iteration
}
```

> *Consulte STRING-OPTIMIZATION para detalhes.*

---

## Prefer Specifying Container Capacity

Specify container capacity where possible to allocate memory up front. This minimizes subsequent allocations from copying and resizing as elements are added.

### Map Capacity Hints

Provide capacity hints when initializing maps with `make()`:

```go
m := make(map[string]os.DirEntry, len(files))
```

**Note**: Unlike slices, map capacity hints do not guarantee complete preemptive allocation—they approximate the number of hashmap buckets required.

### Slice Capacity

Provide capacity hints when initializing slices with `make()`, particularly when appending:

```go
data := make([]int, 0, size)
```

Unlike maps, slice capacity is **not a hint**—the compiler allocates exactly that much memory. Subsequent `append()` operations incur zero allocations until capacity is reached.

| Approach | Time (100M iterations) |
|----------|------------------------|
| No capacity | 2.48s |
| With capacity | 0.21s |

The capacity version is **~12x faster** due to zero reallocations during append.

---

## Pass Values

Don't pass pointers as function arguments just to save a few bytes. If a function refers to its argument `x` only as `*x` throughout, then the argument shouldn't be a pointer.

```go
func process(s string) { // not *string — strings are small fixed-size headers
    fmt.Println(s)
}
```

**Common pass-by-value types**: `string`, `io.Reader`, small structs.

**Exceptions**:
- Large structs where copying is expensive
- Small structs that might grow in the future

---

## String Concatenation

Choose the right strategy based on complexity:

| Method | Best For |
|--------|----------|
| `+` | Few strings, simple concat |
| `fmt.Sprintf` | Formatted output with mixed types |
| `strings.Builder` | Loop/piecemeal construction |
| `strings.Join` | Joining a slice |
| Backtick literal | Constant multi-line text |

> *Consulte STRING-OPTIMIZATION para detalhes.*

---

## Benchmarking and Profiling

Always measure before and after optimizing. Use Go's built-in benchmark framework and profiling tools.

```bash
go test -bench=. -benchmem -count=10 ./...
```

> *Consulte BENCHMARKS para detalhes.*

> **Validation**: After applying optimizations, run `bash scripts/bench-compare.sh` to measure the actual impact. Only keep optimizations with measurable improvement.

---

## Quick Reference

| Pattern | Bad | Good | Improvement |
|---------|-----|------|-------------|
| Int to string | `fmt.Sprint(n)` | `strconv.Itoa(n)` | ~2x faster |
| Repeated `[]byte` | `[]byte("str")` in loop | Convert once outside | ~7x faster |
| Map initialization | `make(map[K]V)` | `make(map[K]V, size)` | Fewer allocs |
| Slice initialization | `make([]T, 0)` | `make([]T, 0, cap)` | ~12x faster |
| Small fixed-size args | `*string`, `*io.Reader` | `string`, `io.Reader` | No indirection |
| Simple string join | `s1 + " " + s2` | (already good) | Use `+` for few strings |
| Loop string build | Repeated `+=` | `strings.Builder` | O(n) vs O(n²) |

---

## Related Skills

- **Data structures**: See [[go-data-structures]] when choosing between slices, maps, and arrays, or understanding allocation semantics
- **Declaration patterns**: See [[go-declarations]] when using `make` with capacity hints or initializing maps and slices
- **Concurrency**: See [[go-concurrency]] when parallelizing work across goroutines or using sync.Pool for buffer reuse
- **Style principles**: See [[go-style-core]] when deciding whether an optimization is worth the readability cost

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-concurrency|Concurrency]]
- [[go-data-structures|Data Structures]]
- [[go-declarations|Declarations]]
- [[go-style-core|Style Core]]
