---
feature_id: "004"
plan_for: "jschan Forum Manager"
spec: "specs/features/004-jschan-forum-manager/spec.md"
created: "2026-06-20"
author: phm-aguiar
stack: "mongosh (MongoDB Shell), Bash, jschan MongoDB schema"
depends_on: ~
---

# Plano Arquitetural — jschan Forum Manager

## Metadados

| Campo | Valor |
|---|---|
| **Stack** | `mongosh` (MongoDB Shell 6.0+), Bash, jschan MongoDB schema |
| **Feature fonte** | `specs/features/004-jschan-forum-manager/spec.md` |
| **Escopo (1 frase)** | Wiki documentação + skill Hermes para CRUD de boards jschan via mongosh direto |
| **Dependência** | Nenhuma — opera sobre MongoDB externo, não depende de features anteriores |

## Contratos e Fronteiras

### Entrada

| Artefato | Formato | Fonte |
|---|---|---|
| MongoDB connection string | `mongodb://user:pass@host:port/db` | Parâmetro `--mongo-url` ou env `MONGO_URL` |
| Database name | string (default: `jschan`) | Parâmetro `--db-name` ou env `MONGO_DB` |
| Operação | `create`, `list`, `get`, `update`, `delete` | Subcomando CLI |
| Board data | name, uri, description, owner, tags | Argumentos CLI ou JSON stdin |

### Saída

| Artefato | Formato | Destino |
|---|---|---|
| Board criado | JSON `{uri, name, owner, status: "created"}` | stdout |
| Lista de boards | JSON array `[{uri, name, owner, sequence_value}]` | stdout |
| Board atualizado | JSON `{uri, changed_fields: [...]}` | stdout |
| Board deletado | JSON `{uri, status: "deleted", posts_deleted: N}` | stdout |
| Erro | JSON `{error: "mensagem", code: "DUPLICATE_URI"}` | stderr + exit code ≠ 0 |

### Schema MongoDB (coleção `Boards`)

```
{
  _id: String,              // uri do board (lowercase)
  owner: String,            // username do dono
  tags: [String],           // tags do board
  banners: [Object],        // banners (vazio no create)
  sequence_value: Number,   // contador de posts (inicia 1)
  pph: Number,              // posts por hora (0 inicial)
  ppd: Number,              // posts por dia (0 inicial)
  ips: Number,              // IPs únicos (0 inicial)
  lastPostTimestamp: null,  // timestamp último post
  webring: false,           // participa do webring
  staff: {                  // staff do board
    "<username>": {
      permissions: Binary,  // bitmap de permissões
      addedDate: Date
    }
  },
  flags: {},                // flags customizadas
  assets: [],               // assets do board
  settings: {
    name: String,
    description: String,
    language: String,       // ex: "en-GB", "pt-BR"
    theme: String,          // ex: "yotsuba", "tomorrow"
    codeTheme: String,
    customCss: String,
    announcement: { raw: String, markdown: String },
    sfw: Boolean,
    lockMode: Number,
    captchaMode: Number,
    ...                     // demais defaults do template.js
  }
}
```

### Comandos da skill

```
hermes skill run jschan-forum-manager create \
  --mongo-url "mongodb://..." --db-name jschan \
  --name "Meu Forum" --uri "meuforum" --owner "admin" \
  --description "Descrição" --tags "tag1,tag2"

hermes skill run jschan-forum-manager list \
  --mongo-url "mongodb://..." --db-name jschan

hermes skill run jschan-forum-manager get \
  --mongo-url "mongodb://..." --db-name jschan \
  --uri "meuforum"

hermes skill run jschan-forum-manager update \
  --mongo-url "mongodb://..." --db-name jschan \
  --uri "meuforum" --name "Novo Nome" --theme "tomorrow"

hermes skill run jschan-forum-manager delete \
  --mongo-url "mongodb://..." --db-name jschan \
  --uri "meuforum" --force
```

## ADRs

### ADR-001: mongosh direto em vez de HTTP API

**Decisão:** Usar `mongosh --eval` para operações CRUD diretamente no MongoDB, em vez da API HTTP do jschan (`POST /forms/create`, etc).

**Justificativa:** A API HTTP requer (a) sessão autenticada com cookie, (b) bypass de captcha (`NO_CAPTCHA=1` em dev), (c) jschan estar rodando. O `mongosh` direto elimina todas essas dependências — funciona com jschan parado, sem autenticação web, e é idempotente. O jschan já usa MongoDB como source of truth; operar direto no banco é seguro desde que o schema seja respeitado.

