package model

import "time"

// Board representa uma categoria/canal do fórum (ex: /tech, /projects).
// Inspirado no schema de boards do jschan, adaptado para PostgreSQL + identidades reais.
type Board struct {
	ID          string    `json:"id" db:"id"`                       // UUIDv7
	Slug        string    `json:"slug" db:"slug"`                   // URI única (ex: "tech")
	Name        string    `json:"name" db:"name"`                   // Nome humano
	Description string    `json:"description" db:"description"`     // Descrição
	OwnerID     int       `json:"owner_id" db:"owner_id"`           // Dono (users.id — INT da API 42)
	SFW         bool      `json:"sfw" db:"sfw"`
	Theme       string    `json:"theme" db:"theme"`
	Language    string    `json:"language" db:"language"`
	IsLocked    bool      `json:"is_locked" db:"is_locked"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`

	// Joined fields
	OwnerLogin  string `json:"owner_login,omitempty" db:"-"`
}

// BoardStaff representa um membro da staff de um board.
type BoardStaff struct {
	BoardID string    `json:"board_id" db:"board_id"`       // UUIDv7
	UserID  int       `json:"user_id" db:"user_id"`         // users.id (INT)
	Role    string    `json:"role" db:"role"`               // "owner" | "mod" | "admin"
	AddedAt time.Time `json:"added_at" db:"added_at"`
	AddedBy int       `json:"added_by" db:"added_by"`       // users.id (INT)
}

// StaffRoles define os papéis disponíveis para staff de board.
var StaffRoles = struct {
	Owner string
	Mod   string
	Admin string
}{
	Owner: "owner",
	Mod:   "mod",
	Admin: "admin",
}

// ReservedBoardSlugs são slugs reservados que não podem ser usados como board.
var ReservedBoardSlugs = map[string]bool{
	"admin":    true,
	"api":      true,
	"forum":    true,
	"chat":     true,
	"settings": true,
	"all":      true,
	"new":      true,
}
