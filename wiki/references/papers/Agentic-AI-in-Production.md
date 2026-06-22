---
title: "Agentic AI in Production — Tool-Calling, Planning, Recovery"
tags: [paper, agentic-ai, tool-calling, planning, error-recovery, observability, production-patterns]
status: analyzed
created: 2026-06-21
rag_score: 0.5
source: "https://www.kalviumlabs.ai/blog/agentic-ai-in-production-tool-calling-planning-recovery/"
authors: "Anil Gulecha (Kalvium Labs)"
base_confidence: 0.95
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
summary: "6 sistemas agentic em produção. 23 falhas depuradas, 4 padrões de falha (malformed tool calls, infinite loops, error cascades, context overflow). Tool design com schemas tight (14% → 2.1% falha), planning loops com hard limits em código, error recovery tipado, e observabilidade com session traces."
---

# Agentic AI in Production: Tool-Calling, Planning, Recovery

> 6 sistemas agentic em produção, 23 falhas depuradas, 4 padrões de falha. O que quebrou e como consertaram — schemas tight, loops com hard limits, recovery tipado, e tracing.

## Resumo

Artigo do Kalvium Labs documentando 6 sistemas de AI agentic em produção. Após depurar 23 falhas em deployments de clientes, identificaram 4 padrões que respondem por quase todas: tool calls malformados (schemas frouxos), loops infinitos de planejamento, cascatas de erro, e estouro de contexto. O artigo detalha soluções de engenharia testadas em produção: schemas JSON com constraints de máquina (`enum`, `format`, `minimum`/`maximum`), limites de step em código (não no system prompt), taxonomia de erro tipada com recovery automático por tipo, e tracing completo de sessão (mensagens + tool inputs/outputs + custo por step).

## Principais Contribuições

### 1. Tool-Calling Design Robusto

**Schemas tight vs loose**: Com schemas abertos (`"filters": {"type": "object"}`), 14% dos tool calls falhavam validação em produção. Após adicionar constraints de máquina — `enum` para valores permitidos, `format: "date"` para datas ISO 8601, `minimum`/`maximum` para ranges numéricos — a taxa de falha caiu para 2.1%. Descriptions são hints, não guardrails; o modelo ignora constraints descritivas quando conflitam com o que acha que o usuário quer.

**Idempotência para writes**: Qualquer tool que modifica estado precisa de idempotency key (`uuid4()`). Cenário crítico: tool call sucede no servidor mas rede cai antes da resposta → agente vê timeout → retry sem idempotency cria duplicata. Padrão ausente na maioria das codebases revisadas.

**Resultados estruturados**: Retornar objetos (com `count`, `records[]`, campos tipados) em vez de strings. O modelo referencia `records[0].id` diretamente, sem precisar interpretar "the first one was John Smith" de prosa inconsistente. Crítico em sessões com 12+ steps onde o contexto está saturado.

### 2. Arquiteturas de Planejamento com Limites

**Loops com hard limits em código**: `MAX_PLANNING_STEPS` e `MAX_TOOL_CALLS` no loop do agente, não no system prompt. Ajustar por complexidade da tarefa: 5 steps para data retrieval simples, 20 para research agent multi-source. Logar toda sessão que atinge o limite como sinal de task complexa demais ou loop em subtask específica.

**Planejamento hierárquico**: Para tasks com 10+ passos, um planner model gera plano estruturado (JSON schema, sem tools), depois executor roda cada step com contexto focado e tool set escopado. Vantagens: contexto enxuto por executor, menos tool calls alucinados, steps required vs optional explícitos. Tradeoff: +1 model call de latência/custo.

**Completion criteria testáveis em código**: Não confiar no senso de "done" do modelo. Validar `required_output_keys` + `validation_fn` programática (ex: `isinstance(records, list) and count == len(records)`). Para code-writing agents: syntax check + test cases passam.

### 3. Error Recovery Tipado (Não Cascateia)

**Taxonomia de erro em 6 tipos**: `TRANSIENT` (retry com backoff exponencial), `INVALID_INPUT` (retorna ao modelo com contexto, sem retry cego), `PERMISSION` (escala para humano), `NOT_FOUND` (roteia alternativa ou falha graciosa), `RATE_LIMIT` (retry após delay), `FATAL` (para o agente).

