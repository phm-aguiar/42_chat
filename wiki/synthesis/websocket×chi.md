---
title: "WebSocket × Chi"
category: synthesis
tags: [websocket, chi, networking, real-time, synthesis]
sources:
  - "entities/websocket.md"
  - "entities/chi.md"
  - "references/websocket-production.md"
  - "entities/hub.md"
  - "entities/client.md"
  - "references/auth-integration.md"
created: "2026-06-21T00:00:00Z"
rag_score: 0.5
updated: "2026-06-21T00:00:00Z"
summary: "A interseção entre o protocolo WebSocket (full-duplex, stateful) e o roteador Chi (HTTP, stateless): como o 42 Chat resolve o impedance mismatch entre dois paradigmas de rede que coexistem no mesmo servidor."
provenance:
  extracted: 0.30
  inferred: 0.65
  ambiguous: 0.05
base_confidence: 0.64
lifecycle: draft
lifecycle_changed: "2026-06-21"
tier: core
---

# WebSocket × Chi

## The Connection

Chi é um roteador HTTP puro — cada request é independente, stateless, com ciclo de vida gerenciado
pelo `net/http`. WebSocket começa como HTTP (upgrade) e depois se torna um protocolo distinto:
full-duplex, stateful, com goroutines de longa duração e keepalive constante. A interseção é o
momento do **upgrade**: Chi entrega a `*http.Request` para o `ws.Handler`, que realiza a metamorfose
de "request HTTP" para "conexão WebSocket persistente". ^[extracted]

O 42 Chat resolve esse impedance mismatch com dois invariantes: (1) o Chi gerencia autenticação
e roteamento **antes** do upgrade, e (2) após o upgrade, o WebSocket assume completamente — o Chi
não sabe que a conexão existe e não interfere. ^[inferred]

## Onde se Encontram

O único ponto de contato no código: `r.Get("/ws", wsHandler.ServeHTTP)`.

```go
// cmd/server/main.go
r.Get("/ws", wsHandler.ServeHTTP)  // Chi registra a rota

// internal/ws/handler.go
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // 1. JWT validation (ainda no mundo HTTP/Chi)
    token := r.URL.Query().Get("token")
    claims, err := h.jwtManager.ValidateToken(token)

    // 2. Upgrade — a fronteira entre os mundos
    conn, err := h.upgrader.Upgrade(w, r, nil)
    // A partir daqui, Chi não existe mais para essa conexão.

    // 3. Mundo WebSocket
    client := &Client{UserID: claims.UserID, Login: claims.Login, ...}
    h.hub.Register(client)
    go client.readPump()   // goroutine de longa duração
    go client.writePump()  // goroutine de longa duração
}
```

## Cross-cutting Insight

O Chi e o WebSocket não são concorrentes arquiteturais — são **camadas complementares de rede**
que o 42 Chat usa para propósitos distintos. Chi gerencia o tráfego REST (mensagens históricas,
stats de usuário, callback OAuth2) — operações pontuais e stateless. WebSocket gerencia o tráfego
em tempo real (broadcast de mensagens, join/leave, user_stats_changed) — operações contínuas e
stateful. ^[inferred]

**Padrão: "Router-Grade Boundary"**

O Chi atua como um guarda de fronteira: autentica, autoriza, loga, e então passa o controle para
o WebSocket. Este padrão tem implicações importantes:

| Responsabilidade | Dono | Por quê |
|---|---|---|
| Autenticação (JWT) | Chi (middleware) | Reusa o `JWTMiddleware` — mesma lógica para REST e WS |
| Rate limiting | Chi (middleware) | Pode limitar upgrades/s antes mesmo de abrir conexão |
| Logging (RequestID) | Chi (middleware) | `middleware.RequestID` gera ID antes do upgrade |
| CORS | Chi (middleware) | Necessário para handshake HTTP inicial |
| Keepalive (ping/pong) | WebSocket | Responsabilidade do protocolo, não do roteador |
| Broadcast | WebSocket (Hub) | Stateful — Chi não foi feito para isso |
| Graceful shutdown | Ambos | Chi para de aceitar novas conexões; WebSocket drena as existentes |

## Tensions and Trade-offs

- **Single point of failure:** O endpoint `/ws` é uma única rota no Chi. Se o Chi estiver
  overloaded com requests REST, o handshake WebSocket também sofre. Considere um listener
  separado para WebSocket em produção de alta escala. ^[inferred]
- **Middleware duplicado:** O `wsHandler.ServeHTTP` valida JWT manualmente (query param), enquanto
  as rotas REST usam `JWTMiddleware` (Authorization header). Isso é necessário porque o WebSocket
  JavaScript API não envia headers customizados, mas cria um caminho de validação paralelo que
  pode divergir. ^[extracted]
- **Goroutines órfãs:** Se o Chi crashar (ex: `Recoverer` captura um panic), as goroutines de
  WebSocket (readPump/writePump) podem continuar rodando. O `hub.go` implementa graceful shutdown
  com `sync.WaitGroup`, mas depende de o `main()` chamar `hub.Stop()` — se o crash for antes, as
  goroutines ficam órfãs. ^[ambiguous]
- **CheckOrigin sempre true:** O `upgrader.CheckOrigin` retorna `true` para MVP local. Em produção
  com Chi, o `middleware.RealIP` + CORS deveriam ser a defesa primária — o `CheckOrigin` deveria
  validar contra uma whitelist de origens. ^[extracted]

## Open Questions

- Separar o listener WebSocket do listener REST em produção? (porta 8080 vs 8081)
- O `JWTMiddleware` do Chi pode ser adaptado para validar token em query param também?
- Como o graceful shutdown coordena Chi (parar de aceitar) + WebSocket (drenar conexões existentes)?
- Métricas separadas: latência de handshake (Chi) vs latência de broadcast (WebSocket)?

## Related

- [[entities/websocket|WebSocket]] — Protocolo e implementação
- [[entities/chi|Chi]] — Roteador HTTP
- [[entities/hub|Hub]] — Gerenciador de conexões WebSocket
- [[entities/client|Client]] — Conexão WebSocket individual
- [[references/websocket-production|WebSocket Production]] — Ping/pong, scaling, rate limiting
- [[references/auth-integration|Auth Integration]] — Arquitetura de 3 camadas
- [[references/go-chi-router|Go Chi Router]] — Padrões de roteamento
- [[references/integration-testing-docker|Integration Testing with Docker]] — Testes end-to-end com WebSocket
