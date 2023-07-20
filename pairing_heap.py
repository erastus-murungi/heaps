from __future__ import annotations

from dataclasses import dataclass, field
from functools import reduce
from typing import Iterator, Optional

from binary_heap import HeapTree
from core import AbstractNode, Key, NodeType, Value


@dataclass(slots=True)
class Node(AbstractNode[Key, Value, "Node[Key, Value]"]):
    sub_heaps: list[Node] = field(default_factory=list)

    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        yield f"{indent}{prefix}----{self}\n"
        indent += "     " if prefix == "R" else "|    "
        for index, sub_heap in enumerate(self.sub_heaps):
            yield from sub_heap.yield_line(indent, f"S{index}")


class PairingHeap(HeapTree[Key, Value, Node[Key, Value]]):
    @staticmethod
    def _meld(
        heap1: Optional[Node[Key, Value]], heap2: Optional[Node[Key, Value]]
    ) -> Node[Key, Value]:
        # assert heap1 or heap2
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

    def pop(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        else:
            key, value = self.root.key, self.root.value
            self.root = reduce(self._meld, self.root.sub_heaps, None)
            self.size -= 1
            return key, value

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

    def _push_node(self, node: Node[Key, Value]):
        self.root = self._meld(self.root, node)

    def _node(self, key: Key, value: Value) -> Node[Key, Value]:
        return Node(key, value)

    def decrease_key(self, node: NodeType, new_key: Key) -> None:
        raise NotImplementedError

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        raise NotImplementedError
