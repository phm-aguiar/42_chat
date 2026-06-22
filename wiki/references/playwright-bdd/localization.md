---
title: "Localization"
tags:
  - playwright-bdd
  - writing-features
  - i18n
  - localization
created: 2026-06-21
rag_score: 0.5
source: "https://vitalets.github.io/playwright-bdd/#/writing-features/i18n"
---

## Localization

You can write features in any of the [Cucumber supported languages](https://cucumber.io/docs/gherkin/languages/). The language can be set globally in the configuration:

```ts
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  language: 'es',
  // other config
});
```

Or in a particular feature file via the `# language` directive:

```gherkin
# language: es
Característica: Sitio de Playwright

    Escenario: Verificar título
        Dado que abro la url "https://playwright.dev"
        Cuando hago clic en el enlace "Get started"
        Entonces veo en el título "Playwright"
```
