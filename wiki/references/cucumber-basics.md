---
title: "Cucumber & BDD — Referência Completa"
summary: "Síntese completa dos fundamentos de Cucumber, Gherkin, step definitions (JS/TS/Java/Ruby), hooks, World context, data tables, doc strings, Page Object pattern, boas práticas e anti-patterns para testes BDD."
tags:
  - cucumber
  - bdd
  - step-definitions
  - reference
base_confidence: 0.95
lifecycle: stable
tier: reference
---

# Cucumber & BDD — Referência Completa

## Core Concepts

### Behavior-Driven Development (BDD)

BDD é uma metodologia ágil que incentiva colaboração entre desenvolvedores, QA e stakeholders de negócio através de exemplos concretos escritos em linguagem natural. Cucumber é a ferramenta mais popular para automatizar esses exemplos.

**Princípios-chave:**

- **Living Documentation**: Features servem como especificações executáveis
- **Colaboração**: Escrito por devs, testers e stakeholders
- **Ubiquitous Language**: Terminologia de domínio consistente
- **Exemplos sobre Regras**: Exemplos concretos esclarecem requisitos
- **Automação**: Cenários são testes automatizados

---

### Gherkin — Sintaxe

Gherkin é a linguagem estruturada usada pelo Cucumber para escrever cenários.

#### Palavras-chave

| Palavra-chave     | Propósito                                      |
| ----------------- | ---------------------------------------------- |
| **Feature**       | Descrição de alto nível de uma funcionalidade  |
| **Scenario**      | Exemplo concreto ilustrando uma regra de negócio |
| **Given**         | Contexto / pré-condições                       |
| **When**          | Ação ou evento                                 |
| **Then**          | Resultado esperado                             |
| **And / But**     | Conectar múltiplos passos                      |
| **Background**    | Pré-condições comuns para todos os cenários    |
| **Scenario Outline** | Template para múltiplos exemplos com dados variáveis |
| **Examples**      | Tabela de dados para Scenario Outline          |

#### Exemplo completo

```gherkin
Feature: Autenticação de Usuário
  Como um usuário
  Eu quero fazer login na aplicação
  Para que eu possa acessar minha conta

  Background:
    Given que estou na página de login

  Scenario: Login bem-sucedido com credenciais válidas
    When eu insiro credenciais válidas
    And eu clico no botão de login
    Then devo ser redirecionado ao dashboard
    And devo ver uma mensagem de boas-vindas
```

---

### Scenario Outlines

Use `Scenario Outline` com `Examples` para testar o mesmo comportamento com dados diferentes:

```gherkin
Scenario Outline: Login com diferentes tipos de usuário
  Given que estou na página de login
  When eu faço login como "<user_type>"
  Then devo ver o dashboard "<dashboard>"
  And devo ter permissões "<permissions>"

  Examples:
    | user_type | dashboard | permissions    |
    | admin     | Admin     | full_access    |
    | user      | User      | limited_access |
    | guest     | Public    | read_only      |
```

---

### Tags

Organize e filtre cenários com tags:

```gherkin
@smoke @authentication
Scenario: Login do usuário
  Given que estou na página de login
  When eu insiro credenciais válidas
  Then devo estar logado

@wip
Scenario: Reset de senha
  Given que estou na página de reset de senha
  # Work in progress
```

**Filtros no CLI:**

```bash
# Rodar apenas smoke tests
cucumber --tags "@smoke"

# Rodar todos exceto WIP
cucumber --tags "not @wip"

# Smoke AND critical
cucumber --tags "@smoke and @critical"

# Smoke OR critical
cucumber --tags "@smoke or @critical"
```

---

## Step Definitions

Step definitions são o "glue" entre os cenários Gherkin e o código de automação.

### JavaScript / TypeScript (Cucumber.js)

```javascript
const { Given, When, Then } = require('@cucumber/cucumber');

Given('que estou na página de login', async function () {
  await this.page.goto('/login');
});

When('eu insiro credenciais válidas', async function () {
  await this.page.fill('#username', 'testuser');
  await this.page.fill('#password', 'password123');
});

Then('eu devo estar logado', async function () {
  const welcomeMessage = await this.page.textContent('.welcome');
  expect(welcomeMessage).toContain('Welcome, testuser');
});
```

