# Spec: Agent Dev (agente implementador)

## Metadados
- **ID:** 006
- **Status:** draft
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-13
- **Feature Anterior:** 005-runtime-orchestrator
- **Dependência:** 005-runtime-orchestrator (orchestrator spawna o agent-dev como subagente leaf)

## Propósito
> O agent-dev é o braço executor do framework SDD autônomo. Spawnado pelo orchestrator
> como subagente leaf, ele recebe uma task atômica (com spec relevante, ADRs do plan,
> e skills da stack) e gera código funcional com smoke-test, eliminando a necessidade
> de um dev humano escrever a primeira versão.

O orchestrator (feature 005) já sabe COORDENAR — ler DAG, spawnar subagentes, gerenciar
retry, escalar bloqueios. Mas ele não sabe IMPLEMENTAR. O agent-dev preenche essa lacuna:
é uma **persona fixa** (AGENT.md define identidade, tom, ciclo de trabalho) que recebe
**skills plugáveis por stack** (go-implement, python-implement, etc.) injetadas pelo
orchestrator conforme o `tech.md` do projeto.

Skills são **trilhos, não jaulas**: o agente usa templates e convenções como guia, mas
pode adaptar criativamente quando a skill não cobre um padrão específico — desde que
mantenha as convenções do projeto.

## Escopo

### Dentro do escopo
- Definir a persona do agente Dev (`AGENT.md` + `context.yaml` em `.hermes/agents/agent-dev/`)
- Ciclo de trabalho padrão: lê contexto → planeja → implementa → smoke-test → reporta
- Receber skills plugáveis por stack (injetadas pelo orchestrator) e integrá-las ao fluxo
- Reportar DONE com evidência rastreável à spec (diff, arquivos criados, smoke-test output,
  link explícito spec→código: "Função X atende requisito Y da spec, seção Z")
- Reportar BLOCKED com pergunta específica quando a spec for ambígua (nunca infere)
- Reportar FAIL com stack trace e arquivo afetado quando build/smoke-test quebra
- Aceitar re-spawn com contexto melhorado (ciclo de retry gerenciado pelo orchestrator)
- Aceitar rejeição do QA futuro: se o QA desmarcar a conclusão, o orchestrator re-spawna
  o Dev com contexto enriquecido (incluindo o problema apontado pelo QA)

### Fora do escopo (explicitamente)
- Skills de implementação por stack (`go-implement`, `python-implement`, `go-refactor`,
  `smoke-check`, etc.) — são features separadas
- Decidir quais skills injetar — responsabilidade do orchestrator
- Gerenciar ciclo de retry — responsabilidade do orchestrator
- Validar qualidade do código além do smoke-test — responsabilidade do QA (feature 007)
- Testes unitários, Gherkin, lint — responsabilidade do QA (feature 007)
- CI/CD, deploy — responsabilidade do DevOps (feature 008)
- Segurança, OWASP, secrets — responsabilidade do Pentester (feature 009)
- Modificar spec.md ou plan.md — o Dev implementa, não redefine requisitos

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Orchestrator monta contexto: spec relevante, ADRs do plan, task atômica (Papel: Dev,
   Arquivos: [...], Dependências satisfeitas: [...]), skills da stack (ex: `go-implement`,
   `smoke-check`), tentativa N/3
2. Orchestrator spawna agent-dev via `delegate_task` com toolsets `terminal` + `file`
3. Agent-dev lê o contexto completo (spec, plan, task, skills)
4. Planeja implementação: identifica funções/arquivos necessários, verifica se as skills
   cobrem os padrões exigidos
5. Implementa código seguindo as skills como trilhos (adaptando criativamente se necessário,
   mantendo convenções do projeto)
6. Executa smoke-test (build, checagem de sintaxe) usando a skill `smoke-check` (ou
   comando equivalente da stack)
