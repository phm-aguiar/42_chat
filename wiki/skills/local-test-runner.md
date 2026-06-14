---
title: "local-test-runner"
category: skills
tags: [qa, skill, go, test-runner, coverage]
summary: "Executa a suite de testes do QA: build, vet, test, cover. Formata o relatorio DONE/REJECTED para o ciclo QA."
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
sources: [.hermes/skills/qa/local-test-runner/SKILL.md]
---

# local-test-runner

> Skill procedural — passos 4-6 do ciclo QA: build → vet → test → cover → relatorio.

## Localizacao
`.hermes/skills/qa/local-test-runner/SKILL.md`

## Comandos por stack
| Stack | Build | Vet | Test | Cover |
|---|---|---|---|---|
| Go | `go build` | `go vet` | `go test -v -count=1` | `go test -cover` |
| Python | `compileall` | `ruff check` | `pytest -v` | `pytest --cov` |
| Node | `npm run build` | `npm run lint` | `npm test` | `npm test -- --coverage` |

## Relacionado
- [[skills/go-unit-tests]] — Passo anterior (escrever testes)
- [[skills/gherkin-scenarios]] — Inicio do ciclo QA
