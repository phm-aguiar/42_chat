# Spec: Runtime Orchestrator SDD

## Metadados
- **ID:** 013
- **Status:** draft
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-12
- **Feature Anterior:** 012-sdd-tasks-dag
- **Dependência:** 012-sdd-tasks-dag (tasks.md com formato DAG: fases, dependências, paralelismo, isolamento de arquivos)

## Propósito
> Automatizar a supervisão da fase de implementação SDD, permitindo paralelismo real
> entre subagentes especializados (Dev, QA) enquanto garante rastreabilidade
> total à spec. Elimina a necessidade de babysitting humano durante a execução das
> tasks, com ciclo de retry inteligente e escalação seletiva de bloqueios.

O sdd-orchestrator atual gera artefatos (spec → plan → tasks) mas não executa nada.
Depois que o tasks.md está pronto, o usuário precisa manualmente spawnar e monitorar
cada subagente. O Runtime Orchestrator preenche essa lacuna: lê o DAG de tasks,
spawna subagentes em paralelo, monitora saúde, aplica política de retry, e só
interrompe o humano quando há um bloqueio real que requer decisão.

## Approval Gate

> **HARD-GATE:** O Runtime Orchestrator NUNCA spawna subagentes sem que o campo
> `Aprovado` nos metadados esteja `true`. Este campo é modificado exclusivamente
> pelo usuário. O fluxo é:

1. `sdd-orchestrator` gera spec.md → plan.md → tasks.md (feature 004: sdd-generate-tasks com DAG)
2. Usuário revisa os artefatos
3. Usuário altera `Aprovado: false` → `Aprovado: true` no spec.md
4. Usuário invoca `agent-run runtime-orchestrator "orquestra a feature 005"`
5. Orchestrator lê spec.md, verifica `Aprovado: true` → prossegue
6. Se `Aprovado: false` → orchestrator reporta "Spec não aprovada. Altere Aprovado: true no spec.md e re-invoque." e **aborta**

## Escopo

### Dentro do escopo
- Ler `tasks.md` e interpretar o DAG de dependências (sequencial/paralelo)
- Verificar `Aprovado: true` no spec.md antes de qualquer spawn (approval gate)
- Spawnar subagentes especializados via `delegate_task` com contexto mastigado
- Janela deslizante de 3 subagentes simultâneos (limite do `delegate_task`)
- Política de retry: máx 3 tentativas por task, com contexto enriquecido a cada falha
- Timeout configurável por task (default: 30min); estouro conta como falha
- Validar evidência de DONE (diff, smoke-test, arquivos criados) antes de marcar `[x]`
- Escalar bloqueios para o humano após 3 falhas, pausando só a sub-árvore dependente
- Atualizar `tasks.md` com marcação `[x]` nas tasks concluídas
- Re-spawnar task do zero após ajuste humano

### Fora do escopo (explicitamente)
- Gerar artefatos SDD (spec.md, plan.md, tasks.md) — responsabilidade do `sdd-orchestrator`
- Implementar código — responsabilidade do subagente Dev
- Escrever cenários de teste (Gherkin/Cucumber) — responsabilidade do subagente QA
- Executar testes unitários/integração — responsabilidade do subagente QA
- Tomar decisões arquiteturais — definido em `plan.md` + aprovação humana
- Substituir o `sdd-orchestrator` existente — são complementares

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Usuário altera `Aprovado: true` no `spec.md` da feature
2. Usuário invoca: `agent-run` → agente `runtime-orchestrator` → "orquestra a feature 005"
3. Orchestrator lê `spec.md`, verifica `Aprovado: true` ✓
4. Orchestrator lê `specs/features/005-*/tasks.md`, extrai DAG de dependências
5. Identifica tasks sem dependências (raízes do DAG), spawna até 3 em paralelo via `delegate_task`
6. Subagente Dev conclui, reporta DONE com evidência: diff, arquivos criados, smoke-test output
7. Orchestrator valida evidência (arquivos existem? smoke-test passou?), marca `[x]` no tasks.md
8. Libera próxima task cujas dependências estão satisfeitas; spawna se houver vaga na janela
9. Ciclo se repete até tasks.md completamente `[x]` — feature implementada

### Cenário de Gate Bloqueado
1. Usuário invoca orchestrator sem ter alterado `Aprovado: true`
2. Orchestrator lê spec.md, encontra `Aprovado: false`
3. Orchestrator reporta: "Spec não aprovada. Altere `Aprovado: true` no spec.md e re-invoque."
4. Orchestrator **aborta** — zero subagentes spawnados

### Cenário de Falha com Retry
1. Subagente reporta FAIL (exit code ≠ 0, build quebrou, erro não recuperável)
2. Orchestrator extrai contexto do erro (stack trace, mensagem, arquivo afetado)
3. Re-spawna o mesmo subagente com contexto enriquecido: "tentativa 2/3. Erro anterior: ..."
4. Se 2ª tentativa falhar → re-spawna com "tentativa 3/3. Histórico de erros: ..."
5. Se 3ª tentativa falhar → escala pro humano, pausa a sub-árvore dependente
6. Tasks paralelas sem dependência na task travada **continuam rodando normalmente**

