from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from typing import Generic, Optional

from core import Heap, Key, Value


@dataclass(slots=True)
class Node(Generic[Key, Value]):
    key: Key
    value: Value
    sub_heaps: list[Node] = field(default_factory=list)


class PairingHeap(Heap[Key, Value]):
    root: Node | None
    size: int

    def __init__(self, items: Optional[list[tuple[Key, Value]]] = None) -> None:
        self.root = None
        self.size = 0
        for key, value in items or []:
            self.push(key, value)

    def find_min(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        return self.root.key, self.root.value

    @staticmethod
    def _meld(
        heap1: Optional[Node[Key, Value]], heap2: Optional[Node[Key, Value]]
    ) -> Node[Key, Value]:
        if heap1 is None:
            assert heap2 is not None
            return heap2
        elif heap2 is None:
            assert heap1 is not None
            return heap1
        elif heap1.key > heap2.key:
            heap2.sub_heaps.append(heap1)
            return heap2
        else:
            heap1.sub_heaps.append(heap2)
            return heap1

    def push(self, key: Key, value: Value) -> None:
        self.root = self._meld(self.root, Node(key, value))
        self.size += 1

    def pop(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        else:
            key, value = self.root.key, self.root.value
            self.root = reduce(self._meld, self.root.sub_heaps, None)
            self.size -= 1
            return key, value

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        raise NotImplemented

    def __contains__(self, __x: object) -> bool:
        if self.root is None:
            return False
        else:
            nodes: list[Node] = [self.root]
            while nodes:
                current = nodes.pop()
                if current.key == __x:
                    return True
                if current.sub_heaps:
                    nodes.extend(current.sub_heaps)
            return False

    def __len__(self) -> int:
        return self.size
