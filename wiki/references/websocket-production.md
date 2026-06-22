---
title: "WebSocket Production — Ping/Pong, Reconnect, Scaling & Rate Limiting"
tags: [websocket, production, scaling, pingpong, reconnect, rate-limiting, security]
created: 2026-06-21
rag_score: 0.5
category: references
summary: Padrões de produção para WebSocket no 42 Chat — keepalive com ping/pong, estratégias de reconexão client-side, scaling multi-instância via Redis pub/sub, persistência de mensagens com soft delete e cursor pagination, rate limiting e hardening de segurança.
provenance:
  extracted: 0.95
  inferred: 0.05
  ambiguous: 0.00
---

# WebSocket Production — Ping/Pong, Reconnect, Scaling & Rate Limiting

Referência de padrões de produção para a camada WebSocket do 42 Chat. Baseado no código real em `internal/ws/handler.go`, `internal/ws/hub.go` e `internal/db/queries.go`.

---

## Constants Reference

Tabela consolidada de todas as constantes do subsistema WebSocket (`internal/ws/handler.go:16-25`):

| Constante | Valor | Local | Propósito |
|---|---|---|---|
| `writeWait` | `10s` | `handler.go:18` | Timeout máximo para escrever **uma** mensagem no WebSocket. Se o client não conseguir receber em 10s, a conexão é considerada morta. |
| `pongWait` | `60s` | `handler.go:20` | Tempo máximo que o servidor aguarda um pong do client. Se expirar sem pong, o `ReadMessage()` retorna erro e a conexão é fechada. |
| `pingPeriod` | `30s` | `handler.go:22` | Intervalo de envio de ping frames do servidor para o client. **Deve ser menor que `pongWait`** para que o client tenha tempo de responder antes do timeout. Fórmula: `pingPeriod = pongWait / 2` (30s = 60s / 2). |
| `maxMessageSize` | `6144` (6 KB) | `handler.go:24` | Limite máximo de bytes que o `ReadMessage()` aceita em uma única frame. ~5 KB para conteúdo + overhead de JSON/websocket framing. |
| `Send` buffer | `256` | `handler.go:81` | Tamanho do canal de saída por client. Mensagens que excedem o buffer são descartadas com log (backpressure). |
| `ReadBufferSize` | `1024` | `handler.go:28` | Buffer de leitura do upgrader (gorilla/websocket). |
| `WriteBufferSize` | `1024` | `handler.go:29` | Buffer de escrita do upgrader (gorilla/websocket). |
| debounce | `2s` | `hub.go:141` | Debounce para broadcast de `user_stats_changed` — múltiplas mudanças no mesmo user em 2s geram um único broadcast. |

---

## Ping/Pong Keepalive

### Como funciona o protocolo

O protocolo de keepalive do 42 Chat usa o mecanismo nativo de **ping/pong frames** do RFC 6455 (WebSocket). São frames de controle no nível do protocolo — não são mensagens de aplicação, não trafegam como JSON e são tratados automaticamente pelo gorilla/websocket.

```
writePump (goroutine)                    readPump (goroutine)
      │                                        │
      │  ping frame ──────────────────────────>│
      │  (a cada 30s)                          │ pongHandler renova
      │                                        │ deadline +60s
      │  <────────────────────────── pong frame│
      │                                        │
      │  Se pong não chegar em 60s:            │
      │  ReadMessage() retorna erro            │
      │  → readPump encerra                    │
      │  → Disconnect + conn.Close()           │
```

### Ciclo de vida detalhado

**1. Inicialização (`readPump`) — `handler.go:93-104`**

```go
func (h *Handler) readPump(client *Client, conn *websocket.Conn) {
    defer func() {
        h.hub.Disconnect(client)  // Remove do Hub, fecha Send chan
        conn.Close()              // Fecha conexão TCP
    }()

    conn.SetReadLimit(maxMessageSize)             // 6144 bytes
    conn.SetReadDeadline(time.Now().Add(pongWait)) // Timeout inicial: 60s
    conn.SetPongHandler(func(string) error {
        conn.SetReadDeadline(time.Now().Add(pongWait)) // Renova +60s
        return nil
    })
    // ... loop de leitura
}
```

**2. Envio de ping (`writePump`) — `handler.go:157-186`**