### Cenário de Escalação e Recuperação
1. Orchestrator reporta ao usuário: "Task T003 falhou 3x. Erro: ... Sub-árvore pausada: T005, T007"
2. Usuário ajusta spec.md, plan.md ou tasks.md conforme necessário
3. Usuário diz "continua" → orchestrator re-spawna T003 do zero com o contexto atualizado
4. Se T003 passar → destrava sub-árvore, T005 e T007 entram na janela de execução

## Edge Cases

- **Spawn failure (infra):** subagente nem chega a spawnar (API key inválida, rate limit, Hermes Agent fora do ar). **Aborta a feature inteira** — é falha de infraestrutura, não de lógica. Reporta ao usuário com o erro exato.
- **Morte silenciosa do subagente:** subagente morre sem reportar DONE/FAIL/BLOCKED (crash, OOM, rede). **Timeout por task** (configurável, default 30min) detecta. Estouro conta como falha → entra no ciclo de retry com contexto de timeout.
- **Conflito de arquivos em tasks paralelas:** duas tasks paralelas tentando modificar o mesmo arquivo. **NUNCA deve ocorrer** — o `tasks.md` gerado pelo `sdd-generate-tasks` (feature 004) garante isolamento via lista de `Arquivos`. Se um subagente descobrir que precisa modificar algo fora do seu escopo atômico → reporta BLOCKED imediatamente, não força.
- **Tasks.md mal formado:** DAG ilegível, dependência circular, task sem ID. Orchestrator rejeita antes de spawnar qualquer coisa → reporta erro de validação com linha exata do problema.
- **Subagente reporta DONE mas evidência é vazia/inválida:** orchestrator rejeita o DONE → conta como falha → entra no ciclo de retry com contexto: "evidência insuficiente: esperado diff e smoke-test output, recebido vazio".
- **Usuário aborta manualmente:** `Ctrl+C` ou `/stop` no agent-run. Orchestrator faz cleanup (mata subagentes ativos) e reporta estado atual: tasks concluídas vs pendentes.
- **Aprovado alterado para false durante execução:** se o usuário mudar `Aprovado: false` enquanto o orchestrator está rodando, o orchestrator **não re-verifica** — a verificação é only-once no início. Execuções em andamento não são interrompidas.

## Constraints

- **Implementação:** Agente Hermes (`AGENT.md` + `context.yaml`), invocado via `agent-run`. Zero dependências externas.
- **Subagentes:** Exclusivamente via `delegate_task`. Limite de 3 simultâneos com janela deslizante.
- **Timeout:** Configurável por task no `tasks.md`. Default: 30 minutos.
- **Retry:** Hardcoded em 3 tentativas. Sem configuração por task no MVP.
- **Dependência:** Feature 004 (`sdd-generate-tasks` com DAG e paralelismo) deve existir antes. O orchestrator assume que o `tasks.md` tem formato de DAG válido.
- **Approval Gate:** Campo `Aprovado` no spec.md deve ser `true`. Verificado only-once no início da execução.
- **Tecnologia:** Go (alinhado ao stack do projeto). Sem banco de dados — estado em memória + tasks.md.

## Critérios de Sucesso
- [ ] Approval gate funciona: `Aprovado: false` → aborta; `Aprovado: true` → prossegue
- [ ] DAG de tasks é respeitado: tasks sequenciais esperam dependências, tasks paralelas disparam juntas
- [ ] Retry com contexto enriquecido funciona: subagente recebe erro da tentativa anterior e se recupera
- [ ] Escalação pro humano funciona: 3 falhas → pausa seletiva da sub-árvore → usuário ajusta → re-spawn OK
- [ ] Paralelismo não causa conflito: isolamento de arquivos garantido pelo `tasks.md` com DAG (feature 004)
- [ ] Timeout detecta subagente morto e aciona ciclo de retry
- [ ] Spawn failure da infra aborta feature imediatamente (sem retry infinito)

## Abordagem Escolhida
> **Agente Hermes + delegate_task.** Mesmo padrão arquitetural do `sdd-orchestrator` existente.
> O Runtime Orchestrator é um agente Hermes definido por `AGENT.md` + `context.yaml` em
> `.hermes/agents/runtime-orchestrator/`, invocado via `agent-run`. Subagentes são spawnados
> via `delegate_task` com ferramentas específicas por papel (Dev: terminal+file, QA: terminal+file+web).
> Janela deslizante de 3 subagentes gerencia o limite físico do `delegate_task`.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Script standalone + API | Mais controle sobre heartbeat/timeout nativo, mas adiciona complexidade de infra (processo separado, autenticação, estado persistente) | Viola constraint de "zero dependências externas". Agente Hermes já resolve o problema com `delegate_task` |
| Skill inline (sem agente separado) | Mais simples, sem necessidade de AGENT.md/context.yaml | Sem isolamento de contexto, o usuário teria que ficar presente durante toda a execução. Perde o propósito de "soltar e esquecer" |

## Dependências
- **Feature 004 (sdd-tasks-dag):** `sdd-generate-tasks` gera `tasks.md` com DAG (fases, dependências, paralelismo, isolamento de arquivos). O Runtime Orchestrator **não funciona** sem esse formato.
- **`delegate_task`:** Ferramenta Hermes Agent para spawn de subagentes. Já disponível, limite de 3 simultâneos.

## Checklist de Prontidão
- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Approval gate definido e documentado
- [ ] Cenários cobrem happy path, gate bloqueado, falha com retry, e escalação
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada
