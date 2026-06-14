---
tags:
  - bdd
  - gherkin
  - boas-praticas
  - referência
  - qualidade
title: "Gherkin — Boas Práticas"
description: "Guia completo de boas práticas, anti-patterns, estilo declarativo vs imperativo, e dicas de revisão para escrever cenários Gherkin claros, manteníveis e orientados a comportamento."
---

# Gherkin — Boas Práticas

> *Escreva cenários que qualquer pessoa do negócio consiga ler. Gherkin é especificação por exemplo — a clareza vem primeiro.*

---

## Índice

1. [Uma Regra de Ouro](#1-uma-regra-de-ouro)
2. [Boas Práticas Essenciais](#2-boas-práticas-essenciais)
   - [Um Comportamento por Cenário](#um-comportamento-por-cenário)
   - [3 a 5 Passos por Cenário](#3-a-5-passos-por-cenário)
   - [Nomes Descritivos](#nomes-descritivos)
   - [Background para Configuração Compartilhada](#background-para-configuração-compartilhada)
   - [Scenario Outline para Variações de Dados](#scenario-outline-para-variações-de-dados)
   - [Rules para Agrupar Cenários Relacionados](#rules-para-agrupar-cenários-relacionados)
   - [Tags com Propósito](#tags-com-propósito)
   - [Then Observa Resultados, Não Internos](#then-observa-resultados-não-internos)
3. [Anti-Patterns Comuns](#3-anti-patterns-comuns)
   - [Linguagem Técnica nos Passos](#linguagem-técnica-nos-passos)
   - [Cenários Dependentes](#cenários-dependentes)
   - [Testar Implementação, Não Comportamento](#testar-implementação-não-comportamento)
   - [Passos Vagos](#passos-vagos)
   - [Passos em Excesso](#passos-em-excesso)
   - [Misturar Setup e Ação no Given/When](#misturar-setup-e-ação-no-givenwhen)
   - [Arquivos de Feature Sobrecarregados](#arquivos-de-feature-sobrecarregados)
   - [Given com Asserções (Assertion-Heavy Given)](#given-com-asserções-assertion-heavy-given)
   - [Perspectiva Inconsistente](#perspectiva-inconsistente)
   - [Dados Genéricos ou sem Significado](#dados-genéricos-ou-sem-significado)
   - [Futuro em Vez de Presente](#futuro-em-vez-de-presente)
   - [Acoplamento com UI](#acoplamento-com-ui)
4. [Estilo Declarativo vs Imperativo](#4-estilo-declarativo-vs-imperativo)
5. [Dicas de Revisão](#5-dicas-de-revisão)
6. [Checklist Rápido](#6-checklist-rápido)

---

## 1. Uma Regra de Ouro

> **Escreva para o Product Manager, não para o Programador.**

Cenários devem ser legíveis por qualquer pessoa que entenda o domínio do negócio — não apenas por desenvolvedores. Evite nomes de classes, verbos HTTP, operações de banco de dados ou identificadores internos.

**Muito técnico:** ❌

```gherkin
Given o InventoryService marca "SKU-7731" com stock_status = OUT_OF_STOCK
When o StockEventPublisher dispara um LOW_STOCK_EVENT para a fila
Then a linha na tabela `inventory` para "SKU-7731" tem available_qty = 0
```

**Legível para o negócio:** ✅

```gherkin
Given um produto que vendeu sua última unidade
When o nível de estoque chega a zero
Then o produto deve aparecer como "Fora de estoque" na página do catálogo
```

> A Regra de Ouro do Gherkin é simples: **trate os outros leitores como você gostaria de ser tratado.** Crie arquivos de feature que todos consigam compreender facilmente.

---

## 2. Boas Práticas Essenciais

### Um Comportamento por Cenário

Cada cenário deve verificar **exatamente um caminho** através da funcionalidade. Se você se pegar escrevendo "e também verifica…" no nome do cenário, divida-o.

**Fazendo demais:** ❌

```gherkin
Scenario: Cliente adiciona item ao carrinho e vê totais atualizados e pode removê-lo
  Given um cliente logado na página do produto
  When ele adiciona "Tábua de Corte de Bambu" ao carrinho
  Then o carrinho deve conter 1 item
  And o subtotal deve mostrar R$ 124,99
  And o ícone do carrinho deve mostrar contagem 1
  And ele deve poder clicar em "Remover"
  And após remover o carrinho deve estar vazio
```

**Focado:** ✅

```gherkin
Scenario: Contagem do carrinho atualiza ao adicionar um produto
  Given um cliente logado na página do produto
  When ele adiciona "Tábua de Corte de Bambu" ao carrinho
  Then o ícone do carrinho deve mostrar contagem 1

Scenario: Cliente remove um item do carrinho
  Given um cliente logado com "Tábua de Corte de Bambu" no carrinho
  When ele remove o item
  Then o carrinho deve estar vazio
```

---

### 3 a 5 Passos por Cenário

A média ideal: **1-2 `Given`, 1 `When`, 1-2 `Then`.** Se um cenário precisa de mais de 5 passos, geralmente está testando demais ou embutindo setup que pertence a um `Background` ou a um passo nomeado.

**Como encurtar:**

| Problema | Solução |
|---|---|
| Setup repetido entre cenários | Mover para `Background` |
| Múltiplas ações num cenário | Dividir em cenários separados |
| Asserções de outro cenário | Mover para o cenário correto |

---

### Nomes Descritivos

O nome deve contar o que acontece **sem ler os passos**. Um bom teste: alguém consegue ler os nomes num relatório de testes e entender o que quebrou?

**Muito vago:** ❌

```gherkin
Scenario: Entrada inválida
Scenario: Caso de teste 4
Scenario: Erro
```

**Descritivo:** ✅

```gherkin
Scenario: Assinante com cartão vencido é solicitado a atualizar seus dados
Scenario: Resultados da busca são filtrados quando uma categoria é selecionada
Scenario: Gerente de depósito não pode excluir uma localização que contém estoque
```

> **Padrão recomendado:** `[Ator] [ação/condição] [resultado]`

---

### Background para Configuração Compartilhada

Se todo cenário de um arquivo começa com os mesmos passos `Given`, mova-os para um bloco `Background`. Isso reduz duplicação e destaca as partes únicas de cada cenário.

```gherkin
Background:
  Given um membro da biblioteca com conta ativa
  And ele não tem empréstimos em atraso

Scenario: Membro pega um livro disponível emprestado
  When ele retira "A Biblioteca da Meia-Noite"
  Then o livro deve aparecer em seus empréstimos ativos

Scenario: Membro renova um empréstimo que vence amanhã
  Given ele tem "A Biblioteca da Meia-Noite" com vencimento amanhã
  When ele solicita uma extensão de 14 dias
  Then a data de vencimento deve ser estendida em 14 dias
```

> Mantenha o `Background` curto — idealmente **abaixo de 4 passos**. Se precisar de um background longo, talvez o arquivo de feature esteja cobrindo áreas demais.

---

### Scenario Outline para Variações de Dados

Quando o mesmo fluxo se aplica a múltiplas entradas, use `Scenario Outline` com uma tabela `Examples` em vez de duplicar cenários.

```gherkin
Scenario Outline: Faixa de desconto é aplicada com base no valor do carrinho
  Given um carrinho com subtotal de <subtotal>
  When o cliente prossegue para o checkout
  Then o desconto aplicado deve ser <desconto>

  Examples:
    | subtotal  | desconto |
    | R$ 150,00 | 0%       |
    | R$ 250,00 | 5%       |
    | R$ 500,00 | 10%      |
```

> ⚠️ Evite usar `Scenario Outline` apenas para variar dados de teste quando os valores **não representam regras de negócio distintas**. Use-o quando as variações testam casos significativamente diferentes.

---

### Rules para Agrupar Cenários Relacionados

Quando uma feature tem regras de negócio distintas, use blocos `Rule` para agrupar cenários relacionados. Isso explicita a política sendo especificada.

```gherkin
Feature: Devolução de itens

  Rule: Devoluções são aceitas dentro do prazo

    Scenario: Cliente devolve um item dentro de 30 dias da compra
      ...

    Scenario: Cliente não pode devolver um item após 30 dias
      ...

  Rule: Reembolsos refletem o método de pagamento original

    Scenario: Reembolso é creditado no cartão original
      ...

    Scenario: Compras como presente são reembolsadas como crédito na loja
      ...
```

---

### Tags com Propósito

Tags ajudam a organizar e filtrar execuções de teste. Use-as de forma consistente.

| Tag | Propósito |
|---|---|
| `@smoke` | Caminho crítico, executa em todo build |
| `@wip` | Trabalho em andamento, ainda não passa |
| `@slow` | Execução longa, roda separadamente |
| `@critical` | Cenários de alta prioridade para o negócio |
| `@regression` | Suíte completa de regressão |

> Siga as convenções de tagging já existentes no projeto. Se não houver, estabeleça-as cedo e documente-as.

---

### Then Observa Resultados, Não Internos

Passos `Then` devem descrever **o que um usuário ou sistema pode observar** — não o que aconteceu no banco, qual função foi chamada ou qual é o estado interno.

**Testando internos:** ❌

```gherkin
Then a tabela `orders` deve ter uma linha com `status = "cancelado"`
Then o OrderService deve ter chamado `releaseReservedStock()`
Then a chave redis `cart:789` deve ser deletada
```

**Observando resultados:** ✅

```gherkin
Then o status do pedido deve mostrar como "Cancelado"
Then os itens cancelados devem voltar ao estoque
Then o carrinho do cliente deve estar vazio
```

> Se você precisa verificar estado interno, considere se essa verificação pertence a um **teste unitário** em vez de um cenário Gherkin.

---

## 3. Anti-Patterns Comuns

### Linguagem Técnica nos Passos

**Problema:** Passos escritos com conceitos de código (nomes de classes, métodos HTTP, SQL, APIs internas) acoplam a especificação à implementação. Quando a implementação muda, os cenários quebram mesmo que o comportamento permaneça o mesmo.

❌ **Ruim:**
```gherkin
Given o ReservationManager é inicializado com um MockCalendarAdapter
When PUT /api/v2/bookings/42 é chamado com body {"date": "2024-09-14"}
Then a linha em `bookings` tem confirmed = true
```

✅ **Melhor:**
```gherkin
Given um cliente com uma reserva futura
When ele altera a data para "14 de Setembro"
Then a reserva deve ser atualizada
And ele deve ver um resumo de confirmação
```

---

### Cenários Dependentes

**Problema:** Cenários que dependem de cenários anteriores terem executado primeiro. Isso torna a ordem de execução relevante, impede execução paralela e causa falhas em cascata difíceis de diagnosticar.

❌ **Ruim:**
```gherkin
Scenario: Vendedor cria um anúncio
  Given o painel do vendedor
  When ele preenche o formulário do produto e envia
  Then o anúncio deve aparecer no catálogo

Scenario: Vendedor edita o anúncio
  # Depende de "Vendedor cria um anúncio" ter executado primeiro!
  When ele atualiza o preço no anúncio do cenário anterior
  Then o catálogo deve mostrar o preço atualizado
```

✅ **Melhor:**
```gherkin
Scenario: Vendedor edita o preço de um anúncio existente
  Given um vendedor com um anúncio publicado para "Sabonete Artesanal" a R$ 40,00
  When ele atualiza o preço para R$ 47,50
  Then o catálogo deve mostrar o novo preço de R$ 47,50
```

> Cada cenário deve configurar **suas próprias pré-condições** nos passos `Given`.

---

### Testar Implementação, Não Comportamento

**Problema:** Cenários que descrevem **como** o sistema funciona internamente em vez de **o que** ele faz para o usuário. Viram uma carga de manutenção quando a implementação refatora.

❌ **Ruim:**
```gherkin
Scenario: Índice de busca é reconstruído após atualização de produto
  Given um produto com título "Luminária Azul" indexado no Elasticsearch
  When o título do produto é alterado para "Luminária Marinha"
  Then uma requisição PUT para /indexes/products/42 deve ser disparada
  And o documento do índice deve conter título "Luminária Marinha"
```

✅ **Melhor:**
```gherkin
Scenario: Título de produto atualizado aparece nos resultados de busca
  Given um produto intitulado "Luminária Azul" disponível no catálogo
  When o título do produto é atualizado para "Luminária Marinha"
  Then buscar por "Luminária Marinha" deve retornar o produto
  And buscar por "Luminária Azul" não deve retornar resultados
```

---

### Passos Vagos

**Problema:** Passos tão genéricos que poderiam significar qualquer coisa. Dificulta diagnosticar falhas e reutilizar cenários.

❌ **Ruim:**
```gherkin
Given o sistema está no estado certo
When a coisa acontece
Then deve funcionar
```

✅ **Melhor:**
```gherkin
Given um vendedor cuja conta foi suspensa por falta de pagamento
When ele tenta publicar um novo anúncio
Then ele deve ver "Sua conta precisa estar em situação regular para publicar anúncios"
```

> Nomeie passos para descrever um **estado ou ação específica e observável**. Evite "a coisa", "ele", "o estado", "funciona corretamente".

---

### Passos em Excesso

**Problema:** Cenários com 8, 10 ou mais passos estão fazendo demais. São difíceis de ler, manter, e quando falham é difícil identificar qual passo revelou o problema.

❌ **Ruim:**
```gherkin
Scenario: Cliente completa o onboarding
  Given o assistente de onboarding
  And o cliente insere o nome da empresa
  And ele faz upload de um logotipo
  And ele clica em Próximo
  And ele escolhe seu setor
  And ele clica em Próximo
  And ele insere o endereço de cobrança
  And ele clica em Próximo
  And ele adiciona um método de pagamento
  And ele clica em Finalizar
  Then ele deve ver o painel principal
  And a lista de verificação deve mostrar 100% completo
  And ele deve receber um e-mail de boas-vindas
```

✅ **Melhor:** Divida em cenários focados, cada um cobrindo um estágio do fluxo. Use `Background` para setup compartilhado. Use `Scenario Outline` se a mesma validação se aplica a múltiplos campos.

---

### Misturar Setup e Ação no Given/When

**Problema:** Passos `Given` devem estabelecer pré-condições — não devem executar ações que estão sob teste. Quando `Given` faz demais, o cenário obscurece o que está sendo testado de fato.

❌ **Ruim:**
```gherkin
Scenario: Cliente vê histórico de reservas após fazer uma reserva
  Given o cliente navega até a página de reservas e reserva uma mesa para "14 de Setembro"
  When ele abre seu histórico de reservas
  Then ele deve ver "14 de Setembro" em suas reservas futuras
```

✅ **Melhor:**
```gherkin
Scenario: Cliente vê histórico de reservas após fazer uma reserva
  Given um cliente que tem uma reserva confirmada para "14 de Setembro"
  When ele abre seu histórico de reservas
  Then ele deve ver "14 de Setembro" em suas reservas futuras
```

> `Given` **configura o estado**. `When` **descreve a única ação** sendo testada.

---

### Arquivos de Feature Sobrecarregados

**Problema:** Um único arquivo `.feature` cobrindo comportamentos não relacionados, ou dezenas de cenários espalhados por muitas regras de negócio diferentes.

**Sinais de arquivo sobrecarregado:**
- A descrição da `Feature` é muito genérica ("Gestão de produtos", "Reservas")
- O arquivo tem **20+ cenários**
- Cenários no arquivo não têm nada em comum entre si
- Múltiplos blocos `Rule` que poderiam ser features separadas

✅ **Melhor:** Divida em arquivos `.feature` separados por área de negócio. Exemplo: `catalogo/criacao-anuncios.feature`, `catalogo/visibilidade-anuncios.feature`, `catalogo/precificacao.feature`.

> É comum ver **5 a 20 cenários por Feature**. Acima de 20, considere dividir.

---

### Given com Asserções (Assertion-Heavy Given)

**Problema:** Passos `Given` que incluem asserções (verificar se algo é verdade antes do teste executar) em vez de apenas configurar estado. Asserções pertencem ao `Then`.

❌ **Ruim:**
```gherkin
Given o evento está publicado e as vendas de ingressos estão abertas e o local está confirmado
And há lugares disponíveis e o participante tem um método de pagamento válido
When ele compra um ingresso
Then o ingresso deve ser emitido
```

✅ **Melhor:**
```gherkin
Given um evento publicado com ingressos disponíveis
When um cliente com método de pagamento válido compra um ingresso
Then o ingresso deve ser emitido
```

> Mantenha o `Given` focado: descreva o **estado do mundo no início do cenário**, não asserções sobre ele.

---

### Perspectiva Inconsistente

**Problema:** Misturar primeira pessoa ("eu") e terceira pessoa ("o administrador") no mesmo arquivo ou cenário cria confusão sobre quem é o ator.

❌ **Ruim:**
```gherkin
Given estou logado
When o administrador cria uma conta
Then devo ver uma confirmação
```

✅ **Melhor:**
```gherkin
Given Alice está logada como administradora
When Alice cria uma nova conta de usuário
Then o novo usuário recebe um e-mail de boas-vindas
```

> Escolha **terceira pessoa com nomes concretos** (Alice, José, etc.) e seja consistente.

---

### Dados Genéricos ou sem Significado

**Problema:** Usar dados de teste sem significado (produto1, item2) torna os cenários mais difíceis de entender. BDD é especificação por exemplo — os dados devem apoiar a natureza descritiva dos cenários.

❌ **Ruim:**
```gherkin
Given produto1 custa R$ 129,99
  And produto2 custa R$ 29,99
When o usuário adiciona itens
Then o total está correto
```

✅ **Melhor:**
```gherkin
Given um produto "Mouse Sem Fio" com preço de R$ 129,99
  And um produto "Cabo USB" com preço de R$ 29,99
When o usuário adiciona ambos os produtos ao carrinho
Then o total do carrinho é R$ 159,98
```

---

### Futuro em Vez de Presente

**Problema:** Comportamentos são aspectos **presentes** do sistema, não previsões futuras.

❌ **Ruim:**
```gherkin
Then a mensagem de confirmação **será** exibida
```

✅ **Melhor:**
```gherkin
Then a mensagem de confirmação **é** exibida
```

---

### Acoplamento com UI

**Problema:** Cenários atrelados a elementos específicos de UI (botões, campos, dropdowns) são frágeis e quebram quando a interface muda.

❌ **Ruim (acoplado à UI):**
```gherkin
Scenario: Usuário filtra produtos
  Given o usuário está na página de produtos
  When o usuário clica no dropdown de preço
    And seleciona "R$ 250 - R$ 500" no menu suspenso
    And clica no botão "Aplicar Filtro"
  Then a grade de produtos atualiza
    And exibe produtos na faixa de preço
```

✅ **Melhor (focado em comportamento):**
```gherkin
Scenario: Usuário filtra produtos por preço
  Given o catálogo de produtos contém itens em várias faixas de preço
  When o usuário aplica um filtro de preço de R$ 250 a R$ 500
  Then apenas produtos entre R$ 250 e R$ 500 são exibidos
```

---

## 4. Estilo Declarativo vs Imperativo

### Imperativo (❌ Evitar)

Testes imperativos comunicam detalhes e são fortemente atrelados à mecânica da UI atual, exigindo mais trabalho de manutenção. Qualquer mudança na implementação exige atualizar os testes.

```gherkin
Scenario: Usuário faz login
  Given estou na página de login
  When digito "usuario@exemplo.com" no campo de e-mail
    And digito "senha123" no campo de senha
    And pressiono o botão "Enviar"
  Then vejo "Bem-vindo" na página inicial
```

### Declarativo (✅ Preferido)

O estilo declarativo descreve o **comportamento da aplicação**, não os detalhes de implementação. Cenários declarativos funcionam melhor como "documentação viva" e ajudam a focar no valor que o cliente está obtendo.

```gherkin
Scenario: Usuário faz login com sucesso
  Given Alice tem uma conta válida
  When Alice faz login com credenciais válidas
  Then Alice vê seu painel personalizado
```

### A Diferença Fundamental

| Estilo | Foco | Exemplo | Manutenção |
|---|---|---|---|
| **Imperativo** | **Como** o sistema implementa | "clica no botão", "digita no campo" | Alta — quebra com mudanças de UI |
| **Declarativo** | **O que** o sistema faz | "faz login", "aplica filtro" | Baixa — isolado da implementação |

> **Pergunte-se:** Este cenário descreve o comportamento esperado ou os detalhes de como ele é implementado? Se a resposta for "detalhes de implementação", reescreva.

---

## 5. Dicas de Revisão

Ao revisar cenários Gherkin — seus ou de outras pessoas — use estas perguntas como guia:

### 📝 Clareza e Legibilidade

- [ ] Uma pessoa não-técnica do negócio conseguiria entender este cenário?
- [ ] O nome do cenário conta a história sem precisar ler os passos?
- [ ] Os dados usados são significativos e realistas (não "produto1", "item2")?
- [ ] O tempo verbal é presente ("é exibida"), não futuro ("será exibida")?
- [ ] A perspectiva é consistente em terceira pessoa?

### 🎯 Escopo e Foco

- [ ] Cada cenário testa **exatamente um comportamento**?
- [ ] O cenário tem entre 3 e 5 passos? (máximo 5-7 em casos excepcionais)
- [ ] Se há mais de um `When`, os comportamentos deveriam ser separados?
- [ ] O arquivo de feature tem menos de 20 cenários? Senão, deveria ser dividido?

### 🧱 Estrutura

- [ ] Setup repetido entre cenários foi movido para um `Background`?
- [ ] O `Background` tem menos de 4 passos?
- [ ] Variações de dados usam `Scenario Outline` em vez de cenários duplicados?
- [ ] Regras de negócio distintas estão agrupadas com `Rule`?
- [ ] Tags estão sendo usadas consistentemente?

### 🚫 Evitando Anti-Patterns

- [ ] Não há linguagem técnica (nomes de classes, HTTP, SQL, APIs internas)?
- [ ] Nenhum cenário depende de outro cenário ter executado primeiro?
- [ ] `Then` observa resultados observáveis, não internos do sistema?
- [ ] `Given` apenas configura estado — não contém asserções nem ações sob teste?
- [ ] Nenhum passo é vago ou genérico ("a coisa acontece", "funciona corretamente")?
- [ ] Cenários descrevem **o que** o sistema faz, não **como** ele implementa?
- [ ] Não há acoplamento com elementos específicos de UI (botões, campos, dropdowns)?

### 🔄 Declarativo vs Imperativo

- [ ] Os passos estão no estilo declarativo (comportamento) ou imperativo (cliques, digitação)?
- [ ] Um iniciante no projeto entenderia o valor de negócio do cenário?

---

## 6. Checklist Rápido

```markdown
- [ ] Nome descritivo seguindo o padrão [Ator] [ação] [resultado]
- [ ] Um comportamento por cenário
- [ ] 3-5 passos (Given 1-2, When 1, Then 1-2)
- [ ] Setup compartilhado em Background (máx. 4 passos)
- [ ] Variações de dados em Scenario Outline
- [ ] Regras de negócio agrupadas com Rule
- [ ] Tags consistentes (@smoke, @wip, @critical, etc.)
- [ ] Then observa resultados — não internos
- [ ] Linguagem de negócio, não técnica
- [ ] Cenários independentes (sem ordem de execução)
- [ ] Estilo declarativo (o quê), não imperativo (como)
- [ ] Presente, não futuro
- [ ] Dados significativos e realistas
- [ ] Perspectiva consistente em terceira pessoa
```

---

> **Lembre-se:** BDD é uma prática de **colaboração** primeiro. Escreva cenários **com** as partes interessadas do negócio, não **para** elas. Trate seus arquivos `.feature` como **documentação viva** — mantenha-os atualizados conforme o sistema evolui.