```go
func (h *Handler) writePump(client *Client, conn *websocket.Conn) {
    ticker := time.NewTicker(pingPeriod) // 30s
    defer func() {
        ticker.Stop()
        conn.Close()
    }()

    for {
        select {
        case message, ok := <-client.Send:
            // Mensagem de broadcast — writeWait = 10s
            conn.SetWriteDeadline(time.Now().Add(writeWait))
            conn.WriteMessage(websocket.TextMessage, message)

        case <-ticker.C:
            // Ping periódico — writeWait = 10s
            conn.SetWriteDeadline(time.Now().Add(writeWait))
            conn.WriteMessage(websocket.PingMessage, nil)
        }
    }
}
```

**3. Timeout e desconexão**

Quando o client não responde ao ping com pong dentro de `pongWait` (60s), o `ReadMessage()` retorna erro. O defer do `readPump` executa:

1. `hub.Disconnect(client)` — remove do mapa de clients, fecha `client.Send`, broadcast "leave"
2. `conn.Close()` — fecha a conexão TCP

O `writePump` detecta o canal fechado (`!ok` no `case message`) e encerra.

### Por que o design funciona

- **Ping/Pong são nativos do protocolo** — o browser responde automaticamente, sem código JavaScript extra
- **`pingPeriod` < `pongWait`** — o client sempre tem ~30s de margem para responder (60s timeout - 30s intervalo = 30s de folga)
- **Deadline renovado no pong handler** — cada pong reseta o relógio, mantendo a conexão viva indefinidamente enquanto o client responder
- **WriteWait separado** — mesmo que o ping falhe, o timeout de escrita é curto (10s), evitando goroutines zumbis
- **Sem mensagens "ping" na aplicação** — zero tráfego JSON para keepalive, apenas frames de controle binários

### O que NÃO está implementado

- **Heartbeat no client** — o servidor não espera pings do client, apenas envia e espera pongs. Se o client quiser detectar conexão morta, precisa implementar seu próprio timeout de inatividade.
- **Reaproveitamento de conexão** — quando a conexão cai, não há tentativa de reconexão no servidor. A responsabilidade é do client (ver seção Reconnection).

---

## Reconnection

### Status atual

O backend **não implementa lógica de reconexão** — quando uma conexão WebSocket fecha (timeout, erro de rede, navegador fechado), o `readPump`/`writePump` simplesmente encerram e o client é removido do Hub. A reconexão é responsabilidade exclusiva do client.

No entanto, o código foi desenhado para suportar reconexão limpa: o `Client` é stateless em relação ao Hub (apenas `UserID` e `Login` dos claims JWT), então um novo `Connect()` recria o estado completo sem conflitos.

### Padrão recomendado: Exponential Backoff + Jitter

```
                 Tentativa 1: imediata
                      │
                 ┌────▼────┐
                 │ Conectou?│── sim ──> WS aberto
                 └────┬────┘
                      │ não
                 ┌────▼─────────────────────┐
                 │ Espera min(2ⁿ × base, max)│
                 │ + jitter aleatório        │
                 │ n = 1,2,3,...             │
                 └──────────────────────────┘
```

**Pseudocódigo JavaScript (client-side)**:

```javascript
class ChatSocket {
    constructor(url, token) {
        this.url = url;
        this.token = token;
        this.retries = 0;
        this.maxRetries = 10;
        this.baseDelay = 1000;  // 1s
        this.maxDelay = 30000;  // 30s
    }

    connect() {
        this.ws = new WebSocket(`${this.url}?token=${this.token}`);

        this.ws.onclose = (event) => {
            if (!event.wasClean && this.retries < this.maxRetries) {
                const delay = Math.min(
                    this.baseDelay * Math.pow(2, this.retries),
                    this.maxDelay
                );
                const jitter = delay * (0.5 + Math.random() * 0.5); // 50%-100% do delay
                this.retries++;
                console.log(`[ws] reconnect #${this.retries} em ${Math.round(jitter)}ms`);
                setTimeout(() => this.connect(), jitter);
            }
        };

        this.ws.onopen = () => {
            this.retries = 0; // Reset no sucesso
        };
    }
}
```

### Estratégia de Token Refresh

O JWT tem expiração de **12 horas**. Para sessões longas, o client deve:

1. Armazenar o JWT em `localStorage` ou cookie HttpOnly
2. Antes de cada tentativa de reconexão, verificar se o token ainda é válido (decode JWT client-side)
3. Se expirou (ou expira em < 5 min), redirecionar para o fluxo OAuth2 (`/api/auth/42`)
4. Por simplicidade, o 42 Chat **não tem endpoint de refresh token** — quando expira, re-autentica

**Pseudocódigo**:

```javascript
function isTokenExpired(token) {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now() + 5 * 60 * 1000; // 5 min de margem
}