**Infraestrutura lida com transient, modelo não vê**: Retries e rate limits são resolvidos na infra sem surfar ao modelo. O modelo só recebe resultado final ou erro estruturado após exaustão de retries. Mantém o contexto limpo e evita que o modelo "aprenda" com a narrativa de erro.

**Checkpoint-based session recovery**: Salvar `AgentCheckpoint` (messages, completed_steps, timestamp) após cada step completo. Permite resumir sessão de 20 passos que falhou no step 14 a partir do 13, sem reiniciar do zero. Usado para batch agents (30-120s); overhead de storage não vale para real-time chat agents.

### 4. Observabilidade: Tracing Completo

**Session trace como estrutura de dados**: `ToolCallTrace` (tool_name, input_params, output, error, latency_ms, attempt_number) → `StepTrace` (step_number, input_tokens, output_tokens, tool_calls[], latency_ms, cost_usd) → `SessionTrace` (session_id, task, steps[], outcome, total_cost, total_latency).

Sem trace, debugar agente é arqueologia. Com trace: puxa sessão específica, encontra o step onde o raciocínio divergiu, identifica schema problem, planning limit ou system prompt issue.

**Ferramentas open-source**: LangSmith (bom no ecossistema LangChain), Braintrust (mais model-agnostic). Time construiu formato próprio em 2 dias para integração com cost tracking e para lidar com diferenças de estrutura de mensagens entre Anthropic e OpenAI.

**Parallel tool calls**: Logar batch paralelo como single step com múltiplos `ToolCallTrace` entries. Achatar em sequencial corrompe dados de timing.

## Aplicação no 42_Framework

### Gaps Endereçáveis

| Área | Padrão do Artigo | Status no 42_Framework |
|------|-----------------|----------------------|
| **Tool schemas** | Constraints de máquina (`enum`, `format`, `min`/`max`) | ⚠️ Tools definidos com descriptions, sem validação machine-enforceable |
| **Step limits** | `MAX_PLANNING_STEPS` e `MAX_TOOL_CALLS` em código | ⚠️ max-rounds=40 no LATTE, sem distinction tool vs planning |
| **Error taxonomy** | 6 tipos com recovery automático por tipo | ❌ Sem taxonomia; heartbeat detecta inatividade mas não classifica erros |
| **Idempotency** | idempotency_key em todo write | ❌ Não implementado; risco de duplicatas em retry |
| **Completion criteria** | Validação programática de done | ⚠️ Depende do modelo declarar done, sem check externo |
| **Session tracing** | Trace completo com custo por step | ❌ Logging textual, sem estrutura de trace |
| **Hierarchical planning** | Planner + executor por step | ❌ Apenas flat ReAct via LATTE coordination graph |
| **Checkpointing** | Resume de step N após crash | ❌ G_t só em memória (ADR-002) |

### Ações Sugeridas

1. **Hardening de tool schemas** (Feature 005): Adicionar `enum`, `format`, `minimum`/`maximum` nas definições de tools do framework. Meta: reduzir tool call failures de ~14% para <3%.
2. **Error taxonomy + recovery**: Implementar `ErrorType` enum com 6 tipos e handler automático. Transient errors resolvidos na infra sem poluir contexto do modelo.
3. **Step budget enforcement**: Separar `max_planning_steps` de `max_tool_calls` no LATTE coordination loop. Force-finalize com resultado parcial ao atingir limite.
4. **Session tracing**: Estrutura `SessionTrace` com tool calls, tokens, custo e latência por step. Essencial para debugging de produção.
5. **Idempotency keys**: Adicionar `idempotency_key` automático em toda operação de write. Prevenir duplicatas em retry pós-timeout.

## Relacionado

- [[references/papers/LangGraph-vs-LangChain|LangGraph vs LangChain]] — decision matrix para frameworks
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — state pruning, checkpointing, iteration limits
- [[references/papers/Multi-Agent-Systems-in-Production|Multi-Agent Systems in Production]] — failure propagation, cost explosion, timeout decorator
- [[references/papers/Building-AI-Agents-Architecture|Building AI Agents Architecture]] — framework choice, model selection, eval infra
- [[projects/42_Framework/features/005-latte-hardening|Feature 005: LATTE Hardening]] — alvo dos gaps de tool schema e error recovery
