---
title: "Metodologia TDD — Test-Driven Development"
summary: "Referência completa sobre a metodologia TDD: ciclo Red-Green-Refactor-Commit, princípios FIRST, padrão AAA (Arrange-Act-Assert), nomenclatura e organização de testes, e os 8 anti-patterns mais comuns com exemplos práticos em Python/pytest."
tags: [tdd, testing, pytest, reference]
category: references
created: "2026-06-13"
rag_score: 0.48
updated: "2026-06-15"
lifecycle: reviewed
lifecycle_changed: "2026-06-15"
lifecycle_reason: "auto-promoted by wiki-lint: well-established reference page"
sources:
  - "wiki/_raw/qa/tdd/Test-Driven Development (TDD).md"
  - "wiki/_raw/qa/tdd/TDD Workflow Guide.md"
  - "wiki/_raw/qa/tdd/TDD Anti-Patterns Reference.md"
---

# Metodologia TDD — Test-Driven Development


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


## Princípios FIRST e Padrão AAA

> **Movido para:** [[references/tdd-first-principles|TDD FIRST Principles & AAA Pattern]] — Consulte a página dedicada para o detalhamento completo dos princípios FIRST (Fast, Isolated, Repeatable, Self-Validating, Timely) e do padrão Arrange-Act-Assert com exemplos em Python/pytest.

## Anti-Patterns de TDD

> **Movido para:** [[references/tdd-anti-patterns|TDD Anti-Patterns]] — Consulte o catálogo completo dos 8 anti-patterns: The Liar, Excessive Setup, The Giant, The Mockery, The Inspector, The Slow Poke, The Generous Leftovers, e The Free Ride. Cada entrada inclui problema, exemplo ruim, diagnóstico e solução com código Python/pytest.

## Ver Também

- [[references/tdd-first-principles|TDD FIRST Principles & AAA Pattern]] — Princípios e organização de testes
- [[references/tdd-anti-patterns|TDD Anti-Patterns]] — Catálogo de anti-patterns
- [[references/bdd-specification-process|BDD Spec Process]] — BDD complementa TDD
- [[references/qa-overview|QA Overview]] — Estratégia de QA no framework SDD
- [[references/recipe-step-executor|Recipe Step Executor]] — Executor de workflows com TDD
