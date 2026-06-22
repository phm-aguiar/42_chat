---
title: AgentOps — Observability Platform para AI Agents
tags:
  - agentops
  - observability
  - cost-tracking
  - LLM
  - monitoring
  - evaluation
summary: >-
  Plataforma open-source (MIT) de observabilidade, monitoramento e debugging
  para AI Agents. Rastreia custos de LLM, sessões, execução de ferramentas e
  métricas multi-agente, com painel SaaS + self-host.
status: approved
lifecycle: reviewed
created: 2026-06-21
rag_score: 0.5
sources:
  - https://github.com/AgentOps-AI/agentops
  - https://docs.agentops.ai/introduction
---

# AgentOps — Observability Platform para AI Agents

## Visão Geral

AgentOps é uma plataforma open-source (MIT ~13k stars) de observabilidade para AI Agents.
Ajuda a construir, avaliar e monitorar agents do protótipo à produção, com foco em:

- **LLM Cost Management** — rastreio de gastos por provider/modelo
- **Session Replays** — grafo de execução passo-a-passo
- **Debugging** — análise de latência, erros, loops infinitos
- **Multi-Agent Visualization** — interações entre agents
- **API Bill Tracking** — controle de custos reais de API

## Arquitetura

```
pip install agentops
```

```
import agentops

agentops.init("<API_KEY>")    # início do programa
# ... LLM calls ...
agentops.end_session('Success')  # fim da sessão
```

Modelo: **2 linhas de código** para instrumentar qualquer agent Python.
Cada LLM call é interceptada automaticamente, gerando métricas de:

- Tokens de input/output
- Modelo usado
- Latência
- Custo estimado (baseado em tabela de preços interna)
- Tags customizadas

## Integrações

| Framework | Instalação | Observações |
|-----------|-----------|-------------|
| **OpenAI Agents SDK** | `pip install openai-agents` | Python + TypeScript |
| **CrewAI** | `pip install 'crewai[agentops]'` | Auto-detect via env var |
| **AG2 (AutoGen)** | `pip install ag2 agentops` | 2 linhas |
| **LangChain** | `pip install agentops[langchain]` | Callback handler |
| **LlamaIndex** | `pip install llama-index-instrumentation-agentops` | `set_global_handler("agentops")` |
| **LiteLLM** | `pip install agentops litellm` | Usar `litellm.completion()` |
| **Anthropic** | `pip install anthropic agentops` | Sync/Async/Streaming |
| **Mistral** | `pip install mistralai agentops` | Sync/Async/Streaming |
| **Cohere** | `pip install cohere agentops` | Sync/Stream |
| **Llama Stack** | `pip install llama-stack-client agentops` | Cliente Python |
| **SwarmZero** | `pip install swarmzero agentops` | Multi-agent |
| **Camel AI** | `pip install camel-ai agentops` | ChatAgent |

## Como Funciona o Cost Tracking

AgentOps usa **tabelas de preço internas** por modelo para estimar custo real:

1. **Intercepta** cada chamada LLM via monkey-patching dos SDKs suportados
2. **Extrai** model name, input tokens, output tokens da resposta
3. **Calcula** custo: `input_tokens * input_price + output_tokens * output_price`
4. **Acumula** por sessão, por modelo, por tag
5. **Exibe** no dashboard com breakdown por sessão, custo total, custo por agente

Tabela de preços embutida (~400+ modelos conhecidos):
- OpenAI (GPT-4o, GPT-4, GPT-3.5)
- Anthropic (Claude 3/4 Opus, Sonnet, Haiku)
- Google (Gemini 1.5/2.0)
- Mistral, Cohere, e centenas de open-source via LiteLLM

## Decorators (Span Hierarchy)

```python
from agentops.sdk.decorators import session, agent, operation, task, workflow

@session          # Root span
@agent            # Agent operations
@operation/@task  # Specific operations
@workflow         # Multi-operation workflow
```

Todos suportam: input/output recording, exception handling, async/await, generators, custom attributes.

## Self-Hosting

O app AgentOps (dashboard + API backend) é open-source:
- `app/README.md` no repositório
- Docker Compose para deploy local
- Alternativa ao SaaS (app.agentops.ai)

## Roadmap Relevante

| Funcionalidade | Status | Descrição |
|---------------|--------|-----------|
| LLM Cost Management | ✅ | Rastreio de gastos por provider |
| Session Replays | ✅ | Grafo de execução |
| Custom Eval Metrics | ✅ | Métricas customizadas |
| API Bill Tracking | ✅ | Controle de custos reais |
| Honeypot/Prompt Injection | ✅ | Via PromptArmor |
| Evaluation Builder API | 🚧 | Builder de avaliações |
| Agent Scorecards | 🔜 | Scorecards padronizados |
| CI/CD Integration | 🔜 | Checks de regressão |

## Relação com o 42_Framework

O 42_Framework tem:
- **LATTE Hardening (Feature 005)**: Budget tracking por número de LLM calls (`max_llm_calls`), timeout, force_finalize
- **LATTE Metrics**: Estimativa heurística de tokens (~2000 tokens/entrada de histórico)
- **Sem custo real em dólar**: A métrica `tokens_consumed` é estimada, não real

O AgentOps complementa:
- **Estimativa → real**: Substitui heurística por contagem real de tokens e preço por modelo
- **Budget por call → Budget por custo real**: Adiciona budget em dólar
- **Dashboard nativo**: Painel SaaS ou self-host com drilling por sessão
- **Multi-provider**: LiteLLM + AgentOps cobre 100+ providers vs. suporte manual

## Referências

- Repo: https://github.com/AgentOps-AI/agentops
- Docs: https://docs.agentops.ai/introduction
- Dashboard: https://app.agentops.ai
- Integração LiteLLM: https://docs.agentops.ai/v1/integrations/litellm
- Self-Hosting: `app/README.md` no repositório
