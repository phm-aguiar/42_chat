---
title: "TDD Anti-Patterns — Catálogo de Referência"
category: references
tags:
  - tdd
  - testing
  - anti-patterns
  - reference
summary: "Catálogo dos 8 anti-patterns mais comuns em TDD com exemplos em Python/pytest: The Liar, Excessive Setup, The Giant, The Mockery, The Inspector, The Slow Poke, The Generous Leftovers, The Free Ride. Cada anti-pattern inclui problema, exemplo ruim, diagnóstico e solução."
sources:
  - "references/tdd-methodology.md"
base_confidence: 0.80
lifecycle: draft
lifecycle_changed: "2026-06-15"
tier: supporting
created: "2026-06-15"
rag_score: 0.48
updated: "2026-06-15"
---

# TDD Anti-Patterns — Catálogo de Referência

### 1. The Liar (O Mentiroso) — Testes sem Asserções Reais

**Problema:** O teste passa mas não verifica o comportamento que afirma testar.

**Evite isso:**
```python
def test_user_is_saved():
    user = User(email="test@example.com")
    repository.save(user)
    # Sem asserção! Sempre passa
```

**Faça isso:**
```python
def test_user_is_saved():
    user = User(email="test@example.com")
    repository.save(user)
    saved_user = repository.get_by_email("test@example.com")
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
```

**Pontos-chave:**
- Sempre inclua asserções que verifiquem o comportamento esperado
- Teste o resultado observável, não apenas se o código executa sem erros
- Se não há asserção, o teste está mentindo sobre o que verifica

---

### 2. Evergreen Tests (Testes Perenes) — Testes que Nunca Falham

**Problema:** Testes escritos após o código, projetados para passar imediatamente. Fornecem falsa confiança porque nunca provaram que podem capturar bugs.

**Por que é problemático:**
- Você não sabe se o teste realmente valida algo
- O teste pode estar verificando a coisa errada
- Pode passar mesmo quando a funcionalidade está quebrada

**Solução:**
- **Sempre veja seu teste falhar primeiro!**
- Escreva o teste antes da implementação
- Se escrever testes depois, quebre ou delete temporariamente a implementação para verificar se o teste falha
- Um teste que nunca falhou nunca provou seu valor

**A regra do TDD:**
> Você não pode escrever um teste sem vê-lo falhar primeiro. Se você não o viu vermelho, você não testou nada.

---

### 3. Excessive Setup — Configuração Excessiva

**Problema:** Testes exigem configuração massiva (50+ linhas) antes de chegar ao teste real. Isso é sinal de código com acoplamento forte e muitas dependências.

**O que sinaliza:**
- Seu código tem dependências demais
- Classes estão fazendo demais (violando SRP — Single Responsibility Principle)
- Baixa separação de concerns
- Acoplamento forte entre componentes

**Exemplo do problema:**
```python
def test_process_order():
    # 50+ linhas de setup...
    db = Database("connection_string")
    email_service = EmailService(api_key="...")
    payment_gateway = PaymentGateway(merchant_id="...")
    inventory_service = InventoryService(db)
    shipping_service = ShippingService(api_key="...")
    tax_calculator = TaxCalculator(region="US", db=db)
    discount_engine = DiscountEngine(db, email_service)
    order_processor = OrderProcessor(
        db, email_service, payment_gateway,
        inventory_service, shipping_service,
        tax_calculator, discount_engine
    )
    # Finalmente, o teste...
    result = order_processor.process(order_data)
    assert result.success
```

**Solução — Simplifique o design:**
```python
@pytest.fixture
def order_processor():
    # Dependências simplificadas com implementações em memória
    return OrderProcessor(
        repository=InMemoryOrderRepository(),
        emailer=MockEmailer()
    )

def test_process_order(order_processor):
    # ARRANGE: Setup mínimo e focado
    order = Order(items=[...])

    # ACT
    result = order_processor.process(order)

    # ASSERT
    assert result.success
```

**Princípios-chave:**
- Se os testes são difíceis de configurar, o código é difícil de usar
- Use injeção de dependência para reduzir acoplamento
- Crie test doubles em memória em vez de infraestrutura completa
- Extraia setup complexo em fixtures bem nomeadas
- Considere se sua classe está fazendo demais

---

### 4. Assertion-Free Tests — Testes sem Asserções

