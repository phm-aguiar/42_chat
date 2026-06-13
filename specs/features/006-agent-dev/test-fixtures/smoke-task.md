# Smoke-Task: Happy Path do Agent Dev

> Fixture para T003. Simula uma task atômica que o orchestrator enviaria ao agent-dev.
> Contexto: implementar uma função simples de soma em Go.

## Contexto (o que o orchestrator enviaria)

### Spec relevante (simplificada)
Seção 2.1: O sistema deve prover uma função `Add(a, b int) int` que retorna a soma de dois inteiros.

### Task
- **ID:** T001
- **Papel:** Dev
- **Descrição:** Implementar função `Add` no pacote `calculator`
- **Arquivos:** `internal/calculator/calculator.go`

### Skills injetadas
- `go-implement` (simulada — não disponível ainda, modo força bruta)
- `smoke-check` (simulada — não disponível ainda, usar `go build`)

### Tentativa: 1/3

## Critérios de sucesso (o que verificar após execução)

1. **Agent-dev spawna** via `agent-run agent-dev` e recebe o contexto
2. **Implementa código:** cria `internal/calculator/calculator.go` com função `Add`
3. **Smoke-test:** executa `go build ./...` e reporta exit code
4. **Reporta DONE** com:
   - Lista de arquivos criados
   - Output do smoke-test
   - Rastreabilidade: "Função Add atende requisito 'soma de dois inteiros' da spec, seção 2.1"

## Como executar

```bash
# Invocar o agent-dev com esta task
agent-run agent-dev "implementa a task do arquivo specs/features/006-agent-dev/test-fixtures/smoke-task.md"

# Verificar resultado esperado
# - Arquivo internal/calculator/calculator.go existe
# - Contém função Add(a, b int) int
# - go build ./... passa
# - Relatório contém DONE com rastreabilidade
```
