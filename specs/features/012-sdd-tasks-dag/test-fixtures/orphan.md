# tasks.md: Teste — Tasks Órfãs

## Fase 1: Fundação
- [ ] **T001:** Task raiz
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `a.go`

## Fase 2: Implementação
- [ ] **T002:** Task conectada
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** false
  - **Arquivos:** `b.go`

## Fase 3: Validação
- [ ] **T003:** Task órfã (sem deps, ninguém depende dela, fase tardia)
  - **Papel:** QA
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `test/orphan_test.go`