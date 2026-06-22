---
title: "Table Driven"
tags: [qa, reference]
created: 2026-06-20
rag_score: 0.484
---
# Table-Driven Tests em Go

## Por que table-driven?
- Um unico loop teste executa todos os cenarios
- Adicionar novo caso = adicionar linha na tabela
- `t.Run()` isola cada subteste (falha de um nao para os outros)
- Facil de ler e manter

## Estrutura

```go
func TestXxx(t *testing.T) {
    tests := []struct {
        name    string    // nome do subteste
        // campos de entrada...
        // campos de saida esperada...
    }{
        {name: "caso 1", ...},
        {name: "caso 2", ...},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // executa e compara
        })
    }
}
```

## Convencoes Go
- Arquivo: `xxx_test.go`
- Pacote: mesmo do codigo (ou `xxx_test` para teste externo)
- Funcao: `TestXxx(t *testing.T)`
- Benchmark: `BenchmarkXxx(b *testing.B)`
- Exemplo: `ExampleXxx()` (aparece no godoc)

## Comandos
```bash
go test ./...           # todos os pacotes
go test -v ./...        # verbose
go test -run TestXxx    # filtra por nome
go test -cover ./...    # cobertura
```
