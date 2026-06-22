---
title: "gocritic"
tags: ['golangci-lint', 'linters']
created: 2026-06-21
part_of: "tools/golangci-lint/Linters.md"
---

# gocritic

## dogsled

Checks assignments with too many blank identifiers (e.g. x, *,* , \_,:= f()).

```
linters-settings:
  dogsled:
    # Checks assignments with too many blank identifiers.
    # Default: 2
    max-blank-identifiers: 3
```

## dupl

Detects duplicate fragments of code.

```
linters-settings:
  dupl:
    # Tokens count to trigger issue.
    # Default: 150
    threshold: 100
```

## dupword

Checks for duplicate words in the source code.

```
linters-settings:
  dupword:
    # Keywords for detecting duplicate words.
    # If this list is not empty, only the words defined in this list will be detected.
    # Default: []
    keywords:
      - "the"
      - "and"
      - "a"
    # Keywords used to ignore detection.
    # Default: []
    ignore:
      - "0C0C"
```

## errcheck

Errcheck is a program for checking for unchecked errors in Go code. These unchecked errors can be critical bugs in some cases.

```
linters-settings:
  errcheck:
    # Report about not checking of errors in type assertions: \`a := b.(MyStruct)\`.
    # Such cases aren't reported by default.
    # Default: false
    check-type-assertions: true
    # report about assignment of errors to blank identifier: \`num, _ := strconv.Atoi(numStr)\`.
    # Such cases aren't reported by default.
    # Default: false
    check-blank: true
    # To disable the errcheck built-in exclude list.
    # See \`-excludeonly\` option in https://github.com/kisielk/errcheck#excluding-functions for details.
    # Default: false
    disable-default-exclusions: true
    # List of functions to exclude from checking, where each entry is a single function to exclude.
    # See https://github.com/kisielk/errcheck#excluding-functions for details.
    exclude-functions:
      - io/ioutil.ReadFile
      - io.Copy(*bytes.Buffer)
      - io.Copy(os.Stdout)
```

## errchkjson

Checks types passed to the json encoding functions. Reports unsupported types and reports occurrences where the check for the returned error can be omitted.

```
linters-settings:
  errchkjson:
    # With check-error-free-encoding set to true, errchkjson does warn about errors
    # from json encoding functions that are safe to be ignored,
    # because they are not possible to happen.
    #
    # if check-error-free-encoding is set to true and errcheck linter is enabled,
    # it is recommended to add the following exceptions to prevent from false positives:
    #
    #     linters-settings:
    #       errcheck:
    #         exclude-functions:
    #           - encoding/json.Marshal
    #           - encoding/json.MarshalIndent
    #
    # Default: false
    check-error-free-encoding: true
    # Issue on struct encoding that doesn't have exported fields.
    # Default: false
    report-no-exported: false
```

## errorlint

Errorlint is a linter for that can be used to find code that will cause problems with the error wrapping scheme introduced in Go 1.13.

```
linters-settings:
  errorlint:
    # Check whether fmt.Errorf uses the %w verb for formatting errors.
    # See the https://github.com/polyfloyd/go-errorlint for caveats.
    # Default: true
    errorf: false
    # Permit more than 1 %w verb, valid per Go 1.20 (Requires errorf:true)
    # Default: true
    errorf-multi: false
    # Check for plain type assertions and type switches.
    # Default: true
    asserts: false
    # Check for plain error comparisons.
    # Default: true
    comparison: false
    # Allowed errors.
    # Default: []
    allowed-errors:
      - err: "io.EOF"
        fun: "example.com/pkg.Read"
    # Allowed error "wildcards".
    # Default: []
    allowed-errors-wildcard:
      - err: "example.com/pkg.ErrMagic"
        fun: "example.com/pkg.Magic"
```

## exhaustive

Check exhaustiveness of enum switch statements.

