---
name: sdd-generate_tasks
description: >
  Use ONLY when the user asks to generate or create a tasks.md for an SDD feature from
  existing spec.md and plan.md. Produces a DAG (Directed Acyclic Graph) of atomic tasks
  with metadata: Papel (Dev/QA), Dependências, Paralelizável, Arquivos. Includes
  approval gate (Aprovado: true), phase-by-phase user interaction, and DAG validation
  (cycle detection, broken deps, orphan tasks). Supports --with-memory flag for
  experiential memory retrieval: queries the semantic index before generating G₀,
  injects top-5 similar wiki chunks as experiential_prior in the prompt. Trigger
  keywords: gerar tasks, criar tasks.md, generate tasks, criar tarefas.
version: 2.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Tasks, DAG, Execution, Planning]
    related_skills: [wiki-query, wiki-experiential_memory, sdd-generate_plan, sdd-refactor_artifact, agent_run, agent-orchestrator]
    category: sdd
    resources:
      - SKILL.md
      - references/task-rules.md
      - references/latte-task-rules.md
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
skill_view(name="sdd-generate_tasks", file_path="references/task-rules.md")
```

Este arquivo contém: regras de atomicidade, formato DAG, detecção de paralelismo,
mapeamento spec→tasks, fases canônicas e exemplos de derivação. Siga-o estritamente.

### Passo 4: Derivar tarefas atômicas com metadados DAG

Para cada elemento extraído no Passo 2, crie UMA tarefa. Cada task deve ter:

```markdown
- [ ] **Tnnn:** Descrição da tarefa
  - **Papel:** Dev | QA
  - **Dependências:** Txxx, Tyyy | Nenhuma
  - **Paralelizável:** true | false
  - **Arquivos:** `path/to/file.go`
```

**Regras de preenchimento:**

- **Papel:** derive da natureza da task. Código/implementação = Dev. Testes (unitários, integração, Gherkin, lint) = QA.
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

### --with-memory sem índice populado
Se `--with-memory` é passado mas `search_similar()` retorna erro (índice não existe, módulo não instalado): log warning, prossiga sem hints. Não aborte a geração — o `--with-memory` é um enhancement, não um hard requirement.

## Guardrails

- **Nunca agrupe ações:** "Criar X e testar Y" → 2 tarefas.
- **Tarefas já feitas:** verifique sistema de arquivos. Se código existe, `[x]`.
- **Dependências explícitas:** sempre declare no campo `Dependências:`.
- **Idempotência:** se `tasks.md` existe, pergunte se sobrescreve ou mescla.
- **Tamanho mínimo:** ao menos 4 tarefas (1 por fase).
- **Isolamento de arquivos:** HARD RULE — tasks paralelas NUNCA compartilham paths.
- **Interação fase por fase:** NUNCA gere todas as fases de uma vez. Use `clarify()`.

## Modo --with-memory (Experiential Memory)

> **Feature 002: Wiki Experiential Memory.** O `sdd-generate_tasks` pode consultar
> o índice semântico da wiki antes de gerar G₀, recuperando chunks similares de
> features anteriores e injetando-os como `experiential_prior` no prompt de
> derivação de tarefas.

### Quando ativar

Passe a flag `--with-memory` ao invocar o skill:

```
sdd-generate_tasks specs/features/NNN-slug --with-memory
```

**Pré-requisitos:**
- Índice semântico populado (`hermes wiki index --full` executado ao menos uma vez)
- Feature 002 (Wiki Experiential Memory) implementada (T001–T007 concluídos)
- Se o índice não existir, fallback gracioso: geração procede sem hints (Edge Case #1 do spec 002)

### Passo 3.5: Retrieve experiential hints

**Só execute se `--with-memory` foi passado.** Após carregar as regras (Passo 3)
e antes de derivar tarefas (Passo 4):

1. Extraia o texto completo do `spec.md` (propósito, cenários BDD, restrições).
   Inclua também campos relevantes do `plan.md` (stack, ADRs, contratos).
2. Chame `search_similar()` do módulo `../wiki/experiential_memory/search.py`:

```python
from ..wiki.experiential_memory.search import search_similar

