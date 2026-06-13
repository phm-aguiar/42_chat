# Plano Arquitetural: Agent Orchestrator (Runtime SDD)

## 1. Metadados do Plano

- **Stack Tecnológico:** Hermes Agent (`AGENT.md` + `context.yaml`), invocado via `agent-run`. Zero dependências de runtime externas. Subagentes spawnados exclusivamente via `delegate_task`.
- **Feature Fonte:** `specs/features/005-runtime-orchestrator/spec.md`
- **Escopo:** Agente supervisor que lê `tasks.md` com formato DAG (feature 004), spawna subagentes especializados (Dev, QA, Test) em paralelo com janela deslizante de 3, aplica política de retry (3 tentativas com contexto enriquecido), valida evidência de conclusão, e escala bloqueios para o humano.

## 2. Design de Contratos e Fronteiras

- **Contrato de entrada:** `tasks.md` com formato DAG (metadados `Papel`, `Dependências`, `Paralelizável`, `Arquivos` por task). Feature 004 garante o formato.
- **Contrato de saída:** `tasks.md` atualizado com `[x]` nas tasks concluídas. Relatório de execução no último turno.
- **Contrato com subagentes:**
  - Cada subagente recebe contexto mastigado: spec relevante + task específica + arquivos que deve tocar
  - Subagente deve reportar `DONE` com evidência (diff, smoke-test output, arquivos criados) ou `FAIL` com stack trace
  - Timeout por task: 30 minutos (default, configurável)
- **Convenção:**
  - Estado em memória (sem banco de dados)
  - Janela deslizante de 3 subagentes simultâneos (limite do `delegate_task`)
  - Approval gate: verificado once no início (`Aprovado: true` no spec.md)

### Interface com subagentes

```
delegate_task(
    goal="T003: Criar handler HTTP POST /messages",
    context="
        Spec: specs/features/005-*/spec.md (seções: X, Y)
        Task: T003 — Papel: Dev, Arquivos: internal/handler/message_handler.go
        Dependências satisfeitas: T001, T002 (já concluídas)
        Tentativa: 1/3
    ",
    toolsets=["terminal", "file"]  # Dev: código + build
)
```

### Mapeamento Papel → Toolset

| Papel | Toolsets | Descrição |
|---|---|---|
| Dev | `terminal`, `file` | Escreve código, build, smoke-test |
| QA | `terminal`, `file`, `web` | Testes, Gherkin, lint, referências |
| Test | `terminal`, `file` | Testes unitários, cobertura |

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-001: Agente Hermes, não binário Go standalone

- **Decisão:** O orchestrator é um agente Hermes (`AGENT.md` + `context.yaml`), não um binário Go compilado.
- **Justificativa:** A orquestração é essencialmente um loop de leitura de arquivo + spawn de subagente + validação de output. Um agente Hermes com `delegate_task` executa isso nativamente, sem necessidade de um runtime separado. O estado (tasks concluídas, tentativas, timeouts) cabe em memória durante a execução. A complexidade adicional de um binário Go (compilação, deploy, gestão de processos) não se justifica para um supervisor que essencialmente coordena outros agentes.
- **Alternativa Rejeitada:** Binário Go com API de spawn de processos. Rejeitado — viola a constraint de "zero dependências externas" e adiciona complexidade de infra desnecessária para a função de supervisão.

### ADR-002: Janela deslizante de 3 subagentes

- **Decisão:** No máximo 3 subagentes simultâneos. Quando um conclui, o próximo elegível (dependências satisfeitas) entra na janela.
- **Justificativa:** O limite de 3 é físico — `delegate_task` suporta até 3 chamadas paralelas. A janela deslizante maximiza utilização: enquanto tasks longas rodam, tasks curtas não ficam bloqueadas atrás delas.
- **Alternativa Rejeitada:** Spawn sequencial (uma task por vez). Rejeitada — subutiliza o paralelismo disponível e estica desnecessariamente o tempo total de execução.

### ADR-003: Política de retry com contexto enriquecido

- **Decisão:** 3 tentativas por task. A cada retry, o subagente recebe o erro da tentativa anterior no contexto. Após 3 falhas, escala para o humano e pausa apenas a sub-árvore dependente.
- **Justificativa:** Muitos erros são transientes (race condition, timeout de rede, modelo instável). O contexto enriquecido permite que o subagente corrija o próprio erro na tentativa seguinte. 3 tentativas é um sweet spot — mais que isso raramente resolve sem intervenção humana. Pausar apenas a sub-árvore (não a feature inteira) mantém tasks independentes rodando.
- **Alternativa Rejeitada:** Retry infinito até sucesso. Rejeitada — bloqueia a pipeline indefinidamente em erros não recuperáveis.

### ADR-004: Validação de evidência antes de marcar `[x]`

- **Decisão:** O orchestrator não confia cegamente no report `DONE` do subagente. Verifica: arquivos listados em `Arquivos` existem? Smoke-test passou (exit code 0)? Se não, rejeita o DONE e trata como falha.
- **Justificativa:** Subagentes podem reportar DONE por engano (alucinação, crash parcial, escrita em path errado). A validação é barata (stat + grep) e previne falsos positivos que corromperiam o DAG.
- **Alternativa Rejeitada:** Confiança cega no report do subagente. Rejeitada — um falso DONE destrava tasks dependentes que vão falhar em cascata.

### ADR-005: Spawn failure de infra → aborta feature inteira

- **Decisão:** Se um subagente não chega a spawnar (API key inválida, rate limit, Hermes Agent fora do ar), o orchestrator aborta a feature inteira imediatamente. Não aplica retry.
- **Justificativa:** Falha de infraestrutura é qualitativamente diferente de falha de lógica. Retry em erro de auth ou rate limit é inútil e desperdiça tentativas. Abortar com erro claro evita que o usuário espere 3x30min por um timeout que nunca vai resolver.
- **Alternativa Rejeitada:** Tratar spawn failure como erro comum (entra no ciclo de retry). Rejeitada — viola o spec que explicitamente lista este edge case como abort.

## 4. Auditoria de Constituição

- [ ] Constitution.md está vazio — nenhuma regra para auditar.
