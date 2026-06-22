---
title: "revive"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# revive

## grouper

Analyze expression groups.

```
linters-settings:
  grouper:
    # Require the use of a single global 'const' declaration only.
    # Default: false
    const-require-single-const: true
    # Require the use of grouped global 'const' declarations.
    # Default: false
    const-require-grouping: true
    # Require the use of a single 'import' declaration only.
    # Default: false
    import-require-single-import: true
    # Require the use of grouped 'import' declarations.
    # Default: false
    import-require-grouping: true
    # Require the use of a single global 'type' declaration only.
    # Default: false
    type-require-single-type: true
    # Require the use of grouped global 'type' declarations.
    # Default: false
    type-require-grouping: true
    # Require the use of a single global 'var' declaration only.
    # Default: false
    var-require-single-var: true
    # Require the use of grouped global 'var' declarations.
    # Default: false
    var-require-grouping: true
```

## iface

Detect the incorrect use of interfaces, helping developers avoid interface pollution.

```
linters-settings:
  iface:
    # List of analyzers.
    # Default: ["identical"]
    enable:
      - identical # Identifies interfaces in the same package that have identical method sets.
      - unused # Identifies interfaces that are not used anywhere in the same package where the interface is defined.
      - opaque # Identifies functions that return interfaces, but the actual returned value is always a single concrete implementation.
    settings:
      unused:
        # List of packages path to exclude from the check.
        # Default: []
        exclude:
          - github.com/example/log
```

## importas

Enforces consistent import aliases.

```
linters-settings:
  importas:
    # Do not allow unaliased imports of aliased packages.
    # Default: false
    no-unaliased: true
    # Do not allow non-required aliases.
    # Default: false
    no-extra-aliases: true
    # List of aliases
    # Default: []
    alias:
      # Using \`servingv1\` alias for \`knative.dev/serving/pkg/apis/serving/v1\` package.
      - pkg: knative.dev/serving/pkg/apis/serving/v1
        alias: servingv1
      # Using \`autoscalingv1alpha1\` alias for \`knative.dev/serving/pkg/apis/autoscaling/v1alpha1\` package.
      - pkg: knative.dev/serving/pkg/apis/autoscaling/v1alpha1
        alias: autoscalingv1alpha1
      # You can specify the package path by regular expression,
      # and alias by regular expression expansion syntax like below.
      # see https://github.com/julz/importas#use-regular-expression for details
      - pkg: knative.dev/serving/pkg/apis/(\w+)/(v[\w\d]+)
        alias: $1$2
      # An explicit empty alias can be used to ensure no aliases are used for a package.
      # This can be useful if \`no-extra-aliases: true\` doesn't fit your need.
      # Multiple packages can use an empty alias.
      - pkg: errors
        alias: ""
```

## inamedparam

Reports interfaces with unnamed method parameters.

```
linters-settings:
  inamedparam:
    # Skips check for interface methods with only a single parameter.
    # Default: false
    skip-single-param: true
```

## interfacebloat

A linter that checks the number of methods inside an interface.

```
linters-settings:
  interfacebloat:
    # The maximum number of methods allowed for an interface.
    # Default: 10
    max: 5
```

## ireturn

Accept Interfaces, Return Concrete Types.

```
linters-settings:
  ireturn:
    # List of interfaces to allow.
    # Lists of the keywords and regular expressions matched to interface or package names can be used.
    # \`allow\` and \`reject\` settings cannot be used at the same time.
    #
    # Keywords:
    # - \`empty\` for \`interface{}\`
    # - \`error\` for errors
    # - \`stdlib\` for standard library
    # - \`anon\` for anonymous interfaces
    # - \`generic\` for generic interfaces added in go 1.18
    #
    # Default: [anon, error, empty, stdlib]
    allow:
      - anon
      # You can specify idiomatic endings for interface
      - (or|er)$
    # List of interfaces to reject.
    # Lists of the keywords and regular expressions matched to interface or package names can be used.
    # \`allow\` and \`reject\` settings cannot be used at the same time.
    #
    # Keywords:
    # - \`empty\` for \`interface{}\`
    # - \`error\` for errors
    # - \`stdlib\` for standard library
    # - \`anon\` for anonymous interfaces
    # - \`generic\` for generic interfaces added in go 1.18
    #
    # Default: []
    reject:
      - github.com\/user\/package\/v4\.Type
```

