---
name: skill-forge
description: >
  Use ONLY when the user asks to create a new Hermes skill. Scaffolds the directory structure
  and SKILL.md following Hermes Agent conventions. Versões são gravadas em
  `.hermes/skills/<categoria>/<nome>/` do projeto atual e linkadas em `~/.hermes/skills/`
  via symlink, mantendo o versionamento no repo (convenção do 42_chat). Trigger keywords:
  criar skill, nova skill, create skill, forge skill, nova habilidade, criar habilidade.
version: 1.0.1
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Skill-Creation, Scaffold, Authoring]
    related_skills: [hermes-agent-skill-authoring]
    category: general
    resources:
      - SKILL.md
      - assets/template-skill.md
      - scripts/scaffold-skill.sh
      - references/skill-format.md
---

# Forjar Nova Skill (Hermes)

## Propósito

Esta skill instrumentaliza o agente para gerar o alicerce completo de uma nova skill Hermes, garantindo estrutura padronizada e frontmatter correto conforme as convenções do Hermes Agent.

### Convenção de versionamento do 42_chat

Skills vivem **versionadas no repositório** e linkadas na home via symlink:

```
<raiz-do-repo>/.hermes/skills/<categoria>/<nome>/   ← versionado (fonte da verdade)
~/.hermes/skills/<categoria>/<nome>/                 → symlink para o caminho acima
```

Portanto, **nunca** grave uma skill nova diretamente em `~/.hermes/skills/`. Crie no
repo e faça o symlink em seguida. O script `scripts/scaffold-skill.sh` faz os dois
passos atomicamente.

## Estrutura de referência

```
<raiz-do-repo>/.hermes/skills/<categoria>/<nome>/
├── SKILL.md              (skill principal — frontmatter YAML + corpo markdown)
├── assets/               (templates, imagens, dados auxiliares)
│   └── templates/        (subpasta para templates markdown)
├── scripts/              (scripts bash/python auxiliares — referenciados via skill_view)
└── references/           (documentos de referência — carregados sob demanda)
```

> Nota: o repositório 42_chat, até a data desta versão, mantém as skills **sem**
> subpasta de categoria em `.hermes/skills/<nome>/`. Esta skill, porém, **sempre**
> cria com categoria (mais organizado, escala melhor). Se quiser alinhar com o
> layout atual (sem categoria), passe `--no-category` ao `scaffold-skill.sh`.

## Pré-requisitos

- Repositório com `.hermes/skills/` já presente (criado pelo setup Hermes). Se
  não existir, o `scaffold-skill.sh` cria.
- Permissão de escrita em `~/.hermes/skills/` (para o symlink).
- `ln -sf` disponível (padrão em qualquer Unix).

## Quando usar (gatilhos)

Carregue esta skill quando o usuário disser algo como:

- "criar skill", "nova skill", "create skill"
- "forge skill", "nova habilidade", "criar habilidade"

## Fluxo de Execução

### Passo A: Coletar informações

Pergunte ao usuário (use `clarify` se for múltipla escolha):

1. **Nome da skill** (lowercase, hyphen-separated, max 64 chars). Ex: `review-code`,
   `deploy-k8s`.
2. **Categoria** (obrigatória). Categorias aceitas no 42_chat: `sdd`, `doc`,
   `agent-runtime`, `devops`, `general`. Se outra, pergunte antes.
3. **Descrição** (1-3 frases, com gatilhos / trigger keywords). Sem `description`
   a skill é **ignorada** pelo Hermes.
4. **Propósito** detalhado e fluxo de execução.

### Passo B: Validar nome e categoria

- Nome: `^[a-z0-9][a-z0-9-]*$`, max 64 chars.
- Categoria: `^[a-z0-9][a-z0-9-]*$`, max 32 chars.
- Verifique se a skill já existe:
  - No repo: `<raiz-do-repo>/.hermes/skills/<categoria>/<nome>/`
  - Na home: `~/.hermes/skills/<categoria>/<nome>/` (pode ser symlink ou dir real)
  - Se já existir (em qualquer um), **interrompa e avise**. Nunca sobrescreva.

### Passo C: Criar estrutura (script)

Execute `scripts/scaffold-skill.sh` (acesse via `skill_view(name='skill-forge',
file_path='scripts/scaffold-skill.sh')`):

```bash
bash <caminho_do_script> \
  --category <categoria> \
  --name <nome_da_skill> \
  [--repo-root <caminho-do-repo>] \
  [--no-category] \
  [--description "<descrição curta>"] \
  [--author "<nome>"] \
  [--no-symlink]
```

Argumentos:

