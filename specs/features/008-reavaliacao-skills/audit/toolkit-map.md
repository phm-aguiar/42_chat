# Mapa Final de Consolidação de Toolkits

> **Feature:** 008-reavaliacao-skills — T003
> **Fonte:** T001 (skill-matrix.md) + T002 (agent-usage.md)
> **Data:** 2026-06-19
> **Status:** Aprovado para execução (Fase 2)

## Visão Geral

```
ANTES:  119 skills atômicas (73% atômicas, 6% multi-modo, 7% referência)
        17 categorias fragmentadas
        Subagentes carregam 5-10 skills por tarefa

DEPOIS: 10 toolkits coesos
        8 referências no vault (desativadas como entry-points)
        3 skills absorvidas como duplicatas
        Subagentes carregam 1-2 toolkits
```

## Toolkits (ordem de prioridade)

### 1. `brain` — Wiki + Obsidian + Docs
- **Absorve:** 30 skills
- **Usuário:** Principal (humano)
- **Arquivo:** `.hermes/skills/wiki/brain/SKILL.md`
- **Tamanho estimado:** ~15KB (atenção ao limite)

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `ingest` | wiki-ingest, wiki-capture, wiki-hermes-history-ingest, document-consolidation | Entrada de conhecimento (fontes, sessões, histórico, consolidação) |
| `query` | wiki-query | Leitura do cérebro (normal, index-only, filtered, multi-hop) |
| `lint` | wiki-lint, vault-health | Saúde e auditoria (13 checks + --consolidate) |
| `weave` | wiki-cross-linker, wiki-dedup, wiki-synthesize, wiki-tag-taxonomy | Tecer/ligar/descobrir conexões e deduplicar |
| `report` | wiki-dashboard, wiki-status, wiki-digest, wiki-export | Visualizações e relatórios |
| `init` | wiki-setup (absorve hermes-wiki-setup como sub-modo `--hermes`) | Inicializar vault |
| `extract` | doc-extract (absorve doc-generate-toc como sub-modo `--toc`) | Extrair seções e gerar TOC |
| `format` | N/A (referencia vault: ofm-spec, obsidian-cli, json-canvas, obsidian-bases) | Consulta de formato OFM e tooling |

**Referências no vault (desativadas como entry-points):**
- `references/ofm-spec.md` ← obsidian-markdown, obsidian-cli, obsidian-bases, json-canvas
- `references/llm-wiki-foundation.md` ← llm-wiki (fundação teórica, referenciada por todas as skills wiki)

**Skills absorvidas (duplicatas):**
- `hermes-wiki-setup` → absorvida por `brain` modo `init --hermes`
- `vault-health` → absorvida por `brain` modo `lint --fast`
- `doc-generate-toc` → absorvida por `brain` modo `extract --toc`
- `tag-taxonomy` → absorvida por `brain` modo `weave --taxonomy`
- `cross-linker` → absorvida por `brain` modo `weave --cross-link`

### 2. `sdd` — Pipeline SDD
- **Absorve:** 9 skills
- **Usuário:** Principal, onboard
- **Arquivo:** `.hermes/skills/sdd/sdd/SKILL.md`
- **Tamanho estimado:** ~10KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `brainstorm` | sdd-brainstorm | Entrevista interativa → spec.md |
| `explore-tech` | sdd-explore-tech | Mapear stack → tech.md |
| `init-repo` | sdd-init-repo | Inicializar estrutura SDD |
| `plan` | sdd-generate-plan | Gerar plan.md arquitetural |
| `tasks` | sdd-generate-tasks | Gerar tasks.md com DAG |
| `validate` | sdd-validate | Validar conformidade SDD |
| `refactor` | sdd-refactor-artifact | Normalizar artefatos |
| `wiki-enforce` | sdd-wiki-enforcement | Wire wiki enforcement no AGENTS.md |

**Referências no vault:**
- `references/agent-persona-pattern.md` ← agent-persona-pattern (padrão arquitetural, não workflow)

