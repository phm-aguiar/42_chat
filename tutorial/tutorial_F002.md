# Tutorial — Feature 002: Wiki Experiential Memory

> **Status:** ✅ Implementado em `.hermes/skills/wiki/experiential_memory/`

A 002 é infraestrutura — tu interage via comandos CLI. Não muda teu pipeline
SDD, mas os resultados aparecem nele automaticamente.

---

## Comandos do dia a dia

### 1. Indexar a wiki

```bash
python3 .hermes/skills/wiki/experiential_memory/cli_index.py --full
```

Na primeira vez instala o `sentence-transformers` + baixa o modelo
(`all-MiniLM-L6-v2`). Depois indexa tudo em < 30s.

Saída típica:

```
Indexados 312 chunks de 84 documentos em 18.3s
```

### 2. Busca semântica

```bash
python3 .hermes/skills/wiki/experiential_memory/cli_query.py \
  --semantic "autenticação OAuth2 com JWT" --top-k 5
```

Retorna os chunks mais relevantes por similaridade de embedding, não por
palavra-chave. Mesmo que "JWT" não apareça no texto, se o conceito for
similar semanticamente, ele acha.

### 3. Destilar (quando acumular > 30 chunks)

```bash
python3 .hermes/skills/wiki/experiential_memory/cli_distill.py
```

Agrupa chunks redundantes, gera versões canônicas. Saída típica:

```
Destilados 200 → 138 chunks (-31%). 8 padrões canônicos gerados.
```

---

## Como aparece no pipeline SDD (transparente)

### No sdd-generate-tasks

Quando tu gera tasks com a wiki indexada, o spec.md é embeddado, o índice
retorna top-5 chunks similares (de features passadas, papers, decisões
arquiteturais), e eles são injetados como `experiential_prior` no prompt.

**Resultado:** G₀ nasce mais completo. Tasks que seriam descobertas
dinamicamente (Discover) já vêm prontas. ~30% menos tokens.

### No sdd-brainstorm

Quando tu brainstorma uma feature, o índice já recupera contexto de features
similares automaticamente:

```
> "vamos fazer um forum"
[índice encontra: wiki/features/forum/spec.md chunks, wiki/concepts/jschan.md]
[injeta como contexto pro brainstorm]
```

### No sdd-validate (feedback loop)

Após executar a feature, as métricas do LATTE viram utility signal:

- Feature rodou limpa (poucos overwrites) → chunks usados ganham +0.1
- Feature problemática → chunks perdem -0.05
- Chunks não usados por várias features → decay de 0.01 por feature

Com o tempo, o top-5 fica cada vez mais relevante porque só o que realmente
funciona sobe.

---

## Quando usar o quê

| Situação | Comando |
|---|---|
| Primeira vez ou wiki mudou muito | `cli_index.py --full` |
| Feature específica nova | `generate-tasks --with-memory` |
| Pesquisar algo na wiki | `cli_query.py --semantic "termos"` |
| Acumulou muitas features | `cli_distill.py` |
| Só quer ver se o índice existe | `cli_index.py --status` |

---

## Resumo

- **Setup único:** `cli_index.py --full` depois que a wiki estiver povoada
- **Default:** use `--with-memory` no generate-tasks
- **Manutenção:** `cli_distill.py` de vez em quando (ou via cron)
- **Zero esforço:** feedback loop é automático via sdd-validate

---

## Rodar os testes

```bash
cd /home/zeenyt__/Projetos/42_chat/.hermes/skills/wiki/experiential_memory
PYTHONPATH=.. python3 tests/test_reindex_idempotent.py
PYTHONPATH=.. python3 tests/test_index_coverage.py
```
