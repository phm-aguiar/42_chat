# tasks.md: Lista de Execução — Forjar Nova Skill

## Fase 1: Infraestrutura Base (Paralelizável)

- [x] **T001:** Criar script `scaffold-skill.sh` que gera árvore `.opencode/skills/<nome>/` com subpastas `assets/`, `scripts/`, `references/`.
- [x] **T002:** Criar template `template-skill.md` com placeholders `{{skill_name}}`, `{{skill_description}}`, `{{skill_title}}` e estrutura de seções (Propósito, Fluxo, Guardrails).
- [x] **T003:** Criar referência `skill-format.md` documentando o formato opencode de SKILL.md (frontmatter, descrição, caminhos).

## Fase 2: Skill Principal (Paralelizável com Fase 3)

- [x] **T004:** Escrever `SKILL.md` da `forge-new-skill` com fluxo de 4 passos (Preparar estrutura → Consultar formato → Preencher molde → Persistir). (Depende de T001, T002, T003)
- [x] **T005:** Escrever `spec.md` da feature `003-forge-skill` no formato canônico SDD.

## Fase 3: Integração e Validação (Paralelizável)

- [ ] **T006:** Adicionar ao `sdd-refactor-artifact` suporte para gerar `plan.md` e `tasks.md` atômicos a partir de `spec.md`.
- [ ] **T007:** Testar a skill criando uma skill dummy com `forge-new-skill` e validando estrutura com `sdd-validate`.
- [ ] **T008:** Adicionar a `forge-new-skill` a capacidade de sugerir o escopo (projeto vs global) com confirmação do usuário.

## Fase 4: Documentação

- [ ] **T009:** Adicionar `plan.md` e `tasks.md` para a própria feature `003-forge-skill`.
- [ ] **T010:** Criar `llms.txt` na raiz do projeto com navegação completa.
