---
title: "TDD FIRST Principles & AAA Pattern"
category: references
tags:
  - tdd
  - testing
  - first-principles
  - aaa-pattern
  - reference
summary: "Princípios FIRST (Fast, Isolated, Repeatable, Self-Validating, Timely) para escrita de testes eficazes e o padrão AAA (Arrange-Act-Assert) para organização de testes limpos e legíveis."
sources:
  - "references/tdd-methodology.md"
base_confidence: 0.80
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
updated: "2026-06-15"
---

# TDD FIRST Principles & AAA Pattern

## Princípios FIRST

Escreva testes que sigam os princípios FIRST para um conjunto de testes robusto.

### F — Fast (Rápido)

**Testes devem rodar rapidamente (milissegundos, não segundos).**

**Por quê:**
- Testes lentos desencorajam execução frequente
- O ciclo de feedback rápido é essencial para TDD
- A produtividade do desenvolvedor depende de ciclos de teste rápidos

**Como:**
- Evite operações de I/O (disco, rede, banco de dados) em testes unitários
- Use implementações em memória
- Mock dependências externas
- Mantenha a configuração do teste mínima

**Exemplo:**

**Lento:**
```python
def test_user_registration():
    # Lento: Cria conexão real com banco de dados
    db = PostgreSQLDatabase("postgresql://localhost/test")
    db.execute("CREATE TABLE users ...")
    repository = UserRepository(db)
    # ...
    db.execute("DROP TABLE users")
```

**Rápido:**
```python
def test_user_registration():
    # Rápido: Repositório em memória
    repository = InMemoryUserRepository()
    result = register_user({"email": "test@example.com"}, repository)
    assert result.success
```

---

### I — Isolated (Isolado)

**Testes independentes, sem estado compartilhado.**

**Por quê:**
- Falhas em um teste não contaminam outros
- Ordem de execução não importa
- Testes podem ser executados em paralelo
- Diagnóstico preciso de falhas

**Como:**
- Cada teste cria seu próprio cenário
- Não compartilhe estado global
- Use fixtures com escopo adequado
- Evite variáveis globais e singletons

**Exemplo:**

**Violação de Isolamento:**
```python
# BAD: Estado compartilhado entre testes
users = []

def test_create_user():
    users.append(User(email="test@example.com"))
    assert len(users) == 1

def test_create_admin():
    users.append(User(email="admin@example.com", is_admin=True))
    assert len(users) == 2  # Depende do teste anterior!
```

**Correto:**
```python
# GOOD: Cada teste é independente
@pytest.fixture
def user_repository():
    return InMemoryUserRepository()

def test_create_user(user_repository):
    user = User(email="test@example.com")
    user_repository.save(user)
    assert user_repository.count() == 1

def test_create_admin(user_repository):
    admin = Admin(email="admin@example.com")
    user_repository.save(admin)
    assert user_repository.count() == 1
```

---

### R — Repeatable (Repetível)

**Mesmos resultados toda vez, independente de ambiente ou ordem.**

**Por quê:**
- Cria confiança nos testes
- Sem testes flaky (instáveis)
- Funciona em qualquer máquina
- Comportamento determinístico

**Como:**
- Evite depender de hora do sistema ou valores aleatórios
- Não dependa de serviços externos
- Use mocks para comportamento não-determinístico
- Controle todas as entradas

**Exemplo:**

**Não Repetível:**
```python
def test_user_age():
    # RUIM: Resultado muda com o tempo
    user = User(birth_year=2000)
    assert user.age == 24  # Falha em 2026!
```

**Repetível:**
```python
def test_user_age():
    # BOM: Entrada explícita e controlada
    user = User(birth_year=2000)
    age = user.calculate_age(current_year=2024)
    assert age == 24  # Sempre verdadeiro
```

---

### S — Self-Validating (Autovalidável)

**Resultado claro de passa/falha sem inspeção manual.**

**Por quê:**
- Sem ambiguidade nos resultados
- Pode ser automatizado
- Feedback imediato
- Nenhuma interpretação humana necessária

**Como:**
- Sempre use asserções
- Não exija inspeção manual da saída
- Torne os valores esperados explícitos
- Use mensagens de asserção claras

**Exemplo:**

**Não Autovalidável:**
```python
def test_calculate_total():
    result = calculate_total([10, 20, 30])
    print(f"Total: {result}")  # RUIM: Requer inspeção manual
```

**Autovalidável:**
```python
def test_calculate_total():
    result = calculate_total([10, 20, 30])
    assert result == 60  # BOM: Passa/Falha claro
```

---

### T — Timely (Oportuno)

**Escritos antes (ou no máximo junto com) o código de produção.**

**Por quê:**
- Garante que os testes podem falhar (não são perenes)
- Direciona um design de API melhor
- Previne viés de implementação
- Força a pensar nos requisitos primeiro

