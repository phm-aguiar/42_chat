# Auditoria de Skills por Subagente

> **Feature:** 008-reavaliacao-skills
> **Objetivo:** Mapear quais skills cada subagente realmente referencia, para guiar a consolidação baseada em uso real (ADR-5 do plan.md).
> **Data da auditoria:** 2026-06-19

---

## Metodologia

Para cada agente, foram inspecionados dois arquivos:

- **`context.yaml`**: campo `skills:` (carregamento hard, direto no contexto de spawn) e campo `toolsets` (presença de `skills` como toolset).
- **`AGENT.md`**: menções explícitas a nomes de skills no texto do prompt (referências soft) e instruções de `skill_view()`.

**Classificação de referências:**

| Tipo | Significado |
|------|-------------|
| `hard` | Campo `skills:` no `context.yaml` — carregada automaticamente no spawn |
| `soft` | Mencionada no texto do `AGENT.md` como skill esperada (mas sem carregamento automático) |
| `conditional` | Carregada apenas em modo fallback ou "se disponível" |
| `toolset` | Agente tem acesso ao toolset `skills` (pode chamar `skill_view()` sob demanda) |

---

## 1. agent-dev

### context.yaml

```yaml
toolsets:
  - terminal
  - file
```

- **Campo `skills:`**: ❌ Ausente
- **Toolset `skills`**: ❌ Ausente

### AGENT.md — Skills referenciadas

| Skill | Linha(s) | Tipo | Modo |
|-------|----------|------|------|
| `go-implement` | 16 | `soft` | Mencionada como exemplo de skill injetada pelo orchestrator conforme `tech.md` |
| `react-implement` | 16 | `soft` | Idem |
| `build-check` | 16, 38 | `soft` + `conditional` | Mencionada como skill de smoke-test; "use se disponível", senão fallback para comando padrão |

**Frequência:** `build-check` é a única skill mencionada múltiplas vezes (linhas 16 e 38).

### Resumo agent-dev

O agent-dev **não carrega skills diretamente** — nem via `skills:` no context.yaml, nem tem o toolset `skills`. As skills (`go-implement`, `react-implement`, `build-check`) são **injetadas pelo orchestrator no contexto compilado** (via campo `context` do `delegate_task`), e o Dev as trata como "trilhos, não jaulas": se presentes, usa como guia; se ausentes, opera em "força bruta".

---

## 2. agent-qa

### context.yaml

```yaml
toolsets:
  - terminal
  - file
```

- **Campo `skills:`**: ❌ Ausente
- **Toolset `skills`**: ❌ Ausente

### AGENT.md — Skills referenciadas

| Skill | Linha(s) | Tipo | Modo |
|-------|----------|------|------|
| `gherkin-scenarios` | 16, 23, 29, 133 | `soft` + `conditional` | Usada para gerar cenários `.feature`; se indisponível, pula o passo |
| `go-unit-tests` | 16, 33, 127, 133 | `soft` + `conditional` | Usada para escrever testes unitários; se não cobre padrão → BLOCKED |
| `local-test-runner` | 16, 43, 133 | `soft` + `conditional` | Usada para build + vet + test integrado; se indisponível, usa comandos diretos |

**Frequência:** `gherkin-scenarios` (4 menções), `go-unit-tests` (4), `local-test-runner` (3).

### Resumo agent-qa

Assim como o Dev, o QA **não carrega skills diretamente**. O toolset `skills` está ausente e não há campo `skills:`. As três skills (`gherkin-scenarios`, `go-unit-tests`, `local-test-runner`) são esperadas como parte do contexto injetado pelo orchestrator. O QA as trata como condicionais: se presentes, usa; se ausentes, opera em modo degradado (comandos diretos) ou reporta BLOCKED quando a skill não cobre um padrão.

---

## 3. agent-orchestrator

### context.yaml

```yaml
toolsets:
  - terminal
  - file
  - delegation
  - todo
```

