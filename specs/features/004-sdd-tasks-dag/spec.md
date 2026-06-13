# Spec: Tasks com DAG (sdd-generate-tasks upgrade)

## Metadados
- **ID:** 004
- **Status:** draft
- **Aprovado:** false
- **Autor:** phm-aguiar
- **Data:** 2026-06-12
- **Feature Anterior:** 003-forge-skill
- **Dependência:** Nenhuma (feature independente)

## Propósito
> Upgrade do `sdd-generate-tasks` para gerar `tasks.md` com formato DAG (Directed Acyclic
> Graph), permitindo que o Runtime Orchestrator (feature 005) execute tasks em paralelo
> com segurança. O formato atual é flat (fases sequenciais com "Depende de Tnnn" simples) —
> não modela paralelismo explícito nem garante isolamento de arquivos entre tasks concorrentes.

Sem esse upgrade, o Runtime Orchestrator não tem como saber quais tasks podem rodar juntas
e quais precisam esperar. O DAG resolve isso: cada task declara explicitamente suas
dependências, os arquivos que afeta, e se é paralelizável com outras da mesma fase.

## Approval Gate
> **HARD-GATE:** Mesmo padrão definido na feature 005. O campo `Aprovado` no spec.md
> controla se o `sdd-generate-tasks` pode gerar o tasks.md final. O fluxo:

1. `sdd-brainstorm` gera spec.md → `sdd-generate-plan` gera plan.md
2. Usuário revisa spec.md + plan.md
3. Usuário altera `Aprovado: false` → `Aprovado: true` no spec.md
4. Usuário invoca `sdd-generate-tasks` para a feature
5. Skill verifica `Aprovado: true` → prossegue com a decomposição interativa
6. Se `Aprovado: false` → skill reporta "Spec não aprovada. Altere Aprovado: true no spec.md." e **aborta**

## Escopo

### Dentro do escopo
- Verificar `Aprovado: true` no spec.md antes de gerar tasks (approval gate)
- Ler `spec.md` e `plan.md` para extrair responsabilidades e escopo técnico
- Propor decomposição interativa: tasks atômicas por responsabilidade (Dev, QA, Test)
- Agrupar tasks em fases (Fase 1, Fase 2, ...) com dependências explícitas
- Detectar paralelismo: tasks da mesma fase sem dependência entre si E sem conflito de arquivos → marcadas como paralelizáveis
- Garantir isolamento de arquivos: **nunca** sugerir tasks paralelas que tocam o mesmo arquivo
- Validar DAG antes de salvar: detectar ciclos, dependências quebradas (ID inexistente), tasks órfãs
- Gerar `tasks.md` com formato DAG estruturado
- Formato legível por humanos E parseável pelo Runtime Orchestrator (feature 005)
- Interação fase por fase: usuário aprova/ajusta cada fase antes de avançar

### Fora do escopo (explicitamente)
- Modificar o `plan.md` — as 4 seções canônicas permanecem inalteradas
- Executar as tasks — responsabilidade do Runtime Orchestrator (feature 005)
- Garantir isolamento em runtime — o orchestrator confia no DAG validado
- Substituir o `sdd-generate-tasks` — é um upgrade da skill existente

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Usuário altera `Aprovado: true` no spec.md da feature
2. Usuário invoca: `sdd-generate-tasks` para `specs/features/004-*/`
3. Skill lê `spec.md` (funcionalidade, cenários) + `plan.md` (ADRs, stack)
4. Skill propõe Fase 1: tasks atômicas derivadas do spec, com papéis (Dev, QA, Test)
5. Usuário revisa: aprova, ajusta IDs, reordena, ou adiciona/remove tasks
6. Skill avança para Fase 2, repete interação
7. Ao final de todas as fases, skill monta DAG completo
8. Skill valida: sem ciclos, sem dependências quebradas, sem tasks órfãs
9. Skill gera `tasks.md` e salva

### Cenário de Conflito de Arquivos
1. Skill detecta que T003 e T004 (ambas Dev) tocariam em `internal/handler/message.go`
2. Skill **não sugere paralelismo** entre T003 e T004
3. Skill as coloca na mesma fase mas com dependência: T004 depende de T003
4. Skill alerta: "T003 e T004 compartilham handler/message.go — forçado sequencial"
5. Se inevitável (ex: arquivo único como `main.go`), skill alerta que a fase terá tasks sequenciais

### Cenário de DAG Inválido
1. Durante a interação, usuário insiste em dependência circular (T002 → T003 → T002)
2. Skill rejeita na validação final: "Ciclo detectado: T002 → T003 → T002. Corrija as dependências."
3. Skill mostra o ciclo exato e volta pra edição da fase problemática
4. Mesmo comportamento para dependência quebrada: "T005 depende de T099 que não existe"

### Cenário de Gate Bloqueado
1. Usuário invoca `sdd-generate-tasks` sem alterar `Aprovado: true`
2. Skill lê spec.md, encontra `Aprovado: false`
3. Skill reporta: "Spec não aprovada. Altere `Aprovado: true` no spec.md e re-invoque."
4. Skill **aborta** — zero interação iniciada

## Formato do tasks.md (DAG)

Cada seção de fase contém tasks com metadados estruturados:

