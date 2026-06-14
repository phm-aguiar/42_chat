---
title: "Sintaxe Gherkin — Referência Completa"
summary: "Guia de referência completo da sintaxe Gherkin para BDD (Behavior-Driven Development). Abrange estrutura de feature files, keywords, step arguments, Scenario Outline, internacionalização, convenções de nomenclatura, organização de diretórios e quick reference."
tags:
  - gherkin
  - syntax
  - reference
  - bdd
category: references
created: "2026-06-13"
updated: "2026-06-14"
---

# Sintaxe Gherkin — Referência Completa

---

## O que é Gherkin?

Gherkin é uma linguagem de domínio específico (DSL) para especificar o comportamento de aplicações de forma legível por humanos. Utiliza texto simples em linguagem natural, preenchendo a lacuna de comunicação entre stakeholders de negócio, desenvolvedores e testadores.

### Características Principais

- **Linguagem legível**: elimina jargão técnico; qualquer pessoa do time pode entender
- **Documentação viva**: os cenários servem como especificação executável
- **Testes executáveis**: pode ser executado como testes automatizados com ferramentas como Cucumber, Behat, SpecFlow, etc.
- **Internacionalizado**: suporta dezenas de idiomas com keywords localizadas

---

## Estrutura Básica de um Feature File

Cada arquivo `.feature` contém **exatamente uma** `Feature`. As features podem conter cenários (scenarios) agrupados opcionalmente por `Rule`.

```gherkin
# language: en
Feature: Título Curto da Feature
  Uma descrição mais longa da feature.
  Pode abranger múltiplas linhas.

  Background:
    Given pré-condição compartilhada para todos os cenários

  Rule: Agrupamento de regra de negócio (opcional, Gherkin 6+)

    Scenario: Nome do cenário
      Given alguma pré-condição
      When uma ação acontece
      Then um resultado esperado

    Scenario: Outro cenário
      Given alguma pré-condição
      When uma ação diferente acontece
      Then um resultado diferente
```

---

## Keyword Reference

### Keywords Principais

| Keyword | Propósito | Exemplo |
|---------|-----------|---------|
| `Feature:` | Agrupamento de alto nível (um por arquivo) | `Feature: Autenticação de Usuário` |
| `Scenario:` / `Example:` | Um caso de teste concreto (são sinônimos) | `Scenario: Login bem-sucedido` |
| `Given` | Estabelece contexto inicial (pré-condições) | `Given o usuário está na página de login` |
| `When` | Descreve a ação ou evento | `When o usuário insere credenciais válidas` |
| `Then` | Afirma o resultado esperado | `Then o usuário é logado no sistema` |
| `And` | Passo adicional do mesmo tipo anterior | `And o dashboard é exibido` |
| `But` | Passo adicional negativo | `But a mensagem de erro não é exibida` |
| `*` | Keyword curinga para passos (listas) | `* item na lista de tarefas` |
| `Background:` | Setup compartilhado executado antes de cada cenário | — |
| `Scenario Outline:` | Template parametrizado para múltiplos casos de teste | — |
| `Examples:` | Tabela de dados para o Scenario Outline | — |
| `Rule:` | Agrupamento de cenários por regra de negócio (Gherkin 6+) | — |

### Tabela de Keywords Avançadas

| Keyword | Propósito | Uso |
|---------|-----------|-----|
| `Background:` | Setup comum para todos os cenários da feature | Executa antes de cada cenário |
| `Scenario Outline:` | Template para múltiplos casos de teste | Usado com tabela Examples |
| `Examples:` | Tabela de dados para o Scenario Outline | Fornece variações de dados de teste |
| `Rule:` | Agrupamento de regra de negócio (Gherkin 6+) | Agrupa cenários relacionados |
| `*` | Keyword curinga | Substitui Given/When/Then em listas |
| `@tag` | Tags para organizar e filtrar cenários | `@smoke @regression @wip` |
| `#` | Comentários (linha inteira apenas) | `# Isto é um comentário` |

---

## A Estrutura Given-When-Then

A notação Given-When-Then é considerada uma das melhores para garantir que uma especificação seja abrangente e precisa.

### GIVEN — Contexto / Pré-condições

Define o estado inicial antes da ação acontecer.

```gherkin
Given o usuário está logado
Given o carrinho de compras contém 3 itens
Given existe um post intitulado "Meu Primeiro Post"
Given o usuário tem uma assinatura premium
```

### WHEN — Ação / Evento

A ação que dispara o comportamento a ser testado.

```gherkin
When o usuário clica no botão "Finalizar Compra"
When o usuário submete o formulário de registro
When o usuário busca por "câmera vintage"
When um novo comentário é postado
```

