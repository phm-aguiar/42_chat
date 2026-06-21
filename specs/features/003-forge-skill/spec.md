# spec.md: Forjar Nova Skill (forge-new-skill)

## 1. Visão Geral e Intenção de Negócios

- **Funcionalidade:** Skill que instrumentaliza o agente para criar novas skills opencode com estrutura padronizada.
- **Objetivo:** Gerar o alicerce completo de uma nova skill — diretórios, SKILL.md com frontmatter correto e conteúdo estruturado — garantindo que todas as habilidades sigam o padrão de separação (referências, scripts, assets).

## 2. Histórias de Usuário e Comportamento (BDD)

- **Como** desenvolvedor, **Quero** solicitar a criação de uma nova skill, **Para que** a estrutura de diretórios e o SKILL.md sejam gerados automaticamente no formato opencode.
- **Como** agente de IA, **Quero** um fluxo determinístico de scaffold + template + preenchimento, **Para que** eu não precise adivinhar o formato correto de SKILL.md.
- **Cenário Principal:**
  - *Dado* que o usuário fornece um `nome_da_skill` e uma descrição,
  - *Quando* a skill forge-new-skill é acionada,
  - *Então* a árvore `.opencode/skills/<nome>/` é criada com SKILL.md, assets/, scripts/ e references/, e o frontmatter `name` + `description` está preenchido corretamente.

## 3. Limites, Restrições e Não-Funcionais

- **Segurança de Sobrescrita:** Antes de criar o diretório, verificar se a pasta com o `nome_da_skill` já existe. Se existir, interromper e avisar o usuário.
- **Isolamento de Diretório:** Operações de escrita restritas a `.opencode/skills/<nome_da_skill>/`.
- **Nome Válido:** Apenas lowercase, hífens e dígitos. Máximo de 64 caracteres.
- **Frontmatter Obrigatório:** `name` (idêntico ao nome da pasta) e `description` (com gatilhos). Sem `description` a skill é ignorada pelo opencode.
- **Fidelidade ao Formato:** Nunca inventar campos de frontmatter. Usar apenas o documentado em `https://opencode.ai/docs/skills/`: `name`, `description`, `license`, `compatibility`, `metadata`.

## 4. Checklist de Ambiguidade para a IA

- [ ] Deve-se oferecer a opção de criar a skill no escopo global (`~/.config/opencode/skills/`) ou apenas no projeto?
- [ ] O template deve incluir seções opcionais como `## Exemplos` ou manter o mínimo?
- [ ] A skill deve suportar criação de subagentes também (`.opencode/agents/`) ou apenas skills?

---

# Notas Adicionais

## Fluxo de Execução (preservado da spec original)

### Passo A: Preparar a estrutura de diretórios
1. Capturar o `nome_da_skill` (lowercase, hyphen-separated, max 64 chars).
2. Verificar se `.opencode/skills/<nome>/` já existe. Se sim, interromper.
3. Executar `scripts/scaffold-skill.sh <nome>` para criar a árvore:
   ```
   .opencode/skills/<nome>/
   ├── SKILL.md
   ├── assets/
   ├── scripts/
   └── references/
   ```

### Passo B: Consultar o formato de skill opencode
1. Ler `references/skill-format.md` para confirmar o formato do frontmatter.
2. Se necessário, buscar atualizações em `https://opencode.ai/docs/skills/`.

### Passo C: Preencher o molde
1. Ler `assets/template-skill.md`.
2. Substituir placeholders: `{{skill_name}}`, `{{skill_description}}`, `{{skill_title}}`.
3. Preencher seções Propósito, Fluxo de Execução e Guardrails.

### Passo D: Persistir e reportar
1. Escrever em `.opencode/skills/<nome>/SKILL.md`.
2. Apresentar resumo: pastas criadas, nome, descrição.

## Mapa do Inventário (infraestrutura interna da skill)

- **`references/`**: Contém `skill-format.md` com o formato canônico de SKILL.md.
- **`scripts/`**: Contém `scaffold-skill.sh` para criar a árvore de diretórios.
- **`assets/`**: Contém `template-skill.md`, o molde estrutural com placeholders.
