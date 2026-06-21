---
name: sdd
description: >
  Toolkit consolidado do pipeline SDD (Spec-Driven Development). 8 modos cobrindo
  o ciclo completo: brainstorm → explore-tech → init-repo → plan → tasks → validate →
  refactor → wiki-enforce. Carregue SEMPRE antes de qualquer operação SDD.
  Trigger keywords: SDD, spec, feature, pipeline, brainstorm, explore tech, init repo,
  gerar plano, gerar tasks, validar SDD, refatorar artefato, wiki enforcement.
version: 1.0.0
author: phm-aguiar (consolidação feature 008-reavaliacao-skills T007)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Pipeline, Spec, Plan, Tasks, Validate, Refactor, Wiki]
    category: sdd
    modes:
      - brainstorm
      - explore-tech
      - init-repo
      - plan
      - tasks
      - validate
      - refactor
      - wiki-enforce
    umbrella_for:
      - sdd-brainstorm
      - sdd-explore-tech
      - sdd-init-repo
      - sdd-generate-plan
      - sdd-generate-tasks
      - sdd-validate
      - sdd-refactor-artifact
      - sdd-wiki-enforcement
    resources:
      - SKILL.md
    absorbed_skills_resources:
      brainstorm: [references/interview-dimensions.md, assets/spec-template.md]
      explore-tech: [assets/tech-template.md]
      init-repo: [assets/templates/constitution-template.md, assets/templates/spec-template.md, assets/templates/plan-template.md, assets/templates/tasks-template.md, references/sdd-workflow-agents-md.md, references/agents-md-sdd-section.md, scripts/scaffold-sdd.sh]
      plan: [references/architecture-patterns.md]
      tasks: [references/task-rules.md]
      validate: [references/content-quality.md, scripts/check-sdd.sh]
      refactor: [references/canonical-templates.md]
      wiki-enforce: [references/yaml-pitfalls.md, references/lightweight-skill-pattern.md]
    demoted_to_reference:
      agent-persona-pattern: "Padrão arquitetural referenciado nos modos plan/tasks mas não absorvido como modo. Ver ~/.hermes/skills/sdd/agent-persona-pattern/SKILL.md ou wiki/projects/agent-persona-pattern.md."
---

# sdd — Pipeline SDD Consolidado (8 modos)

> Toolkit unificado do pipeline Spec-Driven Development. Cada modo cobre uma fase do ciclo.

## Pipeline e Fluxo entre Modos

```
brainstorm → spec.md ──→ plan → plan.md ──→ tasks → tasks.md
     ↑                    ↑                    ↑
     │                    │                    │
  explore-tech        init-repo            validate
  (tech.md)         (estrutura)         (auditoria)
                                             │
                    wiki-enforce ←───────────┘
                  (AGENTS.md triggers)
```

| Modo | Gatilho | Entrada | Saída |
|---|---|---|---|
| `brainstorm` | Discutir feature, nova ideia | Ideia do usuário | `spec.md` |
| `explore-tech` | Mapear stack, preencher tech.md | Repo | `tech.md` |
| `init-repo` | Inicializar SDD, criar estrutura | Repo vazio/existente | `.github/memory/` + `specs/` |
| `plan` | Gerar plano arquitetural | `spec.md` | `plan.md` |
| `tasks` | Gerar matriz de tasks DAG | `spec.md` + `plan.md` | `tasks.md` |
| `validate` | Auditar estrutura SDD | Repo | Relatório PASS/FAIL/WARN |
| `refactor` | Normalizar artefato SDD | `spec/plan/tasks.md` | Artefato canônico |
| `wiki-enforce` | Wire wiki no AGENTS.md | `AGENTS.md` | Tabela de gatilhos wiki |

---

## Modo: brainstorm

**Gatilhos:** brainstorm, discutir ideia, nova feature, entrevista, discovery, bora pensar, como voce faria.

**HARD-GATE:** Nunca implemente antes do spec aprovado.

### Fluxo

