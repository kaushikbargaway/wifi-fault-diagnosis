"""Standalone retrieval test for the RAG pipeline.

Run from the project root:

    python scripts/test_retrieval.py

What it does
------------
1. Runs ingestion: loads all .md documents, chunks them, embeds them,
   builds a FAISS index, and saves it to rag/vectorstore/.
2. Queries the index with example questions.
3. Prints the top-3 retrieved chunks with source, section, and similarity.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path

# Force UTF-8 output on Windows (avoids CP1252 UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Ensure the backend package is importable regardless of CWD
# ---------------------------------------------------------------------------
# Bootstrap: compute root the same way paths.py does — walk up looking for
# the sentinel dirs (rag/ + backend/) — then import get_project_root() for
# everything else.
_here = Path(__file__).resolve().parent  # scripts/
for _candidate in [_here.parent, *_here.parents]:
    if (_candidate / "rag").is_dir() and (_candidate / "backend").is_dir():
        _PROJECT_BOOTSTRAP = _candidate
        break
else:
    raise RuntimeError("Cannot locate project root from scripts/test_retrieval.py")

BACKEND_DIR = _PROJECT_BOOTSTRAP / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Now we can import the canonical helper and use it everywhere
from app.core.paths import get_project_root  # noqa: E402

PROJECT_ROOT = get_project_root()

# Change CWD to project root so relative paths in config work correctly
os.chdir(PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("test_retrieval")

# ---------------------------------------------------------------------------
# Step 1 — Ingestion
# ---------------------------------------------------------------------------

def run_ingestion() -> int:
    from app.rag.ingestion import ingest_documents

    logger.info("=" * 60)
    logger.info("STEP 1 — Running ingestion pipeline …")
    logger.info("=" * 60)
    total_chunks = ingest_documents()
    print(f"\n✓ Ingestion complete — {total_chunks} chunks indexed.\n")
    return total_chunks


# ---------------------------------------------------------------------------
# Step 2 — Retrieval test
# ---------------------------------------------------------------------------

EXAMPLE_QUERIES = [
    "What are the common causes of packet loss and what recovery actions are recommended?",
    "How do I diagnose and fix DNS failure?",
    "What causes high latency in Wi-Fi networks?",
]


def run_retrieval_test() -> None:
    from app.rag.retriever import retrieve_context

    logger.info("=" * 60)
    logger.info("STEP 2 — Running retrieval test …")
    logger.info("=" * 60)

    for query_idx, query in enumerate(EXAMPLE_QUERIES, start=1):
        print(f"\n{'='*60}")
        print(f"Query {query_idx}: {query}")
        print("=" * 60)

        results = retrieve_context(query, top_k=3)

        if not results:
            print("  [No results returned — check that ingestion ran successfully]")
            continue

        for rank, result in enumerate(results, start=1):
            bar_width = int(result["score"] * 30)
            similarity_bar = "█" * bar_width + "░" * (30 - bar_width)

            print(f"\n  ── Result #{rank} ──────────────────────────────────────")
            print(f"  Source   : {result['source']}")
            print(f"  Section  : {result['section']}")
            print(f"  Score    : {result['score']:.4f}  [{similarity_bar}]")
            print(f"  Chunk idx: {result['chunk_index']}")
            print(f"\n  Text:")
            # Indent and wrap the chunk text for readability
            for line in result["text"].splitlines():
                print(f"    {line}")

        print()


# ---------------------------------------------------------------------------
# Step 3 — Summary
# ---------------------------------------------------------------------------

def print_vectorstore_summary() -> None:
    vs_dir = PROJECT_ROOT / "rag" / "vectorstore"
    index_file = vs_dir / "index.faiss"
    meta_file = vs_dir / "metadata.json"

    print("\n" + "=" * 60)
    print("Vectorstore files:")
    for f in [index_file, meta_file]:
        size_kb = f.stat().st_size / 1024 if f.exists() else 0
        status = "✓" if f.exists() else "✗"
        print(f"  {status} {f.relative_to(PROJECT_ROOT)}  ({size_kb:.1f} KB)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\nRAG Retrieval Pipeline — Integration Test")
    print("Project root:", PROJECT_ROOT)
    print()

    try:
        run_ingestion()
        run_retrieval_test()
        print_vectorstore_summary()
        print("\n✓ All tests passed.\n")
    except FileNotFoundError as e:
        print(f"\n✗ FileNotFoundError: {e}\n", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"\n✗ ImportError: {e}\n", file=sys.stderr)
        print(
            "Install dependencies:  pip install faiss-cpu>=1.8.0 sentence-transformers>=3.0.0",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        logger.exception("Unexpected error during retrieval test.")
        print(f"\n✗ {type(e).__name__}: {e}\n", file=sys.stderr)
        sys.exit(1)
