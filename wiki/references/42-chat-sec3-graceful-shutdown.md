---
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
updated: "2026-06-15"
---
title: "42 Chat — Desligamento Gracioso (Graceful Shutdown) e Prevenção de Perda de Dados"
summary: "Seção 3/9 do relatório de arquitetura e viabilidade do 42 Chat. Desligamento Gracioso (Graceful Shutdown) e Prevenção de Perda de Dados."
---

# 42 Chat — Desligamento Gracioso (Graceful Shutdown) e Prevenção de Perda de Dados


A natureza persistente das conexões WebSocket introduz um desafio arquitetônico severo relacionado ao ciclo de vida da aplicação.

A interceptação correta de sinais do sistema operacional é vital para evitar perda de dados no buffer, corrupção do estado do banco de dados e problemas de disponibilidade temporária em um ambiente conteinerizado (como o gerenciado via Docker Compose) ou em ambientes orquestrados por Kubernetes, onde os desligamentos são ocorrências normais.

Quando o sistema de orquestração recebe um comando para atualizar a imagem do contêiner ou reiniciar o serviço, ele emite um sinal de término (como SIGINT acionado via Ctrl+C no terminal local, ou SIGTERM gerado pelo orquestrador para solicitar a interrupção ordenada).

A aplicação backend não pode simplesmente encerrar o processo abruptamente, sob o risco de deixar mensagens em memória que ainda não foram gravadas em disco.A sequência de engenharia projetada para o ciclo de encerramento do backend em Go (Graceful Shutdown) garante que a integridade transacional e a fluidez da experiência do usuário sejam mantidas.

O processo inicia-se com o bloqueio imediato de novas conexões.

O roteador HTTP principal encerra a escuta de novas portas chamando o método padrão http.Server.Shutdown(ctx), o que instrui o kernel a rejeitar novos pacotes SYN e novos handshakes de WebSocket com o erro "connection refused", impedindo a entrada de tráfego adicional.

Em seguida, o sinal de encerramento é propagado internamente para o Hub de chat através de um context.Context com cancelamento.O Hub, ao receber este sinal, interrompe seu laço principal de escuta.

Ele não encerra as conexões abruptamente, mas notifica todas as goroutines de clientes ainda abertas.

Para garantir a transparência para o frontend, o servidor envia intencionalmente um opcode de controle específico do padrão WebSocket (um CloseMessage amigável) a todos os clientes conectados.

Este pacote instrui o cliente (o microfrontend React) de que o encerramento foi intencional, acionando a interface de usuário para exibir um feedback visual claro de "Manutenção em andamento" ou "Reconectando", em oposição a um erro genérico de rede.Crucialmente, a persistência residual deve ser finalizada.

Quaisquer mensagens que estejam em trânsito no channel de envio, mas que ainda não tenham sido confirmadas pela transação do banco de dados PostgreSQL, são capturadas e enviadas em lote por uma goroutine final que opera fora do contexto cancelado, garantindo a atomicidade e consistência imutável dos logs de auditoria requeridos pelo Bocal.

O processo aguardará ativamente essas finalizações utilizando um sync.WaitGroup associado a um timeout de salvaguarda (ex: 30 segundos).

Finalmente, o processo de liberação de recursos é invocado, onde a pool de conexões ativas com o PostgreSQL é encerrada ordenadamente através da chamada db.Close(), permitindo que o sistema operacional recupere a memória alocada e o processo principal do Go termine de forma asséptica com código de saída zero.

## Ver Também

- [[references/42-chat-research-report|42 Chat Research Report]] — MoC do relatório completo
- [[references/42-chat-platform-architecture|Platform Architecture]] — Visão arquitetural
- [[references/42-chat-engineering-requirements|Engineering Requirements]] — Requisitos técnicos
