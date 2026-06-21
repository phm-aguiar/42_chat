# Spec: Agent QA (guardião da qualidade)

## Metadados
- **ID:** 007
- **Status:** draft
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-13
- **Feature Anterior:** 006-agent-dev
- **Dependência:** 013-runtime-orchestrator (orchestrator spawna o agent-qa como subagente leaf)

## Propósito
> O agent-qa é o guardião da qualidade do framework SDD. Spawnado pelo orchestrator como
> subagente leaf, ele valida implementações do agent-dev contra a spec, escreve cenários
> Gherkin, executa testes, e tem o poder de **rejeitar** tasks que não atendem aos critérios
> — forçando o orchestrator a re-spawnar o Dev com contexto melhorado.

O agent-dev (006) implementa código. Mas implementar não garante qualidade. O agent-qa
preenche essa lacuna: é uma **persona fixa** (molde) que recebe skills de teste por stack
(gherkin-scenarios, go-unit-tests, local-test-runner) injetadas pelo orchestrator.

**Skills são trilhos, não jaulas.** Se a skill não cobre o necessário, reporta BLOCKED:
"impossível testar com as skills disponíveis". Sem acesso web — apenas terminal + file,
para evitar alucinação e overengineering fora do microcontexto.

> **Nota:** As skills de teste (gherkin, unitário, lint, cobertura) serão desenvolvidas
> posteriormente, baseadas em padrões da comunidade. Por enquanto, o QA é um molde.

## Escopo

### Dentro do escopo
- Definir a persona do agente QA (`AGENT.md` + `context.yaml` em `.hermes/agents/agent-qa/`)
- Ciclo de trabalho: lê spec → escreve cenários Gherkin → executa testes → lint → cobertura → reporta
- Receber skills de teste por stack (injetadas pelo orchestrator)
- Reportar DONE com evidência completa (testes passando, lint limpo, cobertura OK)
- Reportar REJECTED: implementação não atende a spec — com evidência do que falhou
- Reportar BLOCKED: spec ambígua ou skill não cobre o necessário
- Não julga causa de falha — reporta tudo e deixa o orchestrator decidir
- Cobre: testes unitários, cenários Gherkin/BDD, lint, cobertura, E2E, regressão

### Fora do escopo (explicitamente)
- Skills de teste por stack (`gherkin-scenarios`, `go-unit-tests`, `local-test-runner`) — features separadas
- Testes de integração e performance — responsabilidade do DevOps (008)
- Segurança (OWASP, secrets) — responsabilidade do Pentester (009)
- Corrigir código — responsabilidade do Dev (006)
- Modificar spec.md ou plan.md — QA valida, não redefine requisitos
- Acesso web — apenas terminal + file (skills são os trilhos)

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Orchestrator monta contexto: spec relevante, código implementado pelo Dev, task atômica,
   skills de teste da stack, tentativa N/3
2. Orchestrator spawna agent-qa via `delegate_task` com toolsets `terminal` + `file`
3. QA lê a spec e identifica os requisitos a serem validados
4. Escreve cenários Gherkin (.feature) baseados nos cenários BDD da spec
5. Implementa testes unitários (`_test.go` files) cobrindo as funções da task
6. Executa testes: `go test ./...` (ou equivalente da stack)
7. Roda lint: `go vet`, `golangci-lint` (ou equivalente)
8. Verifica cobertura: `go test -cover` (ou equivalente)
9. Se tudo passa → DONE com evidência:
   - Output dos testes (exit code 0)
   - Output do lint (sem warnings)
   - Cobertura atingida
   - Arquivos de teste criados
10. Orchestrator valida evidência e marca `[x]` no tasks.md

### Cenário: Rejeição (REJECTED)
1. QA executa testes e encontra falha (teste quebrado, lint warning, cobertura abaixo do threshold)
2. QA NÃO tenta corrigir — reporta REJECTED com:
   - Teste que falhou (nome, arquivo, linha)
   - Output completo do erro
   - Lint warning encontrado
   - Cobertura atual vs esperada
3. QA não julga se a falha é culpa do Dev ou pré-existente — reporta tudo
4. Orchestrator recebe REJECTED, re-spawna Dev com contexto enriquecido:
   "QA rejeitou: <evidência>. Corrija e re-implemente."
5. Se 3 rejeições → orchestrator escala pro humano

### Cenário: Spec Ambígua (BLOCKED)
1. QA lê a spec e encontra ambiguidade que impede a validação
   (ex: "sistema deve ser rápido" sem métrica de tempo)