**Problema:** Testes que executam código mas nunca verificam nada. Podem passar mesmo quando o sistema está quebrado.

**Evite isso:**
```python
def test_email_sending():
    email_service = EmailService()
    email_service.send("test@example.com", "Subject", "Body")
    # Nenhuma verificação — sempre passa, mesmo se o email não for enviado
```

**Faça isso:**
```python
def test_email_sending():
    email_service = EmailService()
    email_service.send("test@example.com", "Subject", "Body")
    assert email_service.sent_count == 1
    sent = email_service.get_last_sent()
    assert sent.recipient == "test@example.com"
    assert sent.subject == "Subject"
```

**Como detectar:**
- Testes sem a palavra-chave `assert`
- Testes que só chamam funções sem verificar resultados
- Testes com `print()` ou logging em vez de asserções
- Testes marcados como `@pytest.mark.skip` permanentemente

**Regra de ouro:** Se não há `assert`, não é um teste.

---

### 5. Fragile Tests (Testes Frágeis) — Testes que Quebram Sem Motivo

**Problema:** Testes que quebram quando código não relacionado muda, ou quando a estrutura interna muda apesar do comportamento externo permanecer o mesmo.

**Causas comuns:**

**a) Acoplamento a detalhes de implementação:**
```python
def test_cache_uses_dictionary():
    cache = Cache()
    cache.set("key", "value")
    # RUIM: Testa implementação interna
    assert isinstance(cache._data, dict)
    assert "key" in cache._data
```

**b) Dependência de ordem de execução:**
```python
# RUIM: Teste que depende de outro teste rodar antes
all_users = []
def test_create_user():
    all_users.append("user1")
    assert len(all_users) == 1

def test_create_another_user():
    all_users.append("user2")
    assert len(all_users) == 2  # Falha se rodar sozinho!
```

**c) Asserções muito específicas:**
```python
def test_format_currency():
    result = format_currency(10.5)
    assert result == "R$ 10,50"  # Frágil: muda com locale
```

**Soluções:**
- Teste comportamento, não implementação
- Garanta isolamento total entre testes
- Use asserções flexíveis quando apropriado
- Não acesse atributos privados (`_`)

```python
# BOM: Testa comportamento observável
def test_cache_retrieves_stored_values():
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"

def test_cache_returns_none_for_missing_keys():
    cache = Cache()
    assert cache.get("missing") is None
```

**O princípio:** Teste o "o quê", não o "como". Teste comportamento, não implementação.

---

### 6. Slow Tests (Testes Lentos) — Testes que Demoram Demais

**Problema:** Testes que levam segundos ou minutos para rodar, desencorajando execução frequente.

**O que causa testes lentos:**

| Causa | Exemplo | Solução |
|-------|---------|---------|
| I/O real | Conexão com banco, chamadas HTTP | Use repositórios em memória, mocks |
| Operações pesadas | Processamento de milhões de registros | Teste com conjuntos pequenos |
| Sleep/wait | `time.sleep(5)` para simular latência | Use mocks de tempo, não espere |
| Setup desnecessário | Criar objetos complexos para teste simples | Use fábricas ou builders |

**Exemplo de teste lento:**
```python
def test_generate_report():
    # Lento: banco real, email server, sistema de arquivos
    db = create_test_database()
    email_server = start_test_email_server()
    file_system = create_test_file_system()
    config = load_config_file()

    report_generator = ReportGenerator(db, email_server, file_system, config)

    report = report_generator.generate(user_id=123)
    assert report.total > 0
```

**Solução — Separe lógica de I/O:**
```python
class ReportBuilder:
    """Lógica pura — fácil de testar, rápida"""
    def build(self, user_data: dict) -> Report:
        return Report(
            title=f"Report for {user_data['name']}",
            data=self._format_data(user_data)
        )

# Teste rápido sem I/O
def test_report_builder_formats_user_data():
    builder = ReportBuilder()
    report = builder.build({"name": "Alice", "sales": 1000})
    assert report.title == "Report for Alice"
```

**Diretrizes:**
- Testes unitários: milissegundos
- Testes de integração: segundos (execute separadamente)
- Se um teste leva > 100ms, pergunte-se por quê
- Separe testes lentos em diretório/suíte própria

---

### 7. Interdependent Tests (Testes Interdependentes) — Testes que Dependem Uns dos Outros

