---
name: forge-new-skill
description: Use ONLY when the user asks to create a new opencode skill. Scaffolds the directory structure and SKILL.md following opencode conventions. Trigger keywords: "criar skill", "nova skill", "create skill", "forge skill".
---

# Forjar Nova Skill

## Propósito

Esta skill instrumentaliza o agente para gerar o alicerce completo de uma nova skill opencode, garantindo estrutura padronizada e frontmatter correto conforme a [documentação oficial](https://opencode.ai/docs/skills/).

## Estrutura de referência interna

```
.opencode/skills/forge-new-skill/
├── SKILL.md              (esta skill)
├── assets/
│   └── template-skill.md (molde para novas skills)
├── scripts/
│   └── scaffold-skill.sh (cria árvore de diretórios)
└── references/
    └── skill-format.md   (referência do formato SKILL.md)
```

## Fluxo de Execução

### Passo A: Preparar a estrutura de diretórios

1. Capture o `nome_da_skill` (lowercase, hyphen-separated, max 64 chars).
2. Verifique se `.opencode/skills/<nome_da_skill>/` já existe. Se existir, **interrompa e avise o usuário**.
3. Execute o script `scripts/scaffold-skill.sh <nome_da_skill>` para criar a árvore.
4. A estrutura resultante será:
   ```
   .opencode/skills/<nome_da_skill>/
   ├── SKILL.md
   ├── assets/
   ├── scripts/
   └── references/
   ```

### Passo B: Consultar o formato de skill opencode

1. Leia `references/skill-format.md` para confirmar o formato exato do frontmatter e corpo.
2. Se necessário, busque atualizações em `https://opencode.ai/docs/skills/`.

### Passo C: Preencher o molde

1. Leia `assets/template-skill.md`.
2. Substitua os placeholders:
   - `{{skill_name}}` → nome da skill (ex: `review-code`)
   - `{{skill_description}}` → descrição concisa com gatilhos. Formato: "Use ONLY when... <condição>. <o que faz>. Trigger keywords: ..."
   - `{{skill_title}}` → título em markdown (ex: `# Revisão de Código`)
3. Preencha as seções de **Propósito**, **Fluxo de Execução** e **Guardrails** com base no que o usuário pediu.
4. A `description` no frontmatter é **obrigatória** e deve incluir palavras-chave de gatilho no início.

### Passo D: Persistir e reportar

1. Escreva o conteúdo gerado em `.opencode/skills/<nome_da_skill>/SKILL.md`.
2. Apresente um resumo: pastas criadas, nome da skill, descrição.

## Guardrails

- **Segurança de sobrescrita**: nunca sobrescreva uma skill existente. Interrompa com aviso claro.
- **Nome válido**: apenas lowercase, hífens, dígitos. Max 64 caracteres.
- **Frontmatter obrigatório**: `name` e `description` são requeridos. Sem `description`, a skill é ignorada.
- **Isolamento**: operações de escrita restritas a `.opencode/skills/<nome_da_skill>/`.
- **Sem invenção**: use apenas o formato documentado de SKILL.md do opencode. Não invente campos de frontmatter.
