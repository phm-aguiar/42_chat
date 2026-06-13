# Formato de Skills Hermes — Referência

Documento de referência para autores de skills no Hermes Agent. Use este guia
junto com o template em `assets/template-skill.md`.

## 1. Anatomia de uma skill

Uma skill é um diretório com pelo menos um arquivo `SKILL.md` (com frontmatter
YAML) e, opcionalmente, subpastas para organizar conteúdo:

```
<nome-da-skill>/
├── SKILL.md              ← Obrigatório. Frontmatter + corpo markdown.
├── assets/               ← Templates, imagens, dados estáticos.
│   └── templates/        ← Subpasta convencional para templates .md.
├── scripts/              ← Scripts bash/python auxiliares (chamados pelo SKILL.md).
└── references/           ← Documentos longos carregados sob demanda.
```

## 2. Convenção de versionamento do 42_chat

No projeto 42_chat, skills são **versionadas no repositório** e linkadas na
home do Hermes via symlink:

```
<repo>/.hermes/skills/<categoria>/<nome>/   ← FONTE DA VERDADE (git)
~/.hermes/skills/<categoria>/<nome>/        → symlink para o caminho acima
```

Regras:

- **Sempre** criar a skill primeiro no repo.
- **Depois** criar o symlink em `~/.hermes/skills/`.
- O script `scripts/scaffold-skill.sh` (na skill `skill-forge`) faz os dois.
- Nunca criar diretamente em `~/.hermes/skills/`. Se já existir um diretório
  real ali (não symlink), provavelmente é de outro projeto — abortar.

### Quando NÃO usar categoria

A maioria das skills do repo atual vive em `.hermes/skills/<nome>/` (sem
subpasta de categoria). O scaffold padrão da `skill-forge` cria COM categoria
porque escala melhor. Se quiser alinhar ao layout flat, use `--no-category`.

## 3. Frontmatter YAML (obrigatório)

O frontmatter é o cabeçalho entre `---` no início do `SKILL.md`. Dois campos
são **obrigatórios** (sem eles a skill é ignorada pelo Hermes):

```yaml
---
name: nome-da-skill              ← Obrigatório. Match o nome do diretório.
description: >                    ← Obrigatório. Sem isso a skill NÃO é roteada.
  Descrição concisa com gatilhos. Use when... <condição>. <o que faz>.
  Trigger keywords: palavra1, palavra2, ...
version: 1.0.0
author: Seu Nome <voce@exemplo.com>
license: MIT
platforms: [linux, macos, windows]    ← Plataformas suportadas
metadata:
  hermes:
    tags: [Tag1, Tag2, Tag3]          ← Tags para busca
    related_skills: [outra-skill]     ← Skills complementares
    category: sdd                     ← Categoria (espelha o diretório)
    created: 2025-01-15               ← Data de criação
    updated: 2025-02-01               ← Data da última atualização
    resources:                        ← Lista de arquivos que a skill declara
      - SKILL.md
      - assets/template.md
      - scripts/auxiliar.sh
---
```

### 2.1. Campo `description` — o mais importante

É o que o roteador do Hermes usa para decidir **quando** carregar a skill. Sem
ele, a skill é IGNORADA mesmo estando no diretório certo.

Boas práticas:

- Máximo 5-6 linhas.
- Primeira frase: "Use when/ONLY when..." indicando a condição de carga.
- Segunda frase: o que a skill faz.
- Última frase: `Trigger keywords: a, b, c, "frase exata"`.
- Use `>` (folded scalar) pra quebrar linhas limpas.

Exemplo bom:

```yaml
description: >
  Use when the user asks to validate or audit the SDD structure of a repository.
  Checks for required directories (.github/memory/, specs/) and files
  (constitution.md, tech.md, spec.md, plan.md, tasks.md). Trigger keywords:
  validar SDD, validate sdd, auditar estrutura, check sdd.
```

Exemplo ruim (vago, sem gatilhos):

```yaml
description: Validate stuff.
```

### 2.2. Campo `name`

- Match exato com o nome do diretório: se a skill está em
  `.hermes/skills/sdd/validate/`, então `name: validate`.