### Java (Cucumber-JVM)

```java
import io.cucumber.java.en.*;
import static org.junit.Assert.*;

public class LoginSteps {

  @Given("que estou na página de login")
  public void i_am_on_login_page() {
    driver.get("http://example.com/login");
  }

  @When("eu insiro credenciais válidas")
  public void i_enter_valid_credentials() {
    driver.findElement(By.id("username")).sendKeys("testuser");
    driver.findElement(By.id("password")).sendKeys("password123");
  }

  @Then("eu devo estar logado")
  public void i_should_be_logged_in() {
    String welcome = driver.findElement(By.className("welcome")).getText();
    assertTrue(welcome.contains("Welcome, testuser"));
  }
}
```

### Ruby

```ruby
Given('que estou na página de login') do
  visit '/login'
end

When('eu insiro credenciais válidas') do
  fill_in 'username', with: 'testuser'
  fill_in 'password', with: 'password123'
end

Then('eu devo estar logado') do
  expect(page).to have_content('Welcome, testuser')
end
```

---

### Steps Parametrizados

Capture valores dos steps Gherkin usando expressões Cucumber:

```javascript
// {string} — captura texto entre aspas
// Scenario: Eu busco por "Cucumber" na barra de pesquisa
When('eu busco por {string} na barra de pesquisa', async function (searchTerm) {
  await this.page.fill('#search', searchTerm);
  await this.page.click('#search-button');
});

// {int} — captura números inteiros
// Scenario: Eu adiciono 5 itens ao meu carrinho
When('eu adiciono {int} itens ao meu carrinho', async function (quantity) {
  for (let i = 0; i < quantity; i++) {
    await this.addItemToCart();
  }
});

// {float} — captura números decimais
// Scenario: O preço deve ser $99.99
Then('o preço deve ser ${float}', async function (expectedPrice) {
  const actualPrice = await this.page.textContent('.price');
  expect(parseFloat(actualPrice)).toBe(expectedPrice);
});

// {word} — captura uma única palavra (sem aspas)
// Scenario: Eu seleciono a opção Administrador
When('eu seleciono a opção {word}', async function (option) {
  await this.page.selectOption('#role', option);
});
```

---

### Expressões Regulares

Use regex para matching mais flexível:

```javascript
// Match: "I wait 5 seconds", "I wait 10 seconds"
When(/^eu aguardo (\d+) segundos?$/, async function (seconds) {
  await this.page.waitForTimeout(seconds * 1000);
});

// Match: "I should see a success message", "I should see an error message"
Then(/^eu devo ver (?:uma|um) mensagem de (sucesso|erro)$/, async function (type) {
  const message = await this.page.textContent(`.${type}-message`);
  expect(message).toBeTruthy();
});
```

---

### Data Tables

Passe dados estruturados para os steps:

```gherkin
Scenario: Registrar novo usuário
  Given que estou na página de registro
  When eu preencho o formulário de registro:
    | Field        | Value            |
    | First Name   | John             |
    | Last Name    | Doe              |
    | Email        | john@example.com |
    | Password     | SecurePass123!   |
  Then devo ser registrado com sucesso
```

```javascript
// dataTable.hashes() — array de objetos (cada linha = um objeto)
When('eu preencho o formulário de registro:', async function (dataTable) {
  const users = dataTable.hashes();
  for (const user of users) {
    await this.api.createUser({
      firstName: user['First Name'],
      lastName: user['Last Name'],
      email: user['Email']
    });
  }
});

// dataTable.raw() — array 2D bruto
When('eu seleciono as seguintes opções:', async function (dataTable) {
  const options = dataTable.raw().flat();
  for (const option of options) {
    await this.page.check(`input[value="${option}"]`);
  }
});

// dataTable.rowsHash() — tabela 2-colunas como objeto chave-valor
When('eu preencho o formulário:', async function (dataTable) {
  const formData = dataTable.rowsHash();
  // { 'First Name': 'John', 'Last Name': 'Doe', ... }
  for (const [field, value] of Object.entries(formData)) {
    await this.page.fill(`[name="${field}"]`, value);
  }
});
```

---

### Doc Strings

Passe texto multi-linha para steps:

