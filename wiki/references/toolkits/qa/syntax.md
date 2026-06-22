---
title: "Syntax"
tags: [qa, reference]
created: 2026-06-20
rag_score: 0.485
---
# Gherkin Syntax Reference

## Palavras-chave

| Keyword | Proposito |
|---|---|
| `Funcionalidade:` | Nome da funcionalidade sendo testada |
| `Cenario:` | Um cenario de teste especifico |
| `Dado` | Pre-condicao / contexto |
| `Quando` | Acao do usuario/sistema |
| `Entao` | Resultado esperado |
| `E` | Conjuncao (adiciona mais steps) |
| `Mas` | Conjuncao negativa |
| `Background` | Steps comuns a todos os cenarios |
| `Esquema do Cenario:` | Cenario parametrizado com tabela |
| `Exemplos:` | Tabela de dados para Esquema do Cenario |

## Idioma
Use `# language: pt` para portugues. O Gherkin suporta 70+ idiomas.

## Estrutura minima
```gherkin
# language: pt
Funcionalidade: Nome
  Descricao opcional

  Cenario: Nome do cenario
    Dado contexto
    Quando acao
    Entao resultado
```
