package ws

import (
	"encoding/json"
	"log"
	"sync"

	"github.com/zeenyt__/42chat/internal/model"
)

// Client representa uma conexão WebSocket ativa.
type Client struct {
	UserID int
	Login  string
	Send   chan []byte
	Hub    *Hub
}

// Hub gerencia todas as conexões WebSocket ativas.
// Modelo híbrido: sync.RWMutex no mapa + send chan como buffer de saída.
type Hub struct {
	mu      sync.RWMutex
	clients map[*Client]bool
}

// NewHub cria um novo Hub vazio.
func NewHub() *Hub {
	return &Hub{
		clients: make(map[*Client]bool),
	}
}

// Connect registra um novo client no Hub.
// Retorna uma mensagem de sistema "join" para broadcast.
func (h *Hub) Connect(client *Client) {
	h.mu.Lock()
	h.clients[client] = true
	count := len(h.clients)
	h.mu.Unlock()

	log.Printf("[ws] client conectado: %s (total: %d)", client.Login, count)

	// Broadcast de entrada
	h.BroadcastSystem("join", client.Login)
}

// Disconnect remove um client do Hub e fecha seu canal de envio.
func (h *Hub) Disconnect(client *Client) {
	h.mu.Lock()
	if _, ok := h.clients[client]; ok {
		delete(h.clients, client)
		close(client.Send)
	}
	count := len(h.clients)
	h.mu.Unlock()

	log.Printf("[ws] client desconectado: %s (total: %d)", client.Login, count)

	// Broadcast de saída
	h.BroadcastSystem("leave", client.Login)
}

// Broadcast envia uma mensagem para todos os clients conectados.
// Usa RLock para leitura simultânea do mapa.
func (h *Hub) Broadcast(msg *model.WSMessage) {
	data := mustMarshal(msg)

	h.mu.RLock()
	defer h.mu.RUnlock()

	for client := range h.clients {
		select {
		case client.Send <- data:
			// Enviado com sucesso
		default:
			// Buffer do client cheio, descarta mensagem para este client
			log.Printf("[ws] descartando msg para %s (buffer cheio)", client.Login)
		}
	}
}

// BroadcastSystem envia uma mensagem de sistema para todos os clients.
func (h *Hub) BroadcastSystem(sysType string, login string) {
	msg := &model.WSMessage{
		Type:  "system",
		Login: login,
	}
	// Sobrescreve o tipo como "system" com subtype
	msg.Content = sysType
	h.Broadcast(msg)
}

// Shutdown notifica todos os clients sobre shutdown e fecha o Hub.
func (h *Hub) Shutdown() {
	h.mu.RLock()
	defer h.mu.RUnlock()

	shutdownMsg := &model.WSMessage{
		Type:    "system",
		Content: "shutdown",
	}

	data := mustMarshal(shutdownMsg)
	for client := range h.clients {
		select {
		case client.Send <- data:
		default:
		}
	}
}

// ConnectionCount retorna o número de conexões ativas (para /metrics).
func (h *Hub) ConnectionCount() int {
	h.mu.RLock()
	defer h.mu.RUnlock()
	return len(h.clients)
}

// mustMarshal serializa para JSON. Panic em caso de erro (nunca deve acontecer com WSMessage).
func mustMarshal(v interface{}) []byte {
	data, err := json.Marshal(v)
	if err != nil {
		log.Printf("[ws] ERRO serialização: %v", err)
		return []byte(`{"type":"error","content":"internal serialization error"}`)
	}
	return data
}
