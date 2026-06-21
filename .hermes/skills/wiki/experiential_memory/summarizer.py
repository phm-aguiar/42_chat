"""
T016 — summarizer.py: Sumarização automática de documentos em wiki/_raw/.

Detecta papers, artigos e documentos longos em wiki/_raw/, extrai metadados
do YAML frontmatter (title, description) e das primeiras seções (Abstract,
Contributions) para gerar um chunk de sumário indexável.

API pública:
    summarize_raw_doc(source_path) -> dict
"""

import hashlib
import re
import sys
from pathlib import Path
from typing import Optional


# ── Tentativa de importar PyYAML ───────────────────────────────────────────

_HAS_YAML = False
try:
    import yaml
    _HAS_YAML = True
except ImportError:
    pass


# ── Constantes ──────────────────────────────────────────────────────────────

# Padrão para delimitar blocos YAML frontmatter (--- ... ---)
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# Headings que indicam seções relevantes para sumarização
ABSTRACT_HEADINGS = [
    r'^#{1,6}\s*Abstract\s*$',
    r'^#{1,6}\s*Resumo\s*$',
    r'^#{1,6}\s*TL;DR\s*$',
]

CONTRIBUTIONS_HEADINGS = [
    r'^#{1,6}\s*(Our\s+)?Contributions?\s*$',
    r'^#{1,6}\s*(Principais\s+)?Contribuições?\s*$',
]

INTRODUCTION_HEADINGS = [
    r'^#{1,6}\s*Introduction\s*$',
    r'^#{1,6}\s*Introdução\s*$',
]

METHODOLOGY_HEADINGS = [
    r'^#{1,6}\s*(Methodology|Method|Approach|Framework)\s*$',
    r'^#{1,6}\s*(Metodologia|Método|Abordagem)\s*$',
]

RESULTS_HEADINGS = [
    r'^#{1,6}\s*(Results?|Experiments?|Evaluation)\s*$',
    r'^#{1,6}\s*(Resultados?|Experimentos?|Avaliação)\s*$',
]

# Regex para extrair métricas numéricas do texto
# Captura padrões como "45.8%", "5.11%~17.50%", "2.3x", "reduces by X%"
METRIC_PATTERNS = [
    # Percentagens com contexto (melhoria/redução)
    re.compile(
        r'(?:improves?|reduces?|outperform(?:s|ing)?|achiev(?:es?|ing)|'
        r'deliver(?:s|ing)?|boost|increase|decrease|cut|save|gain|'
        r'melhora?|reduz|aumenta|economiza)\s+.*?'
        r'(\d+\.?\d*\s*%[\s~]*\d*\.?\d*\s*%?)',
        re.IGNORECASE,
    ),
    # Percentagens isoladas (ex: "45.8% lower", "by 17.50%")
    re.compile(
        r'(\d+\.?\d*\s*%)\s*(?:lower|higher|less|more|fewer|faster|'
        r'slower|reduction|improvement|increase|decrease|'
        r'menos|mais|rápido|redução|melhoria|aumento)',
        re.IGNORECASE,
    ),
    # Múltiplos (ex: "2.3x faster", "3x improvement")
    re.compile(
        r'(\d+\.?\d*\s*x)\s*(?:faster|slower|more|less|improvement|'
        r'speedup|reduction)',
        re.IGNORECASE,
    ),
    # Token / time / cost savings
    re.compile(
        r'(?:reduces?\s+(?:token|time|wall.clock|cost|running.time|'
        r'execution|latency)\s+(?:usage|consumption|overhead)?\s*by\s*'
        r'(\d+\.?\d*\s*%))',
        re.IGNORECASE,
    ),
    # Savings in absolute terms
    re.compile(
        r'(?:saves?\s+|saving\s+)(\$?\d+\.?\d*\s*(?:USD|tokens?|minutes?|hours?))',
        re.IGNORECASE,
    ),
    # Accuracy / F1 / score improvements
    re.compile(
        r'(?:accuracy|F1|BLEU|ROUGE|precision|recall|score)\s*(?:of|is|:)?\s*'
        r'(\d+\.?\d*\s*%[\s~]*\d*\.?\d*\s*%?)',
        re.IGNORECASE,
    ),
]