**Alternativa rejeitada:** HTTP API do jschan. Rejeitada porque (a) requer jschan rodando com `NO_CAPTCHA=1` (só dev), (b) autenticação com cookie efêmero, (c) não funciona em cold start, (d) adiciona latência de rede extra.

### ADR-002: Shell scripts Bash + mongosh em vez de Python/Node.js

**Decisão:** Implementar a skill como scripts Bash que chamam `mongosh --eval`, empacotados como skill Hermes com `scripts/` e templates.

**Justificativa:** (a) `mongosh` é a ferramenta canônica MongoDB — zero dependências além do binário, (b) Bash é nativo em qualquer Linux, (c) scripts são diretos e auditáveis (sem camadas de abstração), (d) Hermes executa shell nativamente via `terminal()`. Python exigiria `pymongo` como dependência extra; Node.js exigiria `mongodb` driver. Ambos adicionam complexidade desnecessária para operações que são essencialmente `db.collection.findOne()` / `insertOne()` / `updateOne()` / `deleteOne()`.

**Alternativa rejeitada:** Python com `pymongo`. Rejeitado porque (a) adiciona dependência `pip install pymongo`, (b) mais código boilerplate para mesma operação, (c) `mongosh --eval` já resolve com 1 linha.

### ADR-003: Delete em cascata completa

**Decisão:** O comando `delete` remove o board E todos os dados relacionados: posts (com arquivos), bans, modlogs, filters, stats, custom pages, e diretórios de upload. É uma operação atômica do ponto de vista do operador.

**Justificativa:** O model `deleteboard.js` do jschan já implementa cascata completa. A skill replica essa lógica: (a) deleta posts e decrementa contadores de arquivos, (b) remove board dos `ownedBoards` do owner e `staffBoards` dos staff, (c) limpa `Modlogs`, `Bans`, `Filters`, `Stats`, `CustomPages` do board, (d) remove diretórios `html/`, `json/`, `banner/`, `flag/`, `asset/` do board. A confirmação `--force` é obrigatória e o comando reporta quantos posts serão perdidos antes de executar.

**Alternativa rejeitada:** Soft-delete (flag `deleted: true`). Rejeitado porque (a) jschan não tem suporte nativo a soft-delete, (b) boards "deletados" ainda ocupariam URIs e recursos, (c) complexidade adicional de filtrar boards deletados em queries, (d) reconstrução de estado é arriscada (dados ficam stale).

### ADR-004: Conexão parametrizada (--mongo-url + --db-name), não hardcoded

**Decisão:** A skill aceita `--mongo-url` (connection string completa) e `--db-name` (nome do database, default `jschan`) como parâmetros. Também lê das env vars `MONGO_URL` e `MONGO_DB`.

**Justificativa:** Torna a skill portável para qualquer instância jschan: Docker Compose local, servidor remoto, staging, produção. Hardcoding `mongodb://localhost:27017/jschan` travaria a skill no ambiente do desenvolvedor. Env vars permitem uso em CI/CD e cron jobs sem expor credenciais na linha de comando.

**Alternativa rejeitada:** Hardcoded para Docker Compose local. Rejeitado porque a decisão de design na fase brainstorm foi "skill genérica".

## Auditoria de Constituição

> Nota: O repositório não possui `constitution.md`. A auditoria usa as constraints do `AGENTS.md`.

| Regra | Status | Evidência |
|---|---|---|
| **Hermes nativo — sem APIs externas** | ✅ PASS | mongosh é ferramenta local; zero APIs cloud |
| **Nunca inferir — ambiguidade = clarify()** | ✅ PASS | Edge cases documentados (URI duplicada, MongoDB offline, board não encontrado) |
| **Prefere ferramentas locais** | ✅ PASS | mongosh + bash, sem dependências npm/pip adicionais |
| **Vault wiki atualizado após feature** | ✅ PLAN | 3 páginas wiki documentadas no spec (overview, installation, operations) |
| **Spec aprovado antes de implementar** | ✅ PASS | `spec.md` com `Aprovado: true` |
| **Git author = phm-aguiar** | ✅ PLAN | Metadados YAML com author declarado |
| **Skills em `.hermes/skills/`** | ✅ PLAN | Skill será criada em `.hermes/skills/jschan-forum-manager/` |
