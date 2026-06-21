# tasks.md: Teste — Task com Falha e Retry

## Fase 1: Fundação
- [ ] **T001:** Task que falha nas 2 primeiras tentativas e passa na 3ª
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `test-output/result.txt`

- [ ] **T002:** Task dependente (só roda se T001 passar)
  - **Papel:** QA
  - **Dependências:** T001
  - **Paralelizável:** false
  - **Arquivos:** `test-output/qa-result.txt`