```gherkin
Scenario: Enviar formulário de contato
  Given que estou na página de contato
  When eu envio uma mensagem:
    """
    Olá equipe de suporte,

    Tenho uma pergunta sobre meu pedido #12345.

    Atenciosamente,
    João Silva
    """
  Then devo ver uma mensagem de confirmação
```

```javascript
When('eu envio uma mensagem:', async function (messageText) {
  await this.page.fill('#message', messageText);
  await this.page.click('#submit');
});
```

---

## World Context

Compartilhe estado entre steps usando o objeto **World** (contexto compartilhado por cenário):

```javascript
const { setWorldConstructor, World } = require('@cucumber/cucumber');

class CustomWorld extends World {
  constructor(options) {
    super(options);
    this.cart = [];
    this.user = null;
  }

  async login(username, password) {
    this.user = await this.api.login(username, password);
  }

  addToCart(item) {
    this.cart.push(item);
  }
}

setWorldConstructor(CustomWorld);

// Uso nos steps — `this` referencia o World
Given('que estou logado', async function () {
  await this.login('testuser', 'password');
});

When('eu adiciono um item ao carrinho', async function () {
  this.addToCart({ id: 1, name: 'Produto' });
});
```

> **Boa prática:** Compartilhe estado através do World, **nunca** via variáveis globais.

---

## Hooks

Configure e limpe estado do teste com hooks:

```javascript
const { Before, After, BeforeAll, AfterAll } = require('@cucumber/cucumber');

BeforeAll(async function () {
  // Executa uma vez ANTES de todos os cenários
  await startTestServer();
});

Before(async function () {
  // Executa antes de CADA cenário
  this.browser = await launchBrowser();
  this.page = await this.browser.newPage();
});

// Hook com tag — executa apenas para cenários com @database
Before({ tags: '@database' }, async function () {
  await this.db.clear();
});

After(async function () {
  // Executa depois de CADA cenário
  await this.browser.close();
});

AfterAll(async function () {
  // Executa uma vez DEPOIS de todos os cenários
  await stopTestServer();
});
```

---

## Page Object Pattern

Encapsule interações com páginas em classes:

```javascript
// pages/LoginPage.js
class LoginPage {
  constructor(page) {
    this.page = page;
  }

  async navigate() {
    await this.page.goto('/login');
  }

  async fillCredentials(username, password) {
    await this.page.fill('#username', username);
    await this.page.fill('#password', password);
  }

  async submit() {
    await this.page.click('#login-button');
  }
}

module.exports = LoginPage;

// step-definitions/login-steps.js
const LoginPage = require('../pages/LoginPage');

Given('que estou na página de login', async function () {
  this.loginPage = new LoginPage(this.page);
  await this.loginPage.navigate();
});

When('eu insiro {string} e {string}', async function (username, password) {
  await this.loginPage.fillCredentials(username, password);
  await this.loginPage.submit();
});
```

---

## Helpers

Extraia funcionalidades comuns para módulos reutilizáveis:

```javascript
// support/helpers.js
async function waitForElement(page, selector, timeout = 5000) {
  await page.waitForSelector(selector, { timeout });
}

async function takeScreenshot(page, name) {
  await page.screenshot({ path: `screenshots/${name}.png` });
}

module.exports = { waitForElement, takeScreenshot };

// Uso nos steps
const { waitForElement } = require('../support/helpers');

Then('eu devo ver o dashboard', async function () {
  await waitForElement(this.page, '.dashboard');
});
```

---

## Data Management com Factories

Use factories para gerar dados de teste consistentes:

```javascript
// support/factories.js
const faker = require('faker');

class UserFactory {
  static create(overrides = {}) {
    return {
      firstName: faker.name.firstName(),
      lastName: faker.name.lastName(),
      email: faker.internet.email(),
      password: 'Test123!',
      ...overrides
    };
  }
}

class OrderFactory {
  static create(overrides = {}) {
    return {
      productId: faker.datatype.uuid(),
      quantity: faker.datatype.number({ min: 1, max: 5 }),
      status: 'pending',
      ...overrides
    };
  }
}

module.exports = { UserFactory, OrderFactory };

// Uso nos steps
Given('que registro um novo usuário', async function () {
  const user = UserFactory.create();
  this.currentUser = user;
  await this.api.register(user);
});
```

> **Evite IDs hardcoded:** `Given usuário "12345" existe` → prefira `Given um usuário "john@example.com" existe`.

