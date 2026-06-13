---
name: agent-run
description: >
  Use when the user wants to spawn any agent defined in .hermes/agents/<name>/. Generic agent
  runtime. Reads an agent definition from .hermes/agents/<name>/ (AGENT.md + context.yaml),
  compiles a clean micro-context from session history and project files, then spawns the agent
  as an isolated subagent via delegate_task. Trigger keywords: agent-run, rodar agente,
  executar agente, run agent, spawn agent, invoke agent, orquestrar, coordenar.
version: 1.0.1
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Agent-Runtime, Subagent, Context-Compiler, Delegation]
    related_skills: [skill-forge]
    category: agent
    resources:
      - SKILL.md
---

# Agent Run — Runtime Genérico de Agentes

## Propósito

Skill genérica que recebe o nome de um agente e uma demanda, compila um micro-contexto limpo (sem corrosão) a partir do `AGENT.md` + `context.yaml` do agente, e spawna um subagente isolado via `delegate_task`.

O subagente nasce numa **folha em branco** — zero histórico, zero memória. Só enxerga o que o `context.yaml` determinar.

## Pré-requisitos

- Agente definido em `.hermes/agents/<nome>/` com:
  - `AGENT.md` — persona, regras, fluxo de trabalho
  - `context.yaml` — receita do que compilar no contexto

## Quando usar (gatilhos)

Carregue esta skill quando o usuário disser algo como:

- "agent-run", "rodar agente", "executar agente"
- "run agent", "spawn agent", "invoke agent"
- "orquestrar", "coordenar" (quando se tratar de spawnar subagente)

## Fluxo de Execução

### Passo 1: Identificar agente e demanda

O usuário deve fornecer:
- **Agente:** nome do diretório em `.hermes/agents/` (ex: `sdd-orchestrator`)
- **Demanda:** o que o subagente deve fazer (ex: "criar feature 004-login")

Se não informar, pergunte ambos. Use `search_files(target='files', pattern='*', path='.hermes/agents')` para listar agentes disponíveis.

### Passo 2: Ler definição do agente

```
AGENT.md    → read_file('.hermes/agents/<nome>/AGENT.md')
context.yaml → read_file('.hermes/agents/<nome>/context.yaml')
```

Parseie o `context.yaml` para extrair a receita.

### Passo 3: Compilar contexto (mastigação)

Monte uma string de contexto limpa, nesta ordem:

**3a. Persona (do AGENT.md)**
Inclua o conteúdo completo do `AGENT.md` como base.

**3b. Arquivos fixos (`include.files`)**
Para cada arquivo listado, leia com `read_file` e inclua.

**3c. Contexto da sessão (`include.session_last_n` + `include.session_searches`)**
Use `session_search` sem parâmetros para ver sessões recentes. Se `session_searches` tiver termos, use `session_search(query=...)` para cada termo. Extraia apenas fatos relevantes — NÃO inclua a transcrição completa. O objetivo é dar contexto, não poluir.

**3d. Feature específica (se a demanda mencionar ID)**
Se a demanda contiver um padrão como `NNN-slug`, `feature NNN`, `spec NNN`:
- Resolva o diretório: `specs/features/<NNN>-<slug>/`
- Para cada artefato em `include.feature_artifacts`, leia e inclua

**3e. Metadados do ambiente**
Inclua:
```
Projeto: <nome do repo>
Working directory: <cwd>
Branch atual: <git branch>
```

### Passo 4: Spawnar subagente

```python
delegate_task(
  goal="<demanda do usuário>",
  context="<contexto compilado nos passos 3a-3e>",
  toolsets=<lista do context.yaml ou default>
)
```

Use os toolsets definidos em `context.yaml → toolsets`. Se não definido, use `["terminal", "file", "web", "skills", "todo"]`.

### Passo 5: Reportar resultado

O subagente retorna um sumário. Apresente ao usuário e:
- Liste arquivos criados/alterados
- Destaque blockers ou ambiguidades
- Sugira próximos passos

## Estrutura de um agente

```
.hermes/agents/<nome>/
├── AGENT.md              ← Persona, regras, fluxo de trabalho
└── context.yaml           ← Receita de contexto
```

### Formato do context.yaml

```yaml
include:
  files:                          # Arquivos sempre incluídos
    - .github/memory/constitution.md
    - AGENTS.md

  session_last_n: 15              # N mensagens recentes da sessão

  session_searches:               # Termos pra buscar no histórico
    - SDD
    - feature

  feature_artifacts:              # Se demanda menciona feature NNN
    - spec.md
    - plan.md
    - tasks.md

toolsets:                         # Toolsets do subagente
  - terminal
  - file
  - web
  - skills
  - todo
```

## Guardrails

- **Contexto LIMPO é lei**: nunca passe o histórico completo da sessão. Mastigue — inclua só fatos relevantes.
- **Subagente é leaf**: não pode spawnar outros subagentes. Se precisar de mais trabalho, o agente principal faz.
- **Verifique o resultado**: o subagente devolve um sumário auto-reportado. Confira arquivos criados/alterados antes de reportar ao usuário.
- **context.yaml é o contrato**: se um arquivo listado não existe, alerte no contexto ("arquivo X não encontrado"), não quebre.
- **Agente não encontrado**: se `.hermes/agents/<nome>/` não existe, liste os disponíveis e pergunte.

## Verificação

- [ ] Subagente foi spawnado via `delegate_task` (não chamada direta)
- [ ] Contexto passado é COMPILADO (não transcrição completa da sessão)
- [ ] Toolsets usados batem com `context.yaml` ou o default documentado
- [ ] Resultado do subagente foi conferido (arquivos, status) antes de reportar ao usuário
