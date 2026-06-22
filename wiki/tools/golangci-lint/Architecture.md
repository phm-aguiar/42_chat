---
title: "Architecture"
source: "https://golangci.github.io/legacy-v1-doc/contributing/architecture/"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Fast Go linters runner golangci-lint."
tags: [golangci-lint, architecture]
---
## Table of Contents

There are the following `golangci-lint` execution steps:

<svg id="mermaid-1742246585210" width="100%" xmlns="http://www.w3.org/2000/svg" xmlnsxlink="http://www.w3.org/1999/xlink" height="54" viewBox="0 0 742.90625 54" style="max-width: 742.906px;"><g><g><g></g><g><g id="L-init-loadPackages" style="opacity: 1;"><path d="M49.34375,27L53.510416666666664,27C57.677083333333336,27,66.01041666666667,27,74.34375,27C82.67708333333333,27,91.01041666666667,27,95.17708333333333,27L99.34375,27" marker-end="url(#arrowhead22)" style="fill: none;" stroke="currentColor"></path><defs><marker id="arrowhead22" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="strokeWidth" markerWidth="8" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" style="stroke-width: 1; stroke-dasharray: 1, 0;"></path></marker></defs></g><g id="L-loadPackages-runLinters" style="opacity: 1;"><path d="M227.875,27L232.04166666666666,27C236.20833333333334,27,244.54166666666666,27,252.875,27C261.2083333333333,27,269.5416666666667,27,273.7083333333333,27L277.875,27" marker-end="url(#arrowhead23)" style="fill: none;" stroke="currentColor"></path><defs><marker id="arrowhead23" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="strokeWidth" markerWidth="8" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" style="stroke-width: 1; stroke-dasharray: 1, 0;"></path></marker></defs></g><g id="L-runLinters-postprocess" style="opacity: 1;"><path d="M374.359375,27L378.5260416666667,27C382.6927083333333,27,391.0260416666667,27,399.359375,27C407.6927083333333,27,416.0260416666667,27,420.1927083333333,27L424.359375,27" marker-end="url(#arrowhead24)" style="fill: none;" stroke="currentColor"></path><defs><marker id="arrowhead24" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="strokeWidth" markerWidth="8" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" style="stroke-width: 1; stroke-dasharray: 1, 0;"></path></marker></defs></g><g id="L-postprocess-print" style="opacity: 1;"><path d="M582.203125,27L586.3697916666666,27C590.5364583333334,27,598.8697916666666,27,607.203125,27C615.5364583333334,27,623.8697916666666,27,628.0364583333334,27L632.203125,27" marker-end="url(#arrowhead25)" style="fill: none;" stroke="currentColor"></path><defs><marker id="arrowhead25" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="strokeWidth" markerWidth="8" markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" style="stroke-width: 1; stroke-dasharray: 1, 0;"></path></marker></defs></g></g><g><g transform="" style="opacity: 1;"><g transform="translate(0,0)"><rect rx="0" ry="0" width="0" height="0"></rect></g></g><g transform="" style="opacity: 1;"><g transform="translate(0,0)"><rect rx="0" ry="0" width="0" height="0"></rect></g></g><g transform="" style="opacity: 1;"><g transform="translate(0,0)"><rect rx="0" ry="0" width="0" height="0"></rect></g></g><g transform="" style="opacity: 1;"><g transform="translate(0,0)"><rect rx="0" ry="0" width="0" height="0"></rect></g></g></g><g><g id="flowchart-init-10" transform="translate(28.671875,27)" style="opacity: 1;"><rect rx="0" ry="0" x="-20.671875" y="-19" width="41.34375" height="38" fill="none" stroke="currentColor"></rect><g transform="translate(0,0)"><g transform="translate(-10.671875,-9)"><foreignObject width="21.34375" height="18"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">Init</div></foreignObject></g></g></g><g id="flowchart-loadPackages-11" transform="translate(163.609375,27)" style="opacity: 1;"><rect rx="0" ry="0" x="-64.265625" y="-19" width="128.53125" height="38" fill="none" stroke="currentColor"></rect><g transform="translate(0,0)"><g transform="translate(-54.265625,-9)"><foreignObject width="108.53125" height="18"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">Load packages</div></foreignObject></g></g></g><g id="flowchart-runLinters-12" transform="translate(326.1171875,27)" style="opacity: 1;"><rect rx="0" ry="0" x="-48.2421875" y="-19" width="96.484375" height="38" fill="none" stroke="currentColor"></rect><g transform="translate(0,0)"><g transform="translate(-38.2421875,-9)"><foreignObject width="76.484375" height="18"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">Run linters</div></foreignObject></g></g></g><g id="flowchart-postprocess-13" transform="translate(503.28125,27)" style="opacity: 1;"><rect rx="0" ry="0" x="-78.921875" y="-19" width="157.84375" height="38" fill="none" stroke="currentColor"></rect><g transform="translate(0,0)"><g transform="translate(-68.921875,-9)"><foreignObject width="137.84375" height="18"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">Postprocess issues</div></foreignObject></g></g></g><g id="flowchart-print-14" transform="translate(683.5546875,27)" style="opacity: 1;"><rect rx="0" ry="0" x="-51.3515625" y="-19" width="102.703125" height="38" fill="none" stroke="currentColor"></rect><g transform="translate(0,0)"><g transform="translate(-41.3515625,-9)"><foreignObject width="82.703125" height="18"><div xmlns="http://www.w3.org/1999/xhtml" style="display: inline-block; white-space: nowrap;">Print issues</div></foreignObject></g></g></g></g></g></g></svg>

## Init

The configuration is loaded from file and flags by `config.Loader` inside `PersistentPreRun` (or `PreRun`) of the commands that require configuration.

The linter database (`linterdb.Manager`) is fill based on the configuration:

- The linters ("internals" and plugins) are built by `linterdb.LinterBuilder` and `linterdb.PluginBuilder` builders.
- The configuration is validated by `linterdb.Validator`.

## Load Packages

Loading packages is listing all packages and their recursive dependencies for analysis. Also, depending on the enabled linters set some parsing of the source code can be performed at this step.

Packages loading starts here:

```
pkg/lint/load.gofunc (cl *ContextLoader) Load(ctx context.Context, linters []*linter.Config) (*linter.Context, error) {
    loadMode := cl.findLoadMode(linters)
    pkgs, err := cl.loadPackages(ctx, loadMode)
    if err != nil {
        return nil, fmt.Errorf("failed to load packages: %w", err)
    }

    // ...
    ret := &linter.Context{
        // ...
    }
    return ret, nil
}
```

First, we find a load mode as union of load modes for all enabled linters. We use [go/packages](https://pkg.go.dev/golang.org/x/tools/go/packages) for packages loading and use it's enum `packages.Need*` for load modes. Load mode sets which data does a linter needs for execution.

A linter that works only with AST need minimum of information: only filenames and AST. There is no need for packages dependencies or type information. AST is built during `go/analysis` execution to reduce memory usage. Such AST-based linters are configured with the following code:

```
pkg/lint/linter/config.gofunc (lc *Config) WithLoadFiles() *Config {
    lc.LoadMode |= packages.NeedName | packages.NeedFiles | packages.NeedCompiledGoFiles
    return lc
}
```

If a linter uses `go/analysis` and needs type information, we need to extract more data by `go/packages`:

```
pkg/lint/linter/config.gofunc (lc *Config) WithLoadForGoAnalysis() *Config {
    lc = lc.WithLoadFiles()
    lc.LoadMode |= packages.NeedImports | packages.NeedDeps | packages.NeedExportFile | packages.NeedTypesSizes
    lc.IsSlow = true
    return lc
}
```

After finding a load mode, we run `go/packages`: the library get list of dirs (or `./...` as the default value) as input and outputs list of packages and requested information about them: filenames, type information, AST, etc.

## Run Linters

First, we need to find all enabled linters. All linters are registered here:

```
pkg/lint/lintersdb/builder_linter.gofunc (b LinterBuilder) Build(cfg *config.Config) []*linter.Config {
    // ...
    return []*linter.Config{
        // ...
        linter.NewConfig(golinters.NewBodyclose()).
            WithSince("v1.18.0").
            WithLoadForGoAnalysis().
            WithPresets(linter.PresetPerformance, linter.PresetBugs).
            WithURL("https://github.com/timakin/bodyclose"),
        // ...
        linter.NewConfig(golinters.NewGovet(govetCfg)).
            WithEnabledByDefault().
            WithSince("v1.0.0").
            WithLoadForGoAnalysis().
            WithPresets(linter.PresetBugs, linter.PresetMetaLinter).
            WithAlternativeNames("vet", "vetshadow").
            WithURL("https://pkg.go.dev/cmd/vet"),
        // ...
    }
}
```

We filter requested in config and command-line linters in `EnabledSet`:

```
pkg/lint/lintersdb/manager.gofunc (m *Manager) GetEnabledLintersMap() (map[string]*linter.Config, error)
```

We merge enabled linters into one `MetaLinter` to improve execution time if we can:

```
// GetOptimizedLinters returns enabled linters after optimization (merging) of multiple linters into a fewer number of linters.
// E.g. some go/analysis linters can be optimized into one metalinter for data reuse and speed up.
func (m *Manager) GetOptimizedLinters() ([]*linter.Config, error) {
    // ...
    m.combineGoAnalysisLinters(resultLintersSet)
    // ...
}
```

The `MetaLinter` just stores all merged linters inside to run them at once:

```
pkg/golinters/goanalysis/metalinter.gotype MetaLinter struct {
    linters              []*Linter
    analyzerToLinterName map[*analysis.Analyzer]string
}
```

Currently, all linters except `unused` can be merged into this meta linter. The `unused` isn't merged because it has high memory usage.

Linters execution starts in `runAnalyzers`. It's the most complex part of the `golangci-lint`. We use custom [go/analysis](https://pkg.go.dev/golang.org/x/tools/go/analysis) runner there. It runs as much as it can in parallel. It lazy-loads as much as it can to reduce memory usage. Also, it sets all heavyweight data to `nil` as becomes unneeded to save memory.

We don't use existing [multichecker](https://pkg.go.dev/golang.org/x/tools/go/analysis/multichecker) because it doesn't use caching and doesn't have some important performance optimizations.

All found by linters issues are represented with `result.Issue` struct:

```
pkg/result/issue.gotype Issue struct {
    FromLinter string
    Text       string

    Severity string

    // Source lines of a code with the issue to show
    SourceLines []string

    // If we know how to fix the issue we can provide replacement lines
    Replacement *Replacement

    // Pkg is needed for proper caching of linting results
    Pkg *packages.Package \`json:"-"\`

    LineRange *Range \`json:",omitempty"\`

    Pos token.Position

    // HunkPos is used only when golangci-lint is run over a diff
    HunkPos int \`json:",omitempty"\`

    // If we are expecting a nolint (because this is from nolintlint), record the expected linter
    ExpectNoLint         bool
    ExpectedNoLintLinter string
}
```

## Postprocess Issues

We have an abstraction of `result.Processor` to postprocess found issues:

```
$ tree -L 1 ./pkg/result/processors/
./pkg/result/processors/
./pkg/result/processors/
├── autogenerated_exclude.go
├── autogenerated_exclude_test.go
├── base_rule.go
├── cgo.go
├── diff.go
├── exclude.go
├── exclude_rules.go
├── exclude_rules_test.go
├── exclude_test.go
├── filename_unadjuster.go
├── fixer.go
├── identifier_marker.go
├── identifier_marker_test.go
├── issues.go
├── max_from_linter.go
├── max_from_linter_test.go
├── max_per_file_from_linter.go
├── max_per_file_from_linter_test.go
├── max_same_issues.go
├── max_same_issues_test.go
├── nolint.go
├── nolint_test.go
├── path_prefixer.go
├── path_prefixer_test.go
├── path_prettifier.go
├── path_shortener.go
├── processor.go
├── processor_test.go
├── severity_rules.go
├── severity_rules_test.go
├── skip_dirs.go
├── skip_files.go
├── skip_files_test.go
├── sort_results.go
├── sort_results_test.go
├── source_code.go
├── testdata
├── uniq_by_line.go
└── uniq_by_line_test.go
```

The abstraction is simple:

```
pkg/result/processors/processor.gotype Processor interface {
    Process(issues []result.Issue) ([]result.Issue, error)
    Name() string
    Finish()
}
```

A processor can hide issues (`nolint`, `exclude`) or change issues (`path_shortener`).

## Print Issues

We have an abstraction for printing found issues.

```
$ tree -L 1 ./pkg/printers/
./pkg/printers/
├── checkstyle.go
├── checkstyle_test.go
├── codeclimate.go
├── codeclimate_test.go
├── github.go
├── github_test.go
├── html.go
├── html_test.go
├── json.go
├── json_test.go
├── junitxml.go
├── junitxml_test.go
├── printer.go
├── tab.go
├── tab_test.go
├── teamcity.go
├── teamcity_test.go
├── text.go
└── text_test.go
```

Needed printer is selected by command line option `--out-format`.

[Edit this page on GitHub](https://github.com/golangci/golangci-lint/tree/master/docs/src/docs/contributing/architecture.mdx)