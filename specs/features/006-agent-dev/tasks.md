# tasks.md: Agent Dev (persona implementadora)

## Fase 1: Criação

- [x] **T001:** Criar AGENT.md com persona, tom, ciclo de trabalho (lê contexto → planeja → implementa → smoke-test → reporta) e contrato de saída (DONE/FAIL/BLOCKED)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-dev/AGENT.md`

- [x] **T002:** Criar context.yaml com toolsets (`terminal`, `file`), timeout e configuração do agente
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-dev/context.yaml`

## Fase 2: Validação

- [x] **T003:** Smoke-test: spawnar agent-dev com task simulada (happy path) e verificar resposta DONE com evidência rastreável
  - **Papel:** QA
  - **Dependências:** T001, T002
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/006-agent-dev/test-fixtures/smoke-task.md`

- [x] **T004:** Validar contrato BLOCKED: fornecer spec ambígua ao agent-dev e verificar que reporta BLOCKED com pergunta específica (nunca infere)
  - **Papel:** QA
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/006-agent-dev/test-fixtures/ambiguous-spec.md`

## Fase 3: Documentação

- [x] **T005:** Atualizar BACKLOG.md: marcar feature 006 como implementada, linkar spec/plan/tasks
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/BACKLOG.md`

- [x] **T006:** Atualizar AGENTS.md: adicionar agent-dev na lista de agentes com descrição e status
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `AGENTS.md`
