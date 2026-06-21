# Matriz de Classificação de Skills Hermes

> **Feature:** 008-reavaliacao-skills
> **Data:** 2026-06-19
> **Total de skills auditadas:** 119
> **Objetivo:** Guiar a consolidação de ~130 skills em ~10 toolkits coesos.

## Legenda

| Campo | Significado |
|---|---|
| **Redundância** | Lista skills que fazem essencialmente a mesma coisa (sobreposição ≥ 60%) |
| **Granularidade** | `atômica` = 1 operação; `multi-modo` = modos internos; `referência` = doc de formato |
| **Usada por** | `agent-dev`, `agent-qa`, `agent-orchestrator`, `onboard`, ou `principal` (humano) |
| **Ação proposta** | `merge em <toolkit>`, `demover a referência no vault`, `manter como está`, `absorver duplicata` |

---

## Matriz Completa

### 1. Wiki (18 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 1 | `wiki-ingest` | wiki | — | multi-modo (append/full/raw/summary/URL) | principal | merge em `brain` |
| 2 | `wiki-query` | wiki | — | multi-modo (normal/index-only/filtered) | principal | merge em `brain` |
| 3 | `wiki-lint` | wiki | `vault-health` (subset), `cross-linker` (parcial), `tag-taxonomy` (parcial) | multi-modo (13 checks + --consolidate) | principal | merge em `brain` |
| 4 | `wiki-capture` | wiki | `wiki-ingest` (sobreposição parcial: ambos criam páginas) | multi-modo (normal + --quick) | principal | merge em `brain` |
| 5 | `cross-linker` | wiki | `wiki-lint --consolidate` Action 2 | atômica (7 steps, 1 operação) | principal | merge em `brain` (modo `weave`) |
| 6 | `wiki-dedup` | wiki | `wiki-lint` (parcial: ambos encontram colisões) | atômica | principal | merge em `brain` (modo `dedup`) |
| 7 | `wiki-synthesize` | wiki | `cross-linker` (parcial: ambos encontram conexões) | atômica | principal | merge em `brain` (modo `synthesize`) |
| 8 | `wiki-dashboard` | wiki | `wiki-status --insights` (parcial) | atômica | principal | merge em `brain` (modo `dashboard`) |
| 9 | `wiki-status` | wiki | `wiki-digest` (sobreposição conceitual) | multi-modo (delta + insights) | principal | merge em `brain` (modo `status`) |
| 10 | `wiki-digest` | wiki | `wiki-status` (parcial) | atômica | principal | merge em `brain` (modo `digest`) |
| 11 | `wiki-export` | wiki | — | atômica | principal | merge em `brain` (modo `export`) |
| 12 | `wiki-setup` | wiki | `hermes-wiki-setup` (duplicata explícita) | atômica | principal | merge em `brain` (modo `init`); absorver `hermes-wiki-setup` |
| 13 | `hermes-wiki-setup` | wiki | `wiki-setup` (duplicata explícita) | atômica | principal | absorvida por `brain` via `wiki-setup` |
| 14 | `vault-health` | wiki | `wiki-lint` (subset: 3 de 13 checks) | atômica | principal | merge em `brain` (modo `health`); absorver em `wiki-lint` |
| 15 | `tag-taxonomy` | wiki | `wiki-lint --consolidate` Action 5 | multi-modo (4 modos) | principal | merge em `brain` (modo `taxonomy`) |
| 16 | `hermes-history-ingest` | wiki | `wiki-ingest` (modo raw) | atômica | principal | merge em `brain` (modo ingest com source=hermes) |
| 17 | `document-consolidation` | wiki | `wiki-dedup` (parcial) | atômica | principal | merge em `brain` (modo `consolidate`) |
| 18 | `llm-wiki` | research/wiki | Referenciado por todas as skills wiki como fundação | referência | principal | demover a referência no vault; conteúdo integrado ao `brain` |

