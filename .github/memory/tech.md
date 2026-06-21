# Stack Tecnológica — Framework SDD Autônomo

> O produto é o **framework SDD** (agentes Hermes + skills + pipeline),
> não o app de chat. O 42_chat será um smoke-test futuro pra validar o framework.
>
> Preenchido via `sdd-explore-tech` + input do usuário em 2026-06-13.
> Reexecute `sdd-explore-tech` para atualizar conforme novos artefatos forem adicionados.

## Runtime do Framework

| Componente | Tecnologia | Propósito |
|---|---|---|
| Agent host | Hermes Agent (Nous Research) | Execução dos agentes, tools, memória, cron |
| Provider LLM | DeepSeek V4 Pro (primário) | Modelo principal dos agentes |
| Provider LLM | Google Gemini (auxiliar) | Embeddings, Honcho reasoning |
| Provider LLM | Ollama (local, RPi 5) | Inferência local, nomic-embed-text |

## Linguagens do Framework

| Linguagem | Uso |
|---|---|
| Python | Skills (runtime das tools), scripts de validação |
| YAML | Config de agentes (`context.yaml`), frontmatter de skills |
| Markdown | Specs (`spec.md`, `plan.md`, `tasks.md`), docs, wiki |
| Shell (bash) | Scripts auxiliares, CI/CD |

## Agentes (`.hermes/agents/`)

| Agente | Status | Função |
|---|---|---|
| `onboard` | ✅ Implementado | Inicializa projeto SDD (init repo, explore tech, brainstorm) |
| `agent-orchestrator` | ✅ Implementado | Runtime: lê tasks.md DAG, spawna subagentes em paralelo |
| `agent-dev` | ❌ Feature 006 | Implementa código a partir de spec + contratos |
| `agent-qa` | ❌ Feature 007 | Testes unitários, Gherkin/Cucumber, lint |
| `agent-devops` | ❌ Feature 008 | CI/CD, Docker, deploy |
| `agent-pentester` | ❌ Feature 009 | Segurança, OWASP, secrets |

## Skills (`.hermes/skills/`)

### SDD Pipeline
| Skill | Versão | Função |
|---|---|---|
| `sdd-init-repo` | 1.0.0 | Inicializa estrutura SDD |
| `sdd-explore-tech` | 1.0.0 | Mapeia stack tecnológica |
| `sdd-validate` | 1.1.0 | Valida conformidade SDD |
| `sdd-brainstorm` | 1.0.0 | Brainstorm de features |
| `sdd-refactor-artifact` | 1.0.0 | Refatora artefatos SDD |
| `sdd-generate-plan` | 1.0.0 | Gera plan.md |
| `sdd-generate-tasks` | 2.0.0 | Gera tasks.md com DAG |

### Wiki & Conhecimento
| Skill | Função |
|---|---|
| `wiki-setup`, `wiki-ingest`, `wiki-query`, `wiki-capture` | Pipeline de knowledge management |
| `wiki-lint`, `wiki-cross-linker`, `wiki-tag-taxonomy` | Manutenção do vault |
| `wiki-status`, `wiki-dashboard`, `wiki-digest`, `wiki-export` | Monitoramento |
| `wiki/hermes-history-ingest`, `wiki/wiki-dedup`, `wiki/wiki-synthesize` | Operações específicas |

### Obsidian
| Skill | Função |
|---|---|
| `obsidian/obsidian-markdown`, `obsidian/obsidian-cli` | Formato e tooling |
| `obsidian/obsidian-bases`, `obsidian/json-canvas` | Bases e canvas |
| `obsidian/defuddle` | Extração limpa de markdown |

### Visual & Tooling
| Skill | Função |
|---|---|
| `visual/mermaid-visualizer` | Diagramas Mermaid |
| `skill-forge` | Criação de novas skills |
| `agent-run` | Execução de agentes com contexto |
| `git-conventional-commit` | Commits padronizados |

## Infraestrutura

| Componente | Detalhe |
|---|---|
| Homelab | RPi 5 (zeenyt-1), Docker, Tailscale |
| Memory | Honcho self-hosted (Docker, pgvector + Redis, Gemini LLM) |
| Vault | Obsidian vault versionado (`wiki/`) |
| CI/CD | GitHub Actions (branch flow + auto-PR) |

## Ferramentas de Qualidade

| Ferramenta | Propósito |
|---|---|
| `sdd-validate` | Validação estrutural SDD (PASS/FAIL/WARN) |
| `wiki-lint` | Integridade do vault Obsidian |
| `skill-forge` | Scaffold padronizado de skills |

## Atualizado em
2026-06-13
