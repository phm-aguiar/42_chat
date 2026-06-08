---
name: sdd-explore-tech
description: Use when the user asks to map or detect the technology stack of a repository, or to fill .github/memory/tech.md. Scans project files (go.mod, package.json, Cargo.toml, pom.xml, CI configs, etc.) to detect languages, frameworks, build tools, linters, and test frameworks. Trigger keywords: "mapear tech stack", "explorar tecnologia", "preencher tech.md", "detectar stack", "explore tech", "what tech does this repo use".
---

# Explorar Stack Tecnológica (SDD)

## Propósito

Esta skill escaneia o repositório para detectar automaticamente a stack tecnológica e preencher `.github/memory/tech.md` — o documento que centraliza o controle do stack no modelo SDD.

## Pré-requisitos

- Diretório `.github/memory/` deve existir (criado pelo `sdd-init-repo`). Se não existir, crie-o antes de prosseguir.

## Fluxo de Execução

### Passo 1: Detectar linguagens e manifestos

Escanear a raiz do projeto em busca de arquivos de manifesto:

| Arquivo | Linguagem/Ecossistema |
|---|---|
| `go.mod` | Go |
| `package.json` | Node.js / TypeScript |
| `Cargo.toml` | Rust |
| `pom.xml` | Java (Maven) |
| `build.gradle*` | Java/Kotlin (Gradle) |
| `requirements.txt`, `pyproject.toml`, `setup.py` | Python |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |
| `CMakeLists.txt` | C/C++ |
| `*.csproj`, `*.sln` | .NET |

Use `glob` para buscar cada um. Anote todos os encontrados (projetos multi-linguagem são possíveis).

### Passo 2: Extrair versões e dependências

Para cada manifesto encontrado, leia o arquivo e extraia:
- **Versão da linguagem** (ex: `go 1.22` do `go.mod`, `"node": ">=18"` do `package.json`)
- **Frameworks principais** (ex: dependências no `go.mod`, `dependencies` no `package.json`)
- **Ferramentas de build** (ex: `Makefile`, scripts no `package.json`, tasks no `go.mod`)

### Passo 3: Detectar CI e ferramentas auxiliares

Escanear por:
- `.github/workflows/` — CI pipeline, triggers, jobs
- `.golangci.yml`, `.eslintrc*`, `.prettierrc*` — linters/formatters
- `Dockerfile`, `docker-compose*` — containerização
- `Makefile`, `justfile`, `Taskfile*` — task runners
- Ferramentas de teste: `_test.go`, `*.test.ts`, `*Test.java`, `test_*.py`, `*.spec.ts`

### Passo 4: Consolidar e escrever tech.md

Leia o template em `assets/tech-template.md` e preencha com os dados coletados.

Escreva o resultado em `.github/memory/tech.md` com a seguinte estrutura:

```markdown
# Stack Tecnológica

## Linguagens
| Linguagem | Versão | Detecção |
|---|---|---|
| Go | 1.22 | go.mod |

## Frameworks e Bibliotecas
| Nome | Versão | Propósito |
|---|---|---|

## Ferramentas de Build e Teste
| Ferramenta | Comando | Arquivo de Config |
|---|---|---|

## CI/CD
| Plataforma | Pipeline | Gatilhos |
|---|---|---|

## Linting e Formatação
| Ferramenta | Config |
|---|---|

## Infraestrutura
| Ferramenta | Arquivos |
|---|---|

## Atualizado em
YYYY-MM-DD
```

### Passo 5: Reportar

Apresente um resumo do que foi detectado. Pergunte ao usuário se deseja ajustar algo antes de finalizar.

## Guardrails

- **Nunca invente**: reporte apenas o que foi realmente detectado nos arquivos.
- **Campos vazios são OK**: use `—` para entradas não encontradas. Não preencha com suposições.
- **Se `.github/memory/tech.md` já existe**: pergunte ao usuário se deve sobrescrever ou mesclar.
- **Se nenhum manifesto for encontrado**: alerte o usuário. O repositório pode estar vazio ou usar uma linguagem não suportada pela detecção automática.