async function getOrRefreshToken() {
    let token = localStorage.getItem('jwt');
    if (!token || isTokenExpired(token)) {
        window.location.href = '/api/auth/42'; // Re-autentica
        return null;
    }
    return token;
}
```

---

## Scaling Multi-Instance

### Desafio: Broadcast Local vs Multi-Instance

O Hub atual (`internal/ws/hub.go`) mantém os clients em um mapa em memória:

```go
type Hub struct {
    mu      sync.RWMutex
    clients map[*Client]bool  // Em memória — apenas este processo
    // ...
}
```

Quando há **múltiplas instâncias do servidor** (ex: 3 pods Kubernetes), um `Broadcast()` na instância A só alcança os clients conectados a A. Clients conectados às instâncias B e C não recebem a mensagem.

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Instância A │       │  Instância B │       │  Instância C │
│  Hub.local   │       │  Hub.local   │       │  Hub.local   │
│  [C1, C2]    │       │  [C3]        │       │  [C4, C5]    │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Redis Pub/Sub   │
                    │   channel: "ws"   │
                    └───────────────────┘
```

### Solução: Redis Pub/Sub + PostgreSQL

**Arquitetura proposta** (padrão, não implementado no código atual):

```
                      PostgreSQL
                   (source of truth)
                    ┌───────────┐
                    │ messages  │
                    │ users     │
                    └─────┬─────┘
                          │ INSERT/SELECT
          ┌───────────────┼───────────────┐
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │ Instance A│   │ Instance B│   │ Instance C│
    │ Hub       │   │ Hub       │   │ Hub       │
    │ readPump  │   │ readPump  │   │ readPump  │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
          │    SUBSCRIBE "chat:messages"   │
          └───────────────┼───────────────┘
                          │
                   ┌──────▼──────┐
                   │    Redis    │
                   │  Pub/Sub    │
                   └─────────────┘
```

**Fluxo de mensagem cross-instance**:

1. Client C1 (conectado à Instância A) envia mensagem
2. `readPump` da Instância A:
   - **Persiste no PostgreSQL** — `queries.InsertMessage()` → source of truth
   - **Publica no Redis** — `PUBLISH chat:messages <msg_json>`
   - **Broadcast local** — `hub.Broadcast()` → clients da Instância A
3. Instâncias B e C, que assinam `chat:messages`, recebem a mensagem do Redis
4. Cada instância faz **broadcast local** para seus próprios clients

**Pseudocódigo da integração**:

```go
type Hub struct {
    mu      sync.RWMutex
    clients map[*Client]bool
    redis   *redis.Client          // Adicionado
    queries *db.Queries
}

func (h *Hub) StartRedisSubscriber() {
    pubsub := h.redis.Subscribe(ctx, "chat:messages")
    defer pubsub.Close()

    for msg := range pubsub.Channel() {
        var wsMsg model.WSMessage
        json.Unmarshal([]byte(msg.Payload), &wsMsg)
        h.Broadcast(&wsMsg) // Broadcast apenas para clients locais
    }
}
```

**Por que PostgreSQL é source of truth e Redis é apenas transporte:**

| Responsabilidade | PostgreSQL | Redis Pub/Sub |
|---|---|---|
| Persistência | ✅ Durabilidade, ACID | ❌ Fire-and-forget |
| Histórico | ✅ `SELECT * FROM messages` | ❌ Sem histórico |
| Soft delete | ✅ `UPDATE deleted_at` | ❌ |
| Mensagens em trânsito | — | ✅ Sub-milissegundo, at-most-once |
| Broadcast multi-instance | ❌ | ✅ |

**Cuidados**:

- Se o Redis cair, broadcasts cross-instance são perdidos, mas mensagens já estão persistidas no PostgreSQL
- Clients podem perder mensagens em trânsito durante failover — o client deve buscar `/api/messages` no reconnect para preencher o gap
- Cada instância deve usar um Redis connection pool separado

---

## Message Persistence

### Soft Delete

Mensagens nunca são removidas fisicamente do banco. O campo `deleted_at` marca a exclusão lógica (`internal/db/queries.go:120-125`):

```go
func (q *Queries) SoftDeleteMessage(id string) error {
    const query = `UPDATE messages SET deleted_at = NOW() WHERE id = $1`
    _, err := q.db.Exec(query, id)
    return err
}
```

Todas as queries de leitura filtram `WHERE m.deleted_at IS NULL`:

```go
// queries.go:85
WHERE m.deleted_at IS NULL
```

**Modelo** (`internal/model/message.go:8-17`):

