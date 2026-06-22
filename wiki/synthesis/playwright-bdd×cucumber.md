---
title: "Playwright-BDD × Cucumber"
category: synthesis
tags: [playwright-bdd, cucumber, bdd, testing, synthesis]
sources:
  - "references/playwright-bdd/index.md"
  - "references/cucumber/index.md"
  - "references/cucumber/history-of-bdd.md"
  - "references/playwright-bdd/cucumber-reporters.md"
  - "references/playwright-bdd/writing-steps.md"
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
summary: "O que emerge da interseção entre Playwright-BDD e Cucumber tradicional: duas filosofias de BDD que se complementam em camadas — Cucumber para discovery e especificação, Playwright-BDD para execução em browser real."
provenance:
  extracted: 0.20
  inferred: 0.75
  ambiguous: 0.05
base_confidence: 0.59
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: supporting
---

# Playwright-BDD × Cucumber

## The Connection

Playwright-BDD e Cucumber compartilham o mesmo DNA: **Gherkin como linguagem de especificação executável**.
Mas divergem no propósito. Cucumber é um framework de BDD generalista — nasceu em 2008 para Ruby,
hoje suporta dezenas de linguagens. Playwright-BDD é uma camada sobre o Playwright da Microsoft que
traduz `.feature` files diretamente para testes de browser com fixtures, workers hooks e reporters
nativos do Playwright. ^[inferred]

Juntos, eles cobrem o ciclo completo do BDD: **Cucumber para o "porquê"** (discovery, exemplo mapping,
three amigos) e **Playwright-BDD para o "como"** (execução em Chromium/Firefox/WebKit com traces,
screenshots e vídeos). ^[inferred]

## Onde se Encontram

| Dimensão | Cucumber | Playwright-BDD |
|---|---|---|
| **Propósito** | Framework BDD generalista | Bridge Gherkin→Playwright |
| **Linguagem-alvo** | Ruby, Java, JS, Go, Python... | JavaScript/TypeScript apenas |
| **Discovery** | Example Mapping, Discovery Workshop, Three Amigos | Herda do Cucumber (usa `.feature` files) |
| **Execução** | Qualquer driver (Selenium, HTTP, CLI) | Exclusivamente Playwright (Chromium/Firefox/WebKit) |
| **Reporters** | JSON, HTML, JUnit, message format | Playwright reporters + Cucumber reporters + Allure |
| **Hooks** | `Before`, `After`, `BeforeStep`, `AfterStep` | Step/Scenario/Worker hooks + fixtures como preferência |
| **Estado** | World object, DI (PicoContainer, Spring) | Playwright fixtures (`$test`, `$testInfo`, `$step`) |

## Cross-cutting Insight

A interseção mais valiosa não é técnica — é **metodológica**. Projetos que adotam Cucumber para
discovery sessions (com stakeholders) e Playwright-BDD para execução automatizada ganham uma
vantagem única: **rastreabilidade bidirecional entre a conversa de discovery e o teste que quebrou.**

O `example-mapping.md` do Cucumber gera exemplos concretos de comportamento. O `writing-features.md`
do Playwright-BDD transforma esses exemplos em cenários Gherkin executáveis contra um browser real.
O gap tradicional do BDD — "os testes ficam desatualizados e ninguém lê os `.feature` files" —
some quando o mesmo `.feature` é usado na discovery session (com Cucumber) e no CI (com Playwright-BDD).
^[inferred]

**Padrão: "BDD Full-Stack"**

1. **Discovery Workshop** — [[references/cucumber/discovery-workshop|Discovery Workshop]] com Three Amigos usando Example Mapping
2. **Especificação** — `.feature` files escritos colaborativamente (Gherkin como lingua franca)
3. **Step Definitions** — Implementados com [[references/playwright-bdd/writing-steps|Playwright-BDD steps]] (Playwright-style ou Cucumber-style)
4. **CI/CD** — [[references/cucumber/continuous-integration|CI pipeline]] com Playwright-BDD + reporters (Cucumber HTML + Playwright trace)
5. **Debug** — Falhas geram trace, screenshot e vídeo do Playwright — não só stack trace

## Tensions and Trade-offs

- **Lock-in de plataforma:** Playwright-BDD casa com JavaScript/TypeScript e Playwright. Se o time
  migrar para Selenium ou Cypress, perde-se a integração. Cucumber puro é portátil entre drivers. ^[inferred]
- **Cucumber-style vs Playwright-style:** Playwright-BDD oferece dois modos de step definitions.
  Cucumber-style usa `this`/World — familiar para times Cucumber, mas perde type-safety das fixtures
  do Playwright-style. ^[ambiguous]
- **Overhead de Gherkin:** Para testes puramente técnicos (ex: API contract tests), Gherkin adiciona
  indireção desnecessária. Nem todo teste precisa ser BDD. Use [[references/cucumber/testable-architecture|Testable Architecture]]
  para decidir quais camadas merecem `.feature` files: use cases sim, detalhes de implementação não. ^[inferred]
- **Gocuke no meio:** O projeto 42 Chat usa Go, não JS. [[references/cucumber/gocuke|Gocuke]] é a ponte
  Go↔Gherkin, mas não tem integração com Playwright. Para testes end-to-end de browser num projeto Go,
  Playwright-BDD rodaria em paralelo (serviço separado), não integrado. ^[ambiguous]

## Open Questions

- Como orquestrar Playwright-BDD (JS) + servidor Go em CI com Docker Compose?
- Gocuke + Playwright-BDD podem coexistir no mesmo repositório para camadas diferentes (API vs UI)?
- O formato Cucumber Messages (protocol buffers) pode unificar reports entre Cucumber e Playwright-BDD?

## Related

- [[references/playwright-bdd/index|Playwright-BDD]]
- [[references/playwright-bdd/writing-features|Writing Features]]
- [[references/playwright-bdd/cucumber-reporters|Cucumber Reporters]]
- [[references/cucumber/index|Cucumber & BDD]]
- [[references/cucumber/discovery-workshop|Discovery Workshop]]
- [[references/cucumber/example-mapping|Example Mapping]]
- [[references/cucumber/history-of-bdd|History of BDD]]
- [[references/cucumber/gocuke|Gocuke]]
- [[references/cucumber/testable-architecture|Testable Architecture]]
