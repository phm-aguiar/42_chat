# Test Fixture: Código com Bug (REJECTED)

> Fixture para T004. Código com bug intencional para validar que o QA rejeita com evidência.

## Contexto (o que o orchestrator enviaria)

### Spec relevante
Seção 2.1: A função `Divide(a, b int) (int, error)` deve retornar o resultado da divisão.
Se b = 0, deve retornar erro "division by zero".

### Código implementado pelo Dev (COM BUG)
Arquivo `internal/calculator/calculator.go`:
```go
package calculator

import "errors"

func Divide(a, b int) (int, error) {
    return a / b, nil  // BUG: não verifica b == 0
}
```

### Task
- **ID:** T002
- **Papel:** QA
- **Descrição:** Validar implementação da função Divide
- **Arquivos:** `internal/calculator/calculator.go`

## Critérios de sucesso
1. QA escreve teste que cobre divisão por zero
2. Teste falha (panic: division by zero)
3. QA reporta REJECTED com:
   - Nome do teste que falhou
   - Output completo do erro
   - Arquivo e linha do problema
4. QA NÃO tenta corrigir o código

## Comportamento ESPERADO (REJECTED)
```
REJECTED

Teste quebrado:
internal/calculator/calculator_test.go:25 — TestDivideByZero: panic: runtime error: integer divide by zero

Output:
$ go test ./... -run TestDivideByZero
--- FAIL: TestDivideByZero (0.00s)
panic: runtime error: integer divide by zero [recovered]
exit code: 1

Arquivos com problema:
- internal/calculator/calculator.go:6 — não verifica b == 0 antes da divisão
```
