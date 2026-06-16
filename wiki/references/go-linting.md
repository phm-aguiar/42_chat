---
title: "Go Linting"
category: references
tags: [go, style-guide, coding-standards]
sources:
  - "wiki/_raw/go-linting/SKILL.md"
summary: "Go Linting: boas práticas e regras de estilo Go destiladas de Uber Style Guide."
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

# Go Linting

## Core Principle

More important than any "blessed" set of linters: **lint consistently across a codebase**.

Consistent linting helps catch common issues and establishes a high bar for code quality without being unnecessarily prescriptive.

---

## Setup Procedure

1. Create `.golangci.yml` using the configuration below
2. Run `golangci-lint run ./...`
3. If errors appear, fix them category by category (formatting first, then vet, then style)
4. Re-run until clean

---

## Minimum Recommended Linters

These linters catch the most common issues while maintaining a high quality bar:

| Linter | Purpose |
|--------|---------|
| [errcheck](https://github.com/kisielk/errcheck) | Ensure errors are handled |
| [goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) | Format code and manage imports |
| [revive](https://github.com/mgechev/revive) | Common style mistakes (modern replacement for golint) |
| [govet](https://pkg.go.dev/cmd/vet) | Analyze code for common mistakes |
| [staticcheck](https://staticcheck.dev) | Various static analysis checks |

> **Note**: `revive` is the modern, faster successor to the now-deprecated `golint`.

---

## Lint Runner: golangci-lint

Use [golangci-lint](https://github.com/golangci/golangci-lint) as your lint runner. See the [example .golangci.yml](https://github.com/uber-go/guide/blob/master/.golangci.yml) from uber-go/guide.

---

## Example Configuration

> See `assets/golangci.yml` when creating a new `.golangci.yml` or comparing your existing config against a recommended baseline.

Create `.golangci.yml` in your project root:

```yaml
linters:
  enable:
    - errcheck
    - goimports
    - revive
    - govet
    - staticcheck

linters-settings:
  goimports:
    local-prefixes: github.com/your-org/your-repo
  revive:
    rules:
      - name: blank-imports
      - name: context-as-argument
      - name: error-return
      - name: error-strings
      - name: exported

run:
  timeout: 5m
```

### Running

```bash
# Install
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# Run all linters
golangci-lint run

# Run on specific paths
golangci-lint run ./pkg/...
```

---

## Additional Recommended Linters

Beyond the minimum set, consider these for production projects:

| Linter | Purpose | When to enable |
|--------|---------|----------------|
| [gosec](https://github.com/securego/gosec) | Security vulnerability detection | Always for services handling user input |
| [ineffassign](https://github.com/gordonklaus/ineffassign) | Detect ineffectual assignments | Always — catches dead code |
| [misspell](https://github.com/client9/misspell) | Correct common misspellings in comments/strings | Always |
| [gocyclo](https://github.com/fzipp/gocyclo) | Cyclomatic complexity threshold | When functions exceed ~15 complexity |
| [exhaustive](https://github.com/nishanths/exhaustive) | Ensure switch covers all enum values | When using iota enums |
| [bodyclose](https://github.com/timakin/bodyclose) | Detect unclosed HTTP response bodies | Always for HTTP client code |

---

## Nolint Directives

When suppressing a lint finding, always explain why:

```go
//nolint:errcheck // fire-and-forget logging; error is not actionable
_ = logger.Sync()
```

Rules:
- Use `//nolint:lintername` — never bare `//nolint`
- Place the comment on the same line as the finding
- Include a justification after `//`

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint
on: [push, pull_request]
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - uses: golangci/golangci-lint-action@v6
        with:
          version: latest
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit
golangci-lint run --new-from-rev=HEAD~1
```

Use `--new-from-rev` to lint only changed code, keeping the feedback loop fast.

---


---

## Quick Reference

| Task | Command/Action |
|------|----------------|
| Install golangci-lint | `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` |
| Run linters | `golangci-lint run` |
| Run on path | `golangci-lint run ./pkg/...` |
| Config file | `.golangci.yml` in project root |
| CI integration | Run `golangci-lint run` in pipeline |
| Nolint directives | `//nolint:name // reason` — never bare `//nolint` |
| CI integration | Use `golangci/golangci-lint-action` for GitHub Actions |
| Pre-commit | `golangci-lint run --new-from-rev=HEAD~1` |

### Linter Selection Guidelines

| When you need... | Use |
|------------------|-----|
| Error handling coverage | errcheck |
| Import formatting | goimports |
| Style consistency | revive |
| Bug detection | govet, staticcheck |
| All of the above | golangci-lint with config |

---

## Related Skills

- **Style foundations**: See [[go-style-core]] when resolving style questions that linters enforce (formatting, nesting, naming)
- **Code review**: See [[go-code-review]] when combining linter output with a manual review checklist
- **Error handling**: See [[go-error-handling]] when errcheck flags unhandled errors and you need to decide how to handle them
- **Testing**: See [[go-testing]] when running linters alongside tests in CI pipelines

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-code-review|Code Review]]
- [[go-error-handling|Error Handling]]
- [[go-style-core|Style Core]]
- [[go-testing|Testing]]
