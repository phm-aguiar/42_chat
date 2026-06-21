# Guia de Escrita Técnica

Referência compartilhada para skills que produzem documentação. Absorvido de `writing-best-practices.md` (AI-Agents-public) + adaptado ao contexto SDD/Go do squad 42_chat.

## Diataxis: Os 4 Tipos de Documentação

| Tipo | Propósito | Exemplo no 42_chat |
|---|---|---|
| **Tutorial** | Ensinar uma skill (learning-oriented) | `wiki-ingest` — passo a passo |
| **How-to** | Resolver um problema (task-oriented) | `git_conventional_commit` — fluxo de commit |
| **Reference** | Informação detalhada (information-oriented) | `architecture-patterns.md` — decision tree |
| **Explanation** | Esclarecer conceitos (understanding-oriented) | `wiki/llm_wiki/SKILL.md` — teoria da wiki |

**Regra:** Um documento = um propósito. Não misture tutorial com referência.

## Estrutura

### Inverted Pyramid (o mais importante primeiro)

1. **O quê** — Descrição rápida e ponto principal
2. **Por quê** — Contexto e benefícios
3. **Como** — Instruções detalhadas
4. **Avançado** — Edge cases e otimizações

### Template de Seção

```markdown
## Nome da Seção

**O quê:** [1 frase]

**Por quê:** [1-2 frases de contexto]

**Como:**
1. [Passo concreto]
2. [Passo concreto]

**Exemplo:**
```linguagem
[código executável]
```

**Output esperado:**
```
[output real]
```
```

## Linguagem e Estilo

### Voz Ativa (sempre)

| Passiva (fraca) | Ativa (forte) |
|---|---|
| "O banco é consultado pela API." | "A API consulta o banco." |
| "O erro foi encontrado durante o deploy." | "O deploy encontrou um erro." |

### Modo Imperativo para Instruções

| Errado | Certo |
|---|---|
| "Você deve instalar as dependências." | "Instale as dependências." |
| "Você pode rodar os testes." | "Rode os testes." |

### Frases Curtas

**Regra:** 15-20 palavras por frase. Uma ideia por frase.

### Linguagem Concreta

| Vago | Específico |
|---|---|
| "A aplicação pode ficar lenta com muitos usuários." | "Tempo de resposta sobe para 2-3s com 1000+ usuários concorrentes." |
| "Use o padrão adequado." | "Use Repository pattern com interface + implementação concreta." |

### Palavras pra Evitar

basicamente, realmente, muito, bastante, apenas, simplesmente, em ordem de, é importante notar que

## Exemplos de Código

### Completos e Executáveis

```go
// Ruim (incompleto)
user.Save()

// Bom (completo)
user := &User{
    Email: "user@example.com",
    Name:  "John Doe",
}
if err := user.Save(ctx); err != nil {
    return fmt.Errorf("saving user: %w", err)
}
```

### Mostrar Caminho Feliz E de Erro

```go
user, err := repo.FindByID(ctx, id)
if err != nil {
    if errors.Is(err, ErrNotFound) {
        return nil, fmt.Errorf("user %d not found", id)
    }
    return nil, fmt.Errorf("finding user: %w", err)
}
```

### Syntax Highlighting Sempre

Especifique a linguagem: `go`, `bash`, `json`, `yaml`, `sql`, `markdown`.

## Checklist de Auto-Edição

### Conteúdo
- [ ] Propósito está claro
- [ ] Nível técnico adequado ao público
- [ ] Informação está correta e atualizada
- [ ] Todos os passos são testáveis
- [ ] Exemplos são completos e executáveis

### Estrutura
- [ ] Fluxo lógico do início ao fim
- [ ] Headings são descritivos e hierárquicos
- [ ] Parágrafos curtos e focados (3-5 frases)
- [ ] Listas usadas apropriadamente (não paredes de texto)

### Linguagem
- [ ] Voz ativa
- [ ] Modo imperativo para instruções
- [ ] Sem jargão sem explicação
- [ ] Sem filler words
- [ ] Terminologia consistente

### Código
- [ ] Syntax highlighting com linguagem especificada
- [ ] Código completo e executável
- [ ] Código explicado (o que faz e por quê)

## Escrever para Scanning

A maioria dos leitores escaneia, não lê palavra por palavra:

- Use headings descritivos (o leitor deve entender a estrutura só pelos headings)
- Parágrafos de 3-5 frases
- Use bullet points e listas numeradas
- Destaque informação chave com **negrito**
- Tabelas para comparações
- Diagramas Mermaid para fluxos complexos