### THEN — Resultado Esperado

Define as condições que determinam se o teste passou ou falhou.

```gherkin
Then o usuário vê uma mensagem de confirmação
Then o carrinho de compras está vazio
Then os resultados da busca são exibidos
Then o comentário aparece no topo da lista
```

### AND / BUT — Passos Adicionais

Use `And` e `But` para adicionar condições sem repetir Given/When/Then.

```gherkin
Given o usuário está na página de login
  And o usuário tem uma conta válida
When o usuário insere credenciais corretas
  And clica no botão "Entrar"
Then o usuário vê o dashboard
  And o nome do usuário aparece no cabeçalho
  But o painel de administração não está visível
```

---

## A Seção Feature

```gherkin
Feature: Login de Usuário
  Como um usuário registrado
  Eu quero fazer login na minha conta
  Para que eu possa acessar meu dashboard personalizado

  Esta feature garante acesso seguro às contas de usuário
  e fornece tratamento adequado de erros para falhas de autenticação.
```

### Template de Injeção de Feature

Para identificar features no sistema, use o template de injeção:

```
Para <atingir algum objetivo>
Como um <tipo de usuário>
Eu quero <uma funcionalidade>
```

### Boas Práticas para a Descrição da Feature

- Comece com um título claro e descritivo
- Inclua o formato "Como um... Eu quero... Para que..." para contexto
- Adicione descrição adicional para features complexas
- Mantenha em alto nível — não descreva implementação

---

## Background — Setup Compartilhado

O `Background` permite definir critérios de setup que serão usados por todos os cenários da feature. Estes critérios são definidos uma vez e executados antes de cada cenário.

```gherkin
Feature: Saques em Conta Bancária

  Background:
    Given um cliente chamado "João" tem uma conta
      And o saldo da conta do João é R$ 500
      And o caixa eletrônico tem dinheiro suficiente

  Scenario: Saque bem-sucedido dentro do saldo
    When João solicita R$ 100
    Then o caixa eletrônico libera R$ 100
      And o saldo da conta do João é R$ 400

  Scenario: Saque excede o saldo
    When João solicita R$ 600
    Then o caixa eletrônico exibe "Saldo insuficiente"
      And o saldo da conta do João permanece R$ 500
```

**Quando usar Background:**
- Múltiplos cenários compartilham os mesmos passos de setup
- Reduz repetição entre cenários
- Torna os cenários mais focados no comportamento único

---

## Scenario Outline — Variações de Dados

O `Scenario Outline` permite executar o mesmo cenário múltiplas vezes com diferentes conjuntos de dados. A seção de outline é sempre seguida por uma ou mais seções `Examples`, que contêm uma tabela.

```gherkin
Feature: Validação de Senha

  Scenario Outline: Requisitos de força de senha
    Given um usuário está registrando uma conta
    When o usuário insere a senha "<senha>"
    Then o sistema exibe "<mensagem>"
      And a senha é marcada como "<status>"

    Examples:
      | senha      | mensagem                             | status   |
      | abc        | Muito curta (mínimo 8 caracteres)    | inválida |
      | abcdefgh   | Sem números ou caracteres especiais  | fraca    |
      | Abcd123!   | Senha boa                            | válida   |
      | P@ssw0rd!  | Senha forte                          | forte    |
```

**Quando usar Scenario Outline:**
- Testar o mesmo comportamento com diferentes entradas
- Focar em classes de equivalência únicas em vez de testar "tudo"
- Variações de dados são importantes para a especificação

---

## Rule — Agrupamento por Regra de Negócio (Gherkin 6+)

O propósito da keyword `Rule` é representar uma regra de negócio que deve ser implementada. Uma `Rule` agrupa vários cenários que pertencem a esta regra de negócio.

```gherkin
Feature: Controle de Acesso à Conta

  Rule: Usuários gratuitos só podem acessar conteúdo gratuito
    Scenario: Usuário gratuito visualiza artigo gratuito
      Given um usuário com assinatura gratuita
      When o usuário acessa um artigo gratuito
      Then o artigo é exibido

    Scenario: Usuário gratuito tenta acessar conteúdo premium
      Given um usuário com assinatura gratuita
      When o usuário tenta acessar um artigo premium
      Then o usuário vê um prompt de upgrade

  Rule: Usuários premium podem acessar todo o conteúdo
    Scenario: Usuário premium visualiza qualquer artigo
      Given um usuário com assinatura premium
      When o usuário acessa qualquer artigo
      Then o artigo é exibido
```

---

## Step Arguments

### Doc Strings — Texto Multilinha

Doc strings permitem passar blocos de texto maiores como argumento de um passo. São delimitadas por três aspas duplas (`"""`).