**Como:**
- Escreva o teste primeiro (RED)
- Depois escreva o código mínimo para passar (GREEN)
- Finalmente refatore (REFACTOR)
- Nunca escreva código sem um teste falhando primeiro

**Exemplo:**

**Oportuno (jeito TDD):**
```
1. Escreva teste para funcionalidade X (RED)
2. Implemente funcionalidade X (GREEN)
3. Refatore (REFACTOR)
4. Commit
```

**Não Oportuno (jeito tradicional):**
```
1. Implemente funcionalidade X
2. Escreva teste para funcionalidade X (sempre passa — perene!)
```

---



## Padrão AAA (Arrange-Act-Assert)

O padrão AAA organiza cada teste em três seções distintas, tornando os testes legíveis e focados.

### Estrutura

```
def test_<comportamento>():
    # ARRANGE  (Preparar): configure dados e dependências
    # ACT      (Agir):     execute a ação sendo testada
    # ASSERT   (Verificar): verifique o resultado
```

### ARRANGE — Preparar

Configure o cenário do teste: crie objetos, inicialize dependências, prepare dados de entrada.

```python
def test_calculate_total_with_multiple_items():
    # ARRANGE
    cart = ShoppingCart()
    cart.add_item(Item("Book", price=30.0, quantity=2))
    cart.add_item(Item("Pen", price=5.0, quantity=3))
```

Mantenha o ARRANGE o mais simples possível. Se ficar muito longo, considere:

1. **Extrair fixtures do pytest:**
```python
@pytest.fixture
def cart_with_items():
    cart = ShoppingCart()
    cart.add_item(Item("Book", price=30.0, quantity=2))
    cart.add_item(Item("Pen", price=5.0, quantity=3))
    return cart

def test_calculate_total(cart_with_items):
    total = cart_with_items.calculate_total()
    assert total == 75.0
```

2. **Usar factory functions:**
```python
def make_user(email="user@example.com", role="member", active=True):
    return User(email=email, role=role, active=active)

def test_admin_can_delete_posts():
    admin = make_user(role="admin")
    assert admin.can_delete_posts() is True

def test_member_cannot_delete_posts():
    member = make_user(role="member")
    assert member.can_delete_posts() is False
```

### ACT — Agir

Execute a ação que está sendo testada — normalmente uma única chamada de função ou método.

```python
def test_calculate_total():
    cart = ShoppingCart()
    cart.add_item(Item("Book", price=30.0, quantity=2))

    # ACT — uma única linha, uma única ação
    total = cart.calculate_total()

    assert total == 60.0
```

**Regras para a seção ACT:**
- Deve conter **uma única ação**
- Não misture setup com a ação
- A ação deve ser o centro do teste
- O nome do teste deve descrever esta ação

### ASSERT — Verificar

Verifique se o resultado corresponde ao esperado.

```python
def test_calculate_total():
    cart = ShoppingCart()
    cart.add_item(Item("Book", price=30.0, quantity=2))

    total = cart.calculate_total()

    # ASSERT — verificação clara do resultado
    assert total == 60.0
```

**Boas práticas para ASSERT:**
- Uma asserção lógica por teste
- Use asserções específicas do pytest quando aplicável
- Mensagens de erro descritivas ajudam no debugging

### Exemplo completo com pytest:

```python
class TestUserRegistration:
    def test_register_user_with_valid_data_creates_user(self):
        # ARRANGE
        repository = InMemoryUserRepository()
        user_data = {
            "email": "alice@example.com",
            "password": "secure_password"
        }

        # ACT
        result = register_user(user_data, repository)

        # ASSERT
        assert result.success is True
        assert result.user.email == "alice@example.com"
        assert repository.count() == 1

    def test_register_user_with_invalid_email_fails(self):
        # ARRANGE
        repository = InMemoryUserRepository()
        user_data = {
            "email": "invalid-email",
            "password": "secure_password"
        }

        # ACT
        result = register_user(user_data, repository)

        # ASSERT
        assert result.success is False
        assert "email" in result.errors
        assert repository.count() == 0
```

### Dica de visualização AAA

Sempre separe as três seções visualmente com linhas em branco:

```python
def test_something():
    # ARRANGE
    ...

    # ACT
    ...

    # ASSERT
    ...
```

Use comentários de seção (`# ARRANGE`, `# ACT`, `# ASSERT`) para tornar a estrutura explícita.

---



## Ver Também

- [[references/tdd-methodology|TDD Methodology]] — Ciclo Red-Green-Refactor
- [[references/tdd-anti-patterns|TDD Anti-Patterns]] — Catálogo de anti-patterns
- [[references/qa-overview|QA Overview]] — Onde TDD se encaixa na estratégia SDD
