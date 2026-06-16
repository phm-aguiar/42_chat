---
title: "QA & BDD no Framework SDD"
summary: "Visão geral da estratégia de Quality Assurance no framework SDD, integrando BDD, TDD e o agente QA (feature 007) para garantir qualidade desde a especificação até a execução. Este documento mapeia o ecossistema de referências de QA, define quando cada ferramenta se aplica e orienta o uso das skills do agent-qa."
category: references
tags:
  - qa
  - bdd
  - tdd
  - overview
  - sdd
base_confidence: 0.90
lifecycle: evolving
tier: overview
created: "2026-06-13"
updated: "2026-06-14"
aliases:
  - Estratégia de QA
  - QA Strategy
  - Qualidade SDD
---

# QA & BDD no Framework SDD

> *Qualidade não é uma etapa final — é o fio condutor que conecta a especificação à implementação. No SDD, QA é embedded no pipeline, não um checkpoint externo.*

---

## Visão Geral da Estratégia de QA

No framework **Spec-Driven Development (SDD)** — [[concepts/sdd|veja SDD]] —, a qualidade é garantida por um ciclo fechado de validação que começa na especificação e termina na evidência de testes. O guardião desse ciclo é o **agent-qa** (feature 007), um subagente leaf spawnado pelo orchestrator que valida implementações contra a spec, escreve cenários Gherkin, executa testes e tem poder de **rejeitar** tarefas que não atendem aos critérios.

A estratégia se apoia em três pilares:

1. **BDD na especificação** — Cenários Gherkin documentam o comportamento esperado antes de qualquer código.
2. **TDD na implementação** — Testes unitários guiam o design do código, escritos a partir dos cenários BDD.
3. **Validação automatizada** — O agent-qa executa lint, testes, cobertura e reporta DONE/REJECTED/BLOCKED.

---

## Como BDD e TDD se Complementam

| Aspecto | BDD (Behavior-Driven Development) | TDD (Test-Driven Development) |
|---------|-----------------------------------|-------------------------------|
| **Foco** | Comportamento do sistema do ponto de vista do negócio | Design e corretude do código |
| **Linguagem** | Gherkin (Given/When/Then) — legível por stakeholders | Linguagem de programação (assertivas, mocks) |
| **Quando** | Durante a especificação (pré-código) | Durante a implementação (pré-código) |
| **Quem escreve** | Product Owners, Devs, QA juntos | Desenvolvedores |
| **Output** | Arquivos `.feature` com cenários de aceitação | Testes unitários (`_test.go`, `*.spec.ts`) |
| **Ferramentas** | Cucumber, Playwright BDD, Behave | Go test, Jest, Vitest, pytest |
| **Valida** | "O sistema faz o que o negócio espera?" | "O código faz o que o desenvolvedor espera?" |

**Como se complementam no SDD:**

```
BDD (especificação) ──define o "o quê"──> TDD (implementação)
                                              │
                    TDD (implementação) ──valida o "como"──> Código final
                                              │
                    BDD (validação QA) ──verifica o "o quê"──> Código final
```

- **BDD responde** "qual comportamento o sistema deve ter?" — Cenários Gherkin na spec.
- **TDD responde** "como implementar esse comportamento corretamente?" — Testes unitários.
- **QA une ambos**: usa os cenários BDD como entrada e executa tanto os testes BDD (Cucumber/Playwright BDD) quanto os testes TDD (unitários) na validação.

---

## Fluxo Completo: Specs BDD → TDD → Implementação → Testes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE SDD — QA EMBEDDED                       │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐
  │ SPEC BDD │───>│  TDD (Dev)   │───>│ IMPLEMENT │───>│ QA VALIDA│
  │ (Gherkin)│    │ (testes     )│    │ (código)  │    │ (agente) │
  └──────────┘    └──────────────┘    └──────────┘    └──────────┘
       │                │                  │               │
       │ 1. Cenários    │ 2. Testes        │ 3. Código     │ 4. Gherkin +
       │    Given/When/ │    unitários     │    que passa  │    testes  +
       │    Then na     │    derivados dos │    nos testes │    lint    +
       │    spec        │    cenários      │    TDD        │    cobertura
       │                │                  │               │
       ▼                ▼                  ▼               ▼
  ┌──────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐
  │ Feature  │    │ _test.go     │    │ main.go  │    │ DONE /   │
  │ .feature │    │ *.spec.ts    │    │ *.ts     │    │ REJECTED │
  └──────────┘    └──────────────┘    └──────────┘    └──────────┘
```

### Passo a passo detalhado:

1. **Especificação (sdd-brainstorm → spec.md)**
   - A spec contém cenários Gherkin que definem o comportamento esperado.
   - Esses cenários são escritos em linguagem de negócio (Given/When/Then).
   - Referência: [[bdd-specification-process|Processo de Especificação BDD]].

2. **Planejamento (sdd-generate-plan → plan.md)**
   - Decisões arquiteturais derivadas dos cenários BDD.
   - Identificação de funções, módulos e interfaces a serem testadas.

3. **Geração de Tarefas (sdd-generate-tasks → DAG)**
   - Tasks atômicas com critérios de aceitação derivados dos cenários.

4. **Implementação pelo agent-dev**
   - Escreve testes unitários primeiro (TDD) baseados nos cenários BDD.
   - Implementa o código que passa nos testes.
   - Reporta DONE com evidência de testes passando.

5. **Validação pelo agent-qa**
   - Lê a spec e os cenários BDD.
   - Escreve/executa testes Gherkin (Cucumber/Playwright BDD).
   - Executa testes unitários e lint.
   - Verifica cobertura.
   - Reporta: **DONE** (tudo OK), **REJECTED** (testes falham, força re-spawn do Dev), ou **BLOCKED** (spec ambígua).

6. **Ciclo de retry**
   - Máximo 3 rejeições. Após isso, escala para humano.

---

## Quando Usar Gherkin vs Cucumber vs Playwright BDD

| Ferramenta | Propósito | Quando usar | Quando **não** usar |
|------------|-----------|-------------|---------------------|
| **Gherkin** | Linguagem de especificação (.feature files) | Escrever cenários de comportamento legíveis por stakeholders. Sempre que houver uma spec. | Para testes puramente técnicos (ex: validar algoritmo interno). | 
| **Cucumber** | Runner BDD clássico (step definitions + Gherkin) | Equipes que querem BDD tradicional com suporte multi-linguagem (JS, Java, Ruby, Go). Cenários de aceitação em projetos não-Playwright. | Testes E2E que já usam Playwright (Playwright BDD é mais integrado). Projetos que só precisam de testes unitários. |
| **Playwright BDD** | BDD integrado ao Playwright Test | Testes E2E e de componentes que precisam de browser real. Quando a stack já usa Playwright. Cenários que envolvem interação com UI. | Testes puramente unitários (sem UI). Cenários que não precisam de browser (use Cucumber puro + step definitions leves). |

### Regra prática para o framework SDD:

```
A spec usa Gherkin?  ──Sim──>  O cenário precisa de browser?
                                    ├── Sim → Playwright BDD
                                    └── Não → Cucumber

                          ──Não──>  Testes unitários (TDD puro, sem BDD)
