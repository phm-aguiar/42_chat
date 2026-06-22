---
title: "False Positives"
source: "https://golangci.github.io/legacy-v1-doc/usage/false-positives/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, troubleshooting]
---
## Table of Contents

False positives are inevitable, but we did our best to reduce their count. For example, we have a default enabled set of [exclude patterns](https://golangci.github.io/legacy-v1-doc/usage/configuration#command-line-options).

If a false positive occurred, you have the several choices.

## Specific Linter Excludes

Most of the linters has a configuration, sometimes false-positives can be related to a bad configuration of a linter. So it's recommended to check the linters configuration.

Otherwise, some linters have dedicated configuration to exclude or disable rules.

An example with `staticcheck`:

```
linters-settings:
  staticcheck:
    checks:
      - all
      - '-SA1000' # disable the rule SA1000
      - '-SA1004' # disable the rule SA1004
```

## Exclude or Skip

### Exclude Issue by Text

Exclude issue by text using command-line option `-e` or config option `issues.exclude`. It's helpful when you decided to ignore all issues of this type. Also, you can use `issues.exclude-rules` config option for per-path or per-linter configuration.

In the following example, all the reports that contains the sentences defined in `exclude` are excluded:

```
issues:
  exclude:
    - "Error return value of .((os\\.)?std(out|err)\\..*|.*Close|.*Flush|os\\.Remove(All)?|.*printf?|os\\.(Un)?Setenv). is not checked"
    - "exported (type|method|function) (.+) should have comment or be unexported"
    - "ST1000: at least one file in a package should have a package comment"
```

In the following example, all the reports from the linters (`linters`) that contains the text (`text`) are excluded:

```
issues:
  exclude-rules:
    - linters:
        - mnd
      text: "Magic number: 9"
```

In the following example, all the reports from the linters (`linters`) that originated from the source (`source`) are excluded:

```
issues:
  exclude-rules:
    - linters:
        - lll
      source: "^//go:generate "
```

In the following example, all the reports that contains the text (`text`) in the path (`path`) are excluded:

```
issues:
  exclude-rules:
    - path: path/to/a/file.go
      text: "string \`example\` has (\\d+) occurrences, make it a constant"
```

### Exclude Issues by Path

Exclude issues in path by `issues.exclude-dirs`, `issues.exclude-files` or `issues.exclude-rules` config options.

Beware that the paths that get matched here are relative to the current working directory. When the configuration contains path patterns that check for specific directories, the `--path-prefix` parameter can be used to extend the paths before matching.

In the following example, all the reports from the linters (`linters`) that concerns the path (`path`) are excluded:

```
issues:
  exclude-rules:
    - path: '(.+)_test\.go'
      linters:
        - funlen
        - goconst
```

The opposite, excluding reports **except** for specific paths, is also possible. In the following example, only test files get checked:

```
issues:
  exclude-rules:
    - path-except: '(.+)_test\.go'
      linters:
        - funlen
        - goconst
```

In the following example, all the reports related to the files (`exclude-files`) are excluded:

```
issues:
  exclude-files:
    - path/to/a/file.go
```

In the following example, all the reports related to the directories (`exclude-dirs`) are excluded:

```
issues:
  exclude-dirs:
    - path/to/a/dir/
```

## Nolint Directive

To exclude issues from all linters use `//nolint:all`. For example, if it's used inline (not from the beginning of the line) it excludes issues only for this line.

```
var bad_name int //nolint:all
```

To exclude issues from specific linters only:

```
var bad_name int //nolint:golint,unused
```

To exclude issues for the block of code use this directive on the beginning of a line:

```
//nolint:all
func allIssuesInThisFunctionAreExcluded() *string {
  // ...
}

//nolint:govet
var (
  a int
  b int
)
```

Also, you can exclude all issues in a file by:

```
//nolint:unparam
package pkg
```

You may add a comment explaining or justifying why `//nolint` is being used on the same line as the flag itself:

```
//nolint:gocyclo // This legacy function is complex but the team too busy to simplify it
func someLegacyFunction() *string {
  // ...
}
```

You can see more examples of using `//nolint` in [our tests](https://github.com/golangci/golangci-lint/tree/HEAD/pkg/result/processors/testdata) for it.

Use `//nolint` instead of `// nolint` because machine-readable comments should have no space by Go convention.

## Default Exclusions

Some exclusions are considered as common, to help golangci-lint users those common exclusions are used as default exclusions.

If you don't want to use it you can set `issues.exclude-use-default` to `false`.

### EXC0001

- linter: `errcheck`
- pattern: `Error return value of .((os\.)?std(out|err)\..*|.*Close|.*Flush|os\.Remove(All)?|.*print(f|ln)?|os\.(Un)?Setenv). is not checked`
- why: Almost all programs ignore errors on these functions and in most cases it's ok.

### EXC0002

- linter: `golint`
- pattern: `(comment on exported (method|function|type|const)|should have( a package)? comment|comment should be of the form)`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### EXC0003

- linter: `golint`
- pattern: `func name will be used as test\.Test.* by other packages, and that stutters; consider calling this`
- why: False positive when tests are defined in package 'test'.

### EXC0004

- linter: `govet`
- pattern: `(possible misuse of unsafe.Pointer|should have signature)`
- why: Common false positives.

### EXC0005

- linter: `staticcheck`
- pattern: `SA4011`
- why: Developers tend to write in C-style with an explicit 'break' in a 'switch', so it's ok to ignore.

### EXC0006

- linter: `gosec`
- pattern: `G103: Use of unsafe calls should be audited`
- why: Too many false-positives on 'unsafe' usage.

### EXC0007

- linter: `gosec`
- pattern: `G204: Subprocess launched with variable`
- why: Too many false-positives for parametrized shell calls.

### EXC0008

- linter: `gosec`
- pattern: `G104`
- why: Duplicated errcheck checks.

### EXC0009

- linter: `gosec`
- pattern: `(G301|G302|G307): Expect (directory permissions to be 0750|file permissions to be 0600) or less`
- why: Too many issues in popular repos.

### EXC0010

- linter: `gosec`
- pattern: `G304: Potential file inclusion via variable`
- why: False positive is triggered by 'src, err:= ioutil.ReadFile(filename)'.

### EXC0011

- linter: `stylecheck`
- pattern: `(ST1000|ST1020|ST1021|ST1022)`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### EXC0012

- linter: `revive`
- pattern: `exported (.+) should have comment( \(or a comment on this block\))? or be unexported`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### EXC0013

- linter: `revive`
- pattern: `package comment should be of the form "(.+)..."`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### EXC0014

- linter: `revive`
- pattern: `comment on exported (.+) should be of the form "(.+)..."`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### EXC0015

- linter: `revive`
- pattern: `should have a package comment`
- why: Annoying issue about not having a comment. The rare codebase has such comments.

### Default Directory Exclusions

By default, the reports from directory names, that match the following regular expressions, are excluded:

- `third_party$`
- `examples$`
- `Godeps$`
- `builtin$`

This option has been defined when Go modules was not existed and when the golangci-lint core was different, this is not something we still recommend.

At some point, we will remove all those obsolete exclusions, but as it's a breaking changes it will only happen inside a major version.

So we recommend setting `issues.exclude-dirs-use-default` to `false`.

[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/usage/false-positives.mdx)