7. Smoke-test passa → reporta DONE com evidência:
   - Diff ou lista de arquivos criados/modificados
   - Output do smoke-test (exit code 0)
   - Rastreabilidade: "Função X atende requisito Y da spec, seção Z"
8. Orchestrator valida evidência e marca `[x]` no tasks.md

### Cenário: Spec Ambígua (BLOCKED)
1. Agent-dev lê o contexto e encontra ambiguidade na spec (ex: "implementar autenticação"
   sem especificar mecanismo — JWT? OAuth? session?)
2. Agent-dev NÃO infere — reporta BLOCKED com pergunta específica:
   "Spec ambígua na seção 3.2: 'implementar autenticação' não especifica mecanismo.
   Opções: JWT, OAuth2, session-based. Qual usar?"
3. Orchestrator recebe BLOCKED, escala pro humano
4. Humano ajusta spec → orchestrator re-spawna agent-dev do zero

### Cenário: Build Quebra (FAIL → Retry)
1. Agent-dev implementa código, executa smoke-test
2. Build quebra com erro de compilação
3. Agent-dev reporta FAIL com: stack trace completo, arquivo e linha do erro,
   possível causa
4. Orchestrator recebe FAIL, re-spawna agent-dev com contexto enriquecido:
   "Tentativa 2/3. Erro anterior: <stack trace>"
5. Agent-dev re-implementa considerando o erro anterior
6. Se 3 falhas → orchestrator escala pro humano

### Cenário: Rejeição pelo QA (futuro, feature 007)
1. QA (feature 007) valida implementação do Dev e encontra problema
   (ex: "função X não cobre edge case Y da spec")
2. QA reporta ao orchestrator: task desmarcada, motivo do problema
3. Orchestrator re-spawna agent-dev com contexto enriquecido incluindo o feedback do QA
4. Agent-dev re-implementa endereçando o problema apontado
5. Ciclo normal de DONE/FAIL se aplica

## Edge Cases
- **Skill injetada não cobre padrão necessário:** o agente adapta criativamente mantendo
  as convenções do projeto. Skills são trilhos, não jaulas. Se a adaptação falhar no
  smoke-test → entra no ciclo normal de FAIL
- **Smoke-test não definido pra stack:** se a skill `smoke-check` não existir ou não cobrir
  a stack atual, o agente tenta o comando padrão da linguagem (`go build`, `python -m
  compileall`, `cargo check`). Se falhar → reporta BLOCKED: "smoke-test indisponível
  para stack X"
- **Dependência não listada no tech.md:** se a implementação exigir uma lib externa não
  prevista, o agente pode instalá-la (`go get`, `pip install`) e modificar o arquivo de
  manifesto (`go.mod`, `pyproject.toml`). O DAG do tasks.md garante que nenhuma outra
  task paralela está mexendo no mesmo arquivo
- **Arquivo fora do escopo da task:** se a implementação naturalmente exigir modificar
  um arquivo não listado na task (ex: registro de rota em `main.go`), o agente modifica
  mesmo assim e reporta no DONE: "Arquivos adicionais modificados: main.go (registro de
  rota)". O DAG garante que não há conflito
- **Contexto do orchestrator corrompido ou vazio:** se o contexto recebido não contiver
  spec, plan ou task → reporta FAIL imediatamente: "Contexto insuficiente: faltam spec,
  plan ou task"
- **Spawning sem skills:** se o orchestrator não injetar skills, o agente opera em modo
  "força bruta" — implementa usando conhecimento geral da stack. Qualidade pode ser menor,
  mas não é BLOCKED (skills são trilhos, não pré-requisitos)
- **Re-spawn após rejeição do QA (futuro):** o agente recebe o feedback do QA no contexto
  e trata como uma nova tentativa (reseta o contador interno de planejamento, não acumula
  "teimosia")

## Constraints
- **Execução:** Subagente leaf via `delegate_task`. Não pode delegar, não pode usar
  `clarify` (interage apenas via DONE/FAIL/BLOCKED)