```

---

## Mapa das Referências Disponíveis

O diretório `wiki/references/` contém seis páginas que formam a base de conhecimento de QA do framework:

| # | Página | Conteúdo | Quando consultar |
|---|--------|----------|------------------|
| 1 | [[bdd-specification-process|Processo de Especificação BDD]] | Metodologia BDD, estrutura Gherkin, palavras-chave, cenários, Background, Scenario Outline, Rules, boas práticas de escrita | Durante a especificação (sdd-brainstorm) e quando o agent-qa for interpretar cenários da spec |
| 2 | [[gherkin-syntax|Sintaxe Gherkin — Referência Completa]] | Referência completa da sintaxe: keywords, step arguments, Doc Strings, Data Tables, tags, internacionalização, organização de diretórios | Consulta rápida durante a escrita de qualquer arquivo `.feature` |
| 3 | [[gherkin-best-practices|Gherkin — Boas Práticas]] | Regra de ouro, boas práticas essenciais, anti-patterns, estilo declarativo vs imperativo, dicas de revisão, checklist | Revisão e linting de cenários Gherkin pelo agent-qa |
| 4 | [[gherkin-examples|Exemplos de Gherkin]] | Exemplos reais: busca de produtos, carrinho de compras, login, saque bancário, validação de senha, controle de acesso; comparações lado a lado | Template e inspiração para escrever novos cenários |
| 5 | [[cucumber-basics|Cucumber & BDD — Referência Completa]] | Core concepts, step definitions (JS/TS/Java/Ruby), hooks, World context, Data Tables, Doc Strings, Page Object, boas práticas e anti-patterns | Quando o agent-qa for implementar step definitions para Cucumber |
| 6 | [[playwright-bdd|Playwright BDD — Referência Completa]] | Instalação, configuração com `defineBddConfig`, projects, step definitions com `createBdd`, fixtures, POM, Data Tables, tags especiais, execução, troubleshooting | Quando o agent-qa for executar testes E2E com browser via Playwright BDD |
| 7 | [[tdd-methodology|TDD Methodology]] | Ciclo Red-Green-Refactor-Commit, princípios FIRST, padrão AAA, naming conventions, organização de testes, 8 anti-patterns com exemplos em Python/pytest | Durante implementação (agent-dev) e validação de qualidade de testes (agent-qa) |
| 8 | [[recipe-step-executor|Recipe Step Executor]] | Implementação de referência em Python: executor de workflows com condições, DAG, retry/backoff, timeout, templates e sub-recipes. Cobertura de testes com 6 features + 7 cross-feature interactions | Referência para smoke-tests e padrão de executor para testes BDD |

### Relação entre as referências:

```
                    ┌──────────────────────┐
                    │  qa-overview.md      │ ← Você está aqui
                    │  (estratégia, mapa)  │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
    ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
    │ BDD Especificação│ │ Ferramentas │ │ Validação & QA   │
    ├─────────────────┤ ├─────────────┤ ├──────────────────┤
    │ bdd-specification│ │ gherkin-   │ │ playright-bdd[] │
    │ -process         │ │ syntax     │ │ cucumber-basics │
    │                  │ │ gherkin-   │ │                  │
    │                  │ │ best-      │ │                  │
    │                  │ │ practices  │ │                  │
    │                  │ │ gherkin-   │ │                  │
    │                  │ │ examples   │ │                  │
    └─────────────────┘ └─────────────┘ └──────────────────┘
```

---

## Como as Skills do Agent-QA Usarão Essas Referências

O **agent-qa** ([spec 007](specs/features/007-agent-qa/spec.md)) é um agente Hermes com persona fixa e **skills de teste plugáveis por stack**, injetadas pelo orchestrator. As referências em `wiki/references/` servem como fonte canônica de conhecimento para essas skills:

### Skill 1: `gherkin-scenarios` (futura)

- **O quê faz:** Escreve cenários Gherkin a partir da spec (arquivos `.feature`).
- **Referências usadas:**
  - [[bdd-specification-process]] — Para entender a estrutura de cenários e como derivá-los da spec.
  - [[gherkin-syntax]] — Consulta sintática durante a geração dos `.feature` files.
  - [[gherkin-best-practices]] — Para aplicar boas práticas e evitar anti-patterns na geração.
  - [[gherkin-examples]] — Templates reais para basear a geração.

### Skill 2: `cucumber-step-defs` (futura)

- **O quê faz:** Implementa step definitions para os cenários Gherkin usando Cucumber.
- **Referências usadas:**
  - [[cucumber-basics]] — Para implementar step definitions, hooks, World context, Data Tables.
  - [[gherkin-syntax]] — Para garantir que os passos correspondem à sintaxe do `.feature`.

### Skill 3: `playwright-bdd-runner` (futura)

- **O quê faz:** Executa cenários BDD que exigem interação com browser, usando Playwright BDD.
- **Referências usadas:**
  - [[playwright-bdd]] — Guia completo de instalação, configuração, fixtures, POM e execução.
  - [[gherkin-best-practices]] — Boas práticas de cenários para E2E.

### Skill 4: `local-test-runner` (futura)

- **O quê faz:** Executa testes unitários e lint, mede cobertura.
- **Referências usadas:** Nenhuma diretamente — depende da stack (Go, Node, etc.).

### Modo "força bruta" (sem skills injetadas)

- Se o orchestrator spawnar o agent-qa sem skills específicas, ele opera em modo reduzido:
  - Executa comandos padrão da stack (`go test ./...`, `go vet`, `go test -cover`).
  - Não gera cenários Gherkin — apenas testes unitários básicos.
  - Reporta DONE com cobertura real e nota explicativa.
  - Referências não são consultadas — QA opera com conhecimento embutido na persona.

### Ciclo de consulta das referências:

```
1. QA recebe contexto (spec + código + skills)
2. QA lê a spec → identifica cenários BDD → consulta:
   ├── bdd-specification-process (se precisar relembrar estrutura)
   ├── gherkin-syntax (se precisar de sintaxe específica)
   └── gherkin-examples (se precisar de template)
