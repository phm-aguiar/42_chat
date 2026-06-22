---
title: "Go Code Review Rules — Uber Style Guide (59 Regras)"
category: references
tags: [go, style-guide, code-review, uber-guide, reference]
sources:
  - "wiki/_raw/01-intro.md" 
  - "wiki/_raw/02-interface-pointer.md"
  - "wiki/_raw/03-interface-compliance.md"
  - "wiki/_raw/04-interface-receiver.md"
  - "wiki/_raw/05-mutex-zero-value.md"
  - "wiki/_raw/06-container-copy.md"
  - "wiki/_raw/07-defer-clean.md"
  - "wiki/_raw/08-channel-size.md"
  - "wiki/_raw/09-enum-start.md"
  - "wiki/_raw/10-time.md"
  - "wiki/_raw/11-error-type.md"
  - "wiki/_raw/12-error-wrap.md"
  - "wiki/_raw/13-error-name.md"
  - "wiki/_raw/14-error-once.md"
  - "wiki/_raw/15-type-assert.md"
  - "wiki/_raw/16-panic.md"
  - "wiki/_raw/17-atomic.md"
  - "wiki/_raw/18-global-mut.md"
  - "wiki/_raw/19-embed-public.md"
  - "wiki/_raw/20-builtin-name.md"
  - "wiki/_raw/21-init.md"
  - "wiki/_raw/22-exit-main.md"
  - "wiki/_raw/23-exit-once.md"
  - "wiki/_raw/24-struct-tag.md"
  - "wiki/_raw/25-goroutine-forget.md"
  - "wiki/_raw/26-goroutine-exit.md"
  - "wiki/_raw/27-goroutine-init.md"
  - "wiki/_raw/28-performance.md"
  - "wiki/_raw/29-strconv.md"
  - "wiki/_raw/30-string-byte-slice.md"
  - "wiki/_raw/31-container-capacity.md"
  - "wiki/_raw/32-line-length.md"
  - "wiki/_raw/33-consistency.md"
  - "wiki/_raw/34-decl-group.md"
  - "wiki/_raw/35-import-group.md"
  - "wiki/_raw/36-package-name.md"
  - "wiki/_raw/37-function-name.md"
  - "wiki/_raw/38-import-alias.md"
  - "wiki/_raw/39-function-order.md"
  - "wiki/_raw/40-nest-less.md"
  - "wiki/_raw/41-else-unnecessary.md"
  - "wiki/_raw/42-global-decl.md"
  - "wiki/_raw/43-global-name.md"
  - "wiki/_raw/44-struct-embed.md"
  - "wiki/_raw/45-var-decl.md"
  - "wiki/_raw/46-slice-nil.md"
  - "wiki/_raw/47-var-scope.md"
  - "wiki/_raw/48-param-naked.md"
  - "wiki/_raw/49-string-escape.md"
  - "wiki/_raw/50-struct-field-key.md"
  - "wiki/_raw/51-struct-field-zero.md"
  - "wiki/_raw/52-struct-zero.md"
  - "wiki/_raw/53-struct-pointer.md"
  - "wiki/_raw/54-map-init.md"
  - "wiki/_raw/55-printf-const.md"
  - "wiki/_raw/56-printf-name.md"
  - "wiki/_raw/57-test-table.md"
  - "wiki/_raw/58-functional-option.md"
  - "wiki/_raw/59-lint.md"
summary: "Consolidação das 59 regras do Uber Go Style Guide (tradução PT-BR) com exemplos Ruim/Bom. Baseado no guia original de Prashant Varanasi e Simon Newton."
provenance:
  extracted: 0.98
  inferred: 0.02
  ambiguous: 0.00
base_confidence: 0.95
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: core
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
---

# Go Code Review Rules — 59 Regras do Uber Go Style Guide

