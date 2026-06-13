# Regras de Geração de Tarefas (tasks.md)

Referência para `sdd-generate-tasks`. Contém regras de atomicidade, mapeamento spec→tasks e fases canônicas.

## Regras de Atomicidade (OBRIGATÓRIO)

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

## Exemplo de derivação

```
Fonte: spec.md seção 2 — Cenário "Dado X, Quando Y, Então Z"
→ Tarefa: "Implementar cenário: Dado X, Quando Y, Então Z"

Fonte: plan.md ADR-001 — "Usar Gorilla WebSocket para comunicação"
→ Tarefa: "Configurar Gorilla WebSocket conforme ADR-001"

Fonte: constitution.md — "Toda função pública deve ter teste"
→ Tarefa: "Adicionar teste unitário para função pública Z"
```

## Exemplo de sumário

Ao apresentar a matriz ao usuário, use este formato:

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