### 2. Obsidian (5 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 19 | `obsidian` | note-taking | `obsidian-cli` (parcial) | multi-modo (read/search/create/edit) | principal | demover a referência no vault (wrapper genérico) |
| 20 | `obsidian-cli` | obsidian | `obsidian` (sobreposição funcional) | referência (CLI command reference) | principal | demover a referência no vault |
| 21 | `obsidian-markdown` | obsidian | — | referência (formato OFM) | principal | demover a referência no vault (formato) |
| 22 | `json-canvas` | obsidian | — | referência (formato JSON Canvas) | principal | demover a referência no vault (formato) |
| 23 | `obsidian-bases` | obsidian | `wiki-dashboard` (parcial) | referência (formato .base) | principal | demover a referência no vault (formato) |

### 3. Documentação (3 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 24 | `doc-extract` | doc | `doc-generate-toc` (tem operação TOC embutida) | atômica | principal | merge em `brain` (modo `extract`) |
| 25 | `doc-generate-toc` | doc | `doc-extract` Operação 1 | atômica | principal | merge em `brain` (modo `toc`); absorver em `doc-extract` |
| 26 | `doc-generate-llms-txt` | doc | — | atômica | principal | demover a referência no vault (operação rara) |

### 4. SDD (9 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 27 | `sdd-brainstorm` | sdd | — | atômica | principal | merge em `sdd` (modo `brainstorm`) |
| 28 | `sdd-generate-plan` | sdd | `plan` (software-dev; escopo diferente) | atômica | principal | merge em `sdd` (modo `plan`) |
| 29 | `sdd-generate-tasks` | sdd | — | atômica | principal | merge em `sdd` (modo `tasks`) |
| 30 | `sdd-init-repo` | sdd | — | atômica | principal, onboard | merge em `sdd` (modo `init`) |
| 31 | `sdd-refactor-artifact` | sdd | — | atômica | principal | merge em `sdd` (modo `refactor`) |
| 32 | `sdd-validate` | sdd | — | atômica | principal | merge em `sdd` (modo `validate`) |
| 33 | `sdd-explore-tech` | sdd | — | atômica | principal | merge em `sdd` (modo `explore-tech`) |
| 34 | `sdd-wiki-enforcement` | sdd | — | atômica | principal | merge em `sdd` (modo `wiki-enforce`) |
| 35 | `agent-persona-pattern` | sdd | — | referência | onboard | demover a referência no vault |

### 5. QA (7 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 36 | `bdd-spec-process` | qa | — | atômica | agent-qa, onboard | merge em `qa-toolkit` (modo `bdd-spec`) |
| 37 | `gherkin-scenarios` | qa | — | atômica | agent-qa | merge em `qa-toolkit` (modo `gherkin`) |
| 38 | `cucumber-step-definitions` | qa | — | atômica | agent-qa | merge em `qa-toolkit` (modo `cucumber`) |
| 39 | `go-unit-tests` | qa | — | atômica | agent-qa | merge em `qa-toolkit` (modo `unit-tests`) |
| 40 | `local-test-runner` | qa | `build-check` (sobreposição: ambos rodam go build/vet/test) | atômica | agent-qa | merge em `qa-toolkit` (modo `test-runner`) |
| 41 | `playwright-bdd-e2e` | qa | — | atômica | agent-qa | merge em `qa-toolkit` (modo `e2e`) |
| 42 | `tdd-workflow` | qa | `test-driven-development` (software-dev; duplicata explícita) | atômica | agent-qa, agent-dev | merge em `qa-toolkit`; absorver `test-driven-development` |

### 6. Dev (3 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 43 | `build-check` | dev | `local-test-runner` (sobreposição: ambos go build/vet) | atômica | agent-dev | merge em `dev-toolkit` (modo `build-check`) |
| 44 | `go-implement` | dev | — | atômica | agent-dev | merge em `dev-toolkit` (modo `go`) |
| 45 | `react-implement` | dev | — | atômica | agent-dev | merge em `dev-toolkit` (modo `react`) |