3. QA escreve .feature files
4. QA implementa step definitions → consulta:
   ├── cucumber-basics (se for Cucumber)
   └── playwright-bdd (se for Playwright)
5. QA executa testes, lint, cobertura
6. QA formata evidência → reporta DONE/REJECTED/BLOCKED
```

---

## Recomendações de Próximos Passos

### Imediatos (curto prazo)

1. **Criar as skills de teste do agent-qa**
   - `gherkin-scenarios` — Skill para gerar cenários Gherkin a partir de specs.
   - `cucumber-step-defs` — Skill para implementar step definitions.
   - `playwright-bdd-runner` — Skill para executar testes com Playwright BDD.
   - `local-test-runner` — Skill para execução de testes unitários e lint.

2. **Definir thresholds de qualidade**
   - Cobertura mínima: 80% (com exceções documentadas para tasks pequenas).
   - Lint: zero warnings (golint, ESLint, etc.).
   - Testes: exit code 0 em toda a suite.

3. **Homologar a stack de teste**
   - Definir para cada stack homologada (Go, Node/Python futuramente) qual runner usar:
     - Cucumber vs Playwright BDD.
     - Framework de teste unitário (Go test, Jest, Vitest, pytest).

### Médio prazo

4. **Integrar QA ao pipeline CI/CD**
   - O agent-qa deve ser executado automaticamente em PRs.
   - Evidência de QA deve ser anexada ao PR como comentário.

5. **Criar dashboard de qualidade**
   - Métricas: cobertura por pacote, taxa de aprovação, tempo médio de validação.
   - Usar [[skills/wiki-dashboard|wiki-dashboard]] para visualizar.

6. **Expandir as referências**
   - Adicionar guias por stack (ex: `go-test-guide.md`, `jest-config.md`).
   - Documentar anti-patterns específicos do framework.

### Longo prazo

7. **Automatizar a evolução das referências**
   - Quando uma skill for atualizada, as referências devem ser revisadas automaticamente via `wiki-ingest`.
   - Usar [[skills/wiki-query|wiki-query]] para verificar consistência entre skills e referências.

8. **QA como gate de release**
   - O agent-qa deve ser o último gate antes de um release, validando regressão completa.

---

## Notas Técnicas

- **Todas as referências** em `wiki/references/` estão no formato [[skills/obsidian-markdown|wikilinks]] do Obsidian e são interligadas.
- O agent-qa **nunca infere** comportamento ambíguo — reporta BLOCKED.
- Skills são **trilhos, não jaulas**: se a skill não cobre, QA reporta BLOCKED, não improvisa.
- O agent-qa **não tem acesso web** — apenas terminal + file. As referências do vault são o conhecimento máximo disponível.

---

## Relacionado

- [[concepts/sdd|SDD — Spec-Driven Development]]
- [[bdd-specification-process|Processo de Especificação BDD]]
- [[gherkin-syntax|Sintaxe Gherkin]]
- [[gherkin-best-practices|Gherkin — Boas Práticas]]
- [[gherkin-examples|Exemplos de Gherkin]]
- [[cucumber-basics|Cucumber & BDD]]
- [[playwright-bdd|Playwright BDD]]
- [[projects/42_chat/agents/agent-onboard|Agent Onboard]]
- [[projects/42_chat/features/feature-006-agent-dev|Agent Dev (006)]]
- `specs/features/007-agent-qa/spec.md` — Spec do agente QA
- `specs/features/007-agent-qa/plan.md` — Plano arquitetural do agente QA

## Ver Também

- [[references/bdd-specification-process|BDD Specification Process]] — Metodologia e fluxo completo
- [[references/gherkin-syntax|Gherkin Syntax]] — Sintaxe de referência
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Boas práticas e anti-patterns
- [[references/gherkin-examples|Gherkin Examples]] — Exemplos reais
- [[references/cucumber-basics|Cucumber Basics]] — Step definitions e hooks
- [[references/playwright-bdd|Playwright BDD]] — Testes E2E com browser
- [[references/tdd-methodology|TDD Methodology]] — Red-Green-Refactor e FIRST
- [[references/recipe-step-executor|Recipe Step Executor]] — Executor de workflows Python
