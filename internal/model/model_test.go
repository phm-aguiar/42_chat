package model

import (
	"encoding/json"
	"testing"
	"time"
)

func TestUser_Marshaling(t *testing.T) {
	now := time.Now().UTC().Truncate(time.Second)
	u := User{
		ID:          42,
		Login:       "marvin",
		ImageURL:    "https://cdn.42.fr/marvin.jpg",
		CurrentHost: "e1z2m4",
		Level:       9.87,
		CreatedAt:   now,
	}

	data, err := json.Marshal(u)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var decoded User
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}

	if decoded.ID != u.ID {
		t.Errorf("ID: got %d, want %d", decoded.ID, u.ID)
	}
	if decoded.Login != u.Login {
		t.Errorf("Login: got %s, want %s", decoded.Login, u.Login)
	}
	if decoded.Level != u.Level {
		t.Errorf("Level: got %f, want %f", decoded.Level, u.Level)
	}
}

func TestMessage_Marshaling(t *testing.T) {
	now := time.Now().UTC()
	m := Message{
		ID:        "550e8400-e29b-41d4-a716-446655440000",
		UserID:    42,
		Content:   "Hello, 42!",
		CreatedAt: now,
	}

	data, err := json.Marshal(m)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var decoded Message
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}

	if decoded.ID != m.ID {
		t.Errorf("ID: got %s, want %s", decoded.ID, m.ID)
	}
	if decoded.UserID != m.UserID {
		t.Errorf("UserID: got %d, want %d", decoded.UserID, m.UserID)
	}
}

func TestWSMessage_TypeRouting(t *testing.T) {
	tests := []struct {
		name string
		msg  WSMessage
		want string
	}{
		{
			name: "message type",
			msg:  WSMessage{Type: "message", Content: "hello"},
			want: "message",
		},
		{
			name: "system type join",
			msg:  WSMessage{Type: "system", Login: "marvin"},
			want: "system",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			data, err := json.Marshal(tt.msg)
			if err != nil {
				t.Fatalf("marshal: %v", err)
			}

			var decoded WSMessage
			if err := json.Unmarshal(data, &decoded); err != nil {
				t.Fatalf("unmarshal: %v", err)
			}

			if decoded.Type != tt.want {
				t.Errorf("Type: got %s, want %s", decoded.Type, tt.want)
			}
		})
	}
}

func TestMessage_SoftDelete(t *testing.T) {
	now := time.Now().UTC()
	m := Message{
		ID:        "msg-1",
		DeletedAt: &now,
	}

	data, err := json.Marshal(m)
	if err != nil {
		t.Fatalf("marshal: %v", err)
	}

	var decoded Message
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatalf("unmarshal: %v", err)
	}

	if decoded.DeletedAt == nil {
		t.Error("DeletedAt should not be nil after marshal/unmarshal")
	}
}
