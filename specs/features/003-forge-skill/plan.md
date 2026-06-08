# plan.md: Plano de Implementação Técnica — Forjar Nova Skill

## 1. Metadados do Plano

- **Stack Tecnológico:** opencode skill system (SKILL.md com frontmatter YAML), bash scripts auxiliares.
- **Feature Fonte:** `specs/features/003-forge-skill/spec.md`
- **Escopo:** Skill `forge-new-skill` que automatiza a criação de novas skills opencode com estrutura padronizada.

## 2. Design de Contratos e Fronteiras

- **Contrato de Skill:** Toda skill opencode segue o formato `SKILL.md` com frontmatter obrigatório (`name`, `description`) e corpo markdown livre.
- **Estrutura de Diretórios:** Toda skill criada pelo forge-new-skill contém `SKILL.md` + subpastas `assets/`, `scripts/`, `references/`.
- **Validação de Nome:** lowercase, hyphen-separated, ≤ 64 chars, idêntico ao nome da pasta.

## 3. Decisões Arquiteturais e Justificativas

- **Decisão:** Script `scaffold-skill.sh` como executor da criação de diretórios, não lógica inline no SKILL.md.
  - **Justificativa:** Separação de concerns — o SKILL.md descreve o fluxo, o script executa. Facilita testes isolados do script.
  - **Alternativa Rejeitada:** Lógica inline no SKILL.md usando comandos bash. Rejeitada — difícil de testar e manter.

- **Decisão:** Template `template-skill.md` com placeholders `{{...}}` como molde base.
  - **Justificativa:** Placeholders são semanticamente distintos de conteúdo final. O refatorador (`sdd-refactor-artifact`) já sabe preservá-los.
  - **Alternativa Rejeitada:** Template com comentários HTML (`<!-- -->`). Rejeitada — conflita com frontmatter YAML e é ambíguo com comentários reais.

- **Decisão:** Referência `skill-format.md` como fonte local do formato, com fallback para `https://opencode.ai/docs/skills/`.
  - **Justificativa:** Cache local evita dependência de rede. Fallback garante atualização quando necessário.
  - **Alternativa Rejeitada:** Apenas docs online. Rejeitada — frágil em ambientes offline ou com rate limiting.

## 4. Auditoria de Constituição

- [x] A skill opera apenas dentro de `.opencode/skills/`? Sim — isolamento de diretório é um guardrail explícito.
- [x] A skill valida nome antes de criar? Sim — `scaffold-skill.sh` valida regex e tamanho.
- [x] A skill pergunta antes de sobrescrever? Sim — verificação de existência com interrupção e aviso.