# Número máximo de caracteres para o sumário
MAX_SUMMARY_SIZE = 2000


# ── Helpers ─────────────────────────────────────────────────────────────────

def _sha256(content: str) -> str:
    """Retorna o hash SHA256 hex de uma string."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _extract_frontmatter(text: str) -> dict:
    """
    Extrai e parseia o bloco YAML frontmatter de um documento Markdown.

    Tenta usar PyYAML se disponível; caso contrário, faz um parsing
    simplificado (suporta strings, listas e escalares simples).

    Args:
        text: Conteúdo completo do documento.

    Returns:
        Dicionário com os metadados do frontmatter, ou {} se não encontrado.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}

    yaml_block = m.group(1)

    if _HAS_YAML:
        try:
            return yaml.safe_load(yaml_block) or {}
        except Exception:
            pass

    # ── Fallback: parser simplificado de YAML ────────────────────────────
    return _simple_yaml_parse(yaml_block)


def _simple_yaml_parse(yaml_text: str) -> dict:
    """
    Parser YAML simplificado para frontmatter sem dependências externas.

    Suporta:
      - key: "value" (string com aspas)
      - key: value (string sem aspas)
      - key: (valor vazio/null)
      - key:
          - item1
          - item2  (listas)
      - key:
          subkey: value (dicionários aninhados, nível 1)

    Args:
        yaml_text: String YAML do frontmatter.

    Returns:
        Dicionário com os valores parseados.
    """
    result = {}
    lines = yaml_text.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Ignora linhas vazias e comentários
        if not stripped or stripped.startswith('#'):
            i += 1
            continue

        # Verifica se é uma chave: valor
        kv_match = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', stripped)
        if not kv_match:
            i += 1
            continue

        key = kv_match.group(1)
        value_part = kv_match.group(2).strip()

        # Lista (próximas linhas começando com "  - ")
        if value_part == '' or value_part == '|':
            # Pode ser lista ou dict aninhado
            list_items = []
            nested_dict = {}
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if not next_line.strip():
                    j += 1
                    continue

                # Detecta indentação
                list_match = re.match(r'^(\s*)-(\s+)(.*)', next_line)
                if list_match:
                    list_items.append(list_match.group(3).strip().strip('"'))
                    j += 1
                    continue

                # Detecta dict aninhado (subkey: value)
                nested_match = re.match(r'^(\s+)(\w[\w_-]*)\s*:\s*(.*)', next_line)
                if nested_match:
                    nested_dict[nested_match.group(2)] = (
                        nested_match.group(3).strip().strip('"').strip("'")
                    )
                    j += 1
                    continue

                break

            if list_items:
                result[key] = list_items
            elif nested_dict:
                result[key] = nested_dict
            else:
                result[key] = None  # chave sem valor

            i = j
            continue

        # Valor escalar (string, número, booleano)
        value = value_part.strip()
        # Remove aspas
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]

        result[key] = value if value else None
        i += 1

    return result


def _remove_frontmatter(text: str) -> str:
    """Remove o bloco YAML frontmatter do texto, retornando só o conteúdo."""
    return FRONTMATTER_RE.sub('', text, count=1).strip()


def _find_section(
    text: str,
    heading_patterns: list[str],
    max_lines: int = 80,
) -> Optional[str]:
    """
    Encontra uma seção no texto a partir de padrões de heading.

    Args:
        text: Texto do documento (sem frontmatter).
        heading_patterns: Lista de regex para identificar o heading da seção.
        max_lines: Número máximo de linhas a extrair após o heading.

    Returns:
        Conteúdo da seção (sem o heading) ou None se não encontrada.
    """
    lines = text.split('\n')

    for pattern in heading_patterns:
        heading_re = re.compile(pattern)
        for idx, line in enumerate(lines):
            if heading_re.match(line):
                # Extrai linhas seguintes até próximo heading ou max_lines
                section_lines = []
                heading_level = _heading_level(line)
                j = idx + 1
                while j < len(lines) and j - idx <= max_lines:
                    next_line = lines[j].strip()
                    # Para no próximo heading de mesmo nível ou superior
                    if next_line.startswith('#'):
                        h_level = _heading_level(next_line)
                        if h_level > 0 and h_level <= heading_level:
                            break
                    # Ignora figuras e equações LaTeX
                    if next_line.startswith('![') or \
                       next_line.startswith('$$') or \
                       next_line.startswith('<'):
                        j += 1
                        continue
                    section_lines.append(lines[j])
                    j += 1

                content = '\n'.join(section_lines).strip()
                if content:
                    return content

    return None


