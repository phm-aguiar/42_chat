# tasks.md: Reavaliação e Consolidação de Skills

> 21 tasks em 4 fases. 11 toolkits. DAG validado: 0 ciclos, 0 órfãos, 0 conflitos de arquivo.

## Fase 1: Fundação — Auditoria e Design

- [x] **T001:** Auditar ~130 skills — matriz de classificação (domínio, uso por subagente, redundância, granularidade)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/008-reavaliacao-skills/audit/skill-matrix.md`

- [x] **T002:** Auditar uso real das skills pelos subagentes — quais skills cada `AGENTS.md` e `context.yaml` referencia
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/008-reavaliacao-skills/audit/agent-usage.md`

- [x] **T003:** Projetar mapa final de toolkits — quais skills absorvem quais, nomes finais, modos internos, arquivos afetados
  - **Papel:** Dev
  - **Dependências:** T001, T002
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/008-reavaliacao-skills/audit/toolkit-map.md`

## Fase 2: Implementação — Consolidar Toolkits

Todas as tasks desta fase são paralelizáveis (diretórios disjuntos). Dependem de T003.

- [ ] **T004:** Consolidar `brain` toolkit — 30 skills wiki/obsidian/docs → 1 toolkit com modos (ingest, query, lint, weave, report, init, extract)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/wiki/brain/SKILL.md`

- [ ] **T005:** Consolidar `qa-toolkit` — 8 skills QA/testes → 1 toolkit com modos (bdd-spec, gherkin, cucumber, unit-tests, test-runner, e2e, tdd, dogfood)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/qa/qa-toolkit/SKILL.md`

- [ ] **T006:** Consolidar `dev-toolkit` — 15 skills dev/build/runtime/autonomous → 1 toolkit com modos (go, react, build-check, plan, spike, debug, code-review, simplify, node-debug, python-debug, claude-code, codex, opencode, hermes-config, skill-forge)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/dev/dev-toolkit/SKILL.md`

- [ ] **T007:** Consolidar `sdd` toolkit — 9 skills pipeline SDD → 1 toolkit com modos (brainstorm, explore-tech, init-repo, plan, tasks, validate, refactor, wiki-enforce)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/sdd/sdd/SKILL.md`

- [ ] **T008:** Consolidar `github` toolkit — 7 skills GitHub → 1 toolkit com modos (auth, pr, review, issues, repo, commit, inspect)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/github/github/SKILL.md`

- [ ] **T009:** Consolidar `devops` toolkit — 6 skills DevOps/infra → 1 toolkit com modos (docker-dev, honcho, honcho-save, kanban-orch, kanban-work, linux-audio)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/devops/devops/SKILL.md`

- [ ] **T010:** Consolidar `visual` toolkit — 13 skills design/diagramas → 1 toolkit com modos (mermaid, arch-diagram, excalidraw, design, sketch, p5js, manim, ascii, infographic, web-designs, pretext, touchdesigner, humanize)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/creative/visual/SKILL.md`

- [ ] **T011:** Consolidar `ml` toolkit — 8 skills MLOps → 1 toolkit com modos (hf-hub, llama-cpp, vllm, eval, wandb, audiocraft, sam, jupyter)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/mlops/ml/SKILL.md`

- [ ] **T012:** Consolidar `research` toolkit — 6 skills pesquisa → 1 toolkit com modos (arxiv, blogwatch, polymarket, paper-write, defuddle, youtube)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/research/research/SKILL.md`

- [ ] **T013:** Consolidar `productivity` toolkit — 15 skills produtividade/integrações → 1 toolkit com modos (airtable, gworkspace, notion, pptx, pdf-edit, ocr, maps, teams, email, x, hue, gif, yuanbao)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/productivity/productivity/SKILL.md`

- [ ] **T014:** Consolidar `media` toolkit — 7 skills áudio/vídeo/música → 1 toolkit com modos (ascii-video, songwrite, heartmula, songsee, comfyui, gif, design-md)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/creative/media/SKILL.md`

## Fase 3: Integração — Agentes + Wiki + Symlinks

- [ ] **T015:** Atualizar `agent-dev` — AGENTS.md + context.yaml referenciando `dev-toolkit` (substitui 15 skills individuais)
  - **Papel:** Dev
  - **Dependências:** T006
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-dev/AGENTS.md`, `.hermes/agents/agent-dev/context.yaml`

- [ ] **T016:** Atualizar `agent-qa` — AGENTS.md + context.yaml referenciando `qa-toolkit` (substitui 8 skills individuais)
  - **Papel:** Dev
  - **Dependências:** T005
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-qa/AGENTS.md`, `.hermes/agents/agent-qa/context.yaml`

- [ ] **T017:** Atualizar `wiki/` — index.md + skills/* refletindo nova arquitetura (11 toolkits), páginas de skills antigas marcadas com `superseded_by`, novas páginas para cada toolkit
  - **Papel:** Dev
  - **Dependências:** T004
  - **Paralelizável:** true
  - **Arquivos:** `wiki/index.md`, `wiki/skills/*.md`

- [ ] **T018:** Limpar symlinks antigos e verificar novos — `~/.hermes/skills/` deve apontar para os 11 toolkits, skills absorvidas removidas com `absorbed_into`
  - **Papel:** Dev
  - **Dependências:** T004, T005, T006, T007, T008, T009, T010, T011, T012, T013, T014
  - **Paralelizável:** false
  - **Arquivos:** `~/.hermes/skills/`

## Fase 4: Validação

- [ ] **T019:** Smoke test — `skill_view(name=...)` em cada um dos 11 toolkits → carrega sem erro, modos documentados no SKILL.md acessíveis
  - **Papel:** QA
  - **Dependências:** T018
  - **Paralelizável:** true
  - **Arquivos:** Nenhum (verificação em runtime)

- [ ] **T020:** `wiki-lint` — 0 broken links, 0 órfãos, index.md consistente com estrutura real
  - **Papel:** QA
  - **Dependências:** T017
  - **Paralelizável:** true
  - **Arquivos:** Nenhum (verificação em runtime)

- [ ] **T021:** `sdd-validate` — estrutura SDD íntegra, spec/plan/tasks presentes e válidos
  - **Papel:** QA
  - **Dependências:** T018
  - **Paralelizável:** true
  - **Arquivos:** Nenhum (verificação em runtime)

---

**Resumo:** 21 tasks | 4 fases | 11 Dev + 3 QA | 15 paralelizáveis | 0 conflitos de arquivo

**Métrica alvo:** 119 skills → 11 toolkits. Subagentes carregam ≤2 toolkits cada.
