# Spec: 42 Chat Core (MVP)

## Metadados
- **ID:** 100
- **Status:** draft
- **Aprovado:** true
- **Autor:** phm-aguiar
- **Data:** 2026-06-13
- **Stack:** Go, React, PostgreSQL, Docker

## Propósito
> Chat em tempo real para a 42 São Paulo (~300 alunos simultâneos), substituindo
> Slack/Discord com integração nativa à API da 42. MVP focado: login OAuth2 42,
> WebSocket, sala única "general", mensagens persistidas.

O campus perdeu o Discord e os alunos têm dificuldade com o Slack. O 42 Chat
resolve isso com uma plataforma leve, integrada à intra da 42, que facilita a
comunicação P2P — essencial para avaliações, pair programming e grupos de estudo.

## Escopo

### Dentro do escopo (MVP)
- **Autenticação:** Login exclusivo via OAuth2 da 42. JWT interno para sessão
- **Chat em tempo real:** WebSocket (gorilla/websocket) com sala única "general"
- **Persistência:** PostgreSQL para usuários, mensagens e logs de auditoria
- **Frontend:** React + Vite + Tailwind + Shadcn/ui. Estética brutalista 42
- **Deploy:** Docker Compose (Go + PostgreSQL). Alvo: AWS EC2 t2.micro
- **API REST:** Rotas para histórico de mensagens, status do usuário
- **Graceful shutdown:** Interceptação SIGINT/SIGTERM, desconexão limpa

### Fora do escopo (features futuras)
- **Matchmaking de avaliação** (/eval) — Feature 101
- **Campus map** (localização em tempo real) — Feature 102
- **TUI cliente terminal** (Bubbletea) — Feature 103
- **Painel admin Bocal** (moderação, kill switch) — Feature 104
- **Salas múltiplas** (públicas, privadas, pair programming) — Feature 105
- **Mensagens diretas (DM)** — Feature 106

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Aluno acessa https://chat.42sp.org.br
2. Redirecionado para OAuth2 da 42 (authorize endpoint)
3. Autoriza → callback para o backend com authorization code
4. Backend troca code por token (POST /oauth/token)
5. Backend busca dados do aluno (GET /v2/me) e cria/atualiza registro no PostgreSQL
6. Backend gera JWT interno e retorna pro frontend
7. Frontend armazena JWT (Zustand) e conecta WebSocket com token
8. Aluno vê a sala "general" com histórico recente (últimas 50 mensagens via REST)
9. Envia mensagem → WebSocket → broadcast para todos conectados → persiste PostgreSQL
10. Recebe mensagens de outros alunos em tempo real
11. Logout/desconexão → WebSocket fecha, JWT expira

### Cenário: Reconexão
1. Aluno perde conexão (wi-fi do campus)
2. Frontend detecta WebSocket close e tenta reconectar com backoff exponencial
3. Reconecta → recebe mensagens perdidas (timestamp > última recebida)
4. UI mostra indicador "reconectando..."

### Cenário: Token expirado
1. JWT expira durante sessão
2. Próxima requisição REST retorna 401
3. Frontend redireciona para login OAuth2
4. Se ainda tiver cookie de sessão na 42, login é transparente (sem re-autenticação)

### Cenário: Rate limit da API 42
1. Múltiplos alunos logam simultaneamente
2. Backend faz cache do perfil do aluno (foto, nível, host) por 15 minutos
3. Se API 42 retornar 429, backend usa cache e agenda retry

## Edge Cases
- **300 conexões simultâneas:** Ajustar ulimit (file descriptors) no servidor
- **Race condition no Hub:** sync.RWMutex no mapa de clientes WebSocket
- **Load balancer timeout:** Ping/Pong a cada 30s para manter conexão viva
- **Graceful shutdown:** Salvar buffer de mensagens pendentes antes de desligar
- **Aluno sem foto:** Placeholder padrão (iniciais em círculo com cor aleatória)
- **Mensagem muito longa:** Limite de 5000 caracteres. Acima disso, truncar com "..."
- **Conexão duplicada:** Mesmo aluno em múltiplas abas — permitir, cada aba = um client WebSocket
- **Logs de auditoria:** Toda mensagem tem user_id + timestamp. Soft delete, nunca hard delete

