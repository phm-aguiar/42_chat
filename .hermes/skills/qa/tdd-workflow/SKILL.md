---
name: tdd-workflow
description: >
  Use when any agent (Dev or QA) needs to apply Test-Driven Development. Teaches the
  RED-GREEN-REFACTOR cycle: write failing test → minimal code to pass → refactor.
  References the TDD methodology in the wiki vault instead of duplicating content.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [TDD, Testing, Workflow, Methodology]
    related_skills: [wiki-query, go-unit-tests, local-test-runner]
    category: qa
    resources:
      - SKILL.md
---

# TDD Workflow — RED-GREEN-REFACTOR

> Ensina o ciclo TDD classico. A metodologia completa esta no vault.

## Proposito

Esta skill ensina o ciclo TDD (Test-Driven Development) para qualquer agente
do framework. Em vez de duplicar a documentacao de TDD, referencia a pagina
[[references/tdd-methodology]] no vault Obsidian para consulta detalhada.

## Pre-requisitos

- Agente tem acesso a escrita de codigo (Dev) ou teste (QA)
- Stack configurada (Go, Python, Node)

## Fluxo TDD

### Fase RED: Escreva um teste que falha
1. Leia a spec e identifique o proximo comportamento a implementar
2. Escreva um teste unitario que define o comportamento esperado
3. Execute o teste → deve falhar (RED)
4. Se passar sem implementacao → o teste nao e util, refine

### Fase GREEN: Codigo minimo para passar
1. Escreva a implementacao mais simples que faz o teste passar
2. Nao implemente alem do necessario (YAGNI)
3. Execute o teste → deve passar (GREEN)
4. Se falhar → corrija a implementacao, nao o teste

### Fase REFACTOR: Melhore sem mudar comportamento
1. Com o teste passando, refatore: renomeie, extraia, simplifique
2. Execute o teste novamente → deve continuar passando
3. Se quebrar → desfaca o refactor

### Repetir
Volte para RED com o proximo comportamento.

## Regras de Ouro
- **Nunca escreva codigo sem um teste falhando primeiro**
- **O teste define o comportamento, nao a implementacao**
- **Refatore apenas com testes passando**
- **Commite apos cada ciclo GREEN**

## Referencia
Consulte [[references/tdd-methodology]] no vault para:
- Fundamentos teoricos do TDD
- Anti-patterns comuns
- Exemplos em Go
- TDD vs BDD vs testes tradicionais
