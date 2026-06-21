---
title: "42 Chat — Engineering Requirements"
category: references
tags: [42_chat, engineering, go, linux, websockets, devops]
sources:
  - wiki/_raw/42-chat-research.md
summary: "Requisitos críticos de engenharia: concorrência segura em Go, graceful shutdown, tuning de file descriptors no Linux, caching contra rate limits da API 42, e observabilidade com Prometheus."
provenance:
  extracted: 0.88
  inferred: 0.10
  ambiguous: 0.02
base_confidence: 0.82
lifecycle: draft
lifecycle_changed: "2026-06-14"
tier: core
created: "2026-06-14"
updated: "2026-06-14"
---

# 42 Chat — Engineering Requirements

> Requisitos críticos que separam um projeto amador de uma aplicação pronta para produção no campus.

## 1. Gestão de Recursos do Linux (File Descriptors)

### Problema

Cada conexão WebSocket consome um file descriptor no servidor. Com ~300 alunos e múltiplas abas por aluno, o limite padrão do Linux (frequentemente 1024) é insuficiente.

### Solução

- Ajustar `ulimit -n` no servidor de produção
- Configurar `fs.file-max` no kernel
- Monitorar uso de descritores via métricas expostas

## 2. Concorrência Segura em Go

### Problema

O Hub de WebSockets gerencia um mapa de clientes (`map[*Client]bool`). Mapas em Go não são thread-safe — acesso concorrente causa panic e crash do servidor.

### Soluções (em ordem de preferência)

1. **Channels**: Centralizar operações de registro/remoção em uma única goroutine dedicada (filosofia Go)
2. **`sync.RWMutex`**: Travar o mapa antes de escrita, permitir leituras paralelas

```go
// Abordagem com Channels (recomendada)
type Hub struct {
    clients    map[*Client]bool
    register   chan *Client
    unregister chan *Client
}

func (h *Hub) Run() {
    for {
        select {
        case client := <-h.register:
            h.clients[client] = true
        case client := <-h.unregister:
            delete(h.clients, client)
        }
    }
}
```

## 3. Graceful Shutdown

### Problema

Ao matar o processo Go para deploy, 300 conexões WebSocket caem abruptamente, mensagens podem ser perdidas no buffer.

### Solução

Interceptar sinais do SO (`SIGINT`, `SIGTERM`) e executar shutdown limpo:

1. Parar de aceitar novos logins
2. Notificar clientes conectados sobre reinício
3. Flush do buffer de mensagens → PostgreSQL
4. Fechar conexões WebSocket de forma amigável
5. Encerrar o processo

```go
sigChan := make(chan os.Signal, 1)
signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
<-sigChan
// graceful shutdown sequence
```

## 4. Rate Limits e Cache da API 42

### Problema

A API da Intra tem rate limit (~2 req/s por credencial). Bater na API para cada mensagem bloqueia o backend.

### Solução

- **Cache em memória** (map no Go) — localização do aluno atualizada a cada 10-15 minutos
- **Ou Redis leve** — se houver necessidade de compartilhar cache entre instâncias
- **Webhook** — se a 42 fornecer, usar para atualizações push

## 5. Heartbeat (Ping/Pong) para WebSockets

### Problema

Load balancers de cloud (AWS) derrubam conexões TCP inativas após ~60s. Fatal para WebSockets.

### Solução

Implementar ping/pong no servidor Go a cada 30 segundos para manter a conexão viva:

```go
// gorilla/websocket
conn.SetReadDeadline(time.Now().Add(60 * time.Second))
conn.SetPongHandler(func(string) error {
    conn.SetReadDeadline(time.Now().Add(60 * time.Second))
    return nil
})

// Ticker para ping
ticker := time.NewTicker(30 * time.Second)
go func() {
    for range ticker.C {
        conn.WriteMessage(websocket.PingMessage, nil)
    }
}()
```

## 6. Observabilidade

### Métricas Expostas

- Endpoint `/metrics` com:
  - Número de goroutines ativas
  - Consumo de memória
  - Latência do banco de dados (`DB.Stats()`)
  - Conexões WebSocket ativas
  - Conexões idle, transações em espera, pool exhaustion

### Stack de Monitoramento

- **MVP**: `expvar` ou handler HTTP simples exportando métricas em texto plano
- **Produção**: Prometheus + Grafana, ou CloudWatch na AWS

