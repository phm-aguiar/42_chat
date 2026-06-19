---
title: "42_chat — Knowledge Base"
category: index
tags: [meta]
created: "2026-06-13"
updated: "2026-06-17"
---
	
# 42_chat Knowledge Base

> Vault do framework SDD autônomo. Agentes: `onboard` + `agent-orchestrator` + `agent-dev`.
> Estrutura segue [[concepts/vault-taxonomy|Vault Taxonomy]]. 185 páginas | 7 core | 148 fontes.

## Estrutura

| Diretório     | Função                            |
| ------------- | --------------------------------- |
| `concepts/`   | Padrões, metodologia, arquitetura |
| `references/` | Docs técnicas destiladas          |
| `skills/`     | Docs das skills Hermes            |
| `projects/`   | Conhecimento por projeto          |
| `_raw/`       | Fontes brutas históricas          |
| `journal/`    | Sessões capturadas                |
| `synthesis/`  | Conexões cross-cutting            |
| `entities/`   | Glossário de termos               |

## Journal

- [[journal/2026-06-18-sessao-feat100-oauth|Sessão 18/jun]] — Feature 100 execução, OAuth2 42 debug, constitution anti-hardcoded
- [[journal/2026-06-14-sessao-qa-skills-42chat|Sessão 14/jun]] — Finalização QA, skills, 42 Chat

## Conceitos (cross-project)

- [[concepts/sdd|SDD]] — Spec-Driven Development: metodologia e pipeline
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo com exemplo real
- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero
- [[concepts/vault-taxonomy|Vault Taxonomy]] — Taxonomia canônica de diretórios do vault

## Wiki & Conhecimento

- [[concepts/wiki-model|Wiki Model]] — Modelo de 3 camadas (sources → wiki → schema)
- [[concepts/obsidian-flow|Fluxo Obsidian]] — Ciclo de vida do vault integrado ao pipeline
- [[skills/wiki-ingest|wiki-ingest]] — Destila sources em páginas wiki
- [[skills/wiki-lint|wiki-lint]] — Audita saúde do vault (13 checks)
- [[skills/wiki-query|wiki-query]] — Busca conhecimento compilado
- [[skills/wiki-capture|wiki-capture]] — Salva sessão atual
- [[skills/wiki-cross-linker|cross-linker]] — Descobre wikilinks faltantes

## Skills de Obsidian

- [[skills/obsidian-markdown|obsidian-markdown]] — Sintaxe OFM de referência
- [[skills/obsidian-cli|obsidian-cli]] — CLI para operações no vault
- [[skills/obsidian-bases|obsidian-bases]] — Tabelas dinâmicas (.base)
- [[skills/json-canvas|json-canvas]] — Mapas visuais (.canvas)
- [[skills/defuddle|defuddle]] — Extrai markdown limpo de páginas web

## Skills Visuais

- [[skills/mermaid-visualizer|mermaid-visualizer]] — Diagramas Mermaid (flowchart, sequence, ERD)

## Skills SDD (toolkit)

