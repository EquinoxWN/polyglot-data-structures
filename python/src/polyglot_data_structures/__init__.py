"""polyglot-data-structures: core data structures that behave identically in Java, Python and JS."""

from polyglot_data_structures.hash_map import HashMap
from polyglot_data_structures.lru_cache import LRUCache
from polyglot_data_structures.min_heap import EmptyError, MinHeap

__version__ = "0.1.0"
__all__ = ["EmptyError", "HashMap", "LRUCache", "MinHeap"]