## lll

Reports long lines.

```
linters-settings:
  lll:
    # Max line length, lines longer will be reported.
    # '\t' is counted as 1 character by default, and can be changed with the tab-width option.
    # Default: 120.
    line-length: 120
    # Tab width in spaces.
    # Default: 1
    tab-width: 1
```

## loggercheck

Checks key value pairs for common logger libraries (kitlog,klog,logr,zap).

```
linters-settings:
  loggercheck:
    # Allow check for the github.com/go-kit/log library.
    # Default: true
    kitlog: false
    # Allow check for the k8s.io/klog/v2 library.
    # Default: true
    klog: false
    # Allow check for the github.com/go-logr/logr library.
    # Default: true
    logr: false
    # Allow check for the log/slog library.
    # Default: true
    slog: false
    # Allow check for the "sugar logger" from go.uber.org/zap library.
    # Default: true
    zap: false
    # Require all logging keys to be inlined constant strings.
    # Default: false
    require-string-key: true
    # Require printf-like format specifier (%s, %d for example) not present.
    # Default: false
    no-printf-like: true
    # List of custom rules to check against, where each rule is a single logger pattern, useful for wrapped loggers.
    # For example: https://github.com/timonwong/loggercheck/blob/7395ab86595781e33f7afba27ad7b55e6956ebcd/testdata/custom-rules.txt
    # Default: empty
    rules:
      - k8s.io/klog/v2.InfoS # package level exported functions
      - (github.com/go-logr/logr.Logger).Error # "Methods"
      - (*go.uber.org/zap.SugaredLogger).With # Also "Methods", but with a pointer receiver
```

## maintidx

Maintidx measures the maintainability index of each function.

```
linters-settings:
  maintidx:
    # Show functions with maintainability index lower than N.
    # A high index indicates better maintainability (it's kind of the opposite of complexity).
    # Default: 20
    under: 100
```

## makezero

Finds slice declarations with non-zero initial length.

```
linters-settings:
  makezero:
    # Allow only slices initialized with a length of zero.
    # Default: false
    always: true
```

## misspell

Finds commonly misspelled English words.

```
linters-settings:
  misspell:
    # Correct spellings using locale preferences for US or UK.
    # Setting locale to US will correct the British spelling of 'colour' to 'color'.
    # Default is to use a neutral variety of English.
    locale: US
    # Typos to ignore.
    # Should be in lower case.
    # Default: []
    ignore-words:
      - someword
    # Extra word corrections.
    # \`typo\` and \`correction\` should only contain letters.
    # The words are case-insensitive.
    # Default: []
    extra-words:
      - typo: "iff"
        correction: "if"
      - typo: "cancelation"
        correction: "cancellation"
    # Mode of the analysis:
    # - default: checks all the file content.
    # - restricted: checks only comments.
    # Default: ""
    mode: restricted
```

## mnd

An analyzer to detect magic numbers.

```
linters-settings:
  mnd:
    # List of enabled checks, see https://github.com/tommy-muehle/go-mnd/#checks for description.
    # Default: ["argument", "case", "condition", "operation", "return", "assign"]
    checks:
      - argument
      - case
      - condition
      - operation
      - return
      - assign
    # List of numbers to exclude from analysis.
    # The numbers should be written as string.
    # Values always ignored: "1", "1.0", "0" and "0.0"
    # Default: []
    ignored-numbers:
      - '0666'
      - '0755'
      - '42'
    # List of file patterns to exclude from analysis.
    # Values always ignored: \`.+_test.go\`
    # Default: []
    ignored-files:
      - 'magic1_.+\.go$'
    # List of function patterns to exclude from analysis.
    # Following functions are always ignored: \`time.Date\`,
    # \`strconv.FormatInt\`, \`strconv.FormatUint\`, \`strconv.FormatFloat\`,
    # \`strconv.ParseInt\`, \`strconv.ParseUint\`, \`strconv.ParseFloat\`.
    # Default: []
    ignored-functions:
      - '^math\.'
      - '^http\.StatusText$'
```

