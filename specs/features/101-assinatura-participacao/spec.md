# Spec: Assinatura de Participação (User Signature)

## Metadados
- **ID:** 101
- **Status:** approved
- **Autor:** phm-aguiar
- **Data:** 2026-06-17
- **Feature Anterior:** 100-42chat-core (depende de mensagens e WebSocket existentes)

## Propósito
> Cada usuário do chat (e futuro fórum) tem uma **assinatura de participação** 
> exibida inline abaixo de suas mensagens/posts, estilo chan/fórum clássico.
> 
> O cartão mostra o nível de engajamento na comunidade — total de mensagens,
> salas ativas e um tier de participação — servindo como marcador social de
> reputação e incentivando contribuição contínua.
> 
> **Público:** todos os usuários logados. A assinatura é pública, visível por
> qualquer um que veja uma mensagem do usuário.
> 
> **Por que agora:** o chat core (feature 100) já está implementado com mensagens
> e WebSocket. A assinatura é a primeira feature de "identidade comunitária",
> pavimentando o caminho para o fórum de tech futuro.

## Escopo

### Dentro do escopo
- Componente `UserSignature` reutilizável (chat hoje, fórum amanhã)
- API `GET /api/users/{id}/stats` retornando stats agregados do usuário
- Atualização em tempo real via WebSocket quando stats mudam
- Placeholder visual "novato" para usuários sem atividade
- Tiers de participação: novato → iniciante → participante → veterano

### Fora do escopo (explicitamente)
- Gráficos, charts, ou visualizações temporais (mensagens por dia/semana)
- Ranking/leaderboard entre usuários
- Edição de perfil (foto, bio, etc.) — isso é perfil 42, não assinatura
- Página dedicada `/perfil/@login` — a assinatura é inline, não standalone
- Conquistas/badges complexos (só o tier de participação)

## Comportamento Esperado

### Cenário Principal (Happy Path)
1. Usuário logado abre o chat e vê mensagens no canal
2. Abaixo de cada mensagem, o componente `UserSignature` renderiza o cartão do autor
3. Cartão mostra: avatar, login, tier de participação, total de mensagens, salas ativas
4. Quando o autor envia uma nova mensagem, o WebSocket notifica todos os clientes
5. Todos os `UserSignature` daquele autor atualizam em tempo real (total de msgs incrementa, tier pode subir)

### Cenários Alternativos
- **Usuário sem avatar:** Mostra avatar default (já existente no sistema 42)
- **Usuário logado vê a própria assinatura:** Mesmo componente, sem distinção visual (assinatura é pública)
- **Chat sem mensagens carregadas:** Nenhuma assinatura renderizada — só aparece quando há mensagens

## Edge Cases
- **Usuário novo (0 mensagens):** Placeholder "novato" com stats zerados e visual reduzido
- **WebSocket cai:** Assinatura mantém último estado conhecido. Reconecta automaticamente e puxa estado fresco via API
- **Stats de usuário que nunca enviou mensagem no canal atual:** Stats são globais (todas as salas), não por canal. Um usuário pode ter 50 mensagens no canal A e aparecer com stats completos no canal B
- **Alta frequência de mensagens (spam/flood):** WebSocket envia atualização de stats com debounce de 2s para evitar rajadas de updates

## Constraints
- **Performance:** Nenhuma constraint específica — stats são agregados SQL simples, sem latência crítica
- **Tecnologia:** Frontend React/TypeScript (componente), Backend Go/Chi (endpoint API), WebSocket (hub existente)
- **Prazo:** Sem prazo rígido
- **Segurança/Compliance:** Stats são públicos (qualquer usuário autenticado pode ver stats de qualquer outro). Sem PII além do login e avatar (já públicos)

## Critérios de Sucesso
- [ ] Assinatura renderiza abaixo de cada mensagem sem quebrar o layout do chat
- [ ] WebSocket mantém stats atualizados em tempo real com 50+ usuários simultâneos
- [ ] Stats exibidos batem com queries diretas no banco (sem discrepância)
- [ ] Placeholder "novato" aparece corretamente para usuários sem mensagens
- [ ] Tiers de participação refletem os thresholds definidos
- [ ] Testes automatizados cobrem o happy path e edge cases identificados

## Abordagem Escolhida
**API on-demand + WebSocket push.** Sem tabela materializada — stats são computados
via query SQL agregada na tabela `messages` quando o endpoint é chamado.
O WebSocket hub existente (feature 100) é estendido para broadcast de eventos
`user_stats_changed` quando uma mensagem é enviada. O frontend escuta o evento
e invalida/re-fetcha os stats do autor.

**Justificativa:** Sem constraint de performance, a abordagem mais simples evita
estado derivado (tabela materializada) e mantém single source of truth no banco.
A query `COUNT + DISTINCT` na tabela de mensagens é trivial para o volume esperado.

### Alternativas Consideradas
| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| Tabela `user_stats` materializada | Leitura O(1), mas introduz estado derivado e risco de inconsistência | Complexidade extra sem ganho real — sem constraint de performance |
| Stats inline no payload de mensagem | Zero requests extras | Acopla mensagens a stats, polui contrato da API de mensagens, overfetching pra quem não precisa da assinatura |

## Dependências
- **Feature 100 (42chat-core):** Mensagens, WebSocket hub, autenticação JWT
- **Tabela `messages`:** Precisa ter `user_id` e `room_id` para agregar stats
- **Tabela `users`:** `created_at` para "membro desde"

## Definições de Tiers
| Tier | Threshold (total de mensagens) | Rótulo |
|------|-------------------------------|--------|
| 0 | 0 | novato |
| 1 | 1-50 | iniciante |
| 2 | 51-200 | participante |
| 3 | 201+ | veterano |

## Checklist de Prontidão
- [ ] Propósito claro e sem ambiguidade
- [ ] Escopo delimitado (dentro/fora)
- [ ] Cenários cobrem happy path e alternativos
- [ ] Edge cases identificados com comportamento esperado
- [ ] Constraints explícitas
- [ ] Critérios de sucesso mensuráveis
- [ ] Abordagem escolhida justificada
- [ ] Aprovado: true
