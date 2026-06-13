# tasks.md: Teste — Hard Fail e Escalação

## Fase 1: Fundação
- [ ] **T001:** Task que falha 3x consecutivas
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `should_fail.go`

- [ ] **T002:** Task dependente de T001 (deve ser pausada na escalação)
  - **Papel:** QA
  - **Dependências:** T001
  - **Paralelizável:** false
  - **Arquivos:** `test-output/dependent.txt`

- [ ] **T003:** Task independente (deve continuar rodando)
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `test-output/independent.txt`