---
title: Observabilidade em Produção — Go + Chi + Datadog
tags: [observability, monitoring, devops, go, datadog, health-check, logging, metrics]
created: 2026-06-21
rag_score: 0.5
---

# Observabilidade em Produção

Guia de padrões de observabilidade para o **42_chat** — aplicação Go com Chi router,
deploy em AWS EC2, stack de monitoramento Datadog.

---

## 1. Health Checks

### 1.1 Endpoint `/api/health`

Endpoint HTTP que responde ao Kubernetes/Docker/ALB e ferramentas externas.

```go
// internal/handler/health.go
package handler

import (
    "context"
    "database/sql"
    "encoding/json"
    "net/http"
    "time"
)

type HealthResponse struct {
    Status    string            `json:"status"`
    Timestamp string            `json:"timestamp"`
    Checks    map[string]string `json:"checks,omitempty"`
}

func HealthHandler(db *sql.DB) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        checks := map[string]string{}

        // Database check
        ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
        defer cancel()
        if err := db.PingContext(ctx); err != nil {
            checks["postgres"] = "unhealthy: " + err.Error()
        } else {
            checks["postgres"] = "healthy"
        }

        resp := HealthResponse{
            Status:    "ok",
            Timestamp: time.Now().UTC().Format(time.RFC3339),
            Checks:    checks,
        }

        // Se algum check falhou, retornar 503
        for _, v := range checks {
            if v != "healthy" {
                resp.Status = "degraded"
                w.Header().Set("Content-Type", "application/json")
                w.WriteHeader(http.StatusServiceUnavailable)
                json.NewEncoder(w).Encode(resp)
                return
            }
        }

        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusOK)
        json.NewEncoder(w).Encode(resp)
    }
}
```

**Registrar no Chi router:**

```go
r.Get("/api/health", handler.HealthHandler(db))
```

### 1.2 Docker Healthcheck

No `Dockerfile` ou `docker-compose.yml`:

```dockerfile
# Dockerfile — healthcheck para o app Go
HEALTHCHECK --interval=15s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1
```

```yaml
# docker-compose.yml — healthcheck para PostgreSQL
services:
  postgres:
    image: postgres:16-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s
```

### 1.3 Readiness vs Liveness

| Tipo       | Endpoint            | O que verifica                        | Falha =         |
| ---------- | ------------------- | ------------------------------------- | --------------- |
| Liveness   | `/api/health`       | App responde, sem deadlock            | Reinicia o pod  |
| Readiness  | `/api/health/ready` | DB + dependências externas respondem  | Remove do ALB   |

```go
// Readiness: verifica tudo, inclusive dependências
r.Get("/api/health/ready", handler.HealthHandler(db))

// Liveness: só confirma que o processo está vivo
r.Get("/api/health/live", func(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)
    w.Write([]byte(`{"status":"alive"}`))
})
```

---

## 2. Logging Estruturado

### 2.1 `log/slog` — Logger Estruturado Nativo (Go 1.21+)

O **`log/slog`** é o logger estruturado oficial da stdlib. Substitui `logrus`, `zap` e outros
para a maioria dos casos. Suporta níveis, atributos estruturados, context propagation e handlers
plugáveis (JSON, texto, Datadog).

### 2.2 Configuração Padrão

```go
// internal/observability/logger.go
package observability

import (
    "log/slog"
    "os"
)

func NewLogger(level string, format string) *slog.Logger {
    var handler slog.Handler

    opts := &slog.HandlerOptions{
        Level: parseLevel(level),
        // Adiciona source file:line em desenvolvimento
        AddSource: os.Getenv("ENV") != "production",
    }

    switch format {
    case "json":
        handler = slog.NewJSONHandler(os.Stdout, opts)
    default:
        handler = slog.NewTextHandler(os.Stdout, opts)
    }

    return slog.New(handler)
}

func parseLevel(level string) slog.Level {
    switch level {
    case "debug":
        return slog.LevelDebug
    case "warn":
        return slog.LevelWarn
    case "error":
        return slog.LevelError
    default:
        return slog.LevelInfo
    }
}
```

### 2.3 Uso no Código

