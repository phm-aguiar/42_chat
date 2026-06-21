# tasks.md: Lista de Execução — Estrutura SDD do Repositório

## Fase 1: Fundação (Paralelizável)

- [x] **T001:** Criar `.github/memory/` com `constitution.md` (template vazio) e `tech.md` (placeholder). *Skill: sdd-init-repo*
- [x] **T002:** Criar árvore `specs/domain-events/`, `specs/features/`, `specs/infra/`. *Skill: sdd-init-repo*
- [x] **T003:** Atualizar `AGENTS.md` com seção SDD Workflow (comportamento, regras, skills disponíveis). *Skill: sdd-init-repo*

## Fase 2: Validação (Paralelizável)

- [x] **T004:** Criar script de validação `check-sdd.sh` que audita estrutura: `.github/memory/`, `specs/`, features. *Skill: sdd-validate*
- [x] **T005:** Integrar validação no CI (GitHub Actions) — falhar PR se estrutura SDD inválida. (Depende de T004)

## Fase 3: Documentação e Tooling (Paralelizável)

- [ ] **T006:** Criar `llms.txt` na raiz com navegação do repositório para LLMs.
- [ ] **T007:** Documentar o fluxo SDD completo no README.md (workflow: spec → plan → tasks → code).
- [x] **T008:** Criar template de `constitution.md` com portões de qualidade, restrições e anti-padrões.
