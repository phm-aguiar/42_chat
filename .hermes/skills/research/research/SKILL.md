---
name: research
description: >
  Toolkit consolidado de pesquisa. 6 modos: arxiv (papers acadêmicos), blogwatch (RSS/blogs),
  polymarket (mercados de predição), paper-write (papers ML), defuddle (extração web limpa),
  youtube (transcrição e resumo de vídeos).
version: 1.0.0
author: phm-aguiar (consolidação feature 008-reavaliacao-skills)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, arxiv, papers, rss, blogs, polymarket, prediction-markets, youtube]
    category: research
    modes:
      - arxiv
      - blogwatch
      - polymarket
      - paper-write
      - defuddle
      - youtube
    resources:
      - SKILL.md
    umbrella_for:
      - arxiv
      - blogwatcher
      - polymarket
      - research-paper-writing
      - defuddle
      - youtube-content
---

# research — Toolkit de Pesquisa (6 modos)

> Toolkit unificado de pesquisa acadêmica, monitoramento de conteúdo, mercados de predição e escrita científica. Cada modo cobre um domínio específico.

## Índice de Modos

| Modo | Gatilho | Domínio |
|---|---|---|
| `arxiv` | Buscar/sumarizar papers, citações, BibTeX | Papers acadêmicos |
| `blogwatch` | Monitorar blogs/RSS, listar artigos | Conteúdo web |
| `polymarket` | Consultar odds, mercados de predição | Prediction markets |
| `paper-write` | Escrever papers ML (NeurIPS/ICML/ICLR) | Escrita científica |
| `defuddle` | Extrair conteúdo limpo de URLs | Web scraping |
| `youtube` | Transcrever e resumir vídeos | Conteúdo multimídia |

---

## Modo: arxiv

**Gatilho:** Buscar papers no arXiv, descobrir citações, gerar BibTeX, avaliar impacto de artigos científicos.

### Fluxo

1. **Buscar papers no arXiv** (API REST, sem auth):
   ```bash
   curl -s "https://export.arxiv.org/api/query?search_query=all:QUERY&max_results=5&sortBy=submittedDate&sortOrder=descending"
   ```
   - Prefixos: `all:` (tudo), `ti:` (título), `au:` (autor), `abs:` (abstract), `cat:` (categoria)
   - Operadores: `+` (AND), `OR`, `ANDNOT`
   - Parse XML com script helper: `python scripts/search_arxiv.py "QUERY" --max 10`

2. **Avaliar impacto** via Semantic Scholar API (JSON, 1 req/s):
   ```bash
   curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=title,citationCount,influentialCitationCount,year"
   ```
   Campos úteis: `citationCount`, `referenceCount`, `influentialCitationCount`, `isOpenAccess`, `openAccessPdf`, `externalIds`

3. **Citações e referências:**
   ```bash
   # Quem citou este paper
   curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/citations?fields=title,authors,year&limit=10"
   # O que este paper cita
   curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID/references?fields=title,authors,year&limit=10"
   ```

4. **Ler conteúdo do paper:**
   - Abstract: `web_extract(urls=["https://arxiv.org/abs/ID"])`
   - PDF completo: `web_extract(urls=["https://arxiv.org/pdf/ID"])`

5. **Gerar BibTeX** (programaticamente, nunca de memória):
   ```bash
   curl -s "https://export.arxiv.org/api/query?id_list=ID" | python3 -c "
   import sys, xml.etree.ElementTree as ET
   ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
   root = ET.parse(sys.stdin).getroot()
   entry = root.find('a:entry', ns)
   # ... extrair title, authors, year, id, primary_category
   # ... formatar @article{...}
   "
   ```

### Categorias comuns

| Categoria | Campo |
|-----------|-------|
| `cs.AI` | Inteligência Artificial |
| `cs.CL` | NLP / Computação e Linguagem |
| `cs.CV` | Visão Computacional |
| `cs.LG` | Machine Learning |
| `stat.ML` | ML (Estatística) |

### Pitfalls

