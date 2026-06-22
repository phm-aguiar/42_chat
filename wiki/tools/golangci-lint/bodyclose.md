---
title: "bodyclose — HTTP Response Body Checker"
category: tools
tags: [go, linter, golangci-lint, http, bodyclose]
sources:
  - "wiki/_raw/timakinbodyclose Analyzer checks whether HTTP response body is closed and a re-use of TCP connection is not blocked..md"
summary: "bodyclose — static analysis tool which checks whether res.Body is correctly closed in Go HTTP clients."
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

# bodyclose

> [!tldr] Static analysis tool which checks whether `res.Body` is correctly closed. Essential for HTTP client code to prevent TCP connection leaks.

**Repo**: [github.com/timakin/bodyclose](https://github.com/timakin/bodyclose)

---

## Install

```bash
go install github.com/timakin/bodyclose@latest
```

---

## How to Use

Run with `go vet` (Go ≥ 1.12):

```bash
go vet -vettool=$(which bodyclose) ./...
```

### Options

Enable additional checks with `-check-consumption` to verify response bodies are consumed:

```bash
go vet -vettool=$(which bodyclose) -check-consumption ./...
```

---

## Problem Detected

`bodyclose` validates whether `*net/http.Response` of HTTP request calls method `Body.Close()`:

**Wrong:**
```go
resp, err := http.Get("http://example.com/")
if err != nil {
    // handle error
}
body, err := io.ReadAll(resp.Body)
// BUG: resp.Body.Close() never called
```

**Correct:**
```go
resp, err := http.Get("http://example.com/")
if err != nil {
    // handle error
}
defer resp.Body.Close()
body, err := io.ReadAll(resp.Body)
```

If you forget to close the body, the HTTP client cannot re-use a persistent TCP connection for subsequent "keep-alive" requests.

---

## Supported Consumption Patterns

When `-check-consumption` is enabled:
- `io.Copy(io.Discard, resp.Body)`
- `io.ReadAll(resp.Body)`
- `json.NewDecoder(resp.Body)`
- `bufio.NewScanner(resp.Body)`
- `bufio.NewReader(resp.Body)`

Custom consumption patterns may trigger false positives. Use `//nolint:bodyclose` to suppress.

---

## Ver Também
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