- **Campo `skills:`**: ❌ Ausente
- **Toolset `skills`**: ❌ Ausente

### AGENT.md — Skills referenciadas

Nenhuma skill referenciada. O AGENT.md do orchestrator não menciona nomes de skills, `skill_view`, nem carregamento de skills. Ele apenas coordena subagentes via `delegate_task`.

### Resumo agent-orchestrator

O orchestrator **não usa skills**. Ele é um coordenador puro: lê specs, gerencia DAG de tasks, spawna Dev e QA com `delegate_task`, e valida evidências. As skills que ele "conhece" são apenas as que ele deve injetar no contexto dos subagentes (definidas por `tech.md`), mas ele mesmo não as carrega nem executa.

---

## 4. onboard

### context.yaml

```yaml
toolsets:
  - terminal
  - file
  - web
  - skills
  - todo
```

- **Campo `skills:`**: ❌ Ausente
- **Toolset `skills`**: ✅ Presente — o onboard **pode** chamar `skill_view()` sob demanda

### AGENT.md — Skills referenciadas

| Skill | Linha(s) | Tipo | Modo |
|-------|----------|------|------|
| `sdd-init-repo` | 11, 22 | `soft` (toolset disponível) | Inicializar estrutura SDD |
| `sdd-explore-tech` | 12, 23 | `soft` (toolset disponível) | Mapear stack e preencher `tech.md` |
| `sdd-brainstorm` | 13, 31 | `soft` (toolset disponível) | Entrevista interativa para gerar spec.md |
| `sdd-validate` | 14, 24, 29 | `soft` (toolset disponível) | Auditar estrutura SDD |
| `sdd-generate-plan` | 33 | `soft` (mencionada) | Mencionada como skill que o **usuário** deve invocar (não o onboard) |
| `sdd-generate-tasks` | 33 | `soft` (mencionada) | Idem — usuário invoca, não o onboard |

**Frequência:** `sdd-validate` (3 menções), `sdd-init-repo` (2), `sdd-explore-tech` (2), `sdd-brainstorm` (2), `sdd-generate-plan` (1), `sdd-generate-tasks` (1).

### Resumo onboard

O onboard é o **único** subagente com o toolset `skills` ativo. Ele referencia explicitamente 4 skills core que ele mesmo carrega e executa (`sdd-init-repo`, `sdd-explore-tech`, `sdd-brainstorm`, `sdd-validate`). Outras 2 skills (`sdd-generate-plan`, `sdd-generate-tasks`) são apenas mencionadas como próximos passos para o usuário, não para o onboard.

---

## 5. Visão Consolidada

### Tabela geral

| Agente | Toolset `skills` | Campo `skills:` hard | Skills soft (AGENT.md) | Total skills únicas |
|--------|------------------|-----------------------|------------------------|---------------------|
| **agent-dev** | ❌ | ❌ | `go-implement`, `react-implement`, `build-check` | 3 |
| **agent-qa** | ❌ | ❌ | `gherkin-scenarios`, `go-unit-tests`, `local-test-runner` | 3 |
| **agent-orchestrator** | ❌ | ❌ | *(nenhuma)* | 0 |
| **onboard** | ✅ | ❌ | `sdd-init-repo`, `sdd-explore-tech`, `sdd-brainstorm`, `sdd-validate` | 4 (+2 mencionadas para usuário) |

### Modo de consumo de skills

| Agente | Modo de consumo |
|--------|----------------|
| **agent-dev** | Skills injetadas pelo orchestrator no campo `context` do `delegate_task`. Tratadas como condicionais/opcionais. |
| **agent-qa** | Idem — injetadas pelo orchestrator. Condicionais: se ausentes, opera em modo degradado. |
| **agent-orchestrator** | Não consome skills. Apenas as referencia para injetar nos subagentes. |
| **onboard** | Carrega skills sob demanda via `skill_view()` (toolset `skills` disponível). Fluxo linear e previsível. |

---

## 6. Agrupamentos Naturais

