---
title: "Building AI Agents — Architecture, Trade-offs, and What We've Learned"
tags: [paper, ai-agents, architecture, langchain, tool-design, model-selection, evaluation, production-patterns]
status: analyzed
created: 2026-06-21
rag_score: 0.5
source: "https://www.kalviumlabs.ai/blog/building-ai-agents-architecture-tradeoffs/"
authors: "Anil Gulecha (Kalvium Labs)"
base_confidence: 0.95
provenance:
  extracted: 0.90
  inferred: 0.05
  ambiguous: 0.05
summary: "Decisões de arquitetura em agentes AI de produção. LangChain abandonado após 3 projetos — abstração custa mais que conveniência. Claude 3.5 Sonnet como default, tool design como decisão mais subestimada, e eval infra antes do agente. 3 erros comuns cometidos e corrigidos."
---

# Building AI Agents: Architecture, Trade-offs, and What We've Learned

> LangChain abandonado após o 3º projeto. Claude 3.5 Sonnet como default. Tool design > model selection. Eval infra antes do agente. O que realmente funciona em produção.

## Resumo

Artigo do Kalvium Labs documentando a jornada de arquitetura em sistemas de AI agents para clientes em compliance, analytics, content generation e customer support. Decisões que mudaram entre projetos: LangChain foi abandonado para produção após o 3º sistema (abstração custa mais que conveniência), Claude 3.5 Sonnet estabelecido como modelo default (melhor instruction following e tool-calling accuracy), tool design como decisão mais subestimada (5-8 tools bem desenhadas superam 15-20 mal desenhadas), e infraestrutura de avaliação construída antes do agente (dataset de 50-100 test cases, métricas de completion rate, tool accuracy, step efficiency, latency p50/p95, cost per task).

## Principais Contribuições

### 1. Framework Choice: Por Que LangChain Foi Abandonado

**LangChain otimiza para demo em 30min, produção precisa de outras coisas**: observabilidade, error recovery, deterministic tool routing, e capacidade de debugar por que o agente tomou uma decisão específica às 3am.

**Três problemas críticos**:
- **Debugging doloroso**: Erro simples ("model returned JSON in wrong format") vira stack trace de 40 linhas atravessando múltiplas camadas de abstração.
- **Instabilidade de versão**: API muda significativamente entre 0.1.x e 0.2.x. Dependency instability é liability em produção.
- **Custo de abstração**: Wrappers que adicionam method overhead sem adicionar confiabilidade. Para 500 requests/dia, você quer saber exatamente o que está sendo enviado à API.

**Solução: custom loop minimalista** (~30 linhas): loop explícito com `llm.chat(messages, tools=tools)`, tool execution direta, logging por step (input, output, latency). Vantagens: zero hidden abstractions, error handling explícito, fácil adicionar guardrails, rate limiting, cost tracking. Custo de setup: 2-4 horas extras, paga em debugging às 3am.

**Quando ainda usar LangChain**: protótipos, ferramentas internas, agentes com lógica simples onde overhead de abstração não importa.

### 2. Model Selection Baseada em Dados de Produção

| Use Case | Modelo | Por Quê |
|----------|--------|---------|
| Interactive agent (default) | Claude 3.5 Sonnet | Melhor instruction following + tool use |
| Structured data extraction | GPT-4o (structured output) | JSON válido garantido, sempre |
| Batch document processing | Llama 3.1 70B | 10x redução de custo |
| Simple classification | Claude Haiku / GPT-4o-mini | Rápido + barato para tarefas simples |
| Code generation within agents | Claude 3.5 Sonnet | Qualidade de código superior |

**Claude 3.5 Sonnet** vence em: instruction following multi-step, tool-calling accuracy (menos malformed calls), context utilisation (usa informação de earlier turns), custo competitivo com GPT-4o.

**GPT-4o** quando structured output é hard requirement: populate databases, generate reports, typed API integration. JSON schema → JSON válido, toda vez.

**Open-source** (Llama 3.1 70B, Mixtral) para batch: 80-90% da qualidade a 10-20% do custo. Não usar para interactive agents — gap de latência e confiabilidade ainda importa.

### 3. Tool Design: A Decisão Mais Subestimada

> "A well-designed tool with a mediocre model outperforms a poorly-designed tool with the best model. Every time."

**4 princípios**:
1. **One tool = one action**: `manage_database` (CRUD) confunde o modelo. Quatro tools separadas (`create_record`, `get_record`, `update_record`, `delete_record`) funcionam melhor.
2. **Nomes e parâmetros descritivos**: `search_knowledge_base(query: str, max_results: int)` > `search(q: str, n: int)`. O modelo lê nome e description para decidir quando usar.
3. **Erros estruturados, não stack traces**: "No records found matching that query. Try broadening the search terms." → mensagem que o modelo pode usar para recovery.
4. **Limitar o tool set**: 5-8 tools significativamente outperform 15-20 tools, mesmo quando o set maior é tecnicamente mais capaz.

