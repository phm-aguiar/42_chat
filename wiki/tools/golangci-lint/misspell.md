---
title: "misspell — Spell Checker for Source Code"
category: tools
tags: [go, linter, golangci-lint, misspell, spelling]
sources:
  - "wiki/_raw/client9misspell Correct commonly misspelled English words in source files.md"
summary: "Correct commonly misspelled English words in source files — fast, parallel spell checker for Go, text, and markdown."
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

# misspell

> [!tldr] Correct commonly misspelled English words in source files. 100-1000x faster than other spelling correctors. For `.go` files, only checks spelling in comments.

**Repo**: [github.com/client9/misspell](https://github.com/client9/misspell)

---

## Install

```bash
curl -L -o ./install-misspell.sh https://git.io/misspell
sh ./install-misspell.sh

# Or via Go:
go install github.com/client9/misspell/cmd/misspell@latest
```

---

## Usage

```bash
$ misspell all.html your.txt important.md files.go
your.txt:42:10 found "langauge" a misspelling of "language"
```

### Key Flags

| Flag | Description |
|------|-------------|
| `-w` | Overwrite file with corrections |
| `-error` | Exit with 2 if misspelling found |
| `-locale US\|UK` | Correct for American or British English |
| `-source go\|text\|auto` | Source mode (go = only check comments) |
| `-i "list"` | Ignore specific corrections (comma-separated) |
| `-f template` | Custom output format (CSV, SQLite, Go template) |

---

## Auto-Correction

```bash
misspell -w all.html your.txt important.md files.go
```

Files are rewritten only if misspellings are found.

---

## British vs American English

```bash
# Convert to American spelling
misspell -locale US important.txt

# Convert to British spelling
echo "My favorite color is blue" | misspell -locale UK
```

---

## For Go Source Files

When checking `.go` files, misspell only checks spelling in **comments**. Variable names using camelCase per [Effective Go naming conventions](https://golang.org/doc/effective_go.html#mixed-caps) won't trigger false positives.

---

## golangci-lint Integration

Enable via `.golangci.yml`:
```yaml
linters:
  enable:
    - misspell
```

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-documentation|Go Documentation]] — Doc comments
