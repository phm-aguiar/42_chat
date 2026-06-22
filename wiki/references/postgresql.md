---
title: "PostgreSQL no 42 Chat"
tags: [postgresql, go, database]
created: 2026-06-21
rag_score: 0.5
category: references
summary: Padrões de uso do PostgreSQL no 42 Chat Core — connection pool, migrations, queries parametrizadas, schema design e escolha lib/pq.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# PostgreSQL no 42 Chat Core

Referência prática de como o PostgreSQL é usado no projeto **42 Chat Core** — do pool de conexões ao schema, passando por migrations e patterns de queries.

---

## Connection Pool

A struct `Postgres` (`internal/db/postgres.go`) encapsula um `*sql.DB` — o pool de conexões nativo da stdlib.

### Inicialização

```go
db, err := sql.Open("postgres", databaseURL)
```

O driver é registrado via `import _ "github.com/lib/pq"` (blank import no `postgres.go`).

### Parâmetros de pool

Ajustados para **t2.micro (1 GB RAM)** com meta de 300 conexões simultâneas:

| Parâmetro               | Valor         | Motivação                                      |
|-------------------------|---------------|------------------------------------------------|
| `SetMaxOpenConns`       | 25            | Limita conexões ativas para não estourar RAM   |
| `SetMaxIdleConns`       | 10            | Mantém um pool de reuso sem desperdiçar memória|
| `SetConnMaxLifetime`    | 30 minutos    | Recicla conexões periodicamente                |
| `SetConnMaxIdleTime`    | 5 minutos     | Fecha conexões ociosas após esse tempo         |

### Health check

```go
if err := db.Ping(); err != nil {
    return nil, fmt.Errorf("db.Ping: %w", err)
}
```

`Ping()` é chamado na criação para validar conectividade antes de retornar o pool — se falhar, o servidor não sobe.

### Métricas de pool

```go
func (p *Postgres) Stats() sql.DBStats {
    return p.DB.Stats()
}
```

Expõe `sql.DBStats` (open, idle, in-use, wait duration, etc.) para o endpoint `/metrics`.

---

## Migrations

As migrations vivem em `internal/db/migrations/` e são montadas como volume no PostgreSQL via `docker-compose.yml`:

```yaml
volumes:
  - ./internal/db/migrations:/docker-entrypoint-initdb.d:ro,z
```

O entrypoint oficial do PostgreSQL (`postgres:16-alpine`) executa arquivos `.sql` desse diretório em ordem alfabética na primeira inicialização.

### Schema: 001_init.sql

#### Tabela `users`