```gherkin
Given um ticket de suporte com a descrição:
  """
  A página de checkout falha ao carregar quando uso Safari.
  Isso aconteceu três vezes esta semana.
  """
```

### Data Tables — Dados Estruturados

Data tables fornecem dados estruturados em formato tabular para um passo.

```gherkin
Given os seguintes produtos estão no catálogo:
  | nome             | sku     |
  | Caneca Cerâmica  | MUG-001 |
  | Caderno Bambu    | NB-042  |

When o usuário adiciona ao carrinho:
  | produto         | quantidade |
  | Caneca Cerâmica | 2          |
  | Caderno Bambu   | 1          |
```

---

## Internacionalização (i18n)

Gherkin suporta a escrita de cenários em diversos idiomas. Para usar keywords traduzidas, adicione o cabeçalho `# language: xx` como **primeira linha** do arquivo `.feature`.

```gherkin
# language: pt
Funcionalidade: Reserva de Mesa
  Clientes podem reservar uma mesa no restaurante.

  Cenário: Cliente reserva mesa disponível
    Dado uma mesa disponível no "14 de setembro" às 19h para 2 pessoas
    Quando o cliente reserva para 2 pessoas às 19h
    Então a reserva deve ser confirmada
```

### Códigos de Idioma Comuns

| Código | Idioma      | Keyword Feature (exemplo) |
|--------|-------------|---------------------------|
| `en`   | Inglês      | `Feature:` _(padrão)_     |
| `pt`   | Português   | `Funcionalidade:`         |
| `fr`   | Francês     | `Fonctionnalité:`         |
| `es`   | Espanhol    | `Característica:`         |
| `de`   | Alemão      | `Funktionalität:`         |
| `it`   | Italiano    | `Funzionalità:`           |
| `ja`   | Japonês     | `フィーチャ:`             |
| `zh-CN`| Chinês (Simplificado) | `功能:`        |
| `nl`   | Holandês    | `Functionaliteit:`        |
| `ru`   | Russo       | `Функционал:`             |

