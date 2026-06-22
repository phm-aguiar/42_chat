---
title: "jschan — Anonymous Imageboard Engine"
category: tools
tags: [jschan, imageboard, forum, mongodb, redis, nginx, nodejs]
created: "2026-06-20"
rag_score: 0.5
author: phm-aguiar
aliases: ["jschan engine", "imageboard software"]
---

# jschan — Anonymous Imageboard Engine

> Engine de imageboard anônimo open-source. Stack Node.js + MongoDB + Redis + Nginx.
> Licença GNU AGPLv3. Criado por [fatchan](https://gitgud.io/fatchan).

## Stack

| Componente | Função |
|---|---|
| **Node.js** (LTS) | Runtime da aplicação (Express + WebSocket) |
| **MongoDB** ≥ 4.4 | Database principal (boards, posts, accounts, bans) |
| **Redis** | Session store, fila de tasks, locks, cache, pub/sub WebSocket |
| **Nginx** | Proxy reverso, serve estáticos, HTTPS, GeoIP |
| **PM2** | Process manager (cluster mode) |
| **GraphicsMagick + ImageMagick** | Thumbnails, captchas |
| **FFmpeg** | Thumbnails de vídeo/audio/GIF |

## Funcionalidades

- [x] Multi-idioma (🇬🇧 🇵🇹 🇧🇷 🇷🇺 🇮🇹 🇪🇸)
- [x] Criação de boards por usuários (opcional)
- [x] Múltiplos arquivos por post
- [x] Antispam/Anti-flood + DNSBL
- [x] 3 captchas built-in + 3 third-party (hCaptcha, reCaptcha, Yandex)
- [x] 2FA (TOTP) para contas
- [x] Painel web completo para gestão
- [x] Permissões granulares por role
- [x] Compatível com Tor, Lokinet e outras redes anônimas
- [x] Integração Web3 (MetaMask: registro, login, assinar posts)
- [x] Tegaki (drawing applet com replays)
- [x] API documentada
- [x] Webring built-in
- [x] Frontend com múltiplos temas e opções

## Schema MongoDB

A coleção `Boards` é a principal para criação de fóruns:

```json
{
  "_id": "meuforum",
  "owner": "admin",
  "tags": ["tech", "programming"],
  "banners": [],
  "sequence_value": 1,
  "pph": 0, "ppd": 0, "ips": 0,
  "lastPostTimestamp": null,
  "webring": false,
  "staff": {
    "admin": {
      "permissions": "<Binary bitmap>",
      "addedDate": "<Date>"
    }
  },
  "flags": {},
  "assets": [],
  "settings": {
    "name": "Meu Fórum",
    "description": "Descrição do fórum",
    "language": "pt-BR",
    "theme": "yotsuba",
    "codeTheme": "github",
    "customCss": "",
    "sfw": false,
    "lockMode": 0,
    "captchaMode": 0
  }
}
```

## Instâncias ao vivo (não-oficiais)

- 🇵🇹/🇧🇷 [ptchan](https://ptchan.org)
- 🇧🇷 [27chan](https://27chan.org)
- 🇺🇸 [zzzchan](https://zzzchan.xyz)
- 🇮🇹 [nuichan](https://niuchan.org)
- E várias outras...

## Projetos relacionados

- [jschan-docs](https://gitgud.io/fatchan/jschan-docs/) — Documentação da API
- [jschan-api-go](https://gitgud.io/fatchan/jschan-api-go) — Client Golang para API
- [jschan-antispam](https://gitgud.io/jschan-antispam/) — Projetos antispam

## Relacionado

- [[installation|Guia de Instalação]]
- [[operations|Guia de Operações]]
