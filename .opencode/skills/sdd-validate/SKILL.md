---
name: sdd-validate
description: Use when the user asks to validate or audit the SDD structure of a repository. Checks for required directories (.github/memory/, specs/), required files (constitution.md, tech.md, spec.md, plan.md, tasks.md per feature), and reports missing or malformed artifacts. Trigger keywords: "validar SDD", "validate sdd", "auditar estrutura", "check sdd", "verificar conformidade", "audit structure".
---

# Validar Estrutura SDD

## Propósito

Audita a estrutura do repositório para verificar conformidade com o padrão Spec-Driven Development (SDD). Detecta diretórios ausentes, artefatos faltantes e inconsistências.

## Critérios de validação

### Nível 1: Memória de Contexto Global

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Diretório memory | `.github/memory/` | Sim |
| Constituição | `.github/memory/constitution.md` | Sim |
| Stack tecnológica | `.github/memory/tech.md` | Sim |

### Nível 2: Diretório de Especificações

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Raiz specs | `specs/` | Sim |
| Domain events | `specs/domain-events/` | Sim |
| Features | `specs/features/` | Sim |
| Infra | `specs/infra/` | Sim |

### Nível 3: Features (por feature numerada)

| Artefato | Caminho | Obrigatório? |
|---|---|---|
| Especificação | `specs/features/<id>-<nome>/spec.md` | Sim |
| Plano | `specs/features/<id>-<nome>/plan.md` | Sim |
| Tarefas | `specs/features/<id>-<nome>/tasks.md` | Sim |

## Fluxo de Execução

### Passo 1: Validar Memória de Contexto

1. Verifique se `.github/memory/` existe.
2. Verifique se `constitution.md` existe e não está vazio.
3. Verifique se `tech.md` existe e não está vazio.

Reporte cada item como: PASS, FAIL (ausente), ou WARN (existe mas está vazio).

### Passo 2: Validar specs/

1. Verifique se `specs/` existe.
2. Verifique subdiretórios obrigatórios: `domain-events/`, `features/`, `infra/`.
3. Se `specs/features/` estiver vazio, reporte WARN (sem features ainda).

### Passo 3: Validar cada feature

Para cada subdiretório em `specs/features/`:
1. Verifique se o nome segue o padrão `<id numérico>-<nome>`.
2. Verifique `spec.md` — existe? não está vazio? contém seções de aceite?
3. Verifique `plan.md` — existe? não está vazio?
4. Verifique `tasks.md` — existe? não está vazio? contém checkboxes?

### Passo 4: Validar AGENTS.md

1. Verifique se `AGENTS.md` existe.
2. Verifique se contém referência ao workflow SDD.

### Passo 5: Sumário

Apresente um relatório consolidado:

```
SDD Validation Report
=====================

.github/memory/            PASS
  constitution.md          PASS
  tech.md                  WARN (vazio — execute sdd-explore-tech)

specs/                     PASS
  domain-events/           PASS (vazio — esperado se sem eventos)
  features/                PASS
    001-start-repo/        FAIL — plan.md ausente
  infra/                   PASS

AGENTS.md                  PASS (SDD workflow presente)

Resultado: 8/9 checks passaram
Ação sugerida: criar specs/features/001-start-repo/plan.md
```

## Guardrails

- **Não crie arquivos**: esta skill é somente leitura. Apenas reporte, nunca corrija.
- **Features sem numeração**: reporte WARN para diretórios que não seguem o padrão `<id>-<nome>`.
- **Arquivos vazios**: diferencie entre "ausente" (FAIL) e "vazio" (WARN). Um arquivo vazio pode estar em progresso.
- **Projetos novos**: um repositório recém-inicializado com `sdd-init-repo` sem features ainda deve passar com WARNs aceitáveis.