1. **Explorar contexto:** leia `tech.md`, `constitution.md`, liste `specs/features/`.
2. **Avaliar escopo:** se múltiplos subsistemas independentes, decomponha em features separadas.
3. **Entrevista interativa com `clarify()`:** uma pergunta por vez, múltipla escolha. Cubra propósito, escopo, constraints, critérios de sucesso. Só avance quando a dimensão atual estiver clara. Se usuário disser "confio em você", preencha com defaults e valide no passo 4.
4. **Propor 2-3 abordagens** com trade-offs e recomendação.
5. **Gerar spec.md:** ID incremental (`specs/features/<NNN>-<slug>/spec.md`), seções canônicas preenchidas. Template em `~/.hermes/skills/sdd/brainstorm/assets/spec-template.md`.
6. **Self-review:** placeholders? contradições? escopo focado?
7. **Gate de aprovação:** `clarify()` para aprovação explícita.
8. **Transição:** carregue `plan` (próximo modo) ou aguarde.

### Pitfalls

- **Empilhar perguntas:** uma por `clarify()`, SEMPRE.
- **YAGNI violado:** spec com máximo possível em vez de mínimo viável.
- **Constitution ignorado:** spec não pode violar portões/anti-padrões. Se inevitável, alerte e peça autorização.
- **Idempotência:** detecte spec existente e pergunte se refinar ou começar do zero.
- **IDs não incrementais:** derive do maior ID em `specs/features/`. Vazio = `001`.

---

## Modo: explore-tech

**Gatilhos:** mapear tech stack, explorar tecnologia, preencher tech.md, detectar stack, what tech does this repo use.

### Fluxo

1. **Detectar manifestos:** busque `go.mod`, `package.json`, `Cargo.toml`, `pom.xml`, `pyproject.toml`, `Gemfile`, `mix.exs`, `CMakeLists.txt`, `*.csproj`.
2. **Extrair versões e dependências:** leia cada manifesto, extraia versão da linguagem e frameworks principais.
3. **Detectar CI e ferramentas:** `.github/workflows/`, linters (`.golangci.yml`, `.eslintrc*`), Docker, task runners (`Makefile`, `justfile`), padrões de teste.
4. **Consolidar em tech.md:** preencha template (`~/.hermes/skills/sdd/explore-tech/assets/tech-template.md`). Use `—` para entradas não encontradas.
5. **Reportar:** resuma achados, pergunte se usuário quer ajustar.

### Pitfalls

- **Nunca inventar stack:** apenas o detectado em arquivos reais.
- **Campos vazios = `—`:** não preencha com suposições.
- **Nenhum manifesto:** alerte — repo pode estar vazio ou usar linguagem não suportada.
- **tech.md existente:** pergunte se sobrescreve ou mescla.

---

## Modo: init-repo

**Gatilhos:** iniciar SDD, init sdd, estrutura sdd, setup sdd, inicializar repo SDD, criar estrutura SDD.

### Fluxo

1. **Verificar estado:** liste raiz. Se `.github/memory/` ou `specs/` existirem, pergunte preservar ou recriar.
2. **Criar memória de contexto:**
   - `.github/memory/constitution.md` — template em `~/.hermes/skills/sdd/init-repo/assets/templates/constitution-template.md`
   - `.github/memory/tech.md` — placeholder; preencher depois via `explore-tech`
   - Automação opcional: `bash scripts/scaffold-sdd.sh`
3. **Criar specs/:** `mkdir -p specs/domain-events specs/features specs/infra`
4. **Atualizar AGENTS.md:** merge da seção SDD Workflow (template em `references/sdd-workflow-agents-md.md`). Idempotente — se já existe, pule.
5. **Sugerir próximos passos:** `explore-tech` → preencher `constitution.md` → `brainstorm`.

### Pitfalls

- **Sobrescrever sem perguntar:** idempotência é obrigatória.
- **Assumir stack:** estrutura SDD é agnóstica de linguagem.
- **AGENTS.md truncado:** faça merge, não replace.
- **constitution.md é sagrado:** regras exigem confirmação do usuário.

---

## Modo: plan

**Gatilhos:** gerar plan, criar plan.md, generate plan, criar plano, generate architectural plan.

### Fluxo

1. **Identificar feature:** usuário informa diretório (ex: `specs/features/003-forge-skill`).
2. **Ler fontes:** `spec.md` (funcionalidade, cenários), `tech.md` (stack), `constitution.md` (portões).
3. **Gerar 4 seções canônicas:**
   - **Metadados:** stack, feature fonte, escopo (1 frase).
   - **Contratos e Fronteiras:** APIs/eventos/schemas ou "Nenhum contrato formal neste estágio."
   - **ADRs:** ao menos 1 decisão arquitetural com justificativa + alternativa rejeitada.
   - **Auditoria de Constituição:** checklist contra cada regra do `constitution.md`.
