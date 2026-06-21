---
name: jschan-forum-manager
description: >
  CRUD de boards jschan via mongosh direto. Cria, lista, busca, edita e
  deleta boards de imageboard sem depender do jschan estar rodando.
  Conexão MongoDB parametrizável (--mongo-url + --db-name).
  Use para criar fóruns, listar boards existentes, editar configurações
  ou remover boards em cascata.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux]
tags: [jschan, forum, imageboard, mongodb, crud, boards, mongosh, devops]
category: devops
metadata:
  hermes:
    triggers:
      - criar forum jschan
      - criar board imageboard
      - listar boards jschan
      - deletar board jschan
      - editar board jschan
      - jschan board CRUD
    requires:
      commands: [mongosh]
      env_vars: [MONGO_URL, MONGO_DB]
    scripts:
      - scripts/create.sh
      - scripts/list.sh
      - scripts/get.sh
      - scripts/update.sh
      - scripts/delete.sh
---

# jschan-forum-manager

> CRUD de boards jschan via `mongosh` direto. Sem dependência do jschan estar rodando,
> sem autenticação web, sem captcha.

## Gatilhos

Use esta skill quando o usuário pedir para:
- "criar um fórum/imageboard"
- "listar boards do jschan"
- "editar configurações de um board"
- "deletar/remover um board"
- "gerenciar boards jschan"

## Pré-requisitos

- `mongosh` instalado (MongoDB Shell 6.0+)
- Connection string MongoDB com permissões readWrite no database jschan
- Opcional: env vars `MONGO_URL` e `MONGO_DB` para evitar passar --mongo-url toda vez

## Comandos

### create — Criar um board

```bash
bash scripts/create.sh \
  --mongo-url "mongodb://jschan:***@127.0.0.1:27017/jschan" \
  --db-name jschan \
  --name "Meu Fórum" \
  --uri "meuforum" \
  --owner "admin" \
  --description "Descrição do fórum" \
  --tags "tech,programação,linux"
```

**Parâmetros obrigatórios:** `--mongo-url`, `--name`, `--uri`, `--owner`
**Parâmetros opcionais:** `--db-name` (default: jschan), `--description`, `--tags`
**Env vars:** `MONGO_URL`, `MONGO_DB`, `JSCHAN_LANGUAGE` (default: pt-BR), `JSCHAN_THEME` (default: yotsuba)

**Validações:**
- URI não pode ser reservada (captcha, forms, randombanner, all)
- URI não pode já existir (DUPLICATE_URI)
- Cria staff entry com permissões máximas para o owner
- Adiciona board ao `ownedBoards` do owner
- Registra no Modlog

**Saída (sucesso):**
```json
{"uri": "meuforum", "name": "Meu Fórum", "owner": "admin", "status": "created"}
```

### list — Listar todos os boards

```bash
bash scripts/list.sh \
  --mongo-url "mongodb://jschan:***@127.0.0.1:27017/jschan"
```

**Saída:**
```json
[
  {"uri": "meuforum", "name": "Meu Fórum", "owner": "admin", "posts": 0, "pph": 0, "ppd": 0, "last_post": null},
  {"uri": "outro", "name": "Outro Board", "owner": "user2", "posts": 42, "pph": 3, "ppd": 72, "last_post": "2026-06-20T..."}
]
```

### get — Buscar board por URI

```bash
bash scripts/get.sh \
  --mongo-url "mongodb://..." \
  --uri "meuforum"
```

**Saída:** JSON completo do board com settings, contagens de staff/flags/assets/banners.

### update — Editar settings de um board

```bash
bash scripts/update.sh \
  --mongo-url "mongodb://..." \
  --uri "meuforum" \
  --name "Novo Nome" \
  --description "Nova descrição" \
  --theme "tomorrow" \
  --language "en-GB"
```

**Campos editáveis:** `--name`, `--description`, `--theme`, `--language`, `--code-theme`, `--custom-css`, `--sfw`
**Requer ao menos 1 campo para alterar.**

**Saída:**
```json
{"uri": "meuforum", "changed_fields": ["name", "description", "theme"], "status": "updated"}
```

### delete — Remover board em cascata

```bash
bash scripts/delete.sh \
  --mongo-url "mongodb://..." \
  --uri "meuforum" \
  --force
```

**⚠️ Operação DESTRUTIVA e IRREVERSÍVEL. Requer `--force` para confirmar.**

**Cascata:**
1. Conta e deleta todos os posts do board
2. Deleta o board da coleção `Boards`
3. Limpa `Modlogs`, `Bans`, `Filters`, `Stats`, `CustomPages` do board
4. Remove board do `ownedBoards` do owner
5. Remove board do `staffBoards` de todos os staff

**Saída:**
```json
{"uri": "meuforum", "status": "deleted", "posts_deleted": 42, "cascaded": ["Modlogs", "Bans", ...]}
```

## Uso com env vars

Para evitar repetir `--mongo-url`:

```bash
export MONGO_URL="mongodb://jschan:***@127.0.0.1:27017/jschan"
export MONGO_DB="jschan"

bash scripts/create.sh --name "Test" --uri "test" --owner "admin"
bash scripts/list.sh
bash scripts/get.sh --uri "test"
bash scripts/delete.sh --uri "test" --force
```

## Edge Cases

| Situação | Comportamento |
|---|---|
| URI reservada (captcha, forms, randombanner, all) | Erro `RESERVED_URI`, exit 1 |
| URI duplicada no create | Erro `DUPLICATE_URI`, exit 1 |
| Board não encontrado no get/update/delete | Erro `NOT_FOUND`, exit 1 |
| Delete sem --force | Erro `CONFIRMATION_REQUIRED`, exit 1 |
| MongoDB offline | Erro de conexão do mongosh, exit ≠ 0 |
| Campos obrigatórios ausentes no create | Erro `MISSING_PARAM`, exit 1 |
| Nenhum campo no update | Erro `NO_FIELDS`, exit 1 |
| Tags vazias | Array vazio `[]` |

## Pitfalls

- **Nunca rode `delete` sem `--force` antes de verificar:** o script para com erro sem `--force`, mas com `--force` a deleção é imediata e irreversível. Sempre rode `get` antes para ver o que será perdido.
- **O script NÃO remove arquivos do filesystem:** diretórios `html/`, `json/`, `banner/`, `flag/`, `asset/` do board permanecem no disco. Limpe-os manualmente se necessário.
- **Permissions bitmap é hardcoded:** o create usa `//////////8=` (todos os bits set). Se seu jschan tem roles customizadas, ajuste o bitmap no script.
- **mongosh deve estar no PATH:** verifique com `which mongosh` antes de usar.
- **Connection string com caracteres especiais:** use aspas simples ao passar no terminal para evitar escape de `$`, `&`, etc.
- **Board settings defaults:** language default é `pt-BR`, theme default é `yotsuba`. Ajuste via env vars `JSCHAN_LANGUAGE` e `JSCHAN_THEME` ou edite o script.
