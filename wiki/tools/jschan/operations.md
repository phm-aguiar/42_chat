---
title: "jschan — Guia de Operações"
category: tools
tags: [jschan, operations, boards, crud, mongosh, mongodb]
created: "2026-06-20"
rag_score: 0.5
author: phm-aguiar
aliases: ["operar jschan", "gerenciar boards jschan", "jschan CRUD"]
---

# jschan — Guia de Operações

> Como gerenciar boards jschan: criar, listar, editar, deletar.
> Via `mongosh` direto (funciona mesmo com jschan parado) ou via skill Hermes `jschan-forum-manager`.

## Schema do Board

```json
{
  "_id": "uri-do-board",
  "owner": "username",
  "tags": ["tag1", "tag2"],
  "banners": [],
  "sequence_value": 1,
  "pph": 0,
  "ppd": 0,
  "ips": 0,
  "lastPostTimestamp": null,
  "webring": false,
  "staff": {
    "username": {
      "permissions": "<Binary bitmap>",
      "addedDate": "<ISODate>"
    }
  },
  "flags": {},
  "assets": [],
  "settings": {
    "name": "Nome do Board",
    "description": "Descrição",
    "language": "pt-BR",
    "theme": "yotsuba",
    "codeTheme": "github",
    "customCss": "",
    "announcement": { "raw": "", "markdown": "" },
    "sfw": false,
    "lockMode": 0,
    "fileR9KMode": 0,
    "messageR9KMode": 0,
    "captchaMode": 0,
    "unlistedLocal": false,
    "unlistedWebring": false,
    "reverseImageSearchLinks": true,
    "archiveLinks": true,
    "tphTrigger": 0,
    "pphTrigger": 0,
    "userPostDelete": true,
    "userPostSpoiler": true,
    "userPostUnlink": true,
    "replyLimit": 0,
    "deleteProtectionAge": 0,
    "deleteProtectionCount": 0
  }
}
```

## URIs Reservadas

Estas URIs **não podem** ser usadas como nome de board:

- `captcha` — endpoint de geração de captcha
- `forms` — endpoint de formulários
- `randombanner` — endpoint de banner aleatório
- `all` — rota especial do overboard

## Operações via mongosh

### Conectar

```bash
mongosh "mongodb://jschan:***@127.0.0.1:27017/jschan"
```

### Criar board

```javascript
db.Boards.insertOne({
  _id: "meuforum",
  owner: "admin",
  tags: ["tech", "programacao"],
  banners: [],
  sequence_value: 1,
  pph: 0, ppd: 0, ips: 0,
  lastPostTimestamp: null,
  webring: false,
  staff: {
    "admin": {
      permissions: new BinData(0, "<bitmap>"),
      addedDate: new Date()
    }
  },
  flags: {},
  assets: [],
  settings: {
    name: "Meu Fórum",
    description: "Um fórum sobre tecnologia",
    language: "pt-BR",
    theme: "yotsuba",
    codeTheme: "github",
    customCss: "",
    sfw: false,
    lockMode: 0,
    captchaMode: 0
  }
})
```

### Listar todos os boards

```javascript
db.Boards.find({}, {
  _id: 1,
  "settings.name": 1,
  owner: 1,
  sequence_value: 1,
  pph: 1
}).sort({ _id: 1 }).toArray()
```

### Buscar board por URI

```javascript
db.Boards.findOne({ _id: "meuforum" })
```

### Atualizar settings de um board

```javascript
db.Boards.updateOne(
  { _id: "meuforum" },
  {
    $set: {
      "settings.name": "Novo Nome",
      "settings.description": "Nova descrição",
      "settings.theme": "tomorrow",
      "settings.language": "en-GB"
    }
  }
)
```

### Deletar board (cascata)

**⚠️ Operação destrutiva e irreversível!**

```javascript
// 1. Contar posts antes
const posts = db.Posts.countDocuments({ board: "meuforum" })
print(`Atenção: ${posts} posts serão deletados do board /meuforum/`)

// 2. Deletar posts
db.Posts.deleteMany({ board: "meuforum" })

// 3. Deletar board
db.Boards.deleteOne({ _id: "meuforum" })

// 4. Limpar dados relacionados
db.Modlogs.deleteMany({ board: "meuforum" })
db.Bans.deleteMany({ board: "meuforum" })
db.Filters.deleteMany({ board: "meuforum" })
db.Stats.deleteMany({ board: "meuforum" })
db.CustomPages.deleteMany({ board: "meuforum" })

// 5. Remover ownedBoards do owner
db.Accounts.updateOne(
  { _id: "admin" },
  { $pull: { ownedBoards: "meuforum" } }
)
```

## Skill Hermes: jschan-forum-manager

Alternativa automatizada ao mongosh manual. A skill encapsula todas as operações acima:

```bash
# Criar
hermes skill run jschan-forum-manager create \
  --mongo-url "mongodb://jschan:***@127.0.0.1:27017/jschan" \
  --name "Meu Fórum" --uri "meuforum" --owner "admin"

# Listar
hermes skill run jschan-forum-manager list \
  --mongo-url "mongodb://..."

# Buscar
hermes skill run jschan-forum-manager get \
  --mongo-url "mongodb://..." --uri "meuforum"

# Editar
hermes skill run jschan-forum-manager update \
  --mongo-url "mongodb://..." --uri "meuforum" \
  --name "Novo Nome" --theme "tomorrow"

# Deletar (requer --force)
hermes skill run jschan-forum-manager delete \
  --mongo-url "mongodb://..." --uri "meuforum" --force
```

A skill também aceita env vars: `MONGO_URL` e `MONGO_DB`.

## Temas disponíveis

| Tema | Arquivo CSS | Descrição |
|---|---|---|
| Yotsuba | `yotsuba.css` | Clássico 4chan-like |
| Tomorrow | `tomorrow.css` | Moderno escuro |
| CyberHub | `cybhub.css` | Cyberpunk |
| Favela | `favela.css` | Brasileiro |
| AMOLED | `amoled.css` | Preto puro |
| Win95 | `win95.css` | Retrô Windows |
| Teletext | `teletext.css` | Vintage |
| Pink | `pink.css` | Rosa |
| Vapor | `vapor.css` | Vaporwave |

## Relacionado

- [[overview|Visão Geral do jschan]]
- [[installation|Guia de Instalação]]
