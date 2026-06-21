# Spec: 42 Forum

## Metadados
- **ID:** 102
- **Status:** draft
- **Aprovado:** false
- **Autor:** phm-aguiar
- **Data:** 2026-06-21
- **Stack:** Go, React + MDX, PostgreSQL (reuse), OAuth2 42
- **Based on:** [[004-jschan-forum-manager]] (modelo board/thread/post do jschan)
- **Referências:** [[wiki/_raw/What is MDX]], [[wiki/_raw/Using MDX]]

## Propósito
> Fórum tech para alunos da 42 compartilharem descobertas, aprendizados e
> conhecimento técnico. Inspirado no modelo board/thread/post de imageboards
> (chans), mas com **identidade real** (login 42 visível) — sem anonimato.
>
> Ao contrário do chat em tempo real (Feature 100), o fórum é **assíncrono e
> permanente**: uma thread de hoje pode ser consultada daqui 6 meses. É o
> "lugar das coisas que merecem mais que 5 minutos de atenção".

## Escopo

### Dentro do escopo (v1)

- **Boards (categorias):** CRUD por mods/admins. Slug único (ex: /tech). Alunos podem sugerir novos boards.
- **Threads (tópicos):** Qualquer aluno logado cria em qualquer board não-locked. Título (3-200 chars) + conteúdo MDX (até 10k chars).
- **Posts (respostas):** Qualquer aluno logado responde em qualquer thread não-locked. Conteúdo MDX (até 10k chars). Reply-to opcional (tree view).
- **Conteúdo MDX:** Markdown + JSX — texto, imagens inline (`![alt](url)`), code snippets com syntax highlight, links, embed de componentes React.
- **Identidade real:** Todo post exibe login 42 + avatar do autor. Sem tripcodes, sem nome genérico, sem anonimato.
- **Moderação completa:**
  - **Board owner:** controle total sobre o board (editar settings, promover staff, deletar board)
  - **Board mod:** pode pin/lock/delete threads e posts dentro do board
  - **Admin global:** pode gerenciar qualquer board, criar boards, promover admins
