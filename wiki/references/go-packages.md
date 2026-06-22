---
title: "Go Packages"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-packages/SKILL.md"
summary: "Go Packages: boas práticas e regras de estilo Go destiladas de Google Style Guide, Uber Style Guide, Go Wiki CodeReviewComments."
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

# Go Packages and Imports

> **When this skill does NOT apply**: For naming individual identifiers within a package, see [[go-naming]]. For organizing functions within a single file, see [[go-functions]]. For configuring linters that enforce import rules, see [[go-linting]].

## Package Organization

### Avoid Util Packages

Package names should describe what the package provides. Avoid generic names
like `util`, `helper`, `common` — they obscure meaning and cause import
conflicts.

```go
// Good: Meaningful package names
db := spannertest.NewDatabaseFromFile(...)
_, err := f.Seek(0, io.SeekStart)

// Bad: Vague names obscure meaning
db := test.NewDatabaseFromFile(...)
_, err := f.Seek(0, common.SeekStart)
```

Generic names can be used as *part* of a name (e.g., `stringutil`) but should
not be the entire package name.

### Package Size

| Question | Action |
|----------|--------|
| Can you describe its purpose in one sentence? | No → split by responsibility |
| Do files never share unexported symbols? | Those files could be separate packages |
| Distinct user groups use different parts? | Split along user boundaries |
| Godoc page overwhelming? | Split to improve discoverability |

**Do NOT split** just because a file is long, to create single-type packages, or
if it would create circular dependencies.

> *Consulte PACKAGE-SIZE para detalhes.*

---

## Imports

Imports are organized in groups separated by blank lines. Standard library
packages always come first. Use
[goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) to manage this
automatically.

```go
import (
    "fmt"
    "os"

    "github.com/foo/bar"
    "rsc.io/goversion/version"
)
```

**Quick rules:**

| Rule | Guidance |
|------|----------|
| Grouping | stdlib first, then external. Extended: stdlib → other → protos → side-effects |
| Renaming | Avoid unless collision. Rename the most local import. Proto packages get `pb` suffix |
| Blank imports (`import _`) | Only in `main` packages or tests |
| Dot imports (`import .`) | Never use, except for circular-dependency test files |

> *Consulte IMPORTS para detalhes.*

---

## Avoid init()

Avoid `init()` where possible. When unavoidable, it must be:

1. Completely deterministic
2. Independent of other `init()` ordering
3. Free of environment state (env vars, working dir, args)
4. Free of I/O (filesystem, network, system calls)

**Acceptable uses**: complex expressions that can't be single assignments,
pluggable hooks (e.g., `database/sql` dialects), deterministic precomputation.

> *Consulte PACKAGE-SIZE para detalhes.*

---

## Exit in Main

Call `os.Exit` or `log.Fatal*` **only in `main()`**. All other functions should
return errors.

**Why**: Non-obvious control flow, untestable, `defer` statements skipped.

**Best practice**: Use the `run()` pattern — extract logic into
`func run() error`, call from `main()` with a single exit point:

```go
func main() {
    if err := run(); err != nil {
        log.Fatal(err)
    }
}
```

> *Consulte PACKAGE-SIZE para detalhes.*

---

## Command-Line Flags

> **Advisory**: Define flags only in `package main`.

- Flag names use `snake_case`: `--output_dir` not `--outputDir`
- Libraries should accept configuration as parameters, not read flags directly —
  this keeps them testable and reusable
- Prefer the standard `flag` package; use `pflag` only when POSIX conventions
  (double-dash, single-char shortcuts) are required

```go
// Good: Flag in main, passed as parameter to library
func main() {
    outputDir := flag.String("output_dir", ".", "directory for output files")
    flag.Parse()
    if err := mylib.Generate(*outputDir); err != nil {
        log.Fatal(err)
    }
}
```

---

## Related Skills

- **Package naming**: See [[go-naming]] when choosing package names, avoiding stuttering, or naming exported symbols
- **Error handling across packages**: See [[go-error-handling]] when wrapping errors at package boundaries with `%w` vs `%v`
- **Import linting**: See [[go-linting]] when configuring goimports local-prefixes or enforcing import grouping
- **Global state**: See [[go-defensive]] when replacing `init()` with explicit initialization or avoiding mutable globals

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-defensive|Defensive]]
- [[go-error-handling|Error Handling]]
- [[go-functions|Functions]]
- [[go-linting|Linting]]
- [[go-naming|Naming]]