```go
type Message struct {
    ID        string     `json:"id"`
    UserID    int        `json:"user_id"`
    Login     string     `json:"login,omitempty"`
    ImageURL  string     `json:"image_url,omitempty"`
    Content   string     `json:"content"`
    CreatedAt time.Time  `json:"created_at"`
    DeletedAt *time.Time `json:"deleted_at,omitempty"` // nil = ativa
}
```

### Cursor Pagination

O endpoint de mensagens históricas usa **cursor pagination** baseada em `created_at` — sem OFFSET, que degrada em tabelas grandes (`internal/db/queries.go:71-118`):

```go
func (q *Queries) SelectRecentMessages(before time.Time, limit int) ([]model.Message, error) {
    if before.IsZero() {
        // Primeira página: mensagens mais recentes
        query = `
            SELECT m.id, m.user_id, u.login, u.image_url, m.content, m.created_at
            FROM messages m
            JOIN users u ON u.id = m.user_id
            WHERE m.deleted_at IS NULL
            ORDER BY m.created_at DESC
            LIMIT $1
        `
    } else {
        // Próximas páginas: mensagens antes do cursor
        query = `
            SELECT ... FROM messages m JOIN users u ON u.id = m.user_id
            WHERE m.deleted_at IS NULL AND m.created_at < $1
            ORDER BY m.created_at DESC
            LIMIT $2
        `
    }
}
```

**Vantagens do cursor sobre OFFSET**:

- **Estável** — novas mensagens inseridas não deslocam os resultados (sem "página pulando")
- **Index-friendly** — `WHERE created_at < $1 ORDER BY created_at DESC` usa índice B-tree diretamente
- **Performático** — complexidade O(log n) vs O(n) do OFFSET em tabelas grandes

**Fluxo no client**:

```javascript
// Primeira carga
const response = await fetch('/api/messages?limit=50');
const messages = await response.json();

// Scroll infinito — usar o created_at da mensagem mais antiga como cursor
const oldest = messages[messages.length - 1].created_at;
const nextPage = await fetch(`/api/messages?before=${oldest}&limit=50`);
```

### Validação de tamanho

O conteúdo da mensagem tem **duas camadas de validação**:

| Camada | Limite | Onde | Comportamento |
|---|---|---|---|
| WebSocket frame | `maxMessageSize = 6144` | `readPump` (`conn.SetReadLimit`) | Descarta frame, fecha conexão |
| Conteúdo da mensagem | `5000` caracteres | `readPump` (`len(inbound.Content) > 5000`) | Descarta mensagem, conexão continua |
| Banco de dados | `CHECK (length(content) <= 5000)` | PostgreSQL | Rejeita INSERT |

```go
// handler.go:99
conn.SetReadLimit(maxMessageSize) // 6144 bytes

// handler.go:128-130
if len(inbound.Content) > 5000 {
    continue // Descarta silenciosamente
}
```

---

## Rate Limiting por Client

### Rate limiting implícito (atual)

O 42 Chat não implementa rate limiting explícito (token bucket, sliding window), mas possui **backpressure implícito**:

**1. Limite de tamanho de mensagem (`readPump`)**

```go
conn.SetReadLimit(maxMessageSize)  // 6144 bytes por frame
// ...
if len(inbound.Content) > 5000 {
    continue  // Descarta mensagens com conteúdo > 5000 chars
}
```

Mensagens que excedem o limite são descartadas silenciosamente.

**2. Buffer de saída com backpressure (`writePump`)**

```go
client := &Client{
    Send: make(chan []byte, 256), // Buffer de 256 mensagens
}
```

No `Broadcast()`:

```go
for client := range h.clients {
    select {
    case client.Send <- data:
        // Sucesso
    default:
        // Buffer cheio — descarta mensagem para este client
        log.Printf("[ws] descartando msg para %s (buffer cheio)", client.Login)
    }
}
```

Se um client não consegue consumir mensagens rápido o suficiente, mensagens são descartadas **apenas para aquele client** — outros clients não são afetados.

**3. Write timeout**

```go
conn.SetWriteDeadline(time.Now().Add(writeWait)) // 10s por mensagem
```

Se o client travar por >10s, a escrita falha e a goroutine `writePump` encerra, fechando a conexão.

### Rate limiting explícito (recomendado para produção)

Para hardening em produção, implementar um **token bucket por client** no `readPump`:

```go
type Client struct {
    UserID    int
    Login     string
    Send      chan []byte
    Hub       *Hub
    limiter   *rate.Limiter          // golang.org/x/time/rate
}

// No readPump, antes de processar a mensagem:
if !client.limiter.Allow() {
    // Rate limit excedido — descarta ou envia warning
    continue
}
```

