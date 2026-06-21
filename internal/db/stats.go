package db

import (
	"time"
)

// UserStats representa estatísticas agregadas de participação de um usuário.
// Alimenta o endpoint GET /api/users/{id}/stats (Feature 101).
type UserStats struct {
	UserID        int       `json:"user_id"`
	Login         string    `json:"login"`
	AvatarURL     string    `json:"avatar_url"`
	TotalMessages int       `json:"total_messages"`
	ActiveRooms   int       `json:"active_rooms"`
	Tier          string    `json:"tier"`
	MemberSince   time.Time `json:"member_since"`
}

// ComputeTier retorna o tier de participação baseado no total de mensagens.
// Thresholds: 0 → novato, 1-50 → iniciante, 51-200 → participante, 201+ → veterano.
func ComputeTier(totalMessages int) string {
	switch {
	case totalMessages == 0:
		return "novato"
	case totalMessages <= 50:
		return "iniciante"
	case totalMessages <= 200:
		return "participante"
	default:
		return "veterano"
	}
}

// SelectUserStats busca estatísticas agregadas de um usuário na tabela messages.
// Usa LEFT JOIN para retornar stats zerados para usuários sem mensagens.
// Exclui mensagens soft-deleted (deleted_at IS NULL).
// active_rooms = 1 se há mensagens, 0 caso contrário (chat single-room atual).
func (q *Queries) SelectUserStats(userID int) (*UserStats, error) {
	const query = `
		SELECT
			u.id,
			u.login,
			u.image_url,
			COUNT(m.id) AS total_messages,
			u.created_at
		FROM users u
		LEFT JOIN messages m ON m.user_id = u.id AND m.deleted_at IS NULL
		WHERE u.id = $1
		GROUP BY u.id, u.login, u.image_url, u.created_at
	`

	stats := &UserStats{}
	err := q.db.QueryRow(query, userID).Scan(
		&stats.UserID,
		&stats.Login,
		&stats.AvatarURL,
		&stats.TotalMessages,
		&stats.MemberSince,
	)
	if err != nil {
		return nil, err
	}

	if stats.TotalMessages > 0 {
		stats.ActiveRooms = 1
	}
	stats.Tier = ComputeTier(stats.TotalMessages)
	return stats, nil
}