- Apenas `^[a-z0-9][a-z0-9-]*$`, max 64 chars.
- Sem espaços, sem underscores, sem acentos.

### 2.3. Campo `version`

SemVer-like (MAJOR.MINOR.PATCH):

- MAJOR: mudança incompatível no fluxo de execução.
- MINOR: nova feature ou passo opcional.
- PATCH: clarificação, correção de typo, novo exemplo.

Bumpar SEMPRE que o `SKILL.md` for alterado. Outros arquivos da skill
(assets, scripts, references) também contam.

## 4. Corpo do SKILL.md (markdown)

Estrutura recomendada (não obrigatória, mas o `skill-forge` gera nesse formato):

```markdown
# <Nome da skill>

## Propósito
1-3 parágrafos. O que faz, quando carregar, que problema resolve.

## Pré-requisitos
Dependências externas. "Nenhum." se for o caso.

## Quando usar (gatilhos)         ← OPCIONAL mas útil
Lista de trigger keywords.

## Fluxo de Execução
### Passo 1: <nome>
Descrição + comando exato (se houver).
### Passo 2: <nome>
...

## Guardrails
- Regra 1
- Regra 2
- Idempotência: o que acontece rodando 2x?
- Erros comuns / pitfalls reais

## Verificação                     ← OPCIONAL mas útil
Como saber que funcionou.
```

## 5. Boas práticas

### Descrições keywords-rich
O roteador lê só a `description`. Coloque TODOS os sinônimos que o usuário
pode usar, em PT e EN se o agente é bilíngue.

### Comandos exatos, não "rodar tal coisa"
```markdown
# BOM
bash scripts/check-sdd.sh

# RUIM
Execute o script de validação.
```

### Guardrails com pitfallls reais
Não escreva "cuidado com X" genericamente. Escreva "Em 12/jun/2026 o agente X
caiu num loop infinito ao processar Y. Solução: adicionar timeout no passo Z".

### Idempotência explícita
Toda skill que escreve arquivos DEVE declarar o que acontece rodando 2x.

### Sempre referencie paths relativos
```markdown
# BOM
Use `assets/template.md` como base.

# RUIM
Use `/home/zeenyt__/Projetos/42_chat/.hermes/skills/foo/assets/template.md`.
```

## 6. Erros comuns

| Erro | Sintoma | Solução |
|---|---|---|
| Sem `description` | Skill não é roteada | Adicionar frontmatter |
| `description` vaga | Roteador erra, chama outra skill | Adicionar gatilhos específicos |
| `name` ≠ nome do diretório | Skill ignorada ou conflito | Renomear diretório ou campo |
| Versão fixa em 1.0.0 | Impossível bumpar com semVer | Iniciar em 0.1.0 e bumpar |
| Path absoluto hardcoded | Quebra em outro CWD | Usar path relativo à skill |
| `metadata.hermes.resources` faltando | Roteador não descobre subarquivos | Listar todos os arquivos em `resources` |
| Skill na home sem symlink pro repo | Não é versionada, se perde | `rm` e recriar via `skill-forge` |

## 7. Workflow de criação (resumo)

1. Rodar `skill-forge` (ou `bash scripts/scaffold-skill.sh`) com nome + categoria.
2. Editar o `SKILL.md` gerado: Propósito, Pré-requisitos, Fluxo, Guardrails.
3. Adicionar `metadata.hermes.resources` com TODOS os arquivos da skill.
4. Bumpar `version` no frontmatter.
5. Smoke-test: rodar a skill de verdade e ver se funciona.
6. `git add` + commit. (O symlink na home não vai pro git — é local.)

## 8. Workflow de atualização

1. Editar arquivos.
2. Bumpar `version` no frontmatter (MINOR ou PATCH).
3. Atualizar `metadata.hermes.updated` se você usa esse campo.
4. Se mudou a estrutura, atualizar `metadata.hermes.resources`.
5. Recarregar skills do Hermes: `/reload-skills`.
6. Commit.

## 9. Workflow de remoção

1. `rm` no repo: `rm -rf .hermes/skills/<cat>/<nome>`.
2. `rm` no symlink: `rm ~/.hermes/skills/<cat>/<nome>`.
3. Commit. (Não esquecer de remover dos `related_skills` de outras skills.)
