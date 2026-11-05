"""Behaviour the shared vectors cannot express: growth, validation and bad input."""

import math

import pytest

from polyglot_data_structures import HashMap, LRUCache, MinHeap


def filled(n):
    m = HashMap()
    for i in range(n):
        m.put(f"k{i}", i)
    return m


def test_hash_map_grows_past_three_quarters_load():
    assert filled(6).capacity == 8
    # The 7th key would pass 3/4 of 8 slots; the new table keeps load at or below 3/8.
    assert filled(7).capacity == 32


def test_reusing_a_tombstone_does_not_count_as_a_new_slot():
    m = filled(5)
    m.remove("k0")
    m.put("k0", 0)  # lands in its own tombstone
    m.put("k5", 5)
    assert m.capacity == 8
    assert [m.get(f"k{i}") for i in range(6)] == list(range(6))


@pytest.mark.parametrize("capacity", [0, -1, 2.5, math.inf, math.nan, "2", True])
def test_lru_rejects_capacity_that_is_not_a_positive_integer(capacity):
    with pytest.raises(ValueError, match="capacity must be an integer"):
        LRUCache(capacity)


def test_lru_accepts_a_whole_float_capacity_as_before():
    cache = LRUCache(2.0)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.put("c", 3) == "a"


def test_heap_rejects_nan():
    h = MinHeap()
    with pytest.raises(ValueError, match="NaN"):
        h.push(math.nan)
    assert len(h) == 0
