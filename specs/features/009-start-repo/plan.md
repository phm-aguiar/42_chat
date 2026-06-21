# plan.md: Plano de Implementação Técnica — Estrutura SDD do Repositório

## 1. Metadados do Plano

- **Stack Tecnológico:** Go (principal), Docker, GitHub Actions — agnóstico e extensível.
- **Feature Fonte:** `specs/features/009-start-repo/spec.md`
- **Escopo:** Estrutura física de diretórios `.github/memory/`, `specs/` e atualização de `AGENTS.md`.

## 2. Design de Contratos e Fronteiras

- **Contrato:** Nenhum contrato formal (AsyncAPI/OpenAPI) neste estágio. A estrutura em si é o contrato.
- **Convenção de Nomes:** Features em `/specs/features/` seguem `<id numérico>-<slug kebab-case>`. IDs são sequenciais e imutáveis.
- **Artefatos por Feature:** Toda feature deve conter `spec.md`, `plan.md`, `tasks.md`. A ausência de qualquer um bloqueia implementação.

## 3. Decisões Arquiteturais e Justificativas

- **Decisão:** `.github/memory/` como local canônico para constitution.md e tech.md.
  - **Justificativa:** `.github/` já é reconhecido pelo ecossistema GitHub (CI, templates). Adicionar `memory/` mantém coesão.
  - **Alternativa Rejeitada:** Colocar na raiz (`/constitution.md`, `/tech.md`). Rejeitada por poluir a raiz e confundir com docs de usuário.

- **Decisão:** `specs/` como raiz única das especificações, não `docs/specs/` ou `design/`.
  - **Justificativa:** Nome curto, semântica clara, facilita paths como `specs/features/001-nome/spec.md`.
  - **Alternativa Rejeitada:** `docs/` — ambíguo (mistura docs de usuário com specs técnicas).

- **Decisão:** AGENTS.md na raiz, não em `.github/AGENTS.md`.
  - **Justificativa:** Ferramentas como opencode e Claude Code esperam AGENTS.md na raiz por convenção.

## 4. Auditoria de Constituição

- [x] A estrutura respeita a separação specs vs código derivado? Sim — `specs/` é independente da stack.
- [x] A estrutura é agnóstica de linguagem? Sim — nenhuma referência a Go, Java, etc. nos diretórios SDD.
- [x] Modificações no código derivado exigem artefatos SDD? Sim — AGENTS.md será atualizado com essa regra.
