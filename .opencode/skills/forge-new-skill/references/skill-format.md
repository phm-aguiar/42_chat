# Formato SKILL.md (OpenCode)

O opencode escaneia `**/SKILL.md` dentro dos diretórios de skills. O nome da pasta é o nome da skill.

## Frontmatter obrigatório

```yaml
---
name: nome-da-skill        # lowercase, hyphen-separated, max 64 chars, igual ao nome da pasta
description: Descrição...  # OBRIGATÓRIO. Sem isso a skill é ignorada. Inclua gatilhos no início.
---
```

## Frontmatter opcional

```yaml
license: MIT
compatibility: opencode>=1.0.0
metadata:
  author: nome
  version: "1.0.0"
```

## Regras da description

- Deve cobrir **o que** a skill faz e **quando** usá-la
- Escreva em terceira pessoa ("Use when...", não "I help with...")
- Inclua palavras-chave de gatilho no início
- Use "Use ONLY when..." se a skill deve ficar restrita a tópicos específicos

## Corpo

Markdown livre. Estruture com:
- Propósito
- Fluxo de execução (passos numerados)
- Guardrails / regras
- Referências a ferramentas e arquivos do projeto

## Caminhos reconhecidos

- Projeto: `.opencode/skills/<nome>/SKILL.md`
- Global: `~/.config/opencode/skills/<nome>/SKILL.md`
- Externos (auto-carregados): `~/.claude/skills/<nome>/SKILL.md`, `~/.agents/skills/<nome>/SKILL.md`

Skills de paths não-padrão devem ser registradas em `opencode.json` via `skills.paths` ou `skills.urls`.
