package ws

import (
	"encoding/json"
	"log"
	"net/http"
	"time"

	"github.com/gorilla/websocket"

	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

const (
	// Tempo máximo para escrever uma mensagem no WS.
	writeWait = 10 * time.Second
	// Tempo máximo para ler o próximo pong.
	pongWait = 60 * time.Second
	// Intervalo de ping (deve ser < pongWait).
	pingPeriod = 30 * time.Second
	// Tamanho máximo de mensagem lida (5KB + overhead).
	maxMessageSize = 6144
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // MVP: aceita qualquer origem (dev local)
	},
}

// Handler gerencia upgrade HTTP → WebSocket e pumps de leitura/escrita.
type Handler struct {
	hub        *Hub
	jwtManager *auth.JWTManager
	queries    *db.Queries
}

// NewHandler cria um handler WebSocket.
func NewHandler(hub *Hub, jwtManager *auth.JWTManager, queries *db.Queries) *Handler {
	return &Handler{
		hub:        hub,
		jwtManager: jwtManager,
		queries:    queries,
	}
}

// ServeHTTP faz o upgrade da conexão HTTP para WebSocket.
func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// 1. Validar JWT do query param ou header
	tokenStr := r.URL.Query().Get("token")
	if tokenStr == "" {
		// Fallback: header Authorization
		tokenStr = r.Header.Get("Sec-WebSocket-Protocol")
	}
	if tokenStr == "" {
		http.Error(w, `{"error":"missing token"}`, http.StatusUnauthorized)
		return
	}

	claims, err := h.jwtManager.ValidateToken(tokenStr)
	if err != nil {
		http.Error(w, `{"error":"invalid token"}`, http.StatusUnauthorized)
		return
	}

	// 2. Upgrade HTTP → WebSocket
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("[ws] upgrade error: %v", err)
		return
	}

	// 3. Criar client e registrar no Hub
	client := &Client{
		UserID: claims.UserID,
		Login:  claims.Login,
		Send:   make(chan []byte, 256),
		Hub:    h.hub,
	}

	h.hub.Connect(client)

	// 4. Iniciar pumps (read/write goroutines)
	go h.writePump(client, conn)
	go h.readPump(client, conn)
}

// readPump lê mensagens do WebSocket e faz broadcast.
func (h *Handler) readPump(client *Client, conn *websocket.Conn) {
	defer func() {
		h.hub.Disconnect(client)
		conn.Close()
	}()

	conn.SetReadLimit(maxMessageSize)
	conn.SetReadDeadline(time.Now().Add(pongWait))
	conn.SetPongHandler(func(string) error {
		conn.SetReadDeadline(time.Now().Add(pongWait))
		return nil
	})

	for {
		_, rawMsg, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err,
				websocket.CloseGoingAway, websocket.CloseNormalClosure) {
				log.Printf("[ws] read error: %v", err)
			}
			break
		}

		// Decodificar mensagem do cliente
		var inbound model.WSMessage
		if err := json.Unmarshal(rawMsg, &inbound); err != nil {
			log.Printf("[ws] decode error: %v", err)
			continue
		}

		if inbound.Type != "message" || inbound.Content == "" {
			continue
		}

		// Validar tamanho no servidor também
		if len(inbound.Content) > 5000 {
			continue
		}

		// Persistir no banco
		msg, err := h.queries.InsertMessage(client.UserID, inbound.Content)
		if err != nil {
			log.Printf("[ws] insert message error: %v", err)
			continue
		}

		// Dispara broadcast de estatísticas do usuário (debounce 2s)
		h.hub.BroadcastUserStatsChanged(client.UserID)

		// Enriquecer com dados do autor para o broadcast
		outbound := &model.WSMessage{
			Type:      "message",
			ID:        msg.ID,
			UserID:    client.UserID,
			Login:     client.Login,
			Content:   inbound.Content,
			CreatedAt: msg.CreatedAt.Format(time.RFC3339),
		}

		h.hub.Broadcast(outbound)
	}
}

// writePump escreve mensagens do canal Send para o WebSocket.
func (h *Handler) writePump(client *Client, conn *websocket.Conn) {
	ticker := time.NewTicker(pingPeriod)
	defer func() {
		ticker.Stop()
		conn.Close()
	}()

	for {
		select {
		case message, ok := <-client.Send:
			conn.SetWriteDeadline(time.Now().Add(writeWait))
			if !ok {
				// Hub fechou o canal
				conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			if err := conn.WriteMessage(websocket.TextMessage, message); err != nil {
				log.Printf("[ws] write error: %v", err)
				return
			}

		case <-ticker.C:
			conn.SetWriteDeadline(time.Now().Add(writeWait))
			if err := conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}
