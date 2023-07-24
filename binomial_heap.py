from __future__ import annotations

from dataclasses import dataclass
from itertools import zip_longest
from operator import attrgetter
from typing import Iterator, Optional

from core import AbstractNode, Heap, Key, Value


@dataclass(slots=True)
class Node(AbstractNode[Key, Value, "Node[Key, Value]"]):
    """
    A node in a binomial heap.

    Attributes
    ----------
    key : Key
        The key of the node.
    value : Value
        The value of the node.
    child : Optional[Node[Key, Value]]
        The leftmost child of the node.
        If the node has no children, then it is None.
    sibling : Optional[Node[Key, Value]]
        The sibling of the node immediately to the right.
        If the node is the rightmost child of its parent,then sibling is None.
    """

    child: Optional[Node[Key, Value]] = None
    sibling: Optional[Node[Key, Value]] = None

    def link(self, other: Node[Key, Value]) -> Node[Key, Value]:
        """
        Links two binomial trees of the same order together.

        Parameters
        ----------
        other : Node[Key, Value]
            The other node to link to.

        Returns
        -------
        Node[Key, Value]
            The root of the resulting tree.

        Notes
        ------
        The nodes do not store their order, so the caller must ensure that the orders are the same.
        The root with the smaller key becomes the parent of the root with the larger key.

        """
        root = self
        if root.key > other.key:
            root, other = other, root
        other.sibling = root.child
        root.child = other
        return root

    def children(self) -> Iterator[Node[Key, Value]]:
        """
        Iterate over the children of the node.

        Yields
        ------
        Node[Key, Value]
            The siblings of the node.
        """
        node: Optional[Node[Key, Value]] = self.child
        while node is not None:
            yield node
            node = node.sibling

    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        yield f"{indent}{prefix}----{self}\n"
        indent += "     " if prefix == "R" else "|    "
        for index, sub_heap in enumerate(self.children()):
            yield from sub_heap.yield_line(indent, f"S{index}")


class BinomialHeap(Heap[Key, Value, Node[Key, Value]]):
    def __init__(self, items: list[tuple[Key, Value]] | None = None) -> None:
        self.trees: list[Node[Key, Value] | None] = []
        self.size: int = 0

        for key, value in items or []:
            self.enqueue(key, value)

    @staticmethod
    def _one_bit_full_adder(
        a: Optional[Node[Key, Value]],
        b: Optional[Node[Key, Value]],
        carry: Optional[Node[Key, Value]],
    ) -> tuple[Optional[Node[Key, Value]], Optional[Node[Key, Value]]]:
        """
        Add three nodes ('bits') together using a full adder

        References
        ----------
        .. [1] https://web.mit.edu/6.111/www/f2017/handouts/L08.pdf
        """
        if a is None:
            if b is None and carry is None:
                return None, None
            elif b is None and carry:
                return carry, None
            elif b and carry is None:
                return b, None
            else:
                assert b and carry
                return None, carry.link(b)
        elif b is None:
            # `a` is not None
            if carry is None:
                return a, None
            else:
                return None, a.link(carry)
        else:
            # `a` and `b` are not None
            if carry is None:
                return None, a.link(b)
            else:
                return carry, a.link(b)

    @staticmethod
    def _add_root_lists(
        list1: list[Node[Key, Value] | None], list2: list[Node[Key, Value] | None]
    ) -> list[Node[Key, Value] | None]:
        """
        Adds two lists of binomial trees together.

        Parameters
        ----------
        list1 : list[Node[Key, Value] | None]
            The first list of binomial trees.
        list2 : list[Node[Key, Value] | None]
            The second list of binomial trees.

        Returns
        -------
        list[Node[Key, Value] | None]
            The resulting list of binomial trees.

        Notes
        -----
        This idea of merging is taken from [2].
        We are essentially simulating a ripple carry adder.
        https://en.wikipedia.org/wiki/Adder_(electronics)#Ripple-carry_adder

        We treat the tree at index i in the list as a binary number. The tree
        at index has 2^i nodes. We add the two lists together by adding the binary numbers together. The result is a
        list of binomial trees with no more than one tree of each order. We go from the least significant bit to most
        significant bit, and we keep track of the carry.


        References
        ----------
        .. [1] https://web.stanford.edu/class/archive/cs/cs166/cs166.1186/lectures/08/Slides08.pdf
        .. [2] https://en.wikipedia.org/wiki/Binomial_heap#Merging

        """

        result: list[Node[Key, Value] | None] = []
        carry: Node[Key, Value] | None = None

        for top, low in zip_longest(list1, list2):
            t, carry = BinomialHeap._one_bit_full_adder(top, low, carry)
            result.append(t)

        # Finally, if the carry is set, append it to the result.
        if carry is not None:
            result.append(carry)
        return result

    def enqueue(self, key: Key, value: Value) -> Node[Key, Value]:
        """
        Insert a new element into the Binomial heap.

        Parameters
        ----------
        key : Key
            The key of the new element.
        value : Value
            The value of the new element.

        Notes
        -----
        This operation is O(log n) where n is the number of elements in the heap.
        Works by simply adding a 'least significant packet' to the root list.
        """
        node = Node[Key, Value](key, value)
        self.trees = self._add_root_lists(self.trees, [node])
        self.size += 1
        return node

    def find_min(self) -> tuple[Key, Value]:
        """
        Return the minimum element of the Binomial heap.

        Returns
        -------
        tuple[Key, Value]
            The smallest element of the Binomial heap.

        Raises
        ------
        IndexError
            If the heap is empty, this throws an IndexError.

        Notes
        -----
        This operation is O(log n) where n is the number of elements in the heap.
        Works by checking which of the root nodes has the smallest key.

        """

        if not self.trees:
            raise IndexError("Heap is empty.")
        min_node = min(filter(None, self.trees), key=attrgetter("key"))
        return min_node.key, min_node.value

    def extract_min(self) -> tuple[Key, Value]:
        if not self.trees:
            raise IndexError("Heap is empty.")

        min_node = min(filter(None, self.trees), key=attrgetter("key"))
        min_node_index = self.trees.index(min_node)

        # fracture the packet
        fractures: list[Node[Key, Value] | None] = []
        current_child = min_node.child

        while current_child is not None:
            fractures.append(current_child)
            nxt_child = current_child.sibling
            current_child.sibling = None
            current_child = nxt_child

        self.trees.pop(min_node_index)

        # remove any trailing None values
        while self.trees and self.trees[-1] is None:
            self.trees.pop()

        # ensure that the fractures are in monotonically increasing order
        fractures.reverse()
        self.trees = self._add_root_lists(self.trees, fractures)
        self.size -= 1
        return min_node.key, min_node.value

    def __len__(self) -> int:
        return self.size

    def __contains__(self, item: object) -> bool:
        nodes = self.trees[:]
        while nodes:
            node = nodes.pop()
            if node is None:
                continue
            if node.key == item:
                return True
            nodes.append(node.child)
            nodes.append(node.sibling)
        return False


if __name__ == "__main__":
    keys = [0, 0, 0, 0, 0, 0, 0]
    heap = BinomialHeap[int, None]([(k, None) for k in keys])  # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]
