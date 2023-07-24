from dataclasses import dataclass
from typing import Optional

from binary_heap import BinaryNodeAbstract
from core import Key, SelfAdjustingHeap, Value


@dataclass(slots=True)
class LeftistTreeNode(BinaryNodeAbstract[Key, Value, "LeftistTreeNode[Key, Value]"]):
    npl: int = 1


def null_path_length(node: Optional[LeftistTreeNode[Key, Value]]) -> int:
    if node is None:
        return 0
    else:
        return node.npl


class LeftistHeap(SelfAdjustingHeap[Key, Value, LeftistTreeNode[Key, Value]]):
    def _node(self, key: Key, value: Value) -> LeftistTreeNode[Key, Value]:
        return LeftistTreeNode(key, value)

    def _merge(
        self,
        heap1: Optional[LeftistTreeNode[Key, Value]],
        heap2: Optional[LeftistTreeNode[Key, Value]],
    ) -> Optional[LeftistTreeNode[Key, Value]]:
        if heap1 is None:
            return heap2
        elif heap2 is None:
            return heap1

        if heap1.key > heap2.key:
            heap1, heap2 = heap2, heap1

        heap1.right = self._merge(heap1.right, heap2)

        if null_path_length(heap1.left) < null_path_length(heap1.right):
            heap1.left, heap1.right = heap1.right, heap1.left

        heap1.npl = null_path_length(heap1.right) + 1

        return heap1
