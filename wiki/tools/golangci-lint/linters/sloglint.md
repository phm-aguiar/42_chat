---
title: "sloglint"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# sloglint

## rowserrcheck

Checks whether Rows.Err of rows is checked successfully.

```
linters-settings:
  rowserrcheck:
    # database/sql is always checked
    # Default: []
    packages:
      - github.com/jmoiron/sqlx
```


Ensure consistent code style when using log/slog.

```
linters-settings:
  sloglint:
    # Enforce not mixing key-value pairs and attributes.
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#no-mixed-arguments
    # Default: true
    no-mixed-args: false
    # Enforce using key-value pairs only (overrides no-mixed-args, incompatible with attr-only).
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#key-value-pairs-only
    # Default: false
    kv-only: true
    # Enforce using attributes only (overrides no-mixed-args, incompatible with kv-only).
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#attributes-only
    # Default: false
    attr-only: true
    # Enforce not using global loggers.
    # Values:
    # - "": disabled
    # - "all": report all global loggers
    # - "default": report only the default slog logger
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#no-global
    # Default: ""
    no-global: "all"
    # Enforce using methods that accept a context.
    # Values:
    # - "": disabled
    # - "all": report all contextless calls
    # - "scope": report only if a context exists in the scope of the outermost function
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#context-only
    # Default: ""
    context: "all"
    # Enforce using static values for log messages.
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#static-messages
    # Default: false
    static-msg: true
    # Enforce using constants instead of raw keys.
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#no-raw-keys
    # Default: false
    no-raw-keys: true
    # Enforce a single key naming convention.
    # Values: snake, kebab, camel, pascal
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#key-naming-convention
    # Default: ""
    key-naming-case: snake
    # Enforce not using specific keys.
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#forbidden-keys
    # Default: []
    forbidden-keys:
      - time
      - level
      - msg
      - source
      - foo
    # Enforce putting arguments on separate lines.
    # https://github.com/go-simpler/sloglint?tab=readme-ov-file#arguments-on-separate-lines
    # Default: false
    args-on-sep-lines: true
```
