"""Generate the shared test vectors from standard-library reference models.

Usage:
    python spec/generate_vectors.py          # rewrite spec/vectors/*.json
    python spec/generate_vectors.py --check  # fail if the committed files are stale
"""

from __future__ import annotations

import argparse
import heapq
import json
import random
import sys
from collections import OrderedDict
from pathlib import Path

VECTORS = Path(__file__).parent / "vectors"
EMPTY = {"error": "empty"}
SEED = 20260930


def run_heap(ops):
    """Replay heap ops against heapq."""
    h, out = [], []
    for op, *args in ops:
        if op == "push":
            heapq.heappush(h, args[0])
            out.append(None)
        elif op == "pop":
            out.append(heapq.heappop(h) if h else EMPTY)
        elif op == "peek":
            out.append(h[0] if h else EMPTY)
        elif op == "size":
            out.append(len(h))
        else:
            raise ValueError(op)
    return out


def run_map(ops):
    """Replay map ops against dict."""
    d, out = {}, []
    for op, *args in ops:
        if op == "put":
            out.append(d.get(args[0]))
            d[args[0]] = args[1]
        elif op == "get":
            out.append(d.get(args[0]))
        elif op == "remove":
            out.append(d.pop(args[0], None))
        elif op == "contains":
            out.append(args[0] in d)
        elif op == "size":
            out.append(len(d))
        else:
            raise ValueError(op)
    return out


def run_lru(capacity, ops):
    """Replay LRU ops against OrderedDict."""
    d, out = OrderedDict(), []
    for op, *args in ops:
        if op == "put":
            key, evicted = args[0], None
            if key in d:
                d.move_to_end(key)
            elif len(d) == capacity:
                evicted, _ = d.popitem(last=False)
            d[key] = args[1]
            out.append(evicted)
        elif op == "get":
            if args[0] in d:
                d.move_to_end(args[0])
            out.append(d.get(args[0]))
        elif op == "size":
            out.append(len(d))
        else:
            raise ValueError(op)
    return out


def random_heap_ops(rng, n):
    """Random heap workload with duplicates, negatives and empty pops."""
    ops = []
    for _ in range(n):
        r = rng.random()
        if r < 0.5:
            ops.append(["push", rng.randint(-1000, 1000)])
        elif r < 0.85:
            ops.append(["pop"])
        elif r < 0.95:
            ops.append(["peek"])
        else:
            ops.append(["size"])
    return ops


def random_map_ops(rng, n, keyspace):
    """Random map workload over a small keyspace to force collisions and reuse."""
    ops = []
    for _ in range(n):
        key = f"k{rng.randrange(keyspace)}"
        r = rng.random()
        if r < 0.45:
            ops.append(["put", key, rng.randint(0, 10**6)])
        elif r < 0.7:
            ops.append(["get", key])
        elif r < 0.9:
            ops.append(["remove", key])
        elif r < 0.97:
            ops.append(["contains", key])
        else:
            ops.append(["size"])
    return ops


def random_lru_ops(rng, n, keyspace):
    """Random LRU workload."""
    ops = []
    for _ in range(n):
        key = f"k{rng.randrange(keyspace)}"
        r = rng.random()
        if r < 0.5:
            ops.append(["put", key, rng.randint(0, 1000)])
        elif r < 0.95:
            ops.append(["get", key])
        else:
            ops.append(["size"])
    return ops


def heap_cases(rng):
    """Hand-written heap edge cases plus random ones."""
    cases = [
        {"name": "pop and peek on empty", "ops": [["pop"], ["peek"], ["size"]]},
        {
            "name": "orders ascending",
            "ops": [["push", 5], ["push", 1], ["push", 3], ["pop"], ["pop"], ["pop"], ["pop"]],
        },
        {
            "name": "keeps duplicates",
            "ops": [["push", 2], ["push", 2], ["push", 1], ["size"], ["pop"], ["pop"], ["pop"]],
        },
        {
            "name": "negative values",
            "ops": [["push", -1], ["push", -7], ["push", 0], ["peek"], ["pop"], ["peek"]],
        },
    ]
    cases.extend({"name": f"random {i}", "ops": random_heap_ops(rng, 400)} for i in range(3))
    for c in cases:
        c["init"] = {}
        c["expect"] = run_heap(c["ops"])
    return cases


