# plan.md: Plano de Implementação Técnica — Templates Canônicos SDD

## 1. Metadados do Plano

- **Stack Tecnológico:** Markdown + frontmatter YAML. Ferramentas de validação: bash scripts, sdd-validate.
- **Feature Fonte:** `specs/features/002-sdd-templates/spec.md`
- **Escopo:** Definição e manutenção dos formatos canônicos de spec.md, plan.md, tasks.md, AGENTS.md e llms.txt.

## 2. Design de Contratos e Fronteiras

- **Contrato de Formato:** Cada artefato tem um número fixo de seções canônicas (4 para spec.md, 4 para plan.md, N fases para tasks.md, 2 para AGENTS.md SDD section, estrutura livre para llms.txt).
- **Extensibilidade:** Seções não-mapeadas pelo refatorador vão para `## Notas Adicionais`. Novos campos de frontmatter devem ser validados contra o schema do opencode.
- **Fonte da Verdade:** `spec-elementos-sdd.md` (agora em `002-sdd-templates/spec.md`) é o documento raiz. Alterações aqui propagam para `sdd-refactor-artifact/references/canonical-templates.md`.

## 3. Decisões Arquiteturais e Justificativas

- **Decisão:** 4 seções canônicas fixas para spec.md e plan.md.
  - **Justificativa:** Número suficiente para cobrir o essencial sem sobrecarregar. Facilita mapeamento automático pelo refatorador.
  - **Alternativa Rejeitada:** Seções livres (cada feature define suas próprias). Rejeitada — agentes de IA precisam de estrutura previsível.

- **Decisão:** Tasks.md usa numeração global `T001`, `T002` (não reinicia por fase).
  - **Justificativa:** Identificadores únicos permitem referência cruzada exata ("Depende de T004") sem ambiguidade de fase.
  - **Alternativa Rejeitada:** Numeração por fase (`F1-T1`, `F2-T1`). Rejeitada — mais verbosa sem ganho real.

- **Decisão:** Plan.md inclui seção obrigatória "Auditoria de Constituição".
  - **Justificativa:** Força o autor a verificar conformidade com constitution.md antes de aprovar o plano.
  - **Alternativa Rejeitada:** Checklist separada. Rejeitada — integração no plan.md torna a auditoria parte do fluxo, não um passo extra.

## 4. Auditoria de Constituição

- [x] Os templates são agnósticos de stack? Sim — placeholders `{{...}}` garantem independência.
- [x] Placeholders não preenchidos bloqueiam implementação? Sim — `sdd-refactor-artifact` preserva `{{...}}` e o AGENTS.md instrui a não preencher sem usuário.
- [x] Há risco de fragmentação (múltiplos formatos concorrentes)? Não — `canonical-templates.md` é a fonte única referenciada pelo refatorador.
