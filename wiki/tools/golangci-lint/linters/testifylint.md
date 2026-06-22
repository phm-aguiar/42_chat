---
title: "testifylint"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# testifylint

## tenv

Duplicate feature in another linter. Replaced by usetesting.

```
linters-settings:
  tenv:
    # The option \`all\` will run against whole test files (\`_test.go\`) regardless of method/function signatures.
    # Otherwise, only methods that take \`*testing.T\`, \`*testing.B\`, and \`testing.TB\` as arguments are checked.
    # Default: false
    all: false
```


Checks usage of github.com/stretchr/testify.

```
linters-settings:
  testifylint:
    # Enable all checkers (https://github.com/Antonboom/testifylint#checkers).
    # Default: false
    enable-all: true
    # Disable checkers by name
    # (in addition to default
    #   suite-thelper
    # ).
    disable:
      - blank-import
      - bool-compare
      - compares
      - contains
      - empty
      - encoded-compare
      - error-is-as
      - error-nil
      - expected-actual
      - float-compare
      - formatter
      - go-require
      - len
      - negative-positive
      - nil-compare
      - regexp
      - require-error
      - suite-broken-parallel
      - suite-dont-use-pkg
      - suite-extra-assert-call
      - suite-subtest-run
      - suite-thelper
      - useless-assert
    # Disable all checkers (https://github.com/Antonboom/testifylint#checkers).
    # Default: false
    disable-all: true
    # Enable checkers by name
    # (in addition to default
    #   blank-import, bool-compare, compares, contains, empty, encoded-compare, error-is-as, error-nil, expected-actual,
    #   go-require, float-compare, formatter, len, negative-positive, nil-compare, regexp, require-error,
    #   suite-broken-parallel, suite-dont-use-pkg, suite-extra-assert-call, suite-subtest-run, useless-assert
    # ).
    enable:
      - blank-import
      - bool-compare
      - compares
      - contains
      - empty
      - encoded-compare
      - error-is-as
      - error-nil
      - expected-actual
      - float-compare
      - formatter
      - go-require
      - len
      - negative-positive
      - nil-compare
      - regexp
      - require-error
      - suite-broken-parallel
      - suite-dont-use-pkg
      - suite-extra-assert-call
      - suite-subtest-run
      - suite-thelper
      - useless-assert
    bool-compare:
      # To ignore user defined types (over builtin bool).
      # Default: false
      ignore-custom-types: true
    expected-actual:
      # Regexp for expected variable name.
      # Default: (^(exp(ected)?|want(ed)?)([A-Z]\w*)?$)|(^(\w*[a-z])?(Exp(ected)?|Want(ed)?)$)
      pattern: ^expected
    formatter:
      # To enable go vet's printf checks.
      # Default: true
      check-format-string: false
      # To require f-assertions (e.g. \`assert.Equalf\`) if format string is used, even if there are no variable-length
      # variables, i.e. it requires \`require.NoErrorf\` for both these cases:
      # - require.NoErrorf(t, err, "unexpected error")
      # - require.NoErrorf(t, err, "unexpected error for sid: %v", sid)
      # To understand this behavior, please read the
      # https://github.com/Antonboom/testifylint?tab=readme-ov-file#historical-reference-of-formatter.
      # Default: false
      require-f-funcs: true
    go-require:
      # To ignore HTTP handlers (like http.HandlerFunc).
      # Default: false
      ignore-http-handlers: true
    require-error:
      # Regexp for assertions to analyze. If defined, then only matched error assertions will be reported.
      # Default: ""
      fn-pattern: ^(Errorf?|NoErrorf?)$
    suite-extra-assert-call:
      # To require or remove extra Assert() call?
      # Default: remove
      mode: require
```
