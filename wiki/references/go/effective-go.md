---
title: "Effective Go"
category: references
tags: [go, effective-go, style-guide, canonical, reference]
sources:
  - "wiki/_raw/Effective Go - The Go Programming Language.md"
summary: "Effective Go — o guia canônico da linguagem Go, cobrindo formatação, nomes, estruturas de controle, funções, dados, métodos, interfaces, concorrência e erros."
provenance:
  extracted: 1.00
  inferred: 0.00
  ambiguous: 0.00
base_confidence: 0.98
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: core
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
---

# Effective Go

> [!tldr] Documento canônico da linguagem Go. Escrito originalmente para Go 1.0 (2009), não cobre generics, módulos ou bibliotecas recentes. Para mudanças, veja [release notes](https://go.dev/doc/devel/release).

**Fonte**: [go.dev/doc/effective_go](https://go.dev/doc/effective_go)

> **Nota**: Este documento foi escrito para Go's release em 2009 e não é ativamente atualizado. Embora continue sendo um bom guia para usar a linguagem core, ele não cobre mudanças significativas (generics), ecossistema (modules), ou bibliotecas adicionadas desde então. Veja [issue 28782](https://go.dev/issue/28782).

---

## Introduction

Go is an open-source programming language that focuses on simplicity, reliability, and efficiency, specifically designed to make it easy to build software at scale. To write Go well, it's important to understand its properties and idioms. It's also important to know the established conventions for programming in Go, such as naming, formatting, program construction, and so on.

This document gives tips for writing clear, idiomatic Go code. It augments the [language specification](https://go.dev/ref/spec), the [Tour of Go](https://go.dev/tour/), and [How to Write Go Code](https://go.dev/doc/code.html).

---

## Formatting

With Go we take an unusual approach and let the machine take care of most formatting issues. The `gofmt` program reads a Go program and emits the source in a standard style of indentation and vertical alignment, retaining and if necessary reformatting comments. If you want to know how to handle some new layout situation, run `gofmt`; if the answer doesn't seem right, rearrange your program, don't work around it.

Key formatting points:
- Use tabs for indentation; `gofmt` emits them by default
- No line length limit — wrap when it feels right
- Go has no semicolons; the lexer inserts them automatically

---

## Commentary

Go provides C-style `/* */` block comments and C++-style `//` line comments. Every package should have a package comment, a block comment preceding the package clause. Every exported name should have a doc comment.

Doc comments work best as complete sentences. The first sentence should be a one-sentence summary that starts with the name being declared:

```go
// Compile parses a regular expression and returns, if successful, a Regexp
// that can be used to match against text.
func Compile(str string) (*Regexp, error) { ... }
```

---

## Names

### Package Names
- Lowercase, single-word names; no underscores or mixedCaps
- Keep names short and concise
- Avoid `util`, `common`, `misc` — these are meaningless

### Getters
- Don't use `Get` prefix: use `Owner()` not `GetOwner()`
- Setter with `SetOwner()` is fine

### Interface Names
- One-method interfaces: method name + `er` suffix (`Reader`, `Writer`, `Formatter`)

### MixedCaps
- Use `MixedCaps` or `mixedCaps`, not underscores
- Unexported: `maxLength` not `MAX_LENGTH` or `max_length`

---

## Semicolons

Go's lexer uses a simple rule: if the last token before a newline is an identifier, basic literal, or one of `break continue fallthrough return ++ -- ) }`, the lexer inserts a semicolon. This means you cannot put the opening brace of a control structure on a new line.

---

## Control Structures

### If
Accepts an optional initialization statement:
```go
if err := file.Chmod(0664); err != nil {
    log.Print(err)
    return err
}
```

### For
Go's only looping construct:
```go
// Like C for
for init; condition; post { }

// Like C while
for condition { }

// Like C for(;;)
for { }

// Range
for key, value := range m { }
```

### Switch
Go's switch is more general: expressions need not be constants, cases evaluate top-to-bottom, and there's no automatic fallthrough.

### Type Switch
A switch that discovers the dynamic type of an interface variable:
```go
switch v := i.(type) {
case int:
    fmt.Printf("twice %v is %v\n", v, v*2)
case string:
    fmt.Printf("%q is %v bytes long\n", v, len(v))
default:
    fmt.Printf("I don't know about type %T!\n", v)
}
```

---

## Functions

### Multiple Return Values
Used extensively for returning both result and error:
```go
func nextInt(b []byte, i int) (int, int) {
    x := 0
    for ; i < len(b); i++ {
        x = x*10 + int(b[i]) - '0'
    }
    return x, i
}
```

### Named Result Parameters
Can be named; act as regular variables initialized to zero:
```go
func ReadFull(r Reader, buf []byte) (n int, err error) {
    for len(buf) > 0 && err == nil {
        var nr int
        nr, err = r.Read(buf)
        n += nr
        buf = buf[nr:]
    }
    return
}
```

### Defer
Schedules a function call to run after the function completes. Arguments are evaluated when `defer` is executed:
```go
func Contents(filename string) (string, error) {
    f, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer f.Close()  // f.Close will run when we're finished
    // ...
}
```

---

## Data

### Allocation with `new`
`new(T)` allocates zeroed storage for a new item of type T and returns `*T`.

### Constructors and Composite Literals
Use composite literals to create new instances:
```go
a := [...]string{Enone: "no error", Eio: "Eio", Einval: "invalid argument"}
```

### Allocation with `make`
`make(T, args)` creates slices, maps, and channels only. It returns an initialized (not zeroed) value of type T, not `*T`.

### Arrays
Arrays are values. Assigning one array to another copies all elements. In Go, arrays are rarely used directly; use slices instead.

### Slices
Slices wrap arrays to give a more general, powerful, and convenient interface to sequences of data:
```go
var buf []byte
buf = append(buf, 'a', 'b', 'c')
```

### Maps
A convenient and powerful built-in data structure that associates values of one type (the key) with values of another type:
```go
timeZone := map[string]int{
    "UTC":  0*60*60,
    "EST": -5*60*60,
}
```

### Printing
Formatted printing in Go uses a style similar to C's `printf` family:
```go
fmt.Printf("Hello %d\n", 23)
fmt.Fprint(os.Stdout, "Hello ", 23, "\n")
```

### Append
`append` appends items to slices, growing the underlying array as needed:
```go
x := []int{1,2,3}
x = append(x, 4, 5, 6)
```

---

## Initialization

### Constants
Constants in Go are created at compile time. Iota generates successive values within a `const` declaration.

### Variables
Variables can be initialized like constants but the initializer can be a general expression computed at run time.

### The init function
Each source file can define its own niladic `init` function to set up whatever state is required. `init` is called after all variable declarations in the package have evaluated their initializers.

---

## Methods

### Pointers vs. Values
The rule about pointers vs. values for receivers is: value methods can be invoked on pointers and values, but pointer methods can only be invoked on pointers.

---

## Interfaces and Other Types

### Interfaces
Interfaces in Go provide a way to specify the behavior of an object. A type can implement multiple interfaces.

### Conversions
Sequence of conversions between types that share the same underlying type.

### Interface Conversions and Type Assertions
Type switches are a form of conversion: they take an interface and, for each case in the switch, convert it to the type of that case.

### The blank identifier
`_` serves as an anonymous placeholder. Used for unused imports, unused variables, and import for side effects.

---

## Embedding

Go does not provide the typical type-driven notion of subclassing, but it does have the ability to "borrow" pieces of an implementation by embedding types within a struct or interface:
```go
type ReadWriter struct {
    *Reader  // *bufio.Reader
    *Writer  // *bufio.Writer
}
```

---

## Concurrency

### Share by Communicating
Do not communicate by sharing memory; instead, share memory by communicating.

### Goroutines
A goroutine is a lightweight thread managed by the Go runtime. `go f(x, y, z)` starts a new goroutine running `f(x, y, z)`.

### Channels
Channels provide a way for two goroutines to communicate with each other and synchronize their execution:
```go
c := make(chan int)  // unbuffered
c := make(chan int, 10)  // buffered
```

### Channels of Channels
One of the most important properties of Go is that a channel is a first-class value.

### Parallelization
Use goroutines and channels to parallelize computation across multiple CPU cores.

---

## Errors

Library routines often return some sort of error indication. Go's multivalue return makes it easy to report an error without overloading the return value.

```go
f, err := os.Open("filename.ext")
if err != nil {
    log.Fatal(err)
}
```

The `error` type is a built-in interface:
```go
type error interface {
    Error() string
}
```

---

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-code-review|Go Code Review Checklist]] — Checklist sistemática
- [[go-naming|Go Naming]] — Convenções de nomes
- [[go-interfaces|Go Interfaces]] — Interfaces e composição
- [[go-error-handling|Go Error Handling]] — Tratamento de erros
- [[go-concurrency|Go Concurrency]] — Concorrência e goroutines
- [[go-testing|Go Testing]] — Padrões de teste
- [[references/go/go-code-review-rules|Code Review Rules]] — 59 regras do Uber Go Style Guide
