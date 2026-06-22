---
title: "ESM"
tags:
  - playwright-bdd
  - configuration
  - esm
created: 2026-06-21
rag_score: 0.5
source: "https://vitalets.github.io/playwright-bdd/#/configuration/esm"
---

## ESM

Your project runs in [ESM](https://nodejs.org/api/esm.html) if:

- `package.json` contains `"type": "module"`
- `tsconfig.json` contains `"module": "ESNext"`

Since Playwright-BDD **v7** and Playwright **v1.41**, you can run tests in ESM with a regular command:

```
npx bddgen && npx playwright test
```

You can check out a fully working ESM project in [examples](https://github.com/vitalets/playwright-bdd/tree/main/examples/esm).
