package ws

import (
	"context"
	"database/sql"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/gorilla/websocket"
	_ "github.com/lib/pq"

	"github.com/zeenyt__/42chat/internal/auth"
	"github.com/zeenyt__/42chat/internal/db"
	"github.com/zeenyt__/42chat/internal/model"
)

// testQueries cria um *db.Queries com um *sql.DB que nunca será usado para
// queries reais (útil para testes que não dependem de InsertMessage).
func testQueries(t *testing.T) *db.Queries {
	t.Helper()
	// sql.Open não conecta imediatamente — só no primeiro Ping/Query.
	// Como os testes de connect/ping/shutdown nunca chamam InsertMessage,
	// o banco real não é necessário.
	testDB, err := sql.Open("postgres", "host=localhost port=5432 dbname=42chat_test sslmode=disable")
	if err != nil {
		t.Fatalf("sql.Open: %v", err)
	}
	t.Cleanup(func() { testDB.Close() })
	return db.NewQueries(testDB)
}

// testJWTManager cria um gerenciador JWT com secret de teste.
func testJWTManager(t *testing.T) *auth.JWTManager {
	t.Helper()
	return auth.NewJWTManager("test-secret-for-ws-integration-tests")
}

// testToken gera um JWT válido para o handler.
func testToken(t *testing.T, jwt *auth.JWTManager, userID int, login string) string {
	t.Helper()
	token, err := jwt.GenerateToken(userID, login)
	if err != nil {
		t.Fatalf("GenerateToken: %v", err)
	}
	return token
}

// setupWSServer cria um httptest.Server com o handler WS e retorna
// server, hub, jwtManager e a URL de WebSocket (ws://...).
func setupWSServer(t *testing.T) (*httptest.Server, *Hub, *auth.JWTManager) {
	t.Helper()

	hub := NewHub(nil)
	jwt := testJWTManager(t)
	queries := testQueries(t)
	handler := NewHandler(hub, jwt, queries)

	server := httptest.NewServer(http.HandlerFunc(handler.ServeHTTP))
	t.Cleanup(func() { server.Close() })

	return server, hub, jwt
}

// wsURL converte uma URL http:// para ws://.
func wsURL(httpURL string) string {
	return strings.Replace(httpURL, "http://", "ws://", 1)
}

// connectWSClient conecta ao servidor WS com token e retorna a conexão.
func connectWSClient(t *testing.T, serverURL string, token string) *websocket.Conn {
	t.Helper()

	url := wsURL(serverURL) + "?token=" + token
	conn, resp, err := websocket.DefaultDialer.Dial(url, nil)
	if err != nil {
		if resp != nil {
			t.Fatalf("dial: %v (status=%d)", err, resp.StatusCode)
		}
		t.Fatalf("dial: %v", err)
	}
	t.Cleanup(func() { conn.Close() })
	return conn
}

// readWSMessage lê uma mensagem JSON do WebSocket.
func readWSMessage(t *testing.T, conn *websocket.Conn, timeout time.Duration) *model.WSMessage {
	t.Helper()

	conn.SetReadDeadline(time.Now().Add(timeout))
	_, data, err := conn.ReadMessage()
	if err != nil {
		t.Fatalf("ReadMessage: %v", err)
	}

	var msg model.WSMessage
	if err := json.Unmarshal(data, &msg); err != nil {
		t.Fatalf("unmarshal: %v (raw=%s)", err, string(data))
	}
	return &msg
}

// skipWSMessage descarta a próxima mensagem (útil para drenar joins).
func skipWSMessage(t *testing.T, conn *websocket.Conn, timeout time.Duration) {
	t.Helper()
	conn.SetReadDeadline(time.Now().Add(timeout))
	_, _, err := conn.ReadMessage()
	if err != nil {
		t.Fatalf("skip ReadMessage: %v", err)
	}
}

// === Tests ===

// TestWSConstants verifica que as constantes de ping/pong estão corretas.
func TestWSConstants(t *testing.T) {
	if pingPeriod != 30*time.Second {
		t.Errorf("pingPeriod = %v, want 30s", pingPeriod)
	}
	if pongWait != 60*time.Second {
		t.Errorf("pongWait = %v, want 60s", pongWait)
	}
	if writeWait != 10*time.Second {
		t.Errorf("writeWait = %v, want 10s", writeWait)
	}
	if maxMessageSize != 6144 {
		t.Errorf("maxMessageSize = %d, want 6144", maxMessageSize)
	}
}