## musttag

Enforce field tags in (un)marshaled structs.

```
linters-settings:
  musttag:
    # A set of custom functions to check in addition to the builtin ones.
    # Default: json, xml, gopkg.in/yaml.v3, BurntSushi/toml, mitchellh/mapstructure, jmoiron/sqlx
    functions:
      # The full name of the function, including the package.
      - name: github.com/hashicorp/hcl/v2/hclsimple.DecodeFile
        # The struct tag whose presence should be ensured.
        tag: hcl
        # The position of the argument to check.
        arg-pos: 2
```

## nakedret

Checks that functions with naked returns are not longer than a maximum size (can be zero).

```
linters-settings:
  nakedret:
    # Make an issue if func has more lines of code than this setting, and it has naked returns.
    # Default: 30
    max-func-lines: 31
```

## nestif

Reports deeply nested if statements.

```
linters-settings:
  nestif:
    # Minimal complexity of if statements to report.
    # Default: 5
    min-complexity: 4
```

## nilnil

Checks that there is no simultaneous return of `nil` error and an invalid value.

```
linters-settings:
  nilnil:
    # In addition, detect opposite situation (simultaneous return of non-nil error and valid value).
    # Default: false
    detect-opposite: true
    # List of return types to check.
    # Default: ["chan", "func", "iface", "map", "ptr", "uintptr", "unsafeptr"]
    checked-types:
      - chan
      - func
      - iface
      - map
      - ptr
      - uintptr
      - unsafeptr
```

## nlreturn

Nlreturn checks for a new line before return and branch statements to increase code clarity.

```
linters-settings:
  nlreturn:
    # Size of the block (including return statement that is still "OK")
    # so no return split required.
    # Default: 1
    block-size: 2
```

## nolintlint

Reports ill-formed or insufficient nolint directives.

```
linters-settings:
  nolintlint:
    # Disable to ensure that all nolint directives actually have an effect.
    # Default: false
    allow-unused: true
    # Exclude following linters from requiring an explanation.
    # Default: []
    allow-no-explanation: []
    # Enable to require an explanation of nonzero length after each nolint directive.
    # Default: false
    require-explanation: true
    # Enable to require nolint directives to mention the specific linter being suppressed.
    # Default: false
    require-specific: true
```

## nonamedreturns

Reports all named returns.

```
linters-settings:
  nonamedreturns:
    # Report named error if it is assigned inside defer.
    # Default: false
    report-error-in-defer: true
```

## paralleltest

Detects missing usage of t.Parallel() method in your Go test.

```
linters-settings:
  paralleltest:
    # Ignore missing calls to \`t.Parallel()\` and only report incorrect uses of it.
    # Default: false
    ignore-missing: true
    # Ignore missing calls to \`t.Parallel()\` in subtests. Top-level tests are
    # still required to have \`t.Parallel\`, but subtests are allowed to skip it.
    # Default: false
    ignore-missing-subtests: true
```

## perfsprint

Checks that fmt.Sprintf can be replaced with a faster alternative.