- **Seed boards iniciais:** /tech (tech geral), /projects (mostra teu projeto), /career (vagas/carreira), /events (eventos 42), /random (off-topic)
- **Bump order:** threads ordenadas por `last_post_at` (mais recente no topo), pinned threads sempre no topo
- **Soft delete:** threads e posts têm `deleted_at` — nunca hard delete
- **Reuso de PostgreSQL:** Migration 002_add_forum.sql no mesmo banco, mesmo container Docker
- **Reuso de auth:** JWT middleware existente, author_id = users.id (INT da API 42)
- **Backend Go + Chi:** Novas rotas `/api/forum/*`
- **PKs UUIDv7:** Time-sortable, sem enumeration attack
- **Tags/labels:** Array TEXT[] nas threads, input no frontend pra categorizar posts (ex: #go, #websocket, #react)
- **API 42 — Títulos como badge:** Títulos/achievements do aluno da 42 exibidos como flair nos posts do fórum (ex: "Go Expert 🏆"). Buscado durante o login via `/v2/users/:id/titles`.
- **API 42 — Skills como sugestão de tags:** Tags de skill do aluno (Go, Web, C, etc.) sugeridas automaticamente ao criar uma thread. Buscado via `/v2/users/:id/tags_users`.

### Fora do escopo (v1)

- **Upload de imagem/arquivo direto** — imagens só via link externo (markdown `![]()`)
- **Notificações** (push, email, WS) — v2
- **Busca full-text** — v2 (índice GIN já existe mas sem UI)
- **Sistema de reputação/karma** — v2
- **Votação (upvote/downvote)** — v2
- **API de integração externa** (embeds, webhooks) — v2
- **Cliente mobile nativo** — v2
- **Painel admin global** — v1 usa CLI/API direta

## Comportamento Esperado

### Cenário Principal: Aluno cria uma thread
1. Aluno logado acessa `/forum/tech`
2. Vê lista de threads do board /tech (bump order, pinned no topo)
3. Clica "Nova Thread"
4. Preenche título + conteúdo MDX (editor com preview)
5. Backend valida: JWT → author_id, board existe, title ≥ 3 chars, content ≤ 10k
6. Thread criada com UUIDv7
7. Primeiro post (OP) inserido na tabela `posts` com mesmo timestamp
8. Board mostra thread no topo (bump)

### Cenário Principal: Aluno responde uma thread
1. Aluno logado acessa `/forum/tech/thread/{id}`
2. Vê o OP + todas as respostas em ordem cronológica
3. Escreve reply MDX (com reply_to opcional para quote)
4. Post inserido, `last_post_at` da thread atualizado (bump)
5. Thread volta ao topo do board

### Cenário: Moderação
1. Mod vê botão "Pin" / "Lock" / "Delete" em threads do board
2. Pin → `is_pinned = true` → thread fixa no topo
3. Lock → `is_locked = true` → ninguém mais posta (só mods podem, se configurado)
4. Delete → `deleted_at = NOW()` → thread some da lista (mas dados preserved)
5. Admin global vê ações de moderação em qualquer board

### Cenário: Board Management (mod/admin)
1. Mod acessa `/forum/admin/boards`
2. Vê lista de boards existentes + formulário "Criar Board"
3. Cria board com slug, name, description, sfw flag
4. Board aparece na landing page do fórum
5. Mod pode adicionar/remover staff do board
6. Board owner pode editar settings ou deletar o board (com confirmação)

### Cenário: API 42 — Títulos e skills do usuário
1. Durante o login OAuth2 (ExchangeCode), backend busca `/v2/users/:id/titles` (títulos) e `/v2/users/:id/tags_users` (skills)
2. Título principal armazenado em `users.title` (coluna nova, nullable)
3. Skills armazenadas em `users.skills` (TEXT[], nullable)
4. Nos posts do fórum, badge com o título aparece ao lado do login
5. Ao criar thread, input de tags sugere as skills do autor como autocomplete

### Cenário: Edge — URI reservada
1. Tentativa de criar board com slug "admin", "api", "chat", etc
2. Backend rejeita com 400 + mensagem "slug reservado"

### Cenário: Edge — Thread locked
1. Aluno tenta postar em thread com `is_locked = true`
2. Backend rejeita com 403 + "thread fechada para novos posts"

## Edge Cases
- **Board sem threads:** lista vazia com mensagem "seja o primeiro a postar"
- **Thread sem posts (além do OP):** mostra só o OP
- **Reply-to deletado:** post continua visível, referência exibe "[deleted]"
- **Board deletado (hard):** CASCADE deleta threads + posts (com confirmação)
- **Usuário deletado:** posts exibem "[deleted]" no lugar do login (FK ON DELETE CASCADE no board_staff, mas posts mantêm author_id)
- **MDX inválido:** frontend renderiza fallback (texto raw) + aviso
- **Conteúdo muito longo:** validação no backend + frontend (10k chars)
- **Concorrência:** dois alunos postam no mesmo ms → UUIDv7 + clock sequence evitam colisão
- **Reconexão:** fórum é REST, não WS — sem estado de conexão pra gerenciar

## Constraints
- **Stack fixa:** Go + Chi + lib/pq (backend), React + MDX (frontend), PostgreSQL (banco)
- **Zero infra nova:** mesmo Docker Compose, mesmo PostgreSQL, mesmo servidor Go
- **Auth obrigatória:** todo endpoint do fórum requer JWT válido (exceto listar boards públicos, talvez)
- **Limite de conteúdo:** 10k chars por post/thread, 200 chars título
- **Slug de board:** regex `^[a-z0-9]([a-z0-9_-]*[a-z0-9])?$`, slugs reservados bloqueados
- **UUIDv7:** todas as PKs do fórum (boards, threads, posts) — sem SERIAL
- **Identidade real:** nenhum post sem user_id. Sem exceção.
- **MDX v1:** `@mdx-js/react` no frontend para renderização de posts

## Critérios de Sucesso
- [ ] Aluno logado vê lista de boards na página `/forum`
- [ ] Aluno entra em um board e vê threads (bump order, pinned)
- [ ] Aluno cria thread com título + conteúdo MDX
- [ ] Aluno responde thread com MDX (incluindo reply-to)
- [ ] Conteúdo MDX renderiza corretamente (código, imagem, link)
- [ ] Mod pin/lock/delete thread via API
- [ ] Mod cria board com slug/name/description
- [ ] Staff adicionado/removido de board
- [ ] Admin global age em qualquer board
- [ ] Thread locked rejeita novos posts
- [ ] Slug reservado rejeitado
- [ ] Zerar Docker + migration 002 + seed boards → fórum funcional
- [ ] Smoke test: criar board → criar thread → postar reply → ver bump order

## Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Linguagem | Go 1.25 | Reuso do backend existente |
| Roteamento | Chi | Já usado no chat |
| Banco | PostgreSQL 16 | Migration 002, mesmo container |
| Auth | OAuth2 42 + JWT | Middleware existente |
| Frontend | React 18 + MDX | Renderização de posts com MDX |
| Estilo | Tailwind + Shadcn/ui | Mesmo design system do chat |
| PKs | UUIDv7 (stdlib Go) | Time-sortable, sem enumeration |
| Container | Docker Compose | Reuso, sem novo serviço |
| Infra | AWS EC2 t2.micro | Mesmo host do chat |

## Modelagem de Dados

### users (alterado)
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INT PK | ID da API 42 |
| login | VARCHAR(50) UNIQUE | Login da intra |
| image_url | TEXT | URL da foto de perfil |
| current_host | VARCHAR(20) | Localização no campus |
| level | NUMERIC(4,2) | Nível na intra |
| title | VARCHAR(100) | Título atual (ex: "Go Expert") — nullable, v1 |
| skills | TEXT[] | Tags de skill (ex: {go, web, algorithms}) — nullable, v1 |
| created_at | TIMESTAMPTZ | — |

### boards
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | UUIDv7 |
| slug | VARCHAR(50) UNIQUE | URI do board (ex: tech) |
| name | VARCHAR(100) | Nome humano |
| description | TEXT | Descrição do board |
| owner_id | INT FK → users | Dono do board |
| sfw | BOOLEAN | Conteúdo seguro |
| theme | VARCHAR(50) | Tema visual (frontend) |
| language | VARCHAR(10) | Idioma padrão (pt-BR) |
| is_locked | BOOLEAN | Board fechado (só staff) |
| created_at | TIMESTAMPTZ | — |
| updated_at | TIMESTAMPTZ | — |

### board_staff
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| board_id | UUID FK → boards | Board |
| user_id | INT FK → users | Staff member |
| role | VARCHAR(20) | owner / mod / admin |
| added_at | TIMESTAMPTZ | — |
| added_by | INT FK → users | Quem adicionou |

### threads
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | UUIDv7 |
| board_id | UUID FK → boards | Board |
| author_id | INT FK → users | Autor (OP) |
| title | VARCHAR(200) | Título |
| content | TEXT | Conteúdo MDX (OP) |
| is_pinned | BOOLEAN | Fixado? |
| is_locked | BOOLEAN | Fechado? |
| post_count | INT | Contagem total |
| last_post_at | TIMESTAMPTZ | Bump timestamp |
| tags | TEXT[] | Tags da thread (ex: {go, websocket}) |
| created_at | TIMESTAMPTZ | — |
| updated_at | TIMESTAMPTZ | — |
| deleted_at | TIMESTAMPTZ | Soft delete |

### posts
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID PK | UUIDv7 |
| thread_id | UUID FK → threads | Thread |
| author_id | INT FK → users | Autor |
| content | TEXT | Conteúdo MDX |
| reply_to | UUID FK → posts (nullable) | Referência a reply |
| created_at | TIMESTAMPTZ | — |
| deleted_at | TIMESTAMPTZ | Soft delete |

## Abordagem Escolhida
> **Reuso total da stack existente.** Zero infra nova. O fórum é um módulo dentro
> do mesmo servidor Go, usando o mesmo PostgreSQL, mesma auth, mesmo Docker.
> O modelo board/thread/post é inspirado no jschan, mas com identidade real
> (sem anonimato), UUIDv7 em vez de ObjectId, e MDX em vez de markup de imageboard.
>
> O frontend ganha `@mdx-js/react` como única dependência nova. Os posts são
> armazenados como MDX source no banco e renderizados no cliente com componentes
> customizados (code highlight, embed de link, etc).

### Alternativas Consideradas

| Abordagem | Trade-off | Por que não |
|-----------|-----------|-------------|
| **Rodar jschan como serviço separado** | Ganha fórum pronto | Requer MongoDB + Redis + Node.js + Nginx. Stack diferente, mais infra, anonimato indesejado |
| **Markdown puro em vez de MDX** | Mais simples | Perde capacidade de embed de componentes React interativos. MDX é markdown + JSX |
| **SERIAL em vez de UUIDv7** | PKs incrementais | Enumeration attack (alguém descobre total de threads/posts). UUIDv7 é time-sortable e seguro |
| **Feature 004 (jschan) com adaptações** | Reaproveita skill existente | Feature 004 gerencia boards jschan via mongosh. Nosso fórum é PostgreSQL + Go, stack diferente |
