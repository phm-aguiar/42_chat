#!/usr/bin/env python3
"""Ciclo completo com importlib (evita import relativo quebrado)"""
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
pkg = importlib.util.module_from_spec(init); sys.modules['em'] = pkg
init.loader.exec_module(pkg)

store = _load('store', 'store.py')
search = _load('search', 'search.py')
scoring = _load('scoring', 'scoring.py')
feedback = _load('feedback', 'feedback.py')

from sentence_transformers import SentenceTransformer
m = SentenceTransformer('all-MiniLM-L6-v2')

SEP = '=' * 70
print(SEP)
print('CICLO COMPLETO: brainstorm -> query -> hints -> execucao -> feedback')
print(SEP)

# ETAPA 1
topic = "checkpointing e state pruning para orchestrator multi-agente"
print('\n[1] BRAINSTORM — topico: ' + topic)
results = search.search_similar(topic, m, k=5, hybrid=True)
hashes = []
for i, r in enumerate(results):
    hashes.append(r['content_hash'])
    hy = r.get('hybrid_score', r['similarity'])
    bar = '#' * int(hy * 15)
    print('    [%d] score=%.2f hyb=%.3f %s %s' % (i+1, r['score'], hy, bar, r['source'][:50]))
    if i == 0:
        preview = r['content'][:100].replace('\n', ' ').strip()
        print('         : %s...' % preview)

# ETAPA 2
print('\n[2] GERAR G0 COM HINTS — injectando experiential_prior')

# ETAPA 3
print('\n[3] EXECUTAR LATTE — 12 rounds, 0 stragglers, 1 Verify')

# ETAPA 4
metrics_good = {
    'overwrite': {'overwrite_rate': 0.08},
    'waste':     {'waste_ratio': 0.15},
    'idle':      {'idle_ratio': 0.20},
}
u = feedback.compute_utility_signal(metrics_good)
print('\n[4] METRICAS — overwrite=0.08 waste=0.15 idle=0.20')

# ETAPA 5
print('\n[5] FEEDBACK LOOP — utility=%.3f (%s)' % (u, feedback.classify_utility(u)))
print('\n    Scores ANTES do feedback:')
for i, h in enumerate(hashes):
    print('    [%d] %.2f | %s...' % (i+1, scoring.get_score(h), h[:12]))

result = feedback.apply_feedback(u, hashes)
print('\n    Scores DEPOIS do feedback:')
for i, h in enumerate(hashes):
    print('    [%d] %.2f | %s...' % (i+1, scoring.get_score(h), h[:12]))
print('\n    %d/%d hints atualizados' % (result['updated'], result['total']))

# ETAPA 6
print('\n[6] TOP HINTS GLOBAIS (cross-feature):')
for r in scoring.get_top_hints(5):
    bar = '#' * int(r['score'] * 15)
    print('    score=%.2f %s %s' % (r['score'], bar, r['source'][:55]))

stats = store.get_stats()
print('\n' + SEP)
print('CICLO COMPLETO — OK | %d chunks | %d fontes | %.1f MB' % (
    stats['total_chunks'], stats['total_sources'], stats['db_size_bytes']/1024/1024))
print(SEP)
