from typing import Optional

from core import Heap, Key, Value
from heapq import heapify, heappop, heappush, heapreplace


class BinaryMinHeapArray(Heap[Key, Value]):
    items: list[tuple[Key, Value]]

    def __init__(self, items: Optional[list[tuple[Key, Value]]] = None) -> None:
        if items is None:
            self.items = []
        else:
            self.items = items
            heapify(self.items)

    def find_min(self) -> Optional[tuple[Key, Value]]:
        return self.items[0] if self.items else None

    def push(self, key: Key, value: Value) -> None:
        heappush(self.items, (key, value))

    def pop(self) -> tuple[Key, Value]:
        return heappop(self.items)

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        return heapreplace(self.items, (key, value))

    def __contains__(self, __x: object) -> bool:
        return any(key == __x for key, _ in self.items)

    def __len__(self) -> int:
        return len(self.items)
