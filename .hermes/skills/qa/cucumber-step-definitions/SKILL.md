---
name: cucumber-step-definitions
description: >
  Use when the QA agent needs to implement step definitions in Go that connect Gherkin
  .feature files to actual test code. Covers the mapping from Given/When/Then to Go
  functions using Godog (Go Cucumber framework). References Cucumber docs in the wiki.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, Cucumber, Step-Definitions, Godog, BDD]
    related_skills: [gherkin-scenarios, go-unit-tests]
    category: qa
    resources:
      - SKILL.md
---

# Cucumber Step Definitions — Conectar .feature ao codigo Go

> Ensina o QA a implementar step definitions que executam os cenarios Gherkin.

## Proposito

Esta skill ensina a criar step definitions em Go usando Godog — o framework
Cucumber para Go. Conecta os cenarios Gherkin (.feature) com codigo de teste
executavel. A documentacao completa de Cucumber esta em [[references/cucumber-basics]].

## Pre-requisitos

- QA ja escreveu o .feature file (usando gherkin-scenarios)
- Go instalado, modulo com dependencia `github.com/cucumber/godog`
- `go get github.com/cucumber/godog` executado

## Fluxo

### Passo 1: Instalar Godog
```bash
go get github.com/cucumber/godog/cmd/godog@latest
```

### Passo 2: Mapear steps para funcoes Go

Cada linha do .feature vira uma funcao Go:

```gherkin
# .feature
Dado que nao existe usuario com email "teste@email.com"
Quando envio POST /users com email "teste@email.com" e senha "123456"
Entao o status code e 201
```

```go
// step_definitions_test.go
func naoExisteUsuarioComEmail(ctx context.Context, email string) error {
    // verifica que usuario nao existe
    return nil
}

func envioPOSTComEmailESenha(ctx context.Context, email, senha string) error {
    // faz a chamada HTTP
    return nil
}

func oStatusCodeE(ctx context.Context, code int) error {
    // verifica status code
    return nil
}

func InitializeScenario(ctx *godog.ScenarioContext) {
    ctx.Step(`^nao existe usuario com email "([^"]*)"$`, naoExisteUsuarioComEmail)
    ctx.Step(`^envio POST /users com email "([^"]*)" e senha "([^"]*)"$`, envioPOSTComEmailESenha)
    ctx.Step(`^o status code e (\d+)$`, oStatusCodeE)
}
```

### Passo 3: Executar com Godog
```bash
godog run ./features
```

### Passo 4: Reusar steps
Steps bem escritos sao reutilizaveis entre cenarios. Ex: "o status code e 201"
pode ser usado em qualquer cenario que verifica HTTP status.

## Referencia
Consulte [[references/cucumber-basics]] no vault para fundamentos de Cucumber.
