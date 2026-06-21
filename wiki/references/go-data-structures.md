---
title: "Go Data Structures"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-data-structures/SKILL.md"
summary: "Go Data Structures: boas práticas e regras de estilo Go destiladas de Effective Go, Google Style Guide, Uber Style Guide, Go Wiki CodeReviewComments."
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

# Go Data Structures

---

## Choosing a Data Structure

```
What do you need?
├─ Ordered collection of items
│  ├─ Fixed size known at compile time → Array [N]T
│  └─ Dynamic size → Slice []T
│     ├─ Know approximate size? → make([]T, 0, capacity)
│     └─ Unknown size or nil-safe for JSON? → var s []T (nil)
├─ Key-value lookup
│  └─ Map map[K]V
│     ├─ Know approximate size? → make(map[K]V, capacity)
│     └─ Need a set? → map[T]struct{} (zero-size values)
└─ Need to pass to a function?
   └─ Copy at the boundary if the caller might mutate it
```

> **When this skill does NOT apply**: For concurrent access to data structures (mutexes, atomic operations), see [[go-concurrency]]. For defensive copying at API boundaries, see [[go-defensive]]. For pre-sizing capacity for performance, see [[go-performance]].

---

## Slices

### The append Function

**Always assign the result** — the underlying array may change:

```go
x := []int{1, 2, 3}
x = append(x, 4, 5, 6)

// Append a slice to a slice
x = append(x, y...)  // Note the ...
```

### Two-Dimensional Slices

**Independent inner slices** (can grow/shrink independently):

```go
picture := make([][]uint8, YSize)
for i := range picture {
    picture[i] = make([]uint8, XSize)
}
```

**Single allocation** (more efficient for fixed sizes):

```go
picture := make([][]uint8, YSize)
pixels := make([]uint8, XSize*YSize)
for i := range picture {
    picture[i], pixels = pixels[:XSize], pixels[XSize:]
}
```

> *Consulte SLICES para detalhes.*

### Declaring Empty Slices

Prefer nil slices over empty literals:

```go
// Good: nil slice
var t []string

// Avoid: non-nil but zero-length
t := []string{}
```

Both have `len` and `cap` of zero, but the nil slice is the preferred style.

**Exception for JSON**: A nil slice encodes to `null`, while `[]string{}`
encodes to `[]`. Use non-nil when you need a JSON array.

When designing interfaces, avoid distinguishing between nil and non-nil
zero-length slices.

---

## Maps

### Implementing a Set

Use `map[T]bool` — idiomatic and reads naturally:

```go
attended := map[string]bool{"Ann": true, "Joe": true}
if attended[person] {  // false if not in map
    fmt.Println(person, "was at the meeting")
}
```

---

## Copying

Be careful when copying a struct from another package. If the type has methods
on its pointer type (`*T`), copying the value can cause aliasing bugs.

**General rule:** Do not copy a value of type `T` if its methods are associated
with the pointer type `*T`. This applies to `bytes.Buffer`, `sync.Mutex`,
`sync.WaitGroup`, and types containing them.

```go
// Bad: copying a mutex
var mu sync.Mutex
mu2 := mu  // almost always a bug

// Good: pass by pointer
func increment(sc *SafeCounter) {
    sc.mu.Lock()
    sc.count++
    sc.mu.Unlock()
}
```

---

## Quick Reference

| Topic | Key Point |
|-------|-----------|
| Slices | Always assign `append` result; `nil` slice preferred over `[]T{}` |
| Sets | `map[T]bool` is idiomatic |
| Copying | Don't copy `T` if methods are on `*T`; beware aliasing |

## Related Skills

- **Defensive copying**: See [[go-defensive]] when copying slices or maps at API boundaries to prevent mutation
- **Capacity hints**: See [[go-performance]] when pre-sizing slices or maps for known workloads
- **Iteration patterns**: See [[go-control-flow]] when using range loops over slices, maps, or channels
- **Declaration style**: See [[go-declarations]] when choosing between `new`, `make`, `var`, and composite literals

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-concurrency|Concurrency]]
- [[go-control-flow|Control Flow]]
- [[go-declarations|Declarations]]
- [[go-defensive|Defensive]]
- [[go-performance|Performance]]
