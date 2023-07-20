from dataclasses import dataclass
from typing import Optional

from binary_heap import BinaryHeapTreeAbstract, BinaryNodeAbstract
from core import Key, Value


@dataclass
class LeftistTreeNode(BinaryNodeAbstract[Key, Value, "LeftistTreeNode[Key, Value]"]):
    npl: int = 1


def null_path_length(node: Optional[LeftistTreeNode[Key, Value]]) -> int:
    if node is None:
        return 0
    else:
        return node.npl


class LeftistHeap(BinaryHeapTreeAbstract[Key, Value, LeftistTreeNode[Key, Value]]):
    def decrease_key(self, node: LeftistTreeNode[Key, Value], new_key: Key) -> None:
        raise NotImplementedError

    def _push_node_non_empty(self, node: LeftistTreeNode[Key, Value]) -> None:
        self.root = self.meld(self.root, node)

    def pop(self) -> tuple[Key, Value]:
        if self.root is not None:
            key_value = self.root.key, self.root.value
            self.root = self.meld(self.root.left, self.root.right)
            self.size -= 1
            return key_value
        raise IndexError("Empty heap")

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        raise NotImplementedError

    def _node(self, key: Key, value: Value) -> LeftistTreeNode[Key, Value]:
        return LeftistTreeNode(key, value)

    def validate_leftist_property(self):
        def validate(node: Optional[LeftistTreeNode[Key, Value]]) -> bool:
            if node is None:
                return True
            else:
                return (
                    validate(node.left)
                    and validate(node.right)
                    and null_path_length(node.left) >= null_path_length(node.right)
                )

        assert validate(self.root)

    @staticmethod
    def meld(
        heap1: Optional[LeftistTreeNode[Key, Value]],
        heap2: Optional[LeftistTreeNode[Key, Value]],
    ) -> Optional[LeftistTreeNode[Key, Value]]:
        if heap1 is None:
            return heap2
        elif heap2 is None:
            return heap1

        if heap1.key > heap2.key:
            heap1, heap2 = heap2, heap1

        heap1.right = LeftistHeap.meld(heap1.right, heap2)

        if null_path_length(heap1.left) < null_path_length(heap1.right):
            heap1.left, heap1.right = heap1.right, heap1.left

        heap1.npl = null_path_length(heap1.right) + 1

        return heap1