```
linters-settings:
  perfsprint:
    # Enable/disable optimization of integer formatting.
    # Default: true
    integer-format: false
    # Optimizes even if it requires an int or uint type cast.
    # Default: true
    int-conversion: false
    # Enable/disable optimization of error formatting.
    # Default: true
    error-format: false
    # Optimizes into \`err.Error()\` even if it is only equivalent for non-nil errors.
    # Default: false
    err-error: true
    # Optimizes \`fmt.Errorf\`.
    # Default: true
    errorf: false
    # Enable/disable optimization of string formatting.
    # Default: true
    string-format: false
    # Optimizes \`fmt.Sprintf\` with only one argument.
    # Default: true
    sprintf1: false
    # Optimizes into strings concatenation.
    # Default: true
    strconcat: false
    # Enable/disable optimization of bool formatting.
    # Default: true
    bool-format: false
    # Enable/disable optimization of hex formatting.
    # Default: true
    hex-format: false
```

## prealloc

Finds slice declarations that could potentially be pre-allocated.

```
linters-settings:
  prealloc:
    # IMPORTANT: we don't recommend using this linter before doing performance profiling.
    # For most programs usage of prealloc will be a premature optimization.

    # Report pre-allocation suggestions only on simple loops that have no returns/breaks/continues/gotos in them.
    # Default: true
    simple: false
    # Report pre-allocation suggestions on range loops.
    # Default: true
    range-loops: false
    # Report pre-allocation suggestions on for loops.
    # Default: false
    for-loops: true
```

## predeclared

Find code that shadows one of Go's predeclared identifiers.

```
linters-settings:
  predeclared:
    # Comma-separated list of predeclared identifiers to not report on.
    # Default: ""
    ignore: "new,int"
    # Include method names and field names (i.e., qualified names) in checks.
    # Default: false
    q: true
```

## promlinter

Check Prometheus metrics naming via promlint.

```
linters-settings:
  promlinter:
    # Promlinter cannot infer all metrics name in static analysis.
    # Enable strict mode will also include the errors caused by failing to parse the args.
    # Default: false
    strict: true
    # Please refer to https://github.com/yeya24/promlinter#usage for detailed usage.
    # Default: []
    disabled-linters:
      # Help detects issues related to the help text for a metric.
      - Help
      # MetricUnits detects issues with metric unit names.
      - MetricUnits
      # Counter detects issues specific to counters, as well as patterns that should only be used with counters.
      - Counter
      # HistogramSummaryReserved detects when other types of metrics use names or labels reserved for use by histograms and/or summaries.
      - HistogramSummaryReserved
      # MetricTypeInName detects when metric types are included in the metric name.
      - MetricTypeInName
      # ReservedChars detects colons in metric names.
      - ReservedChars
      # CamelCase detects metric names and label names written in camelCase.
      - CamelCase
      # UnitAbbreviations detects abbreviated units in the metric name.
      - UnitAbbreviations
```

## protogetter

Reports direct reads from proto message fields when getters should be used.

```
linters-settings:
  protogetter:
    # Skip files generated by specified generators from the checking.
    # Checks only the file's initial comment, which must follow the format: "// Code generated by <generator-name>".
    # Files generated by protoc-gen-go, protoc-gen-go-grpc, and protoc-gen-grpc-gateway are always excluded automatically.
    # Default: []
    skip-generated-by: ["protoc-gen-go-my-own-generator"]
    # Skip files matching the specified glob pattern from the checking.
    # Default: []
    skip-files:
      - "*.pb.go"
      - "*/vendor/*"
      - "/full/path/to/file.go"
    # Skip any generated files from the checking.
    # Default: false
    skip-any-generated: true
    # Skip first argument of append function.
    # Default: false
    replace-first-arg-in-append: true
```

## reassign

Checks that package variables are not reassigned.

```
linters-settings:
  reassign:
    # Patterns for global variable names that are checked for reassignment.
    # See https://github.com/curioswitch/go-reassign#usage
    # Default: ["EOF", "Err.*"]
    patterns:
      - ".*"
```

## recvcheck

Checks for receiver type consistency.

