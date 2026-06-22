---
title: "gosec — Go Security Checker"
category: tools
tags: [go, linter, golangci-lint, security, gosec, sast]
sources:
  - "wiki/_raw/securegogosec Go security checker.md"
summary: "gosec inspects source code for security problems by scanning the Go AST and SSA code representation. Includes pattern-based rules, SSA analysis, and taint analysis."
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

# gosec — Go Security Checker

> [!tldr] Inspects source code for security problems by scanning the Go AST and SSA code representation. Essential for services handling user input.

**Repo**: [github.com/securego/gosec](https://github.com/securego/gosec)

---

## Features

- **Pattern-based rules** for detecting common security issues
- **SSA-based analyzers** for type conversions, slice bounds, and crypto issues
- **Taint analysis** for tracking data flow from user input to dangerous functions (SQL injection, command injection, path traversal, SSRF, XSS, log injection, SMTP injection, SSTI, unsafe deserialization, open redirect)

---

## Install

```bash
go install github.com/securego/gosec/v2/cmd/gosec@latest
```

---

## Quick Start

```bash
# Scan all packages in current module
gosec ./...

# Write JSON report
gosec -fmt json -out results.json ./...

# Write SARIF report for code scanning
gosec -fmt sarif -out results.sarif ./...
```

### Exit Codes
- `0` — scan finished without unsuppressed findings/errors
- `1` — at least one unsuppressed finding or processing error
- Use `-no-fail` to always return `0`

---

## Available Rules

| Category | Range | Focus |
|----------|-------|-------|
| General | G1xx | Hardcoded credentials, unsafe usage, HTTP hardening, cookie security |
| Injection | G2xx | Query/template/command construction risks |
| File/Path | G3xx | Permissions, traversal, temp files, archive extraction |
| Crypto/TLS | G4xx | Crypto and TLS weaknesses |
| Blocklisted | G5xx | Blocklisted imports |
| Go-specific | G6xx | Range aliasing, slice bounds |
| Taint | G7xx | SQL injection, command injection, path traversal, SSRF, XSS |

---

## Configuration

```json
{
    "global": {
        "nosec": "enabled",
        "audit": "enabled"
    },
    "exclude-rules": [
        {
            "path": "cmd/.*",
            "rules": ["G204", "G304"]
        },
        {
            "path": "scripts/.*",
            "rules": ["*"]
        }
    ]
}
```

```bash
gosec -conf config.json ./...
```

---

## Annotating Code

Suppress false positives with `#nosec`:

```go
tr := &http.Transport{
    TLSClientConfig: &tls.Config{
        InsecureSkipVerify: true, // #nosec G402 -- Verified safe in dev environment
    },
}
```

---

## GitHub Actions Integration

```yaml
name: Run Gosec
on: [push, pull_request]
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: securego/gosec@master
        with:
          args: ./...
```

---

## golangci-lint Integration

Enable via `.golangci.yml`:
```yaml
linters:
  enable:
    - gosec
```

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-defensive|Go Defensive]] — Programação defensiva em Go
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