def map_cases(rng):
    """Hand-written map edge cases plus random ones."""
    cases = [
        {
            "name": "missing key",
            "ops": [["get", "a"], ["remove", "a"], ["contains", "a"], ["size"]],
        },
        {
            "name": "put returns previous value",
            "ops": [["put", "a", 1], ["put", "a", 2], ["get", "a"], ["size"]],
        },
        {
            "name": "remove then reinsert",
            "ops": [
                ["put", "a", 1],
                ["remove", "a"],
                ["contains", "a"],
                ["put", "a", 3],
                ["get", "a"],
                ["size"],
            ],
        },
        {
            "name": "grows past initial capacity",
            "ops": [["put", f"k{i}", i] for i in range(100)]
            + [["size"], ["get", "k0"], ["get", "k99"]],
        },
    ]
    cases.extend(
        {"name": f"random {i}", "ops": random_map_ops(rng, 600, keyspace=40 * (i + 1))}
        for i in range(3)
    )
    for c in cases:
        c["init"] = {}
        c["expect"] = run_map(c["ops"])
    return cases


def lru_cases(rng):
    """Hand-written LRU edge cases plus random ones."""
    cases = [
        {
            "name": "evicts least recently used",
            "init": {"capacity": 2},
            "ops": [
                ["put", "a", 1],
                ["put", "b", 2],
                ["put", "c", 3],
                ["get", "a"],
                ["get", "b"],
                ["get", "c"],
            ],
        },
        {
            "name": "get refreshes recency",
            "init": {"capacity": 2},
            "ops": [
                ["put", "a", 1],
                ["put", "b", 2],
                ["get", "a"],
                ["put", "c", 3],
                ["get", "a"],
                ["get", "b"],
            ],
        },
        {
            "name": "update does not evict",
            "init": {"capacity": 2},
            "ops": [
                ["put", "a", 1],
                ["put", "b", 2],
                ["put", "a", 9],
                ["size"],
                ["get", "a"],
                ["put", "c", 3],
                ["get", "b"],
            ],
        },
        {
            "name": "capacity one",
            "init": {"capacity": 1},
            "ops": [["put", "a", 1], ["put", "b", 2], ["get", "a"], ["get", "b"], ["size"]],
        },
    ]
    cases.extend(
        {
            "name": f"random {i} (capacity {cap})",
            "init": {"capacity": cap},
            "ops": random_lru_ops(rng, 600, keyspace=cap * 3),
        }
        for i, cap in enumerate([3, 8, 32])
    )
    for c in cases:
        c["expect"] = run_lru(c["init"]["capacity"], c["ops"])
    return cases


def build():
    """Return {file name: document} for every structure."""
    rng = random.Random(SEED)
    return {
        "min_heap.json": {"structure": "min_heap", "cases": heap_cases(rng)},
        "hash_map.json": {"structure": "hash_map", "cases": map_cases(rng)},
        "lru_cache.json": {"structure": "lru_cache", "cases": lru_cases(rng)},
    }


def render(doc):
    """Serialise one vector file deterministically."""
    return json.dumps(doc, indent=1, sort_keys=True) + "\n"


def main():
    """Write or check the vector files."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if committed vectors are stale")
    args = parser.parse_args()
    VECTORS.mkdir(exist_ok=True)
    stale = []
    for name, doc in build().items():
        path = VECTORS / name
        text = render(doc)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
    if stale:
        sys.exit(f"stale vectors: {', '.join(stale)}; run python spec/generate_vectors.py")


if __name__ == "__main__":
    main()
