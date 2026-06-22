---
title: "gosimple"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# gosimple

## gocyclo

Computes and checks the cyclomatic complexity of functions.

```
linters-settings:
  gocyclo:
    # Minimal code complexity to report.
    # Default: 30 (but we recommend 10-20)
    min-complexity: 10
```

## godot

Check if comments end in a period.

```
linters-settings:
  godot:
    # Comments to be checked: \`declarations\`, \`toplevel\`, \`noinline\` or \`all\`.
    # Default: declarations
    scope: toplevel
    # List of regexps for excluding particular comment lines from check.
    # Default: []
    exclude:
      # Exclude todo and fixme comments.
      - "^fixme:"
      - "^todo:"
    # Check that each sentence ends with a period.
    # Default: true
    period: false
    # Check that each sentence starts with a capital letter.
    # Default: false
    capital: true
```

## godox

Detects usage of FIXME, TODO and other keywords inside comments.

```
linters-settings:
  godox:
    # Report any comments starting with keywords, this is useful for TODO or FIXME comments that
    # might be left in the code accidentally and should be resolved before merging.
    # Default: ["TODO", "BUG", "FIXME"]
    keywords:
      - NOTE
      - OPTIMIZE # marks code that should be optimized before merging
      - HACK # marks hack-around that should be removed before merging
```

## gofmt

Checks if the code is formatted according to 'gofmt' command.

```
linters-settings:
  gofmt:
    # Simplify code: gofmt with \`-s\` option.
    # Default: true
    simplify: false
    # Apply the rewrite rules to the source before reformatting.
    # https://pkg.go.dev/cmd/gofmt
    # Default: []
    rewrite-rules:
      - pattern: 'interface{}'
        replacement: 'any'
      - pattern: 'a[b:len(a)]'
        replacement: 'a[b:]'
```

## gofumpt

Checks if code and import statements are formatted, with additional rules.

```
linters-settings:
  gofumpt:
    # Module path which contains the source code being formatted.
    # Default: ""
    module-path: github.com/org/project
    # Choose whether to use the extra rules.
    # Default: false
    extra-rules: true
```

## goheader

Checks if file header matches to pattern.

```
linters-settings:
  goheader:
    # Supports two types 'const\` and \`regexp\`.
    # Values can be used recursively.
    # Default: {}
    values:
      const:
        # Define here const type values in format k:v.
        # For example:
        COMPANY: MY COMPANY
      regexp:
        # Define here regexp type values.
        # for example:
    # The template used for checking.
    # Put here copyright header template for source code files
    # Note: {{ YEAR }} is a builtin value that returns the year relative to the current machine time.
    # Default: ""
    template: |-
      SPDX-License-Identifier: Apache-2.0

      Licensed under the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at:

        http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
      See the License for the specific language governing permissions and
      limitations under the License.
    # As alternative of directive 'template', you may put the path to file with the template source.
    # Useful if you need to load the template from a specific file.
    # Default: ""
    template-path: /path/to/my/template.tmpl
```

## goimports

Checks if the code and import statements are formatted according to the 'goimports' command.

```
linters-settings:
  goimports:
    # A comma-separated list of prefixes, which, if set, checks import paths
    # with the given prefixes are grouped after 3rd-party packages.
    # Default: ""
    local-prefixes: github.com/org/project
```

## gomoddirectives

Manage the use of 'replace', 'retract', and 'excludes' directives in go.mod.

```
linters-settings:
  gomoddirectives:
    # Allow local \`replace\` directives.
    # Default: false
    replace-local: true
    # List of allowed \`replace\` directives.
    # Default: []
    replace-allow-list:
      - launchpad.net/gocheck
    # Allow to not explain why the version has been retracted in the \`retract\` directives.
    # Default: false
    retract-allow-no-explanation: true
    # Forbid the use of the \`exclude\` directives.
    # Default: false
    exclude-forbidden: true
    # Forbid the use of the \`toolchain\` directive.
    # Default: false
    toolchain-forbidden: true
    # Defines a pattern to validate \`toolchain\` directive.
    # Default: '' (no match)
    toolchain-pattern: 'go1\.23\.\d+$'
    # Forbid the use of the \`tool\` directives.
    # Default: false
    tool-forbidden: true
    # Forbid the use of the \`godebug\` directive.
    # Default: false
    go-debug-forbidden: true
    # Defines a pattern to validate \`go\` minimum version directive.
    # Default: '' (no match)
    go-version-pattern: '\d\.\d+(\.0)?'
```

## gomodguard

Allow and block list linter for direct Go module dependencies. This is different from depguard where there are different block types for example version constraints and module recommendations.

```
linters-settings:
  gomodguard:
    allowed:
      # List of allowed modules.
      # Default: []
      modules:
        - gopkg.in/yaml.v2
      # List of allowed module domains.
      # Default: []
      domains:
        - golang.org
    blocked:
      # List of blocked modules.
      # Default: []
      modules:
        # Blocked module.
        - github.com/uudashr/go-module:
            # Recommended modules that should be used instead. (Optional)
            recommendations:
              - golang.org/x/mod
            # Reason why the recommended module should be used. (Optional)
            reason: "\`mod\` is the official go.mod parser library."
      # List of blocked module version constraints.
      # Default: []
      versions:
        # Blocked module with version constraint.
        - github.com/mitchellh/go-homedir:
            # Version constraint, see https://github.com/Masterminds/semver#basic-comparisons.
            version: "< 1.1.0"
            # Reason why the version constraint exists. (Optional)
            reason: "testing if blocked version constraint works."
      # Set to true to raise lint issues for packages that are loaded from a local path via replace directive.
      # Default: false
      local_replace_directives: false
```