4. **Apresentar e salvar:** mostre stack, número de ADRs, auditoria. **Pergunte antes de salvar.** Escreva `plan.md`.

Referência de padrões em `~/.hermes/skills/sdd/generate-plan/references/architecture-patterns.md`.

### Pitfalls

- **Stack inventada:** use apenas `tech.md`. Vazio = placeholders `{{...}}`.
- **ADR zero:** mínimo 1 ADR estrutural.
- **Preservar placeholders:** `{{...}}` do spec intactos.
- **Idempotência:** `plan.md` existe → pergunte sobrescrever ou mesclar.

---

## Modo: tasks

**Gatilhos:** gerar tasks, criar tasks.md, generate tasks, criar tarefas.

**HARD-GATE:** spec.md deve ter `Aprovado: true` nos metadados. Se `false` → ABORTE.

### Fluxo

1. **Approval gate:** leia spec.md, verifique `**Aprovado:** true`. Se false, aborte.
2. **Identificar feature:** usuário informa diretório.
3. **Ler fontes:** spec.md + plan.md → funcionalidade, cenários BDD, stack, contratos, ADRs.
4. **Carregar regras:** `~/.hermes/skills/sdd/generate-tasks/references/task-rules.md`.
5. **Derivar tasks atômicas** com metadados DAG — **interação fase por fase via `clarify()`:**
   - Cada task: `Tnnn`, Papel (Dev|QA), Dependências, Paralelizável (true|false), Arquivos (paths exaustivos).
   - **Regra de paralelismo:** tasks da mesma fase são paralelizáveis se e somente se (a) sem dependência entre elas E (b) conjuntos de Arquivos disjuntos. Se compartilham paths → force sequencial.
   - **Exceção inteligente:** QA `.feature` vs Dev `.go` no mesmo dir → sem conflito (extensões diferentes).
6. **Validar DAG completo:** detectar ciclos (DFS), dependências quebradas, tasks órfãs, conflitos de arquivos.
7. **Salvar:** `tasks.md` no diretório da feature. Se existir, pergunte.

### Pitfalls

- **Agrupar ações:** "Criar X e testar Y" → 2 tasks separadas.
- **Gerar todas as fases de uma vez:** interaja fase por fase com `clarify()`.
- **Tasks paralelas compartilhando arquivos:** viola HARD RULE — force sequencial.
- **Órfãs silenciosas:** task sem deps e sem dependentes → pergunte se intencional.
- **Approval gate ignorado:** sem `Aprovado: true`, ABORTE.

---

## Modo: validate

**Gatilhos:** validar SDD, validate sdd, auditar estrutura, check sdd, verificar conformidade, audit structure.

**Read-only:** apenas reporte, nunca crie ou modifique arquivos.

### Fluxo

1. **Nível 1 — Memória global:** `.github/memory/` + `constitution.md` + `tech.md`.
2. **Nível 2 — Diretório specs:** `specs/` + `domain-events/` + `features/` + `infra/`.
3. **Nível 3 — Features:** para cada `specs/features/<id>-<nome>/`, verifique `spec.md`, `plan.md`, `tasks.md`.
4. **Nível 4 — AGENTS.md:** existe? contém workflow SDD?
5. **Sumário:** relatório PASS (existe e não vazio) / FAIL (ausente) / WARN (vazio). Inclua ações sugeridas.

Automação opcional: `~/.hermes/skills/sdd/validate/scripts/check-sdd.sh`.

Qualidade de conteúdo: `~/.hermes/skills/sdd/validate/references/content-quality.md` (freshness scoring, métricas de cobertura).

### Pitfalls

- **Corrigir em vez de reportar:** modo read-only. Nunca crie/modifique.
- **Features sem numeração:** WARN para diretórios fora do padrão `<id>-<nome>`.
- **Confundir FAIL com WARN:** ausente = FAIL, vazio/em progresso = WARN.

---

## Modo: refactor

**Gatilhos:** refatorar spec, refatorar plan, refatorar tasks, formatar spec.md, normalizar artefato, alinhar com template, padronizar spec, refactor artifact.

### Fluxo

