# tasks.md: Teste — Dependência Quebrada

## Fase 1: Fundação
- [ ] **T001:** Task válida
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `a.go`

- [ ] **T002:** Depende de T099 (não existe)
  - **Papel:** QA
  - **Dependências:** T099
  - **Paralelizável:** false
  - **Arquivos:** `test/a_test.go`