```
linters-settings:
  recvcheck:
    # Disables the built-in method exclusions:
    # - \`MarshalText\`
    # - \`MarshalJSON\`
    # - \`MarshalYAML\`
    # - \`MarshalXML\`
    # - \`MarshalBinary\`
    # - \`GobEncode\`
    # Default: false
    disable-builtin: true
    # User-defined method exclusions.
    # The format is \`struct_name.method_name\` (ex: \`Foo.MethodName\`).
    # A wildcard \`*\` can use as a struct name (ex: \`*.MethodName\`).
    # Default: []
    exclusions:
      - "*.Value"
```


Fast, configurable, extensible, flexible, and beautiful linter for Go. Drop-in replacement of golint.

```
linters-settings:
  revive:
    # Maximum number of open files at the same time.
    # See https://github.com/mgechev/revive#command-line-flags
    # Defaults to unlimited.
    max-open-files: 2048
    # When set to false, ignores files with "GENERATED" header, similar to golint.
    # See https://github.com/mgechev/revive#configuration for details.
    # Default: false
    ignore-generated-header: true
    # Sets the default severity.
    # See https://github.com/mgechev/revive#configuration
    # Default: warning
    severity: error
    # Enable all available rules.
    # Default: false
    enable-all-rules: true
    # Enable validation of comment directives.
    # See https://github.com/mgechev/revive#comment-directives
    directives:
      - name: specify-disable-reason
        severity: error
    # Sets the default failure confidence.
    # This means that linting errors with less than 0.8 confidence will be ignored.
    # Default: 0.8
    confidence: 0.1
    # Run \`GL_DEBUG=revive golangci-lint run --enable-only=revive\` to see default, all available rules, and enabled rules.
    rules:
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#add-constant
      - name: add-constant
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - maxLitCount: "3"
            allowStrs: '""'
            allowInts: "0,1,2"
            allowFloats: "0.0,0.,1.0,1.,2.0,2."
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#argument-limit
      - name: argument-limit
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [4]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#atomic
      - name: atomic
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#banned-characters
      - name: banned-characters
        severity: warning
        disabled: false
        exclude: [""]
        arguments: ["Ω", "Σ", "σ", "7"]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#bare-return
      - name: bare-return
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#blank-imports
      - name: blank-imports
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#bool-literal-in-expr
      - name: bool-literal-in-expr
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#call-to-gc
      - name: call-to-gc
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#cognitive-complexity
      - name: cognitive-complexity
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [7]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#comment-spacings
      - name: comment-spacings
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - mypragma
          - otherpragma
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#comments-density
      - name: comments-density
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [15]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#confusing-naming
      - name: confusing-naming
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#confusing-results
      - name: confusing-results
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#constant-logical-expr
      - name: constant-logical-expr
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#context-as-argument
      - name: context-as-argument
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - allowTypesBefore: "*testing.T,*github.com/user/repo/testing.Harness"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#context-keys-type
      - name: context-keys-type
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#cyclomatic
      - name: cyclomatic
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [3]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#datarace
      - name: datarace
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#deep-exit
      - name: deep-exit
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#defer
      - name: defer
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - ["call-chain", "loop"]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#dot-imports
      - name: dot-imports
        severity: warning
        disabled: false
        exclude: [""]
        arguments: []
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#duplicated-imports
      - name: duplicated-imports
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#early-return
      - name: early-return
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "preserveScope"
          - "allowJump"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#empty-block
      - name: empty-block
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#empty-lines
      - name: empty-lines
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#enforce-map-style
      - name: enforce-map-style
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "make"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#enforce-repeated-arg-type-style
      - name: enforce-repeated-arg-type-style
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "short"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#enforce-slice-style
      - name: enforce-slice-style
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "make"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#error-naming
      - name: error-naming
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#error-return
      - name: error-return
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#error-strings
      - name: error-strings
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "xerrors.New"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#errorf
      - name: errorf
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#exported
      - name: exported
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "checkPrivateReceivers"
          - "disableStutteringCheck"
          - "checkPublicInterface"
          - "disableChecksOnFunctions"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#file-header
      - name: file-header
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - This is the text that must appear at the top of source files.
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#file-length-limit
      - name: file-length-limit
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - max: 100
            skipComments: true
            skipBlankLines: true
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#filename-format
      - name: filename-format
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "^[_a-z][_a-z0-9]*\\.go$"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#flag-parameter
      - name: flag-parameter
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#function-length
      - name: function-length
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [10, 0]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#function-result-limit
      - name: function-result-limit
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [3]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#get-return
      - name: get-return
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#identical-branches
      - name: identical-branches
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#if-return
      - name: if-return
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#import-alias-naming
      - name: import-alias-naming
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "^[a-z][a-z0-9]{0,}$"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#import-shadowing
      - name: import-shadowing
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#imports-blocklist
      - name: imports-blocklist
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "crypto/md5"
          - "crypto/sha1"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#increment-decrement
      - name: increment-decrement
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#indent-error-flow
      - name: indent-error-flow
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "preserveScope"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#line-length-limit
      - name: line-length-limit
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [80]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#max-control-nesting
      - name: max-control-nesting
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [3]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#max-public-structs
      - name: max-public-structs
        severity: warning
        disabled: false
        exclude: [""]
        arguments: [3]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#modifies-parameter
      - name: modifies-parameter
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#modifies-value-receiver
      - name: modifies-value-receiver
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#nested-structs
      - name: nested-structs
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#optimize-operands-order
      - name: optimize-operands-order
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#package-comments
      - name: package-comments
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#range
      - name: range
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#range-val-address
      - name: range-val-address
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#range-val-in-closure
      - name: range-val-in-closure
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#receiver-naming
      - name: receiver-naming
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - maxLength: 2
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#redefines-builtin-id
      - name: redefines-builtin-id
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#redundant-build-tag
      - name: redundant-build-tag
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#redundant-import-alias
      - name: redundant-import-alias
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#string-format
      - name: string-format
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - - 'core.WriteError[1].Message'
            - '/^([^A-Z]|$)/'
            - must not start with a capital letter
          - - 'fmt.Errorf[0]'
            - '/(^|[^\.!?])$/'
            - must not end in punctuation
          - - panic
            - '/^[^\n]*$/'
            - must not contain line breaks
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#string-of-int
      - name: string-of-int
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#struct-tag
      - name: struct-tag
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "json,inline"
          - "bson,outline,gnu"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#superfluous-else
      - name: superfluous-else
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "preserveScope"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#time-equal
      - name: time-equal
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#time-naming
      - name: time-naming
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unchecked-type-assertion
      - name: unchecked-type-assertion
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - acceptIgnoredAssertionResult: true
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unconditional-recursion
      - name: unconditional-recursion
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unexported-naming
      - name: unexported-naming
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unexported-return
      - name: unexported-return
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unhandled-error
      - name: unhandled-error
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - "fmt.Printf"
          - "myFunction"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unnecessary-stmt
      - name: unnecessary-stmt
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unreachable-code
      - name: unreachable-code
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unused-parameter
      - name: unused-parameter
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - allowRegex: "^_"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#unused-receiver
      - name: unused-receiver
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - allowRegex: "^_"
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#use-any
      - name: use-any
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#use-errors-new
      - name: use-errors-new
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#useless-break
      - name: useless-break
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#var-declaration
      - name: var-declaration
        severity: warning
        disabled: false
        exclude: [""]
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#var-naming
      - name: var-naming
        severity: warning
        disabled: false
        exclude: [""]
        arguments:
          - ["ID"] # AllowList
          - ["VM"] # DenyList
          - - upperCaseConst: true # Extra parameter (upperCaseConst|skipPackageNameChecks)
      # https://github.com/mgechev/revive/blob/HEAD/RULES_DESCRIPTIONS.md#waitgroup-by-value
      - name: waitgroup-by-value
        severity: warning
        disabled: false
        exclude: [""]
```