### 3. `qa-toolkit` — Qualidade e Testes
- **Absorve:** 8 skills
- **Usuário:** agent-qa
- **Arquivo:** `.hermes/skills/qa/qa-toolkit/SKILL.md`
- **Tamanho estimado:** ~12KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `bdd-spec` | bdd-spec-process | Discovery BDD → especificação |
| `gherkin` | gherkin-scenarios | Cenários Gherkin (.feature) |
| `cucumber` | cucumber-step-definitions | Step definitions (Godog) |
| `unit-tests` | go-unit-tests | Testes unitários Go (table-driven) |
| `test-runner` | local-test-runner | Build + vet + test + cover |
| `e2e` | playwright-bdd-e2e | E2E com Playwright + BDD |
| `tdd` | tdd-workflow (absorve test-driven-development) | Ciclo RED-GREEN-REFACTOR |
| `dogfood` | dogfood | QA exploratória de web apps |

**Skills absorvidas (duplicatas):**
- `test-driven-development` → absorvida por `qa-toolkit` modo `tdd`

### 4. `dev-toolkit` — Desenvolvimento e Runtime
- **Absorve:** 15 skills
- **Usuário:** agent-dev
- **Arquivo:** `.hermes/skills/dev/dev-toolkit/SKILL.md`
- **Tamanho estimado:** ~14KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `go` | go-implement | Implementar Go (Chi, WebSocket, PostgreSQL) |
| `react` | react-implement | Implementar React (Vite, Tailwind, Shadcn) |
| `build-check` | build-check | Smoke test: go build + vet + npm build |
| `plan` | plan (software-dev) | Plano markdown, sem execução |
| `spike` | spike | Experimento throwaway para validar ideia |
| `debug` | systematic-debugging | Debug de 4 fases (root cause) |
| `code-review` | requesting-code-review | Pre-commit review (security, quality) |
| `simplify` | simplify-code | Cleanup paralelo de 3 agentes |
| `node-debug` | node-inspect-debugger | Debug Node.js (Chrome DevTools Protocol) |
| `python-debug` | python-debugpy | Debug Python (pdb + debugpy DAP) |
| `claude-code` | claude-code | Delegar para Claude Code CLI |
| `codex` | codex | Delegar para OpenAI Codex CLI |
| `opencode` | opencode | Delegar para OpenCode CLI |
| `hermes-config` | hermes-agent | Configurar/estender Hermes Agent |
| `skill-forge` | skill-forge | Criar novas skills |

### 5. `github` — GitHub Workflow
- **Absorve:** 7 skills
- **Usuário:** Principal, agent-dev (modo commit)
- **Arquivo:** `.hermes/skills/github/github/SKILL.md`
- **Tamanho estimado:** ~8KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `auth` | github-auth | Autenticação (HTTPS, SSH, gh CLI) |
| `pr` | github-pr-workflow | PR lifecycle (branch, commit, open, merge) |
| `review` | github-code-review | Code review (diffs, inline comments) |
| `issues` | github-issues | Issues (criar, triar, label, assign) |
| `repo` | github-repo-management | Repos (clone, create, fork, remotes) |
| `commit` | git-conventional-commit | Commits padronizados |
| `inspect` | codebase-inspection | Inspeção (LOC, linguagens, ratios) |

### 6. `devops` — Infraestrutura e Operações
- **Absorve:** 6 skills
- **Usuário:** Principal, agent-orchestrator
- **Arquivo:** `.hermes/skills/devops/devops/SKILL.md`
- **Tamanho estimado:** ~8KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `docker-dev` | docker-dev-environment | Docker Compose dev (API + DB + frontend) |
| `honcho` | honcho-self-hosted | Deploy Honcho self-hosted |
| `honcho-save` | honcho-save-conclusion | Salvar conclusões no Honcho |
| `kanban-orch` | kanban-orchestrator | Decomposição e orquestração Kanban |
| `kanban-work` | kanban-worker | Worker Kanban (pitfalls, edge cases) |
| `linux-audio` | linux-audio | Debug áudio Linux (PipeWire/PulseAudio) |