---

## Organização de Diretórios

```
features/
├── authentication/
│   ├── login.feature
│   └── registration.feature
├── shopping/
│   ├── cart.feature
│   └── checkout.feature
└── admin/
    └── user-management.feature

step-definitions/
├── login-steps.js
├── cart-steps.js
└── checkout-steps.js

pages/
├── LoginPage.js
├── CartPage.js
└── CheckoutPage.js

support/
├── world.js          # CustomWorld
├── helpers.js        # Funções utilitárias
├── factories.js      # Fábricas de dados
└── hooks.js          # Before/After hooks
```

---

## Boas Práticas de Step Definitions

### 1. Steps Componíveis e Reutilizáveis

Crie steps pequenos e genéricos que podem ser combinados:

```javascript
// ✅ Bom: composto e reutilizável
Given('que estou na página de login')
And('que sou um usuário premium')
And('que tenho credenciais válidas')

// ❌ Ruim: muito específico
Given('que estou na página de login como um usuário premium com credenciais válidas')
```

### 2. Um Step = Uma Ação ou Uma Assertiva

```javascript
// ✅ Bom
When('eu clico em login')
Then('eu devo ver o dashboard')

// ❌ Ruim: mistura ação + assertiva
When('eu clico em login e vejo o dashboard')
```

### 3. Steps Genéricos com Limite

```javascript
// ✅ Bom: específico o suficiente para ser legível
When('eu faço login com {string} e {string}')
When('eu busco por {string} em {string}')

// ❌ Genérico demais (perde semântica)
When('eu faço {string} com {string} e {string}')
```

### 4. Extraia Lógica para Helpers

Nunca chame steps de dentro de outros steps:

```javascript
// ❌ Ruim: chamar steps como funções
When('eu faço login', async function () {
  await this.Given('que estou na página de login'); // Bad!
  await this.When('eu insiro credenciais');         // Bad!
});

// ✅ Bom: extrair para helper
// support/auth-helpers.js
async function login(world, username, password) {
  await world.page.goto('/login');
  await world.page.fill('#username', username);
  await world.page.fill('#password', password);
  await world.page.click('#login-button');
}

// Uso nos steps
When('eu faço login', async function () {
  await login(this, 'user', 'pass');
});
```

### 5. Steps Assíncronos

Use `async/await` consistentemente:

```javascript
When('eu aguardo o carregamento', async function () {
  await this.page.waitForSelector('.loaded');
});
```

---

## Anti-Patterns

### ❌ Steps Muito Específicos

```gherkin
# ❌ Ruim
Given que estou na página de login como usuário premium com credenciais válidas e 2FA ativado

# ✅ Bom
Given que estou na página de login
And que sou um usuário premium
And que tenho credenciais válidas
And que tenho 2FA ativado
```

### ❌ Asserções em Given/When

```gherkin
# ❌ Ruim: Given deveria ser contexto, não assertiva
Given que o dashboard está visível

# ❌ Ruim: When deveria ser ação, não assertiva
When eu clico em login e vejo o dashboard

# ✅ Bom
When eu clico em login
Then eu devo ver o dashboard
```

### ❌ Chamar Steps Dentro de Steps

```javascript
// ❌ Ruim
When('eu faço login', async function () {
  await this.Given('que estou na página de login');
  await this.When('eu insiro credenciais');
});

// ✅ Bom: extrair para helper
```

### ❌ Steps Imperativos (Foco em "Como")

```gherkin
# ❌ Ruim: focado em implementação
Scenario: Adicionar produto ao carrinho
  Given que navego para "http://shop.com/products"
  When encontro o elemento com CSS ".product[data-id='123']"
  And clico no botão com class "add-to-cart"
  And aguardo a requisição AJAX
  Then o elemento ".cart-count" deve conter "1"

# ✅ Bom: focado em negócio
Scenario: Adicionar produto ao carrinho
  Given que estou navegando por produtos
  When eu adiciono "Fone Bluetooth" ao meu carrinho
  Then meu carrinho deve conter 1 item
```

### ❌ Testar Detalhes de Implementação

```gherkin
# ❌ Ruim
Then o banco de dados deve ter 1 registro na tabela users
Then devo ver uma mensagem de erro vermelha no canto superior direito

# ✅ Bom
Then o usuário deve estar cadastrado
Then devo ver uma mensagem de erro
```

