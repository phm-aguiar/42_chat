---
title: "42_chat — Knowledge Base"
category: index
tags: [meta]
created: "2026-06-13"
updated: "2026-06-13"
---

# 42_chat Knowledge Base

> Vault do framework SDD autônomo. Agentes: `onboard` + `agent-orchestrator` + `agent-dev`.
> Estrutura segue taxonomia `llm-wiki`: concepts/ globais + projects/42_chat/ aninhado.

## Estrutura

- [[concepts/]] — Padrões, arquitetura, decisões de design (cross-project)
- [[skills/]] — Skills do framework (wiki, obsidian, visual)
- [[projects/42_chat/42_chat|42_chat]] — Overview do framework SDD
- [[projects/42_chat/features/]] — Features do framework
- [[projects/42_chat/agents/]] — Agentes Hermes
- [[projects/42_chat/skills/]] — Skills SDD

## Conceitos (cross-project)

- [[concepts/sdd|SDD]] — Spec-Driven Development: metodologia e pipeline
- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo com exemplo real
- [[concepts/onboarding|Onboarding]] — Como começar um projeto do zero

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
Documentos refinados a partir de insumos em `qafiles/`.

- [[references/qa-overview|QA & BDD no Framework SDD]] — Visão geral da estratégia de QA
- [[references/gherkin-syntax|Gherkin Syntax Reference]] — Sintaxe completa do Gherkin
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Boas práticas e anti-patterns
- [[references/gherkin-examples|Gherkin Examples]] — Exemplos reais de feature files
- [[references/cucumber-basics|Cucumber Basics]] — Framework Cucumber e step definitions
- [[references/playwright-bdd|Playwright BDD]] — Integração Playwright + BDD
- [[references/bdd-specification-process|BDD Specification Process]] — Fluxo Gherkin Expert
- [[references/tdd-methodology|TDD Methodology]] — Ciclo Red-Green-Refactor e anti-patterns

## Fontes Canônicas

As regras arquiteturais e stack tecnológica são mantidas em `.github/memory/` (versionadas no repo).
O vault referencia, mas não duplica. Consulte os arquivos diretamente:

- `.github/memory/constitution.md` — Regras, portões de qualidade, anti-padrões
- `.github/memory/tech.md` — Stack homologada (linguagens, frameworks, CI/CD)
