---
feature_id: "004"
title: "jschan Forum Manager"
spec: "specs/features/004-jschan-forum-manager/spec.md"
plan: "specs/features/004-jschan-forum-manager/plan.md"
created: "2026-06-20"
author: phm-aguiar
depends_on: ~
---

# Tasks — jschan Forum Manager

> DAG de 15 tasks em 3 fases. Wiki (3) → Skill scripts (6) → Smoke + Wiki update (6).

## Fase 1: Documentação Wiki

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T001 | Página overview: stack (Node.js/MongoDB/Redis/Nginx), arquitetura, features, licença AGPLv3 | Dev | — | true | `wiki/tools/jschan/overview.md` |
| T002 | Página installation: passo a passo traduzido do INSTALLATION.md (MongoDB, Redis, Node, Nginx, setup, reset, pm2) | Dev | — | true | `wiki/tools/jschan/installation.md` |
| T003 | Página operations: schema Boards, CRUD via mongosh, reserved URIs, board settings tree, exemplos de comandos | Dev | — | true | `wiki/tools/jschan/operations.md` |

## Fase 2: Scripts da Skill

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T004 | Script create: validar reserved URIs, checar duplicata, insertOne com owner+settings+staff, retornar JSON | Dev | — | true | `.hermes/skills/jschan-forum-manager/scripts/create.sh` |
| T005 | Script list: find({}), projetar {_id, name, owner, sequence_value, pph}, ordenar por _id | Dev | — | true | `.hermes/skills/jschan-forum-manager/scripts/list.sh` |
| T006 | Script get: findOne({_id: uri}), retornar JSON completo do board | Dev | — | true | `.hermes/skills/jschan-forum-manager/scripts/get.sh` |
| T007 | Script update: updateOne com $set nos campos permitidos (name, description, theme, language, customCss, sfw), validar board existe | Dev | — | true | `.hermes/skills/jschan-forum-manager/scripts/update.sh` |
| T008 | Script delete: find board + contar posts, pedir --force, cascata: deleteMany posts, deleteOne board, remove ownedBoards, limpar Modlogs/Bans/Filters/Stats/CustomPages, reportar total posts deletados | Dev | — | true | `.hermes/skills/jschan-forum-manager/scripts/delete.sh` |
| T009 | SKILL.md: documentar CLI, parâmetros (--mongo-url, --db-name), subcomandos, exemplos, edge cases, pitfalls | Dev | T004,T005,T006,T007,T008 | — | `.hermes/skills/jschan-forum-manager/SKILL.md` |

## Fase 3: Smoke Tests + Wiki Integration

| ID | Descrição | Papel | Deps | ∥ | Arquivos |
|---|---|---|---|---|---|
| T010 | Smoke create + list + get: criar board "testboard", listar todos (verificar aparece), get por URI (verificar campos) | QA | T004,T005,T006 | true | — |
| T011 | Smoke update: editar name+description+theme do "testboard", get novamente e verificar mudanças | QA | T007 | true | — |
| T012 | Smoke delete: deletar "testboard" com --force, verificar que get retorna null, verificar mensagem com contagem de posts | QA | T008 | true | — |
| T013 | Smoke edge cases: criar board com URI duplicada (erro), URI reservada "captcha" (erro), get board inexistente (erro 404), criar sem name (erro validação) | QA | T004 | true | — |
| T014 | Atualizar wiki cross-links: adicionar jschan em `wiki/tools/index.md` e `wiki/index.md` com links para as 3 páginas | Dev | T001,T002,T003 | true | `wiki/tools/index.md`, `wiki/index.md` |
| T015 | Reindexar wiki com `hermes wiki index --full` para incluir as 3 novas páginas no índice | Dev | T014 | — | — |

## Validação do DAG

✅ Sem ciclos. 15 tasks, 13 paralelizáveis (87%), 0 conflitos de arquivo.
Fase 1: 3 tasks, todas ∥. Fase 2: 5 scripts ∥ + 1 SKILL.md sequencial. Fase 3: 5 tests ∥ + 1 reindex sequencial.
