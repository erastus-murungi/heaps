from typing import Optional

from binary_heap import Node
from core import Key, SelfAdjustingHeap, Value


class SkewHeap(SelfAdjustingHeap[Key, Value, Node[Key, Value]]):
    def _merge(
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
        heap1.left, heap1.right = self._merge(heap1.right, heap2), heap1.left

        return heap1

    def _node(self, key: Key, value: Value) -> Node[Key, Value]:
        return Node(key, value)
