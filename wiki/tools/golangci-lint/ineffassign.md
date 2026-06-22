---
title: "ineffassign — Ineffectual Assignment Detector"
category: tools
tags: [go, linter, golangci-lint, ineffassign, dead-code]
sources:
  - "wiki/_raw/gordonklausineffassign Detect ineffectual assignments in Go code..md"
summary: "Detect ineffectual assignments in Go code. An assignment is ineffectual if the variable assigned is not thereafter used."
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

# ineffassign

> [!tldr] Detect ineffectual assignments in Go code. An assignment is ineffectual if the variable assigned is not thereafter used. Catches dead code and logic errors.

**Repo**: [github.com/gordonklaus/ineffassign](https://github.com/gordonklaus/ineffassign)

---

## Limitations

This tool misses some cases because it does not consider any type information in its analysis. For example, assignments to struct fields are never marked as ineffectual. It should, however, never give any false positives.

---

## Install

```bash
go install github.com/gordonklaus/ineffassign@latest
```

---

## Usage

```bash
ineffassign ./...
```

Analyzes all packages beneath the current directory.

---

## Exit Codes

- `1` — Problems found in checked files
- `3` — Invalid arguments

---

## golangci-lint Integration

Enable via `.golangci.yml`:
```yaml
linters:
  enable:
    - ineffassign
```

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-performance|Go Performance]] — Otimização
