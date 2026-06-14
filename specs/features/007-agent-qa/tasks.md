# tasks.md: Agent QA (guardião da qualidade)

## Fase 1: Criação

- [ ] **T001:** Criar AGENT.md com persona, ciclo de validação (lê spec → Gherkin → testes → lint → cobertura → reporta) e contrato de saída (DONE/REJECTED/BLOCKED)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-qa/AGENT.md`

- [ ] **T002:** Criar context.yaml com toolsets (`terminal`, `file`), timeout e configuração do agente
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `.hermes/agents/agent-qa/context.yaml`

## Fase 2: Validação

- [ ] **T003:** Smoke-test DONE: spawnar agent-qa com task simulada (código correto) e verificar resposta DONE com evidência de testes passando
  - **Papel:** QA
  - **Dependências:** T001, T002
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/007-agent-qa/test-fixtures/smoke-task.md`

- [ ] **T004:** Contrato REJECTED: fornecer código com bug ao agent-qa e verificar que reporta REJECTED com evidência (teste quebrado, arquivo, linha)
  - **Papel:** QA
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/007-agent-qa/test-fixtures/rejected-task.md`

- [ ] **T005:** Contrato BLOCKED: fornecer spec ambígua ao agent-qa e verificar que reporta BLOCKED com pergunta específica (nunca infere)
  - **Papel:** QA
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/007-agent-qa/test-fixtures/ambiguous-spec.md`

## Fase 3: Documentação

- [ ] **T006:** Atualizar BACKLOG.md: marcar feature 007 como implementada, linkar spec/plan/tasks
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `specs/BACKLOG.md`

- [ ] **T007:** Atualizar AGENTS.md: adicionar agent-qa na lista de agentes com descrição e status
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `AGENTS.md`