- **Toolsets:** `terminal` + `file`. Sem acesso a browser/web — apenas código local
- **Timeout:** 30 minutos por task (default do orchestrator). Gerenciado externamente
- **Retry:** Gerenciado pelo orchestrator (máx 3 tentativas). O agent-dev apenas reporta
  FAIL e recebe contexto enriquecido na próxima tentativa
- **Isolamento:** Garantido pelo DAG do tasks.md (feature 004). O agent-dev não precisa
  verificar conflitos de arquivo
- **Skills:** Opcionais (trilhos, não pré-requisitos). O agente funciona sem skills,
  mas com qualidade potencialmente menor
- **Nunca infere:** Ambiguidades na spec sempre resultam em BLOCKED, nunca em inferência
- **Tecnologia:** Agente Hermes (AGENT.md + context.yaml). Zero dependências externas

## Critérios de Sucesso
- [ ] `AGENT.md` existe em `.hermes/agents/agent-dev/` com persona, tom e ciclo de trabalho definidos
- [ ] `context.yaml` configurado com toolsets `terminal` + `file`
- [ ] Agent-dev spawna corretamente via `agent-run` e responde a uma task simulada
- [ ] Happy path funciona: lê contexto → planeja → implementa → smoke-test → reporta DONE com evidência
- [ ] Evidência de DONE é rastreável à spec (link explícito: função X → requisito Y, seção Z)
- [ ] Reporta BLOCKED com pergunta específica quando spec é ambígua (nunca infere)
- [ ] Reporta FAIL com stack trace e arquivo afetado quando build quebra
- [ ] Funciona com skills injetadas (usa skills como trilhos, adapta quando necessário)
- [ ] Funciona sem skills (modo "força bruta" — implementa usando conhecimento geral da stack)
- [ ] Smoke test real executado e verificado (não simulado)

## Abordagem Escolhida
> **Agente Hermes com persona fixa + skills plugáveis por stack.**
> O agent-dev é definido por `AGENT.md` + `context.yaml` em `.hermes/agents/agent-dev/`.
> A persona é fixa (identidade, tom, ciclo de trabalho). As skills de implementação
> por stack (`go-implement`, `python-implement`, etc.) são injetadas pelo orchestrator
> conforme o `tech.md` do projeto.
>
> Skills são **trilhos, não jaulas**: guiam com templates e convenções, mas o agente
> pode adaptar criativamente quando a skill não cobre um padrão — mantendo as
> convenções do projeto. Isso evita o dilema "skill rígida vs criatividade zero".
>
> O contrato com o orchestrator é via `delegate_task`: recebe contexto mastigado,
> reporta DONE (com evidência rastreável), FAIL (com stack trace), ou BLOCKED
> (com pergunta específica).

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Agente monolítico (persona + skills hardcoded) | Mais simples, mas acopla stack à persona. Cada nova linguagem exige reescrever o agente | Viola o princípio de skills plugáveis. O framework precisa ser multi-stack |
| Skill pura sem persona (o orchestrator injeta uma skill que "faz tudo") | Elimina o agente como entidade separada | Sem persona, perde-se identidade e ciclo de trabalho padronizado. Skills viram "mini-agentes" desorganizados |
| Agente que infere ambiguidades | Mais rápido (menos BLOCKEDs), mas arriscado | Viola o princípio de nunca implementar sem spec aprovada. Inferências erradas custam mais caro que BLOCKEDs |

## Dependências
- **Feature 005 (runtime-orchestrator):** o orchestrator é quem spawna o agent-dev como
  subagente leaf. O contrato de comunicação (DONE/FAIL/BLOCKED) é definido pelo orchestrator
- **Skills de stack (features futuras):** `go-implement`, `python-implement`, `smoke-check`,
  etc. Não são pré-requisito — o agent-dev funciona sem skills (modo "força bruta")

## Checklist de Prontidão
- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Cenários cobrem happy path, spec ambígua, build quebra, e rejeição pelo QA
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada com alternativas consideradas