```go
logger := observability.NewLogger("info", "json")

// Info com atributos estruturados
logger.Info("request completed",
    slog.String("method", r.Method),
    slog.String("path", r.URL.Path),
    slog.Int("status", statusCode),
    slog.Duration("latency", latency),
    slog.String("trace_id", traceID),
)

// Erro com stack context
logger.Error("database query failed",
    slog.String("query", "SELECT * FROM messages"),
    slog.String("error", err.Error()),
    slog.Duration("timeout", 2*time.Second),
)

// Debug (suprimido em produção pelo nível Info)
logger.Debug("cache hit",
    slog.String("key", cacheKey),
    slog.Int("ttl_remaining", ttl),
)

// Warn para condições borderline
logger.Warn("connection pool near capacity",
    slog.Int("active", activeConns),
    slog.Int("max", maxConns),
    slog.Int("idle", idleConns),
)
```

### 2.4 Context Propagation com `slog`

```go
// Middleware que injeta logger no context
func LoggerMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            requestID := r.Header.Get("X-Request-ID")
            if requestID == "" {
                requestID = uuid.New().String()
            }

            ctx := context.WithValue(r.Context(), "logger",
                logger.With(
                    slog.String("request_id", requestID),
                    slog.String("method", r.Method),
                    slog.String("path", r.URL.Path),
                ),
            )
            next.ServeHTTP(w, r.WithContext(ctx))
        })
    }
}

// Helper para extrair logger do context
func LoggerFromContext(ctx context.Context) *slog.Logger {
    if logger, ok := ctx.Value("logger").(*slog.Logger); ok {
        return logger
    }
    return slog.Default()
}
```

### 2.5 Níveis e Quando Usar

| Nível  | Uso                                                         |
| ------ | ----------------------------------------------------------- |
| DEBUG  | Detalhes internos: cache hits, parâmetros de query, loops   |
| INFO   | Eventos de negócio: request completado, WebSocket conectado |
| WARN   | Condições anormais recuperáveis: retry, pool quase cheio    |
| ERROR  | Falhas que precisam de atenção: query quebrou, panic, 5xx   |

### 2.6 O Que NÃO Logar

- **Dados sensíveis**: senhas, tokens JWT completos, cookies de sessão
- **PII**: emails, nomes reais, IPs (sem anonimização)
- **Payloads gigantes**: body inteiro de upload. Logar tamanho, não conteúdo.
- **Logs em loop tight**: usar `slog.LogAttrs` com rate-limiting se necessário

---

## 3. Métricas

### 3.1 O Que Medir — Panorama Geral

| Categoria              | Métrica                          | Tipo         | Descrição                                  |
| ---------------------- | -------------------------------- | ------------ | ------------------------------------------ |
| **HTTP**               | `http.requests.total`            | Counter      | Total de requests (por method, path, status) |
| **HTTP**               | `http.request.duration_ms`       | Histogram    | Latência p50, p95, p99                     |
| **HTTP**               | `http.requests.active`           | Gauge        | Requests em voo                            |
| **WebSocket**          | `ws.connections.active`          | Gauge        | Conexões WebSocket abertas                 |
| **WebSocket**          | `ws.connections.total`           | Counter      | Total de conexões estabelecidas            |
| **WebSocket**          | `ws.messages.sent`               | Counter      | Mensagens enviadas via WS                  |
| **WebSocket**          | `ws.messages.received`           | Counter      | Mensagens recebidas via WS                 |
| **PostgreSQL**         | `db.pool.active`                 | Gauge        | Conexões ativas no pool                    |
| **PostgreSQL**         | `db.pool.idle`                   | Gauge        | Conexões idle no pool                      |
| **PostgreSQL**         | `db.pool.wait_duration_ms`       | Histogram    | Tempo de espera por conexão                |
| **PostgreSQL**         | `db.query.duration_ms`           | Histogram    | Duração de queries                         |
| **Erros**              | `errors.total`                   | Counter      | Erros 5xx + panics (por tipo)              |
| **Aplicação**          | `app.memory.bytes`               | Gauge        | Uso de memória do processo                 |
| **Aplicação**          | `app.goroutines`                 | Gauge        | Número de goroutines ativas                |

### 3.2 Exposição de Métricas com `expvar` (stdlib)

Go tem `expvar` nativo — sem dependência externa. O Datadog Agent pode scrape o endpoint.

