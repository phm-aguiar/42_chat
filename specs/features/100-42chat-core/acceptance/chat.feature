# language: pt-BR
# encoding: utf-8
# Feature: Chat em Tempo Real — 42 Chat Core (MVP)
# Feature 100

Funcionalidade: Chat em tempo real para a 42 São Paulo
  Como aluno da 42 São Paulo
  Quero trocar mensagens em tempo real com outros alunos
  Para facilitar a comunicação P2P no campus

  Contexto:
    Dado que o servidor 42 Chat está rodando
    E o PostgreSQL está populado com usuários de teste
    E a API 42 está mockada para retornar dados de OAuth2

  # ============================================================
  # Cenário: Happy Path — Login e envio de mensagem
  # ============================================================

  Cenário: Login OAuth2 e envio de mensagem
    Dado que estou na página de login
    Quando clico em "Login com 42"
    E sou redirecionado para a API 42 (mock)
    E autorizo o acesso
    Então sou redirecionado de volta para /callback
    E recebo um token JWT válido
    E sou redirecionado para /chat
    E vejo a sala "general" com o histórico recente

  Cenário: Enviar mensagem via WebSocket
    Dado que estou autenticado na sala "general"
    Quando digito "Olá, 42!" no input de mensagem
    E pressiono Enter
    Então a mensagem é enviada via WebSocket
    E aparece na minha tela com meu login e avatar
    E outros clientes conectados recebem a mensagem em tempo real

  Cenário: Ver broadcast de mensagem de outro usuário
    Dado que o usuário "marvin" está autenticado
    E eu estou autenticado como "zeenyt__"
    Quando "marvin" envia "Alguém pra fazer pair programming?"
    Então eu recebo a mensagem de "marvin" via WebSocket
    E vejo o avatar e login de "marvin" na mensagem

  # ============================================================
  # Cenário: Reconexão
  # ============================================================

  Cenário: Reconexão após perda de conectividade
    Dado que estou conectado ao WebSocket
    E recebi as últimas 50 mensagens
    Quando minha conexão WebSocket cai
    Então vejo um indicador "reconectando..." na UI
    E o frontend tenta reconectar com backoff exponencial
    Quando a conexão é restabelecida
    Então recebo as mensagens que perdi durante a desconexão
    E o indicador muda para "conectado"

  # ============================================================
  # Cenário: Token Expirado
  # ============================================================

  Cenário: Token JWT expirado redireciona para login
    Dado que meu token JWT expirou
    Quando tento acessar /api/messages
    Então recebo status 401
    E o frontend redireciona para a página de login
    E se ainda houver cookie de sessão na 42, o login é transparente

  # ============================================================
  # Cenário: Rate Limit — Cache 3 camadas
  # ============================================================

  Cenário: Cache anti-rate-limit da API 42
    Dado que o cache PostgreSQL tem o perfil do usuário "marvin"
    Quando "marvin" envia uma mensagem
    Então o backend NÃO consulta a API 42 novamente
    E usa os dados cacheados do PostgreSQL
    E o JWT de 12h é usado para autenticação sem revalidação

  # ============================================================
  # Cenário: Graceful Shutdown
  # ============================================================

  Cenário: Graceful shutdown notifica clientes
    Dado que 10 clientes estão conectados ao WebSocket
    Quando o servidor recebe SIGTERM
    Então todos os clientes recebem mensagem "system" tipo "shutdown"
    E o Hub drena as mensagens pendentes para o PostgreSQL
    E as conexões WebSocket são fechadas limpa-mente
    E o pool de conexões PostgreSQL é fechado
    E o servidor encerra com código 0

  # ============================================================
  # Cenário: Edge Cases
  # ============================================================

  Cenário: Mensagem muito longa é rejeitada
    Dado que estou autenticado
    Quando tento enviar uma mensagem com mais de 5000 caracteres
    Então o servidor rejeita a mensagem
    E o contador de caracteres no frontend mostra limite excedido

  Cenário: Usuário sem foto mostra iniciais
    Dado que o usuário "bocal" não tem image_url
    Quando "bocal" envia uma mensagem
    Então o avatar mostra as iniciais "BO" em um círculo
    Com fundo dot grid e borda cor de acento

  Cenário: Soft delete preserva auditoria
    Dado que uma mensagem foi "deletada" (deleted_at = NOW())
    Quando busco o histórico de mensagens
    Então a mensagem deletada NÃO aparece
    Mas o registro permanece no banco para auditoria LGPD
