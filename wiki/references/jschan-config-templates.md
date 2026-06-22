---
title: "jschan Configuration Templates"
category: references
tags: [jschan, config, secrets, template, mongodb, redis]
created: "2026-06-20"
rag_score: 0.5
author: phm-aguiar
source: "jschan/configs/secrets.js.example + template.js.example"
aliases: ["jschan config", "jschan template"]
---

# jschan Configuration Templates

> Referência extraída do repositório jschan antes da remoção.
> Estes são os templates de configuração necessários para rodar uma instância.

## secrets.js — Credenciais e conexões

```js
module.exports = {
    // MongoDB connection string
    dbURL: 'mongodb://jschan:PASSWORD@127.0.0.1:27017/jschan',
    dbName: 'jschan',

    // Redis connection
    redis: {
        host: '127.0.0.1',
        port: '6379',
        password: 'CHANGE-ME-YOUR-SECURE-REDIS-PASSWORD'
    },

    // Backend webserver port
    port: 7000,

    // Secrets/salts
    cookieSecret: 'changeme',
    tripcodeSecret: 'changeme',
    ipHashSecret: 'changeme',
    postPasswordSecret: 'changeme',

    // Google reCAPTCHA keys
    google: {
        siteKey: 'changeme',
        secretKey: 'changeme'
    },

    // hCaptcha keys
    hcaptcha: {
        siteKey: '10000000-ffff-ffff-ffff-000000000001',
        secretKey: '0x0000000000000000000000000000000000000000'
    },

    // Yandex SmartCaptcha keys
    yandex: {
        siteKey: 'changeme',
        secretKey: 'changeme'
    },

    // Enable debug logging
    debugLogs: true,
};
```

## template.js — Global Settings (principais)

```js
module.exports = {
    globalAnnouncement: { markdown: '', raw: '' },
    secureCookies: true,
    refererCheck: false,
    allowedHosts: [],
    countryCodeHeader: 'x-country-code',
    ipHeader: 'x-real-ip',
    meta: { siteName: '', url: '' },
    language: 'en-GB',

    captchaOptions: {
        type: 'text',
        generateLimit: 250,
        font: 'default',
        text: { line: true, wave: 0, paint: 2, noise: 0 },
        grid: {
            falses: ['○','□','♘','♢','▽','△','♖','✧','♔','♘','♕','♗','♙','♧'],
            trues: ['●','■','♞','♦','▼','▲','♜','✦','♚','♞','♛','♝','♟','♣'],
            question: 'Select the solid/filled icons',
            size: 4, imageSize: 120, iconYOffset: 15, edge: 25, noise: 0
        },
        numDistorts: { min: 2, max: 3 },
        distortion: 7
    },

    dnsbl: { enabled: false, blacklists: ['tor.dan.me.uk'], cacheTime: 3600 },
    forceAccountTwofactor: false,
    forceActionTwofactor: false,
    disableAnonymizerFilePosting: false,
    statsCountAnonymizers: true,

    floodTimers: {
        sameContentSameIp: 120000,
        sameContentAnyIp: 30000,
        anyContentSameIp: 5000
    },

    blockBypass: {
        enabled: false,
        forceAnonymizers: true,
        expireAfterUses: 50,
        expireAfterTime: 86400000,
        bypassDnsbl: false
    },

    pruneImmediately: true,
    hashImages: false,

    rateLimitCost: { captcha: 10, boardSettings: 30, editPost: 30 },

    overboardLimit: 20,
    overboardCatalogLimit: 100,
    allowCustomOverboard: true,
    overboardReverseLinks: true,

    hotThreadsLimit: 5,
    hotThreadsThreshold: 10,
    hotThreadsMaxAge: 2629800000,

    archiveLinksURL: 'https://archive.today/?run=1&url=%s',
    reverseImageLinksURL: 'https://tineye.com/search?url=%s',
    ethereumLinksURL: 'https://etherscan.io/address/%s',

    cacheTemplates: true,
    lockWait: 3000,
    pruneModlogs: 30,
    pruneIps: 0,
    dontStoreRawIps: false,
    enableWebring: false,
    enableWeb3: false,
    ethereumNode: '',

    thumbExtension: '.webp',
    animatedGifThumbnails: false,
    audioThumbnails: true,
    ffmpegGifThumbnails: true,
    thumbSize: 250,
    videoThumbPercentage: 5,

    otherMimeTypes: ['text/plain', 'application/pdf', 'tegaki/replay'],

    // Board defaults (aplicados a novos boards)
    boardDefaults: {
        language: 'en-GB',
        theme: 'yotsuba',
        codeTheme: 'github',
        reverseImageSearchLinks: true,
        archiveLinks: true,
        sfw: false,
        lockMode: 0,
        fileR9KMode: 0,
        messageR9KMode: 0,
        unlistedLocal: false,
        unlistedWebring: false,
        captchaMode: 0,
        tphTrigger: 0,
        pphTrigger: 0,
        deleteProtectionAge: 0,
        deleteProtectionCount: 0
    }
};
```

## Relacionado

- [[tools/jschan/overview|Visão Geral do jschan]]
- [[tools/jschan/installation|Guia de Instalação]]
- [[tools/jschan/operations|Guia de Operações]]