```
linters-settings:
  exhaustive:
    # Program elements to check for exhaustiveness.
    # Default: [ switch ]
    check:
      - switch
      - map
    # Check switch statements in generated files also.
    # Default: false
    check-generated: true
    # Presence of "default" case in switch statements satisfies exhaustiveness,
    # even if all enum members are not listed.
    # Default: false
    default-signifies-exhaustive: true
    # Enum members matching the supplied regex do not have to be listed in
    # switch statements to satisfy exhaustiveness.
    # Default: ""
    ignore-enum-members: "Example.+"
    # Enum types matching the supplied regex do not have to be listed in
    # switch statements to satisfy exhaustiveness.
    # Default: ""
    ignore-enum-types: "Example.+"
    # Consider enums only in package scopes, not in inner scopes.
    # Default: false
    package-scope-only: true
    # Only run exhaustive check on switches with "//exhaustive:enforce" comment.
    # Default: false
    explicit-exhaustive-switch: true
    # Only run exhaustive check on map literals with "//exhaustive:enforce" comment.
    # Default: false
    explicit-exhaustive-map: true
    # Switch statement requires default case even if exhaustive.
    # Default: false
    default-case-required: true
```

## exhaustruct

Checks if all structure fields are initialized.

```
linters-settings:
  exhaustruct:
    # List of regular expressions to match struct packages and their names.
    # Regular expressions must match complete canonical struct package/name/structname.
    # If this list is empty, all structs are tested.
    # Default: []
    include:
      - '.+\.Test'
      - 'example\.com/package\.ExampleStruct[\d]{1,2}'
    # List of regular expressions to exclude struct packages and their names from checks.
    # Regular expressions must match complete canonical struct package/name/structname.
    # Default: []
    exclude:
      - '.+/cobra\.Command$'
```

## fatcontext

Detects nested contexts in loops and function literals.

```
linters-settings:
  fatcontext:
    # Check for potential fat contexts in struct pointers.
    # May generate false positives.
    # Default: false
    check-struct-pointers: true
```

## forbidigo

Forbids identifiers.

```
linters-settings:
  forbidigo:
    # Forbid the following identifiers (list of regexp).
    # Default: ["^(fmt\\.Print(|f|ln)|print|println)$"]
    forbid:
      # Built-in bootstrapping functions.
      - ^print(ln)?$
      # Optional message that gets included in error reports.
      - p: ^fmt\.Print.*$
        msg: Do not commit print statements.
      # Alternatively, put messages at the end of the regex, surrounded by \`(# )?\`
      # Escape any special characters. Those messages get included in error reports.
      - 'fmt\.Print.*(# Do not commit print statements\.)?'
      # Forbid spew Dump, whether it is called as function or method.
      # Depends on analyze-types below.
      - ^spew\.(ConfigState\.)?Dump$
      # The package name might be ambiguous.
      # The full import path can be used as additional criteria.
      # Depends on analyze-types below.
      - p: ^v1.Dump$
        pkg: ^example.com/pkg/api/v1$
    # Exclude godoc examples from forbidigo checks.
    # Default: true
    exclude-godoc-examples: false
    # Instead of matching the literal source code,
    # use type information to replace expressions with strings that contain the package name
    # and (for methods and fields) the type name.
    # This makes it possible to handle import renaming and forbid struct fields and methods.
    # Default: false
    analyze-types: true
```

## funlen

Checks for long functions.

```
linters-settings:
  funlen:
    # Checks the number of lines in a function.
    # If lower than 0, disable the check.
    # Default: 60
    lines: -1
    # Checks the number of statements in a function.
    # If lower than 0, disable the check.
    # Default: 40
    statements: -1
    # Ignore comments when counting lines.
    # Default false
    ignore-comments: true
```

## gci

Checks if code and import statements are formatted, with additional rules.

```
linters-settings:
  gci:
    # Section configuration to compare against.
    # Section names are case-insensitive and may contain parameters in ().
    # The default order of sections is \`standard > default > custom > blank > dot > alias > localmodule\`,
    # If \`custom-order\` is \`true\`, it follows the order of \`sections\` option.
    # Default: ["standard", "default"]
    sections:
      - standard # Standard section: captures all standard packages.
      - default # Default section: contains all imports that could not be matched to another section type.
      - prefix(github.com/org/project) # Custom section: groups all imports with the specified Prefix.
      - blank # Blank section: contains all blank imports. This section is not present unless explicitly enabled.
      - dot # Dot section: contains all dot imports. This section is not present unless explicitly enabled.
      - alias # Alias section: contains all alias imports. This section is not present unless explicitly enabled.
      - localmodule # Local module section: contains all local packages. This section is not present unless explicitly enabled.
    # Checks that no inline Comments are present.
    # Default: false
    no-inline-comments: true
    # Checks that no prefix Comments(comment lines above an import) are present.
    # Default: false
    no-prefix-comments: true
    # Skip generated files.
    # Default: true
    skip-generated: false
    # Enable custom order of sections.
    # If \`true\`, make the section order the same as the order of \`sections\`.
    # Default: false
    custom-order: true
    # Drops lexical ordering for custom sections.
    # Default: false
    no-lex-order: true
```

