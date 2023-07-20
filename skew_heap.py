from binary_heap import BinaryHeapTree, Node
from core import Key, NodeType, Value


class SkewHeap(BinaryHeapTree[Key, Value]):
    def _push_node(self, node: NodeType):
        self.root = node if self.root is None else self._skew_merge(self.root, node)

    def pop(self) -> tuple[Key, Value]:
        key_value = self.find_min()
        self.root = self._skew_merge(self.root.left, self.root.right)
        return key_value

    def _skew_merge(
        self, heap1: Node[Key, Value] | None, heap2: Node[Key, Value] | None
    ) -> Node[Key, Value]:
        if heap1 is None:
            return heap2
        if heap2 is None:
            return heap1

        if heap2.key < heap1.key:
            heap1, heap2 = heap2, heap1

        heap1.left, heap1.right = heap1.right, heap1.left
        heap1.left = self._skew_merge(heap1.left, heap2)

        return heap1

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        raise NotImplemented

    def decrease_key(self, node: NodeType, new_key: Key) -> None:
        raise NotImplemented