### 7. Software Development (7 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 46 | `plan` | software-development | `sdd-generate-plan` (escopo diferente: plan genérico vs SDD) | atômica | principal | merge em `dev-toolkit` (modo `plan`) |
| 47 | `spike` | software-development | — | atômica | principal, agent-dev | merge em `dev-toolkit` (modo `spike`) |
| 48 | `test-driven-development` | software-development | `tdd-workflow` (qa; duplicata explícita) | atômica | agent-dev | absorvida por `qa-toolkit` |
| 49 | `systematic-debugging` | software-development | — | atômica | principal, agent-dev | merge em `dev-toolkit` (modo `debug`) |
| 50 | `requesting-code-review` | software-development | `github-code-review` (parcial) | atômica | principal | merge em `dev-toolkit` (modo `code-review`) |
| 51 | `simplify-code` | software-development | — | atômica | agent-dev | merge em `dev-toolkit` (modo `simplify`) |
| 52 | `node-inspect-debugger` | software-development | `python-debugpy` (domínio diferente) | atômica | agent-dev | merge em `dev-toolkit` (modo `node-debug`) |
| 53 | `python-debugpy` | software-development | — | atômica | agent-dev | merge em `dev-toolkit` (modo `python-debug`) |

### 8. DevOps (6 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 54 | `docker-dev-environment` | devops | — | atômica | principal | merge em `devops` (modo `docker-dev`) |
| 55 | `honcho-self-hosted` | devops | — | atômica | principal | merge em `devops` (modo `honcho`) |
| 56 | `honcho-save-conclusion` | devops | — | atômica | principal | merge em `devops` (modo `honcho-save`) |
| 57 | `kanban-orchestrator` | devops | `kanban-worker` (papéis complementares) | atômica | agent-orchestrator | merge em `devops` (modo `kanban-orch`) |
| 58 | `kanban-worker` | devops | `kanban-orchestrator` (papéis complementares) | atômica | agent-orchestrator | merge em `devops` (modo `kanban-work`) |
| 59 | `linux-audio` | devops | — | atômica | principal | merge em `devops` (modo `linux-audio`) |

### 9. GitHub (7 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 60 | `github-auth` | github | — | atômica | principal | merge em `github` (modo `auth`) |
| 61 | `github-pr-workflow` | github | — | atômica | principal | merge em `github` (modo `pr`) |
| 62 | `github-code-review` | github | `requesting-code-review` (parcial) | atômica | principal | merge em `github` (modo `review`) |
| 63 | `github-issues` | github | — | atômica | principal | merge em `github` (modo `issues`) |
| 64 | `github-repo-management` | github | — | atômica | principal | merge em `github` (modo `repo`) |
| 65 | `git-conventional-commit` | github | — | atômica | principal, agent-dev | merge em `github` (modo `commit`) |
| 66 | `codebase-inspection` | github | — | atômica | principal | merge em `github` (modo `inspect`) |

### 10. Creative (16 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 67 | `ascii-art` | creative | — | atômica | principal | merge em `visual` (modo `ascii`) |
| 68 | `ascii-video` | creative | — | atômica | principal | merge em `visual` (modo `ascii-video`) |
| 69 | `architecture-diagram` | creative | `excalidraw`, `mermaid-visualizer` (parcial) | atômica | principal | merge em `visual` (modo `arch-diagram`) |
| 70 | `baoyu-infographic` | creative | — | atômica | principal | merge em `visual` (modo `infographic`) |
| 71 | `claude-design` | creative | `sketch` (sobreposição parcial) | atômica | principal | merge em `visual` (modo `design`) |
| 72 | `sketch` | creative | `claude-design` (sobreposição parcial) | atômica | principal | merge em `visual` (modo `sketch`) |
| 73 | `comfyui` | creative | — | atômica | principal | merge em `visual` (modo `comfyui`) |
| 74 | `design-md` | creative | — | referência (DESIGN.md token spec) | principal | demover a referência no vault |
| 75 | `excalidraw` | creative | `architecture-diagram`, `mermaid-visualizer` | atômica | principal | merge em `visual` (modo `excalidraw`) |
| 76 | `humanizer` | creative | — | atômica | principal | merge em `visual` (modo `humanize`) |
| 77 | `manim-video` | creative | — | atômica | principal | merge em `visual` (modo `manim`) |
| 78 | `p5js` | creative | — | atômica | principal | merge em `visual` (modo `p5js`) |
| 79 | `popular-web-designs` | creative | — | atômica | principal | merge em `visual` (modo `web-designs`) |
| 80 | `pretext` | creative | — | atômica | principal | merge em `visual` (modo `pretext`) |
| 81 | `songwriting-and-ai-music` | creative | `heartmula` (parcial) | atômica | principal | merge em `visual` (modo `songwrite`) |
| 82 | `touchdesigner-mcp` | creative | — | atômica | principal | merge em `visual` (modo `touchdesigner`) |

