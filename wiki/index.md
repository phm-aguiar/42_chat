---
title: "42_chat — Knowledge Base"
category: index
tags: [meta]
created: "2026-06-13"
updated: "2026-06-21"
---

# 42_chat Knowledge Base

> Vault do framework SDD autônomo. 11 toolkits | 6 conceitos | 365 páginas | 3.221 chunks.
> Estrutura segue [[concepts/vault-taxonomy|Vault Taxonomy]].
> Último ingest massivo: 21/jun (159 raw → 91 páginas + 10 gaps preenchidos).

## 🧠 Conceitos

- [[concepts/sdd|SDD]] — Spec-Driven Development: metodologia e pipeline
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo com exemplo real
- [[concepts/wiki-model|Wiki Model]] — Modelo de 3 camadas (sources → wiki → schema)
- [[concepts/vault-taxonomy|Vault Taxonomy]] — Taxonomia canônica de diretórios do vault
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Ciclo de vida do vault integrado ao pipeline
- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero

## Estrutura

| Diretório     | Função                            | Páginas |
| ------------- | --------------------------------- | ------- |
| `concepts/`   | Padrões, metodologia, arquitetura | 6       |
| `references/` | Docs técnicas destiladas          | ~200    |
| `skills/`     | Docs das skills Hermes            | 44      |
| `projects/`   | Conhecimento por projeto          | 14      |
| `entities/`   | Glossário de termos               | 9       |
| `tools/`      | Ferramentas documentadas          | 23      |
| `synthesis/`  | Conexões cross-cutting            | 7       |
| `journal/`    | Sessões capturadas                | 6       |
| `_meta/`      | Meta-informação do vault          | 1       |

## 📖 Glossário (entities/)

- [[entities/hub|Hub]] — Gerenciador central de conexões WebSocket
- [[entities/client|Client]] — Conexão WebSocket ativa (readPump/writePump)
- [[entities/message|Message]] — Modelo de mensagem com soft delete
- [[entities/user|User]] — Modelo de usuário da API 42
- [[entities/jwt|JWT]] — JSON Web Token interno (HS256, 12h)
- [[entities/oauth2|OAuth2]] — Fluxo authorization code da API 42
- [[entities/websocket|WebSocket]] — Protocolo full-duplex (RFC 6455)
- [[entities/chi|Chi]] — Router HTTP Go com middleware stacking
- [[entities/index|Índice do Glossário]]

## Projeto: 42_chat (Framework SDD)

### Features do Domínio

- [[projects/42_chat/features/feature-100-42-chat-core|Feature 100: 42 Chat Core]] ✅ — WebSocket chat, OAuth2, mensagens (416 linhas)
- [[projects/42_chat/features/feature-101-assinatura-participacao|Feature 101: Assinatura de Participação]] ✅ — Registro de presença em eventos

### Features do Pipeline SDD

| ID | Nome | Status |
|----|------|--------|
| [[projects/42_chat/features/feature-001-start-repo|001: Start Repo]] | Estrutura base, CI/CD | ✅ |
| [[projects/42_chat/features/feature-002-sdd-templates|002: SDD Templates]] | Formatos canônicos | ✅ |
| [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] | Scaffold de skills | 🔄 |
| [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks DAG]] | Tasks com formato DAG | ✅ |
| [[projects/42_chat/features/feature-005-agent-orchestrator|005: Runtime Orchestrator]] | Execução paralela | ✅ |
| [[projects/42_chat/features/feature-006-agent-dev|006: Agent Dev]] | Persona implementadora | ✅ |
| [[projects/42_chat/features/feature-007-agent-qa|007: Agent QA]] | Guardião da qualidade | ✅ |

### Agentes

- [[projects/42_chat/agents/agent-onboard|onboard]] ✅ — Inicializa projetos no SDD
- [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]] ✅ — Executor runtime com DAG

### Skills SDD

