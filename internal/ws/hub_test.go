package ws

import (
	"encoding/json"
	"fmt"
	"sync"
	"testing"

	"github.com/zeenyt__/42chat/internal/model"
)

// drainMessages consome todas as mensagens pendentes do canal.
func drainMessages(ch <-chan []byte) {
	for {
		select {
		case <-ch:
		default:
			return
		}
	}
}

// TestHubBroadcast verifica que o broadcast entrega a mensagem para todos os clients.
func TestHubBroadcast(t *testing.T) {
	hub := NewHub(nil)
	n := 5
	clients := make([]*Client, n)

	for i := 0; i < n; i++ {
		clients[i] = &Client{
			UserID: i + 1,
			Login:  fmt.Sprintf("user%d", i+1),
			Send:   make(chan []byte, 256),
			Hub:    hub,
		}
		hub.Connect(clients[i])
	}

	// Drenar mensagens de "join" do Connect
	// Cliente i recebe joins dos clientes i..n-1 = n-i mensagens
	for i, c := range clients {
		for j := 0; j < n-i; j++ {
			<-c.Send
		}
	}

	// Broadcast de uma mensagem real
	msg := &model.WSMessage{
		Type:    "message",
		ID:      "msg-001",
		UserID:  1,
		Login:   "user1",
		Content: "hello everyone",
	}
	hub.Broadcast(msg)

	// Verifica que todos os clients receberam
	for i, c := range clients {
		select {
		case data := <-c.Send:
			var received model.WSMessage
			if err := json.Unmarshal(data, &received); err != nil {
				t.Fatalf("client %d: unmarshal error: %v", i, err)
			}
			if received.Type != "message" {
				t.Errorf("client %d: type = %q, want %q", i, received.Type, "message")
			}
			if received.Content != "hello everyone" {
				t.Errorf("client %d: content = %q, want %q", i, received.Content, "hello everyone")
			}
		default:
			t.Errorf("client %d: no message received", i)
		}
	}

	// Não deve haver mensagens extras
	for i, c := range clients {
		select {
		case extra := <-c.Send:
			t.Errorf("client %d: unexpected extra message: %s", i, string(extra))
		default:
		}
	}
}

// TestHubConnectDisconnect verifica que Connect adiciona e Disconnect remove o client.
func TestHubConnectDisconnect(t *testing.T) {
	hub := NewHub(nil)

	if count := hub.ConnectionCount(); count != 0 {
		t.Fatalf("initial count = %d, want 0", count)
	}

	client := &Client{
		UserID: 42,
		Login:  "testuser",
		Send:   make(chan []byte, 256),
		Hub:    hub,
	}

	// Connect
	hub.Connect(client)
	if count := hub.ConnectionCount(); count != 1 {
		t.Fatalf("count after connect = %d, want 1", count)
	}

	// Drenar mensagem de join
	<-client.Send

	// Conectar segundo client
	client2 := &Client{
		UserID: 99,
		Login:  "user2",
		Send:   make(chan []byte, 256),
		Hub:    hub,
	}
	hub.Connect(client2)
	if count := hub.ConnectionCount(); count != 2 {
		t.Fatalf("count after second connect = %d, want 2", count)
	}
	drainMessages(client.Send)
	drainMessages(client2.Send)

	// Disconnect
	hub.Disconnect(client)
	if count := hub.ConnectionCount(); count != 1 {
		t.Fatalf("count after disconnect = %d, want 1", count)
	}

	// Canal do client desconectado deve estar fechado
	_, open := <-client.Send
	if open {
		t.Error("client.Send should be closed after Disconnect")
	}

	// Segundo client ainda conectado
	if count := hub.ConnectionCount(); count != 1 {
		t.Fatalf("count = %d, want 1", count)
	}

	// Disconnect do segundo
	hub.Disconnect(client2)
	if count := hub.ConnectionCount(); count != 0 {
		t.Fatalf("count after second disconnect = %d, want 0", count)
	}

	// Disconnect duplo não deve panificar
	hub.Disconnect(client)
}

// TestHubShutdown verifica que Shutdown envia mensagem de sistema para todos os clients.
func TestHubShutdown(t *testing.T) {
	hub := NewHub(nil)
	n := 3
	clients := make([]*Client, n)

	for i := 0; i < n; i++ {
		clients[i] = &Client{
			UserID: i + 1,
			Login:  fmt.Sprintf("user%d", i+1),
			Send:   make(chan []byte, 256),
			Hub:    hub,
		}
		hub.Connect(clients[i])
	}

	// Drenar mensagens de join
	// Cliente i recebe joins dos clientes i..n-1 = n-i mensagens
	for i, c := range clients {
		for j := 0; j < n-i; j++ {
			<-c.Send
		}
	}

	// Shutdown
	hub.Shutdown()

	// Verificar que cada client recebeu a mensagem de shutdown
	for i, c := range clients {
		select {
		case data := <-c.Send:
			var msg model.WSMessage
			if err := json.Unmarshal(data, &msg); err != nil {
				t.Fatalf("client %d: unmarshal error: %v", i, err)
			}
			if msg.Type != "system" {
				t.Errorf("client %d: type = %q, want %q", i, msg.Type, "system")
			}
			if msg.Content != "shutdown" {
				t.Errorf("client %d: content = %q, want %q", i, msg.Content, "shutdown")
			}
		default:
			t.Errorf("client %d: no shutdown message received", i)
		}
	}

	// Shutdown não remove clients do mapa (só notifica)
	if count := hub.ConnectionCount(); count != n {
		t.Errorf("count after shutdown = %d, want %d (shutdown only notifies, does not remove)", count, n)
	}
}

// TestHubBroadcastConcurrent verifica thread-safety do broadcast concorrente.
func TestHubBroadcastConcurrent(t *testing.T) {
	hub := NewHub(nil)
	n := 10
	broadcasters := 4
	iterations := 100
	totalMessages := broadcasters * iterations

	clients := make([]*Client, n)

	for i := 0; i < n; i++ {
		clients[i] = &Client{
			UserID: i + 1,
			Login:  fmt.Sprintf("user%d", i+1),
			Send:   make(chan []byte, 1024),
			Hub:    hub,
		}
		hub.Connect(clients[i])
	}

	// Drenar joins
	for i, c := range clients {
		for j := 0; j < n-i; j++ {
			<-c.Send
		}
	}

	var wg sync.WaitGroup

	// Consumidores — cada um lê totalMessages e encerra
	received := make([]int, n)
	for i := 0; i < n; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			count := 0
			for range clients[idx].Send {
				count++
				if count >= totalMessages {
					received[idx] = count
					return
				}
			}
			received[idx] = count
		}(i)
	}

	// Broadcasts concorrentes
	for k := 0; k < broadcasters; k++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			for i := 0; i < iterations; i++ {
				hub.Broadcast(&model.WSMessage{
					Type:    "message",
					Content: fmt.Sprintf("msg-%d-%d", id, i),
				})
			}
		}(k)
	}

	wg.Wait()

	for i := 0; i < n; i++ {
		if received[i] < totalMessages {
			t.Errorf("client %d: received %d messages, want >= %d", i, received[i], totalMessages)
		}
	}
}
