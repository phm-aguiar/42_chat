---
title: "Tag Taxonomy"
category: _meta
tags: [meta, taxonomy]
summary: "Taxonomia canônica de tags do vault. Use estas tags ao criar/editar páginas."
lifecycle: reviewed
created: "2026-06-19"
updated: "2026-06-20"
---

# Tag Taxonomy

> Vocabulário controlado para tags do vault. Toda página deve usar tags desta lista.
> Atualizado em 2026-06-20 via brain lint + taxonomy (Modo 3+4).

## Domain Tags (max 5 por página)

| Tag Canônica | Frequência | Aliases | Descrição |
|---|---|---|---|
| `sdd` | 31 | `spec-driven-development` | Spec-Driven Development, pipeline, features |
| `wiki` | 19 | `knowledge-management`, `obsidian`, `brain` | Vault, conhecimento, gestão de conhecimento |
| `qa` | 10 | `testing`, `qualidade`, `teste` | Testes, BDD, Gherkin, qualidade |
| `go` | 47 | `golang` | Código Go, patterns, convenções |
| `dev` | 2 | `desenvolvimento`, `implementacao`, `implementation` | Código, desenvolvimento, build |
| `github` | 2 | `git`, `versionamento` | GitHub, PR, issues, commits |
| `devops` | 1 | `infra`, `docker`, `infrastructure` | Infraestrutura, deploy, CI/CD |
| `visual` | 2 | `design`, `diagramas`, `diagram` | Design, diagramas, criatividade |
| `ml` | 1 | `machine-learning`, `ai`, `artificial-intelligence` | MLOps, modelos, inferência |
| `research` | 1 | `pesquisa`, `papers` | Pesquisa, arXiv, papers |
| `productivity` | 1 | `produtividade` | Ferramentas de produtividade |
| `media` | 1 | `audio`, `video`, `musica` | Áudio, vídeo, música, ComfyUI |
| `react` | 6 | `reactjs`, `frontend` | React, Vite, frontend |
| `vite` | 9 | `bundler`, `rolldown` | Vite, bundling, build tooling |
| `websocket` | 6 | `ws`, `real-time` | WebSockets, comunicação real-time |
| `go-style` | 43 | `style-guide`, `coding-standards`, `naming` | Guia de estilo Go, convenções |
| `go-patterns` | 20 | `patterns`, `idioms` | Padrões e idioms Go |
| `architecture` | 11 | `arquitetura`, `system-design` | Design de sistema, arquitetura |
| `agents` | 14 | `agent`, `multi-agent`, `orchestrator` | Agentes, orquestração, subagentes |
| `security` | 3 | `auth`, `oauth2`, `seguranca` | Autenticação, autorização, segurança |
| `thinking` | 9 | `reasoning`, `decision-making` | Pensamento, raciocínio, decisões |
| `brand` | 8 | `branding`, `identity` | Branding, identidade, descoberta |
| `template` | 8 | `templates`, `scaffold` | Templates reutilizáveis |
| `hermes` | 10 | `hermes-agent` | Hermes Agent, configuração, skills |
| `toolkit` | 4 | — | Páginas de toolkit consolidado |
| `concepts` | — | — | Conceitos, padrões, metodologia |
| `skills` | — | — | Documentação de skills/toolkits |
| `references` | — | — | Material de referência externo |
| `journal` | — | — | Sessões, decisões, linha do tempo |
| `meta` | — | — | Meta-informação sobre o vault |
| `42_chat` | 4 | `42chat` | Projeto 42 Chat |
| `42_Framework` | — | `42-framework` | Projeto 42 Framework |

## Research & Paper Tags (max 5 por paper + domain tags não contam)

| Tag Canônica | Frequência | Aliases | Descrição |
|---|---|---|---|
| `paper` | 3 | `artigo`, `publicacao` | Paper acadêmico ou artigo técnico |
| `multi-agent` | 2 | `multi-agente`, `agent-teams` | Sistemas multi-agente |
| `coordination` | 1 | `coordenacao`, `orchestration` | Coordenação entre agentes |
| `task-graph` | 1 | `grafo-de-tarefas`, `dag` | Grafo de tarefas (DAG) |
| `heartbeat` | 1 | `monitoring`, `straggler-detection` | Monitoramento de heartbeat |
| `mapreduce` | 1 | `map-reduce` | Paradigma MapReduce |
| `memory` | 1 | `memoria` | Memória e persistência |
| `retrieval` | 1 | `busca`, `search` | Recuperação de informação |
| `cross-task` | 1 | `cross-cutting` | Memória cross-task |
| `langgraph` | 1 | — | LangGraph framework |
| `stateful-agents` | 1 | `stateful` | Agentes com estado |
| `checkpointing` | 1 | `persistencia` | Checkpointing e persistência |
| `human-in-the-loop` | 1 | `hitl` | Human-in-the-loop |
| `production-patterns` | 1 | `producao` | Padrões de produção |

## Type Tags

| Tag | Descrição |
|---|---|
| `spec` | Especificação de feature |
| `plan` | Plano arquitetural |
| `tasks` | Matriz de tarefas DAG |
| `adr` | Decisão arquitetural |
| `template` | Template reutilizável |
| `pitfall` | Armadilhas e lições aprendidas |
| `formato` | Documentação de formato/sintaxe |
| `arquitetura` | Design de sistema |
| `skill` | Skill ou toolkit Hermes |
| `agente` | Subagente do framework |
| `synthesis` | Síntese e destilação |
| `tutorial` | Guia passo-a-passo |
| `reference` | Material de referência |
| `guide` | Guia de uso |
| `checklist` | Checklist de verificação |
| `overview` | Visão geral |

## System Tags (não contam no limite de 5)

| Tag | Descrição |
|---|---|
| `visibility/pii` | Contém dados pessoais |
| `visibility/internal` | Uso interno, não público |
| `visibility/public` | Público (default) |

## Regras

1. **Max 5 domain tags por página.** System tags e Research/Paper tags não contam.
2. **Use a forma canônica.** `go-style`, não `style-guide`. `agents` não `agent`. `go-patterns` não `patterns`.
3. **Não invente tags.** Se precisar de uma nova, proponha aqui primeiro.
4. **`visibility/` tags são system tags.** Não aparecem na taxonomia de domain tags.
5. **Tags no frontmatter YAML.** Ex: `tags: [sdd, wiki, concepts]`
6. **Papers usam Research Tags.** Papers em `references/papers/` podem usar as research tags + domain tags relevantes.
7. **Aliases são aceitos mas desencorajados.** O lint reporta aliases como warnings. Prefira sempre a forma canônica.

## Histórico de Atualizações

| Data | Mudança |
|---|---|
| 2026-06-20 | Brain lint + taxonomy. Top 20 tags por frequência tornam-se canônicas. Adicionadas Research Tags para papers. Adicionados `go-style`, `go-patterns`, `agents`, `architecture`, `security`, `thinking`, `brand`, `hermes`, `react`, `vite`, `websocket`, `42_chat`. |
| 2026-06-19 | Criação inicial. 17 domain tags, 10 type tags, 3 system tags. |
