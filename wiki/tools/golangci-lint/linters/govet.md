---
title: "govet"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# govet

## gosmopolitan

Report certain i18n/l10n anti-patterns in your Go codebase.

```
linters-settings:
  gosmopolitan:
    # Allow and ignore \`time.Local\` usages.
    #
    # Default: false
    allow-time-local: true
    # List of fully qualified names in the \`full/pkg/path.name\` form, to act as "i18n escape hatches".
    # String literals inside call-like expressions to, or struct literals of those names,
    # are exempt from the writing system check.
    #
    # Default: []
    escape-hatches:
      - 'github.com/nicksnyder/go-i18n/v2/i18n.Message'
      - 'example.com/your/project/i18n/markers.Raw'
      - 'example.com/your/project/i18n/markers.OK'
      - 'example.com/your/project/i18n/markers.TODO'
      - 'command-line-arguments.Simple'
    # Ignore test files.
    #
    # Default: true
    ignore-tests: false
    # List of Unicode scripts to watch for any usage in string literals.
    # https://pkg.go.dev/unicode#pkg-variables
    #
    # Default: ["Han"]
    watch-for-scripts:
      - Devanagari
      - Han
      - Hangul
      - Hiragana
      - Katakana
```


Vet examines Go source code and reports suspicious constructs. It is roughly the same as 'go vet' and uses its passes.

```
linters-settings:
  govet:
    # Disable all analyzers.
    # Default: false
    disable-all: true
    # Enable analyzers by name.
    # (in addition to default:
    #   appends, asmdecl, assign, atomic, bools, buildtag, cgocall, composites, copylocks, defers, directive, errorsas,
    #   framepointer, httpresponse, ifaceassert, loopclosure, lostcancel, nilfunc, printf, shift, sigchanyzer, slog,
    #   stdmethods, stringintconv, structtag, testinggoroutine, tests, timeformat, unmarshal, unreachable, unsafeptr,
    #   unusedresult
    # ).
    # Run \`GL_DEBUG=govet golangci-lint run --enable=govet\` to see default, all available analyzers, and enabled analyzers.
    # Default: []
    enable:
      # Check for missing values after append.
      - appends
      # Report mismatches between assembly files and Go declarations.
      - asmdecl
      # Check for useless assignments.
      - assign
      # Check for common mistakes using the sync/atomic package.
      - atomic
      # Check for non-64-bits-aligned arguments to sync/atomic functions.
      - atomicalign
      # Check for common mistakes involving boolean operators.
      - bools
      # Check //go:build and // +build directives.
      - buildtag
      # Detect some violations of the cgo pointer passing rules.
      - cgocall
      # Check for unkeyed composite literals.
      - composites
      # Check for locks erroneously passed by value.
      - copylocks
      # Check for calls of reflect.DeepEqual on error values.
      - deepequalerrors
      # Report common mistakes in defer statements.
      - defers
      # Check Go toolchain directives such as //go:debug.
      - directive
      # Report passing non-pointer or non-error values to errors.As.
      - errorsas
      # Find structs that would use less memory if their fields were sorted.
      - fieldalignment
      # Find calls to a particular function.
      - findcall
      # Report assembly that clobbers the frame pointer before saving it.
      - framepointer
      # Check for mistakes using HTTP responses.
      - httpresponse
      # Detect impossible interface-to-interface type assertions.
      - ifaceassert
      # Check references to loop variables from within nested functions.
      - loopclosure
      # Check cancel func returned by context.WithCancel is called.
      - lostcancel
      # Check for useless comparisons between functions and nil.
      - nilfunc
      # Check for redundant or impossible nil comparisons.
      - nilness
      # Check consistency of Printf format strings and arguments.
      - printf
      # Check for comparing reflect.Value values with == or reflect.DeepEqual.
      - reflectvaluecompare
      # Check for possible unintended shadowing of variables.
      - shadow
      # Check for shifts that equal or exceed the width of the integer.
      - shift
      # Check for unbuffered channel of os.Signal.
      - sigchanyzer
      # Check for invalid structured logging calls.
      - slog
      # Check the argument type of sort.Slice.
      - sortslice
      # Check signature of methods of well-known interfaces.
      - stdmethods
      # Report uses of too-new standard library symbols.
      - stdversion
      # Check for string(int) conversions.
      - stringintconv
      # Check that struct field tags conform to reflect.StructTag.Get.
      - structtag
      # Report calls to (*testing.T).Fatal from goroutines started by a test.
      - testinggoroutine
      # Check for common mistaken usages of tests and examples.
      - tests
      # Check for calls of (time.Time).Format or time.Parse with 2006-02-01.
      - timeformat
      # Report passing non-pointer or non-interface values to unmarshal.
      - unmarshal
      # Check for unreachable code.
      - unreachable
      # Check for invalid conversions of uintptr to unsafe.Pointer.
      - unsafeptr
      # Check for unused results of calls to some functions.
      - unusedresult
      # Checks for unused writes.
      - unusedwrite
      # Check for misuses of sync.WaitGroup.
      - waitgroup
    # Enable all analyzers.
    # Default: false
    enable-all: true
    # Disable analyzers by name.
    # (in addition to default
    #   atomicalign, deepequalerrors, fieldalignment, findcall, nilness, reflectvaluecompare, shadow, sortslice,
    #   timeformat, unusedwrite
    # ).
    # Run \`GL_DEBUG=govet golangci-lint run --enable=govet\` to see default, all available analyzers, and enabled analyzers.
    # Default: []
    disable:
      - appends
      - asmdecl
      - assign
      - atomic
      - atomicalign
      - bools
      - buildtag
      - cgocall
      - composites
      - copylocks
      - deepequalerrors
      - defers
      - directive
      - errorsas
      - fieldalignment
      - findcall
      - framepointer
      - httpresponse
      - ifaceassert
      - loopclosure
      - lostcancel
      - nilfunc
      - nilness
      - printf
      - reflectvaluecompare
      - shadow
      - shift
      - sigchanyzer
      - slog
      - sortslice
      - stdmethods
      - stdversion
      - stringintconv
      - structtag
      - testinggoroutine
      - tests
      - timeformat
      - unmarshal
      - unreachable
      - unsafeptr
      - unusedresult
      - unusedwrite
      - waitgroup
    # Settings per analyzer.
    settings:
      # Analyzer name, run \`go tool vet help\` to see all analyzers.
      printf:
        # Comma-separated list of print function names to check (in addition to default, see \`go tool vet help printf\`).
        # Default: []
        funcs:
          - (github.com/golangci/golangci-lint/pkg/logutils.Log).Infof
          - (github.com/golangci/golangci-lint/pkg/logutils.Log).Warnf
          - (github.com/golangci/golangci-lint/pkg/logutils.Log).Errorf
          - (github.com/golangci/golangci-lint/pkg/logutils.Log).Fatalf
      shadow:
        # Whether to be strict about shadowing; can be noisy.
        # Default: false
        strict: true
      unusedresult:
        # Comma-separated list of functions whose results must be used
        # (in addition to default:
        #   context.WithCancel, context.WithDeadline, context.WithTimeout, context.WithValue, errors.New, fmt.Errorf,
        #   fmt.Sprint, fmt.Sprintf, sort.Reverse
        # ).
        # Default: []
        funcs:
          - pkg.MyFunc
        # Comma-separated list of names of methods of type func() string whose results must be used
        # (in addition to default Error,String)
        # Default: []
        stringmethods:
          - MyMethod
```
