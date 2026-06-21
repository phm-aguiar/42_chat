---
name: playwright-bdd-e2e
description: >
  Use when the QA agent needs to write end-to-end (E2E) tests using Playwright with
  BDD/Gherkin syntax. Covers Playwright test runner with Cucumber integration, browser
  automation, and BDD-style test organization. References Playwright-BDD docs in the wiki.
version: 1.0.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [QA, E2E, Playwright, BDD, Browser-Testing]
    related_skills: [wiki-query, gherkin-scenarios, cucumber-step-definitions]
    category: qa
    resources:
      - SKILL.md
---

# Playwright BDD E2E — Testes end-to-end com BDD

> Ensina o QA a escrever testes E2E com Playwright e Gherkin.

## Proposito

Esta skill ensina testes E2E (end-to-end) usando Playwright com sintaxe BDD/Gherkin.
Cobre automacao de browser, organizacao de cenarios, e integracao com o pipeline QA.
Referencia completa em [[references/playwright-bdd]].

## Pre-requisitos

- Node.js instalado
- Playwright instalado (`npm init playwright`)
- Projeto com suporte a BDD (cucumber-playwright ou similar)

## Fluxo

### Passo 1: Setup do projeto
```bash
npm init -y
npm install @playwright/test @cucumber/cucumber playwright-bdd
npx playwright install
```

### Passo 2: Escrever .feature E2E
```gherkin
# language: pt
Funcionalidade: Login
  Cenario: Login com credenciais validas
    Dado que estou na pagina de login
    Quando preencho email "teste@email.com" e senha "123456"
    E clico em "Entrar"
    Entao vejo a dashboard
    E o titulo da pagina contem "Bem-vindo"
```

### Passo 3: Implementar step definitions
```typescript
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';

Given('que estou na pagina de login', async function () {
    await this.page.goto('/login');
});

When('preencho email {string} e senha {string}', async function (email, senha) {
    await this.page.fill('#email', email);
    await this.page.fill('#senha', senha);
});

Then('vejo a dashboard', async function () {
    await expect(this.page.locator('.dashboard')).toBeVisible();
});
```

### Passo 4: Executar
```bash
npx cucumber-js
# ou via Playwright test runner com BDD config
npx playwright test
```

## Referencia
Consulte [[references/playwright-bdd]] no vault para configuracao completa.
