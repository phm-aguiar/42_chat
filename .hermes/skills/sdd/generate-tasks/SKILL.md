---
name: sdd-generate-tasks
description: >
  Use ONLY when the user asks to generate or create a tasks.md for an SDD feature from
  existing spec.md and plan.md. Produces a DAG (Directed Acyclic Graph) of atomic tasks
  with metadata: Papel (Dev/QA/Test), Dependências, Paralelizável, Arquivos. Includes
  approval gate (Aprovado: true), phase-by-phase user interaction, and DAG validation
  (cycle detection, broken deps, orphan tasks). Trigger keywords: gerar tasks, criar
  tasks.md, generate tasks, criar tarefas.
version: 2.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Tasks, DAG, Execution, Planning]
    related_skills: [sdd-generate-plan, sdd-refactor-artifact, agent-run]
    category: sdd
    resources:
      - SKILL.md
      - references/task-rules.md
---

# Gerar Matriz de Execução com DAG (tasks.md)

## Propósito

Gera `tasks.md` com tarefas atômicas em formato DAG (Directed Acyclic Graph), permitindo
execução paralela segura pelo `agent-orchestrator` (feature 005).

## Pré-requisitos

- Feature deve ter `spec.md` e `plan.md` preenchidos.
- `spec.md` deve ter `Aprovado: true` nos metadados.

## Fluxo de Execução

### Passo 0: Approval Gate (HARD-GATE)

Antes de qualquer interação, verifique o campo `Aprovado` no spec.md:

1. Leia `specs/features/<id>-<slug>/spec.md`
2. Procure por `**Aprovado:** true` ou `**Aprovado:** false`
3. Se `Aprovado: false` → reporte: "Spec não aprovada. Altere `Aprovado: true` no spec.md e re-invoque." **ABORTE.**
4. Se `Aprovado: true` → prossiga para o Passo 1.

### Passo 1: Identificar a feature

Usuário informa o diretório (ex: `specs/features/004-sdd-tasks-dag`). Se não, pergunte.

### Passo 2: Ler spec.md e plan.md

Extraia: funcionalidade, cenários BDD, restrições (do spec) + stack, contratos,
ADRs, componentes, auditoria de constituição (do plan).

### Passo 3: Carregar regras de geração

```
skill_view(name="sdd-generate-tasks", file_path="references/task-rules.md")
```

Este arquivo contém: regras de atomicidade, formato DAG, detecção de paralelismo,
mapeamento spec→tasks, fases canônicas e exemplos de derivação. Siga-o estritamente.

### Passo 4: Derivar tarefas atômicas com metadados DAG

Para cada elemento extraído no Passo 2, crie UMA tarefa. Cada task deve ter:

```markdown
- [ ] **Tnnn:** Descrição da tarefa
  - **Papel:** Dev | QA | Test
  - **Dependências:** Txxx, Tyyy | Nenhuma
  - **Paralelizável:** true | false
  - **Arquivos:** `path/to/file.go`
```

**Regras de preenchimento:**

- **Papel:** derive da natureza da task. Código = Dev. Testes/cenários = QA. Testes unitários = Test.
- **Dependências:** liste TODOS os IDs de tasks que devem estar concluídas antes desta.
- **Paralelizável:** `true` se e somente se NÃO compartilha arquivos com outra task `Paralelizável: true` da mesma fase E não tem dependência não satisfeita na mesma fase.
- **Arquivos:** lista exaustiva de paths que a task vai criar ou modificar. Essencial para detecção de conflitos.

**Detecção de conflito de arquivos (regra primária de paralelismo):**

Duas tasks da mesma fase são paralelizáveis se e somente se:
1. Nenhuma depende da outra
2. Seus conjuntos de `Arquivos` são disjuntos (interseção vazia)

Se duas tasks compartilham arquivos:
- Force dependência sequencial (ex: T004 depende de T003)
- Alerte: "T003 e T004 compartilham handler/message.go — forçado sequencial"

**Exceção inteligente:** QA gerando `.feature` vs Dev gerando `.go` no mesmo diretório — extensões diferentes = sem conflito real.

### Passo 5: Interação fase por fase via clarify()

