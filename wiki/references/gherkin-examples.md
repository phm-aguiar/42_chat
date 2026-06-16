---
title: "Gherkin Examples"
category: references
tags:
  - gherkin
  - bdd
  - cucumber
  - exemplos
  - referência
summary: "Exemplos reais de feature files Gherkin: busca de produtos, carrinho de compras, login, saque bancário, validação de senha, controle de acesso. Inclui comparações lado a lado: declarativo vs imperativo, behavior-focused vs UI-specific, focused vs multiple behaviors, meaningful vs generic data."
created: "2026-06-13"
updated: "2026-06-15"
lifecycle: reviewed
lifecycle_changed: "2026-06-15"
lifecycle_reason: "auto-promoted by wiki-lint: well-established reference page"
sources:
  - "wiki/_raw/qa/gherkin-examples/Examples real-world examples gherkin.md"
---

# Exemplos de Gherkin — Referência Completa

> Exemplos reais e bem escritos de arquivos `.feature` em Gherkin, prontos para usar como templates ou consulta rápida.

---

## Índice

1. [Product Search (Busca de Produtos)](#product-search)
2. [Shopping Cart Management (Gerenciamento de Carrinho)](#shopping-cart-management)
3. [User Login (Login de Usuário)](#user-login)
4. [Bank Account Withdrawals (Saques em Conta Bancária)](#bank-account-withdrawals)
5. [Password Validation (Validação de Senha)](#password-validation)
6. [Account Access Control (Controle de Acesso)](#account-access-control)
7. [Comparações Lado a Lado](#comparações-lado-a-lado)
   - [Declarativo vs Imperativo](#declarativo-vs-imperativo)
   - [UI-Specific vs Behavior-Focused](#ui-specific-vs-behavior-focused)
   - [Focused vs Multiple Behaviors](#focused-vs-multiple-behaviors)
   - [Meaningful vs Generic Data](#meaningful-vs-generic-data)

---

## Product Search

```gherkin
Feature: Product Search
  As a customer
  I want to search for products
  So that I can quickly find items I'm interested in purchasing

  Background:
    Given the product catalog contains the following items:
      | name              | category    | price   |
      | Wireless Mouse    | Electronics | $25.99  |
      | Desk Lamp         | Furniture   | $45.00  |
      | Coffee Mug        | Kitchen     | $12.99  |
      | Laptop Stand      | Electronics | $35.99  |

  Rule: Search returns matching products

    Scenario: Search by product name
      When the customer searches for "Mouse"
      Then the search results show "Wireless Mouse"
        And 1 product is returned

    Scenario: Search by category
      When the customer searches for "Electronics"
      Then the search results show 2 products
        And both products are in the Electronics category

  Rule: Search handles no results gracefully

    Scenario: Search with no matching products
      When the customer searches for "Telescope"
      Then no products are returned
        And a helpful message states "No products found"
        And search suggestions are provided

  Rule: Search can be refined

    Scenario: Filter search results by price range
      Given the customer has searched for "Electronics"
      When the customer applies a price filter of $20-$30
      Then only "Wireless Mouse" is shown in results
```

**Destaques:**
- Uso de `Background` para dados comuns entre cenários
- Organização com `Rule` para agrupar cenários por comportamento
- Cobertura de fluxo feliz, borda (sem resultados) e refinamento

---

## Shopping Cart Management

```gherkin
Feature: Shopping Cart Management
  As an online shopper
  I want to manage items in my shopping cart
  So that I can review and modify my purchases before checkout

  Scenario: Adding an item to an empty cart
    Given the user is viewing a product page
      And the shopping cart is empty
    When the user clicks "Add to Cart"
    Then the cart contains 1 item
      And the cart total reflects the product price

  Scenario: Removing an item from cart
    Given the shopping cart contains 2 items
    When the user removes the first item
    Then the cart contains 1 item
      And the cart total is updated accordingly

  Scenario: Updating item quantity
    Given the shopping cart contains "Wireless Mouse" with quantity 1
    When the user changes the quantity to 3
    Then the cart shows quantity 3 for "Wireless Mouse"
      And the line item total is multiplied by 3
```

**Destaques:**
- Cada cenário testa **uma** operação do carrinho (adicionar, remover, atualizar)
- Cenários concisos e focados no comportamento desejado

---

## User Login

```gherkin
Feature: User Login
  As a registered user
  I want to log into my account
  So that I can access my personalized dashboard

  This feature ensures secure access to user accounts
  and provides proper error handling for authentication failures.

  Scenario: User logs in successfully
    Given Alice has a valid account
    When Alice logs in with valid credentials
    Then Alice sees her personalized dashboard

  Scenario: User logs in with incorrect password
    Given Alice has a valid account
    When Alice attempts to log in with an incorrect password
    Then Alice sees an error message "Invalid credentials"
      And Alice remains on the login page

  Scenario: User account is locked after multiple failed attempts
    Given Alice has a valid account
    When Alice fails to log in 5 times consecutively
    Then Alice's account is temporarily locked
      And Alice sees a message "Account locked. Try again in 15 minutes"
```

**Destaques:**
- Personagem nomeado (`Alice`) para dar contexto humano
- Cobertura de sucesso, falha de senha e bloqueio por tentativas
- Descrição textual do propósito da *feature*

---

## Bank Account Withdrawals

```gherkin
Feature: Bank Account Withdrawals

  Background:
    Given a customer named "John" has an account
      And John's account balance is $500
      And the ATM has sufficient cash

  Scenario: Successful withdrawal within balance
    When John requests $100
    Then the ATM dispenses $100
      And John's account balance is $400

  Scenario: Withdrawal exceeds balance
    When John requests $600
    Then the ATM displays "Insufficient funds"
      And John's account balance remains $500
```

**Destaques:**
- `Background` bem utilizado para configurar o estado inicial invariável
- Cenário de sucesso e de saldo insuficiente — duas regras de negócio distintas
- Resultado financeiro claramente expresso e verificável

---

## Password Validation

```gherkin
Feature: Password Validation

  Scenario Outline: Password strength requirements
    Given a user is registering an account
    When the user enters password "<password>"
    Then the system displays "<message>"
      And the password is marked as "<status>"

    Examples:
      | password    | message                          | status   |
      | abc         | Too short (minimum 8 characters) | invalid  |
      | abcdefgh    | No numbers or special characters | weak     |
      | Abcd123!    | Good password                    | valid    |
      | P@ssw0rd!   | Strong password                  | strong   |
```

**Destaques:**
- Uso de `Scenario Outline` com tabela de `Examples` para cobrir múltiplos casos
- Dados significativos que ilustram diferentes níveis de força de senha
- Cenário único que testa todas as variações de validação

---

## Account Access Control

```gherkin
Feature: Account Access Control

  Rule: Free users can only access free content
    Scenario: Free user views free article
      Given a user with a free subscription
      When the user accesses a free article
      Then the article is displayed

    Scenario: Free user attempts to access premium content
      Given a user with a free subscription
      When the user attempts to access a premium article
      Then the user sees an upgrade prompt

  Rule: Premium users can access all content
    Scenario: Premium user views any article
      Given a user with a premium subscription
      When the user accesses any article
      Then the article is displayed
```

**Destaques:**
- `Rule` separando comportamentos por tipo de assinatura
- Cobertura de permissões para usuários free e premium
- Cenários curtos e diretos — cada um testa uma regra de negócio

---

## Comparações Lado a Lado

### Declarativo vs Imperativo

| ❌ Imperativo (Evitar) | ✅ Declarativo (Preferir) |
|---|---|
| ```gherkin | ```gherkin |
| Scenario: User logs in | Scenario: User logs in successfully |
|   Given I am on the login page |   Given Alice has a valid account |
|   When I type "user@example.com" in the email field |   When Alice logs in with valid credentials |
|     And I type "password123" in the password field |   Then Alice sees her personalized dashboard |
|     And I press the "Submit" button | ``` |
|   Then I see "Welcome" on the home page | |
| ``` | |

**Por que preferir o declarativo:**
- Foca no **o quê** (comportamento), não no **como** (implementação)
- Não vaza detalhes de UI que mudam constantemente
- Cenário mais legível para stakeholders não-técnicos
- Cenário mais resiliente a mudanças de interface

---

### UI-Specific vs Behavior-Focused

| ❌ UI-Specific (Evitar) | ✅ Behavior-Focused (Preferir) |
|---|---|
| ```gherkin | ```gherkin |
| Scenario: User filters products | Scenario: User filters products by price |
|   Given the user is on the products page |   Given the product catalog contains items |
|   When the user clicks the price dropdown |     in various price ranges |
|     And selects "$50-$100" from the dropdown |   When the user applies a price filter |
|     And clicks the "Apply Filter" button |     of $50-$100 |
|   Then the product grid refreshes |   Then only products priced between $50 |
|     And displays products in that price range |     and $100 are shown |
| ``` | ``` |

**Por que preferir o behavior-focused:**
- Descreve a **intenção do usuário**, não os cliques
- Cenário não quebra se a UI mudar (ex: dropdown vira slider)
- Foco no resultado de negócio (produtos filtrados) vs interação técnica

---

### Focused vs Multiple Behaviors

| ❌ Múltiplos Comportamentos (Evitar) | ✅ Cenários Focados (Preferir) |
|---|---|
| ```gherkin | ```gherkin |
| Scenario: Coupon application | Scenario: User with valid coupon receives discount |
|   Given a user has coupons |   Given a user has a valid 10% off coupon |
|   When the user applies a valid coupon |   When the user applies the coupon at checkout |
|   Then the discount is applied |   Then the order total is reduced by 10% |
|   When the user applies an expired coupon | |
|   Then an error is shown | Scenario: User with expired coupon sees error |
|   # This tests two different behaviors! |   Given a user has an expired coupon |
| ``` |   When the user applies the coupon at checkout |
| |   Then an error message states "Coupon has expired" |
| | ``` |

**Por que preferir cenários focados:**
- Cada cenário testa **exatamente uma** regra de negócio
- Falhas são mais fáceis de diagnosticar
- Cenários são independentes e reutilizáveis
- Legibilidade e manutenção significativamente melhores

---

### Meaningful vs Generic Data

| ❌ Dados Genéricos (Evitar) | ✅ Dados Significativos (Preferir) |
|---|---|
| ```gherkin | ```gherkin |
| Given product1 costs $25.99 | Given a product "Wireless Mouse" priced at $25.99 |
|   And product2 costs $5.99 |   And a product "USB Cable" priced at $5.99 |
| When the user adds items | When the user adds both products to the cart |
| Then total is correct | Then the cart total is $31.98 |
| ``` | ``` |

**Por que preferir dados significativos:**
- Nomes descritivos (`Wireless Mouse`) são mais memoráveis que `product1`
- O valor esperado (`$31.98`) é verificável — o leitor pode somar mentalmente
- Cenário funciona como **documentação viva** do negócio
- Dados genéricos tornam o cenário vago e difícil de depurar

---

## Boas Práticas Resumidas

| Prática | Recomendação |
|---|---|
| **Linguagem** | Declarativa — descreva o **comportamento**, não a interação |
| **Foco** | Um comportamento por cenário |
| **Dados** | Nomes e valores significativos e reais |
| **Personas** | Use nomes de pessoas (`Alice`, `John`) para dar contexto |
| **Organização** | Use `Rule` para agrupar cenários por regra de negócio |
| **Cobertura** | Inclua fluxo feliz, borda e exceção |
| **Dados comuns** | Use `Background` para configurar estado invariável |
| **Cenários parametrizados** | Use `Scenario Outline` com `Examples` para variações |

---

*Fonte: `wiki/_raw/qa/gherkin-examples/Examples real-world examples gherkin.md` (fonte bruta já ingerida)*

## Ver Também

- [[references/gherkin-syntax|Gherkin Syntax]] — Sintaxe usada nos exemplos
- [[references/gherkin-best-practices|Gherkin Best Practices]] — Práticas ilustradas nos exemplos
- [[references/cucumber-basics|Cucumber Basics]] — Como automatizar estes cenários