```go
// Exemplo com DB.Stats()
go func() {
    for range time.Tick(10 * time.Second) {
        stats := db.Stats()
        // Exportar: idle connections, in-use, wait count, etc.
    }
}()
```

## 7. Segurança e Moderação

### JWT

Tokens gerados após OAuth2 da 42, com claims de sessão e expiração.

### Kill Switch

Rota de API restrita ao Bocal para:
- Suspender usuário imediatamente
- Apagar mensagens que violem o código de conduta

### Logs de Auditoria

Toda mensagem registrada com `user_id`, `room_id`, `content`, `created_at`. Logs imutáveis para compliance.

### Retenção de Dados (LGPD)

Cron job no Go para expurgar mensagens com mais de 6 meses, mantendo conformidade com leis de privacidade.

## 8. Gerenciamento de Segredos

- Credenciais OAuth2 (Client ID/Secret) **nunca** hardcoded
- Injeção via variáveis de ambiente no deploy
- CI/CD usa CLI de gerenciador de senhas (ex: Bitwarden CLI) para buscar segredos

## 9. Comparativo: Channels vs Mutex vs RWMutex

Debate arquitetural sobre proteção do mapa de clientes no Hub. Dados extraídos da análise de concorrência em Go.

| Abordagem | Mecanismo | Aplicação Recomendada | Desvantagem em WebSocket Hub |
|---|---|---|---|
| **Channels** | Goroutines comunicam via dutos sincronizados | Transferência de propriedade, pipelines, distribuição de trabalho | Round-trip via goroutine gerente por mensagem adiciona latência e overhead de escalonamento |
| **sync.Mutex** | Bloqueia acesso ao bloco de memória | Proteção de estado simples, variáveis atômicas | Estrangulamento em leituras simultâneas (bloqueia leitura também) |
| **sync.RWMutex** | Múltiplas leituras simultâneas, exclusão mútua só na escrita | Caches, mapas de sessão com perfil de alta leitura/baixa escrita | Maior complexidade estrutural, risco de deadlock se mal encapsulado |

**Decisão arquitetural:** Modelo híbrido — `sync.RWMutex` protege o dicionário de conexões (leituras de broadcast paralelas, bloqueio só em insert/remove). Cada cliente encapsula um `send chan []byte` como buffer elástico de saída.

## 10. Tuning do Sistema Operacional (Linux)

Parâmetros críticos para a instância AWS EC2 t2.micro (1 vCPU, 1GB RAM):

### File Descriptors e Rede

| Parâmetro | Valor | Justificativa |
|---|---|---|
| `fs.file-max` | 100000 | Limite global do kernel para arquivos abertos |
| `ulimit -n` | 65535 | Limite hard/soft por processo |
| `net.ipv4.tcp_rmem/wmem` | Otimizado | Buffers TCP sob alta concorrência |

### PostgreSQL Tuning (1GB RAM total)

| Parâmetro | Valor | Justificativa |
|---|---|---|
| `shared_buffers` | 256MB (~25% RAM) | Cache de dados em memória |
| `effective_cache_size` | 512MB | Estimativa para query planner (não aloca memória) |
| `work_mem` | 16MB | Memória por operação de sort/hash — conservador para evitar swap |
| `max_connections` | 100 | Alinhado ao pool de conexões do driver Go |

## 11. Estratégia Anti-Rate-Limit (API 42)

A API da 42 impõe **2 req/s e 1200 req/h**. Estratégia de cache agressiva:

| Domínio de Dados | Estratégia de Cache | Impacto |
|---|---|---|
| **Identidade/Autenticação** | OAuth2 → JWT de 12h assinado internamente | Remove tráfego de validação contínua da cota oficial |
| **Perfil (foto, nome, nível)** | Cache durável no PostgreSQL no primeiro login, atualização em background espaçada | 1 chamada por aluno por período vs N chamadas por visualização |
| **Mapeamento de Laboratório** | Ingestão unificada de todas as posições via job em intervalos fixos (ex: 30s) | 1 chamada batch por ciclo vs 300 chamadas individuais |

## 12. Algoritmo de Matchmaking (Evals)

Sistema de pareamento para avaliações entre alunos, modelado matematicamente:

