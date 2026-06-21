# Plano Arquitetural: Agent Dev (feature 006)

## 1. Metadados do Plano
- **Stack Tecnológico:** Hermes Agent (runtime), Python (skills), YAML (config), Markdown (specs)
- **Feature Fonte:** `specs/features/006-agent-dev/spec.md`
- **Escopo:** Definir a persona do agente Dev como subagente leaf do orchestrator — identidade, ciclo de trabalho e contrato de comunicação — com skills plugáveis por stack

## 2. Design de Contratos e Fronteiras

### Contrato com o Orchestrator (entrada)
- `delegate_task(goal, context, toolsets=["terminal", "file"])`
- Contexto inclui: spec relevante, ADRs do plan, task atômica, skills da stack, tentativa N/3
- Se contexto vazio ou sem spec/plan/task → FAIL imediato: "Contexto insuficiente: faltam spec, plan ou task"

### Contrato com o Orchestrator (saída)
- **DONE:** diff/arquivos criados + smoke-test output + rastreabilidade spec→código ("Função X atende requisito Y da spec, seção Z")
- **FAIL:** stack trace + arquivo e linha do erro + possível causa
- **BLOCKED:** pergunta específica sobre ambiguidade na spec (nunca infere)

### Convenção de diretórios
```
.hermes/agents/agent-dev/
├── AGENT.md          # Persona, tom, ciclo de trabalho
└── context.yaml      # Toolsets, timeout, configuração
```

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-1: Agente Hermes nativo (AGENT.md + context.yaml)
- **Decisão:** Implementar como agente Hermes padrão, invocável via `agent-run`
- **Justificativa:** Mesmo padrão arquitetural do `onboard` e `agent-orchestrator`. `agent-run` compila contexto limpo (sem corrosão de sessão). Zero dependências externas — o Hermes Agent já provê `delegate_task`, `terminal`, `file`
- **Alternativa Rejeitada:** Script Python standalone com subprocess — adiciona complexidade de infra (processo separado, autenticação, estado persistente) sem ganho real sobre o que o Hermes já oferece nativamente

### ADR-2: Skills como parâmetro de entrada, não hardcoded
- **Decisão:** Skills de implementação por stack (`go-implement`, `python-implement`, `smoke-check`) são injetadas pelo orchestrator no contexto, não embutidas no AGENT.md
- **Justificativa:** Permite multi-stack sem reescrever o agente. O orchestrator lê `tech.md`, seleciona as skills apropriadas e injeta no contexto. Skills são **trilhos, não jaulas** — templates e convenções que guiam sem matar criatividade. O agente funciona sem skills (modo "força bruta")
- **Alternativa Rejeitada:** Skills hardcoded no AGENT.md — acopla stack à persona. Cada nova linguagem exige reescrever o agente, violando o princípio de que o framework é multi-stack

### ADR-3: Comunicação via relatório textual (DONE/FAIL/BLOCKED)
- **Decisão:** Subagente leaf se comunica exclusivamente via relatório de conclusão textual com status explícito (DONE, FAIL, BLOCKED)
- **Justificativa:** Subagentes leaf não têm acesso a `clarify()` — a comunicação é assíncrona via relatório. O orchestrator interpreta o status e age: DONE → marca `[x]` e libera dependentes; FAIL → retry com contexto enriquecido; BLOCKED → escala pro humano
- **Alternativa Rejeitada:** Callbacks ou sistema de eventos — adiciona complexidade desnecessária para leaf agents que têm ciclo de vida curto (uma task por spawn)

### ADR-4: Nunca inferir — reportar BLOCKED
- **Decisão:** Ambiguidades na spec resultam em BLOCKED com pergunta específica, nunca em inferência silenciosa
- **Justificativa:** Alinhado com `constitution.md`: "Nunca implemente sem spec aprovada". Ambiguidades na spec são bugs da spec, não do agente. Inferências erradas custam mais caro (retrabalho, debug) do que BLOCKEDs (pergunta rápida)
- **Alternativa Rejeitada:** Inferência com flag de confiança — complexo de implementar, difícil de auditar, e viola o princípio fundamental do SDD de que a spec é a fonte da verdade

## 4. Auditoria de Constituição

- [x] **Validação SDD obrigatória** — O agent-dev só implementa tasks de specs com `Aprovado: true` (gate gerenciado pelo orchestrator, feature 005)
- [x] **Aprovação humana** — O orchestrator verifica `Aprovado: true` antes de spawnar. O agent-dev nunca toma decisões arquiteturais (BLOCKED quando spec ambígua)
- [x] **Smoke test** — Ciclo de trabalho inclui smoke-test obrigatório antes de reportar DONE (critério de sucesso #10 do spec)
- [x] **Agentes versionados** — AGENT.md e context.yaml em `.hermes/agents/agent-dev/`, versionados no repo. Symlink em `~/.hermes/agents/`
- [x] **Pipeline imutável** — O agent-dev é etapa 5 do pipeline SDD (orchestrator spawna → Dev implementa). Não cria atalhos nem pula etapas
- [x] **Isolamento de agentes** — Subagente leaf via `delegate_task`. Não pode delegar (profundidade máxima = 1). Contexto compilado limpo pelo `agent-run`
- [x] **Framework primeiro, app depois** — Feature 006 é parte do framework SDD, não do app de chat 42_chat
- [x] **Specs são do framework** — A spec 006 descreve capacidade do framework (agente implementador), não funcionalidade de chat
- [x] **Knowledge management é first-class** — Decisões de design do agent-dev serão documentadas no vault Obsidian após implementação
- [x] **Nunca implementar sem spec aprovada** — Alinhado via ADR-4: BLOCKED quando spec ambígua, nunca infere
- [x] **Corrosão de contexto** — `agent-run` compila contexto limpo. Subagente não recebe histórico de sessões anteriores
- [x] **Agentes que delegam** — Leaf agent. Profundidade máxima = 1 (orchestrator → Dev, sem netos). Max spawn depth do Hermes = 1
- [x] **Skills fora do padrão** — Skills injetadas seguem formato Hermes (SKILL.md com frontmatter YAML). O agent-dev espera esse formato
- [x] **Ferramentas inventadas** — Toolsets `terminal` + `file` apenas (definido no `context.yaml`). Sem invenção de APIs ou imports