2. QA NÃO infere — reporta BLOCKED com pergunta específica
3. Orchestrator escala pro humano

### Cenário: Skill Não Cobre (BLOCKED)
1. QA recebe task que exige um tipo de teste não coberto pelas skills injetadas
2. QA reporta BLOCKED: "impossível testar X: skill Y não cobre este cenário"
3. Não tenta buscar na web ou improvisar — skills são os trilhos

## Edge Cases
- **Falso positivo do lint:** QA encontra lint warning em código pré-existente. Reporta
  REJECTED com evidência. Não julga causa. O orchestrator decide se é falso positivo
- **Cobertura impossível:** task é pequena (ex: config, constantes) e cobertura de 80%
  é irreal. QA reporta DONE com cobertura real e nota: "task pequena, cobertura X% é
  o máximo atingível"
- **Rejeição em cascata:** QA rejeita → Dev re-implementa → QA rejeita de novo →
  Dev re-implementa → QA rejeita 3ª vez → orchestrator escala pro humano
- **QA spawnado sem skills:** modo "força bruta" — executa testes com comandos padrão
  da stack (`go test`, `go vet`), sem Gherkin. Qualidade menor mas não é BLOCKED
- **Contexto corrompido:** se spec ou código do Dev não estiverem no contexto → FAIL
  imediato: "Contexto insuficiente para validação"

## Constraints
- **Execução:** Subagente leaf via `delegate_task`. Não pode delegar, não pode usar `clarify`
- **Toolsets:** `terminal` + `file`. **Sem acesso web** — skills são os trilhos para evitar alucinação
- **Timeout:** 30 minutos por task (default do orchestrator). Gerenciado externamente
- **Retry:** Gerenciado pelo orchestrator. QA apenas reporta REJECTED
- **Nunca infere:** Ambiguidades → BLOCKED. Skill não cobre → BLOCKED
- **Não julga causa:** Reporta tudo que encontra. Não decide se é culpa do Dev ou pré-existente
- **Tecnologia:** Agente Hermes (AGENT.md + context.yaml). Zero dependências externas

## Critérios de Sucesso
- [ ] `AGENT.md` existe em `.hermes/agents/agent-qa/` com persona, tom e ciclo de trabalho definidos
- [ ] `context.yaml` configurado com toolsets `terminal` + `file`
- [ ] Agent-qa spawna corretamente via `agent-run`
- [ ] Happy path: lê spec → escreve cenários Gherkin → executa testes → lint → reporta DONE
- [ ] Reporta REJECTED com evidência quando testes falham
- [ ] Reporta BLOCKED quando spec é ambígua
- [ ] Reporta BLOCKED quando skill não cobre o necessário
- [ ] Funciona com skills injetadas (usa skills como trilhos)
- [ ] Funciona sem skills (modo "força bruta" com comandos padrão da stack)
- [ ] Smoke test real executado e verificado

## Abordagem Escolhida
> **Agente Hermes com persona fixa + skills de teste plugáveis por stack.**
> Mesmo padrão do agent-dev (006). Persona é um molde — as skills de teste
> (gherkin-scenarios, go-unit-tests, local-test-runner) serão desenvolvidas
> posteriormente baseadas em padrões da comunidade.
>
> Toolsets: `terminal` + `file` apenas. Sem acesso web — skills são os trilhos.
> Se a skill não cobre, BLOCKED. Isso evita alucinação e overengineering.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| QA com acesso web | Poderia buscar soluções pra erros, mas alto risco de alucinação e fuga do microcontexto | Viola princípio de skills como trilhos. Aumenta superfície de erro |
| QA + Dev no mesmo agente | Elimina ciclo de rejeição, mais rápido | Sem separação de responsabilidades. Dev não pode validar o próprio código |
| QA como skill do Dev (não agente separado) | Mais simples, menos arquivos | Perde isolamento de contexto. Dev não deveria testar o próprio código |

## Dependências
- **Feature 005 (runtime-orchestrator):** orchestrator spawna QA como subagente leaf
- **Feature 006 (agent-dev):** QA valida código implementado pelo Dev. Rejeição força re-spawn
- **Skills de teste (futuro):** `gherkin-scenarios`, `go-unit-tests`, `local-test-runner`

## Checklist de Prontidão
- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Cenários cobrem happy path, rejeição, spec ambígua, e skill não cobre
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada com alternativas consideradas
