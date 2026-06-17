package model

import "time"

// Message representa uma mensagem no chat.
// ID é UUID v4 gerado pelo PostgreSQL.
// Content tem CHECK constraint ≤5000 no banco.
// DeletedAt é soft delete (nunca hard delete).
type Message struct {
	ID        string     `json:"id" db:"id"`
	UserID    int        `json:"user_id" db:"user_id"`
	Login     string     `json:"login,omitempty" db:"-"`
	ImageURL  string     `json:"image_url,omitempty" db:"-"`
	Content   string     `json:"content" db:"content"`
	CreatedAt time.Time  `json:"created_at" db:"created_at"`
	DeletedAt *time.Time `json:"deleted_at,omitempty" db:"deleted_at"`
}

// WSMessage é o payload do WebSocket (tanto inbound quanto outbound).
type WSMessage struct {
	Type      string `json:"type"`                 // "message" | "system"
	ID        string `json:"id,omitempty"`         // UUID da mensagem (outbound)
	UserID    int    `json:"user_id,omitempty"`    // ID do autor (outbound)
	Login     string `json:"login,omitempty"`      // Login do autor (outbound)
	ImageURL  string `json:"image_url,omitempty"`  // Foto do autor (outbound)
	Content   string `json:"content,omitempty"`    // Texto da mensagem
	Token     string `json:"token,omitempty"`      // JWT (inbound no connect / primeira msg)
	CreatedAt string `json:"created_at,omitempty"` // ISO8601 (outbound)
}