**Caso real — Compliance Agent**: 5 tools (`search_call_transcripts`, `get_compliance_rules`, `score_compliance`, `generate_report`, `flag_violation`) lidam com análise de compliance em milhares de calls. Adicionar `summarize_call` ou `compare_agents` degradou performance — o modelo usava-as desnecessariamente.

### 4. Evaluation Infrastructure: Construir Antes do Agente

**Dataset de 50-100 test cases** por agente antes do deployment:
```json
{
  "task": "Find all compliance violations for Agent Smith in March 2026",
  "expected_tools": ["search_call_transcripts", "get_compliance_rules", "score_compliance"],
  "expected_output_contains": ["violation", "Smith", "March"],
  "max_acceptable_steps": 5,
  "max_acceptable_latency_ms": 8000
}
```

**Métricas tracked**: task completion rate, tool accuracy (chamou tools certas com parâmetros certos?), step efficiency (quantos steps vs mínimo necessário), latency p50/p95, cost per task (API costs totais), failure modes (model error, tool error, ambiguous input, max steps exceeded).

**Regra de ouro**: mudou o prompt? Roda eval. Trocou de modelo? Roda eval. Adicionou tool nova? Roda eval. Sem baseline, você está chutando. E em AI de produção, chutar é caro.

### 5. Erros Comuns (Cometidos e Corrigidos)

1. **System prompt sobrecarregado**: 3,000 palavras tentando cobrir todo edge case underperform 500 palavras com: role statement (2 frases) + tool usage guidelines (1 parágrafo) + output format (1 exemplo) + explicit constraints ("Never do X").

2. **Não tratar falhas parciais**: Quando um tool call falha em sequência multi-step, agente frequentemente alucina resultado ou entra em retry loop. Solução: fallback explícito — se `search_call_transcripts` retorna zero resultados, agente diz ao usuário, não tenta 5 reformulações de query.

3. **Ignorar custo**: Agente complexo (8 tool calls/query) pode custar $0.50-$2.00/interação. A 1,000 queries/dia = $500-$2,000/dia. Solução: cost budgets por task, tracking desde day one, modelos baratos para routing decisions simples.

## Aplicação no 42_Framework

### Gaps Endereçáveis

| Área | Padrão do Artigo | Status no 42_Framework |
|------|-----------------|----------------------|
| **Framework** | Custom loop minimalista sobre LangChain | ✅ 42_Framework é custom, não usa LangChain |
| **Model selection** | Matriz por use case (Sonnet default, GPT-4o structured, Llama batch) | ⚠️ Modelo fixo por configuração, sem routing por task type |
| **Tool design** | One tool = one action, 5-8 tools, nomes descritivos | ⚠️ Tools tendem a ser multifuncionais; sem limite explícito de tool count |
| **Eval infra** | Dataset 50-100 cases, 6 métricas, rodar a cada change | ❌ Sem eval dataset automatizado; testes manuais |
| **Cost tracking** | Cost budget por task, tracking desde day one | ❌ Sem cost tracking; LLM calls não contabilizadas |
| **System prompt** | 500 palavras máximo, role + guidelines + exemplo + constraints | ⚠️ Prompts longos sem otimização de tamanho |
| **Partial failures** | Fallback explícito, sem retry loop cego | ⚠️ Retry sem estratégia de escape |

### Ações Sugeridas

1. **Model routing por task type**: Implementar matriz de seleção — Claude Sonnet para planning/interactive, GPT-4o para structured output, Llama para batch. Feature candidate para otimização de custo.
2. **Tool set audit**: Revisar tools do framework — garantir one action per tool, nomes descritivos, limitar a 5-8 tools por agente. Tool count ceiling como constraint de design.
3. **Eval dataset**: Criar dataset de 50-100 test cases para o 42_Framework cobrindo expected tools, output characteristics, max steps, max latency. Integrar no CI/CD.
4. **Cost tracking**: Adicionar `total_cost_usd` no state do agente, calcular após cada LLM call, enforce budget limits ($0.50 soft, $2.00 hard).
5. **System prompt compression**: Auditar prompts atuais, reduzir para ~500 palavras com estrutura Role → Guidelines → Example → Constraints.

## Relacionado

- [[references/papers/LangGraph-vs-LangChain|LangGraph vs LangChain]] — aprofundamento na decisão framework vs custom
- [[references/papers/Agentic-AI-in-Production|Agentic AI in Production]] — tool-calling design, error recovery, observability
- [[references/papers/Multi-Agent-Systems-in-Production|Multi-Agent Systems in Production]] — quando single agent não basta, cost explosion
- [[references/papers/LangGraph-in-Production|LangGraph in Production]] — state management, checkpointing, human-in-the-loop
- [[projects/42_Framework/features/005-latte-hardening|Feature 005: LATTE Hardening]] — tool schema hardening, error taxonomy
