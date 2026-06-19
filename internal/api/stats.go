package api

import (
	"database/sql"
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"

	"github.com/zeenyt__/42chat/internal/db"
)

// StatsHandler serve estatísticas de participação dos usuários.
type StatsHandler struct {
	queries *db.Queries
}

// NewStatsHandler cria o handler de estatísticas.
func NewStatsHandler(queries *db.Queries) *StatsHandler {
	return &StatsHandler{queries: queries}
}

// ServeHTTP responde GET /api/users/{id}/stats
func (h *StatsHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	idStr := chi.URLParam(r, "id")
	id, err := strconv.Atoi(idStr)
	if err != nil {
		http.Error(w, `{"error":"invalid user id"}`, http.StatusBadRequest)
		return
	}

	stats, err := h.queries.SelectUserStats(id)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, `{"error":"user not found"}`, http.StatusNotFound)
			return
		}
		http.Error(w, `{"error":"internal server error"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}