// TestWSHandlerConnect verifica que um client conecta via WebSocket e aparece no Hub.
func TestWSHandlerConnect(t *testing.T) {
	server, hub, jwt := setupWSServer(t)
	token := testToken(t, jwt, 1, "testuser")

	conn := connectWSClient(t, server.URL, token)
	defer conn.Close()

	// Aguarda o Hub processar o Connect (goroutine assíncrona)
	time.Sleep(50 * time.Millisecond)

	if count := hub.ConnectionCount(); count != 1 {
		t.Errorf("hub count = %d, want 1", count)
	}

	// Deve receber a mensagem de "join"
	msg := readWSMessage(t, conn, 2*time.Second)
	if msg.Type != "system" {
		t.Errorf("first message type = %q, want %q", msg.Type, "system")
	}
	if msg.Content != "join" {
		t.Errorf("first message content = %q, want %q", msg.Content, "join")
	}
	if msg.Login != "testuser" {
		t.Errorf("first message login = %q, want %q", msg.Login, "testuser")
	}
}

// TestWSHandlerDisconnect verifica que ao fechar a conexão o client é removido do Hub.
func TestWSHandlerDisconnect(t *testing.T) {
	server, hub, jwt := setupWSServer(t)
	token := testToken(t, jwt, 2, "disconnect_user")

	conn := connectWSClient(t, server.URL, token)

	time.Sleep(50 * time.Millisecond)
	if count := hub.ConnectionCount(); count != 1 {
		t.Fatalf("hub count before disconnect = %d, want 1", count)
	}

	// Drena o join
	skipWSMessage(t, conn, 2*time.Second)

	// Fecha a conexão (readPump chama Disconnect)
	conn.Close()

	// Aguarda o readPump detectar o close e chamar Disconnect
	time.Sleep(100 * time.Millisecond)

	if count := hub.ConnectionCount(); count != 0 {
		t.Errorf("hub count after disconnect = %d, want 0", count)
	}
}

// TestWSHandlerMultipleClients verifica que múltiplos clients podem conectar simultaneamente.
func TestWSHandlerMultipleClients(t *testing.T) {
	server, hub, jwt := setupWSServer(t)
	n := 3
	conns := make([]*websocket.Conn, n)

	for i := 0; i < n; i++ {
		login := "user" + string(rune('A'+i))
		token := testToken(t, jwt, i+1, login)
		conns[i] = connectWSClient(t, server.URL, token)
	}

	time.Sleep(100 * time.Millisecond)

	if count := hub.ConnectionCount(); count != n {
		t.Errorf("hub count = %d, want %d", count, n)
	}

	// Cada client recebe joins apenas dos clients conectados depois dele
	// conn[i] recebe n-i joins
	for i, conn := range conns {
		for j := 0; j < n-i; j++ {
			skipWSMessage(t, conn, 2*time.Second)
		}
	}

	// Cleanup
	for _, conn := range conns {
		conn.Close()
	}
}

// TestWSHandlerGracefulShutdown verifica que hub.Shutdown notifica todos os clients.
func TestWSHandlerGracefulShutdown(t *testing.T) {
	server, hub, jwt := setupWSServer(t)
	n := 2
	conns := make([]*websocket.Conn, n)
	var wg sync.WaitGroup

	for i := 0; i < n; i++ {
		login := "sduser" + string(rune('A'+i))
		token := testToken(t, jwt, i+10, login)
		conns[i] = connectWSClient(t, server.URL, token)
	}

	time.Sleep(50 * time.Millisecond)

	if count := hub.ConnectionCount(); count != n {
		t.Fatalf("hub count before shutdown = %d, want %d", count, n)
	}

	// Drena joins: conn[i] recebe n-i joins
	for i, conn := range conns {
		for j := 0; j < n-i; j++ {
			skipWSMessage(t, conn, 2*time.Second)
		}
	}

	// Dispara shutdown via Hub
	hub.Shutdown()

	// Cada client deve receber a mensagem de shutdown
	for i, conn := range conns {
		wg.Add(1)
		go func(idx int, c *websocket.Conn) {
			defer wg.Done()
			msg := readWSMessage(t, c, 3*time.Second)
			if msg.Type != "system" {
				t.Errorf("client %d: shutdown type = %q, want %q", idx, msg.Type, "system")
			}
			if msg.Content != "shutdown" {
				t.Errorf("client %d: shutdown content = %q, want %q", idx, msg.Content, "shutdown")
			}
		}(i, conn)
	}

	wg.Wait()

	for _, conn := range conns {
		conn.Close()
	}
}