### ❌ Given Usado como Ação

```gherkin
# ❌ Ruim: Given é contexto, não ação
Given que clico no botão de submit

# ✅ Bom
When eu clico no botão de submit
```

### ❌ Cenários Dependentes

```gherkin
# ❌ Ruim: cenário depende do anterior
Scenario: Criar pedido
  When eu crio o pedido #12345

Scenario: Ver pedido
  When eu vejo o pedido #12345  # Depende do anterior!

# ✅ Bom: cada cenário prepara seu próprio contexto
Scenario: Ver pedido
  Given que existe um pedido com ID "12345"
  When eu vejo os detalhes do pedido
  Then devo ver as informações do pedido
```

---

## Boas Práticas de Cenários Gherkin

### Escreva Cenários Declarativos

Foco no **o que**, não no **como**.

### Um Cenário = Um Comportamento

Cada cenário deve testar exatamente uma regra de negócio:

```gherkin
# ❌ Ruim: múltiplos comportamentos
Scenario: Registro, login e atualização de perfil
  When eu registro uma nova conta
  And eu faço login
  And eu atualizo meu perfil
  Then tudo deve funcionar

# ✅ Bom: cenários separados
Scenario: Registrar nova conta
  When eu registro com dados válidos
  Then devo receber um email de confirmação

Scenario: Login com nova conta
  Given que registrei uma conta
  When eu faço login com minhas credenciais
  Then devo ver meu dashboard
```

### Use Background com Moderação

```gherkin
# ✅ Bom: Background com setup relevante para todos
Feature: Carrinho de Compras
  Background:
    Given que estou logado como cliente

  Scenario: Adicionar produto ao carrinho
    ...

  Scenario: Remover produto do carrinho
    ...

# ❌ Ruim: Background fazendo demais
Background:
  Given que estou na homepage
  And clico no menu
  And navego para produtos
  And filtro por categoria "Eletrônicos"
  And ordeno por preço
  # Setup excessivo — nem todos os cenários precisam disso
```

### Evite Steps Conjuntivos

```gherkin
# ❌ Ruim
When eu faço login e adiciono um produto ao carrinho e finalizo a compra

# ✅ Bom
When eu faço login
And eu adiciono um produto ao meu carrinho
And eu prossigo para o checkout
```

---

## Testing Pyramid

Use Cucumber adequadamente dentro da sua estratégia de testes:

```
        ╱╲
       ╱  ╲
      ╱ E2E ╲            ← Cucumber: jornadas críticas do usuário (20%)
     ╱────────╲
    ╱          ╲
   ╱ Integration ╲       ← Testes de API / serviço (30%)
  ╱────────────────╲
 ╱                  ╲
╱    Unit Tests      ╲    ← Lógica de negócio (50%)
╱──────────────────────╲
```

- **E2E (20%)**: Cucumber para jornadas críticas de usuário — alto valor, baixa quantidade
- **Integração (30%)**: Testes de API, interações entre serviços
- **Unitários (50%)**: Lógica de negócio pura, sem infraestrutura

> **Importante:** Não tente testar tudo com Cucumber. Use-o para testes de aceitação de alto valor que documentam comportamento de negócio.

---

## Resumo Rápido de Boas Práticas

| Princípio                     | Descrição                                            |
| ----------------------------- | ---------------------------------------------------- |
| Cenários declarativos         | Foco no *o que*, não no *como*                       |
| Cenários independentes        | Cada cenário configura seu próprio contexto           |
| Linguagem de domínio          | Termos de negócio, não jargão técnico                |
| Um cenário, um comportamento  | Teste uma coisa por vez                              |
| Background enxuto             | Só o que é realmente comum a todos os cenários       |
| Steps componíveis             | Pequenos, reutilizáveis, combináveis                 |
| World para estado             | Nunca use variáveis globais                          |
| Helpers em vez de steps aninhados | Extraia lógica, não chame steps dentro de steps  |
| Page Objects                  | Encapsule seletores e interações de UI               |
| Factories para dados          | Evite dados hardcoded e IDs mágicos                  |
| Assertivas só em Then         | Given = contexto, When = ação, Then = verificação    |
