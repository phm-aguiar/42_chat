package api

import (
	"encoding/json"
	"net/http"
	"strconv"
	"time"

	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

// MessagesHandler serve o histórico de mensagens.
type MessagesHandler struct {
	queries *db.Queries
}

// NewMessagesHandler cria o handler de mensagens.
func NewMessagesHandler(queries *db.Queries) *MessagesHandler {
	return &MessagesHandler{queries: queries}
}

// ServeHTTP responde GET /api/messages?before=&limit=50
func (h *MessagesHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	// Validar JWT
	claims := auth.GetClaims(r.Context())
	if claims == nil {
		http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized)
		return
	}
	_ = claims // claims disponível para futuras verificações

	// Parse query params
	limit := 50
	if l := r.URL.Query().Get("limit"); l != "" {
		if n, err := strconv.Atoi(l); err == nil && n > 0 && n <= 100 {
			limit = n
		}
	}

	var before time.Time
	if b := r.URL.Query().Get("before"); b != "" {
		if t, err := time.Parse(time.RFC3339, b); err == nil {
			before = t
		}
	}

	messages, err := h.queries.SelectRecentMessages(before, limit)
	if err != nil {
		http.Error(w, `{"error":"internal server error"}`, http.StatusInternalServerError)
		return
	}

	// Garantir que não retorna null, mas sim []
	if messages == nil {
		messages = []model.Message{}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(messages)
}