> Para a lista completa de idiomas suportados e traduções de keywords, consulte a [referência i18n do Cucumber](https://cucumber.io/docs/gherkin/languages/).

---

## Convenções de Nomenclatura de Arquivos

Convenção padrão: converter o nome da feature para **minúsculas** e substituir **espaços por underlines**.

| Nome da Feature                 | Nome do Arquivo                          |
|---------------------------------|------------------------------------------|
| User Authentication             | `user_authentication.feature`            |
| Shopping Cart Checkout          | `shopping_cart_checkout.feature`         |
| Password Reset Flow             | `password_reset_flow.feature`            |
| Feedback When Entering Invalid Credit Card Details | `feedback_when_entering_invalid_credit_card_details.feature` |

### Convenções Alternativas (encontradas em projetos reais)

- `reservations.feature` — minúsculas, sem hífen (mais comum)
- `booking-cancellation.feature` — minúsculas com hífens
- `BookingCancellation.feature` — PascalCase (menos comum)
- `booking_cancellation.feature` — snake_case

**Regras gerais:**
- Use o nome que uma pessoa de produto usaria para a feature
- Seja específico: `listing-visibility.feature` é melhor que `catalogue.feature`
- Siga a convenção já existente no projeto (consistência > qualquer convenção)
- Uma feature por arquivo — não combine features não relacionadas

---

## Organização de Diretórios

Não existe uma estrutura única e correta. Abaixo estão os padrões mais comuns.

### Simples (plano) — Um único diretório

```
features/
  search.feature
  listings.feature
  bookings.feature
  reviews.feature
```

Funciona bem para projetos pequenos ou com conjunto limitado de features.

### Médio (agrupado por área) — Subdiretórios por área

```
features/
  catalogue/
    listings.feature
    search.feature
    reviews.feature
  bookings/
    reservations.feature
    cancellations.feature
    availability.feature
  account/
    profile.feature
    notifications.feature
```

Funciona bem para projetos de médio porte. Facilita executar todos os specs de uma área.

### Grande (espelhando módulos da aplicação)

```
features/
  discovery/
    search/
    recommendations/
  marketplace/
    listings/
    pricing/
  transactions/
    bookings/
    payments/
    refunds/
```

Funciona bem quando a aplicação tem contextos delimitados ou módulos de domínio claros.

### Para Projetos Novos

1. **Escolha um diretório raiz.** `features/` na raiz do projeto é o padrão mais comum. `test/features/` ou `spec/features/` se o projeto tiver uma convenção existente.
2. **Comece plano.** Não crie subdiretórios para 3 arquivos de feature. Introduza subdiretórios quando a lista plana ficar difícil de navegar (~8-10 arquivos).
3. **Estabeleça nomenclatura cedo.** Lowercase com hífens (`feature-name.feature`) é um padrão seguro. Comprometa-se com um estilo desde o início.
4. **Estabeleça tags cedo.** Decida por `@smoke`, `@critical`, `@wip` antes que o projeto tenha 50 cenários — retroagir tags é doloroso.

### Quando Criar vs. Quando Adicionar a um Arquivo Existente

**Adicione a um arquivo existente quando:**
- Os novos cenários pertencem a uma feature que já tem um arquivo `.feature`
- O comportamento é uma variação do que já está lá (ex.: adicionar outro bloco `Rule` ou mais linhas de `Scenario Outline`)
- O arquivo não está muito grande (~ < 15-20 cenários)

**Crie um novo arquivo quando:**
- Nenhum arquivo existente cobre esta área de feature
- O novo comportamento é conceitualmente distinto de qualquer arquivo existente
- O arquivo mais próximo já é grande o suficiente para que adicionar mais prejudicaria a legibilidade

---

## Quick Reference

### Template de Feature File

```gherkin
Feature: [Nome da Feature]
  [Opcional: Como um... Eu quero... Para que...]

  [Opcional: descrição multilinha]

  Background:
    Given [setup comum que se aplica a todos os cenários]

  Scenario: [Nome do cenário descrevendo comportamento específico]
    Given [contexto/pré-condição]
      And [contexto adicional]
    When [ação/trigger]
      And [ação adicional]
    Then [resultado esperado]
      And [resultado adicional]
      But [asserção negativa]

  Scenario Outline: [Template para múltiplos casos de teste]
    Given [contexto com "<parâmetro>"]
    When [ação com "<parâmetro>"]
    Then [resultado com "<parâmetro>"]

    Examples:
      | parâmetro  | outro_param |
      | valor1     | resultado1  |
      | valor2     | resultado2  |
```

### Guia Rápido Given-When-Then

| Passo | Propósito | Exemplos |
|-------|-----------|----------|
| **Given** | Contexto inicial | `Given o usuário está logado` / `Given o carrinho contém 3 itens` |
| **When** | Ação que dispara o comportamento | `When o usuário clica em "Checkout"` / `When o formulário é submetido` |
| **Then** | Resultado esperado | `Then o usuário vê confirmação` / `Then o carrinho está vazio` |

### Checklist de Cenários de Qualidade

- [ ] Nome do cenário é claro e descritivo
- [ ] Usa terceira pessoa consistentemente
- [ ] Focado em um comportamento específico
- [ ] Passos em presente do indicativo
- [ ] Sem detalhes específicos de UI (botões, campos)
- [ ] Sem detalhes de implementação (APIs, banco de dados)
- [ ] Dados de teste significativos e realistas
- [ ] Cenário pode ser executado independentemente
- [ ] Menos de 10 passos no total
- [ ] Resultados claros e específicos nos passos Then
- [ ] Usa `And`/`But` para evitar repetição desnecessária de keywords

### Árvore de Decisão Rápida

**É uma nova feature de negócio?**
- Sim → Crie novo arquivo `.feature`

**O cenário se relaciona a uma feature existente?**
- Sim → Adicione ao arquivo `.feature` existente

**A feature tem mais de 20 cenários?**
- Sim → Divida em múltiplos arquivos ou use `Rule`

**Múltiplos cenários compartilham o mesmo setup?**
- Sim → Use `Background`

**Precisa testar o mesmo comportamento com dados diferentes?**
- Sim → Use `Scenario Outline`

### Lembretes Importantes

**FAÇA:**
- Use estilo declarativo (o quê, não como)
- Mantenha cenários focados (< 10 passos)
- Use presente do indicativo
- Seja específico e claro
- Use dados de teste significativos
- Torne cenários independentes
- Escreva para stakeholders de negócio

**NÃO FAÇA:**
- Incluir detalhes de implementação
- Usar jargão técnico
- Criar cenários que dependam uns dos outros
- Misturar múltiplos comportamentos em um cenário
- Usar asserções vagas
- Acoplar a elementos específicos de UI
- Escrever cenários com mais de 10 passos

---

> **Regra de Ouro:** Trate os outros leitores como você gostaria de ser tratado. Escreva cenários que qualquer pessoa do time — stakeholders de negócio, desenvolvedores, testadores — possa entender sem conhecimento técnico.

---

## Referências

- [Cucumber Gherkin Documentation](https://cucumber.io/docs/gherkin/)
- [Gherkin i18n — Lista completa de idiomas](https://cucumber.io/docs/gherkin/languages/)
- [Cucumber Best Practices](https://cucumber.io/docs/bdd/best-practices/)