### 7. `visual` — Design e Diagramas
- **Absorve:** 13 skills
- **Usuário:** Principal
- **Arquivo:** `.hermes/skills/creative/visual/SKILL.md`
- **Tamanho estimado:** ~10KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `mermaid` | mermaid-visualizer | Diagramas Mermaid |
| `arch-diagram` | architecture-diagram | SVG arquitetura dark-themed |
| `excalidraw` | excalidraw | Diagramas hand-drawn |
| `design` | claude-design | HTML artifacts (landing, deck, prototype) |
| `sketch` | sketch | Mockups throwaway (2-3 variantes) |
| `p5js` | p5js | Sketches gen art, shaders, 3D |
| `manim` | manim-video | Animações matemáticas (3Blue1Brown) |
| `ascii` | ascii-art | ASCII art (pyfiglet, cowsay, boxes) |
| `infographic` | baoyu-infographic | Infográficos (21 layouts × 21 estilos) |
| `web-designs` | popular-web-designs | 54 design systems como HTML/CSS |
| `pretext` | pretext | Demos tipográficas (@chenglou/pretext) |
| `touchdesigner` | touchdesigner-mcp | Controle TouchDesigner via MCP |
| `humanize` | humanizer | Humanizar texto (strip AI-isms) |

### 8. `media` — Áudio, Vídeo e Música
- **Absorve:** 7 skills
- **Usuário:** Principal
- **Arquivo:** `.hermes/skills/creative/media/SKILL.md`
- **Tamanho estimado:** ~7KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `ascii-video` | ascii-video | Vídeo ASCII MP4/GIF |
| `songwrite` | songwriting-and-ai-music | Songwriting + Suno AI prompts |
| `heartmula` | heartmula | HeartMuLa (Suno-like song generation) |
| `songsee` | songsee | Audio spectrograms/features |
| `comfyui` | comfyui | ComfyUI (imagens, vídeo, áudio) |
| `gif` | gif-search | Buscar/download GIFs (Tenor) |
| `design-md` | design-md | DESIGN.md token spec |
- `visual` (design/diagramas: mermaid, arch-diagram, excalidraw, design, sketch, p5js, manim, ascii, ascii-video, infographic, web-designs, pretext, touchdesigner)
- `media` (áudio/vídeo/criatividade: humanize, songwrite, heartmula, songsee, comfyui, gif-search, design-md)

### 8. `ml` — Machine Learning Ops
- **Absorve:** 8 skills
- **Usuário:** Principal
- **Arquivo:** `.hermes/skills/mlops/ml/SKILL.md`
- **Tamanho estimado:** ~10KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `hf-hub` | huggingface-hub | HuggingFace (search, download, upload) |
| `llama-cpp` | llama-cpp | Inferência local GGUF |
| `vllm` | serving-llms-vllm | High-throughput LLM serving |
| `eval` | evaluating-llms-harness | Benchmark LLMs (MMLU, GSM8K) |
| `wandb` | weights-and-biases | Experiment tracking, sweeps |
| `audiocraft` | audiocraft-audio-generation | AudioCraft (MusicGen, AudioGen) |
| `sam` | segment-anything-model | Segmentação zero-shot de imagens |
| `jupyter` | jupyter-live-kernel | Kernel Jupyter iterativo |

### 9. `research` — Pesquisa e Conhecimento
- **Absorve:** 6 skills
- **Usuário:** Principal
- **Arquivo:** `.hermes/skills/research/research/SKILL.md`
- **Tamanho estimado:** ~8KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `arxiv` | arxiv | Buscar papers (keyword, autor, categoria) |
| `blogwatch` | blogwatcher | Monitorar blogs e RSS/Atom |
| `polymarket` | polymarket | Query Polymarket (preços, mercados) |
| `paper-write` | research-paper-writing | Escrever papers ML (NeurIPS/ICML/ICLR) |
| `defuddle` | defuddle | Extrair markdown limpo de páginas web |
| `youtube` | youtube-content | YouTube transcripts → resumos |

### 10. `productivity` — Produtividade e Integrações
- **Absorve:** 15 skills
- **Usuário:** Principal
- **Arquivo:** `.hermes/skills/productivity/productivity/SKILL.md`
- **Tamanho estimado:** ~12KB

| Modo | Skills absorvidas | Descrição |
|---|---|---|
| `airtable` | airtable | Airtable REST API (CRUD, filters) |
| `gworkspace` | google-workspace | Gmail, Calendar, Drive, Docs, Sheets |
| `notion` | notion | Notion API (pages, databases, markdown) |
| `pptx` | powerpoint | PowerPoint (.pptx decks, slides) |
| `pdf-edit` | nano-pdf | Editar PDF (texto/títulos via NL) |
| `ocr` | ocr-and-documents | Extrair texto de PDFs/scans |
| `maps` | maps | Geocode, POIs, rotas (OSM/OSRM) |
| `teams` | teams-meeting-pipeline | Teams meeting summary pipeline |
| `email` | himalaya | Email CLI (IMAP/SMTP) |
| `x` | xurl | X/Twitter (post, search, DM, media) |
| `hue` | openhue | Philips Hue (luzes, cenas, rooms) |
| `gif` | gif-search | Buscar/download GIFs (Tenor) |
| `yuanbao` | yuanbao | Yuanbao groups (@mention, query) |

