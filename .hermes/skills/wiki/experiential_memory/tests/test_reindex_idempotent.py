#!/usr/bin/env python3
"""
T023: Smoke test de re-indexação idempotente.

Feature 002: Wiki Experiential Memory.

Verifica que ao re-indexar a wiki (index --full), chunks existentes
(com mesmo content_hash) preservam seus scores, e novos chunks recebem
score inicial 0.5 (neutro).

Estratégia do teste:
  1. Configurar um banco SQLite temporário com schema do store.py.
  2. Simular primeira indexação inserindo chunks A, B, C (score default 0.5).
  3. Usar scoring.py para modificar scores: A=0.8, B=0.3, C=0.5 (inalterado).
  4. Salvar snapshot dos scores antes da re-indexação.
  5. Simular re-indexação: inserir A, B, C novamente + novo chunk D.
  6. Verificar que A, B, C preservaram scores modificados e D tem score 0.5.
  7. Verificar que content_hash match é o mecanismo de preservação.

Módulos utilizados:
  - store.py (insert_chunk, create_tables, get_stats)
  - scoring.py (update_score, get_score, get_top_hints)
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import Any

# ── Setup do path para importar os módulos da feature ──────────────────────
# Os módulos usam imports relativos (ex: from .store import ...).
# Para viabilizar execução standalone, adicionamos o diretório pai ao path
# e usamos importlib para forçar o pacote.
_PARENT_DIR = Path(__file__).resolve().parent.parent
_PACKAGE_NAME = "experiential_memory"

# Registra o pacote no sys.modules para que imports relativos funcionem
if _PACKAGE_NAME not in sys.modules:
    import importlib

    # Importa store.py primeiro (sem imports relativos)
    _store_spec = importlib.util.spec_from_file_location(
        f"{_PACKAGE_NAME}.store",
        str(_PARENT_DIR / "store.py"),
    )
    _store_module = importlib.util.module_from_spec(_store_spec)
    sys.modules[f"{_PACKAGE_NAME}.store"] = _store_module
    _store_spec.loader.exec_module(_store_module)

    # Agora scoring.py pode importar de .store (resolvido via sys.modules)
    _scoring_spec = importlib.util.spec_from_file_location(
        f"{_PACKAGE_NAME}.scoring",
        str(_PARENT_DIR / "scoring.py"),
    )
    _scoring_module = importlib.util.module_from_spec(_scoring_spec)
    sys.modules[f"{_PACKAGE_NAME}.scoring"] = _scoring_module
    _scoring_spec.loader.exec_module(_scoring_module)
else:
    import store as _store_module  # noqa: E402
    import scoring as _scoring_module  # noqa: E402

# Monkey-patch DB_PATH ANTES dos imports para isolar o teste
_TEST_DB_PATH: str = ""


# ── Fixtures ────────────────────────────────────────────────────────────────

def _setup_test_db() -> str:
    """Cria um banco SQLite temporário e configura DB_PATH para apontar para ele.

    Monkey-patcha store.DB_PATH e scoring.DB_PATH (importado via store).
    Retorna o caminho do banco temporário.
    """
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_reindex_")
    os.close(fd)

    # Patch em todos os lugares que referenciam DB_PATH
    _store_module.DB_PATH = path
    _scoring_module.DB_PATH = path

    # Também define a env var para consistência com cli_index.py
    os.environ["HERMES_WIKI_DB"] = path

    # Cria o schema
    _store_module.create_tables()
    return path


def _teardown_test_db(db_path: str) -> None:
    """Remove o banco temporário e restaura DB_PATH."""
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass
    try:
        os.unlink(db_path + "-wal")
    except FileNotFoundError:
        pass
    try:
        os.unlink(db_path + "-shm")
    except FileNotFoundError:
        pass


def _make_chunk(
    content: str,
    source: str = "test/doc.md",
    heading_path: str = "Test Section",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Cria um dicionário de chunk compatível com chunker.py e store.insert_chunk."""
    import hashlib

    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return {
        "content": content,
        "source": source,
        "heading_path": heading_path,
        "content_hash": content_hash,
        "char_count": len(content),
        "tags": tags or [],
    }


# ── Helpers do teste ────────────────────────────────────────────────────────

def _get_all_chunks_with_scores() -> dict[str, float]:
    """Retorna um dicionário content_hash -> score de todos os chunks no banco."""
    conn = _store_module._get_conn()
    try:
        rows = conn.execute(
            "SELECT content_hash, score FROM chunks ORDER BY content_hash"
        ).fetchall()
        return {row["content_hash"]: row["score"] for row in rows}
    finally:
        conn.close()


def _count_chunks() -> int:
    """Retorna o número total de chunks no banco."""
    conn = _store_module._get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    finally:
        conn.close()


