---
name: sdd-refactor-artifact
description: >
  Use when the user asks to refactor, normalize, format, or align an SDD artifact (spec.md,
  plan.md, tasks.md, AGENTS.md, llms.txt) to the canonical template. Reads the file, maps
  content to canonical sections, and rewrites preserving all information. For generating
  plan.md from spec.md, use sdd-generate-plan. For generating tasks.md, use sdd-generate-tasks.
  Trigger keywords: refatorar spec, refatorar plan, refatorar tasks, formatar spec.md,
  normalizar artefato, alinhar com template, padronizar spec, refactor artifact, format SDD file.
version: 1.0.1
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Refactor, Format, Normalize]
    related_skills: [sdd-generate-plan, sdd-generate-tasks, sdd-validate]
    category: sdd
    resources:
      - SKILL.md
      - references/canonical-templates.md
---

# Refatorar Artefato SDD

## Propósito

Reorganiza qualquer artefato SDD existente (`spec.md`, `plan.md`, `tasks.md`, `AGENTS.md`, `llms.txt`) para o formato canônico definido em `specs/features/002-sdd-templates/spec.md`. Preserva todo o conteúdo original, apenas reorganiza seções.

## Pré-requisitos

- O arquivo alvo deve existir e ter conteúdo.
- O template canônico está documentado em `references/canonical-templates.md` (acesse via `skill_view(name='sdd-refactor-artifact', file_path='references/canonical-templates.md')`). Leia-o antes de refatorar.

## Quando usar (gatilhos)

Carregue esta skill quando o usuário disser algo como:

- "refatorar spec", "refatorar plan", "refatorar tasks"
- "formatar spec.md", "normalizar artefato"
- "alinhar com template", "padronizar spec"
- "refactor artifact", "format SDD file"

## Fluxo de Execução

### Passo 1: Identificar o tipo de artefato

Pelo nome do arquivo alvo:

| Arquivo | Tipo | Template canônico |
|---|---|---|
| `spec.md`, `spec-*.md`, `requirements.md` | Especificação funcional | spec.md |
| `plan.md`, `plan-*.md`, `design.md` | Plano arquitetural | plan.md |
| `tasks.md`, `tasks-*.md` | Matriz de execução | tasks.md |
| `AGENTS.md` | Diretrizes para agentes | AGENTS.md |
| `llms.txt` | Navegação para LLMs | llms.txt |

Se o nome não corresponder a nenhum padrão, pergunte ao usuário qual template aplicar.

### Passo 2: Ler conteúdo atual

Leia o arquivo alvo por completo. Extraia semanticamente:
- Títulos e seções existentes
- Parágrafos de conteúdo
- Listas, checkboxes, tabelas
- Placeholders `{{...}}` ou `` não resolvidos

### Passo 3: Mapear para seções canônicas

Para cada seção canônica do template, busque conteúdo correspondente no arquivo original. Regras de mapeamento no `references/canonical-templates.md`.

### Passo 4: Apresentar diff e pedir confirmação

1. Gere o conteúdo refatorado.
2. Mostre um resumo das mudanças (seções renomeadas, movidas, adicionadas).
3. **Pergunte ao usuário se pode aplicar**. Nunca sobrescreva sem confirmação.

### Passo 5: Aplicar e reportar

Após confirmação, escreva o arquivo refatorado e liste seções adicionadas, renomeadas e conteúdo preservado.

## Guardrails

- **Preservação total**: nenhum conteúdo original pode ser descartado. Se não houver seção canônica correspondente, mova o conteúdo para `## Notas Adicionais`.
- **Idempotência**: se o arquivo já segue o formato canônico, reporte "já está em conformidade" e não modifique.
- **Placeholders**: preserve `{{...}}` e `` exatamente como estão.
- **AGENTS.md parcial**: apenas a seção SDD Workflow é refatorada. O restante fica intacto.
- **Linguagem agnóstica**: não injete stack específica. Use placeholders genéricos.
- **Nunca sobrescreva sem confirmação**: sempre apresente o resultado e pergunte antes de salvar.

## Verificação

- [ ] Arquivo alvo continua existindo e tem o mesmo número de linhas (±5% para mudanças cosméticas)
- [ ] Todas as seções originais aparecem na nova versão (busca por headings antigos deve retornar ≥ matches do original)
- [ ] Placeholders `{{...}}` foram preservados intactos
- [ ] Se o arquivo era `AGENTS.md`, a seção não-SDD está idêntica
- [ ] Usuário aprovou o diff antes de salvar
