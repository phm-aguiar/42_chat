---
title: "Anti Patterns"
tags: [qa, reference]
created: 2026-06-20
---
# Gherkin Anti-Patterns

## 1. Cenario com multiplos When/Then
❌ Ruim: um cenario com "Quando faco A, Entao vejo X, Quando faco B, Entao vejo Y"
✅ Bom: dois cenarios separados, cada um com seu When/Then

## 2. Steps imperativos (UI-specific)
❌ Ruim: "Dado que clico no menu 'Arquivo' e seleciono 'Salvar'"
✅ Bom: "Dado que salvo o documento"

## 3. Dados irrelevantes no cenario
❌ Ruim: "Dado que o usuario 'joao' nascido em '01/01/1990' com CPF '123.456.789-00' faz login..."
✅ Bom: "Dado que um usuario valido faz login" (dados especificos vao nos steps, nao no cenario)

## 4. Cenarios sem assercao clara
❌ Ruim: "Quando faco login, Entao o sistema responde" (responde o que?)
✅ Bom: "Quando faco login, Entao o status code e 200 E o body contem 'token'"

## 5. Testar implementacao, nao comportamento
❌ Ruim: "Entao a funcao saveUser() e chamada 1 vez"
✅ Bom: "Entao o usuario aparece na listagem de usuarios"

## 6. Cenario muito longo (mais de 5-7 steps)
Quebre em cenarios menores. Cenario longo = dificil de entender o que falhou.

## 7. Dados conflitantes entre cenarios
Se dois cenarios assumem estados diferentes do sistema, use Backgrounds separados ou feature files separados.