- **Citações alucinadas**: ~40% erro em citações geradas por LLM. Sempre buscar BibTeX via DOI/arXiv API programaticamente.
- **Versões de arXiv ID**: `1706.03762` sempre resolve para versão mais recente. Use `1706.03762v1` para versão imutável. Preserve o sufixo na citação.
- **Papers retirados**: `<summary>` contém aviso de retirada — verificar antes de tratar como paper válido.
- **Rate limits**: arXiv ~1 req / 3 segundos. Semantic Scholar 1 req / segundo (100/s com API key).
- **PDF vs Abstract**: `arxiv.org/pdf/ID` vs `arxiv.org/abs/ID` — não confundir.

---

## Modo: blogwatch

**Gatilho:** Adicionar blogs para monitorar, escanear feeds RSS/Atom, listar artigos não lidos, importar OPML.

### Pré-requisito

Instalar `blogwatcher-cli`:
```bash
go install github.com/JulienTant/blogwatcher-cli/cmd/blogwatcher-cli@latest
```

### Fluxo

1. **Adicionar blogs:**
   ```bash
   blogwatcher-cli add "Nome do Blog" https://example.com
   blogwatcher-cli add "Nome" https://example.com --feed-url https://example.com/feed.xml
   blogwatcher-cli add "Nome" https://example.com --scrape-selector "article h2 a"
   ```
   Auto-descobre feeds RSS/Atom da homepage. Fallback para HTML scraping se configurado.

2. **Escanear por novos artigos:**
   ```bash
   blogwatcher-cli scan              # Todos os blogs
   blogwatcher-cli scan "Nome"       # Blog específico
   ```

3. **Listar artigos:**
   ```bash
   blogwatcher-cli articles                  # Não lidos
   blogwatcher-cli articles --all            # Todos
   blogwatcher-cli articles --blog "Nome"    # Filtro por blog
   blogwatcher-cli articles --category "Eng" # Filtro por categoria
   ```

4. **Marcar como lido:**
   ```bash
   blogwatcher-cli read 1              # Artigo #1
   blogwatcher-cli read-all            # Todos
   blogwatcher-cli read-all --blog "Nome" --yes
   ```

5. **Importar/gerenciar:**
   ```bash
   blogwatcher-cli import subscriptions.opml  # OPML (Feedly, Inoreader, etc.)
   blogwatcher-cli blogs                      # Listar blogs monitorados
   blogwatcher-cli remove "Nome" --yes         # Remover blog
   ```

### Configuração

| Variável | Descrição |
|----------|-----------|
| `BLOGWATCHER_DB` | Caminho do SQLite (default: `~/.blogwatcher-cli/blogwatcher-cli.db`) |
| `BLOGWATCHER_WORKERS` | Workers de scan concorrentes (default: 8) |
| `BLOGWATCHER_SILENT` | Apenas "scan done" ao escanear |

### Pitfalls

- DB em container Docker é perdido no restart — usar volume mount ou `BLOGWATCHER_DB` para persistir.
- Migrando do blogwatcher original (`Hyaxia/blogwatcher`): mover `~/.blogwatcher/blogwatcher.db` → `~/.blogwatcher-cli/blogwatcher-cli.db`.
- Nome do binário é `blogwatcher-cli`, não `blogwatcher`.

---

## Modo: polymarket

**Gatilho:** Consultar odds de eventos, probabilidades de mercado, preços de outcomes, volume de mercados de predição.

### APIs (read-only, sem auth)

| API | URL | Função |
|-----|-----|--------|
| Gamma | `gamma-api.polymarket.com` | Busca, descoberta |
| CLOB | `clob.polymarket.com` | Preços, orderbooks |
| Data | `data-api.polymarket.com` | Trades, open interest |

### Fluxo

1. **Buscar mercados** via Gamma API:
   ```bash
   curl -s "https://gamma-api.polymarket.com/events?tag=QUERY&limit=5"
   curl -s "https://gamma-api.polymarket.com/markets?tag=QUERY&limit=5"
   ```

2. **Apresentar resultados:**
   - `outcomePrices` como porcentagens: `"[\"0.652\", \"0.348\"]"` → "Yes: 65.2%, No: 34.8%"
   - Incluir volume (USDC), pergunta do mercado, data de fechamento
   - Exemplo: `"Will X happen?" — 65.2% Yes ($1.2M volume)`

3. **Deep dive** (se solicitado):
   - Orderbook: usar `clobTokenIds` para consultar CLOB API
   - Histórico: usar `conditionId` para consultar Data API
   - Ver `references/api-endpoints.md` na skill original `polymarket` para endpoints completos