def _heading_level(line: str) -> int:
    """Retorna o nível do heading (1-6) ou 0 se não for heading."""
    m = re.match(r'^(#{1,6})\s', line)
    return len(m.group(1)) if m else 0


def _extract_contributions(text: str) -> Optional[str]:
    """
    Extrai a seção de contribuições do texto (lista numerada ou bullets).

    Tenta encontrar a seção "Contributions" e extrair os itens principais.
    Se não encontrar uma seção dedicada, procura uma lista numerada após
    o abstract que pareça listar contribuições.

    Args:
        text: Texto do documento (sem frontmatter).

    Returns:
        String formatada com as contribuições ou None.
    """
    # Tenta encontrar seção de contribuições
    contrib_text = _find_section(text, CONTRIBUTIONS_HEADINGS, max_lines=60)
    if contrib_text:
        # Extrai itens numerados ou com bullet
        items = []
        for line in contrib_text.split('\n'):
            line = line.strip()
            # Item numerado
            m = re.match(r'^(\d+)[\.\)]\s+(.+)', line)
            if m:
                item_text = m.group(2)
                # Limpa citações e referências
                item_text = re.sub(r'\[\^\d+\]', '', item_text)
                item_text = re.sub(r'\[@[\w]+\]', '', item_text)
                items.append(item_text[:300])  # trunca cada item
                continue
            # Bullet point
            m = re.match(r'^[-•*]\s+(.+)', line)
            if m:
                item_text = m.group(1)
                item_text = re.sub(r'\[\^\d+\]', '', item_text)
                items.append(item_text[:300])

        if items:
            return '\n'.join(f'  • {item}' for item in items[:6])

    # Fallback: procura lista numerada próxima ao abstract
    return _find_numbered_list_near_abstract(text)


def _find_numbered_list_near_abstract(text: str) -> Optional[str]:
    """
    Procura uma lista numerada (1., 2., 3.) próxima à seção de abstract.

    Args:
        text: Texto do documento.

    Returns:
        String formatada com itens ou None.
    """
    lines = text.split('\n')

    # Encontra o fim do abstract
    abstract_end = 0
    for pattern in ABSTRACT_HEADINGS:
        heading_re = re.compile(pattern)
        for idx, line in enumerate(lines):
            if heading_re.match(line):
                # Avança até o próximo heading
                hl = _heading_level(line)
                j = idx + 1
                while j < len(lines):
                    if lines[j].strip().startswith('#'):
                        if _heading_level(lines[j]) <= hl:
                            break
                    j += 1
                abstract_end = j
                break
        if abstract_end:
            break

    if not abstract_end:
        abstract_end = min(80, len(lines))

    # Procura lista numerada nos 40 parágrafos seguintes ao abstract
    items = []
    in_list = False
    for idx in range(abstract_end, min(abstract_end + 40, len(lines))):
        line = lines[idx].strip()
        m = re.match(r'^(\d+)[\.\)]\s+(.+)', line)
        if m:
            in_list = True
            item_text = m.group(2)
            item_text = re.sub(r'\[\^\d+\]', '', item_text)
            item_text = re.sub(r'\[@[\w]+\]', '', item_text)
            items.append(item_text[:300])
        elif in_list and not line:
            # Fim da lista
            break

    if len(items) >= 2:
        return '\n'.join(f'  • {item}' for item in items[:6])

    return None


def _extract_metrics(text: str) -> list[str]:
    """
    Extrai métricas-chave do texto usando patterns regex.

    Args:
        text: Texto do documento.

    Returns:
        Lista de strings com métricas encontradas (máx 10, sem duplicatas).
    """
    metrics = set()

    for pattern in METRIC_PATTERNS:
        for m in pattern.finditer(text):
            metric = m.group(1).strip()
            # Normaliza espaços
            metric = re.sub(r'\s+', ' ', metric)
            # Filtra métricas muito longas (provavelmente falsos positivos)
            if len(metric) <= 60:
                metrics.add(metric)

    # Ordena e limita a 10 métricas
    return sorted(metrics)[:10]