### 11. Visual (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 83 | `mermaid-visualizer` | visual | `architecture-diagram`, `excalidraw` | atômica | principal | merge em `visual` (modo `mermaid`) |

### 12. MLOps (7 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 84 | `huggingface-hub` | mlops | — | atômica | principal | merge em `ml` (modo `hf-hub`) |
| 85 | `llama-cpp` | mlops | `serving-llms-vllm` (domínio relacionado, tool diferente) | atômica | principal | merge em `ml` (modo `llama-cpp`) |
| 86 | `serving-llms-vllm` | mlops | `llama-cpp` (domínio relacionado) | atômica | principal | merge em `ml` (modo `vllm`) |
| 87 | `audiocraft-audio-generation` | mlops | — | atômica | principal | merge em `ml` (modo `audiocraft`) |
| 88 | `segment-anything-model` | mlops | — | atômica | principal | merge em `ml` (modo `sam`) |
| 89 | `evaluating-llms-harness` | mlops | — | atômica | principal | merge em `ml` (modo `eval`) |
| 90 | `weights-and-biases` | mlops | — | atômica | principal | merge em `ml` (modo `wandb`) |

### 13. Data Science (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 91 | `jupyter-live-kernel` | data-science | — | atômica | principal | merge em `ml` (modo `jupyter`) |

### 14. Research (5 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 92 | `arxiv` | research | — | atômica | principal | merge em `research` (modo `arxiv`) |
| 93 | `blogwatcher` | research | — | atômica | principal | merge em `research` (modo `blogwatch`) |
| 94 | `polymarket` | research | — | atômica | principal | merge em `research` (modo `polymarket`) |
| 95 | `research-paper-writing` | research | — | atômica | principal | merge em `research` (modo `paper-write`) |
| 96 | `defuddle` | obsidian | — | atômica | principal | merge em `research` (modo `defuddle`); ferramenta de extração web |

### 15. Productivity (8 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 97 | `airtable` | productivity | — | atômica | principal | merge em `productivity` (modo `airtable`) |
| 98 | `google-workspace` | productivity | — | atômica | principal | merge em `productivity` (modo `gworkspace`) |
| 99 | `maps` | productivity | — | atômica | principal | merge em `productivity` (modo `maps`) |
| 100 | `nano-pdf` | productivity | `ocr-and-documents` (parcial) | atômica | principal | merge em `productivity` (modo `pdf-edit`) |
| 101 | `notion` | productivity | — | atômica | principal | merge em `productivity` (modo `notion`) |
| 102 | `ocr-and-documents` | productivity | `nano-pdf` (parcial) | atômica | principal | merge em `productivity` (modo `ocr`) |
| 103 | `powerpoint` | productivity | — | atômica | principal | merge em `productivity` (modo `pptx`) |
| 104 | `teams-meeting-pipeline` | productivity | — | atômica | principal | merge em `productivity` (modo `teams`) |

### 16. Media (4 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 105 | `gif-search` | media | — | atômica | principal | merge em `productivity` (modo `gif`) |
| 106 | `heartmula` | media | `songwriting-and-ai-music` (parcial: ambos geram música) | atômica | principal | merge em `visual` (modo `heartmula`) |
| 107 | `songsee` | media | — | atômica | principal | merge em `visual` (modo `songsee`) |
| 108 | `youtube-content` | media | — | atômica | principal | merge em `research` (modo `youtube`) |

### 17. Email (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 109 | `himalaya` | email | — | atômica | principal | merge em `productivity` (modo `email`) |

### 18. Social Media (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 110 | `xurl` | social-media | — | atômica | principal | merge em `productivity` (modo `x`) |