- [[skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
- [[skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
- [[skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md (v2.0.0)
- [[skills/sdd-init-repo|sdd-init-repo]] — Inicializa estrutura SDD
- [[skills/sdd-explore-tech|sdd-explore-tech]] — Mapeia stack tecnológica
- [[skills/sdd-validate|sdd-validate]] — Valida conformidade SDD
- [[skills/sdd-refactor-artifact|sdd-refactor-artifact]] — Normaliza artefatos

## Skills de Documentação

- [[skills/doc-extract|doc-extract]] — Extrai seções de markdown
- [[skills/doc-generate-llms-txt|doc-generate-llms-txt]] — Gera llms.txt
- [[skills/doc-generate-toc|doc-generate-toc]] — Gera tabela de conteúdo

## Skills Wiki (toolkit)

- [[skills/wiki-setup|wiki-setup]] — Inicializa vault
- [[skills/wiki-status|wiki-status]] — Estado/delta do vault
- [[skills/wiki-dashboard|wiki-dashboard]] — Dashboards
- [[skills/wiki-digest|wiki-digest]] — Resumo periódico
- [[skills/wiki-export|wiki-export]] — Exporta grafo
- [[skills/wiki-synthesize|wiki-synthesize]] — Síntese cross-cutting
- [[skills/wiki-dedup|wiki-dedup]] — Deduplicação
- [[skills/wiki-tag-taxonomy|wiki-tag-taxonomy]] — Taxonomia de tags
- [[skills/wiki-hermes-history-ingest|hermes-history-ingest]] — Ingere histórico
- [[skills/wiki-llm-wiki|llm-wiki]] — Fundação teórica

## Skills de Tooling

- [[skills/agent-run|agent-run]] — Runtime de agentes
- [[skills/skill-forge|skill-forge]] — Cria novas skills
- [[skills/git-conventional-commit|git-conventional-commit]] — Commits padronizados

## Skills de QA (agent-qa)

- [[skills/gherkin-scenarios|gherkin-scenarios]] — Escrever cenários Gherkin
- [[skills/go-unit-tests|go-unit-tests]] — Testes unitários em Go
- [[skills/local-test-runner|local-test-runner]] — Build + vet + test + cover
- [[skills/tdd-workflow|tdd-workflow]] — Ciclo RED-GREEN-REFACTOR
- [[skills/cucumber-step-definitions|cucumber-step-definitions]] — Step definitions com Godog
- [[skills/bdd-spec-process|bdd-spec-process]] — Processo discovery BDD
- [[skills/playwright-bdd-e2e|playwright-bdd-e2e]] — E2E com Playwright + BDD

## Projeto: 42_chat (Framework SDD)

### Agentes

- [[projects/42_chat/agents/agent-onboard|onboard]] ✅ — Inicializa projetos no SDD
- [[projects/42_chat/agents/agent-orchestrator|agent-orchestrator]] ✅ — Executor runtime com DAG
- `agent-dev` ✅ — Implementado (006). Persona fixa com skills plugáveis.
- `agent-qa` ✅ — Implementado (007). Guardião da qualidade.

### Features

**Ativas (004-007):**
- [[projects/42_chat/features/feature-004-sdd-tasks-dag|004: Tasks com DAG]] ✅ — `sdd-generate-tasks` v2.0.0
- [[projects/42_chat/features/feature-005-agent-orchestrator|005: Agent Orchestrator]] ✅ — Runtime de execução paralela
- [[projects/42_chat/features/feature-006-agent-dev|006: Agent Dev]] ✅ — Persona implementadora
- [[projects/42_chat/features/feature-007-agent-qa|007: Agent QA]] ✅ — Guardião da qualidade

**Pendentes (008-009):**
- 008: Agent DevOps — CI/CD, Docker, deploy
- 009: Agent Pentester — Segurança, OWASP, secrets

**Experimentais (001-003):**
- [[projects/42_chat/features/feature-001-start-repo|001: Estrutura]] ✅ — Templates base, CI/CD
- [[projects/42_chat/features/feature-002-sdd-templates|002: Templates SDD]] ✅ — Formatos canônicos
- [[projects/42_chat/features/feature-003-forge-skill|003: Forge Skill]] 🔄 — Scaffold de skills

### Skills SDD

- [[projects/42_chat/skills/sdd-brainstorm|sdd-brainstorm]] — Entrevista interativa → spec.md
- [[projects/42_chat/skills/sdd-generate-plan|sdd-generate-plan]] — Decisões arquiteturais → plan.md
- [[projects/42_chat/skills/sdd-generate-tasks|sdd-generate-tasks]] — DAG de tasks → tasks.md (v2.0.0)

## Referências de QA (agent-qa — Feature 007)

Base de conhecimento para o agente de QA: BDD, Gherkin, Cucumber, Playwright BDD e TDD.
Documentos refinados a partir de insumos em `qafiles/` e `wiki/_raw/qa/`.

- [[references/qa-overview|QA & BDD no Framework SDD]] — Visão geral da estratégia de QA
- [[references/gherkin-syntax|Gherkin Syntax Reference]] — Sintaxe completa do Gherkin
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Boas práticas e anti-patterns
- [[references/gherkin-examples|Gherkin Examples]] — Exemplos reais de feature files
- [[references/cucumber-basics|Cucumber Basics]] — Framework Cucumber e step definitions
- [[references/playwright-bdd|Playwright BDD]] — Integração Playwright + BDD
- [[references/bdd-specification-process|BDD Specification Process]] — Fluxo Gherkin Expert + Tri-Path PromptWriter
- [[references/tdd-methodology|TDD Methodology]] — Ciclo Red-Green-Refactor, naming, organização
- [[references/tdd-first-principles|TDD FIRST Principles & AAA]] — Princípios FIRST e padrão Arrange-Act-Assert
- [[references/tdd-anti-patterns|TDD Anti-Patterns]] — Catálogo dos 8 anti-patterns com exemplos pytest
- [[references/recipe-step-executor|Recipe Step Executor]] — Executor Python com DAG, retry, timeout, sub-recipes

## Referências de Go (Style Guides)

Guia de boas práticas Go destilado dos style guides oficiais (Google, Uber, Effective Go, CodeReviewComments).
20 páginas cobrindo todos os aspectos do desenvolvimento Go idiomático.

- [[references/go-style-guide|Go Style Guide]] — Catálogo completo ( #go #style-guide)
  - [[references/go-style-core|Go Style Core]] — Princípios, formatação, nesting, naked returns
  - [[references/go-naming|Go Naming]] — Convenções de nomes
  - [[references/go-error-handling|Go Error Handling]] — Estratégia de erros, wrapping, sentinelas
  - [[references/go-concurrency|Go Concurrency]] — Goroutines, channels, mutexes
  - [[references/go-testing|Go Testing]] — Table-driven, subtests, cmp.Diff
  - [[references/go-functions|Go Functions]] — Assinaturas, Printf/Stringer, organização
  - [[references/go-interfaces|Go Interfaces]] — Definição, receivers, embedding
  - [[references/go-packages|Go Packages]] — Organização, imports, tamanho
  - [[references/go-declarations|Go Declarations]] — var vs :=, escopo, shadowing
  - [[references/go-control-flow|Go Control Flow]] — If com init, early returns, switch
  - [[references/go-context|Go Context]] — context.Context, cancelamento, timeouts
  - [[references/go-data-structures|Go Data Structures]] — Slices, maps, arrays
  - [[references/go-defensive|Go Defensive]] — Cópia, interface compliance, panics
  - [[references/go-documentation|Go Documentation]] — Doc comments, exemplos
  - [[references/go-functional-options|Go Functional Options]] — Padrão de construtores
  - [[references/go-generics|Go Generics]] — Constraints, type inference
  - [[references/go-linting|Go Linting]] — golangci-lint, configuração
  - [[references/go-logging|Go Logging]] — slog, níveis, structured logging
  - [[references/go-performance|Go Performance]] — Benchmarks, otimização
  - [[references/go-code-review|Go Code Review]] — Checklist sistemática
  - [[references/go-modular-architecture|Go Modular Architecture]] — Arquitetura modular: camadas, injeção, ciclo de vida
  - [[references/go-repository|Go Repository]] — Padrão Repository
  - [[references/go-service|Go Service]] — Camada de serviço
  - [[references/go-chi-router|Go Chi Router]] — Roteamento HTTP
  - [[references/go-chi-handler|Go Chi Handler]] — Handlers HTTP idiomáticos
  - [[references/go-cache|Go Cache]] — Estratégias de caching
  - [[references/go-enum|Go Enum]] — Padrão de enumeradores type-safe
  - [[references/go-error|Go Error]] — Tratamento de erros idiomático
  - [[references/go-gorm-model|Go GORM Model]] — Models com GORM
  - [[references/go-integration-tests|Go Integration Tests]] — Testes de integração
  - [[references/go-mapper|Go Mapper]] — Mapeamento entre camadas
  - [[references/go-unit-tests|Go Unit Tests]] — Padrões de teste unitário
  - [[references/go-usecase|Go Usecase]] — Camada de casos de uso
  - [[references/go-validator|Go Validator]] — Validação de dados

### WebSocket (gorilla/websocket)

- [[references/go-websocket-core|Go WebSocket Core]] — Upgrade, mensagens, ping/pong, close, anti-patterns ( #go #websocket)
- [[references/go-websocket-server|Go WebSocket Server]] — HTTP routers, auth, CORS, graceful shutdown
- [[references/go-websocket-client|Go WebSocket Client]] — Dial, reconnect, heartbeat, TLS
- [[references/go-websocket-hub|Go WebSocket Hub]] — Broadcast, rooms, direct messaging
- [[references/go-websocket-testing|Go WebSocket Testing]] — httptest, race detection, mocks

### JWT (golang-jwt v5)

- [[references/go-jwt|Go JWT]] — Biblioteca golang-jwt v5: overview, setup, exemplos, migration v4→v5 ( #go #jwt #auth)
- [[references/go-jwt-api-reference|Go JWT API Reference]] — API completa: Token, Claims, Parser, Validator, ParserOptions, signing methods, request sub-package

### Vite (Build Tool)

- [[references/vite-reference|Vite Reference]] — Config, features, Plugin API, build/SSR, JS API consolidado ( #vite #bundler)
- [[references/vite-environment-api|Vite Environment API]] — Multi-environment runtimes (Vite 6+) ( #vite)
- [[references/vite-rolldown-migration|Vite Rolldown Migration]] — Migração Vite 7 → 8: Rolldown + Oxc ( #vite #rolldown)

### React + Vite Performance

- [[references/react-vite-performance|React + Vite Performance MoC]] — Hub: 23 regras em 6 categorias ( #react #vite #performance)
  - [[references/react-vite-build-optimization|Build Optimization]] — 7 regras CRITICAL: chunks, minification, target, sourcemaps, tree shaking, compression, hashing
  - [[references/react-vite-code-splitting|Code Splitting]] — 5 regras CRITICAL: route lazy, Suspense, dynamic imports, component lazy, prefetch
  - [[references/react-vite-development|Development]] — 3 regras HIGH: pre-bundling, Fast Refresh, HMR config
  - [[references/react-vite-asset-handling|Asset Handling]] — 4 regras HIGH: imagens, SVG components, fontes, public dir
  - [[references/react-vite-environment-config|Environment & Bundle]] — 4 regras MEDIUM: VITE_ prefix, modes, secrets, bundle visualizer

## Referências de Arquitetura e Processos

Templates e guias para system design, code review, PRs e documentação de arquitetura.

- [[references/system-design|System Design Guide]] — Abordagem estruturada para sistemas distribuídos ( #architecture)
- [[references/architecture-patterns|Architecture Patterns]] — Catálogo comparativo de padrões
- [[references/database-selection|Database Selection]] — Tipos, trade-offs, critérios
- [[references/nfr-checklist|NFR Checklist]] — Non-Functional Requirements
- [[references/adr-template|ADR Template]] — Architecture Decision Records
- [[references/techspec-template|Tech Spec Template]] — Especificação técnica
- [[references/prd-template|PRD Template]] — Product Requirements Document
- [[references/pr-template|PR Template]] — Pull Request
- [[references/code-review-template|Code Review Template]] — Revisão de código
- [[references/task-template|Task Template]] — Task atômica
- [[references/tasks-template|Tasks Template]] — Lista de tasks
- [[references/implementation-notes-template|Implementation Notes Template]] — Notas de implementação
- [[references/style-guide|Documentation Style Guide]] — Guia de estilo para docs

## Referências de Thinking Tools

Ferramentas e frameworks de reasoning: socrático, adversarial, dialético, pre-mortem.

- [[references/cognitive-bias-inventory|Cognitive Bias Inventory]] — Inventário de vieses ( #thinking)
- [[references/dialectic-synthesis|Dialectic Synthesis]] — Síntese hegeliana com steel manning
- [[references/evidence-audit|Evidence Audit]] — Auditoria de evidências
- [[references/mode-selection-guide|Mode Selection Guide]] — Seleção de modo de reasoning
- [[references/pre-mortem-analysis|Pre-Mortem Analysis]] — Antecipação de falhas
- [[references/red-team-adversarial|Red Team Adversarial]] — Red teaming
- [[references/socratic-questioning|Socratic Questioning]] — Questionamento socrático

## Skills de Agente (Novas)

Skills Hermes adicionais para agentes: arquitetura, benchmark, Go patterns, docs, brand discovery.

- [[skills/architecture-designer|Architecture Designer]] — Design de arquitetura de sistemas ( #hermes #skill)
- [[skills/benchmark|Benchmark]] — Medição de performance
- [[skills/benchmark-methodology|Benchmark Methodology]] — Metodologia de benchmarks
- [[skills/benchmark-optimization-loop|Benchmark Optimization Loop]] — Ciclo de otimização
- [[skills/brand-discovery|Brand Discovery]] — Descoberta de estratégia de marca
- [[skills/golang-patterns|Golang Patterns]] — Padrões idiomáticos Go
- [[skills/golang-testing|Golang Testing]] — Testes em Go
- [[skills/docs-writer|Docs Writer]] — Escrita de documentação
- [[skills/the-fool|The Fool]] — Challenge e adversarial thinking

## Referências de Brand Strategy

Frameworks de brand strategy: propósito, posicionamento, audiência, personalidade, voz.

- [[references/10_purpose-why|Brand Purpose]] — Propósito e Golden Circle ( #brand)
- [[references/20_positioning|Brand Positioning]] — Posicionamento de mercado
- [[references/30_audience-niche|Brand Audience & Niche]] — Audiência e nicho
- [[references/40_personality-archetype|Brand Personality & Archetype]] — Personalidade e arquétipos
- [[references/50_voice-tone|Brand Voice & Tone]] — Voz e tom
- [[references/60_narrative-story|Brand Narrative & Story]] — Narrativa e storytelling
- [[references/70_founder-tension|Brand Founder vs Organization]] — Founder brand vs org brand
- [[references/90_SYNTHESIS|Brand Synthesis]] — Síntese master brandbook

## Sínteses Cross-Cutting

Conexões entre domínios que só se revelam quando olhamos através das fronteiras dos clusters.

- [[synthesis/sdd-go|SDD × Go]] — Spec-Driven Development aplicado a projetos Go ( #synthesis)
- [[synthesis/thinking-architecture|Thinking × Architecture]] — Ferramentas de reasoning em decisões de arquitetura
- [[synthesis/thinking-go|Thinking × Go]] — Reasoning tools aplicadas a code review e design Go

## Referências do 42 Chat (Pesquisa e Ideação)

Pesquisa, arquitetura e design do chat P2P para o campus 42 SP. Consolidado de documentos de brainstorm e análise técnica.

- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Stack completa: Go, React, PostgreSQL, Docker, AWS
- [[references/42-chat-design-system|42 Chat Design System]] — Paleta brutalista, tipografia, regras CSS/Tailwind
- [[references/42-chat-engineering-requirements|42 Chat Engineering Requirements]] — Concorrência, graceful shutdown, caching, SO, segurança
- [[references/42-chat-architecture-diagram|42 Chat Architecture Diagram]] — Diagramas Mermaid (auth flow, hub, deploy, mensagens)
- [[references/42-chat-research-report|42 Chat Research Report]] — MoC do relatório de arquitetura (9 subpáginas)
  - [[references/42-chat-sec1-fundamentacao|Sec 1: Fundamentação e Ecossistema 42]]
  - [[references/42-chat-sec2-backend-concorrencia|Sec 2: Backend e Concorrência]]
  - [[references/42-chat-sec3-graceful-shutdown|Sec 3: Graceful Shutdown]]
  - [[references/42-chat-sec4-infra-tuning|Sec 4: Infra e Tuning de SO]]
  - [[references/42-chat-sec5-api-42-rate-limits|Sec 5: API 42 e Rate Limits]]
  - [[references/42-chat-sec6-campus-locations|Sec 6: Mapeamento de Campus]]
  - [[references/42-chat-sec7-microfrontends|Sec 7: Microfrontends]]
  - [[references/42-chat-sec8-matchmaking-p2p|Sec 8: Matchmaking P2P]]
  - [[references/42-chat-sec9-observabilidade-bdd|Sec 9: Observabilidade e BDD]]

### API 42

- [[references/42-api-specification|42 API Specification]] — Guia de uso: OAuth2, paginação, filtros, rate limits (2 req/s, 1200 req/h) ( #42 #api)
- [[references/42-api-endpoints|42 API Endpoints]] — Catálogo de endpoints: 96 recursos, 739 endpoints organizados por relevância
- [[references/oauth2-42-pitfalls|OAuth2 42 Pitfalls]] — 3 pitfalls comuns: redirect_uri, shell env vars vs .env, React StrictMode ( #oauth2 #debug)

## Fontes Canônicas

As regras arquiteturais e stack tecnológica são mantidas em `.github/memory/` (versionadas no repo).
O vault referencia, mas não duplica. Consulte os arquivos diretamente:

- `.github/memory/constitution.md` — Regras, portões de qualidade, anti-padrões
- `.github/memory/tech.md` — Stack homologada (linguagens, frameworks, CI/CD)

## Journal

- [[journal/2026-06-14-sessao-qa-skills-42chat|2026-06-14 QA + Skills + Feature 100]] — Sessão de QA, 7 skills, feature 100, taxonomia
- [[journal/2026-06-17-brainstorm-feature-101|2026-06-17 Brainstorm Feature 101]] — Assinatura de Participação definida e aprovada ( #sdd #42chat)
