package auth

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

// DevLoginHandler é um endpoint exclusivo para desenvolvimento local.
// Aceita ?login=marvin, cria/atualiza um mock user e retorna JWT.
// Só deve ser usado com DEV_MODE=true.
type DevLoginHandler struct {
	jwt     *JWTManager
	queries *db.Queries
}

func NewDevLoginHandler(jwt *JWTManager, queries *db.Queries) *DevLoginHandler {
	return &DevLoginHandler{jwt: jwt, queries: queries}
}

func (h *DevLoginHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	login := r.URL.Query().Get("login")
	if login == "" {
		login = "marvin"
	}

	// Mock user — o mesmo ID toda vez (consistente pra dev)
	user := &model.User{
		ID:          42,
		Login:       login,
		ImageURL:    "https://cdn.intra.42.fr/users/default.png",
		CurrentHost: "e1z2m3",
		Level:       8.42,
	}

	if _, err := h.queries.UpsertUser(user); err != nil {
		log.Printf("[dev-login] upsert user error: %v", err)
		http.Error(w, `{"error":"failed to upsert user"}`, http.StatusInternalServerError)
		return
	}

	token, err := h.jwt.GenerateToken(user.ID, user.Login)
	if err != nil {
		log.Printf("[dev-login] JWT error: %v", err)
		http.Error(w, `{"error":"token generation failed"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"token": token,
		"user": map[string]interface{}{
			"id":        user.ID,
			"login":     user.Login,
			"image_url": user.ImageURL,
		},
	})
}
