---
title: "42 Chat — Arquitetura de Backend e Gestão de Concorrência Extrema"
category: references
tags:
  - 42_chat
  - arquitetura
  - pesquisa
sources:
  - "wiki/_raw/42-chat-research.md"
  - "references/42-chat-research-report.md"
base_confidence: 0.55
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
rag_score: 0.4867
updated: "2026-06-15"
---
title: "42 Chat — Arquitetura de Backend e Gestão de Concorrência Extrema"
summary: "Seção 2/9 do relatório de arquitetura e viabilidade do 42 Chat. Arquitetura de Backend e Gestão de Concorrência Extrema."
---

# 42 Chat — Arquitetura de Backend e Gestão de Concorrência Extrema


O núcleo de processamento e roteamento da aplicação exige um design que suporte processamento assíncrono intensivo, multiplexação de entrada/saída (I/O) não bloqueante e um consumo estrito e previsível de memória RAM.

Este último ponto é de suma importância para garantir a viabilidade econômica do projeto, permitindo que a aplicação opere de forma confortável dentro da restrição severa de 1GB de RAM imposta pela camada gratuita da AWS EC2 (Elastic Compute Cloud) nas instâncias da família t2.micro ou t3.micro.

A linguagem Go (Golang) foi selecionada deliberadamente para a camada central do backend devido à sua eficiência provada na gestão de concorrência por meio de goroutines leves, que consomem meros kilobytes de memória inicial, e sua facilidade inerente na manipulação de conexões persistentes de longa duração exigidas pelo protocolo WebSocket.A comunicação bidirecional e síncrona será suportada primariamente pela biblioteca gorilla/websocket, que é o padrão da indústria para implementações em Go devido à sua robustez e controle granular sobre buffers de leitura e escrita.

O roteamento de conexões REST para servir a API estática (como o fluxo inicial de autenticação e a recuperação de históricos de mensagens) será provido pelos frameworks Chi ou Gin.

A arquitetura de roteamento de mensagens baseia-se fortemente no padrão de design Hub and Spoke.

Nesse arranjo topológico, um Hub central em memória atua como o motor de roteamento, mantendo o registro rigoroso de todos os clientes atualmente conectados e despachando as mensagens de forma centralizada.O design pattern de Clean Architecture (Arquitetura Limpa) ou arquitetura hexagonal será empregado para garantir a modularidade estrita do código, facilitando testes e futuras substituições de componentes tecnológicos.

O repositório será estruturado em domínios lógicos.

O diretório /cmd abrigará o ponto de entrada da aplicação e a injeção de dependências.

O /internal/domain conterá as entidades puras de negócios, como Mensagem, Usuário, e Sala, independentes de qualquer framework.

O /internal/repository fornecerá as implementações concretas de acesso ao armazenamento em PostgreSQL e aos mecanismos de cache.

O /internal/chat encapsulará a lógica complexa de roteamento do Hub de WebSockets e algoritmos de matchmaking.

Por fim, o /internal/auth manipulará o fluxo OAuth2 e a criptografia dos tokens JWT.Um dos desafios mais clássicos e críticos na implementação de servidores WebSocket paralelos em Go é a prevenção absoluta de condições de corrida (race conditions) ao gerenciar o mapa central de clientes conectados no Hub.

O debate arquitetônico e idiomático na comunidade Go frequentemente oscila entre o uso de primitivas baseadas em troca de mensagens (Channels) e primitivas de bloqueio de memória (sync.Mutex ou sync.RWMutex).

A literatura oficial de concorrência em Go recomenda uma abordagem pragmática, afastando-se do dogma de usar channels para todos os cenários.

Channels são ferramentas ideais para a transferência explícita de propriedade de dados, para a implementação de pools de trabalhadores e para a distribuição de unidades de trabalho assíncronas.

Por outro lado, Mutexes são altamente otimizados e superiores em performance para a proteção direta de estado compartilhado, contadores e caches residentes em memória.A tabela a seguir apresenta uma comparação profunda entre as duas abordagens, justificando a escolha técnica tomada para a arquitetura do Hub de WebSockets.Abordagem de Concorrência em GoMecanismo de FuncionamentoAplicação RecomendadaDesvantagem em Cenário de WebSocket HubChannels (Comunicação de Estado)Goroutines comunicam-se enviando cópias ou ponteiros de dados através de dutos sincronizados.Transferência de propriedade de dados, pipelines de processamento, e distribuição de trabalho.Transformar a leitura de um mapa global de clientes em um ciclo de request-response via channels adiciona latência e overhead de escalonamento excessivo para cada broadcast de mensagem.sync.Mutex (Exclusão Mútua)Bloqueia o acesso a um bloco de memória para todas as demais goroutines enquanto uma detém o cadeado.Proteção de estado simples e variáveis atômicas contra leituras e escritas simultâneas.Causa estrangulamento de performance (bottleneck) se muitas goroutines tentarem ler simultaneamente, pois bloqueia tanto leituras quanto escritas.sync.RWMutex (Leitura Múltipla)Permite que múltiplas goroutines leiam o estado simultaneamente, mas garante exclusão mútua total apenas durante escritas.Caches em memória, mapas de sessões e dicionários com perfil de alta leitura e baixa escrita.Maior complexidade estrutural se as regras de bloqueio não forem bem contidas, podendo levar a deadlocks se não encapsulado corretamente.Em um Hub central de WebSocket, o mapa que mapeia identificadores de usuários para seus respectivos ponteiros de conexão (map[string]*Client) representa uma estrutura de estado compartilhado que sofre leitura intensiva (sempre que uma mensagem precisa ser transmitida para a sala inteira em operações de broadcast) e escrita esporádica (apenas quando um novo usuário efetua o handshake de conexão ou quando a conexão TCP é interrompida).

O uso exclusivo de channels para gerenciar as leituras deste mapa obrigaria cada tentativa de envio de mensagem a realizar um round trip através de uma goroutine gerente, destruindo o benefício do lookup de complexidade O(1) dos mapas em Go e induzindo atrasos indesejados.Portanto, a arquitetura de concorrência adotará um modelo híbrido de alta performance.

Para a proteção do estado global do Hub, utilizar-se-á sync.RWMutex para envolver e proteger o dicionário de conexões.

Isso permite que múltiplas goroutines iterem ou leiam o mapa simultaneamente durante operações de broadcast, resultando em performance inigualável, enquanto impõe um bloqueio total e seguro apenas nas frações de milissegundo em que um novo usuário é inserido ou removido do mapa.

Simultaneamente, cada cliente individual será encapsulado em uma estrutura que manterá um canal interno do tipo send chanbyte.

Este canal enfileirará as mensagens destinadas exclusivamente àquele cliente, atuando como um buffer elástico que absorve picos de tráfego de saída sem bloquear a rotina principal de roteamento do Hub ou outras goroutines clientes.

## Ver Também

- [[references/42-chat-research-report|42 Chat Research Report]] — MoC do relatório completo
- [[references/42-chat-platform-architecture|Platform Architecture]] — Visão arquitetural
- [[references/42-chat-engineering-requirements|Engineering Requirements]] — Requisitos técnicos
