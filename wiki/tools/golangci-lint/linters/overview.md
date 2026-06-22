---
title: "Linters"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# _intro

## Table of Contents

To see a list of supported linters and which linters are enabled/disabled:

```
golangci-lint help linters
```

## Enabled by Default

| Name | Description | Presets | AutoFix | Since |  |
| --- | --- | --- | --- | --- | --- |
| [errcheck](#errcheck "errcheck configuration") | Errcheck is a program for checking for unchecked errors in Go code. These unchecked errors can be critical bugs in some cases. | bugs, error |  | v1.0.0 |  |
| [gosimple](#gosimple "gosimple configuration") | Linter for Go source code that specializes in simplifying code. | style | ✔ | v1.20.0 |  |
| [govet](#govet "govet configuration") | Vet examines Go source code and reports suspicious constructs. It is roughly the same as 'go vet' and uses its passes. | bugs, metalinter | ✔ | v1.0.0 |  |
| [ineffassign](#ineffassign "ineffassign has no configuration") | Detects when assignments to existing variables are not used. | unused |  | v1.0.0 |  |
| [staticcheck](#staticcheck "staticcheck configuration") | It's a set of rules from staticcheck. It's not the same thing as the staticcheck binary. The author of staticcheck doesn't support or approve the use of staticcheck as a library inside golangci-lint. | bugs, metalinter | ✔ | v1.0.0 |  |
| [unused](#unused "unused configuration") | Checks Go code for unused constants, variables, functions and types. | unused |  | v1.20.0 |  |

## Disabled by Default

| Name | Description | Presets | AutoFix | Since |  |
| --- | --- | --- | --- | --- | --- |
| [asasalint](#asasalint "asasalint configuration") | Check for pass \[\]any as any in variadic func(...any). | bugs |  | v1.47.0 |  |
| [asciicheck](#asciicheck "asciicheck has no configuration") | Checks that all code identifiers does not have non-ASCII symbols in the name. | bugs, style |  | v1.26.0 |  |
| [bidichk](#bidichk "bidichk configuration") | Checks for dangerous unicode character sequences. | bugs |  | v1.43.0 |  |
| [bodyclose](#bodyclose "bodyclose has no configuration") | Checks whether HTTP response body is closed successfully. | performance, bugs |  | v1.18.0 |  |
| [canonicalheader](#canonicalheader "canonicalheader has no configuration") | Canonicalheader checks whether net/http.Header uses canonical header. | style | ✔ | v1.58.0 |  |
| [containedctx](#containedctx "containedctx has no configuration") | Containedctx is a linter that detects struct contained context.Context field. | style |  | v1.44.0 |  |
| [contextcheck](#contextcheck "contextcheck has no configuration") | Check whether the function uses a non-inherited context. | bugs |  | v1.43.0 |  |
| [copyloopvar](#copyloopvar "copyloopvar configuration") | A linter detects places where loop variables are copied. | style | ✔ | v1.57.0 |  |
| [cyclop](#cyclop "cyclop configuration") | Checks function and package cyclomatic complexity. | complexity |  | v1.37.0 |  |
| [decorder](#decorder "decorder configuration") | Check declaration order and count of types, constants, variables and functions. | style |  | v1.44.0 |  |
| [depguard](#depguard "depguard configuration") | Go linter that checks if package imports are in a list of acceptable packages. | style, import, module |  | v1.4.0 |  |
| [dogsled](#dogsled "dogsled configuration") | Checks assignments with too many blank identifiers (e.g. x, *,* , \_,:= f()). | style |  | v1.19.0 |  |
| [dupl](#dupl "dupl configuration") | Detects duplicate fragments of code. | style |  | v1.0.0 |  |
| [dupword](#dupword "dupword configuration") | Checks for duplicate words in the source code. | comment | ✔ | v1.50.0 |  |
| [durationcheck](#durationcheck "durationcheck has no configuration") | Check for two durations multiplied together. | bugs |  | v1.37.0 |  |
| [err113](#err113 "err113 has no configuration") | Go linter to check the errors handling expressions. | style, error | ✔ | v1.26.0 |  |
| [errchkjson](#errchkjson "errchkjson configuration") | Checks types passed to the json encoding functions. Reports unsupported types and reports occurrences where the check for the returned error can be omitted. | bugs |  | v1.44.0 |  |
| [errname](#errname "errname has no configuration") | Checks that sentinel errors are prefixed with the `Err` and error types are suffixed with the `Error`. | style |  | v1.42.0 |  |
| [errorlint](#errorlint "errorlint configuration") | Errorlint is a linter for that can be used to find code that will cause problems with the error wrapping scheme introduced in Go 1.13. | bugs, error | ✔ | v1.32.0 |  |
| [exhaustive](#exhaustive "exhaustive configuration") | Check exhaustiveness of enum switch statements. | bugs |  | v1.28.0 |  |
| [exhaustruct](#exhaustruct "exhaustruct configuration") | Checks if all structure fields are initialized. | style, test |  | v1.46.0 |  |
| [exptostd](#exptostd "exptostd has no configuration") | Detects functions from golang.org/x/exp/ that can be replaced by std functions. | style | ✔ | v1.63.0 |  |
| [fatcontext](#fatcontext "fatcontext configuration") | Detects nested contexts in loops and function literals. | performance | ✔ | v1.58.0 |  |
| [forbidigo](#forbidigo "forbidigo configuration") | Forbids identifiers. | style |  | v1.34.0 |  |
| [forcetypeassert](#forcetypeassert "forcetypeassert has no configuration") | Finds forced type assertions. | style |  | v1.38.0 |  |
| [funlen](#funlen "funlen configuration") | Checks for long functions. | complexity |  | v1.18.0 |  |
| [gci](#gci "gci configuration") | Checks if code and import statements are formatted, with additional rules. | format, import | ✔ | v1.30.0 |  |
| [ginkgolinter](#ginkgolinter "ginkgolinter configuration") | Enforces standards of using ginkgo and gomega. | style | ✔ | v1.51.0 |  |
| [gocheckcompilerdirectives](#gocheckcompilerdirectives "gocheckcompilerdirectives has no configuration") | Checks that go compiler directive comments (//go:) are valid. | bugs |  | v1.51.0 |  |
| [gochecknoglobals](#gochecknoglobals "gochecknoglobals has no configuration") | Check that no global variables exist. | style |  | v1.12.0 |  |
| [gochecknoinits](#gochecknoinits "gochecknoinits has no configuration") | Checks that no init functions are present in Go code. | style |  | v1.12.0 |  |
| [gochecksumtype](#gochecksumtype "gochecksumtype configuration") | Run exhaustiveness checks on Go "sum types". | bugs |  | v1.55.0 |  |
| [gocognit](#gocognit "gocognit configuration") | Computes and checks the cognitive complexity of functions. | complexity |  | v1.20.0 |  |
| [goconst](#goconst "goconst configuration") | Finds repeated strings that could be replaced by a constant. | style |  | v1.0.0 |  |
| [gocritic](#gocritic "gocritic configuration") | Provides diagnostics that check for bugs, performance and style issues.   Extensible without recompilation through dynamic rules.   Dynamic rules are written declaratively with AST patterns, filters, report message and optional suggestion. | style, metalinter | ✔ | v1.12.0 |  |
| [gocyclo](#gocyclo "gocyclo configuration") | Computes and checks the cyclomatic complexity of functions. | complexity |  | v1.0.0 |  |
| [godot](#godot "godot configuration") | Check if comments end in a period. | style, comment | ✔ | v1.25.0 |  |
| [godox](#godox "godox configuration") | Detects usage of FIXME, TODO and other keywords inside comments. | style, comment |  | v1.19.0 |  |
| [gofmt](#gofmt "gofmt configuration") | Checks if the code is formatted according to 'gofmt' command. | format | ✔ | v1.0.0 |  |
| [gofumpt](#gofumpt "gofumpt configuration") | Checks if code and import statements are formatted, with additional rules. | format | ✔ | v1.28.0 |  |
| [goheader](#goheader "goheader configuration") | Checks if file header matches to pattern. | style | ✔ | v1.28.0 |  |
| [goimports](#goimports "goimports configuration") | Checks if the code and import statements are formatted according to the 'goimports' command. | format, import | ✔ | v1.20.0 |  |
| [gomoddirectives](#gomoddirectives "gomoddirectives configuration") | Manage the use of 'replace', 'retract', and 'excludes' directives in go.mod. | style, module |  | v1.39.0 |  |
| [gomodguard](#gomodguard "gomodguard configuration") | Allow and block list linter for direct Go module dependencies. This is different from depguard where there are different block types for example version constraints and module recommendations. | style, import, module |  | v1.25.0 |  |
| [goprintffuncname](#goprintffuncname "goprintffuncname has no configuration") | Checks that printf-like functions are named with `f` at the end. | style |  | v1.23.0 |  |
| [gosec](#gosec "gosec configuration") | Inspects source code for security problems. | bugs |  | v1.0.0 |  |
| [gosmopolitan](#gosmopolitan "gosmopolitan configuration") | Report certain i18n/l10n anti-patterns in your Go codebase. | bugs |  | v1.53.0 |  |
| [grouper](#grouper "grouper configuration") | Analyze expression groups. | style |  | v1.44.0 |  |
| [iface](#iface "iface configuration") | Detect the incorrect use of interfaces, helping developers avoid interface pollution. | style | ✔ | v1.62.0 |  |
| [importas](#importas "importas configuration") | Enforces consistent import aliases. | style | ✔ | v1.38.0 |  |
| [inamedparam](#inamedparam "inamedparam configuration") | Reports interfaces with unnamed method parameters. | style |  | v1.55.0 |  |
| [interfacebloat](#interfacebloat "interfacebloat configuration") | A linter that checks the number of methods inside an interface. | style |  | v1.49.0 |  |
| [intrange](#intrange "intrange has no configuration") | Intrange is a linter to find places where for loops could make use of an integer range. | style | ✔ | v1.57.0 |  |
| [ireturn](#ireturn "ireturn configuration") | Accept Interfaces, Return Concrete Types. | style |  | v1.43.0 |  |
| [lll](#lll "lll configuration") | Reports long lines. | style |  | v1.8.0 |  |
| [loggercheck](#loggercheck "loggercheck configuration") | Checks key value pairs for common logger libraries (kitlog,klog,logr,zap). | style, bugs |  | v1.49.0 |  |
|  | Maintidx measures the maintainability index of each function. | complexity |  | v1.44.0 |  |
| [makezero](#makezero "makezero configuration") | Finds slice declarations with non-zero initial length. | style, bugs |  | v1.34.0 |  |
| [mirror](#mirror "mirror has no configuration") | Reports wrong mirror patterns of bytes/strings usage. | style | ✔ | v1.53.0 |  |
| [misspell](#misspell "misspell configuration") | Finds commonly misspelled English words. | style, comment | ✔ | v1.8.0 |  |
| [mnd](#mnd "mnd configuration") | An analyzer to detect magic numbers. | style |  | v1.22.0 |  |
| [musttag](#musttag "musttag configuration") | Enforce field tags in (un)marshaled structs. | style, bugs |  | v1.51.0 |  |
| [nakedret](#nakedret "nakedret configuration") | Checks that functions with naked returns are not longer than a maximum size (can be zero). | style | ✔ | v1.19.0 |  |
| [nestif](#nestif "nestif configuration") | Reports deeply nested if statements. | complexity |  | v1.25.0 |  |
| [nilerr](#nilerr "nilerr has no configuration") | Finds the code that returns nil even if it checks that the error is not nil. | bugs |  | v1.38.0 |  |
| [nilnesserr](#nilnesserr "nilnesserr has no configuration") | Reports constructs that checks for err!= nil, but returns a different nil value error.   Powered by nilness and nilerr. | bugs |  | v1.63.0 |  |
| [nilnil](#nilnil "nilnil configuration") | Checks that there is no simultaneous return of `nil` error and an invalid value. | style |  | v1.43.0 |  |
| [nlreturn](#nlreturn "nlreturn configuration") | Nlreturn checks for a new line before return and branch statements to increase code clarity. | style | ✔ | v1.30.0 |  |
| [noctx](#noctx "noctx has no configuration") | Finds sending http request without context.Context. | performance, bugs |  | v1.28.0 |  |
| [nolintlint](#nolintlint "nolintlint configuration") | Reports ill-formed or insufficient nolint directives. | style | ✔ | v1.26.0 |  |
| [nonamedreturns](#nonamedreturns "nonamedreturns configuration") | Reports all named returns. | style |  | v1.46.0 |  |
| [nosprintfhostport](#nosprintfhostport "nosprintfhostport has no configuration") | Checks for misuse of Sprintf to construct a host with port in a URL. | style |  | v1.46.0 |  |
| [paralleltest](#paralleltest "paralleltest configuration") | Detects missing usage of t.Parallel() method in your Go test. | style, test |  | v1.33.0 |  |
| [perfsprint](#perfsprint "perfsprint configuration") | Checks that fmt.Sprintf can be replaced with a faster alternative. | performance | ✔ | v1.55.0 |  |
| [prealloc](#prealloc "prealloc configuration") | Finds slice declarations that could potentially be pre-allocated. | performance |  | v1.19.0 |  |
| [predeclared](#predeclared "predeclared configuration") | Find code that shadows one of Go's predeclared identifiers. | style |  | v1.35.0 |  |
| [promlinter](#promlinter "promlinter configuration") | Check Prometheus metrics naming via promlint. | style |  | v1.40.0 |  |
| [protogetter](#protogetter "protogetter configuration") | Reports direct reads from proto message fields when getters should be used. | bugs | ✔ | v1.55.0 |  |
| [reassign](#reassign "reassign configuration") | Checks that package variables are not reassigned. | bugs |  | v1.49.0 |  |
| [recvcheck](#recvcheck "recvcheck configuration") | Checks for receiver type consistency. | bugs |  | v1.62.0 |  |
| [revive](#revive "revive configuration") | Fast, configurable, extensible, flexible, and beautiful linter for Go. Drop-in replacement of golint. | style, metalinter | ✔ | v1.37.0 |  |
| [rowserrcheck](#rowserrcheck "rowserrcheck configuration") | Checks whether Rows.Err of rows is checked successfully. | bugs, sql |  | v1.23.0 |  |
| [sloglint](#sloglint "sloglint configuration") | Ensure consistent code style when using log/slog. | style |  | v1.55.0 |  |
| [spancheck](#spancheck "spancheck configuration") | Checks for mistakes with OpenTelemetry/Census spans. | bugs |  | v1.56.0 |  |
| [sqlclosecheck](#sqlclosecheck "sqlclosecheck has no configuration") | Checks that sql.Rows, sql.Stmt, sqlx.NamedStmt, pgx.Query are closed. | bugs, sql |  | v1.28.0 |  |
| [stylecheck](#stylecheck "stylecheck configuration") | Stylecheck is a replacement for golint. | style | ✔ | v1.20.0 |  |
| [tagalign](#tagalign "tagalign configuration") | Check that struct tags are well aligned. | style | ✔ | v1.53.0 |  |
| [tagliatelle](#tagliatelle "tagliatelle configuration") | Checks the struct tags. | style |  | v1.40.0 |  |
| [testableexamples](#testableexamples "testableexamples has no configuration") | Linter checks if examples are testable (have an expected output). | test |  | v1.50.0 |  |
| [testifylint](#testifylint "testifylint configuration") | Checks usage of github.com/stretchr/testify. | test, bugs | ✔ | v1.55.0 |  |
| [testpackage](#testpackage "testpackage configuration") | Linter that makes you use a separate \_test package. | style, test |  | v1.25.0 |  |
| [thelper](#thelper "thelper configuration") | Thelper detects tests helpers which is not start with t.Helper() method. | test |  | v1.34.0 |  |
| [tparallel](#tparallel "tparallel has no configuration") | Tparallel detects inappropriate usage of t.Parallel() method in your Go test codes. | style, test |  | v1.32.0 |  |
| [unconvert](#unconvert "unconvert configuration") | Remove unnecessary type conversions. | style |  | v1.0.0 |  |
| [unparam](#unparam "unparam configuration") | Reports unused function parameters. | unused |  | v1.9.0 |  |
| [usestdlibvars](#usestdlibvars "usestdlibvars configuration") | A linter that detect the possibility to use variables/constants from the Go standard library. | style | ✔ | v1.48.0 |  |
| [usetesting](#usetesting "usetesting configuration") | Reports uses of functions with replacement inside the testing package. | test | ✔ | v1.63.0 |  |
| [varnamelen](#varnamelen "varnamelen configuration") | Checks that the length of a variable's name matches its scope. | style |  | v1.43.0 |  |
| [wastedassign](#wastedassign "wastedassign has no configuration") | Finds wasted assignment statements. | style |  | v1.38.0 |  |
| [whitespace](#whitespace "whitespace configuration") | Whitespace is a linter that checks for unnecessary newlines at the start and end of functions, if, for, etc. | style | ✔ | v1.19.0 |  |
| [wrapcheck](#wrapcheck "wrapcheck configuration") | Checks that errors returned from external packages are wrapped. | style, error |  | v1.32.0 |  |
| [wsl](#wsl "wsl configuration") | Add or remove empty lines. | style | ✔ | v1.20.0 |  |
| [zerologlint](#zerologlint "zerologlint has no configuration") | Detects the wrong usage of `zerolog` that a user forgets to dispatch with `Send` or `Msg`. | bugs |  | v1.53.0 |  |
| [tenv](#tenv "tenv has no configuration") ⚠ | Duplicate feature in another linter. Replaced by usetesting. | test |  | v1.43.0 |  |

## Linters Configuration
