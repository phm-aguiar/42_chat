# tasks.md: Agent Orchestrator — Execução Runtime SDD

## Fase 1: Estrutura do Agente

- [x] **T001:** Criar `.hermes/agents/agent-orchestrator/AGENT.md` com persona, fluxo de trabalho e regras de ouro
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T002:** Criar `.hermes/agents/agent-orchestrator/context.yaml` com receita de contexto (files, session, feature_artifacts, toolsets)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-orchestrator/context.yaml`

- [x] **T003:** Criar `.hermes/agents/agent-orchestrator/references/subagent-prompts.md` com templates de prompt por papel (Dev, QA)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-orchestrator/references/subagent-prompts.md`

## Fase 2: Lógica de Orquestração (sequencial — toca AGENT.md)

- [x] **T004:** Implementar approval gate no AGENT.md: verificar `Aprovado: true` no spec.md antes de qualquer spawn; abortar se false
  - **Papel:** Dev
  - **Dependências:** T001, T002
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T005:** Implementar parser de DAG no AGENT.md: ler tasks.md, extrair fases, dependências, flags de paralelismo, listas de Arquivos
  - **Papel:** Dev
  - **Dependências:** T004
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T006:** Implementar janela deslizante de spawn no AGENT.md: identificar tasks sem dependências (raízes), spawnar até 3 em paralelo via delegate_task, liberar próxima quando uma concluir
  - **Papel:** Dev
  - **Dependências:** T005
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T007:** Implementar política de retry no AGENT.md: 3 tentativas com contexto enriquecido (erro da tentativa anterior), timeout de 30min por task
  - **Papel:** Dev
  - **Dependências:** T006
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T008:** Implementar validação de evidência no AGENT.md: verificar arquivos criados, smoke-test output, exit code antes de marcar `[x]`
  - **Papel:** Dev
  - **Dependências:** T006
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T009:** Implementar escalação de bloqueios no AGENT.md: após 3 falhas, pausar sub-árvore dependente, reportar ao usuário com contexto, aguardar input
  - **Papel:** Dev
  - **Dependências:** T007, T008
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

- [x] **T010:** Adicionar tratamento de edge cases ao AGENT.md: spawn failure (aborta feature), timeout, DONE sem evidência, tasks.md mal formado, abort manual do usuário
  - **Papel:** Dev
  - **Dependências:** T009
  - **Paralelizável:** false
  - **Arquivos:** `.hermes/agents/agent-orchestrator/AGENT.md`

## Fase 3: Validação

- [x] **T011:** Testar happy path: usar tasks.md da feature 004 como cobaia, verificar execução completa com `[x]` em todas as tasks
  - **Papel:** QA
  - **Dependências:** T001, T002, T003, T004, T005, T006, T007, T008, T009, T010
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/004-sdd-tasks-dag/tasks.md`

- [x] **T012:** Testar approval gate: invocar orchestrator com `Aprovado: false` → deve abortar
  - **Papel:** QA
  - **Dependências:** T011
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/005-runtime-orchestrator/test-fixtures/spec-not-approved.md`

- [x] **T013:** Testar retry com falha: criar task que falha 2x e passa na 3ª → verificar contexto enriquecido
  - **Papel:** QA
  - **Dependências:** T011
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/005-runtime-orchestrator/test-fixtures/failing-task/`

- [x] **T014:** Testar escalação: task falha 3x → orchestrator deve pausar sub-árvore e pedir input humano
  - **Papel:** QA
  - **Dependências:** T013
  - **Paralelizável:** false
  - **Arquivos:** `specs/features/005-runtime-orchestrator/test-fixtures/hard-fail-task/`

## Fase 4: Documentação

- [x] **T015:** Atualizar AGENTS.md: referência ao agent-orchestrator no fluxo SDD
  - **Papel:** Dev
  - **Dependências:** T011
  - **Paralelizável:** true
  - **Arquivos:** `AGENTS.md`

- [x] **T016:** Atualizar BACKLOG.md: marcar features 004 e 005 como concluídas
  - **Papel:** Dev
  - **Dependências:** T015
  - **Paralelizável:** false
  - **Arquivos:** `specs/BACKLOG.md`
