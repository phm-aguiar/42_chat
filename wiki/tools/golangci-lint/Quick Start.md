---
title: "Quick Start"
source: "https://golangci.github.io/legacy-v1-doc/welcome/quick-start/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, getting-started]
---
To run golangci-lint execute:

```
golangci-lint run
```

It's an equivalent of executing:

```
golangci-lint run ./...
```

You can choose which directories or files to analyze:

```
golangci-lint run dir1 dir2/...
golangci-lint run file1.go
```

Directories are NOT analyzed recursively. To analyze them recursively append `/...` to their path. It's not possible to mix files and packages/directories, and files must come from the same package.

GolangCI-Lint can be used with zero configuration. By default, the following linters are enabled:

```
$ golangci-lint help linters
Enabled by default linters:
errcheck: Errcheck is a program for checking for unchecked errors in Go code. These unchecked errors can be critical bugs in some cases.
gosimple: Linter for Go source code that specializes in simplifying code. [auto-fix]
govet: Vet examines Go source code and reports suspicious constructs. It is roughly the same as 'go vet' and uses its passes. [auto-fix]
ineffassign: Detects when assignments to existing variables are not used. [fast]
staticcheck: It's a set of rules from staticcheck. It's not the same thing as the staticcheck binary. The author of staticcheck doesn't support or approve the use of staticcheck as a library inside golangci-lint. [auto-fix]
unused: Checks Go code for unused constants, variables, functions and types.
```

Pass `-E/--enable` to enable linter and `-D/--disable` to disable:

```
golangci-lint run --disable-all -E errcheck
```

More information about available linters can be found in the [linters page](https://golangci.github.io/legacy-v1-doc/usage/linters/).

[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/welcome/quick-start.mdx)