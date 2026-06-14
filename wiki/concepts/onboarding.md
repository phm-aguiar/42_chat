---
title: "Onboarding — Começando com o Framework SDD"
category: concepts
tags: [sdd, onboarding, tutorial, iniciante]
aliases: [getting-started, como-comecar]
sources: []
summary: Guia passo a passo para iniciar um projeto do zero com o framework SDD autônomo. Cobre init repo, brainstorm, spec, plan, tasks e execução com orchestrator.
lifecycle: draft
created: "2026-06-13"
updated: "2026-06-13"
---

# Onboarding — Começando com o Framework SDD

> Você tem uma ideia de projeto e quer usar o framework SDD pra transformá-la em código.
> Este guia cobre do zero à primeira feature implementada.

## Pré-requisitos

- **Hermes Agent** instalado e configurado
- **Git** — repositório inicializado (ou vazio)
- **Provider LLM** configurado (DeepSeek, Anthropic, OpenAI, etc.)
- **Honcho** (opcional) — camada de memória para contexto cross-sessão

## Passo 1: Inicializar o repositório

```bash
# Crie o repo e entre nele
mkdir meu-projeto && cd meu-projeto
git init

# Inicialize a estrutura SDD
# O agente onboard faz tudo: init repo, explore tech, brainstorm inicial
agent-run onboard "inicializa o projeto meu-projeto no framework SDD"
```

O onboard vai:
1. Criar `.github/memory/constitution.md` e `tech.md`
2. Criar `specs/features/`, `specs/domain-events/`, `specs/infra/`
3. Mapear a stack tecnológica (`sdd-explore-tech`)
4. Fazer brainstorm da primeira feature (`sdd-brainstorm`)

**Output esperado:**
```
.github/memory/
├── constitution.md    ← Regras arquiteturais (template inicial)
└── tech.md            ← Stack tecnológica mapeada
specs/
├── features/          ← Features virão aqui
├── domain-events/     ← Eventos de domínio
└── infra/             ← Specs de infraestrutura
AGENTS.md              ← Instruções pros agentes
```

## Passo 2: Brainstorm da primeira feature

```bash
# Pule se o onboard já fez o brainstorm.
# Senão, invoque diretamente:
agent-run onboard "brainstorm da feature de login"
```

O agente faz perguntas via `clarify()` — uma por vez:
1. "Qual o propósito? Que problema resolve?"
2. "O que entra e o que NÃO entra no escopo?"
3. "Me conta o passo a passo do caso principal..."
4. "O que pode dar errado? Edge cases?"
5. "Tem constraints? Prazo? Tecnologia obrigatória?"
6. "Como saber que ficou pronto? Critérios de sucesso?"

**Output:** `specs/features/001-login/spec.md`

## Passo 3: Revisar e aprovar a spec

Abra o `spec.md` e verifique:
- Propósito está claro?
- Escopo delimitado (dentro/fora)?
- Cenários cobrem happy path e edge cases?
- Critérios de sucesso são mensuráveis?

Se estiver tudo certo, mude o gate:
```markdown
- **Aprovado:** false  →  - **Aprovado:** true
```

> **Regra de ouro:** NUNCA implemente sem `Aprovado: true`. O orchestrator rejeita specs não aprovadas.

## Passo 4: Gerar plano arquitetural

```bash
# Gera plan.md com ADRs e auditoria de constituição
# (o agente principal executa esta skill)
```

A skill `sdd-generate-plan` lê `spec.md` + `tech.md` + `constitution.md` e gera:
- Contratos e fronteiras (APIs, schemas)
- ADRs (decisões arquiteturais justificadas)
- Auditoria contra cada regra do `constitution.md`

**Output:** `specs/features/001-login/plan.md`

## Passo 5: Gerar matriz de tasks (DAG)

```bash
# Gera tasks.md com DAG — interage fase por fase
```

A skill `sdd-generate-tasks` (v2.0.0) deriva tarefas atômicas e interage **fase por fase**:

```
Fase 1: Fundação (3 tasks, 2 paralelizáveis)
  T001: Criar modelo User (Dev, paralelo)
  T002: Criar migration (Dev, depende T001)
  T003: Criar cenários Gherkin (QA, paralelo)

[Aprovar] [Ajustar] [Adicionar] [Remover]
```

Cada task tem:
- **Papel:** Dev, QA, ou Test
- **Dependências:** IDs que devem estar `[x]` antes
- **Paralelizável:** true/false (baseado em isolamento de arquivos)
- **Arquivos:** paths que a task modifica

**Output:** `specs/features/001-login/tasks.md`

## Passo 6: Executar com o Orchestrator

```bash
# O orchestrator lê o DAG e spawna subagentes
agent-run agent-orchestrator "orquestra a feature 001"
```

O orchestrator:
1. Verifica `Aprovado: true` ✅
2. Lê `tasks.md` e extrai DAG
3. Spawna agent-dev para tasks Dev
4. Valida evidência de DONE
5. Marca `[x]` no tasks.md
6. Escala bloqueios se necessário

**Output:** Tasks concluídas, código implementado, `tasks.md` com `[x]`.

## Passo 7: Atualizar documentação

Após cada feature implementada:
```bash
# Validar estrutura SDD
sdd-validate

# Atualizar vault Obsidian
# O agente principal mantém wiki/ atualizado automaticamente
```

## Comandos Rápidos

| O que | Comando |
|---|---|
| Inicializar projeto | `agent-run onboard "inicializa o projeto X"` |
| Brainstorm de feature | `agent-run onboard "brainstorm da feature Y"` |
| Validar estrutura | `sdd-validate` |
| Executar feature | `agent-run agent-orchestrator "orquestra a feature NNN"` |
| Commit padronizado | `git-conventional-commit` |
| Ver wiki | Abra `wiki/` no Obsidian |

## Dicas

1. **Comece pequeno:** A primeira feature deve ser simples (ex: "hello world endpoint")
2. **Aproveite o onboard:** Ele faz init + brainstorm de uma vez. Economiza 2 comandos
3. **Revise specs:** O agente gera bem, mas revisão humana evita retrabalho
4. **Vault é memória:** Tudo que você decide fica registrado no `wiki/`. Não precisa lembrar
5. **Constitution é lei:** Leia `constitution.md` antes de qualquer decisão arquitetural

## Relacionado

- [[concepts/sdd-workflow|SDD Workflow]] — Pipeline completo explicado em detalhes
- [[concepts/constitution|Constituição]] — Regras que governam o framework
- [[concepts/tech|Stack]] — Tecnologias homologadas
- [[projects/42_chat/features/feature-006-agent-dev|Feature 006]] — Exemplo real de feature implementada