### 19. Smart Home (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 111 | `openhue` | smart-home | — | atômica | principal | merge em `productivity` (modo `hue`) |

### 20. Autonomous AI Agents (4 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 112 | `claude-code` | autonomous-ai-agents | `codex`, `opencode` (delegam código para CLIs diferentes) | atômica | principal | merge em `dev-toolkit` (modo `claude-code`) |
| 113 | `codex` | autonomous-ai-agents | `claude-code`, `opencode` | atômica | principal | merge em `dev-toolkit` (modo `codex`) |
| 114 | `opencode` | autonomous-ai-agents | `claude-code`, `codex` | atômica | principal | merge em `dev-toolkit` (modo `opencode`) |
| 115 | `hermes-agent` | autonomous-ai-agents | — | atômica | principal | merge em `dev-toolkit` (modo `hermes-config`) |

### 21. General (1 skill)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 116 | `skill-forge` | general | — | atômica | principal | merge em `dev-toolkit` (modo `skill-forge`) |

### 22. Misc — Agentes e Operações (3 skills)

| Nº | Nome | Categoria | Redundância | Granularidade | Usada por | Ação Proposta |
|----|------|-----------|-------------|---------------|-----------|---------------|
| 117 | `agent-run` | (sem categoria) | — | atômica | principal | merge em `dev-toolkit` (modo `agent-run`) |
| 118 | `dogfood` | (sem categoria) | — | atômica | principal | merge em `qa-toolkit` (modo `dogfood`) |
| 119 | `yuanbao` | (sem categoria) | — | atômica | principal | merge em `productivity` (modo `yuanbao`) |

---

## Resumo Estatístico

### Distribuição por Ação Proposta

| Ação | Contagem | % |
|---|---|---|
| **merge em `brain`** | 30 | 25.2% |
| **merge em `visual`** | 20 | 16.8% |
| **merge em `dev-toolkit`** | 15 | 12.6% |
| **merge em `productivity`** | 15 | 12.6% |
| **merge em `sdd`** | 9 | 7.6% |
| **merge em `github`** | 7 | 5.9% |
| **merge em `qa-toolkit`** | 8 | 6.7% |
| **merge em `ml`** | 8 | 6.7% |
| **merge em `research`** | 6 | 5.0% |
| **merge em `devops`** | 6 | 5.0% |
| **demover a referência no vault** | 8 | 6.7% |
| **absorver duplicata** | 3 | 2.5% |
| **manter como está** | 0 | 0% |

### Distribuição por Granularidade

| Granularidade | Contagem | % |
|---|---|---|
| atômica | 87 | 73.1% |
| multi-modo | 7 | 5.9% |
| referência | 8 | 6.7% |
| (implícita atômica) | 17 | 14.3% |

### Distribuição por Subagente

| Subagente | Skills que usa |
|---|---|
| **principal** (humano) | 107 (89.9%) |
| **agent-dev** | 15 (12.6%) |
| **agent-qa** | 8 (6.7%) |
| **agent-orchestrator** | 2 (1.7%) |
| **onboard** | 2 (1.7%) |

### Redundâncias Detectadas (≥ 60% sobreposição)

| Par | Tipo | Resolução |
|---|---|---|
| `wiki-setup` ↔ `hermes-wiki-setup` | duplicata explícita | absorver `hermes-wiki-setup` em `brain` (modo `init`) |
| `vault-health` ↔ `wiki-lint` | subset (3/13 checks) | merge em `brain` (modo `health`) |
| `cross-linker` ↔ `wiki-lint --consolidate` | sobreposição parcial | ambos em `brain` como modos distintos |
| `tag-taxonomy` ↔ `wiki-lint --consolidate` | sobreposição parcial | ambos em `brain` como modos distintos |
| `doc-generate-toc` ↔ `doc-extract` (Operação 1) | subset | absorver TOC em `doc-extract` |
| `tdd-workflow` ↔ `test-driven-development` | duplicata explícita | absorver `test-driven-development` em `qa-toolkit` |
| `local-test-runner` ↔ `build-check` | sobreposição parcial (go build/vet) | toolkits separados (qa vs dev) |
| `obsidian` ↔ `obsidian-cli` | sobreposição funcional | ambos demovidos a referências |
| `claude-design` ↔ `sketch` | sobreposição parcial | ambos em `visual` como modos distintos |
| `architecture-diagram` ↔ `excalidraw` ↔ `mermaid-visualizer` | sobreposição parcial | todos em `visual` como modos distintos |

