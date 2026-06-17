package model

import "time"

// User representa um aluno da 42 autenticado no chat.
// ID vem da API 42 (INT fixo).
type User struct {
	ID          int       `json:"id" db:"id"`
	Login       string    `json:"login" db:"login"`
	ImageURL    string    `json:"image_url" db:"image_url"`
	CurrentHost string    `json:"current_host" db:"current_host"`
	Level       float64   `json:"level" db:"level"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
}
