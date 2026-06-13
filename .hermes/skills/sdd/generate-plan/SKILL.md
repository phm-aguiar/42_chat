---
name: sdd-generate-plan
description: >
  Use ONLY when the user asks to generate or create a plan.md for an SDD feature from an
  existing spec.md. Reads spec.md, tech.md, and constitution.md to produce an architectural
  plan with 4 canonical sections: Metadados, Contratos e Fronteiras, Decisões Arquiteturais
  (ADR), Auditoria de Constituição. Trigger keywords: gerar plan, criar plan.md, generate plan,
  criar plano, generate architectural plan.
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Plan, Architecture, ADR]
    related_skills: [sdd-generate-tasks, sdd-refactor-artifact, sdd-validate, sdd-brainstorm]
    category: sdd
    resources:
      - SKILL.md
---

# Gerar Plano Arquitetural (plan.md)

## Propósito

Gera `plan.md` a partir do `spec.md`, `tech.md` e `constitution.md`.

## Pré-requisitos

- Feature deve ter `spec.md` preenchido.
- `.github/memory/tech.md` e `constitution.md` devem existir (vazios = placeholders).

## Fluxo de Execução

### Passo 1: Identificar a feature

Usuário informa o diretório (ex: `specs/features/003-forge-skill`). Se não, pergunte.

### Passo 2: Ler fontes

1. `spec.md` → funcionalidade, cenários BDD, restrições, checklist.
2. `tech.md` → linguagens, frameworks, build/teste.
3. `constitution.md` → portões de qualidade, restrições, anti-padrões.

### Passo 3: Gerar as 4 seções canônicas

#### 1. Metadados do Plano

```markdown
## 1. Metadados do Plano
- **Stack Tecnológico:** {{linguagens e frameworks de tech.md}}
- **Feature Fonte:** `specs/features/{{id}}-{{slug}}/spec.md`
- **Escopo:** {{resumo 1 frase do que será implementado}}
```

#### 2. Design de Contratos e Fronteiras

Se o spec menciona APIs/eventos/schemas, documente. Se usar `{{...}}`, preserve.
Se não houver menção: "Nenhum contrato formal neste estágio."

```markdown
## 2. Design de Contratos e Fronteiras
- **Contrato:** {{contratos formais ou "Nenhum contrato formal neste estágio."}}
- **Convenção:** {{padrões de nomenclatura, estrutura de diretórios}}
```

#### 3. Decisões Arquiteturais e Justificativas (ADR)

Para cada decisão no spec, formalize como mini-ADR. Se o spec não tiver decisões
explícitas, gere ao menos 1 sobre stack ou estrutura.

```markdown
## 3. Decisões Arquiteturais e Justificativas
- **Decisão:** {{o que foi decidido}}
  - **Justificativa:** {{por que esta escolha}}
  - **Alternativa Rejeitada:** {{o que foi descartado e por quê}}
```

#### 4. Auditoria de Constituição

Checklist contra cada regra do `constitution.md`:

```markdown
## 4. Auditoria de Constituição
- [x] {{regra}} — {{como o plano respeita ou por que não se aplica}}
```

Se vazio: `- [ ] Constitution.md está vazio — nenhuma regra para auditar.`

### Passo 4: Apresentar e salvar

Mostre stack, número de ADRs, itens da auditoria. **Pergunte antes de salvar.**

```bash
write_file(path="specs/features/<id>-<slug>/plan.md", content="<plano>")
```

## Guardrails

- **Não invente stack:** use apenas `tech.md`. Vazio = placeholders `{{...}}`.
- **ADR mínimo:** 1 ADR estrutural se o spec não sugerir decisões.
- **Preserve placeholders:** `{{...}}` do spec devem ser preservados.
- **Idempotência:** se `plan.md` existe, pergunte se sobrescreve ou mescla.

## Verificação

- [ ] `plan.md` escrito em `specs/features/<id>-<slug>/`
- [ ] 4 seções canônicas presentes
- [ ] Pelo menos 1 ADR gerada
- [ ] Se constitution.md tem regras, todas listadas na auditoria
- [ ] Usuário aprovou antes de salvar