## ginkgolinter

Enforces standards of using ginkgo and gomega.

```
linters-settings:
  ginkgolinter:
    # Suppress the wrong length assertion warning.
    # Default: false
    suppress-len-assertion: true
    # Suppress the wrong nil assertion warning.
    # Default: false
    suppress-nil-assertion: true
    # Suppress the wrong error assertion warning.
    # Default: false
    suppress-err-assertion: true
    # Suppress the wrong comparison assertion warning.
    # Default: false
    suppress-compare-assertion: true
    # Suppress the function all in async assertion warning.
    # Default: false
    suppress-async-assertion: true
    # Suppress warning for comparing values from different types, like \`int32\` and \`uint32\`
    # Default: false
    suppress-type-compare-assertion: true
    # Trigger warning for ginkgo focus containers like \`FDescribe\`, \`FContext\`, \`FWhen\` or \`FIt\`
    # Default: false
    forbid-focus-container: true
    # Don't trigger warnings for HaveLen(0)
    # Default: false
    allow-havelen-zero: true
    # Force using \`Expect\` with \`To\`, \`ToNot\` or \`NotTo\`.
    # Reject using \`Expect\` with \`Should\` or \`ShouldNot\`.
    # Default: false
    force-expect-to: true
    # Best effort validation of async intervals (timeout and polling).
    # Ignored the suppress-async-assertion is true.
    # Default: false
    validate-async-intervals: true
    # Trigger a warning for variable assignments in ginkgo containers like \`Describe\`, \`Context\` and \`When\`, instead of in \`BeforeEach()\`.
    # Default: false
    forbid-spec-pollution: true
    # Force using the Succeed matcher for error functions, and the HaveOccurred matcher for non-function error values.
    # Default: false
    force-succeed: true
```

## gochecksumtype

Run exhaustiveness checks on Go "sum types".

```
linters-settings:
  gochecksumtype:
    # Presence of \`default\` case in switch statements satisfies exhaustiveness, if all members are not listed.
    # Default: true
    default-signifies-exhaustive: false
    # Include shared interfaces in the exhaustiviness check.
    # Default: false
    include-shared-interfaces: true
```

## gocognit

Computes and checks the cognitive complexity of functions.

```
linters-settings:
  gocognit:
    # Minimal code complexity to report.
    # Default: 30 (but we recommend 10-20)
    min-complexity: 10
```

## goconst

Finds repeated strings that could be replaced by a constant.

```
linters-settings:
  goconst:
    # Minimal length of string constant.
    # Default: 3
    min-len: 2
    # Minimum occurrences of constant string count to trigger issue.
    # Default: 3
    min-occurrences: 2
    # Ignore test files.
    # Default: false
    ignore-tests: true
    # Look for existing constants matching the values.
    # Default: true
    match-constant: false
    # Search also for duplicated numbers.
    # Default: false
    numbers: true
    # Minimum value, only works with goconst.numbers
    # Default: 3
    min: 2
    # Maximum value, only works with goconst.numbers
    # Default: 3
    max: 2
    # Ignore when constant is not used as function argument.
    # Default: true
    ignore-calls: false
    # Exclude strings matching the given regular expression.
    # Default: ""
    ignore-strings: 'foo.+'
```


Provides diagnostics that check for bugs, performance and style issues.  
Extensible without recompilation through dynamic rules.  
Dynamic rules are written declaratively with AST patterns, filters, report message and optional suggestion.

