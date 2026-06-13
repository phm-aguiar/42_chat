---
name: sdd-validate
description: >
  Use when the user asks to validate or audit the SDD structure of a repository. Checks for
  required directories (.github/memory/, specs/), required files (constitution.md, tech.md,
  spec.md, plan.md, tasks.md per feature), and reports missing or malformed artifacts. Trigger
  keywords: validar SDD, validate sdd, auditar estrutura, check sdd, verificar conformidade,
  audit structure.
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Validate, Audit, Quality]
    related_skills: [sdd-init-repo, sdd-refactor-artifact, sdd-brainstorm]
    category: sdd
    resources:
      - SKILL.md
      - scripts/check-sdd.sh
---

# Validar Estrutura SDD

## Propósito

Audita o repositório para verificar conformidade com SDD. Detecta diretórios
ausentes, artefatos faltantes e inconsistências. **Somente leitura — nunca corrija.**

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

Verifique `.github/memory/`, `constitution.md`, `tech.md`.
Reporte: PASS (existe e não vazio), FAIL (ausente), WARN (existe mas vazio).

### Passo 2: Validar specs/

Verifique `specs/` e subdiretórios. `features/` vazio = WARN (sem features ainda).

### Passo 3: Validar cada feature

Para cada `specs/features/<id>-<nome>/`:
- Nome segue `<id numérico>-<nome>`?
- `spec.md`, `plan.md`, `tasks.md`: existe? não vazio? conteúdo canônico?

### Passo 4: Validar AGENTS.md

Existe? Contém referência ao workflow SDD?

### Passo 5: Sumário

Apresente relatório no formato:

```
SDD Validation Report
=====================
.github/memory/            PASS
  constitution.md          PASS
  tech.md                  WARN (vazio — execute sdd-explore-tech)
...
Resultado: 8/9 checks passaram
Ação sugerida: ...
```

### Automação (opcional)

```bash
skill_view(name="sdd-validate", file_path="scripts/check-sdd.sh")
```

## Guardrails

- **Read-only:** apenas reporte, nunca crie ou modifique arquivos.
- **Features sem numeração:** WARN para diretórios fora do padrão `<id>-<nome>`.
- **Arquivos vazios:** diferencie FAIL (ausente) de WARN (vazio/em progresso).
- **Projetos novos:** repo recém-inicializado sem features = WARNs aceitáveis.

## Verificação

- [ ] Relatório segue formato PASS/FAIL/WARN com resumo e ações sugeridas
- [ ] Cada FAIL tem ação sugerida
- [ ] Nenhum arquivo foi criado/modificado (read-only)
