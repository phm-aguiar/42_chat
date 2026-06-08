---
name: sdd-generate-plan
description: Use ONLY when the user asks to generate or create a plan.md for an SDD feature from an existing spec.md. Reads spec.md, tech.md, and constitution.md to produce an architectural plan with 4 canonical sections: Metadados, Contratos e Fronteiras, Decisões Arquiteturais (ADR), Auditoria de Constituição. Trigger keywords: "gerar plan", "criar plan.md", "generate plan", "criar plano", "generate architectural plan".
---

# Gerar Plano Arquitetural (plan.md)

## Propósito

Gera um `plan.md` canônico para uma feature SDD a partir do `spec.md` existente, consultando o contexto do projeto (`tech.md`, `constitution.md`).

## Pré-requisitos

- A feature deve ter `spec.md` preenchido.
- `.github/memory/tech.md` e `.github/memory/constitution.md` devem existir. Se estiverem vazios, alerte o usuário e use placeholders.

## Fluxo de Execução

### Passo 1: Identificar a feature

O usuário deve informar o diretório da feature (ex: `specs/features/003-forge-skill`). Se não informar, pergunte.

### Passo 2: Ler fontes

Leia nesta ordem:

1. `spec.md` da feature — extraia: funcionalidade, objetivo, cenários BDD, restrições, checklist.
2. `.github/memory/tech.md` — extraia linguagens, frameworks, ferramentas de build/teste.
3. `.github/memory/constitution.md` — extraia portões de qualidade, restrições e anti-padrões.

### Passo 3: Gerar as 4 seções canônicas

Preencha cada seção com base nas fontes lidas:

#### 1. Metadados do Plano

```markdown
## 1. Metadados do Plano
- **Stack Tecnológico:** {{linguagens e frameworks extraídos de tech.md}}
- **Feature Fonte:** `specs/features/{{id}}-{{slug}}/spec.md`
- **Escopo:** {{resumo de 1 frase do que será implementado}}
```

#### 2. Design de Contratos e Fronteiras

- Se o spec menciona APIs, eventos, schemas ou contratos, documente-os aqui.
- Se o spec usa placeholders `{{...}}` para contratos, preserve-os.
- Se não houver menção a contratos: "**Contrato:** Nenhum contrato formal neste estágio."

```markdown
## 2. Design de Contratos e Fronteiras
- **Contrato:** {{contratos formais afetados ou "Nenhum contrato formal neste estágio."}}
- **Convenção:** {{padrões de nomenclatura, estrutura de diretórios}}
```

#### 3. Decisões Arquiteturais e Justificativas

Para cada decisão implícita no spec, formalize como mini-ADR:

```markdown
## 3. Decisões Arquiteturais e Justificativas

- **Decisão:** {{o que foi decidido}}
  - **Justificativa:** {{por que esta escolha}}
  - **Alternativa Rejeitada:** {{o que foi descartado e por quê}}
```

**Regra**: extraia decisões do spec (ex: "usar X para Y" vira ADR). Se o spec não contiver decisões explícitas, gere ao menos uma sobre stack ou estrutura de diretórios.

#### 4. Auditoria de Constituição

Checklist verificando cada regra do `constitution.md`:

```markdown
## 4. Auditoria de Constituição

- [x] {{regra do constitution.md}} — {{como o plano respeita ou por que não se aplica}}
```

Se `constitution.md` estiver vazio, use: `- [ ] Constitution.md está vazio — nenhuma regra para auditar.`

### Passo 4: Apresentar e confirmar

Mostre o plano completo. Destaque:
- Stack detectada
- Número de ADRs geradas
- Itens da auditoria de constituição

**Pergunte ao usuário se pode salvar.** Nunca escreva sem confirmação.

### Passo 5: Salvar

Escreva `plan.md` no diretório da feature.

## Guardrails

- **Não invente stack**: use apenas o que está em `tech.md`. Se estiver vazio, use placeholders `{{...}}` e alerte.
- **ADR mínimo**: se o spec não sugerir decisões, gere pelo menos 1 ADR estrutural.
- **Preserve placeholders**: `{{...}}` e `` do spec devem ser preservados no plan.
- **Idempotência**: se `plan.md` já existe, pergunte se deve sobrescrever ou mesclar.
