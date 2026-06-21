package api

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"

	"github.com/zeenyt__/42chat/internal/db"
)

// UsersHandler serve informações de perfil público dos usuários.
type UsersHandler struct {
	queries *db.Queries
}

// NewUsersHandler cria o handler de usuários.
func NewUsersHandler(queries *db.Queries) *UsersHandler {
	return &UsersHandler{queries: queries}
}

// ServeHTTP responde GET /api/users/{id}
func (h *UsersHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	idStr := chi.URLParam(r, "id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, `{"error":"invalid user id"}`, http.StatusBadRequest)
		return
	}

	user, err := h.queries.SelectUserByID(id)
	if err != nil {
		http.Error(w, `{"error":"user not found"}`, http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(user)
}
