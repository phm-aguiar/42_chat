# Smoke-Task: Happy Path do Agent QA

> Fixture para T003. Simula código correto que o QA deve validar e aprovar.

## Contexto (o que o orchestrator enviaria)

### Spec relevante
Seção 2.1: O sistema deve prover uma função `Add(a, b int) int` que retorna a soma de dois inteiros.

### Código implementado pelo Dev
Arquivo `internal/calculator/calculator.go`:
```go
package calculator

func Add(a, b int) int {
    return a + b
}
```

### Task
- **ID:** T001
- **Papel:** QA
- **Descrição:** Validar implementação da função Add
- **Arquivos:** `internal/calculator/calculator.go`

### Skills injetadas
- Nenhuma (modo força bruta — usar `go test` e `go vet` diretamente)

## Critérios de sucesso
1. QA spawna e lê o contexto
2. Escreve `internal/calculator/calculator_test.go` com teste da função Add
3. Executa `go test ./...` → exit 0
4. Executa `go vet ./...` → sem warnings
5. Reporta DONE com evidência (output de teste, lint, cobertura)
