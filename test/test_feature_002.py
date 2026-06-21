#!/usr/bin/env python3
"""Bateria de testes da Feature 002 — Wiki Experiential Memory"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.hermes/skills/wiki/experiential-memory'))
os.chdir(os.path.dirname(__file__))

from sentence_transformers import SentenceTransformer
from search import search_similar
from scoring import update_score, get_score, get_top_hints, get_low_score_hints
from store import get_by_hash, get_stats
from feedback import compute_utility_signal, classify_utility, utility_to_delta, apply_feedback
from summarizer import summarize_raw_doc
from decay import apply_decay
from cluster import cluster_chunks

model = SentenceTransformer('all-MiniLM-L6-v2')

# TESTE 1: Retrieval Quality
print("=" * 60)
print("TESTE 1: Retrieval Quality (5 queries)")
print("=" * 60)
queries = [
    "como implementar coordenação dinâmica com heartbeat para agentes",
    "padrão de decomposição de tasks em features SDD",
    "bug em propagation de dependências no verify operator",
    "indexação semântica de documentos com embeddings",
    "feedback loop para melhorar hints com métricas de execução"
]
for q in queries:
    t0 = time.time()
    results = search_similar(q, model, k=3)
    elapsed = (time.time() - t0) * 1000
    print(f"\nQuery: '{q[:70]}' ({elapsed:.0f}ms)")
    for i, r in enumerate(results):
        sim = r['similarity']
        bar = '█' * int(sim * 20)
        src_short = r['source'][:45] if len(r['source']) > 45 else r['source']
        print(f"  [{i+1}] {sim:.3f} {bar} {src_short}")
        print(f"       > {r['heading'][:55]}")
        if i == 0:
            content_preview = r['content'][:130].replace('\n', ' ').strip()
            print(f"       : {content_preview}...")

# TESTE 2: Scoring
print("\n" + "=" * 60)
print("TESTE 2: Scoring + Top Hints")
print("=" * 60)
results = search_similar("coordenação dinâmica", model, k=5)
hashes = [r['content_hash'] for r in results]
print(f"\n5 chunks da query 'coordenação dinâmica':")
for i, (r, h) in enumerate(zip(results, hashes)):
    print(f"  [{i}] score={r['score']:.2f} sim={r['similarity']:.3f} | {r['source'][:50]}")

print("\nAplicando feedback BOM (+0.08) nos 3 primeiros, RUIM (-0.05) nos 2 últimos...")
for h in hashes[:3]:
    update_score(h, 0.08)
for h in hashes[3:]:
    update_score(h, -0.05)

print("\nScores após feedback:")
for i, h in enumerate(hashes):
    score = get_score(h)
    print(f"  [{i}] score={score:.2f} {'↑' if i < 3 else '↓'} | hash={h[:12]}...")

print("\nTop 5 hints globais:")
for r in get_top_hints(5):
    print(f"  score={r['score']:.2f} | {r['source'][:50]} > {r['heading'][:40]}")

# TESTE 3: Feedback Loop
print("\n" + "=" * 60)
print("TESTE 3: Feedback Loop (utility signal)")
print("=" * 60)
good = {'overwrite_rate': 0.05, 'wasted_chars': 1200, 'idle_rounds': 0.3}
bad = {'overwrite_rate': 0.35, 'wasted_chars': 8000, 'idle_rounds': 0.7}
u_good = compute_utility_signal(good)
u_bad = compute_utility_signal(bad)
print(f"\nFeature BEM-SUCEDIDA: u={u_good:.3f} ({classify_utility(u_good)}) delta={utility_to_delta(u_good):+.3f}")
print(f"Feature PROBLEMÁTICA: u={u_bad:.3f} ({classify_utility(u_bad)}) delta={utility_to_delta(u_bad):+.3f}")
result = apply_feedback(u_good, hashes[:3])
print(f"Aplicado feedback BOM em 3 hints: {result}")

# TESTE 4: Summarizer
print("\n" + "=" * 60)
print("TESTE 4: Summarizer (_raw/ paper)")
print("=" * 60)
raw_dir = 'wiki/_raw'
papers = [f for f in os.listdir(raw_dir) if f.endswith('.md')]
for paper_name in papers[:1]:
    paper_path = os.path.join(raw_dir, paper_name)
    summary = summarize_raw_doc(paper_path)
    print(f"\nPaper: {paper_name[:60]}")
    print(f"  Chars: {summary['char_count']}, Tags: {summary['tags']}")
    for line in summary['content'].split('\n')[:8]:
        print(f"  {line}")

# TESTE 5: Decay
print("\n" + "=" * 60)
print("TESTE 5: Score Decay")
print("=" * 60)
stats_before = get_stats()
print(f"\nAntes do decay: {stats_before['total_chunks']} chunks")
top_before = get_top_hints(3)
print("Top 3 scores antes:")
for r in top_before:
    print(f"  score={r['score']:.2f} | {r['source'][:50]}")
print("\nAplicando decay (inactivity=1, decay=0.02, floor=0.1)...")
affected = apply_decay(inactivity_threshold=1, decay_amount=0.02, floor=0.1)
print(f"Chunks afetados: {affected}")
top_after = get_top_hints(3)
print("Top 3 scores depois:")
for r in top_after:
    print(f"  score={r['score']:.2f} | {r['source'][:50]}")

# TESTE 6: Distillation
print("\n" + "=" * 60)
print("TESTE 6: Distillation (threshold=0.75)")
print("=" * 60)
clusters = cluster_chunks(similarity_threshold=0.75)
print(f"\nClusters formados: {len(clusters)}")
print(f"Chunks em clusters: {sum(len(c) for c in clusters)}")
if clusters:
    for i, cl in enumerate(sorted(clusters, key=len, reverse=True)[:3]):
        sources = set(c['source'] for c in cl)
        print(f"\n  Cluster {i+1}: {len(cl)} chunks de {len(sources)} fontes")
        for c in cl[:2]:
            print(f"    [{c['score']:.2f}] {c['source'][:50]} > {c['heading'][:50]}")

print("\n" + "=" * 60)
print("BATERIA COMPLETA")
print("=" * 60)
