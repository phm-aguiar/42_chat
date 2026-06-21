---
feature_id: "004"
title: "jschan Forum Manager"
status: draft
created: "2026-06-20"
author: phm-aguiar
tags: [sdd, jschan, forum, imageboard, mongodb, crud, wiki, skill, devops]
based_on:
  - "jschan v1.7.x (engine de imageboard Node.js/MongoDB/Redis)"
  - "Repositório local: jschan/"
depends_on: ~
---

**Aprovado:** true

# jschan Forum Manager

> Documentação wiki completa + skill Hermes para CRUD de boards jschan via MongoDB direto.
> Instalação do jschan fica como documentação manual (muitos secrets e passos infra).

## Propósito

O repositório contém o engine jschan (imageboard anônimo) mas não há documentação
estruturada nem automação para criar/gerenciar boards. Hoje o operador precisa
entrar no painel web, preencher formulário, lidar com captcha — tudo manual.

**Esta feature entrega:**
1. Documentação completa no wiki sobre jschan (arquitetura, instalação, operação)
2. Skill Hermes `jschan-forum-manager` que faz CRUD de boards via `mongosh` direto,
   sem depender do jschan estar rodando ou de sessão autenticada

## Escopo

### Wiki (documentação)
- Página `wiki/tools/jschan/overview.md` — o que é, stack, arquitetura
- Página `wiki/tools/jschan/installation.md` — passo a passo de instalação (manual)
- Página `wiki/tools/jschan/operations.md` — como operar: criar boards, gerenciar staff, bans

### Skill (automação)
- **Create:** inserir board no MongoDB com name, description, uri, owner, tags
- **Read/List:** listar todos os boards ou buscar um por URI
- **Update:** editar settings do board (name, description, theme, language, custom CSS, announcement)
- **Delete:** remover board e todos os dados relacionados (posts, bans, modlogs, filters, stats, arquivos, custom pages)
- **Parâmetros de conexão:** `--mongo-url` e `--db-name` (genérica, qualquer instância)

Fora do escopo:
- Instalação automatizada do jschan (muitos secrets e passos sensíveis)
- Gestão de posts individuais (pin, lock, move, delete)
- Gestão de bans, staff, reports, filters
- Configurações globais do jschan
- Bypass de captcha para API HTTP

## Constraints

- Usar `mongosh` (CLI oficial MongoDB) — disponível no container Docker ou instalado no host
- Skill opera com scripts shell chamando `mongosh --eval` — sem dependências Node.js extras
- Conexão MongoDB parametrizável (connection string + dbName)
- Board delete é destrutivo e irreversível — pedir confirmação explícita
- Documentação wiki segue padrão OFM (Obsidian Flavored Markdown) com frontmatter YAML
- Board `uri` validado contra reserved URIs: captcha, forms, randombanner, all

## Critérios de Sucesso

1. Wiki com 3 páginas completas (overview, installation, operations)
2. Skill cria board com mongosh e retorna confirmação com URI
3. Skill lista boards existentes (nome, uri, owner, post count)
4. Skill atualiza settings de board (name, description, theme) e verifica mudança
5. Skill deleta board com confirmação interativa e remove dados relacionados
6. Skill funciona com conexão MongoDB parametrizada (não hardcoded)
7. Validação de URI reservada bloqueia criação de board inválido
8. Smoke test real: criar, listar, editar, deletar board via skill

## Edge Cases

- URI duplicada (board já existe) → erro claro, sem sobrescrever
- URI reservada (captcha, forms, randombanner, all) → rejeitar com mensagem
- MongoDB offline → erro de conexão com diagnóstico
- Board não encontrado no update/delete → erro 404
- Delete sem confirmação → abortar
- Campos obrigatórios ausentes (name, uri, owner) → validar antes de inserir
- Tags vazias ou mal formatadas → sanitizar (split + filter)
- Board com posts existentes no delete → avisar quantidade e pedir confirmação extra
