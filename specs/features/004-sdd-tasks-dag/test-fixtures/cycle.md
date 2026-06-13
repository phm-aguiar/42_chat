# tasks.md: Teste — Ciclo Artificial

## Fase 1: Fundação
- [ ] **T001:** Task raiz
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `a.go`

- [ ] **T002:** Depende de T003 (cria ciclo T002→T003→T002)
  - **Papel:** Dev
  - **Dependências:** T003
  - **Paralelizável:** false
  - **Arquivos:** `b.go`

## Fase 2: Implementação
- [ ] **T003:** Depende de T002 (fecha o ciclo)
  - **Papel:** Dev
  - **Dependências:** T002
  - **Paralelizável:** false
  - **Arquivos:** `c.go`