**Problema:** Testes que compartilham estado, dependem de ordem de execução, ou assumem que outros testes rodaram antes.

**Evite isso:**
```python
# RUIM: Testes que dependem de estado compartilhado
users_db = {}

def test_create_user():
    users_db["user1"] = {"name": "Alice"}
    assert len(users_db) == 1  # Funciona se for o primeiro

def test_create_user_fails_if_duplicate():
    # Falha se test_create_user não rodou antes!
    assert "user1" in users_db
    # ...
```

**Faça isso:**
```python
# BOM: Cada teste cria seu próprio cenário
def test_create_user():
    db = InMemoryDatabase()
    service = UserService(db)
    user = service.create("Alice")
    assert user.name == "Alice"
    assert db.count() == 1

def test_create_user_fails_if_duplicate():
    db = InMemoryDatabase()
    db.save(User(name="Alice"))  # Setup explícito
    service = UserService(db)
    with pytest.raises(DuplicateUserError):
        service.create("Alice")
```

**Sinais de alerta:**
- Variáveis globais ou de módulo sendo modificadas em testes
- Testes que só passam quando executados em uma ordem específica
- Uso de `@pytest.mark.dependency` ou similar
- Testes que falham quando executados isoladamente (`pytest test_file.py::test_func`)
- Estado vazando entre testes via singletons, caches globais

**Solução:**
- Cada teste deve ser executável isoladamente
- Use fixtures com escopo `function` (padrão)
- Reset todo estado compartilhado entre testes
- Nunca dependa de side effects de outros testes
- Use `autouse=True` em fixtures para reset automático

```python
@pytest.fixture(autouse=True)
def reset_database():
    """Reseta o banco antes de cada teste."""
    Database.reset()
    yield
```

---

### 8. Testing Implementation Details — Testar Detalhes de Implementação

**Problema:** Testes que quebram durante refatoração mesmo quando o comportamento externo não mudou.

**Evite isso:**
```python
def test_user_password_stored_with_bcrypt():
    user = User(password="secret")
    assert user._password_hash.startswith("$2b$")  # Detalhe de implementação!
    assert len(user._salt) == 16  # Estrutura interna!
```

**Por que é ruim:**
- Testes se tornam frágeis — quebram durante refatoração
- Você não pode mudar a implementação sem mudar os testes
- Os testes não verificam o comportamento real para o usuário
- Viola encapsulamento ao depender de detalhes privados

**Faça isso:**
```python
def test_user_password_can_be_verified():
    user = User(password="secret")
    assert user.verify_password("secret") is True
    assert user.verify_password("wrong") is False
```

**Mais exemplos:**

**Ruim — Testar estado interno:**
```python
def test_cache_uses_dictionary():
    cache = Cache()
    cache.set("key", "value")
    assert isinstance(cache._data, dict)  # Detalhe interno
    assert "key" in cache._data           # Estrutura interna
```

**Bom — Testar comportamento:**
```python
def test_cache_retrieves_stored_values():
    cache = Cache()
    cache.set("key", "value")
    assert cache.get("key") == "value"

def test_cache_returns_none_for_missing_keys():
    cache = Cache()
    assert cache.get("missing") is None
```

**O princípio:**
> Teste comportamento, não implementação. Teste o "o quê", não o "como".

**Benefícios:**
- Liberdade para refatorar a implementação sem tocar nos testes
- Testes documentam como os usuários interagem com o código
- Suíte de testes mais estável
- Testes permanecem valiosos à medida que o código evolui

**E se a lógica interna for complexa demais?** Extraia para um componente público separado e teste-o independentemente:

```python
# Extrair para módulo próprio
class OrderValidator:
    def validate(self, order):
        if not order.items:
            return ValidationResult(False, "No items")
        return ValidationResult(True)

# Agora é testável independentemente
def test_validator_rejects_empty_orders():
    validator = OrderValidator()
    result = validator.validate(Order(items=[]))
    assert not result.success
```

---



## Ver Também

- [[references/tdd-methodology|TDD Methodology]] — Visão geral e ciclo Red-Green-Refactor
- [[references/tdd-first-principles|TDD FIRST Principles]] — Princípios e padrão AAA
- [[references/bdd-specification-process|BDD Spec Process]] — BDD complementa TDD