| Parâmetro de Busca | Mecânica de Ponderação | Efeito na Fila |
|---|---|---|
| **Projeto Alvo** | Filtro booleano absoluto | Somente mesmo projeto converge na fila |
| **Diferencial de Pontos** | Pesagem dinâmica de assimetria | Prioridade para quem precisa gastar pontos excedentes |
| **Equilíbrio Acadêmico (Nível)** | Threshold de disparidade aceitável | Evita nível 1 avaliando nível 15 |
| **Topologia Física** | Bonificação por proximidade geográfica | Otimiza logística (mesmo cluster/andar) |

**Ciclo de vida:**
1. Aluno invoca `/eval [projeto]` → perfil serializado entra na fila em RAM
2. Worker loop escaneia a fila periodicamente
3. Heurística combinada calcula scores e encontra par ótimo
4. Ready Check (Aceitar/Recusar) disparado para ambos — só consolida após dupla confirmação

## 13. Salas Efêmeras (Pair Programming)

- **Criação:** `/pair [assunto]` → sala UUID isolada, canais limpos
- **Destruição:** Garbage collection quando último cliente desconecta
- **Janela de tolerância:** 5 minutos para sobreviver a oscilações de rede WiFi
- **Persistência:** Metadados de interação → PostgreSQL (auditoria do Bocal)

## 14. Mapeamento de Campus (Location Endpoint)

O endpoint `GET /v2/campus/:campus_id/locations` fornece localização física precisa (ex: `e1z2m4`). Estratégia de ingestão otimizada:

1. **Ingestão Periódica:** Worker assíncrono a cada 30s com `?filter[active]=true&sort=-begin_at&page[size]=100`
2. **Indexação O(1):** Mapa `map[string]HostString` em RAM após decodificação JSON
3. **Diff Propagation:** Worker compara mapa novo vs anterior, emite broadcast apenas das mudanças (entrou/saiu)
4. **Latência:** Respostas em <10ms do cache interno, sem dependência da API remota

## 15. BDD + Agente Hermes (Pipeline de Testes)

O projeto adota Behavior-Driven Development orquestrado pelo **Agente Hermes** (Nous Research) para automação de qualidade:

### Stack de Testes
- **Godog:** Interpreta arquivos `.feature` Gherkin e executa step definitions em Go
- **TestContainers:** PostgreSQL efêmero isolado para cada suite de integração
- **BDD-Godog-Scaffolder Skill:** Skill do Hermes que gera automaticamente step definitions a partir de cenários Gherkin em pull requests
- **Mock de API 42:** Hermes interage com endpoints reais para gravar respostas estáticas usadas nos TestContainers, eliminando dependência de rede e rate limits durante testes

### Fluxo de Qualidade
1. Desenvolvedor escreve cenários Gherkin (`Dado/Quando/Então`)
2. Pull request aciona pipeline com Godog + TestContainers
3. Hermes Agent identifica lacunas de step definitions e gera código Go automaticamente
4. Suite de integração valida contra PostgreSQL efêmero com mocks da API 42
5. Messaging Gateway permite que moderadores interajam via Slack/Discord com a pipeline

## 16. Arquitetura de Microfrontends (Detalhamento)

Aplicação cliente decomposta em 3 módulos via Module Federation (Vite):

| Módulo | Responsabilidade |
|---|---|
| **Host App (Shell)** | Roteamento, autenticação (JWT), barra lateral, inicialização do WebSocket |
| **MFE Chat** | Lista de contatos, histórico, input reativo, salas efêmeras |
| **MFE Campus Map** | Grid SVG/CSS Grid das bancadas de iMacs com perfis sobrepostos |

**Singleton Zustand:** Declarado como dependência compartilhada no Vite Federation para evitar múltiplas instâncias dessincronizadas. Configuração crítica:

| Parâmetro Vite Federation | Valor | Efeito |
|---|---|---|
| `name` | `host` | Identificador global |
| `remotes` | `{ chat: '...', map: '...' }` | Injeta microapps em runtime |
| `exposes` | `{ './store': './src/store/index.ts' }` | Expõe store Zustand como módulo |
| `shared` | `['react', 'react-dom', 'zustand']` | Singleton — baixado e instanciado uma única vez |

## Ver Também

- [[references/42-chat-platform-architecture|42 Chat Platform Architecture]] — Stack e arquitetura
- [[references/42-chat-design-system|42 Chat Design System]] — Sistema visual
- [[references/42-chat-architecture-diagram|42 Chat Architecture Diagram]] — Diagrama Mermaid