---

## Sumário de Consolidação

| # | Toolkit | Skills | Tamanho | Usuários |
|---|---|---|---|---|
| 1 | `brain` | 30 | ~15KB ⚠️ | Principal |
| 2 | `sdd` | 9 | ~10KB | Principal, onboard |
| 3 | `qa-toolkit` | 8 | ~12KB | agent-qa |
| 4 | `dev-toolkit` | 15 | ~14KB | agent-dev |
| 5 | `github` | 7 | ~8KB | Principal, agent-dev |
| 6 | `devops` | 6 | ~8KB | Principal, agent-orchestrator |
| 7 | `visual` | 13 | ~10KB | Principal |
| 8 | `media` | 7 | ~7KB | Principal |
| 9 | `ml` | 8 | ~10KB | Principal |
| 10 | `research` | 6 | ~8KB | Principal |
| 11 | `productivity` | 15 | ~12KB | Principal |

**Total: 124 ações em 119 skills** (5 skills absorvidas como duplicatas + 8 demovidas a referências no vault + 111 merge em 11 toolkits)

## Skills Demovidas a Referências no Vault (8)

Estas skills não são workflows decisionais — são documentação de formato/API. Viram páginas no vault, carregadas sob demanda via `brain query`:

| Skill | Página vault | Motivo |
|---|---|---|
| `obsidian-markdown` | `references/ofm-spec.md` | Formato OFM (sintaxe) |
| `obsidian-cli` | `references/ofm-spec.md` | Dependência interna, documentada junto com OFM |
| `obsidian-bases` | `references/ofm-spec.md` | Formato .base |
| `json-canvas` | `references/ofm-spec.md` | Formato .canvas |
| `obsidian` | `references/ofm-spec.md` | Wrapper genérico (sobreposição com obsidian-cli) |
| `design-md` | `references/design-md-spec.md` | DESIGN.md token spec |
| `agent-persona-pattern` | `references/agent-persona-pattern.md` | Padrão arquitetural, não workflow |
| `doc-generate-llms-txt` | `references/doc-tools.md` | Operação rara, referência bastaria |

## Skills Duplicatas Absorvidas (5)

| Duplicata | Absorvida por | Toolkit | Modo |
|---|---|---|---|
| `hermes-wiki-setup` | `wiki-setup` | `brain` | `init --hermes` |
| `vault-health` | `wiki-lint` | `brain` | `lint --fast` |
| `doc-generate-toc` | `doc-extract` | `brain` | `extract --toc` |
| `tag-taxonomy` | `wiki-tag-taxonomy` | `brain` | `weave --taxonomy` |
| `cross-linker` | `wiki-cross-linker` | `brain` | `weave --cross-link` |
| `test-driven-development` | `tdd-workflow` | `qa-toolkit` | `tdd` |

## Impacto nos Subagentes

| Subagente | Antes (skills) | Depois (toolkits) | Redução |
|---|---|---|---|
| **agent-dev** | 15 referências soft | 2 toolkits (`dev-toolkit`, `github`) | 87% |
| **agent-qa** | 8 referências soft | 1 toolkit (`qa-toolkit`) | 88% |
| **agent-orchestrator** | 2 skills kanban | 1 toolkit (`devops`) | 50% |
| **onboard** | 4 skills SDD | 1 toolkit (`sdd`) | 75% |
| **Principal (humano)** | 107 skills | 10 toolkits | 91% |

## Decisões Resolvidas

1. **`visual` split:** ✅ Aprovado. `visual` (13 design) + `media` (7 áudio/vídeo) = 11 toolkits.
2. **`brain` unificado:** ✅ Mantido unificado. Modos menos usados comprimidos. Se estourar 15KB na implementação, split no ajuste.
3. **`defuddle` → research:** ✅ Classificado como ferramenta de pesquisa (extração web), não formato Obsidian.