**NÃO gere todas as fases de uma vez.** Interaja uma fase por vez:

1. Proponha a Fase 1 com tasks, papéis, dependências e flags de paralelismo
2. Chame `clarify()` com as tasks da fase. Opções: "Aprovar", "Ajustar tasks", "Adicionar task", "Remover task"
3. Incorpore feedback do usuário
4. Avance para a próxima fase (repita 1-3)
5. Ao final de todas as fases, monte o DAG completo

**Sumário por fase (formato para clarify):**

```
Fase 1: Fundação (3 tasks, 2 paralelizáveis)

T001: Criar modelo Message
  Papel: Dev | Deps: Nenhuma | Paralelo: true
  Arquivos: internal/model/message.go

T002: Criar schema do banco
  Papel: Dev | Deps: T001 | Paralelo: false
  Arquivos: internal/db/migrations/001.sql

T003: Criar cenários Gherkin
  Papel: QA | Deps: Nenhuma | Paralelo: true
  Arquivos: specs/features/004-*/acceptance/chat.feature

[Aprovar] [Ajustar] [Adicionar] [Remover]
```

### Passo 6: Validar DAG completo

Antes de salvar, valide o DAG inteiro:

1. **Detecção de ciclos:** percorra o grafo de dependências com DFS. Se encontrar back-edge → ciclo.
   - Reporte: "Ciclo detectado: T002 → T003 → T002. Corrija as dependências."
   - Mostre o ciclo exato e permita edição da fase problemática.

2. **Dependências quebradas:** toda referência em `Dependências:` deve corresponder a um ID existente.
   - Reporte: "T005 depende de T099 que não existe."

3. **Tasks órfãs:** task em fase tardia sem dependências e sem tasks dependentes dela.
   - Pergunte: "T007 é órfã — é intencional ou erro?"

4. **Isolamento de arquivos:** tasks `Paralelizável: true` na mesma fase com Arquivos disjuntos.
   - Se violado, force sequencial ou alerte.

Se validação falhar, retorne à fase problemática para correção.

### Passo 7: Salvar

Escreva `tasks.md` no diretório da feature com o formato DAG completo.

**Se tasks.md já existe:** pergunte "tasks.md já existe. Sobrescrever, mesclar, ou abortar?"

## Edge Cases

### Spec sem cenários BDD
Se o spec.md não tem seção de cenários BDD: "Spec não tem cenários BDD — tasks de QA serão placeholders."

### Fase vazia
Se usuário remove todas as tasks de uma fase: pergunte se quer remover a fase ou mantê-la como placeholder.

### Tasks.md flat legado
Se encontrar tasks.md antigo (formato flat, sem metadados DAG): trate como sequencial. Não tente converter — a feature pode ser experimental (001-003).

### Arquivo listado mas task é QA
QA gerando `.feature` e Dev gerando `.go` no mesmo diretório: sem conflito real (extensões diferentes). Não force sequencial.

## Guardrails

- **Nunca agrupe ações:** "Criar X e testar Y" → 2 tarefas.
- **Tarefas já feitas:** verifique sistema de arquivos. Se código existe, `[x]`.
- **Dependências explícitas:** sempre declare no campo `Dependências:`.
- **Idempotência:** se `tasks.md` existe, pergunte se sobrescreve ou mescla.
- **Tamanho mínimo:** ao menos 4 tarefas (1 por fase).
- **Isolamento de arquivos:** HARD RULE — tasks paralelas NUNCA compartilham paths.
- **Interação fase por fase:** NUNCA gere todas as fases de uma vez. Use `clarify()`.

## Verificação

- [ ] Approval gate verificado (`Aprovado: true`)
- [ ] `tasks.md` escrito em `specs/features/<id>-<slug>/`
- [ ] Cada task no formato DAG com Papel, Dependências, Paralelizável, Arquivos
- [ ] Tarefas agrupadas em fases canônicas
- [ ] DAG validado: sem ciclos, sem dependências quebradas, sem órfãs não intencionais
- [ ] Tasks paralelas têm conjuntos de Arquivos disjuntos
- [ ] Interação fase por fase concluída (clarify por fase)
- [ ] Usuário aprovou antes de salvar