```go
// internal/observability/metrics.go
package observability

import (
    "expvar"
    "runtime"
    "time"
)

var (
    RequestsTotal     = expvar.NewInt("http.requests.total")
    RequestsActive    = expvar.NewInt("http.requests.active")
    Errors5xx         = expvar.NewInt("errors.5xx")
    WSActiveConns     = expvar.NewInt("ws.connections.active")
    WSTotalConns      = expvar.NewInt("ws.connections.total")
)

func init() {
    // Métricas de runtime
    expvar.Publish("app.goroutines", expvar.Func(func() interface{} {
        return runtime.NumGoroutine()
    }))

    expvar.Publish("app.memory.alloc_bytes", expvar.Func(func() interface{} {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        return m.Alloc
    }))

    // Pool de conexões PostgreSQL
    expvar.Publish("db.pool.active", expvar.Func(func() interface{} {
        return db.Stats().InUse  // db é *sql.DB
    }))

    expvar.Publish("db.pool.idle", expvar.Func(func() interface{} {
        return db.Stats().Idle
    }))
}
```

Para métricas mais sofisticadas (histogramas, percentis), use o **Datadog APM** ou uma biblioteca
como `prometheus/client_golang` com exposição no formato Datadog.

### 3.3 Middleware de Métricas HTTP (Chi)

```go
// internal/middleware/metrics.go
package middleware

import (
    "net/http"
    "time"

    "github.com/go-chi/chi/v5"
    "github.com/go-chi/chi/v5/middleware"
)

func MetricsMiddleware() func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            observability.RequestsActive.Add(1)
            defer observability.RequestsActive.Add(-1)

            // Wrap ResponseWriter para capturar status code
            ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
            next.ServeHTTP(ww, r)

            duration := time.Since(start)
            observability.RequestsTotal.Add(1)

            if ww.Status() >= 500 {
                observability.Errors5xx.Add(1)
            }

            // Log estruturado com métricas inline
            slog.Info("request",
                slog.String("method", r.Method),
                slog.String("path", r.URL.Path),
                slog.Int("status", ww.Status()),
                slog.Duration("latency", duration),
                slog.Int("bytes_written", ww.BytesWritten()),
            )
        })
    }
}
```

### 3.4 WebSocket Metrics

```go
// No handler de upgrade WebSocket
func HandleWebSocket(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }

    observability.WSActiveConns.Add(1)
    observability.WSTotalConns.Add(1)
    defer observability.WSActiveConns.Add(-1)

    // ... loop de leitura/escrita
}
```

---

## 4. Datadog Integration

### 4.1 Agent Setup

Instalação do Datadog Agent na EC2 (Amazon Linux 2023 / Fedora):

```bash
# Instalar o Datadog Agent
DD_API_KEY=<YOUR_API_KEY> DD_SITE="datadoghq.com" \
  bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Configurar APM
sudo tee /etc/datadog-agent/datadog.yaml <<EOF
api_key: <YOUR_API_KEY>
site: datadoghq.com
apm_config:
  enabled: true
logs_enabled: true
process_config:
  process_collection:
    enabled: true
EOF

# Habilitar integração PostgreSQL
sudo tee /etc/datadog-agent/conf.d/postgres.d/conf.yaml <<EOF
init_config:
instances:
  - host: localhost
    port: 5432
    username: datadog
    password: <MONITORING_PASSWORD>
    dbname: 42_chat
    tags:
      - env:production
      - service:42-chat
EOF

sudo systemctl restart datadog-agent
```

### 4.2 APM Tracing para Go

Usar o tracer oficial `gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer`.

```go
// internal/observability/tracer.go
package observability

import (
    "gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

func InitTracer(serviceName, env string) {
    tracer.Start(
        tracer.WithService(serviceName),
        tracer.WithEnv(env),
        tracer.WithLogStartup(false),         // não loga startup info
        tracer.WithAnalyticsRate(1.0),        // 100% de amostragem para APM analytics
        tracer.WithRuntimeMetrics(),           // métricas de runtime Go automáticas
    )
}

func StopTracer() {
    tracer.Stop()
}
```

**Middleware HTTP tracing (Chi wrapper):**

