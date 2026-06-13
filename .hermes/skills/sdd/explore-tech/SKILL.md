---
name: sdd-explore-tech
description: >
  Use when the user asks to map or detect the technology stack of a repository, or to fill
  .github/memory/tech.md. Scans project files (go.mod, package.json, Cargo.toml, pom.xml,
  CI configs, etc.) to detect languages, frameworks, build tools, linters, and test frameworks.
  Trigger keywords: mapear tech stack, explorar tecnologia, preencher tech.md, detectar stack,
  explore tech, what tech does this repo use.
version: 1.1.0
author: phm-aguiar
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SDD, Tech-Stack, Discovery, Project-Analysis]
    related_skills: [sdd-init-repo, sdd-validate]
    category: sdd
    resources:
      - SKILL.md
      - assets/tech-template.md
---

# Explorar Stack Tecnológica (SDD)

## Propósito

Escaneia o repositório para detectar a stack e preencher `.github/memory/tech.md`.

## Pré-requisitos

- `.github/memory/` deve existir (criado por `sdd-init-repo`).

## Fluxo de Execução

### Passo 1: Detectar linguagens e manifestos

Busque por arquivos de manifesto com `search_files`:

| Arquivo | Linguagem |
|---|---|
| `go.mod` | Go |
| `package.json` | Node.js / TypeScript |
| `Cargo.toml` | Rust |
| `pom.xml`, `build.gradle*` | Java/Kotlin |
| `requirements.txt`, `pyproject.toml`, `setup.py` | Python |
| `Gemfile` | Ruby |
| `mix.exs` | Elixir |
| `CMakeLists.txt` | C/C++ |
| `*.csproj`, `*.sln` | .NET |

### Passo 2: Extrair versões e dependências

Para cada manifesto, leia o arquivo e extraia: versão da linguagem, frameworks
principais (dependências), ferramentas de build.

### Passo 3: Detectar CI e ferramentas auxiliares

Escanear por: `.github/workflows/`, linters (`.golangci.yml`, `.eslintrc*`),
Docker (`Dockerfile`, `docker-compose*`), task runners (`Makefile`, `justfile`),
padrões de teste (`_test.go`, `*.test.ts`, `*.spec.ts`).

### Passo 4: Consolidar e escrever tech.md

Carregue o template:

```
skill_view(name="sdd-explore-tech", file_path="assets/tech-template.md")
```

Preencha com os dados coletados. Use `—` para entradas não encontradas.
Escreva em `.github/memory/tech.md`.

### Passo 5: Reportar

Resuma o que foi detectado. Pergunte se o usuário quer ajustar algo.

## Guardrails

- **Nunca invente:** apenas o que foi detectado em arquivos reais.
- **Campos vazios = `—`:** não preencha com suposições.
- **Se tech.md já existe:** pergunte se sobrescreve ou mescla.
- **Nenhum manifesto encontrado:** alerte — o repo pode estar vazio ou usar
  linguagem não suportada pela detecção automática.

## Verificação

- [ ] `.github/memory/tech.md` existe com todas as seções do template
- [ ] Cada entrada tem fonte (arquivo detectado) ou `—`
- [ ] Nenhuma dependência foi inventada
- [ ] Usuário pode ajustar manualmente se algo faltar