```
linters-settings:
  gocritic:
    # Disable all checks.
    # Default: false
    disable-all: true
    # Which checks should be enabled in addition to default checks; can't be combined with 'disabled-checks'.
    # By default, list of stable checks is used (https://go-critic.com/overview#checks-overview):
    #   appendAssign, argOrder, assignOp, badCall, badCond, captLocal, caseOrder, codegenComment, commentFormatting,
    #   defaultCaseOrder, deprecatedComment, dupArg, dupBranchBody, dupCase, dupSubExpr, elseif, exitAfterDefer,
    #   flagDeref, flagName, ifElseChain, mapKey, newDeref, offBy1, regexpMust, singleCaseSwitch, sloppyLen,
    #   sloppyTypeAssert, switchTrue, typeSwitchVar, underef, unlambda, unslice, valSwap, wrapperFunc
    # To see which checks are enabled run \`GL_DEBUG=gocritic golangci-lint run --enable=gocritic\`.
    enabled-checks:
      # Detects suspicious append result assignments.
      # https://go-critic.com/overview.html#appendassign
      - appendAssign
      # Detects \`append\` chains to the same slice that can be done in a single \`append\` call.
      # https://go-critic.com/overview.html#appendcombine
      - appendCombine
      # Detects suspicious arguments order.
      # https://go-critic.com/overview.html#argorder
      - argOrder
      # Detects assignments that can be simplified by using assignment operators.
      # https://go-critic.com/overview.html#assignop
      - assignOp
      # Detects suspicious function calls.
      # https://go-critic.com/overview.html#badcall
      - badCall
      # Detects suspicious condition expressions.
      # https://go-critic.com/overview.html#badcond
      - badCond
      # Detects suspicious mutex lock/unlock operations.
      # https://go-critic.com/overview.html#badlock
      - badLock
      # Detects suspicious regexp patterns.
      # https://go-critic.com/overview.html#badregexp
      - badRegexp
      # Detects bad usage of sort package.
      # https://go-critic.com/overview.html#badsorting
      - badSorting
      # Detects bad usage of sync.OnceFunc.
      # https://go-critic.com/overview.html#badsynconcefunc
      - badSyncOnceFunc
      # Detects bool expressions that can be simplified.
      # https://go-critic.com/overview.html#boolexprsimplify
      - boolExprSimplify
      # Detects when predeclared identifiers are shadowed in assignments.
      # https://go-critic.com/overview.html#builtinshadow
      - builtinShadow
      # Detects top-level declarations that shadow the predeclared identifiers.
      # https://go-critic.com/overview.html#builtinshadowdecl
      - builtinShadowDecl
      # Detects capitalized names for local variables.
      # https://go-critic.com/overview.html#captlocal
      - captLocal
      # Detects erroneous case order inside switch statements.
      # https://go-critic.com/overview.html#caseorder
      - caseOrder
      # Detects malformed 'code generated' file comments.
      # https://go-critic.com/overview.html#codegencomment
      - codegenComment
      # Detects comments with non-idiomatic formatting.
      # https://go-critic.com/overview.html#commentformatting
      - commentFormatting
      # Detects commented-out code inside function bodies.
      # https://go-critic.com/overview.html#commentedoutcode
      - commentedOutCode
      # Detects commented-out imports.
      # https://go-critic.com/overview.html#commentedoutimport
      - commentedOutImport
      # Detects when default case in switch isn't on 1st or last position.
      # https://go-critic.com/overview.html#defaultcaseorder
      - defaultCaseOrder
      # Detects loops inside functions that use defer.
      # https://go-critic.com/overview.html#deferinloop
      - deferInLoop
      # Detects deferred function literals that can be simplified.
      # https://go-critic.com/overview.html#deferunlambda
      - deferUnlambda
      # Detects malformed 'deprecated' doc-comments.
      # https://go-critic.com/overview.html#deprecatedcomment
      - deprecatedComment
      # Detects comments that silence go lint complaints about doc-comment.
      # https://go-critic.com/overview.html#docstub
      - docStub
      # Detects suspicious duplicated arguments.
      # https://go-critic.com/overview.html#duparg
      - dupArg
      # Detects duplicated branch bodies inside conditional statements.
      # https://go-critic.com/overview.html#dupbranchbody
      - dupBranchBody
      # Detects duplicated case clauses inside switch or select statements.
      # https://go-critic.com/overview.html#dupcase
      - dupCase
      # Detects multiple imports of the same package under different aliases.
      # https://go-critic.com/overview.html#dupimport
      - dupImport
      # Detects suspicious duplicated sub-expressions.
      # https://go-critic.com/overview.html#dupsubexpr
      - dupSubExpr
      # Detects suspicious formatting strings usage.
      # https://go-critic.com/overview.html#dynamicfmtstring
      - dynamicFmtString
      # Detects else with nested if statement that can be replaced with else-if.
      # https://go-critic.com/overview.html#elseif
      - elseif
      # Detects suspicious empty declarations blocks.
      # https://go-critic.com/overview.html#emptydecl
      - emptyDecl
      # Detects fallthrough that can be avoided by using multi case values.
      # https://go-critic.com/overview.html#emptyfallthrough
      - emptyFallthrough
      # Detects empty string checks that can be written more idiomatically.
      # https://go-critic.com/overview.html#emptystringtest
      - emptyStringTest
      # Detects unoptimal strings/bytes case-insensitive comparison.
      # https://go-critic.com/overview.html#equalfold
      - equalFold
      # Detects unwanted dependencies on the evaluation order.
      # https://go-critic.com/overview.html#evalorder
      - evalOrder
      # Detects calls to exit/fatal inside functions that use defer.
      # https://go-critic.com/overview.html#exitafterdefer
      - exitAfterDefer
      # Detects exposed methods from sync.Mutex and sync.RWMutex.
      # https://go-critic.com/overview.html#exposedsyncmutex
      - exposedSyncMutex
      # Detects suspicious reassignment of error from another package.
      # https://go-critic.com/overview.html#externalerrorreassign
      - externalErrorReassign
      # Detects problems in filepath.Join() function calls.
      # https://go-critic.com/overview.html#filepathjoin
      - filepathJoin
      # Detects immediate dereferencing of \`flag\` package pointers.
      # https://go-critic.com/overview.html#flagderef
      - flagDeref
      # Detects suspicious flag names.
      # https://go-critic.com/overview.html#flagname
      - flagName
      # Detects hex literals that have mixed case letter digits.
      # https://go-critic.com/overview.html#hexliteral
      - hexLiteral
      # Detects nil usages in http.NewRequest calls, suggesting http.NoBody as an alternative.
      # https://go-critic.com/overview.html#httpnobody
      - httpNoBody
      # Detects params that incur excessive amount of copying.
      # https://go-critic.com/overview.html#hugeparam
      - hugeParam
      # Detects repeated if-else statements and suggests to replace them with switch statement.
      # https://go-critic.com/overview.html#ifelsechain
      - ifElseChain
      # Detects when imported package names shadowed in the assignments.
      # https://go-critic.com/overview.html#importshadow
      - importShadow
      # Detects strings.Index calls that may cause unwanted allocs.
      # https://go-critic.com/overview.html#indexalloc
      - indexAlloc
      # Detects non-assignment statements inside if/switch init clause.
      # https://go-critic.com/overview.html#initclause
      - initClause
      # Detects suspicious map literal keys.
      # https://go-critic.com/overview.html#mapkey
      - mapKey
      # Detects method expression call that can be replaced with a method call.
      # https://go-critic.com/overview.html#methodexprcall
      - methodExprCall
      # Finds where nesting level could be reduced.
      # https://go-critic.com/overview.html#nestingreduce
      - nestingReduce
      # Detects immediate dereferencing of \`new\` expressions.
      # https://go-critic.com/overview.html#newderef
      - newDeref
      # Detects return statements those results evaluate to nil.
      # https://go-critic.com/overview.html#nilvalreturn
      - nilValReturn
      # Detects old-style octal literals.
      # https://go-critic.com/overview.html#octalliteral
      - octalLiteral
      # Detects various off-by-one kind of errors.
      # https://go-critic.com/overview.html#offby1
      - offBy1
      # Detects if function parameters could be combined by type and suggest the way to do it.
      # https://go-critic.com/overview.html#paramtypecombine
      - paramTypeCombine
      # Detects expressions like []rune(s)[0] that may cause unwanted rune slice allocation.
      # https://go-critic.com/overview.html#preferdecoderune
      - preferDecodeRune
      # Detects concatenation with os.PathSeparator which can be replaced with filepath.Join.
      # https://go-critic.com/overview.html#preferfilepathjoin
      - preferFilepathJoin
      # Detects fmt.Sprint(f/ln) calls which can be replaced with fmt.Fprint(f/ln).
      # https://go-critic.com/overview.html#preferfprint
      - preferFprint
      # Detects w.Write or io.WriteString calls which can be replaced with w.WriteString.
      # https://go-critic.com/overview.html#preferstringwriter
      - preferStringWriter
      # Detects WriteRune calls with rune literal argument that is single byte and reports to use WriteByte instead.
      # https://go-critic.com/overview.html#preferwritebyte
      - preferWriteByte
      # Detects input and output parameters that have a type of pointer to referential type.
      # https://go-critic.com/overview.html#ptrtorefparam
      - ptrToRefParam
      # Detects append all its data while range it.
      # https://go-critic.com/overview.html#rangeappendall
      - rangeAppendAll
      # Detects expensive copies of \`for\` loop range expressions.
      # https://go-critic.com/overview.html#rangeexprcopy
      - rangeExprCopy
      # Detects loops that copy big objects during each iteration.
      # https://go-critic.com/overview.html#rangevalcopy
      - rangeValCopy
      # Detects redundant fmt.Sprint calls.
      # https://go-critic.com/overview.html#redundantsprint
      - redundantSprint
      # Detects \`regexp.Compile*\` that can be replaced with \`regexp.MustCompile*\`.
      # https://go-critic.com/overview.html#regexpmust
      - regexpMust
      # Detects suspicious regexp patterns.
      # https://go-critic.com/overview.html#regexppattern
      - regexpPattern
      # Detects regexp patterns that can be simplified.
      # https://go-critic.com/overview.html#regexpsimplify
      - regexpSimplify
      # Detects suspicious http.Error call without following return.
      # https://go-critic.com/overview.html#returnafterhttperror
      - returnAfterHttpError
      # Runs user-defined rules using ruleguard linter.
      # https://go-critic.com/overview.html#ruleguard
      - ruleguard
      # Detects switch statements that could be better written as if statement.
      # https://go-critic.com/overview.html#singlecaseswitch
      - singleCaseSwitch
      # Detects slice clear loops, suggests an idiom that is recognized by the Go compiler.
      # https://go-critic.com/overview.html#sliceclear
      - sliceClear
      # Detects usage of \`len\` when result is obvious or doesn't make sense.
      # https://go-critic.com/overview.html#sloppylen
      - sloppyLen
      # Detects suspicious/confusing re-assignments.
      # https://go-critic.com/overview.html#sloppyreassign
      - sloppyReassign
      # Detects redundant type assertions.
      # https://go-critic.com/overview.html#sloppytypeassert
      - sloppyTypeAssert
      # Detects suspicious sort.Slice calls.
      # https://go-critic.com/overview.html#sortslice
      - sortSlice
      # Detects "%s" formatting directives that can be replaced with %q.
      # https://go-critic.com/overview.html#sprintfquotedstring
      - sprintfQuotedString
      # Detects issue in Query() and Exec() calls.
      # https://go-critic.com/overview.html#sqlquery
      - sqlQuery
      # Detects string concat operations that can be simplified.
      # https://go-critic.com/overview.html#stringconcatsimplify
      - stringConcatSimplify
      # Detects redundant conversions between string and []byte.
      # https://go-critic.com/overview.html#stringxbytes
      - stringXbytes
      # Detects strings.Compare usage.
      # https://go-critic.com/overview.html#stringscompare
      - stringsCompare
      # Detects switch-over-bool statements that use explicit \`true\` tag value.
      # https://go-critic.com/overview.html#switchtrue
      - switchTrue
      # Detects sync.Map load+delete operations that can be replaced with LoadAndDelete.
      # https://go-critic.com/overview.html#syncmaploadanddelete
      - syncMapLoadAndDelete
      # Detects manual conversion to milli- or microseconds.
      # https://go-critic.com/overview.html#timeexprsimplify
      - timeExprSimplify
      # Detects TODO comments without detail/assignee.
      # https://go-critic.com/overview.html#todocommentwithoutdetail
      - todoCommentWithoutDetail
      # Detects function with too many results.
      # https://go-critic.com/overview.html#toomanyresultschecker
      - tooManyResultsChecker
      # Detects potential truncation issues when comparing ints of different sizes.
      # https://go-critic.com/overview.html#truncatecmp
      - truncateCmp
      # Detects repeated type assertions and suggests to replace them with type switch statement.
      # https://go-critic.com/overview.html#typeassertchain
      - typeAssertChain
      # Detects method declarations preceding the type definition itself.
      # https://go-critic.com/overview.html#typedeffirst
      - typeDefFirst
      # Detects type switches that can benefit from type guard clause with variable.
      # https://go-critic.com/overview.html#typeswitchvar
      - typeSwitchVar
      # Detects unneeded parenthesis inside type expressions and suggests to remove them.
      # https://go-critic.com/overview.html#typeunparen
      - typeUnparen
      # Detects unchecked errors in if statements.
      # https://go-critic.com/overview.html#uncheckedinlineerr
      - uncheckedInlineErr
      # Detects dereference expressions that can be omitted.
      # https://go-critic.com/overview.html#underef
      - underef
      # Detects redundant statement labels.
      # https://go-critic.com/overview.html#unlabelstmt
      - unlabelStmt
      # Detects function literals that can be simplified.
      # https://go-critic.com/overview.html#unlambda
      - unlambda
      # Detects unnamed results that may benefit from names.
      # https://go-critic.com/overview.html#unnamedresult
      - unnamedResult
      # Detects unnecessary braced statement blocks.
      # https://go-critic.com/overview.html#unnecessaryblock
      - unnecessaryBlock
      # Detects redundantly deferred calls.
      # https://go-critic.com/overview.html#unnecessarydefer
      - unnecessaryDefer
      # Detects slice expressions that can be simplified to sliced expression itself.
      # https://go-critic.com/overview.html#unslice
      - unslice
      # Detects value swapping code that are not using parallel assignment.
      # https://go-critic.com/overview.html#valswap
      - valSwap
      # Detects conditions that are unsafe due to not being exhaustive.
      # https://go-critic.com/overview.html#weakcond
      - weakCond
      # Ensures that \`//nolint\` comments include an explanation.
      # https://go-critic.com/overview.html#whynolint
      - whyNoLint
      # Detects function calls that can be replaced with convenience wrappers.
      # https://go-critic.com/overview.html#wrapperfunc
      - wrapperFunc
      # Detects Yoda style expressions and suggests to replace them.
      # https://go-critic.com/overview.html#yodastyleexpr
      - yodaStyleExpr
    # Enable all checks.
    # Default: false
    enable-all: true
    # Which checks should be disabled; can't be combined with 'enabled-checks'.
    # Default: []
    disabled-checks:
      - appendAssign
      - appendCombine
      - argOrder
      - assignOp
      - badCall
      - badCond
      - badLock
      - badRegexp
      - badSorting
      - badSyncOnceFunc
      - boolExprSimplify
      - builtinShadow
      - builtinShadowDecl
      - captLocal
      - caseOrder
      - codegenComment
      - commentFormatting
      - commentedOutCode
      - commentedOutImport
      - defaultCaseOrder
      - deferInLoop
      - deferUnlambda
      - deprecatedComment
      - docStub
      - dupArg
      - dupBranchBody
      - dupCase
      - dupImport
      - dupSubExpr
      - dynamicFmtString
      - elseif
      - emptyDecl
      - emptyFallthrough
      - emptyStringTest
      - equalFold
      - evalOrder
      - exitAfterDefer
      - exposedSyncMutex
      - externalErrorReassign
      - filepathJoin
      - flagDeref
      - flagName
      - hexLiteral
      - httpNoBody
      - hugeParam
      - ifElseChain
      - importShadow
      - indexAlloc
      - initClause
      - mapKey
      - methodExprCall
      - nestingReduce
      - newDeref
      - nilValReturn
      - octalLiteral
      - offBy1
      - paramTypeCombine
      - preferDecodeRune
      - preferFilepathJoin
      - preferFprint
      - preferStringWriter
      - preferWriteByte
      - ptrToRefParam
      - rangeAppendAll
      - rangeExprCopy
      - rangeValCopy
      - redundantSprint
      - regexpMust
      - regexpPattern
      - regexpSimplify
      - returnAfterHttpError
      - ruleguard
      - singleCaseSwitch
      - sliceClear
      - sloppyLen
      - sloppyReassign
      - sloppyTypeAssert
      - sortSlice
      - sprintfQuotedString
      - sqlQuery
      - stringConcatSimplify
      - stringXbytes
      - stringsCompare
      - switchTrue
      - syncMapLoadAndDelete
      - timeExprSimplify
      - todoCommentWithoutDetail
      - tooManyResultsChecker
      - truncateCmp
      - typeAssertChain
      - typeDefFirst
      - typeSwitchVar
      - typeUnparen
      - uncheckedInlineErr
      - underef
      - unlabelStmt
      - unlambda
      - unnamedResult
      - unnecessaryBlock
      - unnecessaryDefer
      - unslice
      - valSwap
      - weakCond
      - whyNoLint
      - wrapperFunc
      - yodaStyleExpr
    # Enable multiple checks by tags in addition to default checks.
    # Run \`GL_DEBUG=gocritic golangci-lint run --enable=gocritic\` to see all tags and checks.
    # See https://github.com/go-critic/go-critic#usage -> section "Tags".
    # Default: []
    enabled-tags:
      - diagnostic
      - style
      - performance
      - experimental
      - opinionated
    disabled-tags:
      - diagnostic
      - style
      - performance
      - experimental
      - opinionated
    # Settings passed to gocritic.
    # The settings key is the name of a supported gocritic checker.
    # The list of supported checkers can be find in https://go-critic.com/overview.
    settings:
      # Must be valid enabled check name.
      captLocal:
        # Whether to restrict checker to params only.
        # Default: true
        paramsOnly: false
      commentedOutCode:
        # Min length of the comment that triggers a warning.
        # Default: 15
        minLength: 50
      elseif:
        # Whether to skip balanced if-else pairs.
        # Default: true
        skipBalanced: false
      hugeParam:
        # Size in bytes that makes the warning trigger.
        # Default: 80
        sizeThreshold: 70
      ifElseChain:
        # Min number of if-else blocks that makes the warning trigger.
        # Default: 2
        minThreshold: 4
      nestingReduce:
        # Min number of statements inside a branch to trigger a warning.
        # Default: 5
        bodyWidth: 4
      rangeExprCopy:
        # Size in bytes that makes the warning trigger.
        # Default: 512
        sizeThreshold: 516
        # Whether to check test functions
        # Default: true
        skipTestFuncs: false
      rangeValCopy:
        # Size in bytes that makes the warning trigger.
        # Default: 128
        sizeThreshold: 32
        # Whether to check test functions.
        # Default: true
        skipTestFuncs: false
      ruleguard:
        # Enable debug to identify which 'Where' condition was rejected.
        # The value of the parameter is the name of a function in a ruleguard file.
        #
        # When a rule is evaluated:
        # If:
        #   The Match() clause is accepted; and
        #   One of the conditions in the Where() clause is rejected,
        # Then:
        #   ruleguard prints the specific Where() condition that was rejected.
        #
        # The option is passed to the ruleguard 'debug-group' argument.
        # Default: ""
        debug: 'emptyDecl'
        # Determines the behavior when an error occurs while parsing ruleguard files.
        # If flag is not set, log error and skip rule files that contain an error.
        # If flag is set, the value must be a comma-separated list of error conditions.
        # - 'all':    fail on all errors.
        # - 'import': ruleguard rule imports a package that cannot be found.
        # - 'dsl':    gorule file does not comply with the ruleguard DSL.
        # Default: ""
        failOn: dsl,import
        # Comma-separated list of file paths containing ruleguard rules.
        # If a path is relative, it is relative to the directory where the golangci-lint command is executed.
        # The special '${configDir}' variable is substituted with the absolute directory containing the golangci-lint config file.
        # Glob patterns such as 'rules-*.go' may be specified.
        # Default: ""
        rules: '${configDir}/ruleguard/rules-*.go,${configDir}/myrule1.go'
        # Comma-separated list of enabled groups or skip empty to enable everything.
        # Tags can be defined with # character prefix.
        # Default: "<all>"
        enable: "myGroupName,#myTagName"
        # Comma-separated list of disabled groups or skip empty to enable everything.
        # Tags can be defined with # character prefix.
        # Default: ""
        disable: "myGroupName,#myTagName"
      tooManyResultsChecker:
        # Maximum number of results.
        # Default: 5
        maxResults: 10
      truncateCmp:
        # Whether to skip int/uint/uintptr types.
        # Default: true
        skipArchDependent: false
      underef:
        # Whether to skip (*x).method() calls where x is a pointer receiver.
        # Default: true
        skipRecvDeref: false
      unnamedResult:
        # Whether to check exported functions.
        # Default: false
        checkExported: true
```
