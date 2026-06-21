# Plano Arquitetural: Agent QA (feature 007)

## 1. Metadados do Plano
- **Stack Tecnológico:** Hermes Agent (runtime), Python (skills), YAML (config), Markdown (specs)
- **Feature Fonte:** `specs/features/007-agent-qa/spec.md`
- **Escopo:** Definir a persona do agente QA como subagente leaf do orchestrator — identidade, ciclo de validação e contrato de comunicação — com skills de teste plugáveis por stack

## 2. Design de Contratos e Fronteiras

### Contrato com o Orchestrator (entrada)
- `delegate_task(goal, context, toolsets=["terminal", "file"])`
- Contexto inclui: spec relevante, código implementado pelo Dev (paths + diffs), task atômica,
  skills de teste da stack, tentativa N/3
- Se contexto vazio ou sem spec/código → FAIL imediato

### Contrato com o Orchestrator (saída)
- **DONE:** todos os testes passam + lint limpo + cobertura OK + arquivos de teste criados
- **REJECTED:** teste quebrado, lint warning, ou cobertura abaixo do threshold — com evidência
  completa (nome do teste, arquivo, linha, output). Força re-spawn do Dev
- **BLOCKED:** spec ambígua OU skill não cobre o necessário (nunca infere, nunca busca web)

### Contrato com o Agent-Dev (via Orchestrator)
- QA rejeita → orchestrator re-spawna Dev com contexto enriquecido: "QA rejeitou: <evidência>"
- Ciclo de retry: máx 3 rejeições → escala pro humano
- QA não julga se a falha é culpa do Dev ou pré-existente

### Convenção de diretórios
```
.hermes/agents/agent-qa/
├── AGENT.md          # Persona, tom, ciclo de validação
└── context.yaml      # Toolsets, timeout, configuração
```

## 3. Decisões Arquiteturais e Justificativas (ADR)

### ADR-1: Agente Hermes nativo (AGENT.md + context.yaml)
- **Decisão:** Implementar como agente Hermes padrão, invocável via `agent-run`
- **Justificativa:** Mesmo padrão arquitetural do `onboard`, `agent-orchestrator` e `agent-dev`.
  `agent-run` compila contexto limpo sem corrosão de sessão. Zero dependências externas
- **Alternativa Rejeitada:** Script standalone — adiciona complexidade sem ganho sobre o Hermes

### ADR-2: Skills de teste como parâmetro de entrada, não hardcoded
- **Decisão:** Skills de teste (`gherkin-scenarios`, `go-unit-tests`, `local-test-runner`) são
  injetadas pelo orchestrator no contexto, não embutidas no AGENT.md
- **Justificativa:** Permite multi-stack sem reescrever o agente. Mesmo padrão do agent-dev (006).
  Skills são **trilhos, não jaulas**. Se não cobrem → BLOCKED
- **Alternativa Rejeitada:** Skills hardcoded — acopla stack à persona, viola multi-stack

### ADR-3: Três status de saída: DONE, REJECTED, BLOCKED
- **Decisão:** QA introduz um terceiro status além de DONE/FAIL: REJECTED
- **Justificativa:** REJECTED é semanticamente diferente de FAIL. FAIL = "não consegui executar"
  (erro de infra). REJECTED = "executei e encontrei problemas" (erro de qualidade).
  O orchestrator trata diferente: FAIL → retry do QA; REJECTED → retry do Dev
- **Alternativa Rejeitada:** Usar FAIL para tudo — perde semântica, orchestrator não sabe
  se o problema é no QA ou no Dev

### ADR-4: Sem acesso web — terminal + file apenas
- **Decisão:** Toolsets restritos a `terminal` + `file`. Sem `web_search` ou `browser`
- **Justificativa:** Acesso web aumenta superfície de alucinação e overengineering.
  Skills são os trilhos — se não cobrem, BLOCKED. Isso mantém o QA dentro do microcontexto
  e evita que ele tente "resolver" problemas em vez de "reportar" problemas
- **Alternativa Rejeitada:** QA com acesso web — risco de alucinação e fuga do escopo

### ADR-5: Não julga causa de falha
- **Decisão:** QA reporta tudo que encontra, sem decidir se o problema é do Dev ou pré-existente
- **Justificativa:** Separar detecção de julgamento. O orchestrator (ou humano) decide o que
  fazer com a evidência. QA é detector, não juiz
- **Alternativa Rejeitada:** QA filtrar falsos positivos — adiciona complexidade de julgamento
  que pode mascarar problemas reais

### ADR-6: Persona molde — skills de teste são features separadas
- **Decisão:** Feature 007 entrega apenas a persona (AGENT.md + context.yaml).
  Skills de teste (`gherkin-scenarios`, `go-unit-tests`, `local-test-runner`) são
  features separadas, a serem desenvolvidas com base em padrões da comunidade
- **Justificativa:** Mesmo padrão do agent-dev (006). Separa persona de capacidades.
  Permite evoluir as skills independentemente, baseado em pesquisa
- **Alternativa Rejeitada:** Feature monolítica com persona + skills — acopla entrega,
  atrasa o molde, e as skills ficariam obsoletas rapidamente

## 4. Auditoria de Constituição

- [x] **Validação SDD obrigatória** — QA só valida specs com `Aprovado: true` (gate gerenciado pelo orchestrator)
- [x] **Aprovação humana** — Orchestrator verifica `Aprovado: true` antes de spawnar
- [x] **Smoke test** — QA executa testes como parte do ciclo; smoke test real exigido
- [x] **Vault Obsidian fiel** — Após implementação, documentar QA no vault (`wiki-ingest` + `wiki-lint`)
- [x] **Agentes versionados** — AGENT.md e context.yaml em `.hermes/agents/agent-qa/`, versionados
- [x] **Skills versionadas** — Skills de teste serão versionadas em `.hermes/skills/`
- [x] **Pipeline imutável** — QA é etapa do pipeline (orchestrator → Dev → QA)
- [x] **Isolamento de agentes** — Leaf, não delega. Contexto compilado limpo
- [x] **Framework primeiro, app depois** — Feature 007 é parte do framework
- [x] **Specs são do framework** — Spec 007 descreve capacidade do framework
- [x] **Knowledge management first-class** — Vault será atualizado após implementação
- [x] **Nunca implementar sem spec aprovada** — QA valida specs aprovadas; BLOCKED se ambígua
- [x] **Corrosão de contexto** — `agent-run` compila contexto limpo
- [x] **Agentes que delegam** — Leaf agent, profundidade máxima = 1
- [x] **Skills fora do padrão** — Skills seguem formato Hermes (SKILL.md + frontmatter)
- [x] **Ferramentas inventadas** — Toolsets `terminal` + `file` apenas
- [x] **Vault desatualizado** — Vault será atualizado após feature implementada