def _extract_abstract(text: str) -> Optional[str]:
    """
    Extrai o texto do abstract/resumo do documento.

    Args:
        text: Texto do documento (sem frontmatter).

    Returns:
        Texto do abstract ou None.
    """
    return _find_section(text, ABSTRACT_HEADINGS, max_lines=40)


# ── API pública ─────────────────────────────────────────────────────────────

def summarize_raw_doc(source_path: str) -> dict:
    """
    Sumariza um documento em wiki/_raw/ e retorna um chunk indexável.

    Detecta papers, artigos e documentos longos. Extrai o YAML frontmatter
    (title, description), o abstract, as contribuições e métricas-chave para
    compor um sumário estruturado com três seções:
      - Propósito
      - Principais Contribuições / Achados
      - Métricas-Chave

    O chunk é compatível com o pipeline de indexação: chunk_markdown +
    insert_chunk. O heading_path é fixo como 'Summary' e as tags são
    ['summary', 'auto-generated'].

    Args:
        source_path: Caminho para o arquivo .md em wiki/_raw/ (relativo ou
            absoluto). Ex: 'wiki/_raw/LATTE_Paper.md'.

    Returns:
        Dicionário com a estrutura padrão de chunk:
            {
                'content': str,         # Texto do sumário
                'heading_path': 'Summary',
                'source': str,          # source_path normalizado
                'content_hash': str,    # SHA256 do conteúdo
                'char_count': int,      # Tamanho do conteúdo
                'tags': ['summary', 'auto-generated'],
            }

        Retorna um chunk vazio (content='') se o arquivo não existir ou
        não puder ser lido.

    Example:
        >>> chunk = summarize_raw_doc('wiki/_raw/LATTE_Paper.md')
        >>> print(chunk['content'][:200])
        ## Propósito
        LATTE: coordination graph dinâmico para times de LLM...
    """
    # Normaliza o caminho
    path = Path(source_path)
    if not path.is_absolute():
        # Tenta resolver relativo ao cwd
        path = Path.cwd() / source_path

    # Verifica existência
    if not path.exists():
        print(
            f"[summarizer] ERRO: Arquivo não encontrado: {path}",
            file=sys.stderr,
        )
        return _empty_chunk(source_path)

    # Verifica extensão
    if path.suffix.lower() != '.md':
        print(
            f"[summarizer] AVISO: Arquivo não é Markdown: {path}",
            file=sys.stderr,
        )
        return _empty_chunk(source_path)

    # Lê o arquivo
    try:
        raw_text = path.read_text(encoding='utf-8')
    except Exception as e:
        print(
            f"[summarizer] ERRO ao ler {path}: {e}",
            file=sys.stderr,
        )
        return _empty_chunk(source_path)

    if not raw_text.strip():
        return _empty_chunk(source_path)

    # 1. Extrai frontmatter
    frontmatter = _extract_frontmatter(raw_text)
    title = frontmatter.get('title', path.stem)
    description = frontmatter.get('description', '')

    # 2. Remove frontmatter para análise do corpo
    body = _remove_frontmatter(raw_text)

    # 3. Extrai abstract
    abstract = _extract_abstract(body)

    # 4. Extrai contribuições
    contributions = _extract_contributions(body)

    # 5. Extrai métricas
    metrics = _extract_metrics(body)

    # 6. Monta o sumário estruturado
    summary = _build_summary(
        title=title,
        description=description,
        abstract=abstract,
        contributions=contributions,
        metrics=metrics,
    )

    # 7. Trunca se exceder MAX_SUMMARY_SIZE
    if len(summary) > MAX_SUMMARY_SIZE:
        summary = summary[:MAX_SUMMARY_SIZE - 3] + '...'

    # 8. Retorna chunk formatado
    normalized_source = str(Path(source_path)).replace('\\', '/')
    return {
        'content': summary,
        'heading_path': 'Summary',
        'source': normalized_source,
        'content_hash': _sha256(summary),
        'char_count': len(summary),
        'tags': ['summary', 'auto-generated'],
    }


