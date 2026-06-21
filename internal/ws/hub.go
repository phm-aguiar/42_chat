package ws

import (
	"encoding/json"
	"log"
	"sync"
	"time"

	"github.com/zeenyt__/42chat/internal/db"
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

	// Debounce para evento user_stats_changed (Feature 101).
	debounceTimers map[int]*time.Timer
	debounceMu     sync.Mutex

	queries *db.Queries
}

// NewHub cria um novo Hub vazio.
// queries pode ser nil para testes que não dependem de consultas ao banco.
func NewHub(queries *db.Queries) *Hub {
	return &Hub{
		clients:        make(map[*Client]bool),
		debounceTimers: make(map[int]*time.Timer),
		queries:        queries,
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

// BroadcastUserStatsChanged agenda um broadcast de user_stats_changed com debounce de 2s.
// Múltiplas chamadas para o mesmo userID dentro de 2s geram um único broadcast.
func (h *Hub) BroadcastUserStatsChanged(userID int) {
	h.debounceMu.Lock()
	defer h.debounceMu.Unlock()

	// Cancela timer anterior se existir (reset do debounce)
	if old, ok := h.debounceTimers[userID]; ok {
		old.Stop()
	}

	h.debounceTimers[userID] = time.AfterFunc(2*time.Second, func() {
		// Remove o timer do mapa após disparo
		h.debounceMu.Lock()
		delete(h.debounceTimers, userID)
		h.debounceMu.Unlock()

		msg := h.buildStatsPayload(userID)
		if msg != nil {
			h.Broadcast(msg)
		}
	})
}

// buildStatsPayload consulta o banco e monta o WSMessage de user_stats_changed.
// Retorna nil se queries for nil (modo teste) ou se a consulta falhar.
func (h *Hub) buildStatsPayload(userID int) *model.WSMessage {
	if h.queries == nil {
		return nil
	}

	stats, err := h.queries.SelectUserStats(userID)
	if err != nil {
		log.Printf("[ws] erro ao consultar stats do user %d: %v", userID, err)
		return nil
	}

	// Serializa as estatísticas como JSON no campo Content
	payload := map[string]interface{}{
		"user_id":        stats.UserID,
		"total_messages": stats.TotalMessages,
		"active_rooms":   stats.ActiveRooms,
		"tier":           stats.Tier,
	}
	contentBytes, err := json.Marshal(payload)
	if err != nil {
		log.Printf("[ws] erro ao serializar stats do user %d: %v", userID, err)
		return nil
	}

	return &model.WSMessage{
		Type:    "user_stats_changed",
		UserID:  stats.UserID,
		Login:   stats.Login,
		Content: string(contentBytes),
	}
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