- [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
- [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
- [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md

## Stack Documentation (código real)

Referências criadas da implementação do 42_chat:

- [[references/postgresql|PostgreSQL]] — Connection pool, migrations, queries, lib/pq (270 linhas)
- [[references/docker-compose|Docker + Compose]] — Multistage build, dev vs prod, health checks (328 linhas)
- [[references/42-oauth2-flow|OAuth2 42 Flow]] — Authorization code, token exchange, DEV_MODE (390 linhas)
- [[references/auth-integration|Auth Integration]] — OAuth2 → JWT → WebSocket (481 linhas)
- [[references/websocket-production|WebSocket Production]] — Ping/pong, reconnect, scaling (627 linhas)
- [[references/observability|Observabilidade]] — Health checks, slog, métricas, Datadog (705 linhas)
- [[references/integration-testing-docker|Integration Testing]] — Smoke tests, Docker lifecycle (961 linhas)

## ADRs (Architecture Decision Records)

7 ADRs do LATTE Hardening (42_Framework feature 005):

- [[references/adr/adr-001-budget-tracking|ADR-001: Budget Tracking]]
- [[references/adr/adr-002-timeout-enforcement|ADR-002: Timeout Enforcement]]
- [[references/adr/adr-003-failure-propagation|ADR-003: Failure Propagation]]
- [[references/adr/adr-004-verify-deterministic|ADR-004: Verify Deterministic]]
- [[references/adr/adr-005-summarization-strategy|ADR-005: Summarization Strategy]]
- [[references/adr/adr-006-merge-strategy|ADR-006: Merge Strategy]]
- [[references/adr/adr-007-tool-ceiling|ADR-007: Tool Ceiling]]

## Papers

- [[references/papers/LATTE|LATTE]] — Language Agent Teams for Task Evolution
- [[references/papers/Multi-Agent-Systems-in-Production|Multi-Agent Systems in Production]]
- [[references/papers/LangGraph-in-Production|LangGraph in Production]]
- [[references/papers/LangGraph-vs-LangChain|LangGraph vs LangChain]]
- [[references/papers/Agentic-AI-in-Production|Agentic AI in Production]] ← novo 21/jun
- [[references/papers/Building-AI-Agents-Architecture|Building AI Agents Architecture]] ← novo 21/jun
- [[references/papers/A-MapReduce|A-MapReduce]]
- [[references/papers/Obsidian-Otimizacao-IA|Obsidian Otimização IA]]

## QA & BDD (66 páginas)

### Playwright-BDD (40 páginas)
[[references/playwright-bdd/index|Índice Playwright-BDD]] — Docs completas: writing steps, hooks, reporters, configuration

### Cucumber (26 páginas)
[[references/cucumber/index|Índice Cucumber]] — BDD methodology, step definitions, cucumber-expressions

### Referências Core
- [[references/qa-overview|QA & BDD Overview]] — Estratégia de QA no SDD
- [[references/gherkin-syntax|Gherkin Syntax]] — Sintaxe completa
- [[references/gherkin-best-practices|Gherkin Best Practices]]
- [[references/gherkin-examples|Gherkin Examples]]
- [[references/cucumber-basics|Cucumber Basics]]
- [[references/playwright-bdd|Playwright BDD]] — Página única (visão geral)
- [[references/bdd-specification-process|BDD Specification Process]]
- [[references/tdd-methodology|TDD Methodology]]
- [[references/tdd-first-principles|TDD FIRST Principles]]
- [[references/tdd-anti-patterns|TDD Anti-Patterns]]

## Go Tooling (24 páginas)

### golangci-lint
[[tools/golangci-lint/index|Índice golangci-lint]] — Core docs + 6 linters individuais (bodyclose, gosec, misspell...)

### Go Style (4 páginas)
- [[references/go/go-code-review-rules|Go Code Review Rules]] — 59 regras consolidadas (50KB)
- [[references/go/effective-go|Effective Go]] — Guia canônico
- [[references/go/go-wiki-code-review|Go Wiki Code Review]]
- [[references/go/goimports|goimports]]

### Go Style Guides (30+ páginas)
- [[references/go-style-guide|Go Style Guide]] — Catálogo completo
  - [[references/go-style-core|Core]] — [[references/go-naming|Naming]] — [[references/go-error-handling|Error Handling]] — [[references/go-concurrency|Concurrency]] — [[references/go-testing|Testing]] — [[references/go-functions|Functions]] — [[references/go-interfaces|Interfaces]] — [[references/go-packages|Packages]] — [[references/go-declarations|Declarations]] — [[references/go-control-flow|Control Flow]] — [[references/go-context|Context]] — [[references/go-data-structures|Data Structures]] — [[references/go-defensive|Defensive]] — [[references/go-documentation|Documentation]] — [[references/go-functional-options|Functional Options]] — [[references/go-generics|Generics]] — [[references/go-linting|Linting]] — [[references/go-logging|Logging]] — [[references/go-performance|Performance]] — [[references/go-code-review|Code Review]] — [[references/go-modular-architecture|Modular Architecture]] — [[references/go-repository|Repository]] — [[references/go-service|Service]] — [[references/go-chi-router|Chi Router]] — [[references/go-chi-handler|Chi Handler]] — [[references/go-cache|Cache]] — [[references/go-enum|Enum]] — [[references/go-error|Error]] — [[references/go-gorm-model|GORM Model]] — [[references/go-integration-tests|Integration Tests]] — [[references/go-mapper|Mapper]] — [[references/go-unit-tests|Unit Tests]] — [[references/go-usecase|Usecase]] — [[references/go-validator|Validator]]

### WebSocket (gorilla/websocket)
- [[references/go-websocket-core|Core]] — [[references/go-websocket-server|Server]] — [[references/go-websocket-client|Client]] — [[references/go-websocket-hub|Hub]] — [[references/go-websocket-testing|Testing]]

### JWT (golang-jwt v5)
- [[references/go-jwt|Go JWT]] — [[references/go-jwt-api-reference|API Reference]]

## Ferramentas

- **[[tools/golangci-lint/index|golangci-lint]]** — Go linter aggregator (20 páginas)
- **[[tools/jschan/overview|jschan]]** — Engine de imageboard anônimo
  - [[tools/jschan/installation|Instalação]] — [[tools/jschan/operations|Operações]]

## Sínteses Cross-Cutting (7)

- [[synthesis/sdd-go|SDD × Go]] — SDD aplicado a projetos Go
- [[synthesis/thinking-architecture|Thinking × Architecture]] — Reasoning em arquitetura
- [[synthesis/thinking-go|Thinking × Go]] — Reasoning em code review Go
- [[synthesis/playwright-bdd×cucumber|Playwright-BDD × Cucumber]] ← novo 21/jun
- [[synthesis/oauth2×jwt|OAuth2 × JWT]] ← novo 21/jun
- [[synthesis/websocket×chi|WebSocket × Chi]] ← novo 21/jun
- [[synthesis/go-tooling-ecosystem|Go Tooling Ecosystem]] ← novo 21/jun

## Referências de Arquitetura e Processos

- [[references/system-design|System Design]] — [[references/architecture-patterns|Architecture Patterns]] — [[references/database-selection|Database Selection]] — [[references/nfr-checklist|NFR Checklist]] — [[references/adr-template|ADR Template]] — [[references/techspec-template|Tech Spec]] — [[references/prd-template|PRD Template]] — [[references/pr-template|PR Template]] — [[references/code-review-template|Code Review Template]] — [[references/task-template|Task Template]] — [[references/implementation-notes-template|Implementation Notes]]

## Referências de Thinking Tools

- [[references/cognitive-bias-inventory|Cognitive Bias]] — [[references/dialectic-synthesis|Dialectic Synthesis]] — [[references/evidence-audit|Evidence Audit]] — [[references/mode-selection-guide|Mode Selection]] — [[references/pre-mortem-analysis|Pre-Mortem]] — [[references/red-team-adversarial|Red Team]] — [[references/socratic-questioning|Socratic Questioning]]

## Referências do 42 Chat (Pesquisa)

- [[references/42-chat-platform-architecture|Platform Architecture]] — [[references/42-chat-design-system|Design System]] — [[references/42-chat-engineering-requirements|Engineering Requirements]] — [[references/42-chat-architecture-diagram|Architecture Diagram]] — [[references/42-chat-research-report|Research Report]] (9 subpáginas)
- [[references/42-api-specification|42 API Spec]] — [[references/42-api-endpoints|42 API Endpoints]] — [[references/oauth2-42-pitfalls|OAuth2 Pitfalls]]

## Vite/React

- [[references/vite-reference|Vite Reference]] — [[references/vite-environment-api|Environment API]] — [[references/vite-rolldown-migration|Rolldown Migration]]
- [[references/react-vite-performance|React+Vite Performance]] (5 subpáginas)

## Journal

- [[journal/digest-2026-06-21|Digest 21/jun]] ← Hoje: ingest massivo + gap fill (111 páginas novas)
- [[journal/2026-06-18-sessao-feat100-oauth|Sessão 18/jun]] — Feature 100, OAuth2 42 debug
- [[journal/2026-06-17-brainstorm-feature-101|17/jun]] — Brainstorm Feature 101
- [[journal/2026-06-14-sessao-qa-skills-42chat|Sessão 14/jun]] — QA, skills, 42 Chat
- [[journal/digest-2026-06-15|Digest 15/jun]]

## Meta

- [[gap-tasks|Wiki Gap Fill Tasks]] — 10/10 gaps preenchidos
- [[_meta/taxonomy|Tag Taxonomy]] — Vocabulário controlado
- [[log|Change Log]] — Histórico de alterações
- [[hot|Hot Pages]] — Páginas mais acessadas
