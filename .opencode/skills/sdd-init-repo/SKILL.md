---
name: sdd-init-repo
description: Use ONLY when the user asks to initialize a repository with the Spec-Driven Development (SDD) structure. Creates .github/memory/ (constitution.md, tech.md), /specs/ hierarchy, and updates AGENTS.md with SDD workflow. Language-agnostic and reusable across any tech stack. Trigger keywords: "iniciar SDD", "init sdd", "estrutura sdd", "setup sdd", "inicializar repo SDD", "criar estrutura SDD".
---

# Inicializar Repositório SDD

## Propósito

Inicializa ou adapta um repositório existente para seguir o modelo Spec-Driven Development (SDD), criando a hierarquia `.github/memory/` e `/specs/` e atualizando o `AGENTS.md` com o workflow SDD.

## Pré-requisitos

Nenhum. Esta skill é o ponto de entrada do fluxo SDD. Pode ser executada em repositórios vazios ou existentes.

## Estrutura alvo

```
<repo>/
├── .github/
│   └── memory/                   ← Memória de Contexto Global
│       ├── constitution.md       ← Portões de qualidade, restrições, regras de negócio
│       └── tech.md               ← Stack tecnológica homologada
├── specs/                        ← Única Fonte da Verdade (SSOT)
│   ├── domain-events/            ← Contratos formais (AsyncAPI, OpenAPI, etc.)
│   ├── features/                 ← Features numeradas
│   │   └── 001-nome-da-feature/
│   │       ├── spec.md           ← Intenção de negócio e critérios de aceite
│   │       ├── plan.md           ← Plano arquitetural e decisões técnicas
│   │       └── tasks.md          ← Lista granular de passos de implementação
│   └── infra/                    ← Declarações de infraestrutura
└── AGENTS.md                     ← Atualizado com workflow SDD
```

## Fluxo de Execução

### Passo 1: Verificar estado atual

1. Liste o diretório raiz para entender o que já existe.
2. Verifique se `.github/memory/` já existe. Se sim, pergunte ao usuário se deve recriar ou preservar.
3. Verifique se `/specs/` já existe. Se sim, pergunte se deve preservar.

### Passo 2: Criar a Memória de Contexto Global

Crie `.github/memory/` com dois arquivos:

**`constitution.md`** — molde inicial:

```markdown
# Constituição Arquitetural

> Este arquivo define as regras incontornáveis do projeto.
> **Sempre pergunte ao usuário antes de adicionar ou modificar regras neste arquivo.**

## Portões de Qualidade
<!-- Regras automatizadas que bloqueiam PRs se violadas -->
<!-- Ex: "Toda função pública deve ter teste unitário" -->

## Restrições Arquiteturais
<!-- Decisões estruturais que não podem ser violadas -->
<!-- Ex: "Comunicação entre módulos apenas via interfaces/ports" -->

## Regras de Negócio Transversais
<!-- Regras que afetam múltiplas features -->
```

**`tech.md`** — placeholder:

```markdown
# Stack Tecnológica

> Execute a skill `sdd-explore-tech` para preencher este arquivo automaticamente
> ou edite manualmente.

## Linguagens
| Linguagem | Versão | Detecção |
|---|---|---|
| — | — | — |

## Frameworks e Bibliotecas
| Nome | Versão | Propósito |
|---|---|---|
| — | — | — |

## Ferramentas de Build e Teste
| Ferramenta | Comando | Arquivo de Config |
|---|---|---|
| — | — | — |
```

### Passo 3: Criar a árvore de specs

```bash
mkdir -p specs/domain-events
mkdir -p specs/features
mkdir -p specs/infra
```

### Passo 4: Atualizar AGENTS.md

Leia o `AGENTS.md` atual e adicione (ou crie, se não existir) uma seção sobre o workflow SDD. O conteúdo a ser adicionado/mergeado:

```markdown
## SDD Workflow

Este projeto segue **Spec-Driven Development (SDD)**. Toda feature segue o fluxo:

1. `specs/features/<id>-<nome>/spec.md` — Especificação funcional (o QUE, não o COMO)
2. `specs/features/<id>-<nome>/plan.md` — Plano arquitetural (decisões técnicas, ADR)
3. `specs/features/<id>-<nome>/tasks.md` — Tarefas atômicas ordenadas
4. Implementação — Código derivado dos artefatos acima

### Regras
- **Nunca implemente sem spec.md e plan.md aprovados** pelo usuário.
- Leia `constitution.md` antes de qualquer alteração de código.
- Consulte `tech.md` antes de adicionar dependências.
- Valide a estrutura com `sdd-validate` periodicamente.
- Pergunte ao usuário ANTES de modificar `constitution.md`.

### Comandos úteis
- Inicializar estrutura: `sdd-init-repo`
- Mapear stack: `sdd-explore-tech`
- Validar conformidade: `sdd-validate`
```

### Passo 5: Reportar

Liste o que foi criado e sugira os próximos passos:
1. Execute `sdd-explore-tech` para mapear a stack.
2. Preencha `constitution.md` com as regras do projeto (sempre perguntando ao usuário).
3. Crie a primeira feature com `specs/features/001-nome-da-feature/spec.md`.

## Guardrails

- **Idempotência**: nunca sobrescreva arquivos existentes sem perguntar ao usuário.
- **Agnóstico de linguagem**: não assuma nenhuma linguagem ou framework. A estrutura SDD é independente da stack.
- **AGENTS.md preservado**: se o AGENTS.md já existir, faça merge da seção SDD sem apagar o conteúdo existente.
- **constitution.md é sagrado**: sempre lembre que regras nesse arquivo exigem confirmação do usuário.
