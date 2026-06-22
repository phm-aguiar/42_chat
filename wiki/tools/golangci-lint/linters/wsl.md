---
title: "wsl"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# wsl

## whitespace

Whitespace is a linter that checks for unnecessary newlines at the start and end of functions, if, for, etc.

```
linters-settings:
  whitespace:
    # Enforces newlines (or comments) after every multi-line if statement.
    # Default: false
    multi-if: true
    # Enforces newlines (or comments) after every multi-line function signature.
    # Default: false
    multi-func: true
```

## wrapcheck

Checks that errors returned from external packages are wrapped.

```
linters-settings:
  wrapcheck:
    # An array of strings specifying additional substrings of signatures to ignore.
    # Unlike 'ignoreSigs', this option extends the default set (or the set specified in 'ignoreSigs') without replacing it entirely.
    # This allows you to add specific signatures to the ignore list
    # while retaining the defaults or any items in 'ignoreSigs'.
    # Default: []
    extra-ignore-sigs:
      - .CustomError(
      - .SpecificWrap(
    # An array of strings that specify substrings of signatures to ignore.
    # If this set, it will override the default set of ignored signatures.
    # See https://github.com/tomarrell/wrapcheck#configuration for more information.
    # Default: [".Errorf(", "errors.New(", "errors.Unwrap(", "errors.Join(", ".Wrap(", ".Wrapf(", ".WithMessage(", ".WithMessagef(", ".WithStack("]
    ignoreSigs:
      - .Errorf(
      - errors.New(
      - errors.Unwrap(
      - errors.Join(
      - .Wrap(
      - .Wrapf(
      - .WithMessage(
      - .WithMessagef(
      - .WithStack(
    # An array of strings that specify regular expressions of signatures to ignore.
    # Default: []
    ignoreSigRegexps:
      - \.New.*Error\(
    # An array of strings that specify globs of packages to ignore.
    # Default: []
    ignorePackageGlobs:
      - encoding/*
      - github.com/pkg/*
    # An array of strings that specify regular expressions of interfaces to ignore.
    # Default: []
    ignoreInterfaceRegexps:
      - ^(?i)c(?-i)ach(ing|e)
```


Add or remove empty lines.

```
linters-settings:
  wsl:
    # Do strict checking when assigning from append (x = append(x, y)).
    # If this is set to true - the append call must append either a variable
    # assigned, called or used on the line above.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#strict-append
    # Default: true
    strict-append: false
    # Allows assignments to be cuddled with variables used in calls on
    # line above and calls to be cuddled with assignments of variables
    # used in call on line above.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-assign-and-call
    # Default: true
    allow-assign-and-call: false
    # Allows assignments to be cuddled with anything.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-assign-and-anything
    # Default: false
    allow-assign-and-anything: true
    # Allows cuddling to assignments even if they span over multiple lines.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-multiline-assign
    # Default: true
    allow-multiline-assign: false
    # If the number of lines in a case block is equal to or lager than this number,
    # the case *must* end white a newline.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#force-case-trailing-whitespace
    # Default: 0
    force-case-trailing-whitespace: 1
    # Allow blocks to end with comments.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-trailing-comment
    # Default: false
    allow-trailing-comment: true
    # Allow multiple comments in the beginning of a block separated with newline.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-separated-leading-comment
    # Default: false
    allow-separated-leading-comment: true
    # Allow multiple var/declaration statements to be cuddled.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#allow-cuddle-declarations
    # Default: false
    allow-cuddle-declarations: true
    # A list of call idents that everything can be cuddled with.
    # Defaults: [ "Lock", "RLock" ]
    allow-cuddle-with-calls: ["Foo", "Bar"]
    # AllowCuddleWithRHS is a list of right hand side variables that is allowed
    # to be cuddled with anything.
    # Defaults: [ "Unlock", "RUnlock" ]
    allow-cuddle-with-rhs: ["Foo", "Bar"]
    # Causes an error when an If statement that checks an error variable doesn't
    # cuddle with the assignment of that variable.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#force-err-cuddling
    # Default: false
    force-err-cuddling: true
    # When force-err-cuddling is enabled this is a list of names
    # used for error variables to check for in the conditional.
    # Default: [ "err" ]
    error-variable-names: ["foo"]
    # Causes an error if a short declaration (:=) cuddles with anything other than
    # another short declaration.
    # This logic overrides force-err-cuddling among others.
    # https://github.com/bombsimon/wsl/blob/HEAD/doc/configuration.md#force-short-decl-cuddling
    # Default: false
    force-short-decl-cuddling: true
```
