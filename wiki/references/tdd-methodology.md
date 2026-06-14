---
title: "Metodologia TDD — Test-Driven Development"
summary: "Referência completa sobre a metodologia TDD: ciclo Red-Green-Refactor-Commit, princípios FIRST, padrão AAA (Arrange-Act-Assert), nomenclatura e organização de testes, e os 8 anti-patterns mais comuns com exemplos práticos em Python/pytest."
tags: [tdd, testing, pytest, reference]
category: references
created: "2026-06-13"
updated: "2026-06-14"
---

# Metodologia TDD — Test-Driven Development

## Índice

1. [O Ciclo Red-Green-Refactor-Commit](#o-ciclo-red-green-refactor-commit)
2. [Princípios FIRST](#princípios-first)
3. [Padrão AAA (Arrange-Act-Assert)](#padrão-aaa-arrange-act-assert)
4. [Naming Conventions para Testes](#naming-conventions-para-testes)
5. [Organização de Testes](#organização-de-testes)
6. [Quando Testar o Quê](#quando-testar-o-quê)
7. [8 Anti-Patterns de TDD](#8-anti-patterns-de-tdd)

---

## O Ciclo Red-Green-Refactor-Commit

TDD segue um ciclo disciplinado de quatro etapas que garante qualidade, manutenibilidade e confiança no código.

### 1. RED — Escreva um Teste que Falha

**Objetivo:** Definir o comportamento que você deseja desenvolver.

**O que fazer:**
- Escreva um teste que especifique o comportamento esperado
- O teste **deve falhar** inicialmente — isso prova que ele está testando algo de fato
- Observe a falha e leia a mensagem de erro com atenção
- A mensagem de falha deve ser descritiva e revelar o que está faltando
- Esta etapa força você a pensar na API e no comportamento antes da implementação

**Por que é importante:**
- Prova que o teste pode realmente capturar bugs
- Define a interface desejada (design da API)
- Cria documentação executável do comportamento esperado
- Previne "testes perenes" (evergreen tests) que nunca falham

**Exemplo:**

```python
# RED: Este teste vai falhar porque sortArray não existe ainda
def test_sort_array_ascending():
    result = sortArray([2, 4, 1])
    assert result == [1, 2, 4]
```

**Mensagem de falha esperada:**
```
NameError: name 'sortArray' is not defined
```

**Perguntas-chave:**
- Que comportamento quero implementar?
- Como deve ser a API?
- Qual é o caso de teste mais simples que posso escrever?
- O teste falha pelo motivo certo?

---

### 2. GREEN — Faça o Teste Passar

**Objetivo:** Fazer funcionar, sem se preocupar com perfeição ainda.

**O que fazer:**
- Escreva o código **mínimo necessário** para fazer o teste passar
- Não adicione funcionalidades não cobertas pelo teste
- Simplicidade e velocidade acima de elegância nesta etapa
- Quando o teste fica verde, você tem uma rede de segurança para refatorar

**Por que é importante:**
- Valida que o teste pode passar
- Fornece código funcional o mais rápido possível
- Cria uma rede de segurança antes da otimização
- Mantém o foco em resolver um problema de cada vez

**Exemplo:**

```python
def sortArray(arr):
    # GREEN: Implementação simples faz o teste passar
    return sorted(arr)  # Usa o sort nativo do Python
```

**Saída do teste:**
```
test_sort_array_ascending PASSED
```

**Mindset da "coisa mais simples":**

Às vezes a implementação mais simples é quase trivial:

```python
# Primeiro teste
def test_get_greeting_returns_hello():
    assert get_greeting() == "Hello"

# Implementação mais simples (sim, é sério!)
def get_greeting():
    return "Hello"
```

Parece bobo, mas é TDD válido! Adicione mais testes para forçar a solução geral:

```python
# Segundo teste força a generalização
def test_get_greeting_with_name_returns_personalized_greeting():
    assert get_greeting("Alice") == "Hello, Alice"

# Agora precisamos de uma implementação real
def get_greeting(name=None):
    if name:
        return f"Hello, {name}"
    return "Hello"
```

**Perguntas-chave:**
- Qual o código mais simples que faz este teste passar?
- Estou adicionando funcionalidades não cobertas pelos testes?
- O teste realmente passa agora?
- Estou pronto para refatorar?

---

### 3. REFACTOR — Melhore o Design

**Objetivo:** Limpar o código enquanto mantém os testes verdes.

**O que fazer:**

**Seis perguntas-chave para se fazer:**
1. Posso tornar meu conjunto de testes mais expressivo?
2. Meu conjunto de testes fornece feedback confiável?
3. Meus testes estão isolados uns dos outros?
4. Posso reduzir duplicação no código de teste ou implementação?
5. Posso tornar meu código de implementação mais descritivo?
6. Posso implementar algo de forma mais eficiente?

**Por que é importante:**
- Melhora o design preservando o comportamento
- Reduz dívida técnica imediatamente
- Torna o código mais sustentável
- Aproveita a rede de segurança dos testes verdes

**Importante:** Você pode fazer o que quiser com o código quando os testes estão verdes — a única coisa que você **não pode** fazer é adicionar ou alterar comportamento.

**Exemplo:**

```python
def sortArray(arr):
    # REFACTOR: Substitui por algoritmo mais eficiente
    if len(arr) <= 1:
        return arr
    # Implementa merge sort para melhor performance
    return merge_sort(arr)
```

**O teste ainda passa:**
```
test_sort_array_ascending PASSED
```

**Oportunidades comuns de refatoração:**

**Extrair Método:**
```python
# Antes
def process_order(order):
    total = 0
    for item in order.items:
        total += item.price * item.quantity
    tax = total * 0.08
    return total + tax

# Depois
def process_order(order):
    subtotal = calculate_subtotal(order)
    tax = calculate_tax(subtotal)
    return subtotal + tax

def calculate_subtotal(order):
    return sum(item.price * item.quantity for item in order.items)

def calculate_tax(subtotal):
    return subtotal * 0.08
```

**Remover Duplicação:**
```python
# Antes — duplicação nos testes
def test_user_login_success():
    repository = InMemoryUserRepository()
    user = User(email="test@example.com", password="secret")
    repository.save(user)
    # ...

def test_user_login_failure():
    repository = InMemoryUserRepository()
    user = User(email="test@example.com", password="secret")
    repository.save(user)
    # ...

# Depois — fixture extraída
@pytest.fixture
def authenticated_user():
    repository = InMemoryUserRepository()
    user = User(email="test@example.com", password="secret")
    repository.save(user)
    return user, repository
```

**Melhorar Nomenclatura:**
```python
# Antes
def calc(x, y):
    return x * y * 0.08

# Depois
def calculate_sales_tax(price, quantity):
    subtotal = price * quantity
    return subtotal * 0.08
```

**Perguntas-chave:**
- Há duplicação que posso remover?
- Posso tornar o código mais legível?
- Os nomes de variáveis/funções estão claros?
- Posso simplificar lógica complexa?
- Existe um algoritmo mais eficiente?
- Meus testes estão tão limpos quanto meu código?

---

### 4. COMMIT — Salve Seu Progresso

**Objetivo:** Criar commits granulares e significativos.

**O que fazer:**
- Commit após completar cada ciclo RED-GREEN-REFACTOR
- Cada commit representa um estado funcional com testes passando
- Opcional: faça commit antes da refatoração como rede de segurança extra
- Use mensagens de commit descritivas que expliquem o comportamento adicionado
- Commits menores e frequentes são melhores que grandes e infrequentes

**Por que é importante:**

**Benefícios de commits frequentes:**
- Reduz o volume médio de trabalho perdido durante reverts
- Cria um histórico alinhado com os casos de teste
- Facilita a revisão de código
- Fornece checkpoints naturais para experimentação
- Conta a história de como a funcionalidade foi construída

**Exemplos de mensagens de commit:**

```bash
# Após RED-GREEN
git commit -m "feat: Add sortArray function with basic implementation"

# Após REFACTOR
git commit -m "refactor: Replace bubble sort with merge sort for better performance"

# Outro ciclo RED-GREEN
git commit -m "feat: Add support for custom sort comparator"
```

**Estratégias de frequência de commit:**

**Estratégia 1: Commit após cada ciclo**
```
RED → GREEN → COMMIT → REFACTOR → COMMIT
```

**Estratégia 2: Commit apenas após refatoração**
```
RED → GREEN → REFACTOR → COMMIT
```

Ambas são válidas. Escolha a que funciona para seu time.

**Perguntas-chave:**
- Todos os testes estão passando?
- Este é um checkpoint lógico?
- Minha mensagem de commit explica claramente o que mudou?
- O commit é pequeno o suficiente para ser revisado facilmente?

---

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

## Naming Conventions para Testes

### Convenção Geral

```
test_<o_que_está_sendo_testado>_<comportamento_esperado>.py
```

### Nomes de Funções de Teste

```python
# Padrão: test_<comportamento>_<condição>_<resultado_esperado>
def test_login_with_valid_credentials_succeeds():
def test_login_with_invalid_password_fails():
def test_login_with_unknown_email_fails():
def test_sort_array_with_duplicates_returns_sorted():
def test_calculate_discount_with_empty_cart_returns_zero():
```

### Estruturas de Nome Sugeridas

| Padrão | Exemplo |
|--------|---------|
| `test_[ação]_[condição]_[resultado]` | `test_process_payment_with_expired_card_fails` |
| `test_[método]_[cenário]_[comportamento]` | `test_calculate_total_with_multiple_items_returns_sum` |
| `test_[feature]_[should]_[expected]` | `test_user_registration_should_create_user` |
| `test_[contexto]__[comportamento]` (separador duplo) | `test_valid_email__returns_true` |

### Nomes de Arquivos de Teste

```
test_<module_name>.py
test_<feature_name>.py
```

Exemplos:

```
test_user_model.py
test_email_validator.py
test_order_processing.py
test_api_authentication.py
```

### Nomes de Classes de Teste (Opcional)

Agrupe testes relacionados em classes com prefixo `Test`:

```python
class TestUserAuthentication:
    def test_login_with_valid_credentials_succeeds(self):
        ...

    def test_login_with_invalid_password_fails(self):
        ...

    def test_login_with_unknown_email_fails(self):
        ...

class TestUserRegistration:
    def test_register_with_valid_data_creates_user(self):
        ...

    def test_register_with_duplicate_email_fails(self):
        ...
```

### Diretrizes de Nomenclatura

- **Descreva o comportamento, não a implementação**
- Seja específico sobre o cenário
- O nome deve permitir identificar o que falhou sem ler o código do teste
- Use verbos no presente (returns, creates, fails)
- Evite nomes genéricos como `test_functionality`

---

## Organização de Testes

### Estrutura de Diretórios Recomendada

```
projeto/
├── src/
│   └── pacote/
│       ├── models/
│       ├── use_cases/
│       ├── controllers/
│       └── repositories/
└── tests/
    ├── unit/                 # Testes rápidos e isolados
    │   ├── test_models.py
    │   ├── test_use_cases.py
    │   └── test_repositories.py
    ├── integration/          # Testes com dependências reais
    │   ├── test_api_endpoints.py
    │   └── test_database.py
    ├── conftest.py           # Fixtures compartilhadas
    └── __init__.py
```

### Testes Unitários vs Testes de Integração

| Aspecto | Testes Unitários | Testes de Integração |
|---------|------------------|----------------------|
| **Escopo** | Unidade isolada (função/classe) | Múltiplos componentes juntos |
| **Velocidade** | Milissegundos | Segundos |
| **I/O** | Nenhum (mocks/repositórios em memória) | Banco real, rede, etc. |
| **Dependências** | Mocks/Stubs/Fakes | Dependências reais |
| **Frequência** | Durante desenvolvimento constante | Antes de commits/push |
| **Exemplo** | Testar validação de email | Testar fluxo completo de registro |

```python
# Teste unitário — rápido, sem I/O
def test_user_password_verification():
    user = User(email="test@example.com", password="secret")
    assert user.verify_password("secret") is True
    assert user.verify_password("wrong") is False

# Teste de integração — usa banco real
def test_save_and_retrieve_user(database_connection):
    repository = UserRepository(database_connection)
    user = User(email="test@example.com")
    repository.save(user)
    retrieved = repository.get_by_email("test@example.com")
    assert retrieved.email == user.email
```

### Fixtures Compartilhadas (conftest.py)

Use `conftest.py` para compartilhar fixtures entre múltiplos arquivos de teste:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def user_repository():
    """Fixture compartilhada disponível para todos os testes."""
    return InMemoryUserRepository()

@pytest.fixture(scope="module")
def database_connection():
    """Conexão de banco com escopo de módulo."""
    conn = create_test_database()
    yield conn
    conn.close()
```

Testes em qualquer arquivo podem usar estas fixtures:

```python
# tests/unit/test_user_service.py
def test_register_user(user_repository):
    service = UserService(user_repository)
    result = service.register("test@example.com", "password")
    assert result.success
```

### Escopos de Fixture no pytest

| Escopo | Ciclo de Vida | Uso Típico |
|--------|---------------|------------|
| `function` (padrão) | Criada para cada função de teste | Objetos simples, sem estado |
| `class` | Uma vez por classe de teste | Setup compartilhado na classe |
| `module` | Uma vez por módulo `.py` | Conexões de banco (read-only) |
| `session` | Uma vez por sessão de teste | Configuração de ambiente |

---

## Quando Testar o Quê

### O Que Testar

| Categoria | O Que Testar | O Que Não Testar |
|-----------|-------------|------------------|
| **Lógica de negócio** | Regras de validação, cálculos, transformações | Código trivial (getters/setters sem lógica) |
| **Casos de borda** | Valores vazios, nulos, limites, extremos | O que a linguagem já garante (tipagem, etc.) |
| **Fluxos de erro** | Exceções esperadas, estados de falha | Código de terceiros/bibliotecas |
| **Integrações** | Contratos com APIs externas (com mocks) | Funcionalidade não implementada ainda |
| **Regressão** | Bugs corrigidos (adicione um teste!) | Comportamento indefinido ou não especificado |

### Quando Aplicar TDD

| Cenário | Recomendação |
|---------|-------------|
| **Nova funcionalidade** | ✅ Sempre — escreva o teste primeiro |
| **Bug fix** | ✅ Escreva um teste que reproduza o bug, depois corrija |
| **Refatoração** | ✅ Tenha testes verdes antes de começar |
| **Prova de conceito (POC)** | ⚠️ Pode ser rápido/sujo, mas teste as bordas |
| **Código exploratório** | ⚠️ Documente descobertas com testes depois |
| **Configuração/scripts** | ❌ Geralmente não vale a pena |

### Prioridade de Casos de Teste

1. **Happy path** (caminho feliz) — o caso de uso principal
2. **Casos de borda** — valores mínimos, máximos, vazios, nulos
3. **Casos de erro** — o que acontece quando algo dá errado
4. **Casos de regressão** — bugs que já foram corrigidos

### Exemplo de Progressão

```python
# 1. Happy path — primeiro teste
def test_add_two_positive_numbers():
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5

# 2. Caso de borda
def test_add_zero():
    calc = Calculator()
    result = calc.add(5, 0)
    assert result == 5

# 3. Números negativos
def test_add_negative_numbers():
    calc = Calculator()
    result = calc.add(-2, -3)
    assert result == -5

# 4. Sinais mistos
def test_add_positive_and_negative():
    calc = Calculator()
    result = calc.add(10, -3)
    assert result == 7
```

---

## 8 Anti-Patterns de TDD

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

## Resumo

**O Ciclo TDD:**
1. **RED** — Escreva um teste que falha primeiro
2. **GREEN** — Faça passar com código mínimo
3. **REFACTOR** — Melhore o design
4. **COMMIT** — Salve o progresso

**Os 8 Anti-Patterns:**

| # | Anti-Pattern | Sintoma | Solução |
|---|--------------|---------|---------|
| 1 | The Liar | Teste sem asserção real | Sempre verifique o resultado |
| 2 | Evergreen Tests | Teste que nunca falhou | Escreva o teste antes do código |
| 3 | Excessive Setup | 50+ linhas de setup | Simplifique o design, use fixtures |
| 4 | Assertion-Free Tests | Nenhum `assert` no teste | Todo teste precisa verificar algo |
| 5 | Fragile Tests | Quebra sem mudança de comportamento | Teste comportamento, não implementação |
| 6 | Slow Tests | Leva segundos para rodar | Separe lógica de I/O |
| 7 | Interdependent Tests | Falha quando roda sozinho | Cada teste é independente |
| 8 | Testing Implementation | Acessa atributos privados | Teste pela interface pública |

**Lembre-se:**
- Testes difíceis de escrever → código difícil de usar
- Refatoração é obrigatória, não opcional
- Testes são documentação executável
- Comece simples, adicione complexidade incrementalmente
- Commit frequente, histórico claro
