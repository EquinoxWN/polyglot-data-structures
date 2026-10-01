"""Open-addressing hash map with linear probing and tombstones."""

from __future__ import annotations

from collections.abc import Hashable, Iterator
from typing import Any

_EMPTY = object()
_DELETED = object()


class HashMap:
    """Hash map in one flat slot array; grows at 3/4 load counting tombstones."""

    _INITIAL = 8

    def __init__(self) -> None:
        self._keys: list[Any] = [_EMPTY] * self._INITIAL
        self._values: list[Any] = [None] * self._INITIAL
        self._size = 0
        self._used = 0  # live entries plus tombstones

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: Hashable) -> bool:
        return self._find(key) >= 0

    def __iter__(self) -> Iterator[Any]:
        return (k for k in self._keys if k is not _EMPTY and k is not _DELETED)

    def _find(self, key: Hashable) -> int:
        """Return the slot holding key, or -1."""
        mask = len(self._keys) - 1
        i = hash(key) & mask
        while True:
            k = self._keys[i]
            if k is _EMPTY:
                return -1
            if k is not _DELETED and k == key:
                return i
            i = (i + 1) & mask

    def get(self, key: Hashable, default: Any = None) -> Any:
        """Return the value for key, or default."""
        i = self._find(key)
        return self._values[i] if i >= 0 else default

    def put(self, key: Hashable, value: Any) -> Any:
        """Insert or replace; return the previous value or None."""
        i = self._find(key)
        if i >= 0:
            old, self._values[i] = self._values[i], value
            return old
        if (self._used + 1) * 4 > len(self._keys) * 3:
            self._resize()
        mask = len(self._keys) - 1
        i = hash(key) & mask
        while self._keys[i] is not _EMPTY and self._keys[i] is not _DELETED:
            i = (i + 1) & mask
        if self._keys[i] is _EMPTY:
            self._used += 1
        self._keys[i], self._values[i] = key, value
        self._size += 1
        return None

    def remove(self, key: Hashable) -> Any:
        """Delete key; return its value or None."""
        i = self._find(key)
        if i < 0:
            return None
        old = self._values[i]
        self._keys[i], self._values[i] = _DELETED, None
        self._size -= 1
        return old

    def _resize(self) -> None:
        """Rehash live entries into a table sized for them, dropping tombstones."""
        items = [
            (k, v)
            for k, v in zip(self._keys, self._values, strict=True)
            if k is not _EMPTY and k is not _DELETED
        ]
        cap = self._INITIAL
        while cap * 3 < (len(items) + 1) * 8:  # keep load at or below 3/8 after growth
            cap *= 2
        self._keys, self._values = [_EMPTY] * cap, [None] * cap
        self._size = self._used = 0
        for k, v in items:
            self.put(k, v)
