---
name: sdd-brainstorm
description: >
  Use when the user wants to discuss, refine, or brainstorm a new feature idea
  before writing a spec. Conducts an interactive interview using clarify() to
  gather requirements, constraints, and success criteria one question at a time,
  then generates spec.md in the SDD format under specs/features/<id>-<slug>/.
  Trigger keywords: brainstorm, brain storm, discutir ideia, refinar ideia,
  pensar feature, nova feature, nova ideia, discutir feature, entrevista,
  interview, discovery, bora pensar, vamos pensar, como voce faria.
version: 0.2.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Brainstorm, Spec, Discovery, Interactive-Interview, Clarify]
    related_skills: [wiki-query, sdd-init-repo, sdd-explore-tech, sdd-generate-plan, sdd-generate-tasks, sdd-validate, sdd-refactor-artifact]
    category: sdd
    created: "2026-06-12"
    resources:
      - SKILL.md
      - references/interview-dimensions.md
      - assets/spec-template.md
---

# Brainstorm Interativo → Spec SDD

> Entry point do pipeline SDD. Transforma ideias em `spec.md` via entrevista com `clarify()`.

## Propósito

Conduz entrevista interativa com `clarify()` — uma pergunta por vez, múltipla escolha —
para extrair propósito, escopo, constraints, critérios de sucesso e trade-offs de uma feature.
Gera `spec.md` e transiciona para `sdd-generate-plan`.

**HARD-GATE:** Nunca implemente antes do spec aprovado. Vale pra TODA feature, incluindo as "simples".

## Pré-requisitos

- Repo inicializado com SDD (`sdd-init-repo`): `.github/memory/`, `specs/features/`.
- Ferramenta `clarify` habilitada (default).
- Se `tech.md` ou `constitution.md` estiverem vazios, alerte mas prossiga.

## Fluxo de Execução

8 passos. Use `todo` para trackear.

### Passo 1: Explorar contexto

```bash
read_file(path=".github/memory/tech.md")
read_file(path=".github/memory/constitution.md")
search_files(pattern="*", target="files", path="specs/features/")
```

### Passo 2: Avaliar escopo — decompor se necessário

Se a ideia descreve múltiplos subsistemas independentes, alerte e use `clarify()` para
confirmar decomposição. Cada subsistema vira feature própria com ciclo completo.

### Passo 3: Entrevista interativa

Carregue as dimensões da entrevista:

```
skill_view(name="sdd-brainstorm", file_path="references/interview-dimensions.md")
```

Cubra cada dimensão com `clarify()` — **uma pergunta por vez**, múltipla escolha quando possível.
Só avance para a próxima dimensão quando a atual estiver clara.

**Loop de reavaliação:** após cada resposta, avalie se já tem insumos para um spec sem
ambiguidades. Se sim, avance. Se não, continue perguntando. Se o usuário disser "confio
em você", preencha com defaults razoáveis e valide no Passo 4.

### Passo 4: Propor 2-3 abordagens

Use `clarify()` para apresentar abordagens com trade-offs e recomendação.

### Passo 5: Gerar spec.md

Carregue o template canônico:

```
skill_view(name="sdd-brainstorm", file_path="assets/spec-template.md")
```

Substitua os placeholders `{{...}}` pelos insumos coletados. Naming: próximo ID
incremental de `specs/features/`, slug curto (max 3 palavras, lowercase, hífens).

```
write_file(path="specs/features/<id>-<slug>/spec.md", content="<spec gerada>")
```

### Passo 6: Spec self-review

Revise o `spec.md`: placeholders? contradições? escopo focado? ambiguidades?
Corrija inline e avance.

### Passo 7: Gate de aprovação

Use `clarify()` para aprovação explícita. Se o usuário pedir ajustes, faça e re-apresente.

### Passo 8: Transição para pipeline SDD

```
skill_view(name="sdd-generate-plan")
```

Pipeline: brainstorm → spec.md → sdd-generate-plan → plan.md → sdd-generate-tasks → tasks.md

## Guardrails

- **HARD-GATE:** sem implementação antes de spec aprovado.
- **Uma pergunta por `clarify()`:** nunca empilhe. Quebre tópicos em múltiplas chamadas.
- **Múltipla escolha sempre que possível:** "Other" como escape para resposta livre.
- **YAGNI implacável:** spec com mínimo viável, não máximo possível.
- **Reavaliação contínua:** avance quando tiver clareza, não continue perguntando por inércia.
- **Respeite constitution.md:** spec não pode violar portões/anti-padrões definidos.
  Se inevitável, alerte o usuário e peça autorização explícita.
- **Idempotência:** detecte spec existente e pergunte se quer refinar ou começar do zero.
- **Id incremental:** derive do que existe em `specs/features/`. Vazio = comece em `001`.

## Verificação

- [ ] `spec.md` existe em `specs/features/<id>-<slug>/`
- [ ] Seções canônicas preenchidas (sem "TODO" ou "TBD")
- [ ] Propósito, escopo, cenários, edge cases, constraints e critérios de sucesso presentes
- [ ] Usuário aprovou explicitamente (via `clarify`)
- [ ] `sdd-generate-plan` invocado ou pronto para aprovação
