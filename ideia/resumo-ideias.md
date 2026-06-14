Project Brief: 42 Campus Real-Time Chat & Matchmaking
Contexto e Objetivo
Desenvolver uma aplicação de chat em tempo real exclusiva para os alunos da 42 São Paulo (aprox. 300 conexões simultâneas), visando substituir o uso do Slack/Discord. O foco do produto é fomentar o peer-to-peer learning, facilitar o matchmaking de avaliações e mapear a localização física dos alunos nos clusters, mantendo total conformidade com as exigências de auditoria e moderação da administração (Bocal).

1. Arquitetura e Stack de Backend

Linguagem Core: Go (Golang) com foco em alta concorrência e baixo consumo de memória.

Comunicação Real-time: WebSockets (preferencialmente gorilla/websocket).

Roteamento REST: Chi ou Gin para servir as rotas da API estática.

Banco de Dados: PostgreSQL (estruturado via Docker Compose para ambiente local e produção). Necessário para persistência confiável de logs de auditoria e relacionamentos.

Autenticação: Integração estrita com a API OAuth2 da 42 Intra, convertendo o login em um JWT interno para gerenciamento de sessão seguro.

Design Pattern: Arquitetura limpa/modular (ex: /cmd, /internal/chat, /internal/auth, /internal/repository).

2. Arquitetura e Stack de Frontend (Microfrontends)

Core: React + Vite.

Abordagem Estrutural: Microfrontends utilizando Module Federation (separação entre o "Shell/Host" de autenticação e os "Microapps" de Chat e Mapa do Campus).

Estilização e UI: Tailwind CSS combinado com Shadcn/ui.

Identidade Visual: Estética brutalista/hacker. border-radius: 0, alto contraste, paleta restrita (fundo preto sólido, texto branco, destaques em verde neon, ciano e magenta).

Gerenciamento de Estado Global: Zustand (para gerenciar token JWT e status de conexão WS entre os microfrontends).

3. Infraestrutura, Deploy e DevOps

Conteinerização: Docker para toda a stack (Backend e Banco de Dados).

Hospedagem: Instância AWS EC2 (camada gratuita) para o backend Go + PostgreSQL. Deploy do frontend estático via Vercel, Netlify ou AWS S3+CloudFront.

Gerenciamento de Segredos: Injeção de credenciais (Client ID/Secret da 42) via variáveis de ambiente no CI/CD, utilizando ferramentas como Bitwarden CLI.

4. Funcionalidades Core (Regras de Negócio Diferenciais)

Campus Mapping: Consumo em cache da API da 42 para exibir a localização física em tempo real do aluno no chat (ex: e1z2m4).

Evaluation Matchmaking: Comandos interativos (ex: /eval) para encontrar rapidamente pares para avaliação de projetos.

Salas Efêmeras: Criação de salas temporárias para Pair Programming que são destruídas após o uso.

5. Requisitos Críticos de Engenharia (Busca de Soluções)

Gestão de Recursos Linux: Tuning de File Descriptors (ulimit) para evitar gargalos de conexões WebSocket abertas.

Concorrência Segura em Go: Prevenção de Race Conditions no mapa de clientes do WebSocket Hub utilizando sync.RWMutex ou arquitetura orientada a Channels.

Graceful Shutdown: Interceptação de sinais do SO (SIGINT/SIGTERM) para encerramento limpo das rotinas Go, salvamento do buffer de mensagens no Postgres e desconexão amigável dos clientes.

Estratégia de Cache e Rate Limit: Sistema de cache (em memória ou Redis leve) para evitar bloqueio por Rate Limit ao consumir a API da 42 (foto, nível e host atual).

Observabilidade: Exposição de métricas (uso de goroutines, latência do DB) para monitoramento.