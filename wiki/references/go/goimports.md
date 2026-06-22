---
title: "goimports — Go Import Manager"
category: references
tags: [go, tools, goimports, formatter, imports]
sources:
  - "wiki/_raw/goimports command - golang.orgxtoolscmdgoimports.md"
summary: "Command goimports updates your Go import lines, adding missing ones and removing unreferenced ones. Also formats code in the same style as gofmt."
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

# goimports

> [!tldr] Command goimports updates your Go import lines, adding missing ones and removing unreferenced ones. Superset of `gofmt`.

**Fonte**: [pkg.go.dev/golang.org/x/tools/cmd/goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports)

---

## Installation

```bash
go install golang.org/x/tools/cmd/goimports@latest
```

---

## Overview

In addition to fixing imports, goimports also formats your code in the same style as `gofmt` so it can be used as a replacement for your editor's gofmt-on-save hook.

---

## Editor Integration

### Emacs

Make sure you have the latest [go-mode.el](https://github.com/dominikh/go-mode.el). Then in your `.emacs`:

```elisp
(setq gofmt-command "goimports")
(add-hook 'before-save-hook 'gofmt-before-save)
```

### Vim

Set `gofmt_command` to `goimports`.

### GoSublime

Follow the steps described [here](http://michaelwhatcott.com/gosublime-goimports/).

---

## Usage with golangci-lint

`goimports` is one of the recommended linters in the minimum set:

```yaml
# .golangci.yml
linters:
  enable:
    - goimports

linters-settings:
  goimports:
    local-prefixes: github.com/your-org/your-repo
```

---

## Ver Também

- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
