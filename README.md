# 42_chat — Framework SDD Autônomo

> Squad de agentes de IA com wiki como cérebro, toolkits como ferramentas e
> humanos no loop de aprovação. Spec-Driven Development do início ao fim.

## Como funciona (pra humanos)

O sistema tem 3 camadas:

```
🧠 Wiki (cérebro)     →  Memória de longo prazo. Tudo que o sistema sabe
                         fica aqui. Versionado no repo (wiki/).

🔧 Toolkits (skills)  →  Ferramentas consolidadas. 119 skills viram 11
                         toolkits com modos internos. Subagentes carregam
                         1-2 toolkits ao invés de 5-10 skills.

🤖 Agentes (mão de obra)→ Agente principal (você + IA) orquestra. Subagentes
                         especializados (Dev, QA) executam tasks em paralelo.
```

### O cérebro: Wiki

A wiki é um vault Obsidian versionado no repo (`wiki/`). Toda decisão, feature,
skill e padrão arquitetural é documentado aqui. O agente consulta a wiki antes
de agir — não reinventa conhecimento que já foi compilado.

```
wiki/
├── concepts/     — Padrões, metodologia (SDD, wiki-model, vault-taxonomy)
├── skills/       — Documentação dos 11 toolkits
├── references/   — Templates, formatos, padrões externos
├── journal/      — Sessões e decisões capturadas
├── synthesis/    — Conexões cross-cutting entre conceitos
└── index.md      — Índice mestre do vault
```

**Entry points pra humanos:**
- `wiki/index.md` — catálogo completo do que existe
- `wiki/skills/toolkit-map.md` — mapa de qual skill foi absorvida por qual toolkit
- `wiki/references/toolkits/` — templates e padrões de referência

### As ferramentas: 11 Toolkits

| Toolkit | Tamanho | Pra quê | Quem usa |
|---|---|---|---|
| `brain` | 30 skills | Wiki, Obsidian, Docs — o cérebro | Principal |
| `sdd` | 9 skills | Pipeline SDD (spec→plan→tasks) | Principal |
| `qa-toolkit` | 8 skills | Testes, Gherkin, BDD, TDD | agent-qa |
| `dev-toolkit` | 15 skills | Go, React, debug, code review | agent-dev |
| `github` | 7 skills | PR, issues, review, commits | Principal |
| `devops` | 6 skills | Docker, Honcho, Kanban, áudio | Principal |
| `visual` | 13 skills | Diagramas, design, ASCII art | Principal |
| `media` | 6 skills | Áudio, vídeo, ComfyUI | Principal |
| `ml` | 8 skills | HuggingFace, llama.cpp, vLLM | Principal |
| `research` | 6 skills | arXiv, blogwatch, papers | Principal |
| `productivity` | 5 skills | PPTX, PDF, OCR, mapas, Hue | Principal |

**Carregar um toolkit:** `skill_view('dev-toolkit')` — 1 chamada, 15 modos.
Antes eram 15 `skill_view()` separadas.

### Os agentes

| Agente | Toolkits | Função |
|---|---|---|
| **Principal** (você + IA) | `brain`, `sdd`, `github`, etc. | Orquestra features, mantém wiki, interage com humano |
| **agent-dev** | `dev-toolkit` | Implementa código. Leaf (não delega). Reporta DONE/FAIL/BLOCKED |
| **agent-qa** | `qa-toolkit` | Testa, roda Gherkin, build/lint/vet. Rejeita task do Dev |
| **agent-orchestrator** | (coordena apenas) | Lê DAG do tasks.md, spawna subagentes em paralelo |
| **onboard** | `sdd` | Inicializa projetos novos no framework SDD |

## Fluxo SDD (Spec-Driven Development)

Toda feature segue o mesmo pipeline. Nada é implementado sem spec aprovada.

```
1. brainstorm     →  spec.md    (entrevista interativa com humano)
2. plan           →  plan.md    (decisões arquiteturais, ADRs)
3. tasks          →  tasks.md   (DAG de tasks com paralelismo)
4. APPROVE        →  humano marca "Aprovado: true"
5. orchestrator   →  spawna subagentes conforme DAG
6. validate       →  sdd-validate + wiki-lint
```

**Comandos reais (exemplo feature 008):**
```bash
# 1. Brainstorm — o agente entrevista você e gera spec.md
"brainstorm: consolidar skills em toolkits"

# 2-3. O agente gera plan.md e tasks.md
"gera plan para 008-reavaliacao-skills"
"gera tasks para 008-reavaliacao-skills"

# 4. Você aprova (edite o spec.md)
Aprovado: true

# 5-6. Execução fase por fase
"executa fase 1 do tasks.md"   # 3 tasks em paralelo
"executa fase 2"                # 11 toolkits em batches de 3
```

## Setup

```bash
git clone <repo-url> && cd 42_chat

# Skills versionadas no repo, symlinks automáticos
./scripts/setup-skills.sh

# Verificar
hermes skills list | grep -E "brain|sdd|qa-toolkit|dev-toolkit"
```

## Estrutura do Projeto

```
42_chat/
├── .github/memory/
│   ├── constitution.md    # Regras invioláveis
│   └── tech.md            # Stack homologado
├── .hermes/
│   ├── skills/            # 11 toolkits versionados
│   │   ├── wiki/brain/    #   brain (30 skills → 8 modos)
│   │   ├── sdd/sdd/       #   sdd (9 → 8)
│   │   ├── qa/qa-toolkit/ #   qa-toolkit (8 → 8)
│   │   ├── dev/dev-toolkit/#  dev-toolkit (15 → 15)
│   │   ├── github/github/ #   github (7 → 7)
│   │   ├── devops/devops/ #   devops (6 → 6)
│   │   ├── creative/visual/#  visual (13 → 13)
│   │   ├── creative/media/ #   media (6 → 6)
│   │   ├── mlops/ml/      #   ml (8 → 8)
│   │   ├── research/research/ # research (6 → 6)
│   │   └── productivity/productivity/ # productivity (5 → 5)
│   └── agents/            # Definições de subagentes
│       ├── agent-dev/     #   Dev: AGENT.md + context.yaml
│       ├── agent-qa/      #   QA: AGENT.md + context.yaml
│       ├── agent-orchestrator/
│       └── onboard/
├── wiki/                  # 🧠 Cérebro — vault Obsidian versionado
│   ├── index.md           #   Índice mestre
│   ├── skills/            #   Páginas dos 11 toolkits
│   ├── references/toolkits/ # Templates, formatos, padrões ingeridos
│   ├── concepts/          #   SDD, wiki-model, vault-taxonomy
│   └── journal/           #   Sessões e decisões
├── specs/features/        # Features SDD (001-008 + 100-101)
├── llms.txt               # Mapa do repo (entry point pra agentes)
└── AGENTS.md              # Regras de enforcement (tabela de gatilhos wiki)
```

## Convenções

- **Versionado no repo:** skills, agentes, wiki, specs — tudo versionado
- **Symlinks planos:** `~/.hermes/skills/<cat>/<nome>` → `.hermes/skills/<cat>/<nome>`
- **Wiki fiel:** feature concluída → wiki atualizado. Vault desatualizado bloqueia PR
- **Aprovação humana:** `Aprovado: true` no spec.md antes de qualquer código
- **Subagentes leaf:** não delegam. Profundidade máxima = 1
- **Toolkits, não skills:** carregar 1 toolkit ao invés de 5-10 skills

## Atualizado em

2026-06-19 — Feature 008: Reavaliação e Consolidação de Skills
