#!/usr/bin/env python3
"""Benchmark A/B: Cosine-only vs Hybrid (BM25+cosine)"""
import sys, os, time, importlib.util

BASE = '.hermes/skills/wiki/experiential_memory'
sys.path.insert(0, BASE)
os.chdir('/home/zeenyt__/Projetos/42_Framework')

def _load(modname, filename):
    spec = importlib.util.spec_from_file_location('em.'+modname, BASE+'/'+filename)
    m = importlib.util.module_from_spec(spec)
    sys.modules['em.'+modname] = m
    spec.loader.exec_module(m)
    return m

init = importlib.util.spec_from_file_location('em', BASE+'/__init__.py')
pkg = importlib.util.module_from_spec(init)
sys.modules['em'] = pkg; init.loader.exec_module(pkg)
store = _load('store', 'store.py')
search = _load('search', 'search.py')

from sentence_transformers import SentenceTransformer
m = SentenceTransformer('all-MiniLM-L6-v2')

# Queries de teste: mix de lexicais, conceituais e mistas
queries = [
    # LEXICAIS (termos exatos, BM25 deve ganhar)
    ("LEX", "sqlite-vec FTS5 pgvector extensão vetorial"),
    ("LEX", "0xDEADBEEF stack trace segmentation fault"),
    ("LEX", "#3498db hex color css variável"),
    ("LEX", "rank_bm25 BM25Okapi tokenização TF-IDF"),
    ("LEX", "interrupt_before update_state checkpointing thread_id"),
    
    # CONCEITUAIS (semântico, cosine deve manter qualidade)
    ("CON", "coordenação dinâmica entre agentes com heartbeat"),
    ("CON", "memória experiencial com feedback loop"),
    ("CON", "indexação semântica de documentos markdown"),
    ("CON", "orquestração de times de IA com grafo de tarefas"),
    ("CON", "normalização de metadados YAML frontmatter"),
    
    # MISTAS (ambos devem contribuir)
    ("MIX", "LangGraph produção checkpointing stateful agents"),
    ("MIX", "A-MapReduce wide search experiential memory hints"),
    ("MIX", "LATTE coordination graph heartbeat verify operator"),
    ("MIX", "Obsidian otimização IA chunking híbrido BM25"),
    ("MIX", "feature 003 wiki retrieval normalização frontmatter"),
]

print('=' * 80)
print('BENCHMARK A/B: Cosine-only vs Hybrid (BM25+cosine, alpha=0.7)')
print('=' * 80)
print(f'{"Query":<55} {"Tipo":>4} {"Cos":>6} {"Hyb":>6} {"Gain":>6} {"Δt":>5}')
print('-' * 80)

results = []
for qtype, query in queries:
    # Cosine-only
    t0 = time.time()
    r_cos = search.search_similar(query, m, k=1)
    t_cos = (time.time() - t0) * 1000
    
    # Hybrid
    t0 = time.time()
    r_hyb = search.search_similar(query, m, k=1, hybrid=True, alpha=0.7)
    t_hyb = (time.time() - t0) * 1000
    
    cos_score = r_cos[0]['similarity'] if r_cos else 0
    hyb_score = r_hyb[0]['hybrid_score'] if r_hyb else 0
    
    if cos_score > 0:
        gain = (hyb_score - cos_score) / cos_score * 100
    else:
        gain = 0
    
    dt = t_hyb - t_cos
    short = query[:52]
    results.append((qtype, gain, dt, cos_score, hyb_score))
    
    print(f'{short:<55} {qtype:>4} {cos_score:>6.3f} {hyb_score:>6.3f} {gain:>+5.0f}% {dt:>+4.0f}ms')

# Agregados
print('\n' + '=' * 80)
print('AGREGADOS')
print('=' * 80)

for qtype in ['LEX', 'CON', 'MIX']:
    subset = [r for r in results if r[0] == qtype]
    avg_gain = sum(r[1] for r in subset) / len(subset)
    avg_dt = sum(r[2] for r in subset) / len(subset)
    avg_cos = sum(r[3] for r in subset) / len(subset)
    avg_hyb = sum(r[4] for r in subset) / len(subset)
    print(f'{qtype}: gain={avg_gain:+.0f}% | cos={avg_cos:.3f} → hyb={avg_hyb:.3f} | Δt={avg_dt:+.0f}ms')

total_gain = sum(r[1] for r in results) / len(results)
total_dt = sum(r[2] for r in results) / len(results)
print(f'\nTOTAL: gain={total_gain:+.0f}% | Δt={total_dt:+.0f}ms')
print(f'Conclusão: {"✅ GANHO SIGNIFICATIVO" if total_gain > 15 else "⚡ GANHO MODERADO" if total_gain > 5 else "➡️ MARGINAL"}')
