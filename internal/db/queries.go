package db

import (
	"database/sql"
	"time"

	"github.com/zeenyt__/42chat/internal/model"
)

// Queries encapsula todas as queries parametrizadas do sistema.
type Queries struct {
	db *sql.DB
}

// NewQueries cria um repositório de queries.
func NewQueries(db *sql.DB) *Queries {
	return &Queries{db: db}
}

// UpsertUser insere ou atualiza um usuário (OAuth2 callback).
// Retorna o ID do usuário.
func (q *Queries) UpsertUser(u *model.User) (int, error) {
	const query = `
		INSERT INTO users (id, login, image_url, current_host, level, created_at)
		VALUES ($1, $2, $3, $4, $5, $6)
		ON CONFLICT (id) DO UPDATE SET
			login = EXCLUDED.login,
			image_url = EXCLUDED.image_url,
			current_host = EXCLUDED.current_host,
			level = EXCLUDED.level
		RETURNING id
	`
	var id int
	err := q.db.QueryRow(query,
		u.ID, u.Login, u.ImageURL, u.CurrentHost, u.Level, u.CreatedAt,
	).Scan(&id)
	return id, err
}

// SelectUserByID busca um usuário pelo ID da 42.
func (q *Queries) SelectUserByID(id int) (*model.User, error) {
	const query = `SELECT id, login, image_url, current_host, level, created_at FROM users WHERE id = $1`
	u := &model.User{}
	err := q.db.QueryRow(query, id).Scan(
		&u.ID, &u.Login, &u.ImageURL, &u.CurrentHost, &u.Level, &u.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return u, nil
}

// InsertMessage insere uma nova mensagem. Retorna o Message completo (com UUID gerado).
func (q *Queries) InsertMessage(userID int, content string) (*model.Message, error) {
	const query = `
		INSERT INTO messages (user_id, content, created_at)
		VALUES ($1, $2, NOW())
		RETURNING id, created_at
	`
	m := &model.Message{
		UserID:  userID,
		Content: content,
	}
	err := q.db.QueryRow(query, userID, content).Scan(&m.ID, &m.CreatedAt)
	if err != nil {
		return nil, err
	}
	return m, nil
}

// SelectRecentMessages busca as últimas N mensagens antes de um timestamp.
// Se before for zero-value, busca as mais recentes.
// Exclui soft-deleted messages.
func (q *Queries) SelectRecentMessages(before time.Time, limit int) ([]model.Message, error) {
	var query string
	var rows *sql.Rows
	var err error

	if before.IsZero() {
		query = `
			SELECT m.id, m.user_id, u.login, u.image_url,
				   m.content, m.created_at
			FROM messages m
			JOIN users u ON u.id = m.user_id
			WHERE m.deleted_at IS NULL
			ORDER BY m.created_at DESC
			LIMIT $1
		`
		rows, err = q.db.Query(query, limit)
	} else {
		query = `
			SELECT m.id, m.user_id, u.login, u.image_url,
				   m.content, m.created_at
			FROM messages m
			JOIN users u ON u.id = m.user_id
			WHERE m.deleted_at IS NULL AND m.created_at < $1
			ORDER BY m.created_at DESC
			LIMIT $2
		`
		rows, err = q.db.Query(query, before, limit)
	}

	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var messages []model.Message
	for rows.Next() {
		var msg model.Message
		if err := rows.Scan(&msg.ID, &msg.UserID, &msg.Login, &msg.ImageURL,
			&msg.Content, &msg.CreatedAt); err != nil {
			return nil, err
		}
		messages = append(messages, msg)
	}
	return messages, rows.Err()
}

// SoftDeleteMessage marca uma mensagem como deletada (soft delete).
func (q *Queries) SoftDeleteMessage(id string) error {
	const query = `UPDATE messages SET deleted_at = NOW() WHERE id = $1`
	_, err := q.db.Exec(query, id)
	return err
}

// SelectUserByLogin busca um usuário pelo login da 42.
func (q *Queries) SelectUserByLogin(login string) (*model.User, error) {
	const query = `SELECT id, login, image_url, current_host, level, created_at FROM users WHERE login = $1`
	u := &model.User{}
	err := q.db.QueryRow(query, login).Scan(
		&u.ID, &u.Login, &u.ImageURL, &u.CurrentHost, &u.Level, &u.CreatedAt,
	)
	if err != nil {
		return nil, err
	}
	return u, nil
}