Linter for Go source code that specializes in simplifying code.

```
linters-settings:
  gosimple:
    # Sxxxx checks in https://staticcheck.dev/docs/configuration/options/#checks
    # Default: ["*"]
    checks:
      # Use plain channel send or receive instead of single-case select.
      # https://staticcheck.dev/docs/checks/#S1000
      - S1000
      # Replace for loop with call to copy.
      # https://staticcheck.dev/docs/checks/#S1001
      - S1001
      # Omit comparison with boolean constant.
      # https://staticcheck.dev/docs/checks/#S1002
      - S1002
      # Replace call to 'strings.Index' with 'strings.Contains'.
      # https://staticcheck.dev/docs/checks/#S1003
      - S1003
      # Replace call to 'bytes.Compare' with 'bytes.Equal'.
      # https://staticcheck.dev/docs/checks/#S1004
      - S1004
      # Drop unnecessary use of the blank identifier.
      # https://staticcheck.dev/docs/checks/#S1005
      - S1005
      # Use "for { ... }" for infinite loops.
      # https://staticcheck.dev/docs/checks/#S1006
      - S1006
      # Simplify regular expression by using raw string literal.
      # https://staticcheck.dev/docs/checks/#S1007
      - S1007
      # Simplify returning boolean expression.
      # https://staticcheck.dev/docs/checks/#S1008
      - S1008
      # Omit redundant nil check on slices, maps, and channels.
      # https://staticcheck.dev/docs/checks/#S1009
      - S1009
      # Omit default slice index.
      # https://staticcheck.dev/docs/checks/#S1010
      - S1010
      # Use a single 'append' to concatenate two slices.
      # https://staticcheck.dev/docs/checks/#S1011
      - S1011
      # Replace 'time.Now().Sub(x)' with 'time.Since(x)'.
      # https://staticcheck.dev/docs/checks/#S1012
      - S1012
      # Use a type conversion instead of manually copying struct fields.
      # https://staticcheck.dev/docs/checks/#S1016
      - S1016
      # Replace manual trimming with 'strings.TrimPrefix'.
      # https://staticcheck.dev/docs/checks/#S1017
      - S1017
      # Use "copy" for sliding elements.
      # https://staticcheck.dev/docs/checks/#S1018
      - S1018
      # Simplify "make" call by omitting redundant arguments.
      # https://staticcheck.dev/docs/checks/#S1019
      - S1019
      # Omit redundant nil check in type assertion.
      # https://staticcheck.dev/docs/checks/#S1020
      - S1020
      # Merge variable declaration and assignment.
      # https://staticcheck.dev/docs/checks/#S1021
      - S1021
      # Omit redundant control flow.
      # https://staticcheck.dev/docs/checks/#S1023
      - S1023
      # Replace 'x.Sub(time.Now())' with 'time.Until(x)'.
      # https://staticcheck.dev/docs/checks/#S1024
      - S1024
      # Don't use 'fmt.Sprintf("%s", x)' unnecessarily.
      # https://staticcheck.dev/docs/checks/#S1025
      - S1025
      # Simplify error construction with 'fmt.Errorf'.
      # https://staticcheck.dev/docs/checks/#S1028
      - S1028
      # Range over the string directly.
      # https://staticcheck.dev/docs/checks/#S1029
      - S1029
      # Use 'bytes.Buffer.String' or 'bytes.Buffer.Bytes'.
      # https://staticcheck.dev/docs/checks/#S1030
      - S1030
      # Omit redundant nil check around loop.
      # https://staticcheck.dev/docs/checks/#S1031
      - S1031
      # Use 'sort.Ints(x)', 'sort.Float64s(x)', and 'sort.Strings(x)'.
      # https://staticcheck.dev/docs/checks/#S1032
      - S1032
      # Unnecessary guard around call to "delete".
      # https://staticcheck.dev/docs/checks/#S1033
      - S1033
      # Use result of type assertion to simplify cases.
      # https://staticcheck.dev/docs/checks/#S1034
      - S1034
      # Redundant call to 'net/http.CanonicalHeaderKey' in method call on 'net/http.Header'.
      # https://staticcheck.dev/docs/checks/#S1035
      - S1035
      # Unnecessary guard around map access.
      # https://staticcheck.dev/docs/checks/#S1036
      - S1036
      # Elaborate way of sleeping.
      # https://staticcheck.dev/docs/checks/#S1037
      - S1037
      # Unnecessarily complex way of printing formatted string.
      # https://staticcheck.dev/docs/checks/#S1038
      - S1038
      # Unnecessary use of 'fmt.Sprint'.
      # https://staticcheck.dev/docs/checks/#S1039
      - S1039
      # Type assertion to current type.
      # https://staticcheck.dev/docs/checks/#S1040
      - S1040
```
