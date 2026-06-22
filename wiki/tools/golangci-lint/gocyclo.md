---
title: "gocyclo — Cyclomatic Complexity Calculator"
category: tools
tags: [go, linter, golangci-lint, complexity, gocyclo]
sources:
  - "wiki/_raw/fzippgocyclo Calculate cyclomatic complexities of functions in Go source code..md"
summary: "Gocyclo calculates cyclomatic complexities of functions in Go source code. Identifies code needing refactoring."
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

# gocyclo

> [!tldr] Calculates [cyclomatic complexities](https://en.wikipedia.org/wiki/Cyclomatic_complexity) of functions in Go source code. Higher complexity = more test cases needed, potentially harder to understand.

**Repo**: [github.com/fzipp/gocyclo](https://github.com/fzipp/gocyclo)

---

## Calculation Rules

```
1 is the base complexity of a function
+1 for each 'if', 'for', 'case', '&&' or '||'
```

---

## Install

```bash
go install github.com/fzipp/gocyclo/cmd/gocyclo@latest
```

---

## Usage

```
gocyclo [flags] <Go file or directory> ...

Flags:
    -over N         show functions with complexity > N only
    -top N          show the top N most complex functions only
    -avg, -avg-short  show the average complexity over all functions
    -ignore REGEX   exclude files matching the given regular expression

Output: <complexity> <package> <function> <file:line:column>
```

---

## Examples

```bash
gocyclo .
gocyclo -top 10 src/
gocyclo -over 25 docker
gocyclo -avg .
gocyclo -over 3 -avg gocyclo/
```

Example output:
```
9 gocyclo (*complexityVisitor).Visit complexity.go:30:1
8 main main cmd/gocyclo/main.go:53:1
7 gocyclo (*fileAnalyzer).analyzeDecl analyze.go:96:1
4 gocyclo Analyze analyze.go:24:1
Average: 2.72
```

---

## Ignoring Individual Functions

```go
//gocyclo:ignore
func f1() {
    // ...
}

//gocyclo:ignore
var f2 = func() {
    // ...
}
```

---

## Recommended Threshold

Functions exceeding ~15 cyclomatic complexity should be considered for refactoring. The `-over` flag helps identify these.

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-functions|Go Functions]] — Organização e boas práticas de funções