# ═════════════════════════════════════════════════════════════════════════════
# Teste principal
# ═════════════════════════════════════════════════════════════════════════════


def test_reindex_idempotent_scores_preserved() -> None:
    """
    Smoke test: re-indexação preserva scores por content_hash.

    Fluxo:
      1. Primeira indexação: 3 chunks (A, B, C) → scores = 0.5 (default).
      2. Modificar scores via scoring.py: A → 0.8, B → 0.3.
      3. Salvar snapshot dos scores.
      4. Re-indexar: mesmos chunks A, B, C + novo chunk D.
      5. Verificar: A, B, C preservam scores; D tem score 0.5.
    """
    print("=" * 72)
    print("T023: Smoke test — Re-indexação idempotente (preservação de scores)")
    print("=" * 72)

    # ── Setup ────────────────────────────────────────────────────────────
    db_path = _setup_test_db()
    print(f"\n[SETUP] Banco temporário: {db_path}")

    try:
        # ── STEP 1: Primeira indexação ───────────────────────────────────
        print("\n[STEP 1] Primeira indexação: inserindo chunks A, B, C")

        chunk_a = _make_chunk(
            "## Introdução\n\nEste é o chunk A sobre arquitetura de software.",
            source="docs/arquitetura.md",
            heading_path="Introdução",
        )
        chunk_b = _make_chunk(
            "## Padrões\n\nChunk B descreve padrões de design como Singleton e Factory.",
            source="docs/padroes.md",
            heading_path="Padrões",
        )
        chunk_c = _make_chunk(
            "## Testes\n\nChunk C cobre estratégias de teste unitário e integração.",
            source="docs/testes.md",
            heading_path="Testes",
        )

        # Insere sem embedding (embedding=None) — smoke test não testa embeddings
        id_a = _store_module.insert_chunk(chunk_a, embedding=None)
        id_b = _store_module.insert_chunk(chunk_b, embedding=None)
        id_c = _store_module.insert_chunk(chunk_c, embedding=None)

        print(f"    Chunk A inserido (id={id_a}): hash={chunk_a['content_hash'][:12]}...")
        print(f"    Chunk B inserido (id={id_b}): hash={chunk_b['content_hash'][:12]}...")
        print(f"    Chunk C inserido (id={id_c}): hash={chunk_c['content_hash'][:12]}...")

        # Verifica scores iniciais (devem ser 0.5)
        assert _count_chunks() == 3, f"Expected 3 chunks, got {_count_chunks()}"
        assert _scoring_module.get_score(chunk_a["content_hash"]) == 0.5
        assert _scoring_module.get_score(chunk_b["content_hash"]) == 0.5
        assert _scoring_module.get_score(chunk_c["content_hash"]) == 0.5
        print("    ✓ Todos os 3 chunks com score inicial 0.5")

        # ── STEP 2: Modificar scores via scoring.py ──────────────────────
        print("\n[STEP 2] Modificando scores via scoring.update_score()")

        # A: feedback positivo → score sobe para 0.8
        success_a = _scoring_module.update_score(chunk_a["content_hash"], +0.3)
        assert success_a, "update_score(A) should return True (hash exists)"

        # B: feedback negativo → score cai para 0.3
        success_b = _scoring_module.update_score(chunk_b["content_hash"], -0.2)
        assert success_b, "update_score(B) should return True (hash exists)"

        # C: sem alteração — permanece 0.5

        # Tenta atualizar hash inexistente → deve retornar False
        fake_hash = "deadbeef" * 8
        success_fake = _scoring_module.update_score(fake_hash, +1.0)
        assert not success_fake, "update_score with fake hash should return False"

        score_a = _scoring_module.get_score(chunk_a["content_hash"])
        score_b = _scoring_module.get_score(chunk_b["content_hash"])
        score_c = _scoring_module.get_score(chunk_c["content_hash"])

        assert score_a == 0.8, f"Score A should be 0.8, got {score_a}"
        assert score_b == 0.3, f"Score B should be 0.3, got {score_b}"
        assert score_c == 0.5, f"Score C should be 0.5 (unchanged), got {score_c}"

        print(f"    ✓ Score A: 0.5 → {score_a} (delta +0.3)")
        print(f"    ✓ Score B: 0.5 → {score_b} (delta -0.2)")
        print(f"    ✓ Score C: mantido em {score_c}")
        print(f"    ✓ update_score com hash fake retornou False (esperado)")

        # ── STEP 3: Salvar snapshot dos scores ───────────────────────────
        print("\n[STEP 3] Salvando snapshot dos scores antes da re-indexação")

        snapshot_before = _get_all_chunks_with_scores()
        assert len(snapshot_before) == 3, f"Snapshot should have 3 entries, got {len(snapshot_before)}"
        assert snapshot_before[chunk_a["content_hash"]] == 0.8
        assert snapshot_before[chunk_b["content_hash"]] == 0.3
        assert snapshot_before[chunk_c["content_hash"]] == 0.5

        print(f"    Snapshot before: {snapshot_before}")
        print(f"    ✓ Snapshot salvo com {len(snapshot_before)} chunks")

        # ── STEP 4: Re-indexação (insert_chunk novamente) ────────────────
        print("\n[STEP 4] Re-indexação: re-inserindo A, B, C + novo chunk D")

        # Simula re-indexação: re-insere os mesmos chunks (mesmo content_hash)
        # + um novo chunk D
        chunk_d = _make_chunk(
            "## Deploy\n\nChunk D é novo — adicionado entre indexações.",
            source="docs/deploy.md",
            heading_path="Deploy",
        )

        # Re-insere A, B, C (INSERT OR REPLACE deve preservar scores)
        id_a2 = _store_module.insert_chunk(chunk_a, embedding=None)
        id_b2 = _store_module.insert_chunk(chunk_b, embedding=None)
        id_c2 = _store_module.insert_chunk(chunk_c, embedding=None)
        id_d = _store_module.insert_chunk(chunk_d, embedding=None)

        print(f"    Chunk A re-inserido (id={id_a2})")
        print(f"    Chunk B re-inserido (id={id_b2})")
        print(f"    Chunk C re-inserido (id={id_c2})")
        print(f"    Chunk D novo (id={id_d}): hash={chunk_d['content_hash'][:12]}...")

        assert _count_chunks() == 4, f"Expected 4 chunks after re-index, got {_count_chunks()}"

        # ── STEP 5: Verificar preservação de scores ──────────────────────
        print("\n[STEP 5] Verificando scores pós-re-indexação")

        score_a_after = _scoring_module.get_score(chunk_a["content_hash"])
        score_b_after = _scoring_module.get_score(chunk_b["content_hash"])
        score_c_after = _scoring_module.get_score(chunk_c["content_hash"])
        score_d_after = _scoring_module.get_score(chunk_d["content_hash"])

        # Chunks existentes DEVEM preservar scores
        assert score_a_after == 0.8, (
            f"Chunk A: score should be preserved (0.8), got {score_a_after}"
        )
        assert score_b_after == 0.3, (
            f"Chunk B: score should be preserved (0.3), got {score_b_after}"
        )
        assert score_c_after == 0.5, (
            f"Chunk C: score should be preserved (0.5), got {score_c_after}"
        )

        # Novo chunk DEVE ter score 0.5 (default neutro)
        assert score_d_after == 0.5, (
            f"Chunk D (novo): score should be 0.5 (default), got {score_d_after}"
        )

        print(f"    ✓ Chunk A: score preservado → {score_a_after} (era 0.8)")
        print(f"    ✓ Chunk B: score preservado → {score_b_after} (era 0.3)")
        print(f"    ✓ Chunk C: score preservado → {score_c_after} (era 0.5)")
        print(f"    ✓ Chunk D (novo): score default → {score_d_after} (0.5)")

        # ── STEP 6: Verificações adicionais ──────────────────────────────
        print("\n[STEP 6] Verificações adicionais de integridade")

        # Snapshot pós-re-indexação
        snapshot_after = _get_all_chunks_with_scores()
        assert len(snapshot_after) == 4, (
            f"Snapshot after should have 4 entries, got {len(snapshot_after)}"
        )

        # Verifica que content_hashes originais mantiveram scores do snapshot before
        for chash, score_before in snapshot_before.items():
            assert chash in snapshot_after, (
                f"Hash {chash[:12]}... should still exist after re-index"
            )
            assert snapshot_after[chash] == score_before, (
                f"Hash {chash[:12]}... score changed from {score_before} "
                f"to {snapshot_after[chash]} — should be preserved"
            )

        # Chunk D (novo) deve estar presente com score 0.5
        assert chunk_d["content_hash"] in snapshot_after, (
            "New chunk D should be in the index after re-index"
        )
        assert snapshot_after[chunk_d["content_hash"]] == 0.5, (
            f"New chunk D should have score 0.5, got "
            f"{snapshot_after[chunk_d['content_hash']]}"
        )

        print(f"    Snapshot after: {snapshot_after}")
        print(f"    ✓ Todos os content_hashes preservados com scores corretos")

        # get_top_hints: deve retornar chunks ordenados por score DESC
        top_hints = _scoring_module.get_top_hints(k=4)
        assert len(top_hints) == 4, f"get_top_hints(4) should return 4, got {len(top_hints)}"
        # Ordem esperada: A (0.8) > C (0.5) / D (0.5) > B (0.3)
        assert top_hints[0]["content_hash"] == chunk_a["content_hash"], (
            "Top hint should be chunk A (score 0.8)"
        )
        assert top_hints[3]["content_hash"] == chunk_b["content_hash"], (
            "Bottom hint should be chunk B (score 0.3)"
        )
        print(f"    ✓ get_top_hints ordenado corretamente: top={top_hints[0]['score']}, "
              f"bottom={top_hints[3]['score']}")

        # get_low_score_hints: B (0.3) deve aparecer com threshold 0.4
        low_hints = _scoring_module.get_low_score_hints(threshold=0.4)
        assert len(low_hints) == 1, (
            f"get_low_score_hints(0.4) should return 1 (only B), got {len(low_hints)}"
        )
        assert low_hints[0]["content_hash"] == chunk_b["content_hash"]
        print(f"    ✓ get_low_score_hints(0.4) retorna apenas chunk B (score 0.3)")

        # Teste de limite: score não pode ultrapassar [0.0, 1.0]
        # Tenta forçar score > 1.0
        _scoring_module.update_score(chunk_a["content_hash"], +5.0)
        capped_score = _scoring_module.get_score(chunk_a["content_hash"])
        assert capped_score == 1.0, (
            f"Score should be capped at 1.0, got {capped_score}"
        )
        print(f"    ✓ Score capped em 1.0 (tentativa de +5.0 sobre 0.8)")

        # Tenta forçar score < 0.0
        _scoring_module.update_score(chunk_b["content_hash"], -5.0)
        floored_score = _scoring_module.get_score(chunk_b["content_hash"])
        assert floored_score == 0.0, (
            f"Score should be floored at 0.0, got {floored_score}"
        )
        print(f"    ✓ Score floored em 0.0 (tentativa de -5.0 sobre 0.3)")

        # Restaura scores para não poluir asserts seguintes
        _scoring_module.update_score(chunk_a["content_hash"], -0.2)  # volta para 0.8
        _scoring_module.update_score(chunk_b["content_hash"], +0.3)  # volta para 0.3

        # Verifica que get_stats funciona após re-indexação
        stats = _store_module.get_stats()
        assert stats["total_chunks"] == 4, f"Stats total_chunks should be 4, got {stats['total_chunks']}"
        assert stats["total_sources"] == 4, f"Stats total_sources should be 4, got {stats['total_sources']}"
        print(f"    ✓ get_stats: {stats['total_chunks']} chunks, "
              f"{stats['total_sources']} sources")

        # get_by_hash: verifica acesso por content_hash
        chunk_a_retrieved = _store_module.get_by_hash(chunk_a["content_hash"])
        assert chunk_a_retrieved is not None, "get_by_hash(A) should return data"
        assert chunk_a_retrieved["score"] == 0.8
        assert chunk_a_retrieved["content"] == chunk_a["content"]
        print(f"    ✓ get_by_hash recupera chunk A com score preservado")

        chunk_d_retrieved = _store_module.get_by_hash(chunk_d["content_hash"])
        assert chunk_d_retrieved is not None, "get_by_hash(D) should return data"
        assert chunk_d_retrieved["score"] == 0.5
        print(f"    ✓ get_by_hash recupera chunk D (novo) com score 0.5")

        # Hash inexistente → None
        assert _store_module.get_by_hash(fake_hash) is None, (
            "get_by_hash with fake hash should return None"
        )
        print(f"    ✓ get_by_hash com hash fake retorna None")

    finally:
        # ── Teardown ─────────────────────────────────────────────────────
        _teardown_test_db(db_path)
        print(f"\n[TEARDOWN] Banco temporário removido: {db_path}")

    # ═════════════════════════════════════════════════════════════════════
    # Resumo
    # ═════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 72)
    print("RESUMO — T023: Re-indexação idempotente")
    print("=" * 72)
    print("  Chunks na primeira indexação:    3 (A, B, C)")
    print("  Scores modificados:              A=0.8, B=0.3, C=0.5")
    print("  Chunks na re-indexação:          4 (A, B, C + novo D)")
    print("  Scores preservados:              A=0.8 ✓, B=0.3 ✓, C=0.5 ✓")
    print("  Novo chunk (D):                  score 0.5 ✓")
    print("  Mecanismo:                       COALESCE sobre content_hash")
    print("  Content hash match:              verificados 3/3 preservados")
    print("  Score bounds [0.0, 1.0]:         cap=1.0 ✓, floor=0.0 ✓")
    print("=" * 72)
    print("✓ T023 concluído com sucesso!")
    print("=" * 72)


# ═════════════════════════════════════════════════════════════════════════════
# Runner
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_reindex_idempotent_scores_preserved()
