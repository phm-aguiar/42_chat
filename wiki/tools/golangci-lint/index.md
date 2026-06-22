---
title: "golangci-lint"
description: "Documentação do golangci-lint — fast Go linters runner"
created: 2026-06-21
rag_score: 0.5
tags: [golangci-lint, go, linting, index]
---

# golangci-lint

Fast Go linters runner. Documentação ingerida do site oficial e repositórios relacionados.

## Getting Started

- [Quick Start](Quick%20Start.md) — Como executar o golangci-lint
- [Install](Install.md) — Instalação para CI, local, Docker, e package managers
- [Integrations](Integrations.md) — Integração com editores (VS Code, Vim, Emacs, GoLand) e CI

## Configuração & Uso

- [Configuration](Configuration.md) — Configuração completa: linters, issues, output, run, severity
- [Linters](Linters.md) — Lista completa de linters suportados com opções de configuração
- [False Positives](False%20Positives.md) — Como lidar com falsos positivos e exclusões
- [False Positives 1](False%20Positives%201.md) — (Duplicado) Falsos positivos e exclusões
- [Debugging](Debugging.md) — Debug com `-v` e `GL_DEBUG`

## Contribuindo

- [Architecture](Architecture.md) — Arquitetura interna: init, load, run, postprocess, print
- [New linters](New%20linters.md) — Como adicionar linters públicos ou privados
- [Website architecture](Website%20architecture.md) — Gatsby, MDX, estrutura do site

## Referências Externas

- [guide/.golangci.yml at master](guide.golangci.yml%20at%20master.md) — Configuração do Uber Go Style Guide
- [goleak package](goleak%20package%20-%20go.uber.org_goleak.md) — Detector de vazamento de goroutines (go.uber.org/goleak)