| Flag | Default | Significado |
|---|---|---|
| `--category` | `general` | Categoria da skill |
| `--name` | (obrigatório) | Nome da skill (lowercase-hyphen) |
| `--repo-root` | CWD | Raiz do repo onde criar `.hermes/skills/` |
| `--no-category` | off | Cria skill direto em `.hermes/skills/<nome>/` (sem categoria) |
| `--description` | `TODO: preencher description` | Description do frontmatter |
| `--author` | `git config user.name` ou `phm-aguiar` | Author do frontmatter |
| `--no-symlink` | off | Pula a criação do symlink em `~/.hermes/skills/` |

O script faz, em ordem:

1. Valida nome e categoria.
2. Cria `<repo>/.hermes/skills/<categoria>/<nome>/` (ou `<repo>/.hermes/skills/<nome>/`
   com `--no-category`).
3. Cria subpastas `assets/`, `scripts/`, `references/`.
4. Escreve `SKILL.md` a partir de `assets/template-skill.md` (substitui placeholders).
5. Se `--no-symlink` não foi passado: cria/atualiza
   `~/.hermes/skills/<categoria>/<nome>` → symlink para o caminho no repo.
6. Imprime resumo.

### Passo D: Preencher o SKILL.md

O script gera o `SKILL.md` a partir do template com placeholders. Você (ou o
usuário) deve revisar e preencher:

- `## Propósito` — expandido (1-3 parágrafos).
- `## Pré-requisitos` — se houver dependências externas, env vars, ferramentas.
- `## Fluxo de Execução` — passos numerados com comandos exatos.
- `## Guardrails` — regras, pitfalls, verificações.

Para detalhes do formato, leia `references/skill-format.md` (acesse via
`skill_view(name='skill-forge', file_path='references/skill-format.md')`).

#### Frontmatter obrigatório (resumo)

```yaml
---
name: nome-da-skill
description: >                 ← OBRIGATÓRIO. Sem isso a skill é ignorada.
  Descrição concisa com gatilhos. Formato: "Use when... <condição>. <o que faz>.
  Trigger keywords: ..."
version: 0.1.0
author: <seu nome>
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tag1, tag2]
    related_skills: [skill-relacionada-1]
    resources:                 ← recomendado: lista os arquivos da skill
      - SKILL.md
      - assets/template.md
---
```

### Passo E: Validar e persistir

Antes de declarar pronto:

1. Rode `sdd-validate` (se o repo segue SDD) — não é obrigatório, mas recomendado
   pra projetos SDD.
2. Confirme que o symlink na home aponta pro caminho certo:
   ```bash
   ls -la ~/.hermes/skills/<categoria>/<nome>
   readlink -f ~/.hermes/skills/<categoria>/<nome>
   ```
3. Apresente ao usuário: caminho no repo, caminho do symlink, lista de arquivos
   criados, e peça confirmação de que o `SKILL.md` está bom como está.

### Passo F: Reportar

Apresente:
- Caminho completo no repo: `<repo>/.hermes/skills/<categoria>/<nome>/`
- Caminho do symlink: `~/.hermes/skills/<categoria>/<nome> → <repo>/...`
- Lista de arquivos criados
- Lembrete: o Hermes só descobre a skill no próximo carregamento (reindex). Em
  CLI, normalmente basta rodar `/reload-skills` ou reiniciar a sessão.

## Guardrails

- **Segurança de sobrescrita**: nunca sobrescreva uma skill existente (nem no repo
  nem na home). Se o caminho existe como diretório real (não symlink) na home,
  alerte o usuário — pode ser uma skill local de outro projeto.
- **Nome válido**: apenas `^[a-z0-9][a-z0-9-]*$`, max 64 caracteres.
- **Categoria válida**: apenas `^[a-z0-9][a-z0-9-]*$`, max 32 caracteres.
- **Frontmatter obrigatório**: `name` e `description` são requeridos. Sem
  `description`, a skill é IGNORADA pelo Hermes.
- **Convenção do repo**: sempre criar no repo primeiro, symlink depois. Nunca o
  inverso.
- **Symlink idempotente**: rodar o script duas vezes não deve quebrar nada. Se o
  symlink já existe e aponta pro lugar certo, é no-op. Se aponta pra outro lugar,
  atualize com `ln -sf`.
- **Formato Hermes**: use apenas campos documentados em
  `references/skill-format.md`. Não invente campos de frontmatter.
- **Versionamento**: bumpar `version:` no frontmatter a cada mudança incompatível
  da skill (semVer-like).

## Verificação

- [ ] Diretório `<repo>/.hermes/skills/<categoria>/<nome>/` foi criado com `SKILL.md` + subpastas
- [ ] Symlink `~/.hermes/skills/<categoria>/<nome>` aponta para o caminho no repo
- [ ] `readlink -f ~/.hermes/skills/<categoria>/<nome>` resolve para o path no repo
- [ ] Frontmatter do `SKILL.md` tem `name` e `description` (sem `description` a skill é ignorada)
- [ ] `metadata.hermes.resources` lista todos os arquivos da skill
- [ ] Rodar 2x o script não duplica nem sobrescreve (idempotente)