```go
import (
    httptrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/net/http"
    "gopkg.in/DataDog/dd-trace-go.v1/ddtrace/tracer"
)

// No main.go, em vez de http.ListenAndServe
httptrace.WrapHandler(chiRouter, "42-chat", "production")
```

**Tracing em queries PostgreSQL:**

```go
import (
    sqltrace "gopkg.in/DataDog/dd-trace-go.v1/contrib/database/sql"
)

// Substituir sql.Open por sqltrace.Open
db, err := sqltrace.Open("postgres",
    "host=localhost dbname=42_chat sslmode=disable",
    sqltrace.WithServiceName("postgres-42-chat"),
)
```

**Tracing manual de spans críticos:**

```go
func ProcessMessage(ctx context.Context, msg []byte) error {
    span, ctx := tracer.StartSpanFromContext(ctx, "message.process")
    defer span.Finish()

    span.SetTag("message.size", len(msg))

    // ... lógica de negócio
    return nil
}
```

### 4.3 Custom Metrics (DogStatsD)

Métricas além do que `expvar` oferece — histogramas, percentis, distribuições.

```go
// internal/observability/datadog.go
package observability

import (
    "github.com/DataDog/datadog-go/v5/statsd"
)

var statsdClient *statsd.Client

func InitStatsd(addr string) error {
    var err error
    statsdClient, err = statsd.New(addr,
        statsd.WithNamespace("42_chat."),
        statsd.WithTags([]string{"env:production"}),
    )
    return err
}

// Exemplos de uso:
func RecordLatency(method, path string, duration time.Duration) {
    statsdClient.Histogram("http.request.duration_ms",
        duration.Seconds()*1000,
        []string{"method:" + method, "path:" + path},
        1.0,
    )
}

func RecordDBQueryDuration(queryName string, duration time.Duration) {
    statsdClient.Histogram("db.query.duration_ms",
        duration.Seconds()*1000,
        []string{"query:" + queryName},
        1.0,
    )
}

func RecordWSConnection() {
    statsdClient.Count("ws.connections.total", 1, nil, 1.0)
}

func GaugeActiveConns(count int) {
    statsdClient.Gauge("ws.connections.active", float64(count), nil, 1.0)
}

func RecordError(errorType string) {
    statsdClient.Count("errors.total", 1,
        []string{"error_type:" + errorType}, 1.0)
}
```

### 4.4 Datadog Dashboards Essenciais

Widgets recomendados para o dashboard de produção:

| Widget               | Métrica                                  | Visualização |
| -------------------- | ---------------------------------------- | ------------ |
| Request Rate         | `sum:http.requests.total{service:42-chat}` | Timeseries |
| Latência p95         | `p95:trace.http.request.duration_ms`     | Timeseries   |
| Erros 5xx            | `sum:errors.5xx{service:42-chat}`        | Timeseries   |
| WebSocket ativas     | `avg:ws.connections.active`              | Timeseries   |
| Pool PostgreSQL      | `avg:db.pool.active` / `avg:db.pool.idle` | Timeseries   |
| Goroutines           | `avg:app.goroutines`                     | Timeseries   |
| Uptime / Health      | `http_check` do endpoint `/api/health`   | Check Status |

---

## 5. Graceful Shutdown — Métricas

### 5.1 O Que Logar Durante o Shutdown

Durante um graceful shutdown (SIGTERM/SIGINT), logar métricas finais antes de encerrar:

```go
// cmd/server/main.go
func main() {
    // ... setup

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    logger.Info("shutdown initiated")

    // 1. Parar de aceitar novas conexões
    shutdownStart := time.Now()

    // 2. Fechar WebSockets ativamente
    activeWS := observability.WSActiveConns.Value()
    logger.Info("closing websocket connections",
        slog.Int64("active_connections", activeWS),
    )
    hub.Shutdown() // envia close frames

    // 3. Drenar requests HTTP em voo
    ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := server.Shutdown(ctx); err != nil {
        logger.Error("forced shutdown after timeout",
            slog.String("error", err.Error()),
        )
    }

    // 4. Logar métricas finais
    shutdownDuration := time.Since(shutdownStart)
    logger.Info("shutdown complete",
        slog.Duration("duration", shutdownDuration),
        slog.Int64("total_requests", observability.RequestsTotal.Value()),
        slog.Int64("total_ws_connections", observability.WSTotalConns.Value()),
        slog.Int64("errors_5xx", observability.Errors5xx.Value()),
    )

    // 5. Flush dos tracers Datadog
    observability.StopTracer()
}
```

