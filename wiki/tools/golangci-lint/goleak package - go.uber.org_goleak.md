---
title: "goleak package - go.uber.org/goleak"
source: "https://pkg.go.dev/go.uber.org/goleak"
author:
published:
created: 2026-06-21
rag_score: 0.5
description: "Package goleak is a Goroutine leak detector."
tags: [golangci-lint, testing, goroutines]
---
## README

### goleak

Goroutine leak detector to help avoid Goroutine leaks.

#### Installation

You can use `go get` to get the latest version:

`go get -u go.uber.org/goleak`

`goleak` also supports semver releases.

Note that go-leak only [supports](https://go.dev/doc/devel/release#policy) the two most recent minor versions of Go.

#### Quick Start

To verify that there are no unexpected goroutines running at the end of a test:

```
func TestA(t *testing.T) {
    defer goleak.VerifyNone(t)

    // test logic here.
}
```

Instead of checking for leaks at the end of every test, `goleak` can also be run at the end of every test package by creating a `TestMain` function for your package:

```
func TestMain(m *testing.M) {
    goleak.VerifyTestMain(m)
}
```

#### Determine Source of Package Leaks

When verifying leaks using `TestMain`, the leak test is only run once after all tests have been run. This is typically enough to ensure there's no goroutines leaked from tests, but when there are leaks, it's hard to determine which test is causing them.

You can use the following bash script to determine the source of the failing test:

```
# Create a test binary which will be used to run each test individually
$ go test -c -o tests

# Run each test individually, printing "." for successful tests, or the test name
# for failing tests.
$ for test in $(go test -list . | grep -E "^(Test|Example)"); do ./tests -test.run "^$test\$" &>/dev/null && echo -n "." || echo -e "\n$test failed"; done
```

This will only print names of failing tests which can be investigated individually. E.g.,

```
.....
TestLeakyTest failed
.......
```

#### Stability

goleak is v1 and follows [SemVer](http://semver.org/) strictly.

No breaking changes will be made to exported APIs before 2.0.

## Documentation

### Overview

Package goleak is a Goroutine leak detector.

### Index

- [func Find(options...Option) error](#Find)
- [func VerifyNone(t TestingT, options...Option)](#VerifyNone)
- [func VerifyTestMain(m TestingM, options...Option)](#VerifyTestMain)
- [type Option](#Option)
- - [func Cleanup(cleanupFunc func(exitCode int)) Option](#Cleanup)
		- [func IgnoreAnyFunction(f string) Option](#IgnoreAnyFunction)
		- [func IgnoreCurrent() Option](#IgnoreCurrent)
		- [func IgnoreTopFunction(f string) Option](#IgnoreTopFunction)
- [type TestingM](#TestingM)
- [type TestingT](#TestingT)

### Constants

This section is empty.

### Variables

This section is empty.

### Functions

#### func Find ¶

```
func Find(options ...Option) error
```

Find looks for extra goroutines, and returns a descriptive error if any are found.

#### func VerifyNone ¶

```
func VerifyNone(t TestingT, options ...Option)
```

VerifyNone marks the given TestingT as failed if any extra goroutines are found by Find. This is a helper method to make it easier to integrate in tests by doing:

```
defer VerifyNone(t)
```

VerifyNone is currently incompatible with t.Parallel because it cannot associate specific goroutines with specific tests. Thus, non-leaking goroutines from other tests running in parallel could fail this check. If you need to run tests in parallel, use [VerifyTestMain](#VerifyTestMain) instead, which will verify that no leaking goroutines exist after ALL tests finish.

#### func VerifyTestMain ¶

```
func VerifyTestMain(m TestingM, options ...Option)
```

VerifyTestMain can be used in a TestMain function for package tests to verify that there were no goroutine leaks. To use it, your TestMain function should look like:

```
func TestMain(m *testing.M) {
  goleak.VerifyTestMain(m)
}
```

See [https://golang.org/pkg/testing/#hdr-Main](https://golang.org/pkg/testing/#hdr-Main) for more details.

This will run all tests as per normal, and if they were successful, look for any goroutine leaks and fail the tests if any leaks were found.

### Types

#### type Option ¶

```
type Option interface {
    // contains filtered or unexported methods
}
```

Option lets users specify custom verifications.

#### added in v1.2.0

```
func Cleanup(cleanupFunc func(exitCode int)) Option
```

Cleanup sets up a cleanup function that will be executed at the end of the leak check. When passed to [VerifyTestMain](#VerifyTestMain), the exit code passed to cleanupFunc will be set to the exit code of TestMain. When passed to [VerifyNone](#VerifyNone), the exit code will be set to 0. This cannot be passed to [Find](#Find).

#### added in v1.3.0

```
func IgnoreAnyFunction(f string) Option
```

IgnoreAnyFunction ignores goroutines where the specified function is present anywhere in the stack.

The function name must be fully qualified, e.g.,

```
go.uber.org/goleak.IgnoreAnyFunction
```

For methods, the fully qualified form looks like:

```
go.uber.org/goleak.(*MyType).MyMethod
```

#### added in v1.1.0

```
func IgnoreCurrent() Option
```

IgnoreCurrent records all current goroutines when the option is created, and ignores them in any future Find/Verify calls.

#### func IgnoreTopFunction ¶

```
func IgnoreTopFunction(f string) Option
```

IgnoreTopFunction ignores any goroutines where the specified function is at the top of the stack. The function name should be fully qualified, e.g., go.uber.org/goleak.IgnoreTopFunction

#### type TestingM ¶

```
type TestingM interface {
    Run() int
}
```

TestingM is the minimal subset of testing.M that we use.

#### type TestingT ¶

```
type TestingT interface {
    Error(...interface{})
}
```

TestingT is the minimal subset of testing.TB that we use.

## Directories

| Path | Synopsis |
| --- | --- |
| internal |  |