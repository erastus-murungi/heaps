from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator, Optional

from core import AbstractNode, Key, SelfAdjustingHeap, Value


@dataclass(slots=True)
class Node(AbstractNode[Key, Value, "Node[Key, Value]"]):
    sub_heaps: list[Node] = field(default_factory=list)

    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        yield f"{indent}{prefix}----{self}\n"
        indent += "     " if prefix == "R" else "|    "
        for index, sub_heap in enumerate(self.sub_heaps):
            yield from sub_heap.yield_line(indent, f"S{index}")

    def iter_children(self) -> Iterator[Node[Key, Value]]:
        yield from self.sub_heaps


class PairingHeap(SelfAdjustingHeap[Key, Value, Node[Key, Value]]):
    def _merge(
        self, heap1: Optional[Node[Key, Value]], heap2: Optional[Node[Key, Value]]
    ) -> Optional[Node[Key, Value]]:
        if heap1 is None:
            return heap2
        elif heap2 is None:
            return heap1
        elif heap1.key > heap2.key:
            heap2.sub_heaps.append(heap1)
            return heap2
        else:
            heap1.sub_heaps.append(heap2)
            return heap1

    def _node(self, key: Key, value: Value) -> Node[Key, Value]:
        return Node(key, value)
