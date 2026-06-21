# tasks.md: Teste — Spec Não Aprovada

> Este arquivo simula um tasks.md para uma feature cujo spec.md tem `Aprovado: false`.
> O agent-orchestrator deve detectar e abortar ANTES de spawnar qualquer subagente.

## Fase 1: Fundação
- [ ] **T001:** Task que nunca deveria rodar
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `should_not_exist.go`