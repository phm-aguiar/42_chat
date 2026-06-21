---
name: gherkin-scenarios
description: >
  Use when the QA agent needs to write Gherkin scenarios (.feature files) from BDD specs.
  Teaches the QA to read spec scenarios, derive Gherkin Given/When/Then, and apply best
  practices (focused scenarios, declarative style, anti-pattern avoidance). Trigger: QA
  cycle step 2 (escrever cenarios Gherkin).
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, Gherkin, BDD, Testing, Feature]
    related_skills: [wiki-query, go-unit-tests, local-test-runner]
    category: qa
    resources:
      - SKILL.md
      - references/syntax.md
      - references/best-practices.md
      - references/anti-patterns.md
---

# Gherkin Scenarios — Escrever .feature files

> Ensina o QA a transformar cenarios BDD da spec em arquivos .feature validos.

## Proposito

Esta skill e carregada pelo agent-qa (007) no passo 2 do ciclo de validacao:
"Escrever cenarios Gherkin". Ela NAO gera arquivos automaticamente — ela
ensina o processo e fornece referencias de formato, boas praticas e
anti-patterns. O QA usa esta skill como trilho para produzir .feature files
de qualidade.

## Pre-requisitos

- QA recebeu contexto com spec (secoes de cenario BDD)
- QA ja leu a spec e identificou os requisitos a validar
- Diretorio de saida: `<specs/features/NNN-nome/acceptance/>`

## Fluxo de Execucao

### Passo 1: Carregar referencias

```
skill_view(name="gherkin-scenarios", file_path="references/syntax.md")
skill_view(name="gherkin-scenarios", file_path="references/best-practices.md")
skill_view(name="gherkin-scenarios", file_path="references/anti-patterns.md")
```

### Passo 2: Identificar cenarios na spec

1. Leia a spec e extraia cada cenario BDD documentado
2. Para cada cenario, identifique:
   - **Contexto:** pre-condicoes (o que existe antes da acao)
   - **Acao:** o que o usuario/sistema faz
   - **Resultado esperado:** o que deve acontecer

### Passo 3: Escrever o .feature file

Siga o template:

```gherkin
# language: pt
Funcionalidade: <nome da funcionalidade>
  <descricao breve do que esta sendo testado>

  Cenario: <nome do cenario - descritivo>
    Dado <contexto/pre-condicao>
    Quando <acao>
    Entao <resultado esperado>
```

### Passo 4: Aplicar boas praticas

- **Cenarios focados:** um cenario = um comportamento. Nao teste multiplas coisas
- **Declarativo, nao imperativo:** "Dado que estou logado" (nao "Dado que clico no botao X e preencho campo Y")
- **Nomes descritivos:** "Cenario: Cadastro com email invalido retorna erro 400"
- **Background para pre-condicoes comuns:** use `Background` para steps repetidos

### Passo 5: Validar contra anti-patterns

Revise seu .feature e remova:
- Cenarios com multiplos When/Then (quebre em cenarios separados)
- Dados hardcoded que deveriam ser parametrizados (use `Esquema do Cenario`)
- Steps imperativos (UI-specific) — prefira declarativos
- Cenarios sem valor de negocio claro

### Passo 6: Salvar e reportar

Salve o arquivo em `<specs/features/NNN-nome/acceptance/>` com nome descritivo.
Reporte no ciclo do QA quais cenarios foram criados e qual secao da spec cada um cobre.

## Exemplo

Spec: "O sistema deve permitir cadastro de usuario com email e senha.
Email invalido deve retornar erro 400."

```gherkin
# language: pt
Funcionalidade: Cadastro de Usuario
  Validacao de dados de entrada para cadastro de novo usuario.

  Cenario: Cadastro com dados validos
    Dado que nao existe usuario com email "teste@email.com"
    Quando envio POST /users com email "teste@email.com" e senha "123456"
    Entao o status code e 201
    E o body contem "id" e "email"

  Cenario: Cadastro com email invalido
    Dado que o sistema aceita cadastros
    Quando envio POST /users com email "invalido" e senha "123456"
    Entao o status code e 400
    E o body contem "erro": "email invalido"
```

## Verificacao

- [ ] .feature file salvo no diretorio acceptance/
- [ ] Cenarios cobrem todos os casos documentados na spec
- [ ] Cada cenario tem exatamente um When
- [ ] Steps sao declarativos (nao imperativos)
- [ ] Nenhum anti-pattern presente
- [ ] Background usado para pre-condicoes comuns (se aplicavel)
