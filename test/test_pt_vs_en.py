#!/usr/bin/env python3
"""Comparacao pt-BR vs EN na qualidade dos embeddings"""
import sys, os, time, importlib.util

BASE = '/home/zeenyt__/Projetos/42_Framework/.hermes/skills/wiki/experiential-memory'
sys.path.insert(0, BASE)
os.chdir('/home/zeenyt__/Projetos/42_Framework')

def _load(modname, filename):
    spec = importlib.util.spec_from_file_location('em.' + modname, BASE + '/' + filename)
    m = importlib.util.module_from_spec(spec)
    sys.modules['em.' + modname] = m
    spec.loader.exec_module(m)
    return m

init = importlib.util.spec_from_file_location('em', BASE + '/__init__.py')
pkg = importlib.util.module_from_spec(init)
sys.modules['em'] = pkg; init.loader.exec_module(pkg)
search = _load('search', 'search.py')

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

pairs = [
    ("coordenacao dinamica com heartbeat para agentes",
     "dynamic coordination with heartbeat for agents"),
    ("como decompor tasks em features SDD",
     "how to decompose tasks in SDD features"),
    ("bug em propagacao de dependencias no operador verify",
     "dependency propagation bug in verify operator"),
    ("memoria experiencial com retrieval semantico",
     "experiential memory with semantic retrieval"),
    ("indexacao de documentos com embeddings para busca",
     "document indexing with embeddings for search"),
]

print('=' * 70)
print('COMPARACAO PT-BR vs EN -- all-MiniLM-L6-v2')
print('=' * 70)

for pt, en in pairs:
    emb_pt = model.encode(pt)
    emb_en = model.encode(en)

    t0 = time.time()
    results_pt = search.search_similar(pt, model, k=1)
    t_pt = (time.time() - t0) * 1000

    t0 = time.time()
    results_en = search.search_similar(en, model, k=1)
    t_en = (time.time() - t0) * 1000

    sim_between = float(sum(a * b for a, b in zip(emb_pt, emb_en)))
    top_pt = results_pt[0]['similarity'] if results_pt else 0
    top_en = results_en[0]['similarity'] if results_en else 0
    gain = (top_en - top_pt) / max(top_pt, 0.001) * 100

    print()
    src_pt = results_pt[0]['source'][:50] if results_pt else "N/A"
    src_en = results_en[0]['source'][:50] if results_en else "N/A"
    print("PT:", pt[:55])
    print("EN:", en[:55])
    print("  Sim entre queries: %.3f" % sim_between)
    print("  Top hit PT: %.3f (%s)" % (top_pt, src_pt))
    print("  Top hit EN: %.3f (%s)" % (top_en, src_en))
    print("  Ganho EN: %+.0f%% | Tempo: PT=%dms EN=%dms" % (gain, int(t_pt), int(t_en)))

# Agregado
all_gains = []
all_sims = []
for pt, en in pairs:
    emb_pt = model.encode(pt)
    emb_en = model.encode(en)
    sim = float(sum(a * b for a, b in zip(emb_pt, emb_en)))
    all_sims.append(sim)
    r_pt = search.search_similar(pt, model, k=1)
    r_en = search.search_similar(en, model, k=1)
    if r_pt and r_en:
        g = (r_en[0]['similarity'] - r_pt[0]['similarity']) / max(r_pt[0]['similarity'], 0.001) * 100
        all_gains.append(g)

avg_sim = sum(all_sims) / len(all_sims)
avg_gain = sum(all_gains) / len(all_gains)
print()
print('=' * 70)
print('RESUMO')
print('=' * 70)
print("Similaridade media PT<->EN: %.3f" % avg_sim)
print("Ganho medio do EN: %+.0f%%" % avg_gain)
if avg_gain > 15:
    print("Conclusao: SIGNIFICATIVO -- migrar pra EN traria ganho real de +%.0f%%" % avg_gain)
elif avg_gain > 5:
    print("Conclusao: MODERADO -- ganho de +%.0f%%, considerar EN para docs criticos" % avg_gain)
else:
    print("Conclusao: MARGINAL -- nao justifica migrar, pt-BR funciona bem")
