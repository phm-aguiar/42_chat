# TUTORIAL.md — Framework SDD Autônomo

> Guia rápido: da ideia à feature implementada em 6 passos.

## Pré-requisitos

- Hermes Agent instalado
- Git
- Provider LLM configurado

## 6 Passos

### 1. Inicializar o projeto

```bash
git init meu-projeto && cd meu-projeto
agent-run onboard "inicializa o projeto no framework SDD"
```

Cria `.github/memory/`, `specs/`, `AGENTS.md`.

### 2. Brainstorm da feature

```bash
agent-run onboard "brainstorm da feature de login"
```

O agente entrevista você via `clarify()` — 6 perguntas, uma por vez.

**Output:** `specs/features/001-login/spec.md`

### 3. Aprovar a spec

Abra `spec.md` e mude:
```markdown
- **Aprovado:** false  →  - **Aprovado:** true
```

### 4. Gerar plano e tasks

```bash
# O agente principal gera plan.md e tasks.md
# (invocado automaticamente — você só revisa e aprova)
```

### 5. Executar

```bash
agent-run agent-orchestrator "orquestra a feature 001"
```

O orchestrator spawna agent-dev, valida evidência, marca `[x]` nas tasks.

### 6. Validar e commitar

```bash
sdd-validate                    # Estrutura SDD OK?
git add -A && git commit -m "feat: implementa feature 001"
```

## Pipeline Visual

```
onboard (init + brainstorm)
     ↓
spec.md → Aprovado: true
     ↓
sdd-generate-plan → plan.md (ADRs)
     ↓
sdd-generate-tasks → tasks.md (DAG)
     ↓
agent-orchestrator → spawna agent-dev
     ↓
código implementado ✅
```

## Estrutura do Repo

```
meu-projeto/
├── .github/memory/
│   ├── constitution.md    ← Regras arquiteturais
│   └── tech.md            ← Stack tecnológica
├── .hermes/
│   ├── agents/            ← Agentes versionados
│   └── skills/            ← Skills versionadas
├── specs/features/
│   └── 001-login/
│       ├── spec.md        ← O QUE
│       ├── plan.md        ← COMO
│       └── tasks.md       ← QUEM FAZ O QUÊ (DAG)
├── wiki/                  ← Vault Obsidian (knowledge base)
├── AGENTS.md              ← Instruções pros agentes
└── TUTORIAL.md            ← Este arquivo
```

## Agentes do Framework

| Agente | Função | Status |
|---|---|---|
| `onboard` | Inicializa projeto + brainstorm | ✅ |
| `agent-orchestrator` | Lê DAG, spawna subagentes | ✅ |
| `agent-dev` | Implementa código | ✅ |
| `agent-qa` | Testes, Gherkin, lint | ❌ (007) |
| `agent-devops` | CI/CD, Docker, deploy | ❌ (008) |
| `agent-pentester` | Segurança, OWASP | ❌ (009) |

## Documentação Completa

- `wiki/concepts/sdd-workflow.md` — Pipeline SDD em detalhes
- `wiki/concepts/onboarding.md` — Guia passo a passo estendido
- `wiki/concepts/constitution.md` — Regras arquiteturais
- `wiki/index.md` — Índice completo do vault

## Dicas

- **Nunca implemente sem `Aprovado: true`** — o orchestrator rejeita
- **Vault Obsidian é memória** — abra `wiki/` no Obsidian pra navegar
- **Skills são trilhos, não jaulas** — agentes adaptam criativamente
- **Commits padronizados** — use `git-conventional-commit`
