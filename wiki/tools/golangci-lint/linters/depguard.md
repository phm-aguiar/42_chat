---
title: "depguard"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# depguard

## asasalint

Check for pass \[\]any as any in variadic func(...any).

```
linters-settings:
  asasalint:
    # To specify a set of function names to exclude.
    # The values are merged with the builtin exclusions.
    # The builtin exclusions can be disabled by setting \`use-builtin-exclusions\` to \`false\`.
    # Default: ["^(fmt|log|logger|t|)\.(Print|Fprint|Sprint|Fatal|Panic|Error|Warn|Warning|Info|Debug|Log)(|f|ln)$"]
    exclude:
      - Append
      - \.Wrapf
    # To enable/disable the asasalint builtin exclusions of function names.
    # See the default value of \`exclude\` to get the builtin exclusions.
    # Default: true
    use-builtin-exclusions: false
    # Ignore *_test.go files.
    # Default: false
    ignore-test: true
```

## bidichk

Checks for dangerous unicode character sequences.

```
linters-settings:
  bidichk:
    # The following configurations check for all mentioned invisible Unicode runes.
    # All runes are enabled by default.
    left-to-right-embedding: false
    right-to-left-embedding: false
    pop-directional-formatting: false
    left-to-right-override: false
    right-to-left-override: false
    left-to-right-isolate: false
    right-to-left-isolate: false
    first-strong-isolate: false
    pop-directional-isolate: false
```

## copyloopvar

A linter detects places where loop variables are copied.

```
linters-settings:
  copyloopvar:
    # Check all assigning the loop variable to another variable.
    # Default: false
    check-alias: true
```

## cyclop

Checks function and package cyclomatic complexity.

```
linters-settings:
  cyclop:
    # The maximal code complexity to report.
    # Default: 10
    max-complexity: 10
    # The maximal average package complexity.
    # If it's higher than 0.0 (float) the check is enabled
    # Default: 0.0
    package-average: 0.5
    # Should ignore tests.
    # Default: false
    skip-tests: true
```

## decorder

Check declaration order and count of types, constants, variables and functions.

```
linters-settings:
  decorder:
    # Required order of \`type\`, \`const\`, \`var\` and \`func\` declarations inside a file.
    # Default: types before constants before variables before functions.
    dec-order:
      - type
      - const
      - var
      - func
    # If true, underscore vars (vars with "_" as the name) will be ignored at all checks
    # Default: false (underscore vars are not ignored)
    ignore-underscore-vars: false
    # If true, order of declarations is not checked at all.
    # Default: true (disabled)
    disable-dec-order-check: false
    # If true, \`init\` func can be anywhere in file (does not have to be declared before all other functions).
    # Default: true (disabled)
    disable-init-func-first-check: false
    # If true, multiple global \`type\`, \`const\` and \`var\` declarations are allowed.
    # Default: true (disabled)
    disable-dec-num-check: false
    # If true, type declarations will be ignored for dec num check
    # Default: false (type statements are not ignored)
    disable-type-dec-num-check: false
    # If true, const declarations will be ignored for dec num check
    # Default: false (const statements are not ignored)
    disable-const-dec-num-check: false
    # If true, var declarations will be ignored for dec num check
    # Default: false (var statements are not ignored)
    disable-var-dec-num-check: false
```


Go linter that checks if package imports are in a list of acceptable packages.

```
linters-settings:
  depguard:
    # Rules to apply.
    #
    # Variables:
    # - File Variables
    #   Use an exclamation mark \`!\` to negate a variable.
    #   Example: \`!$test\` matches any file that is not a go test file.
    #
    #   \`$all\` - matches all go files
    #   \`$test\` - matches all go test files
    #
    # - Package Variables
    #
    #   \`$gostd\` - matches all of go's standard library (Pulled from \`GOROOT\`)
    #
    # Default (applies if no custom rules are defined): Only allow $gostd in all files.
    rules:
      # Name of a rule.
      main:
        # Defines package matching behavior. Available modes:
        # - \`original\`: allowed if it doesn't match the deny list and either matches the allow list or the allow list is empty.
        # - \`strict\`: allowed only if it matches the allow list and either doesn't match the deny list or the allow rule is more specific (longer) than the deny rule.
        # - \`lax\`: allowed if it doesn't match the deny list or the allow rule is more specific (longer) than the deny rule.
        # Default: "original"
        list-mode: lax
        # List of file globs that will match this list of settings to compare against.
        # Default: $all
        files:
          - "!**/*_a _file.go"
        # List of allowed packages.
        # Entries can be a variable (starting with $), a string prefix, or an exact match (if ending with $).
        # Default: []
        allow:
          - $gostd
          - github.com/OpenPeeDeeP
        # List of packages that are not allowed.
        # Entries can be a variable (starting with $), a string prefix, or an exact match (if ending with $).
        # Default: []
        deny:
          - pkg: "math/rand$"
            desc: use math/rand/v2
          - pkg: "github.com/sirupsen/logrus"
            desc: not allowed
          - pkg: "github.com/pkg/errors"
            desc: Should be replaced by standard lib errors package
```
