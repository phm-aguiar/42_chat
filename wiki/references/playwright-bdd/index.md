---
title: "Playwright-BDD — Reference Index"
tags:
  - playwright-bdd
  - index
  - reference
created: 2026-06-21
rag_score: 0.5
---

# Playwright-BDD Reference Index

Comprehensive documentation reference for [Playwright-BDD](https://vitalets.github.io/playwright-bdd/), sourced from the official documentation. 40 pages covering all aspects of BDD testing with Playwright.

---

## Introduction

- [Introduction](introduction.md) — Overview of Playwright-BDD: what it is, why BDD, and how it works

## Getting Started

- [Getting Started](getting-started.md) — Welcome guide and tutorial outline
- [Installation](installation.md) — Install with npm, pnpm, or yarn
- [Write first BDD test](write-first-test.md) — Create and run your first BDD test
- [Add fixtures](add-fixtures.md) — Adding custom Playwright fixtures to steps

## Configuration

- [Configuration](configuration.md) — Overview of Playwright-BDD configuration
- [Options](options.md) — Complete list of all configuration options
- [Projects](projects.md) — Multiple Playwright projects with BDD
- [ESM](esm.md) — ESM module support

## Writing Features

- [Writing Features](writing-features.md) — Overview of feature file authoring
- [Customize Examples Title](customize-examples-title.md) — Scenario Outline example titles
- [Tags from Path](tags-from-path.md) — Automatic tagging via directory structure
- [Special Tags](special-tags.md) — `@only`, `@skip`, `@fail`, `@timeout`, `@retries`, `@mode`
- [Localization](localization.md) — Writing features in any Gherkin-supported language

## Writing Steps

- [Writing Steps](writing-steps.md) — Overview of step definition styles
- [Playwright-style](playwright-style.md) — Arrow functions, fixtures as first argument
- [Cucumber-style](cucumber-style.md) — CucumberJS-compatible, `this`/World-based
- [Decorators](decorators.md) — TypeScript decorators for Page Object Models
- [BDD Fixtures](bdd-fixtures.md) — `$test`, `$testInfo`, `$step`, `$tags` built-in fixtures
- [Snippets](snippets.md) — Auto-generated code for missing step definitions
- [Data Tables](data-tables.md) — Gherkin DataTable support
- [Doc Strings](doc-strings.md) — Multi-line step arguments with media types
- [Re-using Step Function](reusing-step-fn.md) — Share step logic across definitions
- [Keywords Matching](keywords-matching.md) — Require keyword match for step definitions
- [Scoped Step Definitions](scoped-step-definitions.md) — Scope steps to specific features/tags
- [Passing Data Between Steps](passing-data-between-steps.md) — Cross-step state via fixtures
- [Passing Data Between Scenarios](passing-data-between-scenarios.md) — Serial mode data sharing

## Hooks

- [Fixtures vs Hooks](hooks-fixtures.md) — Why fixtures are preferred over hooks
- [Step Hooks](step-hooks.md) — `BeforeStep` and `AfterStep`
- [Scenario Hooks](scenario-hooks.md) — `BeforeScenario` / `Before` and `AfterScenario` / `After`
- [Worker Hooks](worker-hooks.md) — `BeforeWorker` / `BeforeAll` and `AfterWorker` / `AfterAll`
- [Running Hook Once](running-hook-once.md) — Using `@global-cache/playwright` for single execution

## Reporters

- [Playwright Reporters](playwright-reporters.md) — Native Playwright reporters (html, json, etc.)
- [Cucumber Reporters](cucumber-reporters.md) — Cucumber HTML, JSON, JUnit, message, and custom formatters
- [Allure Reporter](allure-reporter.md) — Allure integration via `allure-playwright`

## Guides

- [Authentication](authentication.md) — Static and dynamic auth approaches
- [Fix with AI](fix-with-ai.md) — AI-assisted test fixing with ARIA snapshots
- [Migration to v9](migration-v9.md) — Breaking changes and migration steps for v9

## Reference

- [API](api.md) — Complete API reference: `defineBddConfig`, `createBdd`, `cucumberReporter`, decorators, hooks
- [CLI](cli.md) — `bddgen test`, `bddgen export`, `bddgen env` commands

---

> **Source:** All pages derived from official [Playwright-BDD documentation](https://vitalets.github.io/playwright-bdd/).
> **Generated:** 2026-06-21
