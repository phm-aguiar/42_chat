# language: pt

Funcionalidade: Assinatura de Participação (User Signature)
  Como um usuário autenticado do 42 Chat
  Quero visualizar a assinatura de participação abaixo de cada mensagem
  Para que eu possa ver o nível de engajamento de cada membro da comunidade

  A assinatura é um componente reutilizável `UserSignature` exibido inline
  abaixo de mensagens, mostrando avatar, login, tier de participação, total
  de mensagens e salas ativas. Stats são globais (cross-channel) e atualizam
  em tempo real via WebSocket. Tiers: novato (0), iniciante (1-50),
  participante (51-200), veterano (201+).

  Contexto:
    Dado que estou autenticado no 42 Chat com o login "joao_silva"
    E o canal "geral" está carregado com mensagens visíveis

  # ===================================================================
  # Happy Path
  # ===================================================================

  Cenário: Usuário visualiza assinatura de participação abaixo de uma mensagem
    Dado que o usuário "maria_dev" possui 42 mensagens no total
    E contribuiu em 3 salas distintas
    E seu tier de participação é "iniciante"
    Quando o canal carrega as mensagens
    Então abaixo de cada mensagem de "maria_dev" o componente UserSignature deve ser exibido
    E o cartão deve conter o avatar do usuário
    E deve exibir o login "maria_dev"
    E deve exibir o rótulo de tier "iniciante"
    E deve exibir "42 mensagens" como total
    E deve exibir "3 salas" como salas ativas

  Cenário: Assinatura renderiza sem quebrar o layout do chat
    Dado que o canal possui 20 mensagens de diversos autores
    Quando todas as mensagens são carregadas
    Então cada mensagem deve ter o componente UserSignature renderizado abaixo do seu conteúdo
    E o layout do chat não deve apresentar overflow horizontal
    E a rolagem vertical deve funcionar normalmente
    E o cartão UserSignature deve ter altura fixa e consistente entre mensagens

  # ===================================================================
  # Tiers de Participação
  # ===================================================================

  Cenário: Usuário novato — 0 mensagens exibe placeholder reduzido
    Dado que o usuário "novato_42" nunca enviou mensagens
    E seu total de mensagens é 0
    E seu total de salas ativas é 0
    Quando o canal carrega uma mensagem desse usuário
    Então o componente UserSignature deve ser exibido em modo reduzido
    E deve exibir o rótulo de tier "novato"
    E deve exibir "0 mensagens"
    E deve exibir "0 salas"
    E deve exibir o avatar default do sistema 42

  Cenário: Usuário iniciante — 1 a 50 mensagens exibe tier "iniciante"
    Dado que o usuário "joao_dev" enviou 1 mensagem
    Quando a assinatura é renderizada
    Então o tier exibido deve ser "iniciante"
    E o total de mensagens deve ser "1 mensagem"

    Dado que o usuário "joao_dev" enviou 50 mensagens
    Quando a assinatura é renderizada
    Então o tier exibido deve ser "iniciante"
    E o total de mensagens deve ser "50 mensagens"

  Cenário: Usuário participante — 51 a 200 mensagens exibe tier "participante"
    Dado que o usuário "ana_silva" enviou 51 mensagens
    Quando a assinatura é renderizada
    Então o tier exibido deve ser "participante"
    E o total de mensagens deve ser "51 mensagens"

    Dado que o usuário "ana_silva" enviou 200 mensagens
    Quando a assinatura é renderizada
    Então o tier exibido deve ser "participante"
    E o total de mensagens deve ser "200 mensagens"

  Cenário: Usuário veterano — 201+ mensagens exibe tier "veterano"
    Dado que o usuário "pedro_lider" enviou 201 mensagens
    Quando a assinatura é renderizada
    Então o tier exibido deve ser "veterano"
    E o total de mensagens deve ser "201 mensagens"

  # ===================================================================
  # Atualização em Tempo Real (WebSocket)
  # ===================================================================

  Cenário: Assinatura atualiza via WebSocket após nova mensagem do autor
    Dado que o usuário "maria_dev" está logado e visualizando o canal "geral"
    E o autor "joao_silva" possui atualmente 49 mensagens (tier "iniciante")
    E o UserSignature de "joao_silva" está renderizado na tela com "49 mensagens"
    Quando "joao_silva" envia uma nova mensagem no canal "geral"
    E o servidor emite o evento WebSocket "user_stats_changed" para o usuário "joao_silva"
    Então o frontend deve receber a notificação em até 3 segundos
    E o componente UserSignature de "joao_silva" deve atualizar para "50 mensagens"
    E o tier deve permanecer "iniciante"

  Cenário: Múltiplos clientes veem a mesma atualização de stats simultaneamente
    Dado que 3 usuários estão conectados e visualizando o canal "geral"
    E todos possuem o UserSignature de "pedro_lider" renderizado com "200 mensagens" (tier "participante")
    Quando "pedro_lider" envia uma mensagem no canal "geral"
    E o WebSocket emite "user_stats_changed" para "pedro_lider"
    Então todos os 3 clientes devem atualizar o UserSignature de "pedro_lider"
    E o novo total deve ser "201 mensagens"
    E o tier deve transitar para "veterano"

  Cenário: Debounce evita rajada de atualizações em alta frequência
    Dado que o usuário "flood_user" envia 10 mensagens em rápida sucessão (menos de 1s entre elas)
    Quando o servidor processa as mensagens
    Então o evento WebSocket "user_stats_changed" deve ser emitido no máximo a cada 2 segundos
    E o frontend não deve receber mais de 1 atualização por período de debounce
    E o estado final do UserSignature deve refletir o total correto de mensagens

  # ===================================================================
  # Transição de Tier
  # ===================================================================

  Cenário: Transição de tier iniciante para participante ao atingir 51 mensagens
    Dado que o usuário "carlos_souza" possui 50 mensagens (tier "iniciante")
    E seu UserSignature exibe o rótulo "iniciante"
    Quando "carlos_souza" envia sua 51ª mensagem
    E o WebSocket notifica a mudança de stats
    Então o UserSignature deve atualizar o total para "51 mensagens"
    E o rótulo de tier deve transitar de "iniciante" para "participante"
    E a transição visual deve ser perceptível (mudança de cor/ícone do tier)

  Cenário: Transição de tier participante para veterano ao atingir 201 mensagens
    Dado que o usuário "ana_silva" possui 200 mensagens (tier "participante")
    Quando "ana_silva" envia sua 201ª mensagem
    E o WebSocket notifica a mudança de stats
    Então o UserSignature deve atualizar o total para "201 mensagens"
    E o rótulo de tier deve transitar de "participante" para "veterano"

  Cenário: Transição de novato para iniciante na primeira mensagem
    Dado que o usuário "novato_user" possui 0 mensagens (tier "novato")
    E seu UserSignature exibe o placeholder reduzido
    Quando "novato_user" envia sua primeira mensagem
    E o WebSocket notifica a mudança de stats
    Então o UserSignature deve deixar o modo reduzido e exibir o cartão completo
    E o total deve ser "1 mensagem"
    E o tier deve transitar de "novato" para "iniciante"

  # ===================================================================
  # Stats Globais (Cross-Channel)
  # ===================================================================

  Cenário: Stats são globais e independem do canal atual
    Dado que o usuário "global_user" enviou 30 mensagens no canal "frontend"
    E enviou 25 mensagens no canal "backend"
    E nunca enviou mensagens no canal "geral"
    Quando qualquer usuário visualiza uma mensagem de "global_user" no canal "geral"
    Então o UserSignature deve exibir o total global de "55 mensagens"
    E deve exibir "2 salas" como salas ativas
    E o tier exibido deve ser "participante"
    E o total NÃO deve refletir apenas as mensagens do canal "geral"

  Cenário: Estatísticas do endpoint GET /api/users/{id}/stats refletem agregado global
    Dado que o usuário "cross_user" possui mensagens em múltiplos canais
    Quando o frontend consulta GET "/api/users/cross_user/stats"
    Então a resposta deve conter o total global de mensagens (soma de todos os canais)
    E deve conter a contagem distinta de salas (COUNT DISTINCT room_id)
    E o tier calculado deve usar o total global como base
    E a resposta deve incluir os campos "total_messages", "active_rooms", "tier" e "tier_label"

  Cenário: Usuário com mensagens em um canal tem stats completos em outro canal
    Dado que o usuário "maria_dev" enviou 100 mensagens apenas no canal "projetos"
    E nunca acessou o canal "off-topic"
    Quando um novo membro entra no canal "off-topic" e vê uma mensagem antiga de "maria_dev"
    Então o UserSignature de "maria_dev" deve exibir "100 mensagens"
    E deve exibir "1 sala" como sala ativa
    E o tier deve ser "participante"
    E não deve exibir "0 mensagens" por estar em um canal diferente

  # ===================================================================
  # Resiliência e Edge Cases
  # ===================================================================

  Cenário: WebSocket cai e assinatura mantém último estado conhecido
    Dado que o cliente possui o UserSignature de "maria_dev" com "42 mensagens" (tier "iniciante")
    E a conexão WebSocket é perdida
    Quando novas mensagens de "maria_dev" chegam ao servidor durante a desconexão
    Então o UserSignature deve continuar exibindo "42 mensagens" (último estado conhecido)
    E o componente não deve remover ou esconder a assinatura
    E o WebSocket deve tentar reconectar automaticamente

  Cenário: Reconexão WebSocket puxa estado fresco via API
    Dado que a conexão WebSocket foi restabelecida após uma queda
    E durante a desconexão "maria_dev" enviou 8 novas mensagens
    Quando o WebSocket reconecta
    Então o frontend deve consultar GET "/api/users/maria_dev/stats"
    E o UserSignature deve atualizar para "50 mensagens"
    E o tier deve refletir o estado mais recente

  Cenário: Usuário sem avatar configurado exibe avatar default do 42
    Dado que o usuário "new_user" não configurou avatar no perfil 42
    Quando a assinatura é renderizada
    Então o UserSignature deve exibir o avatar default do sistema 42
    E o restante do cartão (login, tier, stats) deve renderizar normalmente

  Cenário: Usuário logado vê a própria assinatura sem distinção visual
    Dado que estou autenticado como "joao_silva"
    E minhas mensagens estão visíveis no canal
    Quando visualizo uma mensagem que eu mesmo enviei
    Então o UserSignature deve ser renderizado normalmente abaixo da minha mensagem
    E não deve haver indicador visual de "você" ou destaque diferente dos demais

  Cenário: Canal sem mensagens não renderiza assinatura
    Dado que o canal "vazio" não possui nenhuma mensagem
    Quando o canal é carregado
    Então nenhum componente UserSignature deve ser renderizado
    E o estado vazio do canal deve ser exibido normalmente

  Cenário: API de stats retorna dados consistentes com queries diretas no banco
    Dado que o usuário "check_user" possui registros na tabela "messages"
    Quando a API GET "/api/users/check_user/stats" é consultada
    Então o total de mensagens retornado deve ser igual ao resultado de "SELECT COUNT(*) FROM messages WHERE user_id = 'check_user'"
    E o total de salas ativas deve ser igual a "SELECT COUNT(DISTINCT room_id) FROM messages WHERE user_id = 'check_user'"
    E o tier calculado deve obedecer aos thresholds: 0=novato, 1-50=iniciante, 51-200=participante, 201+=veterano

  Cenário: API de stats responde corretamente para usuário inexistente
    Dado que o ID "fake_user_999" não corresponde a nenhum usuário real
    Quando o frontend consulta GET "/api/users/fake_user_999/stats"
    Então a API deve retornar HTTP 404
    E o corpo da resposta deve indicar que o usuário não foi encontrado