Skills que sempre aparecem juntas e são candidatas a um toolkit único:

### Grupo 1: SDD Core Toolchain (onboard)
Skills carregadas em sequência linear no fluxo de inicialização:
- `sdd-init-repo`
- `sdd-explore-tech`
- `sdd-validate`

**Candidato a toolkit único:** `sdd-core` ou `sdd-init-toolkit`
**Justificativa:** O fluxo do onboard (seção 1 do AGENT.md) carrega estas 3 skills em sequência fixa. Consolidá-las economizaria 2 chamadas de `skill_view()` e unificaria o contexto de inicialização.

### Grupo 2: SDD Brainstorm (onboard)
- `sdd-brainstorm`

**Candidato:** Manter standalone ou consolidar com o Grupo 1.
**Justificativa:** Usada em fase distinta (brainstorm de feature, não inicialização). Pode fazer sentido mantê-la separada ou unificar tudo em `sdd-core` já que o onboard é o único consumidor.

### Grupo 3: Dev Stack Skills (agent-dev)
- `go-implement`
- `react-implement`
- `build-check`

**Candidato a toolkit único:** `dev-stack` ou `stack-implement`
**Justificativa:** São injetadas juntas pelo orchestrator conforme `tech.md`. A skill `build-check` é usada em todo ciclo (smoke-test), enquanto `go-implement`/`react-implement` dependem da stack do projeto. Poderiam ser um toolkit parametrizável por linguagem.

### Grupo 4: QA Validation Suite (agent-qa)
- `gherkin-scenarios`
- `go-unit-tests`
- `local-test-runner`

**Candidato a toolkit único:** `qa-suite` ou `qa-validate`
**Justificativa:** As 3 skills são mencionadas juntas em toda descrição do ciclo de validação do QA (seções 2-4 do AGENT.md). Representam um pipeline coeso: cenários → testes → execução. Consolidar em um toolkit único reduziria de 3 injeções para 1.

---

## 7. Observações para Consolidação (ADR-5)

1. **Nenhum agente usa campo `skills:` hard no context.yaml.** Todas as skills são referenciadas de forma soft (texto do prompt) ou carregadas sob demanda via `skill_view()`. Isso significa que a consolidação não quebra contratos hard — as skills podem ser reorganizadas sem alterar `context.yaml`.

2. **Apenas o onboard tem toolset `skills`.** Dev e QA recebem skills via injeção de contexto do orchestrator, não via `skill_view()`. Se os toolkits consolidados forem carregados via `skill_view()`, Dev e QA precisariam receber o toolset `skills` ou o orchestrator precisaria continuar injetando o conteúdo no contexto.

3. **Orchestrator é o ponto de injeção.** Ele decide quais skills injetar no contexto de Dev e QA com base em `tech.md`. A consolidação deve garantir que os novos toolkits sejam referenciáveis pelo orchestrator com os mesmos nomes (ou com mapeamento claro).

4. **Skills mencionadas para o usuário (`sdd-generate-plan`, `sdd-generate-tasks`)** não são carregadas pelo onboard — são instruções de próximo passo. Não precisam ser consolidadas no toolkit do onboard, mas devem permanecer acessíveis ao usuário.

---

## 8. Conclusão

| Métrica | Valor |
|---------|-------|
| Total de skills únicas referenciadas | 10 (3 dev + 3 qa + 4 onboard) |
| Skills com toolset `skills` disponível | 4 (todas do onboard) |
| Skills injetadas via contexto (sem toolset) | 6 (3 dev + 3 qa) |
| Skills não consumidas por nenhum agente | 2 (`sdd-generate-plan`, `sdd-generate-tasks` — mencionadas apenas como orientação ao usuário) |
| Agrupamentos naturais identificados | 4 |
| Agentes sem skills | 1 (orchestrator) |

**Recomendação:** Consolidar em 4 toolkits (um por agrupamento natural), mantendo `sdd-brainstorm` como decisão de design (standalone vs. parte do `sdd-core`).
