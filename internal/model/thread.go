package model

import "time"

// Thread representa um tópico dentro de um board (equivalente ao OP post de um chan).
type Thread struct {
	ID         string    `json:"id" db:"id"`                     // UUIDv7
	BoardID    string    `json:"board_id" db:"board_id"`         // UUIDv7
	AuthorID   int       `json:"author_id" db:"author_id"`       // users.id (INT)
	Title      string    `json:"title" db:"title"`
	Content    string    `json:"content" db:"content"`
	IsPinned   bool      `json:"is_pinned" db:"is_pinned"`
	IsLocked   bool      `json:"is_locked" db:"is_locked"`
	PostCount  int       `json:"post_count" db:"post_count"`
	LastPostAt time.Time `json:"last_post_at" db:"last_post_at"`
	CreatedAt  time.Time `json:"created_at" db:"created_at"`
	UpdatedAt  time.Time `json:"updated_at" db:"updated_at"`
	DeletedAt  *time.Time `json:"deleted_at,omitempty" db:"deleted_at"`

	// Joined fields (preenchidos nas queries com JOIN)
	AuthorLogin string `json:"author_login,omitempty" db:"-"`
	AuthorImage string `json:"author_image,omitempty" db:"-"`
	BoardSlug   string `json:"board_slug,omitempty" db:"-"`
	BoardName   string `json:"board_name,omitempty" db:"-"`
}

// Post representa uma resposta dentro de uma thread (reply do chan).
type Post struct {
	ID        string     `json:"id" db:"id"`                     // UUIDv7
	ThreadID  string     `json:"thread_id" db:"thread_id"`       // UUIDv7
	AuthorID  int        `json:"author_id" db:"author_id"`       // users.id (INT)
	Content   string     `json:"content" db:"content"`
	ReplyTo   *string    `json:"reply_to,omitempty" db:"reply_to"` // UUIDv7 (nullable)
	CreatedAt time.Time  `json:"created_at" db:"created_at"`
	DeletedAt *time.Time `json:"deleted_at,omitempty" db:"deleted_at"`

	// Joined fields
	AuthorLogin string `json:"author_login,omitempty" db:"-"`
	AuthorImage string `json:"author_image,omitempty" db:"-"`
}