```sql
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL          PRIMARY KEY,
    login       VARCHAR(50)     NOT NULL UNIQUE,
    image_url   TEXT,
    current_host VARCHAR(20),
    level       NUMERIC(4,2)    NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

- `id` é **SERIAL** (auto-increment), mas o valor real vem do ID da API 42 — o `UpsertUser` insere com o ID fornecido.
- `login` tem `UNIQUE` — usado como chave alternativa de lookup (`SelectUserByLogin`).
- `level` é `NUMERIC(4,2)` — precisão de centésimos (ex: 12.34).

#### Tabela `messages`

```sql
CREATE TABLE IF NOT EXISTS messages (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INT             NOT NULL,
    content     TEXT            NOT NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ,

    CONSTRAINT fk_messages_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,

    CONSTRAINT chk_content_length
        CHECK (char_length(content) <= 5000)
);
```

- `id` é **UUID v4** gerado pelo PostgreSQL (`gen_random_uuid()`) — não pelo Go.
- `user_id` tem `ON DELETE CASCADE` — se um usuário for deletado, suas mensagens somem também.
- `content` tem `CHECK (char_length(content) <= 5000)` — validação no banco, não só no código.
- `deleted_at` é `TIMESTAMPTZ` nullable — permite **soft delete**: a mensagem permanece no banco, mas não é retornada nas queries normais.

#### Índices

| Índice                        | Tipo          | Finalidade                                    |
|-------------------------------|---------------|-----------------------------------------------|
| `idx_messages_created_at_desc`| B-tree DESC   | Listagem cronológica reversa (mais novas primeiro) |
| `idx_messages_user_id`        | B-tree        | Lookup rápido por `user_id`                   |
| `idx_messages_active`         | **Partial**   | Indexa só linhas com `deleted_at IS NULL`     |

O `idx_messages_active` é um **índice parcial** — cobre apenas mensagens não-deletadas. Isso reduz o tamanho do índice e acelera a query principal de listagem (`SelectRecentMessages`), que sempre filtra por `WHERE m.deleted_at IS NULL`.

---

## Query Patterns

Todas as queries estão em `internal/db/queries.go`, na struct `Queries`.

### Upsert (INSERT … ON CONFLICT)

```go
const query = `
    INSERT INTO users (id, login, image_url, current_host, level, created_at)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (id) DO UPDATE SET
        login = EXCLUDED.login,
        image_url = EXCLUDED.image_url,
        current_host = EXCLUDED.current_host,
        level = EXCLUDED.level
    RETURNING id
`
q.db.QueryRow(query, u.ID, u.Login, u.ImageURL, u.CurrentHost, u.Level, u.CreatedAt).Scan(&id)
```

- **`ON CONFLICT (id) DO UPDATE`**: Se o usuário já existe (mesmo ID 42), atualiza campos mutáveis (login, foto, host, level).
- **`EXCLUDED`**: Referencia os valores da linha que *seria* inserida — padrão PostgreSQL para upserts limpos.
- **`RETURNING id`**: Retorna o ID após upsert sem precisar de uma segunda query.

### INSERT com RETURNING

```go
INSERT INTO messages (user_id, content, created_at)
VALUES ($1, $2, NOW())
RETURNING id, created_at
```

- `NOW()` é usado no SQL (não `time.Now()` no Go) — o timestamp é gerado pelo servidor PostgreSQL.
- `RETURNING` devolve `id` (UUID) e `created_at` — o Go nunca gera o UUID da mensagem.

### SELECT com JOIN condicional

```go
func (q *Queries) SelectRecentMessages(before time.Time, limit int) ([]model.Message, error) {
```

Dois branches de query:

1. **Sem cursor** (`before.IsZero()`):
   ```sql
   SELECT m.id, m.user_id, u.login, u.image_url, m.content, m.created_at
   FROM messages m
   JOIN users u ON u.id = m.user_id
   WHERE m.deleted_at IS NULL
   ORDER BY m.created_at DESC
   LIMIT $1
   ```

2. **Com cursor** (`before` preenchido):
   ```sql
   -- ...mesmo SELECT...
   WHERE m.deleted_at IS NULL AND m.created_at < $1
   ORDER BY m.created_at DESC
   LIMIT $2
   ```

- **Paginação por cursor**: usa `created_at < $1` em vez de `OFFSET` — mais eficiente e imune a drift de inserções.
- **JOIN com `users`**: enriquece cada mensagem com `login` e `image_url` sem query adicional.
- **Soft delete**: `WHERE deleted_at IS NULL` usa o partial index `idx_messages_active`.

### Soft Delete

```go
const query = `UPDATE messages SET deleted_at = NOW() WHERE id = $1`
_, err := q.db.Exec(query, id)
```

- Apenas define `deleted_at = NOW()` — a linha permanece no banco.
- Nenhuma query do sistema faz `DELETE` físico em `messages`.

### SELECT por chave alternativa

```go
const query = `SELECT id, login, image_url, current_host, level, created_at FROM users WHERE login = $1`
q.db.QueryRow(query, login).Scan(&u.ID, &u.Login, &u.ImageURL, &u.CurrentHost, &u.Level, &u.CreatedAt)
```

Busca por `login` (campo com `UNIQUE`) — útil para lookup sem ter o ID 42.

---

## Schema Design — Decisões

| Decisão                      | Justificativa                                           |
|------------------------------|---------------------------------------------------------|
| UUID gerado no PostgreSQL    | Evita round-trip Go→DB para gerar ID; `gen_random_uuid()` é nativo e performático |
| Soft delete (`deleted_at`)   | Auditoria, undo, e conformidade (nunca se perde dado)   |
| Partial index                | Otimiza a query mais quente do sistema (listar mensagens ativas) |
| `ON DELETE CASCADE`          | Consistência automática users↔messages                  |
| `CHECK` constraint no banco  | Defesa em profundidade — validação dupla Go + PostgreSQL |
| `NUMERIC(4,2)` para level    | Precisão decimal exata, sem surpresas de float          |
| `SERIAL` para `users.id`     | Fallback de auto-increment; valor real sobrescrito pelo upsert |
| `TIMESTAMPTZ` (com timezone) | Consistência entre servidores em fusos diferentes       |

---

## lib/pq vs pgx

O projeto usa **`github.com/lib/pq`** (v1.12.3), não `pgx`.

| Aspecto              | lib/pq                         | pgx                              |
|----------------------|--------------------------------|----------------------------------|
| Interface            | `database/sql` nativa          | API própria + adaptador `database/sql` |
| Performance          | Boa                            | Melhor (protocolo binário)       |
| Features             | Básicas                        | Avançadas (COPY, listen/notify, etc.) |
| Complexidade         | Mínima                         | Maior                            |
| Manutenção           | Modo archive (2024+)           | Ativa                            |

**Escolha**: lib/pq foi escolhida por simplicidade. O projeto não precisa de features avançadas do pgx (sem LISTEN/NOTIFY, sem COPY). O WebSocket gerencia tempo real, não o PostgreSQL.

**Atenção**: lib/pq entrou em modo archive. Para projetos novos, considere `pgx/v5` com `stdlib` adapter se quiser manter `database/sql`.

---

## Pitfalls

### 1. `sql.Open` não conecta
`sql.Open("postgres", url)` apenas valida o driver e a URL — **não abre conexão**. Sempre chame `db.Ping()` depois.

### 2. Pool tuning para hardware específico
`SetMaxOpenConns(25)` é calibrado para **t2.micro (1 GB RAM)**. Em hardware maior, aumente. Em hardware menor, reduza. Conexões PostgreSQL ocupam ~2-10 MB cada no servidor.

### 3. Transações implícitas em migrations
`001_init.sql` usa `BEGIN; … COMMIT;` — todas as operações são atômicas. Se qualquer statement falhar, o schema inteiro é rollback. **Nunca** remova o wrapper de transação.

### 4. Não usar `ON CONFLICT DO NOTHING`
`UpsertUser` usa `DO UPDATE` — sempre queremos os dados mais recentes do OAuth2. `DO NOTHING` ignoraria updates de avatar/login/level.

### 5. Timezone em `TIMESTAMPTZ`
Sempre use `TIMESTAMPTZ` (com timezone), não `TIMESTAMP`. O PostgreSQL armazena sempre em UTC internamente e converte na leitura. Sem timezone, comparações entre servidores em fusos diferentes quebram.

### 6. Migrations executadas só na primeira inicialização
O diretório `docker-entrypoint-initdb.d` só executa scripts quando o volume de dados (`pgdata`) está **vazio**. Para adicionar migrations depois, crie um novo arquivo (ex: `002_xxx.sql`) e recrie o volume (`docker compose down -v`).

### 7. Conexões idle vs memory
`SetConnMaxIdleTime(5 * time.Minute)` é importante em t2.micro: conexões ociosas consomem RAM no servidor PostgreSQL. Sem esse parâmetro, conexões idle podem acumular até `SetMaxIdleConns` e nunca serem liberadas.