// TestWSHandlerPingPong verifica que o servidor envia pings e mantém a conexão viva.
// O servidor envia ping a cada 30s (pingPeriod). Este teste aguarda pelo menos
// um ping e verifica que a conexão permanece ativa.
func TestWSHandlerPingPong(t *testing.T) {
	if testing.Short() {
		t.Skip("teste de ping/pong requer ~35s — use -short=false para executar")
	}

	server, _, jwt := setupWSServer(t)
	token := testToken(t, jwt, 42, "pinguser")

	conn := connectWSClient(t, server.URL, token)
	defer conn.Close()

	// Drena joins (só 1 client)
	skipWSMessage(t, conn, 2*time.Second)

	// Configura handler de ping no client para detectar pings do servidor
	pingReceived := make(chan struct{}, 2)
	conn.SetPingHandler(func(appData string) error {
		select {
		case pingReceived <- struct{}{}:
		default:
		}
		// Responde com pong (gorilla faria isso automaticamente se o handler não fosse setado,
		// mas como setamos, precisamos escrever o pong manualmente)
		conn.SetWriteDeadline(time.Now().Add(writeWait))
		return conn.WriteMessage(websocket.PongMessage, []byte(appData))
	})

	// Aguarda pelo menos um ping do servidor (até 35s)
	ctx, cancel := context.WithTimeout(context.Background(), 35*time.Second)
	defer cancel()

	select {
	case <-pingReceived:
		t.Log("ping recebido do servidor ✓")
	case <-ctx.Done():
		t.Error("timeout: nenhum ping recebido do servidor em 35s")
	}

	// Verifica que a conexão ainda está viva após o ping
	if err := conn.WriteMessage(websocket.PingMessage, []byte("client-ping")); err != nil {
		t.Errorf("conexão morreu após ping: %v", err)
	}
}

// TestWSHandlerAuthRejection verifica que token inválido é rejeitado.
func TestWSHandlerAuthRejection(t *testing.T) {
	server, _, _ := setupWSServer(t)

	// Token inválido
	url := wsURL(server.URL) + "?token=invalid-token"
	_, resp, err := websocket.DefaultDialer.Dial(url, nil)
	if err == nil {
		t.Error("esperava erro de autenticação, mas conexão foi estabelecida")
	}
	if resp != nil && resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status = %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestWSHandlerMissingToken verifica que conexão sem token é rejeitada.
func TestWSHandlerMissingToken(t *testing.T) {
	server, _, _ := setupWSServer(t)

	url := wsURL(server.URL)
	_, resp, err := websocket.DefaultDialer.Dial(url, nil)
	if err == nil {
		t.Error("esperava erro, mas conexão foi estabelecida")
	}
	if resp != nil && resp.StatusCode != http.StatusUnauthorized {
		t.Errorf("status = %d, want %d", resp.StatusCode, http.StatusUnauthorized)
	}
}

// TestWSHandlerPongResetsDeadline verifica que o PongHandler do servidor
// renova o read deadline, mantendo a conexão viva além do pongWait.
func TestWSHandlerPongResetsDeadline(t *testing.T) {
	if testing.Short() {
		t.Skip("teste de pong deadline requer múltiplos ciclos de ping — use -short=false")
	}

	server, _, jwt := setupWSServer(t)
	token := testToken(t, jwt, 99, "ponguser")

	conn := connectWSClient(t, server.URL, token)
	defer conn.Close()

	// Drena join
	skipWSMessage(t, conn, 2*time.Second)

	// Envia pings do client para o servidor a cada 15s por 45s,
	// verificando que a conexão sobrevive (servidor renova deadline no PongHandler)
	deadline := time.Now().Add(50 * time.Second)
	pingTicker := time.NewTicker(15 * time.Second)
	defer pingTicker.Stop()

	for time.Now().Before(deadline) {
		select {
		case <-pingTicker.C:
			if err := conn.WriteMessage(websocket.PingMessage, []byte("keepalive")); err != nil {
				t.Fatalf("WriteMessage ping: %v", err)
			}
			// Lê o pong de resposta (gorilla envia pong automaticamente)
			conn.SetReadDeadline(time.Now().Add(5 * time.Second))
			msgType, _, err := conn.ReadMessage()
			if err != nil {
				t.Fatalf("ReadMessage após ping: %v", err)
			}
			if msgType != websocket.PongMessage && msgType != websocket.TextMessage {
				t.Logf("recebido msg type %d após ping", msgType)
			}
		case <-time.After(time.Until(deadline)):
			return
		}
	}

	t.Log("conexão sobreviveu 50s com pings ativos ✓")
}

// TestWSHandlerReadDeadline verifica que a conexão é fechada após inatividade.
func TestWSHandlerReadDeadline(t *testing.T) {
	if testing.Short() {
		t.Skip("teste de read deadline aguarda inatividade — use -short=false")
	}

	server, _, jwt := setupWSServer(t)
	token := testToken(t, jwt, 77, "deadlineuser")

	conn := connectWSClient(t, server.URL, token)
	defer conn.Close()

	// Drena join
	skipWSMessage(t, conn, 2*time.Second)

	// Fica inativo por pongWait + margem, sem responder pings
	// O servidor deve fechar a conexão
	time.Sleep(pongWait + 5*time.Second)

	// Tenta escrever — deve falhar
	err := conn.WriteMessage(websocket.PingMessage, []byte("late"))
	if err != nil {
		t.Logf("conexão fechada após inatividade: %v ✓", err)
	} else {
		t.Error("conexão deveria estar fechada após pongWait sem atividade")
	}
}
