from typing import Optional

from binary_heap import BinaryHeapTree, Node
from core import Key, Value


class SkewHeap(BinaryHeapTree[Key, Value]):
    def _push_node(self, node: Node[Key, Value]):
        self.root = self._skew_merge(self.root, node)

    def pop(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        key_value = self.root.key, self.root.value
        self.root = self._skew_merge(self.root.left, self.root.right)
        self.size -= 1
        return key_value

    def _skew_merge(
        self, heap1: Optional[Node[Key, Value]], heap2: Optional[Node[Key, Value]]
    ) -> Optional[Node[Key, Value]]:
        """
        Merge two skew heaps.

        Parameters
        ----------
        heap1 : Optional[Node[Key, Value]]
            The first skew heap.
        heap2 : Optional[Node[Key, Value]]
            The second skew heap.

        Returns
        -------
        Optional[Node[Key, Value]]
            The merged skew heap.

        Notes
        -----
        The skew heap is merged in-place.

        References
        ----------
        .. [1] https://en.wikipedia.org/wiki/Skew_heap
        .. [2] https://www.cs.usfca.edu/~galles/visualization/SkewHeap.html
        .. [3] https://www.cs.cmu.edu/~sleator/papers/adjusting-heaps.pdf
        """
        if heap1 is None:
            return heap2
        if heap2 is None:
            return heap1

        # ensure heap1.key <= heap2.key
        if heap1.key > heap2.key:
            heap1, heap2 = heap2, heap1

        # we traverse the right paths of heap1 and heap2,
        # merging them into a single increasing path
        # the left subtrees of nodes along the merged path do not change
        heap1.left, heap1.right = self._skew_merge(heap1.right, heap2), heap1.left

        return heap1

    def decrease_key(self, node: Node[Key, Value], new_key: Key) -> None:
        raise NotImplementedError
