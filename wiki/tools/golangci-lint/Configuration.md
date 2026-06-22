---
title: "Configuration"
source: "https://golangci.github.io/legacy-v1-doc/usage/configuration/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, configuration]
---
## Table of Contents

The config file has lower priority than command-line options. If the same bool/string/int option is provided on the command-line and in the config file, the option from command-line will be used. Slice options (e.g. list of enabled/disabled linters) are combined from the command-line and config file.

To see a list of linters enabled by your configuration use:

```
golangci-lint linters
```

## Config File

GolangCI-Lint looks for config files in the following paths from the current working directory:

- `.golangci.yml`
- `.golangci.yaml`
- `.golangci.toml`
- `.golangci.json`

GolangCI-Lint also searches for config files in all directories from the directory of the first analyzed path up to the root. If no configuration file has been found, GolangCI-Lint will try to find one in your home directory. To see which config file is being used and where it was sourced from run golangci-lint with `-v` option.

Config options inside the file are identical to command-line options. You can configure specific linters' options only within the config file (not the command-line).

There is a [`.golangci.reference.yml`](https://github.com/golangci/golangci-lint/blob/HEAD/.golangci.reference.yml) file with all supported options, their description, and default values. This file is neither a working example nor a recommended configuration, it's just a reference to display all the configuration options.

The configuration file can be validated with the JSON Schema: [https://golangci-lint.rum/jsonschema/golangci.v1.jsonschema.json](https://golangci-lint.rum/jsonschema/golangci.v1.jsonschema.json))

```
linters:
  # See the dedicated "linters" documentation section.
  option: value
# All available settings of specific linters.
linters-settings:
  # See the dedicated "linters-settings" documentation section.
  option: value
issues:
  # See the dedicated "issues" documentation section.
  option: value
# output configuration options
output:
  # See the dedicated "output" documentation section.
  option: value
# Options for analysis running.
run:
  # See the dedicated "run" documentation section.
  option: value
severity:
  # See the dedicated "severity" documentation section.
  option: value
```

### linters configuration

```
linters:
  # Disable all linters.
  # Default: false
  disable-all: true
  # Enable specific linter
  # https://golangci-lint.run/usage/linters/#enabled-by-default
  enable:
    - asasalint
    - asciicheck
    - bidichk
    - bodyclose
    - canonicalheader
    - containedctx
    - contextcheck
    - copyloopvar
    - cyclop
    - decorder
    - depguard
    - dogsled
    - dupl
    - dupword
    - durationcheck
    - err113
    - errcheck
    - errchkjson
    - errname
    - errorlint
    - exhaustive
    - exhaustruct
    - exptostd
    - fatcontext
    - forbidigo
    - forcetypeassert
    - funlen
    - gci
    - ginkgolinter
    - gocheckcompilerdirectives
    - gochecknoglobals
    - gochecknoinits
    - gochecksumtype
    - gocognit
    - goconst
    - gocritic
    - gocyclo
    - godot
    - godox
    - gofmt
    - gofumpt
    - goheader
    - goimports
    - gomoddirectives
    - gomodguard
    - goprintffuncname
    - gosec
    - gosimple
    - gosmopolitan
    - govet
    - grouper
    - iface
    - importas
    - inamedparam
    - ineffassign
    - interfacebloat
    - intrange
    - ireturn
    - lll
    - loggercheck
    - maintidx
    - makezero
    - mirror
    - misspell
    - mnd
    - musttag
    - nakedret
    - nestif
    - nilerr
    - nilnesserr
    - nilnil
    - nlreturn
    - noctx
    - nolintlint
    - nonamedreturns
    - nosprintfhostport
    - paralleltest
    - perfsprint
    - prealloc
    - predeclared
    - promlinter
    - protogetter
    - reassign
    - recvcheck
    - revive
    - rowserrcheck
    - sloglint
    - spancheck
    - sqlclosecheck
    - staticcheck
    - stylecheck
    - tagalign
    - tagliatelle
    - testableexamples
    - testifylint
    - testpackage
    - thelper
    - tparallel
    - unconvert
    - unparam
    - unused
    - usestdlibvars
    - usetesting
    - varnamelen
    - wastedassign
    - whitespace
    - wrapcheck
    - wsl
    - zerologlint
  # Enable all available linters.
  # Default: false
  enable-all: true
  # Disable specific linter
  # https://golangci-lint.run/usage/linters/#disabled-by-default
  disable:
    - asasalint
    - asciicheck
    - bidichk
    - bodyclose
    - canonicalheader
    - containedctx
    - contextcheck
    - copyloopvar
    - cyclop
    - decorder
    - depguard
    - dogsled
    - dupl
    - dupword
    - durationcheck
    - err113
    - errcheck
    - errchkjson
    - errname
    - errorlint
    - exhaustive
    - exhaustruct
    - exptostd
    - fatcontext
    - forbidigo
    - forcetypeassert
    - funlen
    - gci
    - ginkgolinter
    - gocheckcompilerdirectives
    - gochecknoglobals
    - gochecknoinits
    - gochecksumtype
    - gocognit
    - goconst
    - gocritic
    - gocyclo
    - godot
    - godox
    - gofmt
    - gofumpt
    - goheader
    - goimports
    - gomoddirectives
    - gomodguard
    - goprintffuncname
    - gosec
    - gosimple
    - gosmopolitan
    - govet
    - grouper
    - iface
    - importas
    - inamedparam
    - ineffassign
    - interfacebloat
    - intrange
    - ireturn
    - lll
    - loggercheck
    - maintidx
    - makezero
    - mirror
    - misspell
    - mnd
    - musttag
    - nakedret
    - nestif
    - nilerr
    - nilnesserr
    - nilnil
    - nlreturn
    - noctx
    - nolintlint
    - nonamedreturns
    - nosprintfhostport
    - paralleltest
    - perfsprint
    - prealloc
    - predeclared
    - promlinter
    - protogetter
    - reassign
    - recvcheck
    - revive
    - rowserrcheck
    - sloglint
    - spancheck
    - sqlclosecheck
    - staticcheck
    - stylecheck
    - tagalign
    - tagliatelle
    - testableexamples
    - testifylint
    - testpackage
    - thelper
    - tparallel
    - unconvert
    - unparam
    - unused
    - usestdlibvars
    - usetesting
    - varnamelen
    - wastedassign
    - whitespace
    - wrapcheck
    - wsl
    - zerologlint
    - deadcode # Deprecated
    - execinquery # Deprecated
    - exhaustivestruct # Deprecated
    - exportloopref # Deprecated
    - golint # Deprecated
    - gomnd # Deprecated
    - ifshort # Deprecated
    - interfacer # Deprecated
    - maligned # Deprecated
    - nosnakecase # Deprecated
    - scopelint # Deprecated
    - structcheck # Deprecated
    - tenv # Deprecated
    - varcheck # Deprecated
  # Enable presets.
  # https://golangci-lint.run/usage/linters
  # Default: []
  presets:
    - bugs
    - comment
    - complexity
    - error
    - format
    - import
    - metalinter
    - module
    - performance
    - sql
    - style
    - test
    - unused
  # Enable only fast linters from enabled linters set (first run won't be fast)
  # Default: false
  fast: true
```

### linters-settings configuration

See the dedicated [linters-settings](https://golangci.github.io/legacy-v1-doc/usage/linters) documentation section.

### issues configuration

```
issues:
  # List of regexps of issue texts to exclude.
  #
  # But independently of this option we use default exclude patterns,
  # it can be disabled by \`exclude-use-default: false\`.
  # To list all excluded by default patterns execute \`golangci-lint run --help\`
  #
  # Default: https://golangci-lint.run/usage/false-positives/#default-exclusions
  exclude:
    - abcdef
  # Excluding configuration per-path, per-linter, per-text and per-source
  exclude-rules:
    # Exclude some linters from running on tests files.
    - path: _test\.go
      linters:
        - gocyclo
        - errcheck
        - dupl
        - gosec
    # Run some linter only for test files by excluding its issues for everything else.
    - path-except: _test\.go
      linters:
        - forbidigo
    # Exclude known linters from partially hard-vendored code,
    # which is impossible to exclude via \`nolint\` comments.
    # \`/\` will be replaced by current OS file path separator to properly work on Windows.
    - path: internal/hmac/
      text: "weak cryptographic primitive"
      linters:
        - gosec
    # Exclude some \`staticcheck\` messages.
    - linters:
        - staticcheck
      text: "SA9003:"
    # Exclude \`lll\` issues for long lines with \`go:generate\`.
    - linters:
        - lll
      source: "^//go:generate "
  # Independently of option \`exclude\` we use default exclude patterns,
  # it can be disabled by this option.
  # To list all excluded by default patterns execute \`golangci-lint run --help\`.
  # Default: true
  exclude-use-default: false
  # If set to true, \`exclude\` and \`exclude-rules\` regular expressions become case-sensitive.
  # Default: false
  exclude-case-sensitive: false
  # Which dirs to exclude: issues from them won't be reported.
  # Can use regexp here: \`generated.*\`, regexp is applied on full path,
  # including the path prefix if one is set.
  # Default dirs are skipped independently of this option's value (see exclude-dirs-use-default).
  # "/" will be replaced by current OS file path separator to properly work on Windows.
  # Default: []
  exclude-dirs:
    - src/external_libs
    - autogenerated_by_my_lib
  # Enables exclude of directories:
  # - vendor$, third_party$, testdata$, examples$, Godeps$, builtin$
  # Default: true
  exclude-dirs-use-default: false
  # Which files to exclude: they will be analyzed, but issues from them won't be reported.
  # There is no need to include all autogenerated files,
  # we confidently recognize autogenerated files.
  # If it's not, please let us know.
  # "/" will be replaced by current OS file path separator to properly work on Windows.
  # Default: []
  exclude-files:
    - ".*\\.my\\.go$"
    - lib/bad.go
  # Mode of the generated files analysis.
  #
  # - \`strict\`: sources are excluded by following strictly the Go generated file convention.
  #    Source files that have lines matching only the following regular expression will be excluded: \`^// Code generated .* DO NOT EDIT\.$\`
  #    This line must appear before the first non-comment, non-blank text in the file.
  #    https://go.dev/s/generatedcode
  # - \`lax\`: sources are excluded if they contain lines \`autogenerated file\`, \`code generated\`, \`do not edit\`, etc.
  # - \`disable\`: disable the generated files exclusion.
  #
  # Default: lax
  exclude-generated: strict
  # The list of ids of default excludes to include or disable.
  # https://golangci-lint.run/usage/false-positives/#default-exclusions
  # Default: []
  include:
    - EXC0001
    - EXC0002
    - EXC0003
    - EXC0004
    - EXC0005
    - EXC0006
    - EXC0007
    - EXC0008
    - EXC0009
    - EXC0010
    - EXC0011
    - EXC0012
    - EXC0013
    - EXC0014
    - EXC0015
  # Maximum issues count per one linter.
  # Set to 0 to disable.
  # Default: 50
  max-issues-per-linter: 0
  # Maximum count of issues with the same text.
  # Set to 0 to disable.
  # Default: 3
  max-same-issues: 0
  # Make issues output unique by line.
  # Default: true
  uniq-by-line: false
  # Show only new issues: if there are unstaged changes or untracked files,
  # only those changes are analyzed, else only changes in HEAD~ are analyzed.
  # It's a super-useful option for integration of golangci-lint into existing large codebase.
  # It's not practical to fix all existing issues at the moment of integration:
  # much better don't allow issues in new code.
  #
  # Default: false
  new: true
  # Show only new issues created after the best common ancestor (merge-base against HEAD).
  # Default: ""
  new-from-merge-base: main
  # Show only new issues created after git revision \`REV\`.
  # Default: ""
  new-from-rev: HEAD
  # Show only new issues created in git patch with set file path.
  # Default: ""
  new-from-patch: path/to/patch/file
  # Show issues in any part of update files (requires new-from-rev or new-from-patch).
  # Default: false
  whole-files: true
  # Fix found issues (if it's supported by the linter).
  # Default: false
  fix: true
```

### output configuration

```
# output configuration options
output:
  # The formats used to render issues.
  # Formats:
  # - \`colored-line-number\`
  # - \`line-number\`
  # - \`json\`
  # - \`colored-tab\`
  # - \`tab\`
  # - \`html\`
  # - \`checkstyle\`
  # - \`code-climate\`
  # - \`junit-xml\`
  # - \`junit-xml-extended\`
  # - \`github-actions\`
  # - \`teamcity\`
  # - \`sarif\`
  # Output path can be either \`stdout\`, \`stderr\` or path to the file to write to.
  #
  # For the CLI flag (\`--out-format\`), multiple formats can be specified by separating them by comma.
  # The output can be specified for each of them by separating format name and path by colon symbol.
  # Example: "--out-format=checkstyle:report.xml,json:stdout,colored-line-number"
  # The CLI flag (\`--out-format\`) override the configuration file.
  #
  # Default:
  #   formats:
  #     - format: colored-line-number
  #       path: stdout
  formats:
    - format: json
      path: stderr
    - format: checkstyle
      path: report.xml
    - format: colored-line-number
  # Print lines of code with issue.
  # Default: true
  print-issued-lines: false
  # Print linter name in the end of issue text.
  # Default: true
  print-linter-name: false
  # Add a prefix to the output file references.
  # Default: ""
  path-prefix: ""
  # Sort results by the order defined in \`sort-order\`.
  # Default: false
  sort-results: true
  # Order to use when sorting results.
  # Require \`sort-results\` to \`true\`.
  # Possible values: \`file\`, \`linter\`, and \`severity\`.
  #
  # If the severity values are inside the following list, they are ordered in this order:
  #   1. error
  #   2. warning
  #   3. high
  #   4. medium
  #   5. low
  # Either they are sorted alphabetically.
  #
  # Default: ["file"]
  sort-order:
    - linter
    - severity
    - file # filepath, line, and column.
  # Show statistics per linter.
  # Default: false
  show-stats: true
```

### run configuration

```
# Options for analysis running.
run:
  # Timeout for analysis, e.g. 30s, 5m, 5m30s.
  # If the value is lower or equal to 0, the timeout is disabled.
  # Default: 1m
  timeout: 5m
  # The mode used to evaluate relative paths.
  # It's used by exclusions, Go plugins, and some linters.
  # The value can be:
  # - \`gomod\`: the paths will be relative to the directory of the \`go.mod\` file.
  # - \`gitroot\`: the paths will be relative to the git root (the parent directory of \`.git\`).
  # - \`cfg\`: the paths will be relative to the configuration file.
  # - \`wd\` (NOT recommended): the paths will be relative to the place where golangci-lint is run.
  # Default: wd
  relative-path-mode: gomod
  # Exit code when at least one issue was found.
  # Default: 1
  issues-exit-code: 2
  # Include test files or not.
  # Default: true
  tests: false
  # List of build tags, all linters use it.
  # Default: []
  build-tags:
    - mytag
  # If set, we pass it to "go list -mod={option}". From "go help modules":
  # If invoked with -mod=readonly, the go command is disallowed from the implicit
  # automatic updating of go.mod described above. Instead, it fails when any changes
  # to go.mod are needed. This setting is most useful to check that go.mod does
  # not need updates, such as in a continuous integration and testing system.
  # If invoked with -mod=vendor, the go command assumes that the vendor
  # directory holds the correct copies of dependencies and ignores
  # the dependency descriptions in go.mod.
  #
  # Allowed values: readonly|vendor|mod
  # Default: ""
  modules-download-mode: readonly
  # Allow multiple parallel golangci-lint instances running.
  # If false, golangci-lint acquires file lock on start.
  # Default: false
  allow-parallel-runners: true
  # Allow multiple golangci-lint instances running, but serialize them around a lock.
  # If false, golangci-lint exits with an error if it fails to acquire file lock on start.
  # Default: false
  allow-serial-runners: true
  # Define the Go version limit.
  # Mainly related to generics support since go1.18.
  # Default: use Go version from the go.mod file, fallback on the env var \`GOVERSION\`, fallback on 1.17
  go: '1.19'
  # Number of operating system threads (\`GOMAXPROCS\`) that can execute golangci-lint simultaneously.
  # If it is explicitly set to 0 (i.e. not the default) then golangci-lint will automatically set the value to match Linux container CPU quota.
  # Default: the number of logical CPUs in the machine
  concurrency: 4
```

### severity configuration

```
severity:
  # Set the default severity for issues.
  #
  # If severity rules are defined and the issues do not match or no severity is provided to the rule
  # this will be the default severity applied.
  # Severities should match the supported severity names of the selected out format.
  # - Code climate: https://docs.codeclimate.com/docs/issues#issue-severity
  # - Checkstyle: https://checkstyle.sourceforge.io/property_types.html#SeverityLevel
  # - GitHub: https://help.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message
  # - TeamCity: https://www.jetbrains.com/help/teamcity/service-messages.html#Inspection+Instance
  #
  # \`@linter\` can be used as severity value to keep the severity from linters (e.g. revive, gosec, ...)
  #
  # Default: ""
  default-severity: error
  # If set to true \`severity-rules\` regular expressions become case-sensitive.
  # Default: false
  case-sensitive: true
  # When a list of severity rules are provided, severity information will be added to lint issues.
  # Severity rules have the same filtering capability as exclude rules
  # except you are allowed to specify one matcher per severity rule.
  #
  # \`@linter\` can be used as severity value to keep the severity from linters (e.g. revive, gosec, ...)
  #
  # Only affects out formats that support setting severity information.
  #
  # Default: []
  rules:
    - linters:
        - dupl
      severity: info
```

## Command-Line Options

```
golangci-lint run -h
Usage:
  golangci-lint run [flags]

Flags:
  -c, --config PATH                    Read config from file path PATH
      --no-config                      Don't read config file
  -D, --disable strings                Disable specific linter
      --disable-all                    Disable all linters
  -E, --enable strings                 Enable specific linter
      --enable-all                     Enable all linters
      --fast                           Enable only fast linters from enabled linters set (first run won't be fast)
  -p, --presets strings                Enable presets of linters:
                                         - bugs
                                         - comment
                                         - complexity
                                         - error
                                         - format
                                         - import
                                         - metalinter
                                         - module
                                         - performance
                                         - sql
                                         - style
                                         - test
                                         - unused
                                       Run 'golangci-lint help linters' to see them.
                                       This option implies option --disable-all
      --enable-only strings            Override linters configuration section to only run the specific linter(s)
  -j, --concurrency int                Number of CPUs to use (Default: number of logical CPUs) (default 8)
      --modules-download-mode string   Modules download mode. If not empty, passed as -mod=<mode> to go tools
      --issues-exit-code int           Exit code when issues were found (default 1)
      --go string                      Targeted Go version
      --build-tags strings             Build tags
      --timeout duration               Timeout for total work. If <= 0, the timeout is disabled (default 1m0s)
      --tests                          Analyze tests (*_test.go) (default true)
      --allow-parallel-runners         Allow multiple parallel golangci-lint instances running.
                                       If false (default) - golangci-lint acquires file lock on start.
      --allow-serial-runners           Allow multiple golangci-lint instances running, but serialize them around a lock.
                                       If false (default) - golangci-lint exits with an error if it fails to acquire file lock on start.
      --out-format string              Formats of output:
                                         - json
                                         - line-number
                                         - colored-line-number
                                         - tab
                                         - colored-tab
                                         - checkstyle
                                         - code-climate
                                         - html
                                         - junit-xml
                                         - junit-xml-extended
                                         - github-actions
                                         - teamcity
                                         - sarif
                                        (default "colored-line-number")
      --print-issued-lines             Print lines of code with issue (default true)
      --print-linter-name              Print linter name in issue line (default true)
      --sort-results                   Sort linter results
      --sort-order strings             Sort order of linter results
      --path-prefix string             Path prefix to add to output
      --show-stats                     Show statistics per linter
  -e, --exclude strings                Exclude issue by regexp
      --exclude-use-default            Use or not use default excludes:
                                         - EXC0001 (errcheck): Almost all programs ignore errors on these functions and in most cases it's ok.
                                           Pattern: 'Error return value of .((os\.)?std(out|err)\..*|.*Close|.*Flush|os\.Remove(All)?|.*print(f|ln)?|os\.(Un)?Setenv). is not checked'
                                         - EXC0002 (golint): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: '(comment on exported (method|function|type|const)|should have( a package)? comment|comment should be of the form)'
                                         - EXC0003 (golint): False positive when tests are defined in package 'test'.
                                           Pattern: 'func name will be used as test\.Test.* by other packages, and that stutters; consider calling this'
                                         - EXC0004 (govet): Common false positives.
                                           Pattern: '(possible misuse of unsafe.Pointer|should have signature)'
                                         - EXC0005 (staticcheck): Developers tend to write in C-style with an explicit 'break' in a 'switch', so it's ok to ignore.
                                           Pattern: 'SA4011'
                                         - EXC0006 (gosec): Too many false-positives on 'unsafe' usage.
                                           Pattern: 'G103: Use of unsafe calls should be audited'
                                         - EXC0007 (gosec): Too many false-positives for parametrized shell calls.
                                           Pattern: 'G204: Subprocess launched with variable'
                                         - EXC0008 (gosec): Duplicated errcheck checks.
                                           Pattern: 'G104'
                                         - EXC0009 (gosec): Too many issues in popular repos.
                                           Pattern: '(G301|G302|G307): Expect (directory permissions to be 0750|file permissions to be 0600) or less'
                                         - EXC0010 (gosec): False positive is triggered by 'src, err := ioutil.ReadFile(filename)'.
                                           Pattern: 'G304: Potential file inclusion via variable'
                                         - EXC0011 (stylecheck): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: '(ST1000|ST1020|ST1021|ST1022)'
                                         - EXC0012 (revive): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: 'exported (.+) should have comment( \(or a comment on this block\))? or be unexported'
                                         - EXC0013 (revive): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: 'package comment should be of the form "(.+)..."'
                                         - EXC0014 (revive): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: 'comment on exported (.+) should be of the form "(.+)..."'
                                         - EXC0015 (revive): Annoying issue about not having a comment. The rare codebase has such comments.
                                           Pattern: 'should have a package comment' (default true)
      --exclude-case-sensitive         If set to true exclude and exclude rules regular expressions are case-sensitive
      --max-issues-per-linter int      Maximum issues count per one linter. Set to 0 to disable (default 50)
      --max-same-issues int            Maximum count of issues with the same text. Set to 0 to disable (default 3)
      --uniq-by-line                   Make issues output unique by line (default true)
      --exclude-files strings          Regexps of files to exclude
      --exclude-dirs strings           Regexps of directories to exclude
      --exclude-dirs-use-default       Use or not use default excluded directories:
                                         - (^|/)vendor($|/)
                                         - (^|/)third_party($|/)
                                         - (^|/)testdata($|/)
                                         - (^|/)examples($|/)
                                         - (^|/)Godeps($|/)
                                         - (^|/)builtin($|/)
                                        (default true)
      --exclude-generated string       Mode of the generated files analysis (default "lax")
  -n, --new                            Show only new issues: if there are unstaged changes or untracked files, only those changes are analyzed, else only changes in HEAD~ are analyzed.
                                       It's a super-useful option for integration of golangci-lint into existing large codebase.
                                       It's not practical to fix all existing issues at the moment of integration: much better to not allow issues in new code.
                                       For CI setups, prefer --new-from-rev=HEAD~, as --new can skip linting the current patch if any scripts generate unstaged files before golangci-lint runs.
      --new-from-rev REV               Show only new issues created after git revision REV
      --new-from-patch PATH            Show only new issues created in git patch with file path PATH
      --new-from-merge-base string     Show only new issues created after the best common ancestor (merge-base against HEAD)
      --whole-files                    Show issues in any part of update files (requires new-from-rev or new-from-patch)
      --fix                            Fix found issues (if it's supported by the linter)
      --cpu-profile-path string        Path to CPU profile output file
      --mem-profile-path string        Path to memory profile output file
      --print-resources-usage          Print avg and max memory usage of golangci-lint and total time
      --trace-path string              Path to trace output file

Global Flags:
      --color string   Use color when printing; can be 'always', 'auto', or 'never' (default "auto")
  -h, --help           Help for a command
  -v, --verbose        Verbose output
```

When the `--cpu-profile-path` or `--mem-profile-path` arguments are specified, `golangci-lint` writes runtime profiling data in the format expected by the [pprof](https://github.com/google/pprof) visualization tool.

When the `--trace-path` argument is specified, `golangci-lint` writes runtime tracing data in the format expected by the `go tool trace` command and visualization tool.

## Cache

GolangCI-Lint stores its cache in the subdirectory `golangci-lint` inside the [default user cache directory](https://pkg.go.dev/os#UserCacheDir).

You can override the default cache directory with the environment variable `GOLANGCI_LINT_CACHE`; the path must be absolute.

[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/usage/configuration.mdx)