hints = search_similar(
    query_text=spec_full_text,
    k=5,
    min_score=0.3  # ignora chunks com score muito baixo
)
```

3. Cada hint retornado contém:
   - `content`: texto do chunk
   - `source`: documento de origem (ex: `features/003-auth/spec.md`)
   - `heading`: heading path no documento original
   - `score`: score atual do chunk (0.0–1.0)
   - `similarity`: similaridade cosseno com a query (0.0–1.0)

4. Se `hints` for lista vazia (índice vazio ou sem matches acima do threshold):
   - Prossiga com geração normal (sem hints).
   - Não reporte erro — é esperado em cold start (Edge Case #6 do spec 002).

### Formato do experiential_prior no prompt

Injete os hints recuperados como uma seção `## Hints de features anteriores` no
prompt de derivação de tarefas (antes da derivação do Passo 4):

```markdown
## Hints de features anteriores (experiential memory)

Os chunks abaixo foram recuperados da wiki por similaridade semântica com esta feature.
Use-os como contexto para antecipar padrões de decomposição, tasks comuns e pitfalls:

| # | Score | Similaridade | Source | Conteúdo |
|---|-------|-------------|--------|----------|
| 1 | 0.72 | 0.89 | features/003-auth/plan.md > ## ADR-001 | "Migrações de banco devem ser versionadas..." |
| 2 | 0.68 | 0.85 | features/004-api/plan.md > ## Arquitetura | "Handlers HTTP devem seguir o padrão..." |
| 3 | 0.65 | 0.82 | features/003-auth/tasks.md > ## Fase 1 | "Sempre crie migration como primeira task..." |
| 4 | 0.60 | 0.79 | concepts/sdd.md > ## Pipeline | "Features com dependência externa precisam..." |
| 5 | 0.55 | 0.76 | features/005-chat/spec.md > ## Edge Cases | "Auth via OAuth2 requer refresh token rotation..." |

**Instruções para uso dos hints:**
- Prefira padrões de decomposição de features com score alto (> 0.6)
- Antecipe tasks que aparecem recorrentemente (migrations, testes, documentação)
- Evite pitfalls documentados em features com score baixo (< 0.3)
- Não copie tasks cegamente — adapte ao contexto da feature atual
- Hints são sugestivos; a estrutura final do G₀ deve refletir spec.md e plan.md
```

### Interação com o fluxo normal

Quando `--with-memory` está ativo:
- O Passo 3.5 (retrieval) é executado entre Passo 3 e Passo 4
- Os hints são injetados como contexto adicional no prompt de derivação
- A interação fase por fase (Passo 5) permanece idêntica
- A seção de hints é incluída no `tasks.md` gerado como comentário YAML no frontmatter:

```yaml
# experiential_hints:
#   query: "spec da feature NNN"
#   retrieved_at: "YYYY-MM-DD HH:MM"
#   chunks:
#     - source: "features/003-auth/plan.md"
#       heading: "## ADR-001"
#       score: 0.72
#       similarity: 0.89
```

### Referência

- **Módulo de busca:** `../wiki/experiential_memory/search.py` — implementa `search_similar(query_text, k, min_score)` que embedda a query via `all-MiniLM-L6-v2`, calcula similaridade cosseno contra o índice SQLite e retorna top-k chunks ordenados por `score × similarity`.
- **Spec completa:** `specs/features/002-experiential_memory/spec.md`
- **Tasks da feature 002:** `specs/features/002-experiential_memory/tasks.md`

## Modo LATTE — Coordenação Dinâmica (Graph Operators)

> **Feature 001: LATTE Coordination.** O `sdd-generate_tasks` gera `tasks.md` com
> sintaxe estendida para suportar o coordination graph dinâmico. A carga e parsing
> do grafo G₀ são feitos pelo `agent-orchestrator` via `load_G0_from_tasks_md()` —
> o generate_tasks apenas gera o arquivo com a nova sintaxe.

### Quando ativar

O modo LATTE é ativado quando o `tasks.md` contém `graph-operators: enabled` no
YAML frontmatter. **Sem esse campo, o comportamento padrão (DAG estático legado)
permanece inalterado** — compatibilidade reversa garantida (Edge Case #8 do spec:
_"tasks.md sem `graph-operators`: Modo legacy — orchestrator trata como DAG estático"_).

