# tasks.md: Lista de Execução — Templates Canônicos SDD

## Fase 1: Definição dos Templates (Paralelizável)

- [x] **T001:** Definir template canônico de `spec.md` (4 seções: Visão Geral, BDD, Restrições, Checklist).
- [x] **T002:** Definir template canônico de `plan.md` (4 seções: Metadados, Contratos, Decisões, Auditoria).
- [x] **T003:** Definir template canônico de `tasks.md` (fases com T001-TNNN, dependências explícitas).
- [x] **T004:** Definir template da seção SDD Workflow no `AGENTS.md`.
- [x] **T005:** Definir template de `llms.txt` (navegação, camadas, links).

## Fase 2: Implementação do Refatorador (Paralelizável com Fase 3)

- [x] **T006:** Criar arquivo `canonical-templates.md` como referência para o `sdd-refactor-artifact`.
- [x] **T007:** Implementar mapeamento semântico no refatorador (extrair conteúdo → seções canônicas).
- [ ] **T008:** Adicionar suporte a geração de `plan.md` e `tasks.md` a partir de `spec.md` existente. (Depende de T001, T002, T003)

## Fase 3: Validação e CI (Paralelizável)

- [ ] **T009:** Adicionar ao `sdd-validate` verificações de conformidade dos templates (seções obrigatórias presentes, placeholders identificados).
- [ ] **T010:** Criar testes de snapshot para o refatorador: arquivos de entrada → saída esperada.

## Fase 4: Documentação

- [ ] **T011:** Adicionar exemplos de antes/depois da refatoração na spec.