### 5.2 Métricas de Shutdown para Datadog

Logar como métricas customizadas para correlação pós-mortem:

```go
// Antes do shutdown final, enviar métricas de encerramento
statsdClient.Count("app.shutdown", 1, []string{
    "active_ws:" + strconv.FormatInt(activeWS, 10),
}, 1.0)

statsdClient.Histogram("app.shutdown.duration_ms",
    shutdownDuration.Seconds()*1000, nil, 1.0)
```

---

## 6. Checklist de Produção

Antes de subir para AWS EC2, verificar:

### 6.1 Health Checks
- [ ] `/api/health` responde 200 com PostgreSQL healthy
- [ ] `/api/health/live` responde 200 sem dependências
- [ ] `/api/health/ready` responde 200 com todas dependências
- [ ] Docker healthcheck configurado (`pg_isready` + `curl /api/health`)
- [ ] Target group do ALB apontando para `/api/health`

### 6.2 Logs
- [ ] Logger estruturado em JSON (não texto puro) em produção
- [ ] Nível de log: `INFO` em produção, `DEBUG` em staging
- [ ] `request_id` em todas as linhas de log (via middleware)
- [ ] Logs enviados para stdout/stderr (capturados pelo Datadog Agent)
- [ ] Ausência de PII e dados sensíveis nos logs
- [ ] Datadog log collection habilitada (`logs_enabled: true`)
- [ ] Tags padrão nos logs: `env`, `service`, `version`

### 6.3 Métricas
- [ ] Middleware de métricas HTTP ativo (latência, status code, contagem)
- [ ] Métricas de pool PostgreSQL expostas
- [ ] Métricas de WebSocket ativas
- [ ] Métricas de runtime Go (goroutines, memória)
- [ ] Datadog Agent instalado e rodando na EC2
- [ ] Dashboard Datadog configurado com widgets essenciais
- [ ] Alertas configurados:
  - Latência p95 > 500ms
  - Erro 5xx rate > 1%
  - WebSocket connections == 0 por > 5min (se esperado > 0)
  - Pool PostgreSQL > 80% da capacidade
  - Health check falhando

### 6.4 APM / Tracing
- [ ] Tracer Datadog inicializado no `main.go`
- [ ] HTTP tracing via `httptrace.WrapHandler`
- [ ] SQL tracing via `sqltrace.Open`
- [ ] Spans manuais em operações críticas (WebSocket process, file upload)
- [ ] `DD_ENV`, `DD_SERVICE`, `DD_VERSION` configurados

### 6.5 Graceful Shutdown
- [ ] SIGTERM/SIGINT capturados
- [ ] Conexões WebSocket fechadas com close frame
- [ ] Requests HTTP drenados com timeout (máx 30s)
- [ ] Métricas finais logadas antes de encerrar
- [ ] Tracers e statsd clients flushados

### 6.6 Infraestrutura
- [ ] Security group da EC2 permite porta do Datadog Agent (8125/8126 UDP)
- [ ] IAM role com permissão para CloudWatch + métricas customizadas
- [ ] `DD_API_KEY` injetado via Secrets Manager ou variável de ambiente
- [ ] Datadog Agent configurado como systemd service com auto-restart

---

## Referências

- [`log/slog` — Go standard library](https://pkg.go.dev/log/slog)
- [`expvar` — Go standard library](https://pkg.go.dev/expvar)
- [Datadog Go Tracer — dd-trace-go](https://github.com/DataDog/dd-trace-go)
- [Datadog DogStatsD Go Client](https://github.com/DataDog/datadog-go)
- [Chi Middleware — go-chi/chi](https://github.com/go-chi/chi)
- [PostgreSQL Monitoring — Datadog](https://docs.datadoghq.com/integrations/postgres/)
- [Docker HEALTHCHECK](https://docs.docker.com/reference/dockerfile/#healthcheck)
- [Graceful Shutdown in Go](https://pkg.go.dev/net/http#Server.Shutdown)
