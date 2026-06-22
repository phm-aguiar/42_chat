---
title: "Installation"
tags:
  - playwright-bdd
  - installation
  - getting-started
created: 2026-06-21
rag_score: 0.5
source: "https://vitalets.github.io/playwright-bdd/#/getting-started/installation"
---

## Installation

You can install Playwright-BDD with different package managers:

## Npm

- **New project or existing project without Playwright:**
	Install Playwright and Playwright-BDD:
	```
	npm i -D @playwright/test playwright-bdd
	```
	Install Playwright [browsers](https://playwright.dev/docs/browsers):
	```
	npx playwright install
	```
- **Existing project with Playwright:**
	Install only Playwright-BDD:
	```
	npm i -D playwright-bdd
	```

Now you can start [writing BDD tests](#/getting-started/write-first-test).

## Pnpm

- **New project or existing project without Playwright:**
	Install Playwright and Playwright-BDD:
	```
	pnpm i -D @playwright/test playwright-bdd
	```
	Install Playwright [browsers](https://playwright.dev/docs/browsers):
	```
	pnpm playwright install
	```
- **Existing project with Playwright:**
	Install only Playwright-BDD:
	```
	pnpm i -D playwright-bdd
	```

Now you can start [writing BDD tests](#/getting-started/write-first-test).

## Yarn

**Important**: For [Yarn Plug'n'Play](https://yarnpkg.com/features/pnp) you need to add these lines to the `.yarnrc.yml`:

```yml
packageExtensions: 
  playwright-bdd@*: 
    dependencies: 
      playwright: "*"
      playwright-core: "*"
```

Then proceed with installing packages.

- **New project or existing project without Playwright:**
	Install Playwright and Playwright-BDD:
	```
	yarn add -D @playwright/test playwright-bdd
	```
	Install Playwright [browsers](https://playwright.dev/docs/browsers):
	```
	yarn playwright install
	```
- **Existing project with Playwright:**
	Install only Playwright-BDD:
	```
	yarn add -D playwright-bdd
	```

Now you can start [writing BDD tests](#/getting-started/write-first-test).
