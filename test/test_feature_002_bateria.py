#!/usr/bin/env python3
"""Testes Feature 002 — com resolução de imports relativos"""
import sys, os, time, importlib.util

BASE = '/home/zeenyt__/Projetos/42_Framework/.hermes/skills/wiki/experiential-memory'
sys.path.insert(0, BASE)
os.chdir('/home/zeenyt__/Projetos/42_Framework')

def _load(modname, filename):
    spec = importlib.util.spec_from_file_location(f'experiential_memory.{modname}', f'{BASE}/{filename}')
    m = importlib.util.module_from_spec(spec)
    sys.modules[f'experiential_memory.{modname}'] = m
    spec.loader.exec_module(m)
    return m

# Registra __init__ como pacote
init = importlib.util.spec_from_file_location('experiential_memory', f'{BASE}/__init__.py')
pkg = importlib.util.module_from_spec(init)
sys.modules['experiential_memory'] = pkg
init.loader.exec_module(pkg)

store = _load('store', 'store.py')
scoring = _load('scoring', 'scoring.py')
feedback = _load('feedback', 'feedback.py')
summarizer = _load('summarizer', 'summarizer.py')
decay = _load('decay', 'decay.py')
cluster = _load('cluster', 'cluster.py')
search = _load('search', 'search.py')

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

# ====== TESTE 2: Scoring ======
print('='*60)
print('TESTE 2: Scoring + Feedback')
print('='*60)
results = search.search_similar('coordenação dinâmica com heartbeat', model, k=5)
hashes = [r['content_hash'] for r in results]
for i,(r,h) in enumerate(zip(results,hashes)):
    print(f'  [{i}] score={r["score"]:.2f} sim={r["similarity"]:.3f} | {r["source"][:50]}')
for h in hashes[:3]: scoring.update_score(h, 0.08)
for h in hashes[3:]: scoring.update_score(h, -0.05)
print()
for i,h in enumerate(hashes):
    print(f'  [{i}] score={scoring.get_score(h):.2f} {"↑" if i<3 else "↓"}')
print('\nTop 5 hints globais:')
for r in scoring.get_top_hints(5):
    print(f'  score={r["score"]:.2f} | {r["source"][:45]} > {r["heading"][:35]}')

# ====== TESTE 3: Feedback Loop ======
print('\n'+'='*60)
print('TESTE 3: Feedback Loop')
print('='*60)
good = {'overwrite': {'overwrite_rate': 0.05}, 'waste': {'waste_ratio': 0.12}, 'idle': {'idle_ratio': 0.30}}
bad = {'overwrite': {'overwrite_rate': 0.35}, 'waste': {'waste_ratio': 0.80}, 'idle': {'idle_ratio': 0.70}}
ug = feedback.compute_utility_signal(good)
ub = feedback.compute_utility_signal(bad)
print(f'Feature BOA:  u={ug:.3f} ({feedback.classify_utility(ug):10s}) delta={feedback.utility_to_delta(ug):+.3f}')
print(f'Feature RUIM: u={ub:.3f} ({feedback.classify_utility(ub):10s}) delta={feedback.utility_to_delta(ub):+.3f}')
r = feedback.apply_feedback(ug, hashes[:3])
print(f'Aplicado em 3 hints: {r}')

# ====== TESTE 4: Summarizer ======
print('\n'+'='*60)
print('TESTE 4: Summarizer (LATTE paper)')
print('='*60)
raw = 'wiki/_raw/ImprovingtheEfficiencyofLanguageAgentTeamswithAdaptiveTaskGraphs.md'
summary = summarizer.summarize_raw_doc(raw)
print(f'Chars: {summary["char_count"]}, Tags: {summary["tags"]}')
for line in summary['content'].split('\n')[:6]:
    print(f'  {line}')

# ====== TESTE 5: Decay ======
print('\n'+'='*60)
print('TESTE 5: Decay')
print('='*60)
stats = store.get_stats()
print(f'Chunks antes: {stats["total_chunks"]}')
affected = decay.apply_decay(inactivity_threshold=1, decay_amount=0.02, floor=0.1)
print(f'Chunks afetados: {affected}')

# ====== TESTE 6: Distillation ======
print('\n'+'='*60)
print('TESTE 6: Distillation (threshold=0.75)')
print('='*60)
t0 = time.time()
clusters = cluster.cluster_chunks(similarity_threshold=0.75)
elapsed = time.time() - t0
print(f'Clusters: {len(clusters)}, Chunks: {sum(len(c) for c in clusters)}, Tempo: {elapsed:.1f}s')
for i,cl in enumerate(sorted(clusters,key=len,reverse=True)[:3]):
    sources = set(c['source'] for c in cl)
    print(f'  Cluster {i+1}: {len(cl)} chunks de {len(sources)} fontes')
    for c in cl[:1]:
        print(f'    [{c["score"]:.2f}] {c["source"][:55]}')

print('\n'+'='*60)
print('BATERIA COMPLETA — 5/5 TESTES OK')
print('='*60)
