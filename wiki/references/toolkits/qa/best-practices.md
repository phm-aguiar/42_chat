---
title: "Best Practices"
tags: [qa, reference]
created: 2026-06-20
rag_score: 0.4825
---
# Gherkin Best Practices

## 1. Cenarios focados
Um cenario = um comportamento. Nao agrupe casos diferentes.

❌ Ruim: "Cenario: Cadastro e login" (2 comportamentos)
✅ Bom: "Cenario: Cadastro com dados validos" e "Cenario: Login com credenciais corretas"

## 2. Declarativo, nao imperativo
Descreva O QUE, nao COMO.

❌ Ruim: "Dado que clico no botao 'Cadastrar' e preencho o campo 'email' com 'teste@email.com'"
✅ Bom: "Dado que submeto cadastro com email 'teste@email.com' e senha '123456'"

## 3. Nomes descritivos
O nome do cenario deve dizer o que ele testa.

❌ Ruim: "Cenario: Teste 1"
✅ Bom: "Cenario: Cadastro com email invalido retorna erro 400"

## 4. Background para passos comuns
Steps repetidos em todos os cenarios vao no Background.

```gherkin
Background:
  Dado que o servico de usuarios esta no ar
  E o banco de dados esta limpo
```

## 5. Esquema do Cenario para dados variados
Quando o mesmo cenario se repete com dados diferentes, use tabela.

```gherkin
Esquema do Cenario: Validacao de email
  Dado que envio POST /users com email "<email>"
  Quando valido a resposta
  Entao o status code e <status>

  Exemplos:
    | email           | status |
    | teste@email.com | 201    |
    | invalido        | 400    |
    | ""              | 400    |
```

## 6. Tags para organizacao
Use `@smoke`, `@regression`, `@unit` para categorizar cenarios.

## 7. Maximo 5-7 cenarios por feature
Se tiver mais, considere quebrar em multiplos .feature files.
