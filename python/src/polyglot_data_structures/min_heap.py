"""Binary min-heap stored in a flat list."""

from __future__ import annotations


class EmptyError(IndexError):
    """Raised when reading from an empty structure."""


class MinHeap:
    """Array-backed binary heap: O(log n) push and pop, O(1) peek."""

    def __init__(self) -> None:
        self._a: list[int] = []

    def __len__(self) -> int:
        return len(self._a)

    def push(self, value: int) -> None:
        """Add value and restore heap order."""
        self._a.append(value)
        self._sift_up(len(self._a) - 1)

    def peek(self) -> int:
        """Return the smallest value without removing it."""
        if not self._a:
            raise EmptyError("peek from empty heap")
        return self._a[0]

    def pop(self) -> int:
        """Remove and return the smallest value."""
        if not self._a:
            raise EmptyError("pop from empty heap")
        top = self._a[0]
        last = self._a.pop()
        if self._a:
            self._a[0] = last
            self._sift_down(0)
        return top

    def _sift_up(self, i: int) -> None:
        """Move the item at i up while it is smaller than its parent."""
        a = self._a
        item = a[i]
        while i > 0:
            parent = (i - 1) // 2
            if a[parent] <= item:
                break
            a[i] = a[parent]
            i = parent
        a[i] = item

    def _sift_down(self, i: int) -> None:
        """Move the item at i down below any smaller child."""
        a, n = self._a, len(self._a)
        item = a[i]
        while True:
            child = 2 * i + 1
            if child >= n:
                break
            if child + 1 < n and a[child + 1] < a[child]:
                child += 1
            if item <= a[child]:
                break
            a[i] = a[child]
            i = child
        a[i] = item
