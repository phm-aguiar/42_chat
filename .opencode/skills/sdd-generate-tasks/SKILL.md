---
name: sdd-generate-tasks
description: Use ONLY when the user asks to generate or create a tasks.md for an SDD feature from existing spec.md and plan.md. Produces atomic, parallelizable tasks grouped in logical phases (Fundação, Implementação, Validação, Documentação) with Tnnn numbering and explicit dependencies. Trigger keywords: "gerar tasks", "criar tasks.md", "generate tasks", "criar tarefas", "generate task list", "atomic tasks".
---

# Gerar Matriz de Execução (tasks.md)

## Propósito

Gera um `tasks.md` canônico com tarefas atômicas e paralelizáveis, derivadas do `spec.md` e `plan.md` da feature.

## Pré-requisitos

- A feature deve ter `spec.md` e `plan.md` preenchidos.

## Regras de Atomicidade (OBRIGATÓRIO)

Toda tarefa gerada DEVE seguir estas regras:

1. **Uma ação por tarefa**: cada `Tnnn` faz exatamente uma coisa. "Criar X e testar Y" são duas tarefas.
2. **Paralelizável por fase**: tarefas na mesma fase NÃO dependem entre si. Se B depende de A, B vai na fase seguinte ou declara `(Depende de Tnnn)`.
3. **Formato fixo**: `- [ ] **Tnnn:** descrição (Depende de Tnnn)`.
4. **Numeração sequencial global**: `T001`, `T002`... não reinicia por fase.
5. **Checkbox**: `[ ]` para pendente, `[x]` para já concluído.

## Mapeamento spec/plan → tarefas

| Fonte no spec/plan | Gera tarefa do tipo |
|---|---|
| Restrições de segurança/performance | "Adicionar validação/mitigação para restrição X" |
| Cenários BDD | "Implementar cenário: Dado X, Quando Y, Então Z" |
| Contratos (OpenAPI/AsyncAPI) | "Criar/atualizar arquivo de contrato Y" |
| Decisões arquiteturais (ADR) | "Configurar/implementar ADR-NNN: descrição" |
| Componentes mapeados no plan | "Criar diretório/arquivo para componente Y" |
| Portões do constitution.md | "Adicionar teste unitário para Z" |
| Ferramentas de build/CI | "Configurar pipeline/linter Y" |

## Fases canônicas

Agrupe tarefas nestas 4 fases. Tarefas na mesma fase são paralelizáveis.

| Fase | Conteúdo típico |
|---|---|
| **Fase 1: Fundação** | Contratos, schemas, configs, estrutura de diretórios |
| **Fase 2: Implementação** | Lógica de negócio, adapters, handlers, integração |
| **Fase 3: Validação** | Testes, CI, linting, verificação de conformidade |
| **Fase 4: Documentação** | README, llms.txt, docs, comentários |

## Fluxo de Execução

### Passo 1: Identificar a feature

O usuário deve informar o diretório (ex: `specs/features/003-forge-skill`). Se não, pergunte.

### Passo 2: Ler spec.md e plan.md

Leia ambos. Extraia:
- Do `spec.md`: funcionalidade, cenários BDD, restrições, checklist de ambiguidade.
- Do `plan.md`: stack, contratos, decisões (ADRs), componentes mapeados, auditoria de constituição.

### Passo 3: Derivar tarefas atômicas

Para cada elemento extraído, crie UMA tarefa atômica:

```
Fonte: spec.md seção 2 — Cenário "Dado X, Quando Y, Então Z"
→ Tarefa: "Implementar cenário: Dado X, Quando Y, Então Z"

Fonte: plan.md ADR-001 — "Usar Gorilla WebSocket para comunicação"
→ Tarefa: "Configurar Gorilla WebSocket conforme ADR-001"

Fonte: constitution.md — "Toda função pública deve ter teste"
→ Tarefa: "Adicionar teste unitário para função pública Z"
```

### Passo 4: Agrupar em fases com dependências

1. Atribua cada tarefa a uma fase.
2. Verifique dependências: se T005 precisa de T002, mova T005 para a fase seguinte OU adicione `(Depende de T002)`.
3. Marque tarefas já concluídas com `[x]` (verifique se arquivos/diretórios já existem).
4. Numere sequencialmente (T001, T002...).

### Passo 5: Apresentar matriz e confirmar

Mostre um sumário:

```
tasks.md: 12 tarefas em 4 fases

Fase 1: Fundação (5 tarefas, todas paralelizáveis)
  T001 Criar estrutura X
  T002 Configurar Y
  ...

Fase 2: Implementação (4 tarefas, 3 paralelizáveis)
  T006 Implementar core Z (Depende de T002)
  ...

Fase 3: Validação (2 tarefas, paralelizáveis)
Fase 4: Documentação (1 tarefa)
```

**Pergunte ao usuário se pode salvar.**

### Passo 6: Salvar

Escreva `tasks.md` no diretório da feature.

## Guardrails

- **Nunca agrupe ações**: "Criar X e testar Y" → 2 tarefas separadas.
- **Tarefas já feitas**: verifique o sistema de arquivos. Se o código já existe, marque `[x]`.
- **Dependências explícitas**: sempre declare `(Depende de Tnnn)` quando uma tarefa depende de outra em fase anterior.
- **Idempotência**: se `tasks.md` já existe, pergunte se deve sobrescrever ou mesclar.
- **Tamanho mínimo**: cada feature deve ter ao menos 4 tarefas (1 por fase).
