"""Replay the shared JSON vectors against the Python implementations."""

import json
from pathlib import Path

import pytest

from polyglot_data_structures import HashMap, LRUCache, MinHeap
from polyglot_data_structures.min_heap import EmptyError

VECTORS = Path(__file__).resolve().parents[2] / "spec" / "vectors"
EMPTY = {"error": "empty"}


def apply(structure, op, args):
    """Run one operation and normalise its result to the vector format."""
    try:
        if op == "size":
            return len(structure)
        if op == "contains":
            return args[0] in structure
        if op == "push":
            structure.push(*args)
            return None
        return getattr(structure, op)(*args)
    except EmptyError:
        return EMPTY


FACTORIES = {
    "min_heap": lambda init: MinHeap(),
    "hash_map": lambda init: HashMap(),
    "lru_cache": lambda init: LRUCache(init["capacity"]),
}


def load_cases():
    """Yield (id, structure name, case) for every vector case."""
    for path in sorted(VECTORS.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for case in doc["cases"]:
            yield pytest.param(doc["structure"], case, id=f"{doc['structure']}: {case['name']}")


@pytest.mark.parametrize(("name", "case"), list(load_cases()))
def test_vector(name, case):
    structure = FACTORIES[name](case["init"])
    for step, (op, expected) in enumerate(zip(case["ops"], case["expect"], strict=True)):
        got = apply(structure, op[0], op[1:])
        assert got == expected, f"step {step}: {op} returned {got!r}, expected {expected!r}"


def test_vectors_exist():
    assert {p.stem for p in VECTORS.glob("*.json")} >= {"min_heap", "hash_map", "lru_cache"}


def test_lru_rejects_zero_capacity():
    with pytest.raises(ValueError, match="capacity must be at least 1"):
        LRUCache(0)
