---
name: bdd-spec-process
description: >
  Use when the team (or onboard agent) needs to run a BDD specification workshop:
  discover behaviors through examples, map them to Gherkin scenarios, and produce
  a BDD-ready spec. References the BDD specification process in the wiki vault.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [BDD, Specification, Discovery, Workshop]
    related_skills: [wiki-query, gherkin-scenarios, sdd-brainstorm]
    category: qa
    resources:
      - SKILL.md
---

# BDD Spec Process — Discovery e Especificacao

> Ensina o processo de descoberta BDD: do exemplo concreto ao cenario Gherkin.

## Proposito

Esta skill ensina o processo de especificacao BDD (Behavior-Driven Development).
Em vez de duplicar a metodologia, referencia [[references/bdd-specification-process]]
no vault Obsidian. Util para o onboard agent ou quando a equipe precisa refinar
requisitos antes de implementar.

## Fluxo BDD

### Passo 1: Discovery Workshop
- Reuna stakeholders e discuta comportamentos desejados
- Use **Example Mapping**: para cada user story, liste rules, examples e questions
- Priorize: o que e essencial vs nice-to-have

### Passo 2: Formular cenarios
- Converta exemplos em cenarios Gherkin
- Um exemplo = um cenario
- Use linguagem ubiqua (termos do dominio, nao termos tecnicos)

### Passo 3: Refinar com edge cases
- Para cada cenario feliz, pergunte: "o que pode dar errado?"
- Adicione cenarios de erro, validacao, limites
- Consulte a skill `gherkin-scenarios` para anti-patterns

### Passo 4: Validar com stakeholders
- Revisao dos cenarios com quem entende do negocio
- "Se o sistema fizer exatamente isso, esta pronto?"
- Ajuste ate que todos concordem

### Passo 5: Integrar ao pipeline SDD
- Cenarios BDD vao para o `spec.md` (secao de cenarios)
- Depois, `sdd-generate-plan` e `sdd-generate-tasks`
- QA usa `gherkin-scenarios` para implementar os .feature files

## Referencia
Consulte [[references/bdd-specification-process]] no vault para o processo completo.