## Constraints
- **Escala:** Máximo 300 conexões simultâneas (campus presencial)
- **Infra:** AWS EC2 t2.micro (1 vCPU, 1 GB RAM). Go + PostgreSQL no mesmo host
- **Latência:** Mensagens devem chegar em < 500ms (WebSocket local ao campus)
- **Segurança:** OAuth2 42 obrigatório. JWT com expiração de 24h. HTTPS (Let's Encrypt)
- **Privacidade:** Retenção de mensagens por 6 meses (LGPD). Cron job de expurgo
- **Estilo visual:** Brutalista 42: fundo preto, texto branco, accents verde neon/ciano/magenta
- **border-radius:** 0 em todos os componentes
- **Deploy:** Docker Compose. Nada de Kubernetes pra 300 alunos

## Critérios de Sucesso
- [ ] Login OAuth2 42 funcional (happy path + token expirado)
- [ ] WebSocket conecta e recebe mensagens em tempo real
- [ ] Mensagens persistidas no PostgreSQL e recuperadas no histórico
- [ ] Frontend renderiza mensagens com estilo brutalista 42
- [ ] Graceful shutdown: servidor desliga sem corromper mensagens
- [ ] Rate limit da API 42 tratado com cache
- [ ] Docker Compose sobe ambiente completo (go + postgres)
- [ ] 300 conexões simultâneas sem crash (teste de carga)
- [ ] Mensagens expurgadas após 6 meses (cron job)
- [ ] Deploy funcional em EC2 t2.micro

## Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|---|---|---|
| Linguagem | Go | Alta concorrência, baixo consumo de RAM |
| WebSocket | gorilla/websocket | Padrão ouro da comunidade Go |
| Roteamento | Chi | Minimalista, interface padrão Go |
| Banco | PostgreSQL | Relacionamentos complexos, auditoria |
| Autenticação | OAuth2 42 + JWT | Integração nativa, sem gestão de senhas |
| Frontend | React + Vite | Rápido, moderno, Module Federation |
| Estilo | Tailwind + Shadcn/ui | Componentes copy-paste, customizáveis |
| Estado | Zustand | Simples, menos verboso que Redux |
| Container | Docker Compose | Ambiente reproduzível |
| Infra | AWS EC2 t2.micro | Camada gratuita, suficiente pra 300 alunos |

## Modelagem de Dados (MVP)

### users
| Coluna | Tipo | Descrição |
|---|---|---|
| id | INT PK | ID da API 42 |
| login | VARCHAR(50) | Login da intra |
| image_url | TEXT | URL da foto de perfil |
| level | NUMERIC(4,2) | Nível na intra |
| created_at | TIMESTAMP | Data de criação |

### messages
| Coluna | Tipo | Descrição |
|---|---|---|
| id | UUID PK | ID da mensagem |
| user_id | INT FK | Autor |
| content | TEXT | Conteúdo (max 5000 chars) |
| created_at | TIMESTAMP | Data de envio (indexado) |
| deleted_at | TIMESTAMP | Soft delete (auditoria) |

## Abordagem Escolhida
> **Backend Go monolítico + Frontend React.** O Go serve tanto a API REST
> quanto o WebSocket Hub no mesmo processo. Chi para rotas REST, gorilla/websocket
> para upgrade de conexão. PostgreSQL persiste usuários e mensagens.
> Frontend React com Vite, Tailwind e Shadcn/ui — componentes copy-paste com
> tema brutalista 42. Deploy via Docker Compose em EC2 t2.micro.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Backend + frontend monolítico (Go templates) | Mais simples, menos deploy | Sem experiência de SPA. Difícil escalar frontend separado |
| SQLite ao invés de PostgreSQL | Zero infra de banco | Sem suporte a concorrência real. Bocal exige auditoria |
| Frontend Vanilla JS | Zero dependências | Manutenção difícil. Shadcn/ui + Tailwind aceleram entrega |
