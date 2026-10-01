"""Least-recently-used cache: hash index plus a doubly linked recency list."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Any


class _Node:
    __slots__ = ("key", "next", "prev", "value")

    def __init__(self, key: Any = None, value: Any = None) -> None:
        self.key, self.value = key, value
        self.prev: _Node = self
        self.next: _Node = self


class LRUCache:
    """Fixed-capacity cache with O(1) get and put."""

    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._index: dict[Any, _Node] = {}
        self._head = _Node()  # sentinel: head.next is most recent, head.prev least recent

    def __len__(self) -> int:
        return len(self._index)

    def _unlink(self, node: _Node) -> None:
        """Remove node from the recency list."""
        node.prev.next, node.next.prev = node.next, node.prev

    def _push_front(self, node: _Node) -> None:
        """Insert node as most recently used."""
        node.prev, node.next = self._head, self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key: Hashable) -> Any:
        """Return the value and mark key most recent, or None."""
        node = self._index.get(key)
        if node is None:
            return None
        self._unlink(node)
        self._push_front(node)
        return node.value

    def put(self, key: Hashable, value: Any) -> Any:
        """Insert or update key; return the evicted key or None."""
        node = self._index.get(key)
        if node is not None:
            node.value = value
            self._unlink(node)
            self._push_front(node)
            return None
        evicted = None
        if len(self._index) == self._capacity:
            lru = self._head.prev
            self._unlink(lru)
            del self._index[lru.key]
            evicted = lru.key
        node = _Node(key, value)
        self._index[key] = node
        self._push_front(node)
        return evicted
