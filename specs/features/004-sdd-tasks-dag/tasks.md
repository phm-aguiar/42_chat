# tasks.md: Upgrade sdd-generate-tasks → Formato DAG

## Fase 1: Infraestrutura da Skill

- [x] **T001:** Atualizar SKILL.md do `sdd-generate-tasks` com a seção de Approval Gate (verificar `Aprovado: true` antes de gerar)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/SKILL.md`

- [x] **T002:** Adicionar seção de formato DAG ao SKILL.md (template markdown, campos obrigatórios por task)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/SKILL.md`

- [x] **T003:** Atualizar `references/task-rules.md` com regras de paralelismo (disjunção de Arquivos) e detecção de conflitos
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/references/task-rules.md`

## Fase 2: Lógica de DAG (sequencial — todas tocam SKILL.md)

- [x] **T004:** Adicionar algoritmo de validação de DAG ao SKILL.md: detecção de ciclos (DFS), dependências quebradas, tasks órfãs
  - **Papel:** Dev
  - **Dependências:** T001, T002
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/SKILL.md`

- [x] **T005:** Adicionar lógica de interação fase por fase via `clarify()` ao SKILL.md
  - **Papel:** Dev
  - **Dependências:** T001, T002
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/SKILL.md`

- [x] **T006:** Adicionar tratamento de edge cases ao SKILL.md: tasks.md já existe, fase vazia, spec sem cenários BDD, arquivo listado mas task é QA
  - **Papel:** Dev
  - **Dependências:** T004, T005
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/skills/sdd/generate-tasks/SKILL.md`

## Fase 3: Validação

- [x] **T007:** Testar geração de DAG com spec real (feature 005 como cobaia): verificar ausência de ciclos, paralelismo correto, isolamento de arquivos
  - **Papel:** QA
  - **Dependências:** T001, T002, T003, T004, T005, T006
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/005-runtime-orchestrator/tasks.md`

- [x] **T008:** Testar cenários de erro: spec com `Aprovado: false` (gate bloqueado), tasks.md com ciclo artificial, tasks.md com dependência quebrada
  - **Papel:** QA
  - **Dependências:** T007
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/004-sdd-tasks-dag/test-fixtures/`

- [x] **T009:** Validar retrocompatibilidade: tasks.md antigo (formato flat da feature 003) não quebra — é lido como sequencial
  - **Papel:** QA
  - **Dependências:** T007
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/003-forge-skill/tasks.md`

## Fase 4: Documentação

- [x] **T010:** Atualizar AGENTS.md: referência ao novo formato DAG no fluxo SDD
  - **Papel:** Dev
  - **Dependências:** T007
  - **Paralelizável:** true
  - **Arquivos:** `AGENTS.md`
