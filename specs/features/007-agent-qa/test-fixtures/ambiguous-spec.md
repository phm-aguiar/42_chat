# Test Fixture: Spec Ambígua (BLOCKED)

> Fixture para T005. Spec com ambiguidade intencional — QA deve reportar BLOCKED.

## Contexto (o que o orchestrator enviaria)

### Spec relevante (AMBÍGUA)
Seção 3.1: O sistema deve validar dados de entrada.

Seção 3.2: Dados inválidos devem ser rejeitados.

### Código implementado pelo Dev
(Nenhum — a spec ainda não foi implementada. QA está validando pré-implementação.)

### Task
- **ID:** T003
- **Papel:** QA
- **Descrição:** Validar spec e preparar cenários de teste
- **Arquivos:** (nenhum ainda)

## Critérios de sucesso
1. QA lê a spec e detecta ambiguidade:
   - "validar dados de entrada" — quais dados? formato? constraints?
   - "dados inválidos" — o que define inválido?
2. QA NÃO escreve testes (não sabe o que testar)
3. QA reporta BLOCKED com pergunta específica

## Comportamento ESPERADO (BLOCKED)
```
BLOCKED

Motivo: spec ambígua
Seção 3.1: "validar dados de entrada" não especifica:
- Quais campos validar?
- Quais regras de validação? (tamanho, formato, tipo?)
- Constraints exatas?

Pergunta: quais são as regras de validação de entrada? Especifique campos e constraints.
```
