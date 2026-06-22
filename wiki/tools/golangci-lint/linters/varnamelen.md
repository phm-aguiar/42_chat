---
title: "varnamelen"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# varnamelen

## testpackage

Linter that makes you use a separate \_test package.

```
linters-settings:
  testpackage:
    # Regexp pattern to skip files.
    # Default: "(export|internal)_test\\.go"
    skip-regexp: (export|internal)_test\.go
    # List of packages that don't end with _test that tests are allowed to be in.
    # Default: "main"
    allow-packages:
      - example
      - main
```

## thelper

Thelper detects tests helpers which is not start with t.Helper() method.

```
linters-settings:
  thelper:
    test:
      # Check *testing.T is first param (or after context.Context) of helper function.
      # Default: true
      first: false
      # Check *testing.T param has name t.
      # Default: true
      name: false
      # Check t.Helper() begins helper function.
      # Default: true
      begin: false
    benchmark:
      # Check *testing.B is first param (or after context.Context) of helper function.
      # Default: true
      first: false
      # Check *testing.B param has name b.
      # Default: true
      name: false
      # Check b.Helper() begins helper function.
      # Default: true
      begin: false
    tb:
      # Check *testing.TB is first param (or after context.Context) of helper function.
      # Default: true
      first: false
      # Check *testing.TB param has name tb.
      # Default: true
      name: false
      # Check tb.Helper() begins helper function.
      # Default: true
      begin: false
    fuzz:
      # Check *testing.F is first param (or after context.Context) of helper function.
      # Default: true
      first: false
      # Check *testing.F param has name f.
      # Default: true
      name: false
      # Check f.Helper() begins helper function.
      # Default: true
      begin: false
```

## usestdlibvars

A linter that detect the possibility to use variables/constants from the Go standard library.

```
linters-settings:
  usestdlibvars:
    # Suggest the use of http.MethodXX.
    # Default: true
    http-method: false
    # Suggest the use of http.StatusXX.
    # Default: true
    http-status-code: false
    # Suggest the use of time.Weekday.String().
    # Default: true
    time-weekday: true
    # Suggest the use of time.Month.String().
    # Default: false
    time-month: true
    # Suggest the use of time.Layout.
    # Default: false
    time-layout: true
    # Suggest the use of crypto.Hash.String().
    # Default: false
    crypto-hash: true
    # Suggest the use of rpc.DefaultXXPath.
    # Default: false
    default-rpc-path: true
    # Suggest the use of sql.LevelXX.String().
    # Default: false
    sql-isolation-level: true
    # Suggest the use of tls.SignatureScheme.String().
    # Default: false
    tls-signature-scheme: true
    # Suggest the use of constant.Kind.String().
    # Default: false
    constant-kind: true
```

## usetesting

Reports uses of functions with replacement inside the testing package.

```
linters-settings:
  usetesting:
    # Enable/disable \`os.CreateTemp("", ...)\` detections.
    # Default: true
    os-create-temp: false
    # Enable/disable \`os.MkdirTemp()\` detections.
    # Default: true
    os-mkdir-temp: false
    # Enable/disable \`os.Setenv()\` detections.
    # Default: true
    os-setenv: false
    # Enable/disable \`os.TempDir()\` detections.
    # Default: false
    os-temp-dir: true
    # Enable/disable \`os.Chdir()\` detections.
    # Disabled if Go < 1.24.
    # Default: true
    os-chdir: false
    # Enable/disable \`context.Background()\` detections.
    # Disabled if Go < 1.24.
    # Default: true
    context-background: false
    # Enable/disable \`context.TODO()\` detections.
    # Disabled if Go < 1.24.
    # Default: true
    context-todo: false
```

## unconvert

Remove unnecessary type conversions.

```
linters-settings:
  unconvert:
    # Remove conversions that force intermediate rounding.
    # Default: false
    fast-math: true
    # Be more conservative (experimental).
    # Default: false
    safe: true
```

## unparam

Reports unused function parameters.

```
linters-settings:
  unparam:
    # Inspect exported functions.
    #
    # Set to true if no external program/library imports your code.
    # XXX: if you enable this setting, unparam will report a lot of false-positives in text editors:
    # if it's called for subdir of a project it can't find external interfaces. All text editor integrations
    # with golangci-lint call it on a directory with the changed file.
    #
    # Default: false
    check-exported: true
```

## unused

Checks Go code for unused constants, variables, functions and types.

```
linters-settings:
  unused:
    # Mark all struct fields that have been written to as used.
    # Default: true
    field-writes-are-uses: false
    # Treat IncDec statement (e.g. \`i++\` or \`i--\`) as both read and write operation instead of just write.
    # Default: false
    post-statements-are-reads: true
    # Mark all exported fields as used.
    # default: true
    exported-fields-are-used: false
    # Mark all function parameters as used.
    # default: true
    parameters-are-used: false
    # Mark all local variables as used.
    # default: true
    local-variables-are-used: false
    # Mark all identifiers inside generated files as used.
    # Default: true
    generated-is-used: false
```


Checks that the length of a variable's name matches its scope.

```
linters-settings:
  varnamelen:
    # The longest distance, in source lines, that is being considered a "small scope".
    # Variables used in at most this many lines will be ignored.
    # Default: 5
    max-distance: 6
    # The minimum length of a variable's name that is considered "long".
    # Variable names that are at least this long will be ignored.
    # Default: 3
    min-name-length: 2
    # Check method receivers.
    # Default: false
    check-receiver: true
    # Check named return values.
    # Default: false
    check-return: true
    # Check type parameters.
    # Default: false
    check-type-param: true
    # Ignore "ok" variables that hold the bool return value of a type assertion.
    # Default: false
    ignore-type-assert-ok: true
    # Ignore "ok" variables that hold the bool return value of a map index.
    # Default: false
    ignore-map-index-ok: true
    # Ignore "ok" variables that hold the bool return value of a channel receive.
    # Default: false
    ignore-chan-recv-ok: true
    # Optional list of variable names that should be ignored completely.
    # Default: []
    ignore-names:
      - err
    # Optional list of variable declarations that should be ignored completely.
    # Entries must be in one of the following forms (see below for examples):
    # - for variables, parameters, named return values, method receivers, or type parameters:
    #   <name> <type>  (<type> can also be a pointer/slice/map/chan/...)
    # - for constants: const <name>
    #
    # Default: []
    ignore-decls:
      - c echo.Context
      - t testing.T
      - f *foo.Bar
      - e error
      - i int
      - const C
      - T any
      - m map[string]int
```