### Conceitos chave

- **Events** contêm 1 ou mais **Markets** (1:many)
- Preços SÃO probabilidades: preço 0.65 = 65% de chance
- `outcomePrices`: JSON string com array `["YesPrice", "NoPrice"]` (double-encoded)
- `clobTokenIds`: JSON string com array de 2 token IDs `[Yes, No]`
- Volume em USDC

### Pitfalls

- Campos `outcomePrices`, `outcomes`, `clobTokenIds` são **double-encoded JSON strings** dentro da resposta JSON. Parse com `json.loads(market['outcomePrices'])` em Python.
- Apenas leitura — trading requer autenticação cripto (EIP-712).
- Mercados novos podem ter histórico de preço vazio.
- Restrições geográficas para trading, mas dados são globalmente acessíveis.
- Rate limits generosos (4000-9000 req/10s).

---

## Modo: paper-write

**Gatilho:** Escrever paper ML para NeurIPS/ICML/ICLR/ACL/AAAI/COLM. Ciclo completo: experimentos → análise → escrita → review → submissão.

### Filosofia central

1. **Paper é uma história, não uma coleção de experimentos.** Uma contribuição clara em uma frase.
2. **Nunca alucinar citações.** Buscar BibTeX programaticamente. Marcar não verificáveis como `[CITATION NEEDED]`.
3. **Experimentos servem claims.** Cada experimento deve explicitamente declarar qual claim suporta.
4. **Commit early, commit often.** Git log é o histórico de experimentos.

### Fases do pipeline

#### Fase 1: Literature Review
1. Buscar papers relacionados: modo `arxiv` + Semantic Scholar.
2. Busca iterativa (breadth-first, depois depth): 4-6 queries paralelas → refinar com termos descobertos → preencher gaps (2-3 rounds).
3. **Verificar cada citação** (5 passos obrigatórios): Search → Verify (2+ fontes) → Retrieve (DOI→BibTeX) → Validate (claim existe no paper) → Add.
4. Organizar related work por metodologia, não paper-por-paper.

#### Fase 2: Experiment Design
1. Mapear claims → experimentos explicitamente.
2. Baselines: naive, strong, ablações, compute-matched.
3. Definir métricas, agregação, testes estatísticos, sample sizes antes de rodar.
4. Scripts com: incremental saving (skip completed), artifact preservation, separation of concerns.

#### Fase 3: Execution & Monitoring
1. `nohup python run.py > logs/exp.log 2>&1 &` para experimentos longos.
2. Monitorar com cron: checar PID, tail logs, verificar resultados, commitar.
3. Manter `experiment_journal.jsonl` — árvore de exploração com hipóteses, resultados, decisões.

