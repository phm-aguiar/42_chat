---
title: "Writing steps — Overview"
tags:
  - playwright-bdd
  - writing-steps
  - overview
created: 2026-06-21
rag_score: 0.5
source: "https://vitalets.github.io/playwright-bdd/#/writing-steps/index"
---

## Writing steps

**Step definitions** are registered with `Given()`, `When()`, `Then()` functions and contain actual implementation of steps.

There are **3 styles** of writing steps in Playwright-BDD:

1. [Playwright-style](#/writing-steps/playwright-style) - write steps like you write Playwright tests, recommended for new BDD projects or existing Playwright projects.
2. [Cucumber-style](#/writing-steps/cucumber-style) - write steps in a CucumberJS compatible way, use `this` to access the world and Playwright fixtures. Recommended for migrating CucumberJS projects to the Playwright runner.
3. [Decorators](#/writing-steps/decorators) - mark POM class methods as steps, recommended for all projects.

#### Examples

Playwright-style step definition:

```ts
Given('I open page {string}', async ({ page }, url: string) => {
  await page.goto(url);
});
```

Cucumber-style step definition:

```ts
Given('I open page {string}', async function (url: string) {
  await this.page.goto(url);
});
```

Decorator step definition:

```ts
class TodoPage {
  @Given('I open page {string}')
  async open(url: string) {
    await this.page.goto(url);
  }
}
```

Check out the corresponding sections to learn more about each style.

Note that there are no `And()` / `But()` functions, as these keywords are used only for better semantics in `.feature` files.
