---
name: local-test-runner
description: >
  Use when the QA agent needs to execute the test suite locally. Runs go build, go vet,
  go test, and go test -cover in sequence, collects output, and formats the report for
  the QA cycle. Trigger: QA cycle steps 4-6 (executar testes, lint, cobertura).
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, Go, Test-Runner, Coverage]
    related_skills: [wiki-query, gherkin-scenarios, go-unit-tests]
    category: qa
    resources:
      - SKILL.md
---

# Local Test Runner — Executar suite de testes

> Executa build + vet + test + cover e formata o relatorio para o ciclo QA.

## Proposito

Esta skill e carregada pelo agent-qa (007) nos passos 4, 5 e 6 do ciclo:
executar testes, rodar lint, e verificar cobertura. Automatiza a execucao
e formatacao dos resultados.

## Pre-requisitos

- QA ja escreveu os testes unitarios (_test.go)
- Go instalado e modulo inicializado
- Diretorio do pacote acessivel

## Fluxo de Execucao

### Passo 1: Build check

```bash
go build ./...
```

Se falhar → **FAIL imediato.** Reporte o erro de build.

### Passo 2: Vet check

```bash
go vet ./...
```

Se houver warnings → **REJECTED.** Inclua o output completo.

### Passo 3: Executar testes

```bash
go test ./... -v -count=1
```

Flag -count=1 desabilita cache. Flag -v mostra cada subteste.

Se exit code ≠ 0 → **REJECTED** com output completo.

### Passo 4: Verificar cobertura

```bash
go test ./... -cover
```

Compare com threshold (default: 80%). Se abaixo → **REJECTED.**

### Passo 5: Formatar relatorio

Monte o relatorio no formato esperado pelo ciclo QA:

```
DONE

Testes:
$ go test ./... -v
=== RUN   TestAdd
--- PASS: TestAdd (0.00s)
ok      internal/calculator     0.003s
exit code: 0

Vet:
$ go vet ./...
(nenhum warning)

Cobertura:
$ go test ./... -cover
ok      internal/calculator     0.004s  coverage: 100.0% of statements
```

Se algo falhou, use o formato REJECTED com a secao que falhou em destaque.

## Comandos por stack

| Stack | Build | Vet | Test | Cover |
|---|---|---|---|---|
| Go | `go build ./...` | `go vet ./...` | `go test ./... -v -count=1` | `go test ./... -cover` |
| Python | `python -m compileall .` | `ruff check .` | `pytest -v` | `pytest --cov` |
| Node | `npm run build` | `npm run lint` | `npm test` | `npm test -- --coverage` |

## Verificacao

- [ ] Build passou (exit 0)
- [ ] Vet passou (sem warnings)
- [ ] Todos os testes passaram (exit 0)
- [ ] Cobertura atingiu threshold (ou task pequena justificada)
- [ ] Relatorio formatado com output real das ferramentas
