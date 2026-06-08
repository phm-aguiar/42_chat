# spec.md: Templates Canônicos dos Artefatos SDD

## 1. Visão Geral e Intenção de Negócios

- **Funcionalidade:** Definição dos formatos padronizados para todos os artefatos do ciclo SDD.
- **Objetivo:** Garantir que spec.md, plan.md, tasks.md, AGENTS.md e llms.txt sigam uma estrutura consistente, facilitando a leitura por agentes de IA e a validação automatizada.

## 2. Histórias de Usuário e Comportamento (BDD)

- **Como** desenvolvedor, **Quero** um template canônico de spec.md, **Para que** toda feature seja especificada com o mesmo nível de rigor e seções previsíveis.
- **Como** agente de IA, **Quero** artefatos com seções semanticamente estáveis, **Para que** eu possa mapear conteúdo automaticamente sem ambiguidade.
- **Cenário Principal:**
  - *Dado* que uma nova feature é iniciada,
  - *Quando* os artefatos são criados a partir dos templates,
  - *Então* todas as seções obrigatórias estão presentes e os placeholders estão identificados.

## 3. Limites, Restrições e Não-Funcionais

- **Agnóstico de Stack:** Os templates não devem conter referências a linguagens ou frameworks específicos. Use placeholders `{{...}}`.
- **Placeholders Obrigatórios:** Informações pendentes devem ser marcadas com `{{...}}` ou ``. O agente NUNCA deve preenchê-las sem confirmação do usuário.
- **Idempotência:** O refatorador (`sdd-refactor-artifact`) deve preservar 100% do conteúdo original. Seções sem correspondência vão para `## Notas Adicionais`.
- **Checklist de Ambiguidade:** Toda spec.md deve terminar com uma checklist. Itens vazios indicam ambiguidades não resolvidas.

## 4. Checklist de Ambiguidade para a IA

- [ ] Os templates devem incluir `plan.md` dentro do `spec.md` como apêndice ou como arquivo separado?
- [ ] O formato do `tasks.md` deve usar numeração `T001` sequencial global ou reiniciar por fase?
- [ ] O `llms.txt` deve ser gerado automaticamente a partir dos demais artefatos ou mantido manualmente?

---

# Apêndice: Templates de Exemplo

## A. Template de spec.md (Especificação Funcional)

```markdown
# spec.md: {{TÍTULO}}

## 1. Visão Geral e Intenção de Negócios
- **Funcionalidade:** {{descrição curta}}
- **Objetivo:** {{valor de negócio}}

## 2. Histórias de Usuário e Comportamento (BDD)
- **Como** {{ator}}, **Quero** {{ação}}, **Para que** {{objetivo}}.
- **Cenário Principal:**
  - *Dado* que {{precondição}},
  - *Quando* {{evento}},
  - *Então* {{resultado}}.

## 3. Limites, Restrições e Não-Funcionais
- **Segurança:** {{regras}}
- **Performance:** {{SLAs}}

## 4. Checklist de Ambiguidade para a IA
- [ ] {{pergunta pendente}}
```

## B. Template de plan.md (Plano Arquitetural — ADR Vivo)

```markdown
# plan.md: Plano de Implementação Técnica

## 1. Metadados do Plano
- **Stack Tecnológico:** {{linguagens, frameworks, versões}}
- **Feature Fonte:** `specs/features/{{id}}-{{nome}}/spec.md`

## 2. Design de Contratos e Fronteiras
- **Contrato:** {{contratos formais afetados}}
- **Geração de Código:** {{ferramentas de codegen, se aplicável}}

## 3. Decisões Arquiteturais e Justificativas
- **Decisão:** {{o que foi decidido}}
- **Alternativa Rejeitada:** {{o que foi descartado e por quê}}

## 4. Auditoria de Constituição
- [ ] {{checklist de conformidade com constitution.md}}
```

## C. Template de tasks.md (Matriz de Execução)

```markdown
# tasks.md: Lista de Execução

## Fase 1: {{nome da fase}}
- [ ] **T{{nnn}}:** {{descrição}} (Depende de T{{nnn}})

## Fase 2: {{nome da fase}}
- [ ] **T{{nnn}}:** {{descrição}}
```

## D. Template de AGENTS.md (Seção SDD Workflow)

```markdown
## SDD Workflow

Este repositório utiliza Spec-Driven Development (SDD).

### Comportamento Fundamental
- NUNCA inicie implementação sem `spec.md`, `plan.md` e `tasks.md`.
- NUNCA preencha placeholders `{{...}}` sem confirmação do usuário.
- Siga a ordem do `tasks.md`. Marque concluídas com `[x]`.

### Tecnologias e Padrões
- Consulte `.github/memory/tech.md` para stack homologado.
- Consulte `.github/memory/constitution.md` para portões de qualidade.
```

## E. Template de llms.txt (Navegação para LLMs)

```markdown
# {{NOME_DO_PROJETO}}
> {{descrição}}

## Navegação
- `/specs/features/`: SSOT — features modeladas aqui antes do código.
- `/specs/domain-events/`: Contratos formais (AsyncAPI, OpenAPI).
- `.github/memory/constitution.md`: Princípios invioláveis.
- `.github/memory/tech.md`: Stack homologado.

## Camadas de Código
- {{estrutura e propósito}}

## Links
- [Constituição](.github/memory/constitution.md)
- [Stack](.github/memory/tech.md)
```