#### Fase 4: Analysis
1. Agregar resultados, calcular estatísticas (McNemar, bootstrap CI, Cohen's d/h).
2. Identificar a história: 1 frase com o achado principal, surpresas, falhas, follow-ups.
3. Criar `experiment_log.md` — ponte entre resultados brutos e a escrita.

#### Fase 5: Paper Drafting
1. **Ordem**: título → Figure 1 → abstract (5 sentenças) → introduction → methods → experiments → related work → conclusion → limitations.
2. Abstract: (1) o que alcançou, (2) por que é difícil/importante, (3) como fez, (4) evidência, (5) número mais impactante.
3. Two-pass refinement: write+refine per section → global refinement com contexto do paper completo.
4. LaTeX: `booktabs` para tabelas, vetor (PDF) para figuras, `microtype` sempre, `cleveref` após `hyperref`.
5. Cores colorblind-safe: paleta Okabe-Ito.

#### Fase 6: Self-Review
1. Simular reviews com 3-5 revisores (modelos diferentes, viés negativo).
2. Meta-reviewer agrega → reflection loop (2-3 rounds).
3. Claim verification pass: sub-agente fresco verifica cada número contra resultados brutos.
4. Se tiver VLM: revisão visual do PDF compilado.

#### Fase 7: Submission
1. Checklists: venue-specific (NeurIPS 16 itens, ICML broader impact, ICLR LLM disclosure).
2. Anonimização: sem nomes, sem GitHub pessoal (usar anonymous.4open.science), self-citações em 3ª pessoa.
3. Pré-compilação: `chktex`, verificar `\cite` vs `.bib`, checar figuras existem, labels duplicados.
4. Compilar: `latexmk -pdf main.tex`.
5. arXiv timing: postar APÓS deadline para venues double-blind. ICLR permite antes.

### Pitfalls

- **Escrever paper sem contribuição clara de 1 frase**: se não consegue resumir em 1 frase, o paper não está pronto.
- **Alucinar BibTeX**: SEMPRE fetch via DOI/arXiv API. ~40% de erro em citações geradas de memória.
- **Deletar conteúdo do template antes de entender a estrutura**: manter exemplo como comentário.
- **Copiar só `.tex` sem `.sty`**: não compila. Copiar diretório todo do template.
- **Tabelas sem booktabs, figuras raster (PNG) em vez de vetor (PDF)**: usar `booktabs` e `savefig('fig.pdf')`.
- **Pular limitations section**: obrigatório em todos os venues principais.
- **Números no texto que não batem com resultados reais**: rodar claim verification pass com sub-agente fresco.
- **Estimar compute budget sem contingência**: adicionar 30-50% para re-runs.

---

## Modo: defuddle

**Gatilho:** Extrair conteúdo limpo de qualquer URL (artigos, docs, blogs). Remove navegação, ads, clutter. Prefira sobre WebFetch para páginas web.

### Pré-requisito

```bash
npm install -g defuddle
```

### Fluxo

1. **Extrair markdown:**
   ```bash
   defuddle parse <url> --md
   ```

2. **Salvar em arquivo:**
   ```bash
   defuddle parse <url> --md -o content.md
   ```

3. **Extrair metadados específicos:**
   ```bash
   defuddle parse <url> -p title
   defuddle parse <url> -p description
   defuddle parse <url> -p domain
   ```

### Formatos de saída

| Flag | Formato |
|------|---------|
| `--md` | Markdown (recomendado) |
| `--json` | JSON com HTML + markdown |
| (sem flag) | HTML |
| `-p <nome>` | Propriedade específica |

### Pitfalls

- **Não usar para URLs terminadas em `.md`** — já são markdown, usar WebFetch direto.
- **URLs com paywall** podem retornar conteúdo truncado ou bloqueado.

---

## Modo: youtube

**Gatilho:** Transcrever vídeo do YouTube e converter em resumos, threads, blog posts, capítulos.

### Pré-requisito

```bash
uv pip install youtube-transcript-api
```

### Fluxo

1. **Buscar transcrição:**
   ```bash
   uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only --timestamps
   ```
   Suporta: URLs padrão, `youtu.be`, shorts, embeds, live links, ID de 11 chars.
   Opções: `--language tr,en` (fallback chain), `--json` (com metadados).

2. **Validar:** transcrição não-vazia, idioma esperado. Se vazia, retentar sem `--language`. Se ainda vazia, vídeo provavelmente tem transcrições desabilitadas.

3. **Chunking** (se >50K caracteres): dividir em chunks de ~40K com 2K overlap, sumarizar cada chunk, depois merge.

4. **Transformar** conforme solicitado:
   - **Resumo**: 5-10 frases concisas.
   - **Capítulos**: agrupar por mudanças de tópico com timestamps.
   - **Thread X/Twitter**: posts numerados, cada um ≤280 chars.
   - **Blog post**: artigo completo com título, seções, key takeaways.
   - **Quotes**: citações notáveis com timestamps.

5. **Verificar:** coerência, timestamps corretos, completude antes de apresentar.

### Exemplo de capítulos

```
00:00 Introdução — apresentação do problema
03:45 Background — trabalhos anteriores e limitações
12:20 Método proposto — walkthrough da abordagem
24:10 Resultados — benchmarks e conclusões
31:55 Q&A — perguntas da audiência
```

### Pitfalls

- **Transcrições desabilitadas**: avisar usuário, sugerir verificar legendas na página do vídeo.
- **Vídeo privado/indisponível**: relay o erro, pedir para verificar URL.
- **Idioma não encontrado**: retentar sem `--language`, informar idioma real obtido.
- **Dependência ausente**: rodar `uv pip install youtube-transcript-api` e retentar.
- **Transcrição vazia com timestamps mas sem `--text-only`**: alguns formatos não suportam timestamps; tentar sem `--timestamps`.
