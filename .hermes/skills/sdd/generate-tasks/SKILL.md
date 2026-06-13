---
name: sdd-generate-tasks
description: >
  Use ONLY when the user asks to generate or create a tasks.md for an SDD feature from existing
  spec.md and plan.md. Produces atomic, parallelizable tasks grouped in logical phases (Fundação,
  Implementação, Validação, Documentação) with Tnnn numbering and explicit dependencies. Trigger
  keywords: gerar tasks, criar tasks.md, generate tasks, criar tarefas, generate task list,
  atomic tasks.
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Tasks, Execution, Planning]
    related_skills: [sdd-generate-plan, sdd-refactor-artifact, agent-run]
    category: sdd
    resources:
      - SKILL.md
      - references/task-rules.md
---

# Gerar Matriz de Execução (tasks.md)

## Propósito

Gera `tasks.md` com tarefas atômicas e paralelizáveis, derivadas do `spec.md` e `plan.md`.

## Pré-requisitos

- Feature deve ter `spec.md` e `plan.md` preenchidos.

## Fluxo de Execução

### Passo 1: Identificar a feature

Usuário deve informar o diretório (ex: `specs/features/003-forge-skill`). Se não, pergunte.

### Passo 2: Ler spec.md e plan.md

Extraia: funcionalidade, cenários BDD, restrições (do spec) + stack, contratos,
ADRs, componentes, auditoria de constituição (do plan).

### Passo 3: Carregar regras de geração

```
skill_view(name="sdd-generate-tasks", file_path="references/task-rules.md")
```

Este arquivo contém: regras de atomicidade, mapeamento spec→tasks, fases canônicas
e exemplos de derivação. Siga-o estritamente.

### Passo 4: Derivar tarefas atômicas

Para cada elemento extraído no Passo 2, crie UMA tarefa seguindo o mapeamento do
`task-rules.md`. Formato: `- [ ] **Tnnn:** descrição (Depende de Tnnn)`.

### Passo 5: Agrupar em fases com dependências

1. Atribua cada tarefa a uma das 4 fases canônicas.
2. Verifique dependências: se T005 precisa de T002, mova para fase seguinte ou
   declare `(Depende de T002)`.
3. Marque tarefas já concluídas com `[x]` (verifique sistema de arquivos).
4. Numere sequencialmente (T001, T002...).

### Passo 6: Apresentar sumário e confirmar

Mostre sumário (formato no `task-rules.md`). **Pergunte ao usuário se pode salvar.**

### Passo 7: Salvar

Escreva `tasks.md` no diretório da feature.

## Guardrails

- **Nunca agrupe ações:** "Criar X e testar Y" → 2 tarefas.
- **Tarefas já feitas:** verifique sistema de arquivos. Se código existe, `[x]`.
- **Dependências explícitas:** sempre declare `(Depende de Tnnn)`.
- **Idempotência:** se `tasks.md` existe, pergunte se sobrescreve ou mescla.
- **Tamanho mínimo:** ao menos 4 tarefas (1 por fase).

## Verificação

- [ ] `tasks.md` escrito em `specs/features/<id>-<slug>/`
- [ ] Cada tarefa no formato `- [ ] **Tnnn:** ...`
- [ ] Tarefas agrupadas em 4 fases canônicas
- [ ] Dependências entre fases declaradas como `(Depende de Tnnn)`
- [ ] Mínimo 4 tarefas (1 por fase)
- [ ] Usuário aprovou antes de salvar
