# Stack Tecnológica

> Preenchido via `sdd-explore-tech` + input do usuário em 2026-06-07.
> Reexecute `sdd-explore-tech` para atualizar conforme novos artefatos forem adicionados.

## Linguagens
| Linguagem | Versão | Detecção |
|---|---|---|
| Go | a definir (go.mod pendente) | input do usuário + CI Go workflow |
| JavaScript/TypeScript | a definir (package.json pendente) | input do usuário |

## Frameworks e Bibliotecas

### Backend
| Nome | Versão | Propósito |
|---|---|---|
| Gorilla WebSocket | a definir | WebSocket server |
| pgx | a definir | Driver PostgreSQL para Go |

### Frontend
| Nome | Versão | Propósito |
|---|---|---|
| Vite | a definir | Build tool / dev server React |
| Chatscope (chat-ui-kit-react) | a definir | Componentes de chat prontos |
| Tailwind CSS | a definir | Alternativa ao Chatscope (template gratuito) |

## Banco de Dados
| Nome | Versão | Propósito |
|---|---|---|
| PostgreSQL | a definir | Banco de dados principal |
| pgx | a definir | Driver/connector Go para PostgreSQL |

## Ferramentas de Build e Teste
| Ferramenta | Comando | Arquivo de Config |
|---|---|---|
| Go test | `go test ./...` | — |
| Go build | `go build ./...` | go.mod (pendente) |

## CI/CD
| Plataforma | Pipeline | Gatilhos |
|---|---|---|
| GitHub Actions | go-ci.yml | PRs para develop e main |
| GitHub Actions | enforce-branch-flow.yml | PRs para main e develop |
| GitHub Actions | auto-pr-feature-to-develop.yml | push em feature/* |
| GitHub Actions | auto-pr-to-main.yml | push em develop |

## Infraestrutura
| Ferramenta | Arquivos |
|---|---|
| Docker | Dockerfile (pendente) |
| Docker Compose | docker-compose.yml (pendente) |

## Linting e Formatação
| Ferramenta | Config |
|---|---|
| — | — |

## Atualizado em
2026-06-07