---

## Mapa de Consolidação: 10 Toolkits

| Toolkit | Skills Absorvidas | Subagentes | Tamanho Estimado |
|---|---|---|---|
| **`brain`** | 30 (wiki 18 + obsidian 5 + doc 3 + llm-wiki + defuddle + document-consolidation + hermes-wiki-setup) | principal | ~15KB |
| **`sdd`** | 9 (sdd 8 + agent-persona-pattern → ref) | principal, onboard | ~10KB |
| **`qa-toolkit`** | 8 (qa 7 + test-driven-development + dogfood) | agent-qa | ~12KB |
| **`dev-toolkit`** | 15 (dev 3 + software-dev 7 + autonomous-ai 4 + skill-forge) | agent-dev | ~14KB |
| **`github`** | 7 (github 6 + codebase-inspection) | principal, agent-dev | ~8KB |
| **`devops`** | 6 (devops 5 + linux-audio) | principal, agent-orchestrator | ~8KB |
| **`visual`** | 20 (creative 16 + visual 1 + media 3) | principal | ~14KB |
| **`ml`** | 8 (mlops 7 + data-science 1) | principal | ~10KB |
| **`research`** | 6 (research 5 + defuddle + youtube-content) | principal | ~8KB |
| **`productivity`** | 15 (productivity 8 + email 1 + social 1 + smart-home 1 + media 1 + misc 3) | principal | ~12KB |

**Total: 119 skills → 10 toolkits + 8 referências no vault**

---

## Notas da Auditoria

1. **`llm-wiki` é a fundação**: esta skill em `research/` é referenciada por TODAS as skills wiki como fonte dos "Retrieval Primitives", "Config Resolution Protocol", templates de página e convenções de formatação. Não é redundante — é o alicerce arquitetural. Deve ser integrada ao `brain` como seção de referência, não como modo separado.

2. **`obsidian-cli` é dependência interna**: embora classificada como "referência", é usada programaticamente por outras skills para operações de vault. Deve permanecer como referência no vault, acessível via `brain`.

3. **Skills multi-modo são raras (7 de 119)**: Apenas `wiki-lint`, `wiki-query`, `wiki-status`, `wiki-capture`, `wiki-ingest`, `tag-taxonomy` e `wiki-digest` já possuem modos internos. Isso reforça a tese da spec: a granularidade atual é predominantemente atômica.

4. **89.9% das skills são usadas pelo agente principal (humano)**: Apenas ~10% são específicas de subagentes. Isso sugere que a consolidação beneficia primariamente o operador humano, simplificando a descoberta e o carregamento.

5. **Sobreposição `doc-extract`/`doc-generate-toc`**: `doc-extract` já contém uma "Operação 1: Gerar Tabela de Conteúdo" que duplica `doc-generate-toc`. A consolidação natural é `doc-generate-toc` ser absorvido como modo de `doc-extract`.

6. **`hermes-wiki-setup` é especialização de `wiki-setup`**: A skill específica para Hermes adiciona o padrão repo-embedded vault. A consolidação deve preservar ambas as capacidades como modos (`init` vs `init-hermes`) dentro do `brain`.

7. **Skills de formato são 8**: `obsidian-markdown`, `json-canvas`, `obsidian-bases`, `design-md`, `obsidian-cli`, `obsidian`, `defuddle`, `agent-persona-pattern`. Todas devem ser demovidas a páginas de referência no vault (não são workflows, são documentação de formato/API).

8. **Toolkit `visual` é o maior (20 skills)**: Pode precisar de subdivisão se o SKILL.md combinado exceder 15KB. Alternativa: split em `visual` (design/diagramas) e `media` (áudio/vídeo).