```markdown
# tasks.md: {{FEATURE_NAME}}

## Fase 1: Fundação
- [ ] **T001:** Criar modelo Message
  - **Papel:** Dev
  - **Dependências:** Nenhuma
  - **Paralelizável:** true
  - **Arquivos:** `internal/model/message.go`

- [ ] **T002:** Criar schema do banco (migration)
  - **Papel:** Dev
  - **Dependências:** T001
  - **Paralelizável:** false
  - **Arquivos:** `internal/db/migrations/001_create_messages.sql`

## Fase 2: Implementação (paralela)
- [ ] **T003:** Criar handler HTTP POST /messages
  - **Papel:** Dev
  - **Dependências:** T001, T002
  - **Paralelizável:** true
  - **Arquivos:** `internal/handler/message_handler.go`

- [ ] **T004:** Criar cenários de aceitação (Gherkin)
  - **Papel:** QA
  - **Dependências:** Nenhuma (consome spec.md)
  - **Paralelizável:** true
  - **Arquivos:** `specs/features/004-*/acceptance/chat.feature`

- [ ] **T005:** Criar testes unitários do modelo Message
  - **Papel:** Test
  - **Dependências:** T001
  - **Paralelizável:** true
  - **Arquivos:** `internal/model/message_test.go`

## Fase 3: Finalização
- [ ] **T006:** Smoke test fim a fim
  - **Papel:** QA
  - **Dependências:** T003, T004, T005
  - **Paralelizável:** false
  - **Arquivos:** `test/smoke_test.go`
```

**Regras do formato:**
- `Paralelizável: true` → task pode rodar simultaneamente com outras `true` da mesma fase que não compartilhem arquivos
- `Paralelizável: false` → task é naturalmente sequencial (dependência explícita ou conflito de arquivo)
- `Arquivos:` → lista exaustiva de paths que a task vai criar/modificar. Usado pra detecção de conflito
- `Papel:` → Dev, QA, ou Test. Define o toolset do subagente no runtime-orchestrator

## Edge Cases

- **Tasks órfãs:** task em fase tardia sem dependências e sem conexão com o resto do DAG. Validação detecta e pergunta: "T007 é órfã — é intencional ou erro?"
- **Fase vazia:** usuário remove todas as tasks de uma fase. Skill pergunta se quer remover a fase ou mantê-la vazia como placeholder.
- **Arquivo listado mas task é QA:** QA gerando `.feature` files vs Dev gerando `.go`. Sem conflito mesmo se nomes colidirem (extensões diferentes). Skill é inteligente sobre isso.
- **Spec.md sem cenários BDD:** QA não tem base pra gerar cenários. Skill alerta: "Spec não tem cenários BDD — tasks de QA serão placeholders."
- **Tasks.md já existe:** skill detecta arquivo existente e pergunta: "tasks.md já existe. Sobrescrever, mesclar, ou abortar?"
- **Retrocompatibilidade:** tasks.md antigos (formato flat) continuam sendo lidos, mas sem paralelismo. Runtime-orchestrator trata tasks sem metadados como sequenciais.

## Constraints

- **Implementação:** Skill Hermes (upgrade do `sdd-generate-tasks` existente). Sem mudança de arquitetura.
- **Interatividade:** `clarify()` para aprovação fase por fase. Uma pergunta por fase.
- **Validação de DAG:** Lógica inline na skill (sem script externo). Detecção de ciclos, dependências quebradas, órfãs.
- **Formato do tasks.md:** Markdown com metadados estruturados por task (Papel, Dependências, Paralelizável, Arquivos).
- **Isolamento de arquivos:** Hard rule — tasks paralelas NUNCA compartilham paths na lista de Arquivos.
- **Tecnologia:** Nenhuma — skill é markdown + YAML frontmatter. Zero código.

## Critérios de Sucesso
- [ ] DAG gerado sem ciclos, dependências quebradas ou tasks órfãs
- [ ] Tasks marcadas como `Paralelizável: true` nunca compartilham arquivos na lista `Arquivos`
- [ ] Validação rejeita DAG inválido (ciclo, dependência quebrada) com mensagem clara
- [ ] Interação fase por fase funciona: usuário aprova/ajusta cada fase antes de avançar
- [ ] Tasks.md gerado é parseável pelo Runtime Orchestrator (feature 005)
- [ ] Tasks.md antigos (formato flat) não quebram — são tratados como sequenciais

## Abordagem Escolhida
> **Skill interativa com decomposição por responsabilidade.** O `sdd-generate-tasks` lê
> `spec.md` (funcionalidade, cenários BDD, constraints) e `plan.md` (ADRs, stack, contratos).
> A partir disso, propõe tasks atômicas agrupadas por papel (Dev, QA, Test) e por fase.
> A detecção de paralelismo usa isolamento de arquivos como regra primária: duas tasks
> da mesma fase são paralelizáveis se e somente se seus conjuntos de `Arquivos` forem disjuntos.
> O usuário aprova cada fase interativamente via `clarify()`. Ao final, o DAG completo é
> validado (ciclos, dependências, órfãs) antes de salvar.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Decomposição totalmente automática | Rápido, sem interação humana | Alto risco de tasks mal dimensionadas ou dependências incorretas. SDD exige precisão — melhor humano no loop |
| Agente Hermes separado | Isolamento de contexto, autonomia | Overhead desnecessário pra fluxo interativo. Skill com `clarify()` já resolve |
| Script de validação externo (Python/Go) | Validação robusta, testável | Adiciona dependência de runtime. Lógica de ciclo/DAG é simples o suficiente pra inline |

## Dependências
- **Nenhuma.** Feature independente. O `sdd-generate-tasks` atual já funciona — este é um upgrade de formato.
- **Consumido por:** Feature 005 (Runtime Orchestrator), que depende do formato DAG no tasks.md.

## Checklist de Prontidão
- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Approval gate definido e documentado
- [ ] Formato do tasks.md com DAG especificado com exemplo
- [ ] Cenários cobrem happy path, conflito de arquivos, DAG inválido, e gate bloqueado
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada
