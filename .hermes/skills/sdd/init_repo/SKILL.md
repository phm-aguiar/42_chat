---
name: sdd-init_repo
description: >
  Use ONLY when the user asks to initialize a repository with the Spec-Driven Development (SDD)
  structure. Creates .github/memory/ (constitution.md, tech.md), /specs/ hierarchy, and updates
  AGENTS.md with SDD workflow. Language-agnostic and reusable across any tech stack. Trigger
  keywords: iniciar SDD, init sdd, estrutura sdd, setup sdd, inicializar repo SDD, criar estrutura SDD.
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Init, Scaffold, Project-Setup]
    related_skills: [wiki-query, sdd-explore_tech, sdd-validate, sdd-refactor_artifact, sdd-brainstorm]
    category: sdd
    resources:
      - SKILL.md
      - assets/templates/constitution-template.md
      - assets/templates/plan-template.md
      - assets/templates/spec-template.md
      - assets/templates/tasks-template.md
      - references/sdd-workflow-agents-md.md
      - references/agents-md-sdd-section.md
      - scripts/scaffold-sdd.sh
---

# Inicializar Repositório SDD

## Propósito

Inicializa ou adapta um repositório para Spec-Driven Development (SDD), criando a
hierarquia `.github/memory/` e `/specs/` e atualizando `AGENTS.md` com o workflow SDD.

## Pré-requisitos

Nenhum. Entry point do fluxo SDD. Funciona em repositórios vazios ou existentes.

## Estrutura alvo

```
<repo>/
├── .github/memory/
│   ├── constitution.md       ← Portões de qualidade, restrições, anti-padrões
│   └── tech.md               ← Stack tecnológica homologada
├── specs/
│   ├── domain-events/        ← Contratos formais (AsyncAPI, OpenAPI)
│   ├── features/             ← Features numeradas (001-nome/spec.md, plan.md, tasks.md)
│   └── infra/                ← Declarações de infraestrutura
└── AGENTS.md                 ← Atualizado com workflow SDD
```

## Fluxo de Execução

### Passo 1: Verificar estado atual

Liste a raiz. Se `.github/memory/` ou `specs/` já existirem, pergunte se deve
preservar ou recriar.

### Passo 2: Criar Memória de Contexto Global

Carregue o template da constituição e crie os arquivos:

```
skill_view(name="sdd-init_repo", file_path="assets/templates/constitution-template.md")
```

Crie `constitution.md` com o conteúdo do template. Crie `tech.md` como placeholder
que referencia `sdd-explore_tech` para preenchimento futuro.

Se preferir automação: `bash scripts/scaffold-sdd.sh` (acesse via
`skill_view(name='sdd-init_repo', file_path='scripts/scaffold-sdd.sh')`).

### Passo 3: Criar árvore de specs

```bash
mkdir -p specs/domain-events specs/features specs/infra
```

### Passo 4: Atualizar AGENTS.md

Carregue o template da seção SDD:

```
skill_view(name="sdd-init_repo", file_path="references/sdd-workflow-agents-md.md")
```

Leia o `AGENTS.md` atual. Se já existir seção `## SDD Workflow`, pule (idempotente).
Senão, faça merge do bloco. Se `AGENTS.md` não existir, crie-o com o bloco.

### Passo 5: Reportar e sugerir próximos passos

1. Execute `sdd-explore_tech` para mapear a stack.
2. Preencha `constitution.md` com as regras do projeto (sempre perguntando ao usuário).
3. Crie a primeira feature via `sdd-brainstorm`.

## Guardrails

- **Idempotência:** nunca sobrescreva arquivos existentes sem perguntar.
- **Agnóstico de linguagem:** não assuma stack. A estrutura SDD é independente.
- **AGENTS.md preservado:** faça merge da seção SDD sem apagar conteúdo existente.
- **constitution.md é sagrado:** regras nesse arquivo exigem confirmação do usuário.

## Verificação

- [ ] `.github/memory/constitution.md` e `tech.md` existem
- [ ] `specs/{domain-events,features,infra}/` são diretórios
- [ ] `AGENTS.md` contém seção "## SDD Workflow"
- [ ] Se algo já existia, usuário aprovou sobrescrever/preservar
