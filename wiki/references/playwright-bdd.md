---
title: "Playwright BDD — Referência Completa"
category: references
tags:
  - reference
  - playwright
  - bdd
  - testing
  - gherkin
summary: "Referência completa do Playwright BDD: instalação, defineBddConfig, projetos múltiplos, step definitions com createBdd, parâmetros ({string}/{int}/{float}), regex, custom types, fixtures, Page Object Model, data tables, doc strings, tags especiais, execução e troubleshooting."
created: "2026-06-13"
updated: "2026-06-15"
lifecycle: reviewed
lifecycle_changed: "2026-06-15"
lifecycle_reason: "auto-promoted by wiki-lint: well-established reference page"
sources:
  - "wiki/_raw/qa/playwright-bdd/playwright-bdd-gherkin-syntax.md"
  - "wiki/_raw/qa/playwright-bdd/playwright-bdd-configuration.md"
  - "wiki/_raw/qa/playwright-bdd/playwright-bdd-step-definitions.md"
---

# Playwright BDD — Referência Completa

Playwright BDD permite executar testes BDD em sintaxe Gherkin com Playwright Test. As *feature files* `.feature` são transformadas em arquivos de teste Playwright via `bddgen`.

---

## Índice

1. [[#Instalação]]
2. [[#Configuração Básica com defineBddConfig]]
3. [[#Opções de Configuração]]
4. [[#Múltiplos Feature Sets com Projects]]
5. [[#Integração com Playwright Config Completa]]
6. [[#Step Definitions com createBdd]]
7. [[#Parâmetros]]
8. [[#Regex em Steps]]
9. [[#Custom Parameter Types]]
10. [[#Fixtures Customizadas]]
11. [[#Page Object Model (POM)]]
12. [[#Decorator-Based Steps]]
13. [[#Data Tables]]
14. [[#Doc Strings]]
15. [[#Compartilhamento de Estado entre Steps]]
16. [[#Tags Especiais]]
17. [[#Execução]]
18. [[#Export de Steps]]
19. [[#Troubleshooting]]
20. [[#Boas Práticas]]

---

## Instalação

```bash
# Instalar playwright-bdd
npm install -D playwright-bdd

# Ou com versão específica do Playwright
npm install -D playwright-bdd @playwright/test
```

---

## Configuração Básica com `defineBddConfig`

### Mínima

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
});

export default defineConfig({
  testDir,
});
```

`defineBddConfig()` retorna o caminho do diretório de testes gerado (por padrão `.features-gen/features`).

### Diretório de Saída Customizado

```typescript
const testDir = defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
  outputDir: '.generated-tests',
});
```

---

## Opções de Configuração

### `features` — Arquivos Feature

```typescript
// Padrão único
features: 'features/**/*.feature',

// Múltiplos padrões
features: [
  'features/**/*.feature',
  'specs/**/*.feature',
],

// Incluir/Excluir
features: {
  include: 'features/**/*.feature',
  exclude: 'features/**/skip-*.feature',
},
```

### `steps` — Step Definitions

```typescript
// Padrão único
steps: 'steps/**/*.ts',

// Múltiplos padrões
steps: [
  'steps/**/*.ts',
  'features/**/*.steps.ts',
],

// Mistura JS/TS
steps: [
  'steps/**/*.ts',
  'steps/**/*.js',
],
```

### `importTestFrom` — Importar Test Instance Customizada

```typescript
defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
  importTestFrom: 'steps/fixtures.ts', // arquivo que exporta test + createBdd
});
```

### `language` — Idioma Gherkin

```typescript
defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
  language: 'de', // Alemão: Gegeben, Wenn, Dann
});
```

Idiomas suportados: `en` (padrão), `de`, `fr`, `es`, `ru` e muitos outros.

### `quotes` — Estilo de Aspas nos Arquivos Gerados

```typescript
quotes: 'single',  // 'single' | 'double' | 'backtick'
```

### `verbose` — Modo Verboso

```typescript
verbose: true,
```

---

## Múltiplos Feature Sets com Projects

```typescript
import { defineConfig } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const coreTestDir = defineBddConfig({
  features: 'features/core/**/*.feature',
  steps: 'steps/core/**/*.ts',
  outputDir: '.features-gen/core',
});

const adminTestDir = defineBddConfig({
  features: 'features/admin/**/*.feature',
  steps: 'steps/admin/**/*.ts',
  outputDir: '.features-gen/admin',
});

export default defineConfig({
  projects: [
    {
      name: 'core',
      testDir: coreTestDir,
    },
    {
      name: 'admin',
      testDir: adminTestDir,
    },
  ],
});
```

---

## Integração com Playwright Config Completa

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/**/*.feature',
  steps: 'steps/**/*.ts',
  importTestFrom: 'steps/fixtures.ts',
});

export default defineConfig({
  testDir,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Step Definitions com `createBdd()`

### Básico

```typescript
// steps/common.steps.ts
import { createBdd } from 'playwright-bdd';

const { Given, When, Then } = createBdd();

Given('I am on the home page', async ({ page }) => {
  await page.goto('/');
});

When('I click the login button', async ({ page }) => {
  await page.getByRole('button', { name: 'Login' }).click();
});

Then('I should see the dashboard', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

Todos os **fixtures do Playwright** (`page`, `context`, `browserName`, `request`, etc.) estão disponíveis nos parâmetros do callback.

---

## Parâmetros

### `{string}` — Texto entre aspas

```typescript
Given('the user name is {string}', async ({}, name: string) => {
  console.log(name); // "John"
});
```

### `{int}` — Número inteiro

```typescript
When('I wait {int} seconds', async ({}, seconds: number) => {
  await page.waitForTimeout(seconds * 1000);
});
```

### `{float}` — Número decimal

```typescript
Then('the price is {float}', async ({}, price: number) => {
  console.log(price); // 19.99
});
```

### `{word}` — Palavra única (sem espaços)

```typescript
Given('I am on the {word} page', async ({ page }, pageName: string) => {
  await page.goto(`/${pageName}`);
});
```

---

## Regex em Steps

Use **expressões regulares** no lugar de string para casamento flexível:

```typescript
// Qualquer texto entre aspas
Given(/^I enter "(.*)" in the search box$/, async ({ page }, query: string) => {
  await page.getByRole('searchbox').fill(query);
});

// Números
When(/^I add (\d+) items to cart$/, async ({ page }, count: string) => {
  const quantity = parseInt(count, 10);
  for (let i = 0; i < quantity; i++) {
    await page.getByRole('button', { name: 'Add to Cart' }).click();
  }
});
```

Grupos de captura na regex viram parâmetros do callback, na ordem em que aparecem.

---

## Custom Parameter Types

Defina tipos de parâmetro reutilizáveis com `defineParameterType`:

```typescript
// steps/parameters.ts
import { defineParameterType } from 'playwright-bdd';

defineParameterType({
  name: 'color',
  regexp: /red|green|blue/,
  transformer: (s) => s,
});

defineParameterType({
  name: 'boolean',
  regexp: /true|false/,
  transformer: (s) => s === 'true',
});

defineParameterType({
  name: 'date',
  regexp: /\d{4}-\d{2}-\d{2}/,
  transformer: (s) => new Date(s),
});
```

### Uso

```typescript
import { createBdd } from 'playwright-bdd';
import './parameters'; // Importa as definições

const { Given, When, Then } = createBdd();

When('I select the {color} theme', async ({ page }, color: string) => {
  await page.getByRole('button', { name: color }).click();
});

Then('dark mode is {boolean}', async ({ page }, enabled: boolean) => {
  if (enabled) {
    await expect(page.locator('body')).toHaveClass(/dark/);
  }
});
```

---

## Fixtures Customizadas

### Criando Fixtures

```typescript
// steps/fixtures.ts
import { test as base, createBdd } from 'playwright-bdd';
import { TodoPage } from '../pages/TodoPage';
import { ApiClient } from '../utils/ApiClient';

type TestFixtures = {
  todoPage: TodoPage;
  apiClient: ApiClient;
};

export const test = base.extend<TestFixtures>({
  todoPage: async ({ page }, use) => {
    await use(new TodoPage(page));
  },
  apiClient: async ({ request }, use) => {
    await use(new ApiClient(request));
  },
});

export const { Given, When, Then } = createBdd(test);
```

### Usando Fixtures nos Steps

```typescript
// steps/todo.steps.ts
import { Given, When, Then } from './fixtures';

Given('I have an empty todo list', async ({ todoPage }) => {
  await todoPage.goto();
  await todoPage.clearAll();
});

When('I add a todo {string}', async ({ todoPage }, text: string) => {
  await todoPage.addTodo(text);
});

Then('I should see {int} todos', async ({ todoPage }, count: number) => {
  await todoPage.expectTodoCount(count);
});
```

### Fixture com Setup e Teardown

```typescript
export const test = base.extend<{
  authenticatedPage: Page;
}>({
  authenticatedPage: async ({ page, context }, use) => {
    // Setup
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('Password').fill('password');
    await page.getByRole('button', { name: 'Login' }).click();
    await page.waitForURL('/dashboard');

    // Uso
    await use(page);

    // Teardown
    await page.goto('/logout');
  },
});
```

---

## Page Object Model (POM)

### Definindo um Page Object

```typescript
// pages/TodoPage.ts
import { Page, Locator, expect } from '@playwright/test';

export class TodoPage {
  readonly page: Page;
  readonly input: Locator;
  readonly list: Locator;
  readonly items: Locator;

  constructor(page: Page) {
    this.page = page;
    this.input = page.getByPlaceholder('What needs to be done?');
    this.list = page.getByRole('list');
    this.items = page.getByTestId('todo-item');
  }

  async goto() { await this.page.goto('/todos'); }
  async addTodo(text: string) {
    await this.input.fill(text);
    await this.input.press('Enter');
  }
  async removeTodo(text: string) {
    const item = this.items.filter({ hasText: text });
    await item.hover();
    await item.getByRole('button', { name: 'Delete' }).click();
  }
  async toggleTodo(text: string) {
    const item = this.items.filter({ hasText: text });
    await item.getByRole('checkbox').click();
  }
  async expectTodoCount(count: number) {
    await expect(this.items).toHaveCount(count);
  }
  async expectTodoVisible(text: string) {
    await expect(this.items.filter({ hasText: text })).toBeVisible();
  }
  async clearAll() {
    const count = await this.items.count();
    for (let i = count - 1; i >= 0; i--) {
      await this.items.nth(i).hover();
      await this.items.nth(i).getByRole('button', { name: 'Delete' }).click();
    }
  }
}
```

### Integrando com Steps

```typescript
// steps/fixtures.ts
import { test as base, createBdd } from 'playwright-bdd';
import { TodoPage } from '../pages/TodoPage';

export const test = base.extend<{ todoPage: TodoPage }>({
  todoPage: async ({ page }, use) => {
    await use(new TodoPage(page));
  },
});

export const { Given, When, Then } = createBdd(test);
```

```typescript
// steps/todo.steps.ts
import { Given, When, Then } from './fixtures';

Given('I am on the todo page', async ({ todoPage }) => {
  await todoPage.goto();
});

When('I add {string} to my todos', async ({ todoPage }, text: string) => {
  await todoPage.addTodo(text);
});

Then('I should see the todo {string}', async ({ todoPage }, text: string) => {
  await todoPage.expectTodoVisible(text);
});
```

---

## Decorator-Based Steps

Organize steps em **classes com decoradores**:

```typescript
// steps/TodoSteps.ts
import { Fixture, Given, When, Then } from 'playwright-bdd/decorators';
import { test } from './fixtures';

export
@Fixture<typeof test>('todoPage')
class TodoSteps {
  @Given('I am on the todo page')
  async gotoTodoPage() {
    await this.todoPage.goto();
  }

  @When('I add {string} to my todos')
  async addTodo(text: string) {
    await this.todoPage.addTodo(text);
  }

  @Then('I should see {int} todos')
  async checkTodoCount(count: number) {
    await this.todoPage.expectTodoCount(count);
  }
}
```

### Múltiplos Fixtures

```typescript
export
@Fixture<typeof test>('loginPage')
@Fixture<typeof test>('todoPage')
class AuthenticatedSteps {
  @Given('I am logged in')
  async login() {
    await this.loginPage.login('user@example.com', 'password');
  }

  @When('I visit my todos')
  async visitTodos() {
    await this.todoPage.goto();
  }
}
```

---

## Data Tables

Tabelas no Gherkin são recebidas como `DataTable` (do `@cucumber/cucumber`).

### Tabela Simples (lista)

```gherkin
When I add the following todos:
  | Buy milk  |
  | Buy bread |
  | Buy eggs  |
```

```typescript
import { DataTable } from '@cucumber/cucumber';

When('I add the following todos:', async ({ todoPage }, table: DataTable) => {
  const todos = table.raw().flat();
  for (const todo of todos) {
    await todoPage.addTodo(todo);
  }
});
```

### Tabela com Cabeçalhos

```gherkin
When I create users:
  | name  | email           | role  |
  | Alice | alice@test.com  | admin |
  | Bob   | bob@test.com    | user  |
```

```typescript
When('I create users:', async ({ page }, table: DataTable) => {
  const users = table.hashes();
  for (const user of users) {
    await page.getByLabel('Name').fill(user.name);
    await page.getByLabel('Email').fill(user.email);
    await page.getByLabel('Role').selectOption(user.role);
    await page.getByRole('button', { name: 'Create' }).click();
  }
});
```

### Tabela Vertical (chave-valor)

```gherkin
When I fill the form:
  | Name     | John Doe         |
  | Email    | john@example.com |
  | Password | secret123        |
```

```typescript
When('I fill the form:', async ({ page }, table: DataTable) => {
  const data = table.rowsHash();
  await page.getByLabel('Name').fill(data.Name);
  await page.getByLabel('Email').fill(data.Email);
  await page.getByLabel('Password').fill(data.Password);
});
```

### Métodos do `DataTable`

| Método          | Descrição                                           |
|-----------------|-----------------------------------------------------|
| `raw()`         | Matriz 2D de strings (linhas × colunas)             |
| `hashes()`      | Array de objetos (cabeçalho → valor)                |
| `rows()`        | Array de arrays, sem cabeçalho                      |
| `rowsHash()`    | Objeto chave-valor (2 colunas, 1ª é chave, 2ª valor) |

---

## Doc Strings

Blocos de texto multi-linha com `"""`:

```gherkin
When I write the following review:
  """
  This product is amazing!
  I highly recommend it to everyone.
  Five stars!
  """
```

```typescript
When('I write the following review:', async ({ page }, docString: string) => {
  await page.getByRole('textbox', { name: 'Review' }).fill(docString);
});
```

### Doc String com JSON

```gherkin
When I send the API request:
  """json
  {
    "name": "Test Product",
    "price": 29.99,
    "category": "electronics"
  }
  """
```

```typescript
When('I send the API request:', async ({ request }, docString: string) => {
  const data = JSON.parse(docString);
  await request.post('/api/products', { data });
});
```

---

## Compartilhamento de Estado entre Steps

Use **fixtures customizadas** como um "mundo" (world/context) para compartilhar dados entre steps do mesmo cenário.

```typescript
// steps/fixtures.ts
import { test as base, createBdd } from 'playwright-bdd';

type World = {
  currentUser?: { id: string; name: string };
  createdItems: string[];
};

export const test = base.extend<{ world: World }>({
  world: async ({}, use) => {
    await use({ createdItems: [] });
  },
});

export const { Given, When, Then } = createBdd(test);
```

```typescript
// steps/user.steps.ts
import { Given, When, Then } from './fixtures';

Given('I am logged in as {string}', async ({ page, world }, name: string) => {
  world.currentUser = { id: '123', name };
  await page.goto('/login');
});

When('I create an item {string}', async ({ world }, item: string) => {
  world.createdItems.push(item);
});

Then('I should see my items', async ({ page, world }) => {
  for (const item of world.createdItems) {
    await expect(page.getByText(item)).toBeVisible();
  }
});
```

---

## Tags Especiais

Playwright BDD reconhece tags especiais que alteram o comportamento do teste:

| Tag       | Efeito                                           | Equivalente Playwright        |
|-----------|--------------------------------------------------|-------------------------------|
| `@skip`   | Pula o cenário                                   | `test.skip()`                 |
| `@only`   | Executa **apenas** este cenário                  | `test.only()`                 |
| `@fail`   | Marca como falha esperada (falha → teste passa)  | `test.fail()`                 |
| `@fixme`  | Marca como instável (falha não interrompe)       | `test.fixme()`                |

```gherkin
@skip
Scenario: Feature not ready
  Given this is skipped

@only
Scenario: Debug this specific test
  Given I need to focus on this

@fail
Scenario: Known bug #123
  Given this is expected to fail

@fixme
Scenario: Intermittently failing test
  Given this sometimes fails
```

### Filtragem por Tag na Execução

```bash
# Apenas smoke tests
npx playwright test --grep @smoke

# Excluir slow tests
npx playwright test --grep-invert @slow

# Combinar tags (AND)
npx playwright test --grep "@smoke.*@critical"
```

Tags em **Feature** são herdadas por todos os cenários dentro dela.

---

## Execução

### Gerar Arquivos de Teste

```bash
npx bddgen
```

Gera os arquivos `.spec.js` em `.features-gen/` a partir dos `.feature`.

### Executar Testes

```bash
npx playwright test
```

### Combinar Geração + Execução

```bash
npx bddgen && npx playwright test
```

### Watch Mode (Desenvolvimento)

Terminal 1 — regenera ao alterar arquivos:

```bash
npx bddgen --watch
```

Terminal 2 — executa testes continuamente:

```bash
npx playwright test --watch
```

---

## Export de Steps

Gera documentação de todos os steps registrados:

```bash
npx bddgen export
```

Útil para auditoria, referência da equipe e debugging de steps não encontrados.

---

## Troubleshooting

### Steps Não Encontrados

1. Verifique se os padrões em `steps` correspondem à estrutura de diretórios.
2. Confira digitação no texto do step (Gherkin × step definition).
3. Certifique-se de que os arquivos de step estão incluídos na configuração `steps`.
4. Execute `npx bddgen export` para listar todos os steps registrados.

### Erros de Importação

1. Verifique se o caminho em `importTestFrom` está correto.
2. Garanta que o arquivo exporta `test` e as funções `{ Given, When, Then }`.
3. Confira se a configuração TypeScript inclui os arquivos de step.

### Erros de Geração (bddgen)

1. Valide a sintaxe dos arquivos `.feature`.
2. Verifique se existem step definitions para todos os steps usados.
3. Ative `verbose: true` na configuração para detalhes.
4. Confira todos os imports nos arquivos de step.

---

## Estrutura de Diretórios Recomendada

```
project/
├── playwright.config.ts
├── features/
│   ├── auth/
│   │   ├── login.feature
│   │   └── logout.feature
│   └── products/
│       └── catalog.feature
├── steps/
│   ├── fixtures.ts
│   ├── parameters.ts
│   ├── common/
│   │   ├── navigation.steps.ts
│   │   └── forms.steps.ts
│   ├── auth/
│   │   ├── login.steps.ts
│   │   └── logout.steps.ts
│   └── products/
│       ├── catalog.steps.ts
│       └── cart.steps.ts
└── .features-gen/          # Gerado — adicionar ao .gitignore
```

### .gitignore

```
# Playwright BDD generated files
.features-gen/
```

---

## Boas Práticas

1. **Organize por domínio** — Agrupe features e steps por área de negócio.
2. **Use fixtures** — Compartilhe lógica de setup via fixtures do Playwright, não em steps imperativos.
3. **Steps atômicos** — Uma ação por step definition.
4. **Steps reutilizáveis** — Escreva steps genéricos que funcionam em múltiplos cenários.
5. **Steps declarativos** — Descreva o **que** fazer, não **como** fazer.
    - ✅ `Given I am logged in as an admin`
    - ❌ `Given I navigate to "/login"` + `And I type "admin@test.com"`
6. **Nomes significativos** — `Scenario: Logged-in user can add items to wishlist`, não `Scenario: Test 1`.
7. **Cenários independentes** — Cada cenário deve funcionar isoladamente, sem depender de estado de cenários anteriores.
8. **TypeScript** — Use TypeScript para type safety nos steps.
9. **CI/CD** — Execute `npx bddgen` antes dos testes no pipeline.
10. **Documentação** — Exporte steps com `npx bddgen export` para referência da equipe.
11. **Paralelismo** — Deixe o Playwright gerenciar a execução paralela.
12. **Limpeza** — Adicione `.features-gen/` ao `.gitignore`.
13. **Assertions com Playwright** — Use `expect` do Playwright, com auto-wait e retry embutidos.
14. **Skip condicional** — Use `test.skip()` dentro de steps para pular baseado em condições (ex.: browser).

```typescript
// Skip condicional por browser
Given('I am on a supported browser', async ({ browserName }) => {
  if (browserName === 'webkit') {
    test.skip(true, 'Feature not supported on WebKit');
  }
});
```

---

## Referência Rápida — Gherkin Keywords

| Keyword     | Função                              |
|-------------|-------------------------------------|
| `Feature:`  | Título e descrição da funcionalidade |
| `Scenario:` | Um caso de teste específico         |
| `Given`     | Pré-condição (contexto inicial)     |
| `When`      | Ação ou evento                      |
| `Then`      | Resultado esperado                  |
| `And` / `But` | Continuação do step anterior      |
| `Background:` | Setup compartilhado entre cenários |
| `Scenario Outline:` | Cenário data-driven com `Examples:` |
| `Examples:` | Tabela de dados para o Outline      |
| `Rule:`     | Agrupa cenários sob uma regra de negócio |
| `"""`       | Doc string (texto multi-linha)      |
| `|`         | Data table                          |

---

> **Fonte:** Documentação oficial do [playwright-bdd](https://github.com/vitalets/playwright-bdd).

## Ver Também

- [[references/gherkin-syntax|Gherkin Syntax]] — Sintaxe usada nos testes
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Boas práticas para cenários E2E
- [[references/cucumber-basics|Cucumber Basics]] — Framework BDD clássico (alternativa)
- [[references/qa-overview|QA Overview]] — Estratégia de QA no framework SDD