> [!tldr] Consolidação completa das 59 regras do [Uber Go Style Guide](https://github.com/uber-go/guide) (tradução PT-BR), com exemplos de código Ruim vs Bom. Originalmente criado por [Prashant Varanasi](https://github.com/prashantv) e [Simon Newton](https://github.com/nomis52).

**Fontes canônicas**: [Effective Go](https://golang.org/doc/effective_go.html) · [Go Wiki CommonMistakes](https://go.dev/wiki/CommonMistakes) · [Go Wiki CodeReviewComments](https://github.com/golang/go/wiki/CodeReviewComments)

**Ferramentas**: `gofmt` · `goimports` · `golint` · `go vet` · `golangci-lint`

---

## Introdução

Estilos são as convenções que governam nosso código. O termo estilo é um pouco enganoso, pois essas convenções abrangem muito mais do que apenas a formatação de arquivos de origem — `gofmt` cuida disso para nós.

O objetivo deste guia é gerenciar essa complexidade descrevendo detalhadamente os (O que fazer e o que não fazer) de escrever código Go na Uber. Essas regras existem para manter a base de código gerenciável, permitindo ainda que os engenheiros usem os recursos da linguagem Go de maneira produtiva.

Todo o código deve estar sem erros ao passar por `golint` e `go vet`. Recomendamos configurar seu editor para:

- Executar `goimports` ao salvar
- Executar `golint` e `go vet` para verificar erros

---

## Regras

### 01 — Ponteiros para Interfaces

Você quase nunca precisa de um ponteiro para uma interface. Você deve estar passando interfaces como valores — os dados subjacentes ainda podem ser um ponteiro.

Uma interface possui dois campos:
1. Um ponteiro para alguma informação específica do tipo ("tipo").
2. Ponteiro de dados. Se os dados armazenados são um ponteiro, eles são armazenados diretamente. Se os dados armazenados são um valor, então um ponteiro para o valor é armazenado.

Se você deseja que os métodos da interface modifiquem os dados subjacentes, você deve usar um ponteiro.

---

### 02 — Verificar Conformidade de Interface

Verifique a conformidade de interface em tempo de compilação quando apropriado. Isso inclui:

- Tipos exportados que são obrigados a implementar interfaces específicas como parte do seu contrato de API
- Tipos exportados ou não exportados que fazem parte de uma coleção de tipos implementando a mesma interface
- Outros casos em que violar uma interface quebraria os usuários

**Ruim:**
```go
type Handler struct {
  // ...
}

func (h *Handler) ServeHTTP(
  w http.ResponseWriter,
  r *http.Request,
) {
  ...
}
```

**Bom:**
```go
type Handler struct {
  // ...
}

var _ http.Handler = (*Handler)(nil)

func (h *Handler) ServeHTTP(
  w http.ResponseWriter,
  r *http.Request,
) {
  // ...
}
```

A declaração `var _ http.Handler = (*Handler)(nil)` falhará na compilação se `*Handler` deixar de corresponder à interface `http.Handler`.

O lado direito da atribuição deve ser o valor zero do tipo afirmado. Isso é `nil` para tipos de ponteiro (como `*Handler`), slices e maps, e uma struct vazia para tipos de struct.

```go
type LogHandler struct {
  h   http.Handler
  log *zap.Logger
}

var _ http.Handler = LogHandler{}

func (h LogHandler) ServeHTTP(
  w http.ResponseWriter,
  r *http.Request,
) {
  // ...
}
```

---

### 03 — Receptores e Interfaces

Métodos com receptores de valor podem ser chamados em ponteiros, assim como em valores. Métodos com receptores de ponteiro só podem ser chamados em ponteiros ou [valores endereçáveis](https://golang.org/ref/spec#Method_values).

```go
type S struct {
  data string
}

func (s S) Read() string {
  return s.data
}

func (s *S) Write(str string) {
  s.data = str
}

// Não podemos obter ponteiros para valores armazenados em mapas, porque eles não são
// valores endereçáveis.
sVals := map[int]S{1: {"A"}}

// Podemos chamar o método Read em valores armazenados no mapa porque o método Read
// tem um receptor de valor, que não requer que o valor seja endereçável.
sVals[1].Read()

// Não podemos chamar o método Write em valores armazenados no mapa porque o método Write
// tem um receptor de ponteiro, e não é possível obter um ponteiro
// para um valor armazenado em um mapa.

sPtrs := map[int]*S{1: {"A"}}

// Podemos chamar tanto Read quanto Write se o mapa armazenar ponteiros,
// porque os ponteiros são intrinsecamente endereçáveis.
sPtrs[1].Read()
sPtrs[1].Write("test")
```

De forma semelhante, uma interface pode ser satisfeita por um ponteiro, mesmo que o método tenha um receptor de valor.

```go
type F interface {
  f()
}

type S1 struct{}
func (s S1) f() {}

type S2 struct{}
func (s *S2) f() {}

s1Val := S1{}
s1Ptr := &S1{}
s2Val := S2{}
s2Ptr := &S2{}

var i F
i = s1Val
i = s1Ptr
i = s2Ptr

// O seguinte não compila, já que s2Val é um valor, e não há um receptor de valor para f.
//   i = s2Val
```

O Effective Go tem uma boa explicação sobre [Ponteiros vs. Valores](https://golang.org/doc/effective_go.html#pointers_vs_values).

---

### 04 — Mutexes com Valor Zero são Válidos

O valor zero de `sync.Mutex` e `sync.RWMutex` é válido, então você quase nunca precisa de um ponteiro para um mutex.

**Ruim:**
```go
mu := new(sync.Mutex)
mu.Lock()
```

**Bom:**
```go
var mu sync.Mutex
mu.Lock()
```

Se você usar uma struct por ponteiro, então o mutex deve ser um campo não ponteiro nele. Não aninhe o mutex na struct, mesmo que a struct não seja exportada.

**Ruim:**
```go
type SMap struct {
  sync.Mutex
  data map[string]string
}

func NewSMap() *SMap {
  return &SMap{
    data: make(map[string]string),
  }
}

func (m *SMap) Get(k string) string {
  m.Lock()
  defer m.Unlock()
  return m.data[k]
}
```

**Bom:**
```go
type SMap struct {
  mu sync.Mutex
  data map[string]string
}

func NewSMap() *SMap {
  return &SMap{
    data: make(map[string]string),
  }
}

func (m *SMap) Get(k string) string {
  m.mu.Lock()
  defer m.mu.Unlock()
  return m.data[k]
}
```

O campo `Mutex`, e os métodos `Lock` e `Unlock` fazem parte involuntariamente da API exportada de `SMap`. O mutex e seus métodos devem ser detalhes de implementação ocultos de seus chamadores.

---

### 05 — Copie Slices e Maps nos Limites

Slices e maps contêm ponteiros para os dados subjacentes, então tenha cuidado com cenários em que eles precisam ser copiados.

**Recebendo Slices e Maps:**

**Ruim:**
```go
func (d *Driver) SetTrips(trips []Trip) {
  d.trips = trips
}

trips := ...
d1.SetTrips(trips)
// Você quis dizer modificar d1.trips?
trips[0] = ...
```

**Bom:**
```go
func (d *Driver) SetTrips(trips []Trip) {
  d.trips = make([]Trip, len(trips))
  copy(d.trips, trips)
}

trips := ...
d1.SetTrips(trips)
// Agora podemos modificar trips[0] sem afetar d1.trips.
trips[0] = ...
```

**Retornando Slices e Maps:**

**Ruim:**
```go
type Stats struct {
  mu sync.Mutex
  counters map[string]int
}

func (s *Stats) Snapshot() map[string]int {
  s.mu.Lock()
  defer s.mu.Unlock()
  return s.counters
}

// snapshot não está mais protegido pelo mutex, então qualquer
// acesso ao snapshot está sujeito a corridas de dados.
snapshot := stats.Snapshot()
```

**Bom:**
```go
type Stats struct {
  mu sync.Mutex
  counters map[string]int
}

func (s *Stats) Snapshot() map[string]int {
  s.mu.Lock()
  defer s.mu.Unlock()
  result := make(map[string]int, len(s.counters))
  for k, v := range s.counters {
    result[k] = v
  }
  return result
}

// Snapshot agora é uma cópia.
snapshot := stats.Snapshot()
```

---

### 06 — Utilize Defer para Limpeza

Use defer para limpar recursos como arquivos e travas.

**Ruim:**
```go
p.Lock()
if p.count < 10 {
  p.Unlock()
  return p.count
}

p.count++
newCount := p.count
p.Unlock()

return newCount
// fácil perder desbloqueios devido a múltiplos retornos
```

**Bom:**
```go
p.Lock()
defer p.Unlock()

if p.count < 10 {
  return p.count
}

p.count++
return p.count
// mais legível
```

O defer tem uma sobrecarga extremamente pequena e deve ser evitado apenas se você puder provar que o tempo de execução da sua função está na ordem de nanossegundos. O ganho de legibilidade ao usar defers vale o custo minúsculo de usá-los. Isso é especialmente verdadeiro para métodos maiores que têm mais do que simples acessos à memória.

---

### 07 — Tamanho do Canal é Um ou Nenhum

Os canais geralmente devem ter um tamanho de um ou serem não armazenados em buffer. Por padrão, os canais não são armazenados em buffer e têm um tamanho de zero. Qualquer outro tamanho deve ser sujeito a um alto nível de escrutínio.

**Ruim:**
```go
// Deve ser suficiente para qualquer pessoa!
c := make(chan int, 64)
```

**Bom:**
```go
// Tamanho de um
c := make(chan int, 1) // ou
// Canal não armazenado em buffer, tamanho zero
c := make(chan int)
```

---

### 08 — Inicie Enums em Um

A maneira padrão de introduzir enumerações em Go é declarar um tipo personalizado e um grupo `const` com `iota`. Como as variáveis têm um valor padrão de 0, você normalmente deve começar suas enums com um valor não nulo.

**Ruim:**
```go
type Operation int

const (
  Add Operation = iota
  Subtract
  Multiply
)
// Add=0, Subtract=1, Multiply=2
```

**Bom:**
```go
type Operation int

const (
  Add Operation = iota + 1
  Subtract
  Multiply
)
// Add=1, Subtract=2, Multiply=3
```

Existem casos em que usar o valor zero faz sentido, por exemplo, quando o caso de valor zero é o comportamento padrão desejado:

```go
type LogOutput int

const (
  LogToStdout LogOutput = iota
  LogToFile
  LogToRemote
)
// LogToStdout=0, LogToFile=1, LogToRemote=2
```

---

### 09 — Use `"time"` para lidar com o tempo

O tempo é complicado. Suposições incorretas frequentemente feitas sobre o tempo incluem:
1. Um dia tem 24 horas.
2. Uma hora tem 60 minutos.
3. Uma semana tem 7 dias.
4. Um ano tem 365 dias.
5. [E muitos outros](https://infiniteundo.com/post/25326999628/falsehoods-programmers-believe-about-time)

Portanto, sempre use o pacote [`"time"`](https://golang.org/pkg/time/) ao lidar com o tempo.

**Use `time.Time` para instantes de tempo:**

**Ruim:**
```go
func isActive(now, start, stop int) bool {
  return start <= now && now < stop
}
```

**Bom:**
```go
func isActive(now, start, stop time.Time) bool {
  return (start.Before(now) || start.Equal(now)) && now.Before(stop)
}
```

**Use `time.Duration` para períodos de tempo:**

**Ruim:**
```go
func poll(delay int) {
  for {
    // ...
    time.Sleep(time.Duration(delay) * time.Millisecond)
  }
}
poll(10) // eram segundos ou milissegundos?
```

**Bom:**
```go
func poll(delay time.Duration) {
  for {
    // ...
    time.Sleep(delay)
  }
}
poll(10*time.Second)
```

**Use `time.Time` e `time.Duration` com sistemas externos:**

Use `time.Duration` e `time.Time` em interações com sistemas externos sempre que possível:
- Flags da linha de comando: [`flag`](https://golang.org/pkg/flag/) suporta `time.Duration`
- JSON: [`encoding/json`](https://golang.org/pkg/encoding/json/) suporta `time.Time` como string [RFC 3339](https://tools.ietf.org/html/rfc3339)
- SQL: [`database/sql`](https://golang.org/pkg/database/sql/) suporta conversão de `DATETIME`/`TIMESTAMP`
- YAML: [`gopkg.in/yaml.v2`](https://godoc.org/gopkg.in/yaml.v2) suporta `time.Time` como RFC 3339

Quando não for possível usar `time.Duration`, use `int` ou `float64` e inclua a unidade no nome do campo:

**Ruim:**
```go
// {"interval": 2}
type Config struct {
  Interval int `json:"interval"`
}
```

**Bom:**
```go
// {"intervalMillis": 2000}
type Config struct {
  IntervalMillis int `json:"intervalMillis"`
}
```

---

### 10 — Tipos de Erro

Existem poucas opções para declarar erros. Considere o seguinte antes de escolher:

| Corresponder ao Erro? | Mensagem de Erro | Orientação |
|---|---|---|
| Não | estática | [`errors.New`](https://golang.org/pkg/errors/#New) |
| Não | dinâmica | [`fmt.Errorf`](https://golang.org/pkg/fmt/#Errorf) |
| Sim | estática | `var` no nível superior com `errors.New` |
| Sim | dinâmica | tipo de erro personalizado |

**Sem correspondência de erro:**
```go
// package foo
func Abrir() error {
  return errors.New("não foi possível abrir")
}

// package bar
if err := foo.Abrir(); err != nil {
  panic("erro desconhecido")
}
```

**Com correspondência de erro:**
```go
// package foo
var ErrNaoFoiPossivelAbrir = errors.New("não foi possível abrir")

func Abrir() error {
  return ErrNaoFoiPossivelAbrir
}

// package bar
if err := foo.Abrir(); err != nil {
  if errors.Is(err, foo.ErrNaoFoiPossivelAbrir) {
    // manipular o erro
  } else {
    panic("erro desconhecido")
  }
}
```

**Erro dinâmico com tipo personalizado:**
```go
// package foo
type ErroNaoEncontrado struct {
  Arquivo string
}

func (e *ErroNaoEncontrado) Error() string {
  return fmt.Sprintf("arquivo %q não encontrado", e.Arquivo)
}

func Abrir(arquivo string) error {
  return &ErroNaoEncontrado{Arquivo: arquivo}
}

// package bar
if err := foo.Abrir("arquivoteste.txt"); err != nil {
  var naoEncontrado *foo.ErroNaoEncontrado
  if errors.As(err, &naoEncontrado) {
    // Manipular o erro
  } else {
    panic("erro desconhecido")
  }
}
```

---

### 11 — Envoltório de Erro

Existem três opções principais para propagar erros se uma chamada falhar:

- Retornar o erro original como está
- Adicionar contexto com `fmt.Errorf` e o verbo `%w`
- Adicionar contexto com `fmt.Errorf` e o verbo `%v`

Use `%w` se o chamador deve ter acesso ao erro subjacente. Use `%v` para obscurecer o erro subjacente.

Ao adicionar contexto a erros retornados, mantenha o contexto sucinto, evitando frases como "falha ao":

**Ruim:**
```go
s, err := store.New()
if err != nil {
    return fmt.Errorf(
        "ao criar novo armazenamento: %w", err)
}
```

**Bom:**
```go
s, err := store.New()
if err != nil {
    return fmt.Errorf(
        "novo armazenamento: %w", err)
}
```

---

### 12 — Nomeação de Erros

Para valores de erro armazenados como variáveis globais, use o prefixo `Err` ou `err` dependendo se eles são exportados:

```go
var (
  // Exportados para uso com errors.Is
  ErrLinkQuebrado = errors.New("link quebrado")
  ErrNaoFoiPossivelAbrir = errors.New("não foi possível abrir")

  // Não exportado — uso interno
  errNaoEncontrado = errors.New("não encontrado")
)
```

Para tipos de erro personalizados, use o sufixo `Error`:

```go
type ErroNaoEncontrado struct {
  Arquivo string
}

func (e *ErroNaoEncontrado) Error() string {
  return fmt.Sprintf("arquivo %q não encontrado", e.Arquivo)
}

// Não exportado
type erroResolucao struct {
  Caminho string
}

func (e *erroResolucao) Error() string {
  return fmt.Sprintf("resolver %q", e.Caminho)
}
```

---

### 13 — Lide com os Erros Apenas uma Vez

Quando um chamador recebe um erro de um chamado, ele pode tratá-lo de várias maneiras diferentes dependendo do que sabe sobre o erro. Independentemente de como o chamador lida com o erro, ele deve geralmente lidar com cada erro apenas uma vez.

**Ruim: Registrar o erro e retorná-lo**
```go
u, err := getUser(id)
if err != nil {
  // Ruim: gera muito ruído nos logs
  log.Printf("Não foi possível obter o usuário %q: %v", id, err)
  return err
}
```

**Bom: Encapsule o erro e o retorne**
```go
u, err := getUser(id)
if err != nil {
  return fmt.Errorf("obter usuário %q: %w", id, err)
}
```

**Bom: Registre o erro e degrade graciosamente**
```go
if err := emitMetrics(); err != nil {
  // Falha ao escrever métricas não deve quebrar a aplicação.
  log.Printf("Não foi possível emitir métricas: %v", err)
}
```

**Bom: Corresponda ao erro e degrade graciosamente**
```go
tz, err := getUserTimeZone(id)
if err != nil {
  if errors.Is(err, ErrUsuarioNaoEncontrado) {
    // Usuário não existe. Use o UTC.
    tz = time.UTC
  } else {
    return fmt.Errorf("obter usuário %q: %w", id, err)
  }
}
```

---

### 14 — Lidar com Falhas na Asserção de Tipo

A forma de retorno único de uma [asserção de tipo](https://golang.org/ref/spec#Type_assertions) gerará um pânico em um tipo incorreto. Portanto, sempre utilize o "idioma do 'comma ok'".

**Ruim:**
```go
t := i.(string)
```

**Bom:**
```go
t, ok := i.(string)
if !ok {
  // lidar com o erro de forma adequada
}
```

---

### 15 — Não entre em Pânico

Código em produção deve evitar panics. Panics são uma fonte principal de [falhas em cascata](https://en.wikipedia.org/wiki/Cascading_failure). Se ocorrer um erro, a função deve retornar um erro e permitir que o chamador decida como lidar com ele.

**Ruim:**
```go
func run(args []string) {
  if len(args) == 0 {
    panic("é necessário um argumento")
  }
  // ...
}

func main() {
  run(os.Args[1:])
}
```

**Bom:**
```go
func run(args []string) error {
  if len(args) == 0 {
    return errors.New("é necessário um argumento")
  }
  // ...
  return nil
}

func main() {
  if err := run(os.Args[1:]); err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
  }
}
```

Panic/recover não é uma estratégia de tratamento de erros. Mesmo nos testes, prefira `t.Fatal` ou `t.FailNow` em vez de panics.

**Ruim em testes:**
```go
f, err := os.CreateTemp("", "test")
if err != nil {
  panic("falha ao configurar o teste")
}
```

**Bom em testes:**
```go
f, err := os.CreateTemp("", "test")
if err != nil {
  t.Fatal("falha ao configurar o teste")
}
```

---

### 16 — Use go.uber.org/atomic

Operações atômicas com o pacote [sync/atomic](https://golang.org/pkg/sync/atomic/) operam nos tipos brutos (`int32`, `int64`, etc.), então é fácil esquecer de usar a operação atômica para ler ou modificar as variáveis. [go.uber.org/atomic](https://godoc.org/go.uber.org/atomic) adiciona segurança de tipo a essas operações.

**Ruim:**
```go
type foo struct {
  running int32  // atômico
}

func (f *foo) start() {
  if atomic.SwapInt32(&f.running, 1) == 1 {
     return
  }
}

func (f *foo) isRunning() bool {
  return f.running == 1  // corrida!
}
```

**Bom:**
```go
type foo struct {
  running atomic.Bool
}

func (f *foo) start() {
  if f.running.Swap(true) {
     return
  }
}

func (f *foo) isRunning() bool {
  return f.running.Load()
}
```

---

### 17 — Evite Variáveis Globais Mutáveis

Evite mutar variáveis globais, optando em vez disso pela injeção de dependência. Isso se aplica a ponteiros de funções, assim como outros tipos de valores.

**Ruim:**
```go
// sign.go
var _timeNow = time.Now

func sign(msg string) string {
  now := _timeNow()
  return signWithTime(msg, now)
}

// sign_test.go
func TestSign(t *testing.T) {
  oldTimeNow := _timeNow
  _timeNow = func() time.Time { return someFixedTime }
  defer func() { _timeNow = oldTimeNow }()
  assert.Equal(t, want, sign(give))
}
```

**Bom:**
```go
// sign.go
type signer struct {
  now func() time.Time
}

func newSigner() *signer {
  return &signer{now: time.Now}
}

func (s *signer) Sign(msg string) string {
  now := s.now()
  return signWithTime(msg, now)
}

// sign_test.go
func TestSigner(t *testing.T) {
  s := newSigner()
  s.now = func() time.Time { return someFixedTime }
  assert.Equal(t, want, s.Sign(give))
}
```

---

### 18 — Evite Incorporar Tipos em Structs Públicas

Esses tipos incorporados vazam detalhes de implementação, inibem a evolução do tipo e obscurecem a documentação.

**Ruim:**
```go
type ConcreteList struct {
  *AbstractList
}
```

**Bom:**
```go
type ConcreteList struct {
  list *AbstractList
}

func (l *ConcreteList) Add(e Entity) {
  l.list.Add(e)
}

func (l *ConcreteList) Remove(e Entity) {
  l.list.Remove(e)
}
```

Go permite [incorporação de tipos](https://golang.org/doc/effective_go.html#embedding) como um compromisso entre herança e composição. Um tipo incorporado raramente é necessário. É uma conveniência que ajuda a evitar a escrita de métodos delegados tediosos.

Mesmo incorporar uma interface compatível, em vez da struct, ofereceria ao desenvolvedor mais flexibilidade para mudanças no futuro, mas ainda vazaria o detalhe de que as listas concretas usam uma implementação abstrata.

Quer seja com uma struct incorporada ou uma interface incorporada, o tipo incorporado impõe limites à evolução do tipo:
- Adicionar métodos a uma interface incorporada é uma mudança que quebra a compatibilidade.
- Remover métodos de uma struct incorporada é uma mudança que quebra a compatibilidade.
- Remover o tipo incorporado é uma mudança que quebra a compatibilidade.
- Substituir o tipo incorporado é uma mudança que quebra a compatibilidade.

---

### 19 — Evite Usar Nomes Embutidos

A [especificação da linguagem Go](https://golang.org/ref/spec) delineia vários identificadores embutidos que não devem ser usados como nomes em programas Go. Reutilizar esses identificadores como nomes irá sombrear o original.

**Ruim:**
```go
var erro string
// `erro` sombreia o embutido

func lidarComMensagemDeErro(erro string) {
    // `erro` sombreia o embutido
}
```

**Bom:**
```go
var mensagemDeErro string
// `erro` se refere ao embutido

func lidarComMensagemDeErro(msg string) {
    // `erro` se refere ao embutido
}
```

Observe que o compilador não gerará erros ao usar identificadores predefinidos, mas ferramentas como `go vet` devem apontar corretamente esses casos.

---

### 20 — Evite `init()`

Evite `init()` sempre que possível. Quando `init()` é inevitável ou desejável, o código deve tentar:

1. Ser completamente determinístico, independentemente do ambiente ou invocação do programa.
2. Evitar depender da ordem ou efeitos colaterais de outras funções `init()`.
3. Evitar acessar ou manipular o estado global ou de ambiente.
4. Evitar I/O, incluindo chamadas de sistema de arquivos, de rede e do sistema.

**Ruim:**
```go
type Foo struct { /* ... */ }

var _defaultFoo Foo

func init() {
    _defaultFoo = Foo{ /* ... */ }
}
```

**Bom:**
```go
var _defaultFoo = Foo{ /* ... */ }

// ou, melhor, para testabilidade:
var _defaultFoo = defaultFoo()

func defaultFoo() Foo {
    return Foo{ /* ... */ }
}
```

---

### 21 — Sair no Main

Programas Go utilizam [`os.Exit`](https://golang.org/pkg/os/#Exit) ou [`log.Fatal*`](https://golang.org/pkg/log/#Fatal) para sair imediatamente. Chame um dos `os.Exit` ou `log.Fatal*` **apenas em `main()`**. Todas as outras funções devem retornar erros para sinalizar falha.

**Ruim:**
```go
func main() {
  body := readFile(path)
  fmt.Println(body)
}

func readFile(path string) string {
  f, err := os.Open(path)
  if err != nil { log.Fatal(err) }
  b, err := io.ReadAll(f)
  if err != nil { log.Fatal(err) }
  return string(b)
}
```

**Bom:**
```go
func main() {
  body, err := readFile(path)
  if err != nil { log.Fatal(err) }
  fmt.Println(body)
}

func readFile(path string) (string, error) {
  f, err := os.Open(path)
  if err != nil { return "", err }
  b, err := io.ReadAll(f)
  if err != nil { return "", err }
  return string(b), nil
}
```

**Justificativa**: Programas com várias funções que encerram apresentam problemas:
- Fluxo de controle não óbvio
- Difícil de testar
- Falta de limpeza (defer não é executado)

---

### 22 — Encerrar Apenas uma Vez

Se possível, prefira chamar `os.Exit` ou `log.Fatal` **no máximo uma vez** em seu `main()`. Se houver vários cenários de erro que interrompem a execução do programa, coloque essa lógica em uma função separada e retorne erros dela.

**Ruim:**
```go
func main() {
  args := os.Args[1:]
  if len(args) != 1 {
    log.Fatal("arquivo ausente")
  }
  f, err := os.Open(args[0])
  if err != nil { log.Fatal(err) }
  defer f.Close()
  // ...
}
```

**Bom:**
```go
func main() {
  if err := run(); err != nil {
    log.Fatal(err)
  }
}

func run() error {
  args := os.Args[1:]
  if len(args) != 1 {
    return errors.New("arquivo ausente")
  }
  f, err := os.Open(args[0])
  if err != nil { return err }
  defer f.Close()
  // ...
  return nil
}
```

---

### 23 — Use tags de campo em structs serializadas

Qualquer campo de estrutura que seja serializado em JSON, YAML, ou outros formatos que suportam a nomenclatura de campo baseada em tags deve ser anotado com a tag relevante.

**Ruim:**
```go
type Stock struct {
  Price int
  Name  string
}

bytes, err := json.Marshal(Stock{Price: 137, Name: "UBER"})
```

**Bom:**
```go
type Stock struct {
  Price int    `json:"price"`
  Name  string `json:"name"`
  // Seguro renomear Name para Symbol.
}

bytes, err := json.Marshal(Stock{Price: 137, Name: "UBER"})
```

**Justificativa**: A forma serializada da estrutura é um contrato entre diferentes sistemas. Alterações na estrutura da forma serializada quebram esse contrato.

---

### 24 — Não dispare e esqueça goroutines

Goroutines são leves, mas não são gratuitas: no mínimo, elas consomem memória para suas pilhas e CPU para serem agendadas. Não vaze goroutines em código de produção. Use [go.uber.org/goleak](https://pkg.go.dev/go.uber.org/goleak) para testar vazamentos de goroutine.

Em geral, cada goroutine:
- Deve ter um momento previsível em que ela vai parar de ser executada; ou
- Deve haver uma maneira de sinalizar para a goroutine que ela deve parar

**Ruim:**
```go
go func() {
  for {
    flush()
    time.Sleep(delay)
  }
}()
```

**Bom:**
```go
var (
  stop = make(chan struct{})
  done = make(chan struct{})
)
go func() {
  defer close(done)
  ticker := time.NewTicker(delay)
  defer ticker.Stop()
  for {
    select {
    case <-ticker.C:
      flush()
    case <-stop:
      return
    }
  }
}()

// Em outro lugar...
close(stop)  // sinaliza para a goroutine parar
<-done       // e espera ela sair
```

---

### 25 — Aguarde as goroutines terminarem

Dada uma goroutine iniciada pelo sistema, deve haver uma maneira de aguardar a saída da goroutine.

**Use `sync.WaitGroup` para múltiplas goroutines:**
```go
var wg sync.WaitGroup
for i := 0; i < N; i++ {
  wg.Add(1)
  go func() {
    defer wg.Done()
    // ...
  }()
}
wg.Wait()
```

**Use `chan struct{}` para uma única goroutine:**
```go
done := make(chan struct{})
go func() {
  defer close(done)
  // ...
}()

<-done  // Aguarda a goroutine terminar
```

---

### 26 — Sem goroutines em `init()`

Funções `init()` não devem criar goroutines. Se um pacote precisa de uma goroutine em segundo plano, ele deve expor um objeto responsável por gerenciar a vida útil da goroutine.

**Ruim:**
```go
func init() {
  go doWork()
}

func doWork() {
  for { /* ... */ }
}
```

**Bom:**
```go
type Worker struct{ /* ... */ }

func NewWorker(...) *Worker {
  w := &Worker{
    stop: make(chan struct{}),
    done: make(chan struct{}),
  }
  go w.doWork()
  return w
}

func (w *Worker) doWork() {
  defer close(w.done)
  for {
    select {
    case <-w.stop:
      return
    default:
      // ...
    }
  }
}

func (w *Worker) Shutdown() {
  close(w.stop)
  <-w.done
}
```

---

### 27 — Desempenho

As diretrizes específicas de desempenho se aplicam apenas ao caminho crítico.

---

### 28 — Prefira strconv em vez de fmt

Ao converter primitivos de/para strings, `strconv` é mais rápido do que `fmt`.

**Ruim:**
```go
for i := 0; i < b.N; i++ {
  s := fmt.Sprint(rand.Int())
}
```

**Bom:**
```go
for i := 0; i < b.N; i++ {
  s := strconv.Itoa(rand.Int())
}
```

---

### 29 — Evite conversões repetidas de string para byte

Não crie slices de bytes a partir de uma string fixa repetidamente. Em vez disso, faça a conversão uma vez e capture o resultado.

**Ruim:**
```go
for i := 0; i < b.N; i++ {
  w.Write([]byte("Hello world"))
}
```

**Bom:**
```go
data := []byte("Hello world")
for i := 0; i < b.N; i++ {
  w.Write(data)
}
```

---

### 30 — Prefira Especificar a Capacidade do Contêiner

Especifique a capacidade do contêiner sempre que possível para alocar memória para o contêiner antecipadamente. Isso minimiza alocações subsequentes.

**Especificando Dicas de Capacidade para Mapas:**

**Ruim:**
```go
m := make(map[string]os.FileInfo)
files, _ := os.ReadDir("./files")
for _, f := range files {
    m[f.Name()] = f
}
```

**Bom:**
```go
files, _ := os.ReadDir("./files")
m := make(map[string]os.DirEntry, len(files))
for _, f := range files {
    m[f.Name()] = f
}
```

**Especificando a Capacidade de um Slice:**

**Ruim:**
```go
for n := 0; n < b.N; n++ {
  data := make([]int, 0)
  for k := 0; k < size; k++{
    data = append(data, k)
  }
}
```

**Bom:**
```go
for n := 0; n < b.N; n++ {
  data := make([]int, 0, size)
  for k := 0; k < size; k++{
    data = append(data, k)
  }
}
```

---

### 31 — Evite linhas excessivamente longas

Evite linhas de código que exijam que os leitores rolem horizontalmente ou virem muito a cabeça. Recomendamos um limite de comprimento de linha suave de **99 caracteres**. Os autores devem tentar quebrar as linhas antes de atingir esse limite, mas não é um limite rígido.

---

### 32 — Seja Consistente

Algumas das diretrizes delineadas neste documento podem ser avaliadas objetivamente; outras são situacionais, contextuais ou subjetivas. Acima de tudo, **seja consistente**.

Código consistente é mais fácil de manter, é mais fácil de racionalizar, requer menos carga cognitiva e é mais fácil de migrar ou atualizar. Ao aplicar essas diretrizes a um código, é recomendado que as alterações sejam feitas em um nível de pacote (ou superior).

---

### 33 — Agrupe Declarações Semelhantes

Go suporta a agrupação de declarações semelhantes.

**Ruim:**
```go
import "a"
import "b"

const a = 1
const b = 2

var a = 1
var b = 2

type Area float64
type Volume float64
```

**Bom:**
```go
import (
  "a"
  "b"
)

const (
  a = 1
  b = 2
)

var (
  a = 1
  b = 2
)

type (
  Area float64
  Volume float64
)
```

Agrupe apenas declarações relacionadas. Não agrupe declarações que não têm relação entre si.

---

### 34 — Ordem de Agrupamento de Importações

Deve haver dois grupos de importações:
- Biblioteca padrão
- Todo o resto

Este é o agrupamento aplicado pelo goimports por padrão.

**Ruim:**
```go
import (
  "fmt"
  "os"
  "go.uber.org/atomic"
  "golang.org/x/sync/errgroup"
)
```

**Bom:**
```go
import (
  "fmt"
  "os"

  "go.uber.org/atomic"
  "golang.org/x/sync/errgroup"
)
```

---

### 35 — Nomes de Pacotes

Ao nomear pacotes, escolha um nome que seja:
- Todo em minúsculas. Sem maiúsculas ou sublinhados.
- Não precisa ser renomeado usando imports nomeados na maioria dos locais de chamada.
- Curto e sucinto.
- Não plural. Por exemplo, `net/url`, não `net/urls`.
- Não "comum" (common), "util", "compartilhado" (shared) ou "lib".

---

### 36 — Nomes de Funções

Seguimos a convenção da comunidade Go de usar [MixedCaps para nomes de funções](https://golang.org/doc/effective_go.html#mixed-caps). Uma exceção é feita para funções de teste, que podem conter underscores com o propósito de agrupar casos de teste relacionados, por exemplo, `TestMinhaFuncao_OQueEstaSendoTestado`.

---

### 37 — Alias de Importação

O alias de importação deve ser usado se o nome do pacote não corresponder ao último elemento do caminho de importação.

```go
import (
  "net/http"

  client "example.com/client-go"
  trace "example.com/trace/v2"
)
```

Em todos os outros cenários, o uso de alias de importação deve ser evitado, a menos que haja um conflito direto entre importações.

**Ruim:**
```go
import (
  "fmt"
  "os"
  runtimetrace "runtime/trace"
  nettrace "golang.net/x/trace"
)
```

**Bom:**
```go
import (
  "fmt"
  "os"
  "runtime/trace"

  nettrace "golang.net/x/trace"
)
```

---

### 38 — Agrupamento e Ordenação de Funções

- As funções devem ser ordenadas de acordo com a ordem de chamada aproximada.
- As funções em um arquivo devem ser agrupadas pelo receptor.

Portanto, as funções exportadas devem aparecer primeiro em um arquivo, após definições de `struct`, `const`, `var`. Um `newXYZ()`/`NewXYZ()` pode aparecer após o tipo ser definido, mas antes do resto dos métodos no receptor.

**Ruim:**
```go
func (s *something) Cost() {
  return calcCost(s.weights)
}

type something struct{ ... }

func calcCost(n []int) int {...}

func (s *something) Stop() {...}

func newSomething() *something {
    return &something{}
}
```

**Bom:**
```go
type something struct{ ... }

func newSomething() *something {
    return &something{}
}

func (s *something) Cost() {
  return calcCost(s.weights)
}

func (s *something) Stop() {...}

func calcCost(n []int) int {...}
```

---

### 39 — Reduza o Aninhamento

O código deve reduzir o aninhamento sempre que possível, lidando com casos de erro/condições especiais primeiro e retornando cedo ou continuando o loop.

**Ruim:**
```go
for _, v := range data {
  if v.F1 == 1 {
    v = process(v)
    if err := v.Call(); err == nil {
      v.Send()
    } else {
      return err
    }
  } else {
    log.Printf("Inválido v: %v", v)
  }
}
```

**Bom:**
```go
for _, v := range data {
  if v.F1 != 1 {
    log.Printf("Inválido v: %v", v)
    continue
  }

  v = process(v)
  if err := v.Call(); err != nil {
    return err
  }
  v.Send()
}
```

---

### 40 — Else Desnecessário

Se uma variável é definida em ambos os ramos de um if, pode ser substituído por um único if.

**Ruim:**
```go
var a int
if b {
  a = 100
} else {
  a = 10
}
```

**Bom:**
```go
a := 10
if b {
  a = 100
}
```

---

### 41 — Declarações de Variáveis no Nível Superior

No nível superior, use a palavra-chave padrão `var`. Não especifique o tipo, a menos que não seja o mesmo tipo que o da expressão.

**Ruim:**
```go
var _s string = F()

func F() string { return "A" }
```

**Bom:**
```go
var _s = F()
// Já que F já declara que retorna uma string, não precisamos especificar
// o tipo novamente.

func F() string { return "A" }
```

Especifique o tipo se o tipo da expressão não corresponder exatamente ao tipo desejado:

```go
type myError struct{}
func (myError) Error() string { return "error" }
func F() myError { return myError{} }

var _e error = F()
// F retorna um objeto do tipo myError, mas queremos um error.
```

---

### 42 — Prefixe Variáveis e Constantes Não Exportadas com _

Prefixe `var`s e `const`s não exportadas com `_` para deixar claro quando elas são símbolos globais.

**Ruim:**
```go
// foo.go
const (
  defaultPort = 8080
  defaultUser = "user"
)

// bar.go
func Bar() {
  defaultPort := 9090
  // ...
  fmt.Println("Default port", defaultPort)
}
```

**Bom:**
```go
// foo.go
const (
  _defaultPort = 8080
  _defaultUser = "user"
)
```

**Exceção**: Valores de erro não exportados podem usar o prefixo `err` sem o sublinhado. Consulte [Nomeação de Erros](#12--nomeação-de-erros).

---

### 43 — Incorporação em Estruturas

Tipos incorporados devem estar no topo da lista de campos de uma estrutura, e deve haver uma linha em branco separando campos incorporados de campos regulares.

**Ruim:**
```go
type Client struct {
  version int
  http.Client
}
```

**Bom:**
```go
type Client struct {
  http.Client

  version int
}
```

A incorporação deve fornecer benefícios tangíveis. A incorporação **não deve**:
- Ser puramente estética ou orientada à conveniência.
- Dificultar a construção ou utilização dos tipos externos.
- Afetar os valores zero dos tipos externos.
- Expor funções ou campos não relacionados.
- Expor tipos não exportados.
- Afetar a semântica de cópia.
- Alterar a API ou semântica do tipo externo.

Exceção: Mutexes não devem ser incorporados, mesmo em tipos não exportados.

---

### 44 — Declarações Locais de Variáveis

Declarações curtas de variáveis (`:=`) devem ser utilizadas se uma variável estiver sendo atribuída a algum valor explicitamente.

**Ruim:**
```go
var s = "foo"
```

**Bom:**
```go
s := "foo"
```

No entanto, há casos em que o valor padrão é mais claro quando a palavra-chave `var` é utilizada. Por exemplo, [Declarando Fatias Vazias](https://go.dev/wiki/CodeReviewComments#declaring-empty-slices).

**Ruim:**
```go
func f(list []int) {
  filtered := []int{}
  for _, v := range list {
    if v > 10 {
      filtered = append(filtered, v)
    }
  }
}
```

**Bom:**
```go
func f(list []int) {
  var filtered []int
  for _, v := range list {
    if v > 10 {
      filtered = append(filtered, v)
    }
  }
}
```

---

### 45 — nil é uma fatia válida

`nil` é uma fatia válida com comprimento 0. Isso significa que:

- Você não deve retornar explicitamente uma fatia de comprimento zero. Retorne `nil` em vez disso.

**Ruim:**
```go
if x == "" {
  return []int{}
}
```

**Bom:**
```go
if x == "" {
  return nil
}
```

- Para verificar se uma fatia está vazia, sempre use `len(s) == 0`. Não verifique `nil`.

**Ruim:**
```go
func isEmpty(s []string) bool {
  return s == nil
}
```

**Bom:**
```go
func isEmpty(s []string) bool {
  return len(s) == 0
}
```

- O valor zero (uma fatia declarada com `var`) pode ser usado imediatamente sem `make()`.

**Ruim:**
```go
nums := []int{}
if add1 { nums = append(nums, 1) }
if add2 { nums = append(nums, 2) }
```

**Bom:**
```go
var nums []int
if add1 { nums = append(nums, 1) }
if add2 { nums = append(nums, 2) }
```

---

### 46 — Reduza o Escopo de Variáveis

Sempre que possível, reduza o escopo das variáveis. Não reduza o escopo se isso entrar em conflito com [Reduzir o Aninhamento](#39--reduza-o-aninhamento).

**Ruim:**
```go
err := os.WriteFile(name, data, 0644)
if err != nil {
 return err
}
```

**Bom:**
```go
if err := os.WriteFile(name, data, 0644); err != nil {
 return err
}
```

Se você precisa do resultado de uma chamada de função fora do bloco `if`, então você não deve tentar reduzir o escopo.

---

### 47 — Evite Parâmetros Desnecessários

Parâmetros nus em chamadas de função podem prejudicar a legibilidade. Adicione comentários no estilo C (`/* ... */`) para os nomes dos parâmetros quando o significado deles não for óbvio.

**Ruim:**
```go
printInfo("foo", true, true)
```

**Bom:**
```go
printInfo("foo", true /* isLocal */, true /* done */)
```

Melhor ainda, substitua tipos `bool` nus por tipos personalizados:

```go
type Region int
const (
  UnknownRegion Region = iota
  Local
)

type Status int
const (
  StatusReady Status = iota + 1
  StatusDone
)

func printInfo(name string, region Region, status Status)
```

---

### 48 — Use Raw String Literals Para Evitar Sequências de Escape

Go suporta [literais de string "raw"](https://golang.org/ref/spec#raw_string_lit), que podem abranger várias linhas e incluir aspas.

**Ruim:**
```go
wantError := "unknown name:\"test\""
```

**Bom:**
```go
wantError := `unknown error:"test"`
```

---

### 49 — Use Nomes de Campos para Inicializar Estruturas

Você deve quase sempre especificar os nomes dos campos ao inicializar estruturas. Isso agora é aplicado por [`go vet`](https://golang.org/cmd/vet/).

**Ruim:**
```go
k := User{"John", "Doe", true}
```

**Bom:**
```go
k := User{
    FirstName: "John",
    LastName: "Doe",
    Admin: true,
}
```

Exceção: Os nomes dos campos *podem* ser omitidos em tabelas de teste quando houver 3 ou menos campos.

```go
tests := []struct{
  op Operation
  want string
}{
  {Add, "add"},
  {Subtract, "subtract"},
}
```

---

### 50 — Omitir Campos com Valor Zero em Estruturas

Ao inicializar estruturas com nomes de campos, omita os campos que têm valores zero a menos que forneçam contexto significativo.

**Ruim:**
```go
user := User{
  FirstName: "John",
  LastName: "Doe",
  MiddleName: "",
  Admin: false,
}
```

**Bom:**
```go
user := User{
  FirstName: "John",
  LastName: "Doe",
}
```

Inclua valores zero onde os nomes dos campos fornecem contexto significativo. Por exemplo, os casos de teste em tabelas de teste podem se beneficiar dos nomes dos campos mesmo quando têm valor zero.

---

### 51 — Use `var` para Estruturas com Valor Zero

Quando todos os campos de uma estrutura são omitidos em uma declaração, use a forma `var` para declarar a estrutura.

**Ruim:**
```go
user := User{}
```

**Bom:**
```go
var user User
```

Isso diferencia estruturas com valores zero daquelas com campos não nulos.

---

### 52 — Inicializando Referências de Estruturas

Use `&T{}` em vez de `new(T)` ao inicializar referências de estruturas para que seja consistente com a inicialização da estrutura.

**Ruim:**
```go
sval := T{Name: "foo"}
sptr := new(T)
sptr.Name = "bar"
```

**Bom:**
```go
sval := T{Name: "foo"}
sptr := &T{Name: "bar"}
```

---

### 53 — Inicializando Mapas

Prefira `make(..)` para mapas vazios e mapas populados programaticamente. Isso torna a inicialização do mapa visualmente diferente da declaração.

**Ruim:**
```go
var (
  m1 = map[T1]T2{}
  m2 map[T1]T2
)
```

**Bom:**
```go
var (
  m1 = make(map[T1]T2)
  m2 map[T1]T2
)
```

Se o mapa contiver um conjunto fixo de elementos, use literais de mapas para inicializá-lo.

**Ruim:**
```go
m := make(map[T1]T2, 3)
m[k1] = v1
m[k2] = v2
m[k3] = v3
```

**Bom:**
```go
m := map[T1]T2{
  k1: v1,
  k2: v2,
  k3: v3,
}
```

A regra básica é usar literais de mapas ao adicionar um conjunto fixo de elementos durante a inicialização; caso contrário, use `make` (e especifique uma dica de tamanho se disponível).

---

### 54 — Formate Strings fora do Printf

Se você declarar strings de formato para funções estilo `Printf` fora de um literal de string, faça delas valores `const`. Isso ajuda o `go vet` a realizar uma análise estática da string de formato.

**Ruim:**
```go
msg := "valores inesperados %v, %v\n"
fmt.Printf(msg, 1, 2)
```

**Bom:**
```go
const msg = "valores inesperados %v, %v\n"
fmt.Printf(msg, 1, 2)
```

---

### 55 — Nomeando Funções no Estilo Printf

Ao declarar uma função no estilo `Printf`, certifique-se de que o `go vet` pode detectá-la e verificar a string de formato. Isso significa que você deve usar nomes de função pré-definidos no estilo `Printf` se possível.

Se usar os nomes pré-definidos não for uma opção, termine o nome que você escolher com f: `Wrapf`, não `Wrap`.

```shell
go vet -printfuncs=wrapf,statusf
```

---

### 56 — Tabelas de Teste

Testes baseados em tabelas com [subtestes](https://blog.golang.org/subtests) podem ser um padrão útil para escrever testes e evitar a duplicação de código quando a lógica central do teste é repetitiva.

**Ruim:**
```go
func TestSplitHostPort(t *testing.T) {
  host, port, err := net.SplitHostPort("192.0.2.0:8000")
  require.NoError(t, err)
  assert.Equal(t, "192.0.2.0", host)
  assert.Equal(t, "8000", port)

  host, port, err = net.SplitHostPort("192.0.2.0:http")
  require.NoError(t, err)
  assert.Equal(t, "192.0.2.0", host)
  assert.Equal(t, "http", port)
  // ... mais casos
}
```

**Bom:**
```go
func TestSplitHostPort(t *testing.T) {
  tests := []struct{
    give     string
    wantHost string
    wantPort string
  }{
    {give: "192.0.2.0:8000", wantHost: "192.0.2.0", wantPort: "8000"},
    {give: "192.0.2.0:http", wantHost: "192.0.2.0", wantPort: "http"},
    {give: ":8000", wantHost: "", wantPort: "8000"},
    {give: "1:8", wantHost: "1", wantPort: "8"},
  }

  for _, tt := range tests {
    t.Run(tt.give, func(t *testing.T) {
      host, port, err := net.SplitHostPort(tt.give)
      require.NoError(t, err)
      assert.Equal(t, tt.wantHost, host)
      assert.Equal(t, tt.wantPort, port)
    })
  }
}
```

Seguimos a convenção de que a fatia de structs é referida como `tests` e cada caso de teste como `tt`. Além disso, incentivamos a explicitação das entradas e saídas para cada caso de teste com os prefixos `give` e `want`.

**Evite Complexidade Desnecessária em Testes de Tabela**: Testes de tabela **NÃO** devem ser usados sempre que houver lógica complexa ou condicional dentro dos subtestes. Testes de tabela grandes e complexos devem ser divididos em várias tabelas de teste ou várias funções individuais `Test...`.

**Testes Paralelos**: Testes paralelos devem tomar cuidado para atribuir explicitamente variáveis de loop dentro do escopo do loop:

```go
for _, tt := range tests {
  tt := tt // for t.Parallel
  t.Run(tt.give, func(t *testing.T) {
    t.Parallel()
    // ...
  })
}
```

---

### 57 — Opções Funcionais

Opções funcionais são um padrão no qual você declara um tipo opaco `Option` que registra informações em alguma struct interna. Use esse padrão para argumentos opcionais em construtores e outras APIs públicas que você prevê precisar expandir, especialmente se você já tiver três ou mais argumentos nessas funções.

**Ruim:**
```go
func Open(addr string, cache bool, logger *zap.Logger) (*Connection, error) {
  // ...
}
```

**Bom:**
```go
type Option interface {
  // ...
}

func WithCache(c bool) Option { /* ... */ }
func WithLogger(log *zap.Logger) Option { /* ... */ }

func Open(addr string, opts ...Option) (*Connection, error) {
  // ...
}
```

A maneira sugerida de implementar esse padrão é com uma interface `Option` que possui um método não exportado, registrando opções em uma struct não exportada chamada `options`:

```go
type options struct {
  cache  bool
  logger *zap.Logger
}

type Option interface {
  apply(*options)
}

type cacheOption bool

func (c cacheOption) apply(opts *options) {
  opts.cache = bool(c)
}

func WithCache(c bool) Option {
  return cacheOption(c)
}

type loggerOption struct {
  Log *zap.Logger
}

func (l loggerOption) apply(opts *options) {
  opts.logger = l.Log
}

func WithLogger(log *zap.Logger) Option {
  return loggerOption{Log: log}
}

func Open(addr string, opts ...Option) (*Connection, error) {
  options := options{
    cache:  defaultCache,
    logger: zap.NewNop(),
  }

  for _, o := range opts {
    o.apply(&options)
  }
  // ...
}
```

---

### 58 — Linting

Mais importante do que qualquer conjunto "bendito" de linters é aplicar lint de forma consistente em todo o código.

Recomendamos o uso dos seguintes linters no mínimo:

- [errcheck](https://github.com/kisielk/errcheck) — garantir que os erros sejam tratados
- [goimports](https://godoc.org/golang.org/x/tools/cmd/goimports) — formatar o código e gerenciar os imports
- [golint](https://github.com/golang/lint) — apontar erros de estilo comuns
- [govet](https://golang.org/cmd/vet/) — analisar o código em busca de erros comuns
- [staticcheck](https://staticcheck.io/) — realizar várias verificações de análise estática

**Lint Runners**: Recomendamos o [golangci-lint](https://github.com/golangci/golangci-lint) como o principal executor de lint para código Go, principalmente devido à sua performance em código-bases maiores e à capacidade de configurar e usar muitos linters canônicos de uma vez.

---

## Ver Também

- [[go-style-guide|Go Style Guide]] — Catálogo completo de tópicos Go
- [[go-code-review|Go Code Review Checklist]] — Checklist sistemática de revisão
- [[go-linting|Go Linting]] — Configuração de golangci-lint
- [[go-interfaces|Go Interfaces]] — Interfaces e composição
- [[go-error-handling|Go Error Handling]] — Tratamento de erros
- [[go-concurrency|Go Concurrency]] — Concorrência e goroutines
- [[go-testing|Go Testing]] — Padrões de teste
- [[go-performance|Go Performance]] — Otimização e benchmarks
- [[go-naming|Go Naming]] — Convenções de nomes
- [[go-packages|Go Packages]] — Organização de pacotes
- [[go-functional-options|Functional Options]] — Padrão Functional Options
- [[references/go/effective-go|Effective Go]] — Guia canônico da linguagem
- [[references/go/go-wiki-code-review|Go Wiki Code Review]] — CodeReviewComments oficial
