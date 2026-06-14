---
name: go-unit-tests
description: >
  Use when the QA agent needs to write unit tests in Go. Teaches the QA to read implemented
  code, derive table-driven tests, cover edge cases, and verify against spec requirements.
  Trigger: QA cycle step 3 (implementar testes unitarios).
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, Go, Unit-Tests, Testing, TDD]
    related_skills: [gherkin-scenarios, local-test-runner]
    category: qa
    resources:
      - SKILL.md
      - references/table-driven.md
      - references/edge-cases.md
---

# Go Unit Tests — Escrever testes unitarios em Go

> Ensina o QA a escrever testes unitarios (_test.go) a partir do codigo implementado pelo Dev.

## Proposito

Esta skill e carregada pelo agent-qa (007) no passo 3 do ciclo de validacao:
"Implementar testes unitarios". Ensina o padrao table-driven tests do Go,
cobertura de edge cases, e como verificar que o codigo atende a spec.

## Pre-requisitos

- QA recebeu contexto com o codigo implementado pelo Dev (paths + diffs)
- QA ja leu a spec e sabe quais funcoes validar
- Go instalado e modulo inicializado (go mod init)

## Fluxo de Execucao

### Passo 1: Carregar referencias

```
skill_view(name="go-unit-tests", file_path="references/table-driven.md")
skill_view(name="go-unit-tests", file_path="references/edge-cases.md")
```

### Passo 2: Identificar funcoes a testar

1. Leia o codigo implementado pelo Dev
2. Liste todas as funcoes exportadas que a task cobre
3. Para cada funcao, identifique:
   - Assinatura (parametros de entrada, retorno, erros)
   - Comportamento esperado pela spec
   - Edge cases relevantes

### Passo 3: Escrever table-driven test

Siga o padrao Go de table-driven tests:

```go
func TestFuncao(t *testing.T) {
    tests := []struct {
        name    string
        input   TipoEntrada
        want    TipoSaida
        wantErr bool
    }{
        // casos de teste aqui
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Funcao(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("Funcao() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if got != tt.want {
                t.Errorf("Funcao() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

### Passo 4: Cobrir edge cases

Para cada funcao, garanta cobertura de:
- **Happy path:** entrada valida → saida esperada
- **Zero values:** strings vazias, 0, nil
- **Limites:** valores maximos/minimos, bordas
- **Erros:** entradas que devem retornar erro
- **Comportamento especifico da spec:** cada requisito documentado

### Passo 5: Nomear e organizar

- Arquivo: `<nome_do_arquivo>_test.go` no mesmo pacote
- Funcao de teste: `Test<NomeDaFuncao>` (Go convention)
- Subtests com `t.Run()` para cada cenario
- Nomes descritivos: "valido", "vazio", "limite maximo", "erro: divisao por zero"

### Passo 6: Salvar e reportar

Salve o arquivo _test.go no mesmo diretorio do codigo do Dev.
O local-test-runner (skill separada) executara os testes.

## Exemplo

Codigo do Dev: funcao Divide(a, b int) (int, error)

```go
func TestDivide(t *testing.T) {
    tests := []struct {
        name    string
        a, b    int
        want    int
        wantErr bool
    }{
        {"divisao exata", 10, 2, 5, false},
        {"divisao com resto", 7, 2, 3, false},
        {"divisao por zero", 10, 0, 0, true},
        {"zero dividido", 0, 5, 0, false},
        {"negativo dividido", -10, 2, -5, false},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := Divide(tt.a, tt.b)
            if (err != nil) != tt.wantErr {
                t.Errorf("Divide() error = %v, wantErr %v", err, tt.wantErr)
                return
            }
            if got != tt.want {
                t.Errorf("Divide() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

## Verificacao

- [ ] _test.go no mesmo pacote do codigo do Dev
- [ ] Table-driven tests com subtests nomeados
- [ ] Happy path + edge cases cobertos
- [ ] Funcoes de erro testadas (wantErr)
- [ ] Nomes descritivos nos subtests