Para features que se beneficiam de descoberta dinâmica de tasks e coordenação
adaptativa, adicione ao YAML frontmatter do `tasks.md`:

```yaml
graph-operators: enabled
heartbeat-threshold: 4
max-rounds: 40
```

### Estrutura do tasks.md com LATTE

O `tasks.md` gerado em modo LATTE tem a seguinte estrutura:

1. **YAML frontmatter** com `graph-operators: enabled`, `heartbeat-threshold` e `max-rounds`
2. **Seções de fases** com tasks no formato DAG padrão (Papel, Dependências, Paralelizável, Arquivos)
3. **Seção `## Coordination Graph`** com o G₀ (grafo inicial) em formato de tabela markdown

Exemplo de YAML frontmatter para modo LATTE:

```yaml
---
feature_id: "NNN"
title: "Nome da Feature"
spec: "specs/features/NNN-slug/spec.md"
plan: "specs/features/NNN-slug/plan.md"
created: "YYYY-MM-DD"
author: "<autor>"
graph-operators: enabled
heartbeat-threshold: 4
max-rounds: 40
---
```

### Seção `## Coordination Graph`

O G₀ é o grafo inicial de tasks derivado do DAG estático, expresso como tabela
markdown. O `agent-orchestrator` usa `load_G0_from_tasks_md()` para parseá-lo
e inicializar o coordination graph em memória.

Formato:

```markdown
## Coordination Graph

| ID | Agent | Dependencies | Status |
|----|-------|-------------|--------|
| T001 | Dev | — | pending |
| T002 | Dev | T001 | pending |
| T003 | QA | — | pending |
```

**Regras de preenchimento:**

- `ID`: ID da task (T001, T002, ...) — consistente com as tasks nas fases acima
- `Agent`: `Dev` ou `QA` — mesmo valor do campo `Papel` da task correspondente
- `Dependencies`: IDs separados por vírgula (ex: `T001, T002`), ou `—` se `Nenhuma`
- `Status`: sempre `pending` no G₀ (estado inicial de toda task)

> **Nota:** A seção `## Coordination Graph` é gerada pelo `sdd-generate_tasks`
> automaticamente a partir do DAG derivado no Passo 4. O orchestrator a consome
> via `load_G0_from_tasks_md()` para inicializar o coordination graph em memória.

### Referências LATTE

- **Regras LATTE:** `skill_view(name="sdd-generate_tasks", file_path="references/latte-task-rules.md")` — regras específicas para geração de G₀ e coordination graph
- **Orchestrator:** A carga do G₀ é feita pelo `agent-orchestrator` via `load_G0_from_tasks_md()` no módulo `orchestrator.py`. O generate_tasks apenas gera a sintaxe.
- **Spec LATTE:** `specs/features/001-latte_coordination/spec.md` — definição completa do protocolo LATTE
- **Exemplo canônico:** `specs/features/001-latte_coordination/tasks.md` — tasks.md com `graph-operators: enabled`

### Compatibilidade reversa

Tasks.md **sem** `graph-operators` no YAML frontmatter → modo legacy (DAG estático).
O orchestrator detecta a ausência do campo e executa como DAG tradicional.
**Nenhuma mudança no comportamento padrão do generate_tasks.** O fluxo descrito
nos Passos 0–7 continua idêntico para features sem graph-operators.

## Verificação

- [ ] Approval gate verificado (`Aprovado: true`)
- [ ] `tasks.md` escrito em `specs/features/<id>-<slug>/`
- [ ] Cada task no formato DAG com Papel, Dependências, Paralelizável, Arquivos
- [ ] Tarefas agrupadas em fases canônicas
- [ ] DAG validado: sem ciclos, sem dependências quebradas, sem órfãs não intencionais
- [ ] Tasks paralelas têm conjuntos de Arquivos disjuntos
- [ ] Interação fase por fase concluída (clarify por fase)
- [ ] Usuário aprovou antes de salvar
- [ ] Se `--with-memory`: Passo 3.5 executado, hints recuperados e injetados no prompt
- [ ] Se `--with-memory`: hints registrados como comentário YAML no frontmatter do tasks.md