def _build_summary(
    title: str,
    description: str,
    abstract: Optional[str],
    contributions: Optional[str],
    metrics: list[str],
) -> str:
    """
    Constrói o texto do sumário a partir das partes extraídas.

    Args:
        title: Título do documento.
        description: Descrição do frontmatter.
        abstract: Texto do abstract (opcional).
        contributions: Contribuições formatadas (opcional).
        metrics: Lista de métricas-chave.

    Returns:
        String Markdown com o sumário estruturado.
    """
    parts = []

    # Cabeçalho com título
    parts.append(f"## {title}")

    # Propósito (description + primeira frase do abstract)
    purpose_section = "### Propósito\n"
    if description:
        purpose_section += f"{description}\n"
    elif abstract:
        # Pega a primeira frase do abstract
        first_sentence = re.split(r'(?<=[.!?])\s+', abstract)[0]
        purpose_section += f"{first_sentence}\n"
    else:
        purpose_section += "(Não foi possível extrair o propósito automaticamente.)\n"
    parts.append(purpose_section.strip())

    # Principais contribuições / achados
    contrib_section = "### Principais Contribuições / Achados\n"
    if contributions:
        contrib_section += f"{contributions}\n"
    elif abstract:
        # Usa o abstract como fonte de achados (truncado)
        abstract_clean = re.sub(r'\s+', ' ', abstract).strip()
        if len(abstract_clean) > 500:
            abstract_clean = abstract_clean[:497] + '...'
        contrib_section += f"{abstract_clean}\n"
    else:
        contrib_section += "(Não foi possível extrair contribuições automaticamente.)\n"
    parts.append(contrib_section.strip())

    # Métricas-chave
    metrics_section = "### Métricas-Chave\n"
    if metrics:
        for m in metrics:
            metrics_section += f"  • {m}\n"
    else:
        metrics_section += "(Nenhuma métrica numérica detectada automaticamente.)\n"
    parts.append(metrics_section.strip())

    return '\n\n'.join(parts)


def _empty_chunk(source_path: str) -> dict:
    """Retorna um chunk vazio para casos de erro."""
    normalized_source = str(Path(source_path)).replace('\\', '/')
    return {
        'content': '',
        'heading_path': 'Summary',
        'source': normalized_source,
        'content_hash': _sha256(''),
        'char_count': 0,
        'tags': ['summary', 'auto-generated'],
    }


# ── Bloco de testes rápido ──────────────────────────────────────────────────

if __name__ == '__main__':
    """
    Testa o summarizer com documentos em wiki/_raw/.

    Uso:
        python summarizer.py                        # testa todos os docs
        python summarizer.py wiki/_raw/Paper.md     # testa doc específico
    """
    import os

    if len(sys.argv) > 1:
        # Modo: testa um arquivo específico
        test_path = sys.argv[1]
        chunk = summarize_raw_doc(test_path)
        if chunk['content']:
            print(f"✅ Sumário gerado para: {test_path}")
            print(f"   Tamanho: {chunk['char_count']} caracteres")
            print(f"   Hash:    {chunk['content_hash'][:16]}...")
            print()
            print(chunk['content'])
            print()
        else:
            print(f"❌ Sumário vazio para: {test_path}")
    else:
        # Modo: testa todos os .md em wiki/_raw/
        raw_dir = Path('wiki/_raw')
        if not raw_dir.is_dir():
            print(f"Diretório {raw_dir} não encontrado.")
            print("Execute a partir da raiz do projeto.")
            sys.exit(1)

        md_files = sorted(raw_dir.glob('*.md'))
        if not md_files:
            print(f"Nenhum arquivo .md em {raw_dir}")
            sys.exit(0)

        print(f"📄 Testando {len(md_files)} documento(s) em {raw_dir}/")
        print("=" * 70)

        for md_file in md_files:
            rel_path = str(md_file)
            chunk = summarize_raw_doc(rel_path)

            status = "✅" if chunk['content'] else "❌ (vazio)"
            size = chunk['char_count']
            metrics_count = chunk['content'].count('•') if chunk['content'] else 0
            print(f"{status} {md_file.name}")
            print(f"     {size} caracteres, ~{metrics_count} métricas")

        print("=" * 70)