**Limites sugeridos**:

| Métrica | Limite | Justificativa |
|---|---|---|
| Mensagens por segundo | 5 msg/s | Chat humano — digitação normal ~1-2 msg/s |
| Burst | 10 | Permite rajada curta (colar texto, spam rápido) |
| Conexões por IP | 10 | Previne um único IP de exaurir file descriptors |
| Conexões por user | 3 | Um user pode ter múltiplas abas, mas não dezenas |

---

## CheckOrigin — Segurança do Upgrade

### Estado atual (MVP/Dev)

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        return true // MVP: aceita qualquer origem (dev local)
    },
}
```

**Risco**: qualquer site malicioso pode abrir WebSocket para o servidor e receber mensagens do chat (Cross-Site WebSocket Hijacking — CSWSH).

O WebSocket **não** é protegido por CORS — `Access-Control-Allow-Origin` não se aplica ao upgrade WebSocket. A única proteção é o `CheckOrigin`.

### Hardening para produção

```go
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin: func(r *http.Request) bool {
        origin := r.Header.Get("Origin")
        if origin == "" {
            // Clientes não-browser (curl, wscat) não enviam Origin
            return true
        }
        // Whitelist de origens permitidas
        switch origin {
        case "https://meu-chat.exemplo.com",
             "https://app.exemplo.com":
            return true
        default:
            log.Printf("[ws] origem rejeitada: %s", origin)
            return false
        }
    },
}
```

**Alternativa com env var**:

```go
var allowedOrigins = strings.Split(os.Getenv("WS_ALLOWED_ORIGINS"), ",")

CheckOrigin: func(r *http.Request) bool {
    origin := r.Header.Get("Origin")
    if origin == "" {
        return true // non-browser clients
    }
    for _, allowed := range allowedOrigins {
        if origin == allowed {
            return true
        }
    }
    return false
}
```

### Verificação adicional: token no upgrade

Mesmo que um atacante burle `CheckOrigin` (ex: forjando header Origin), a validação JWT no `ServeHTTP` impede conexões não autenticadas:

```go
// handler.go:64-68
claims, err := h.jwtManager.ValidateToken(tokenStr)
if err != nil {
    http.Error(w, `{"error":"invalid token"}`, http.StatusUnauthorized)
    return
}
```

**Defesa em profundidade**:

| Camada | Proteção |
|---|---|
| `CheckOrigin` | Previne CSWSH — sites maliciosos não conseguem abrir WebSocket |
| JWT Validation | Previne conexões sem token válido |
| `Sec-WebSocket-Protocol` | Via de token alternativa que não aparece em logs (opcional) |

---

## Resumo de Boas Práticas

### O que já está implementado ✅

- [x] **Ping/Pong keepalive** — `pingPeriod=30s`, `pongWait=60s`, `writeWait=10s`
- [x] **Soft delete** — `deleted_at` no PostgreSQL, queries filtram `WHERE deleted_at IS NULL`
- [x] **Cursor pagination** — `SELECT ... WHERE created_at < $1 ORDER BY created_at DESC LIMIT $2`
- [x] **Backpressure** — buffer de 256 mensagens por client, descarte com log
- [x] **Validação de tamanho** — duas camadas (frame + conteúdo + CHECK constraint)
- [x] **JWT no upgrade** — validação antes do `Upgrade()`
- [x] **Graceful shutdown** — `Hub.Shutdown()` envia mensagem "shutdown" para todos os clients

### O que precisa de hardening para produção ⚠️

- [ ] **CheckOrigin restritivo** — substituir `return true` por whitelist de origens
- [ ] **Rate limiting explícito** — token bucket por client (5 msg/s, burst 10)
- [ ] **Redis Pub/Sub** — para broadcast cross-instance em multi-pod
- [ ] **Reconnection state** — client-side com exponential backoff + jitter
- [ ] **Métricas** — Prometheus: `ws_connections_active`, `ws_messages_total`, `ws_errors_total`
- [ ] **TLS** — `wss://` em produção (terminação no load balancer ou no servidor)
- [ ] **Log sanitization** — tokens não devem aparecer em logs (query param `?token=` é problemático)
- [ ] **Max connections** — limite global de conexões para evitar exaustão de file descriptors

---

## Dependências

```go
// go.mod
github.com/gorilla/websocket v1.5.3  // WebSocket upgrade, read/write pumps, ping/pong
github.com/golang-jwt/jwt/v5 v5.3.1  // JWT validation no upgrade
github.com/lib/pq v1.10.9            // PostgreSQL driver (persistência de mensagens)
```