1. **Identificar tipo:** especificação (`spec.md`), plano (`plan.md`), tasks (`tasks.md`), agentes (`AGENTS.md`), navegação (`llms.txt`).
2. **Ler conteúdo atual:** extraia semanticamente títulos, parágrafos, listas, placeholders.
3. **Mapear para seções canônicas:** templates em `~/.hermes/skills/sdd/refactor-artifact/references/canonical-templates.md`.
4. **Apresentar diff:** resumo das mudanças. **Pergunte antes de aplicar.**
5. **Aplicar e reportar:** seções adicionadas, renomeadas, conteúdo preservado.

### Pitfalls

- **Descartar conteúdo:** preservação total. Sem seção canônica → mova para `## Notas Adicionais`.
- **Sobrescrever sem confirmação:** sempre apresente diff primeiro.
- **Já conforme:** se artefato segue template, reporte e não modifique.
- **AGENTS.md parcial:** apenas seção SDD Workflow é refatorada.
- **Placeholders:** preserve `{{...}}` e `` intactos.

---

## Modo: wiki-enforce

**Gatilhos:** AGENTS.md trigger table, wiki enforcement, wire wiki into SDD, agent not using wiki skills.

### Fluxo

1. **Auditar AGENTS.md atual:** verifique se já tem tabela de gatilhos wiki.
2. **Inserir/atualizar tabela de enforcement:**

```markdown
### Gatilhos — Quando usar cada skill da base

| Gatilho (o que você vai fazer) | Ação obrigatória | Skill |
|---|---|---|
| Implementar feature, agente, ou skill | Buscar decisões prévias | `wiki-query` |
| Sugerir arquitetura ou ADR | Verificar ADR similar | `wiki-query` |
| Adicionar dependência ao tech.md | Verificar stack atual | `wiki-query` |
| Feature/agente/skill concluída | Criar/atualizar página wiki | `wiki-ingest` |
| Mover, renomear ou criar páginas wiki | Validar integridade vault | `wiki-lint` |
| Antes de commit | Validar estrutura SDD + vault | `sdd-validate` + `wiki-lint` |
| Nova sessão (primeiro contato) | Carregar contexto do vault | `llms.txt` + `wiki/index.md` |
| Mudança no constitution.md ou tech.md | Atualizar concepts/sdd.md | `wiki-ingest` |
| Após criar/modificar múltiplas páginas | Descobrir wikilinks faltantes | `wiki/cross-linker` |
| Sessão importante (decisões, debug) | Salvar conversa no vault | `wiki-capture` |

> **Regra de enforcement:** Se executou uma ação da coluna "Gatilho" e NÃO
> executou a "Ação obrigatória" correspondente, **pare e execute a ação obrigatória
> antes de continuar.**
```

3. **Validar:** tabela completa, regra de enforcement visível.

### Pitfalls

- **YAML frontmatter com `:` no texto:** quebra parser. Envolva em aspas duplas.
- **Prefixos `N|`:** `write_file` via `execute_code` injeta prefixos. Limpe com `re.sub`.
- **Links quebrados:** skills em `skills/` referenciando outras precisam de path completo.
- **Fluxo de consulta genérico:** triggers explícitos funcionam; orientações vagas são ignoradas.

---

## Nota: Criar Subagentes (agent-persona-pattern)

O padrão arquitetural `agent-persona-pattern` (persona fixa + skills plugáveis por stack) **não foi absorvido como modo**. É um documento de referência arquitetural para criar novos agentes do squad (Dev, QA, DevOps, Pentester).

**Fluxo para criar um subagente:**
1. `brainstorm` → spec.md com propósito, escopo e skills do agente
2. `plan` → ADRs: quais toolkits o agente carrega, contrato de entrada/saída
3. `tasks` → DAG: criar AGENT.md, context.yaml, smoke test
4. Consulte a wiki para templates e padrões:
   - `[[references/toolkits/sdd/spec-template|Spec Template]]` — template de especificação
   - `[[references/toolkits/wiki/karpathy-pattern|Karpathy Pattern]]` — padrão de conhecimento compilado
   - `[[skills/brain|brain]]` modo `format` — sintaxe OFM para documentar o agente

**Regras derivadas já incorporadas:**
- Papéis válidos: Dev, QA, DevOps, Pentester ("Test" é obsoleto, migre para QA).
- Features de agente não seguem 4 fases canônicas de código — adapte conforme o domínio.
- **Constitutional (portão #4):** após qualquer feature, o vault Obsidian (`wiki/`) DEVE ser atualizado. Vault desatualizado bloqueia PR.
