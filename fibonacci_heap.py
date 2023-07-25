from __future__ import annotations

from bisect import insort
from collections import deque
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Iterator, Optional

from core import AbstractNode, Heap, Key, Value


@dataclass(slots=True)
class Node(AbstractNode[Key, Value, "Node[Key, Value]"]):
    degree: int = 0
    marked: bool = False
    parent: Node[Key, Value] | None = field(default=None, init=False, repr=False)
    child: Node[Key, Value] | None = field(default=None, init=False, repr=False)
    next: Node[Key, Value] = field(init=False, repr=False)
    prev: Node[Key, Value] = field(init=False, repr=False)

    def __post_init__(self):
        self.next = self.prev = self

    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        raise NotImplementedError

    def iter_children(self) -> Iterator[Node[Key, Value]]:
        """
        Iterate over the children of the node.

        Yields
        ------
        Node[Key, Value]
            The siblings of the node.
        """
        curr = self.child
        if curr is not None:
            while True:
                yield curr
                curr = curr.next
                if curr is self.child:
                    break


@dataclass(slots=True, init=False)
class FibonacciHeap(Heap[Key, Value, Node[Key, Value]]):
    """
    Fibonacci heap implementation.
    Inspired by https://www.keithschwarz.com/interesting/code/?dir=fibonacci-heap
    """

    root: Optional[Node[Key, Value]]
    size: int

    def __init__(self, items: list[tuple[Key, Value]] | None = None) -> None:
        self.root = None
        self.size = 0

        for key, value in items or []:
            self.enqueue(key, value)

    def find_min(self) -> tuple[Key, Value]:
        if not self.root:
            raise IndexError("Empty heap")
        return self.root.key, self.root.value

    def enqueue(self, key: Key, value: Value) -> Node[Key, Value]:
        node = Node(key, value)
        self.root = self._merge_circular_doubly_linked_lists(self.root, node)
        self.size += 1
        return node

    def extract_min(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")

        self.size -= 1

        min_node = self.root
        if min_node.next is min_node:
            self.root = None
        else:
            self.root.prev.next = self.root.next
            self.root.next.prev = self.root.prev
            # Arbitrary element of the root list.
            self.root = self.root.next

        # clear the parent field for all the minimum node's children
        # since they are about to become roots
        if min_node.child is not None:
            curr = min_node.child
            while True:
                curr.parent = None
                curr = curr.next
                if curr is min_node.child:
                    break

        # merge the children of the minimum node with the root list
        self.root = self._merge_circular_doubly_linked_lists(self.root, min_node.child)

        if self.root is not None:
            # consolidate the root list by joining trees of equal degree
            # (by creating a list of root nodes with distinct degrees)
            # Next, we need to coalesce all the roots so that there is only one
            # tree of each degree. To track trees of each size, we allocate an
            # ArrayList where the entry at position `i` is either None or the
            # unique tree of degree `i`.
            tree_table: deque[Optional[Node[Key, Value]]] = deque()

            # We need to traverse the entire list, but since we're going to be
            # messing around with it, we have to be careful not to break our
            # traversal order mid-stream. One major challenge is how to detect
            # whether we're visiting the same node twice. To do this, we'll
            # spend a bit of overhead adding all the nodes to a list, and
            # then will visit each element of this list in order.
            to_visit: deque[Node[Key, Value]] = deque()

            # To add everything, we'll iterate across the elements until we
            # find the first element twice. We check this by looping while the
            # list is empty or while the current element isn't the first element
            # of that list.

            curr = self.root
            while not to_visit or to_visit[0] is not curr:
                to_visit.append(curr)
                curr = curr.next

            # Traverse this list and perform the appropriate union steps.
            for curr in to_visit:
                # Keep merging until a match arises.
                while True:
                    # Ensure that the list is long enough to hold an element of this degree.
                    while curr.degree >= len(tree_table):
                        tree_table.append(None)

                    # If nothing's here, we can record that this tree has this size
                    # and are done processing.
                    if tree_table[curr.degree] is None:
                        tree_table[curr.degree] = curr
                        break

                    # Otherwise, merge with what's there.
                    other = tree_table[curr.degree]
                    if other is None:
                        raise RuntimeError

                    # Clear the slot
                    tree_table[curr.degree] = None

                    # Determine which of the two trees has the smaller root, storing
                    # the two trees accordingly. In the event of a tie, ensure
                    # minimum and maximum and assigned different trees.
                    minimum = min(curr, other, key=attrgetter("key"))
                    maximum = max(other, curr, key=attrgetter("key"))

                    # Break max out of the root list, then merge it into min's child list.
                    maximum.next.prev = maximum.prev
                    maximum.prev.next = maximum.next

                    # Make it a singleton so that we can merge it.
                    maximum.next = maximum.prev = maximum
                    minimum.child = self._merge_circular_doubly_linked_lists(
                        minimum.child, maximum
                    )

                    # Re-parent maximum appropriately.
                    maximum.parent = minimum

                    # Clear maximum's mark, since it can now lose another child.
                    maximum.marked = False

                    # Increase minimum's degree; it now has another child.
                    minimum.degree += 1

                    # Continue merging this tree.
                    curr = minimum  # noqa: PLW2901

                # Update the global min based on this node. Note that we compare
                # for <= instead of < here. That's because if we just did a
                # re-parent operation that merged two different trees of equal
                # priority, we need to make sure that the min pointer points to
                # the root-level one.
                if curr.key <= self.root.key:
                    self.root = curr
        return min_node.key, min_node.value

    def __contains__(self, __x: object) -> bool:
        nodes = [self.root]
        while nodes:
            node = nodes.pop()
            if node is None:
                continue
            if node.key == __x:
                return True
            nodes.append(node.child)
            nodes.append(node.next)
        return False

    def __len__(self) -> int:
        return self.size

    @staticmethod
    def _merge_circular_doubly_linked_lists(
        node1: Optional[Node[Key, Value]], node2: Optional[Node[Key, Value]]
    ) -> Optional[Node[Key, Value]]:
        if node1 is None:
            return node2
        elif node2 is None:
            return node1
        else:
            node1.next, node2.next = node2.next, node1.next
            node1.next.prev, node2.next.prev = node1, node2
            return min(node1, node2, key=attrgetter("key"))

    def _cascading_cut(self, node: Node[Key, Value]) -> None:
        assert node.marked

        node.marked = False
        # Base case: If the node has no parent, we're done.
        if node.parent is None:
            return None

        # if the node has siblings, splice it out
        if node.next is not node:
            node.next.prev, node.prev.next = node.prev, node.next

        # if the node is the child of its parent, set the parent's child to
        # a sibling of the node
        if node.parent.child is node:
            # there exists other children
            if node.next is not node:
                node.parent.child = node.next
            # no other children
            else:
                node.parent.child = None

        # decrement the degree of the parent, since we just removed a child
        node.parent.degree -= 1

        # make the node a singleton tree (circular doubly linked list)
        node.next = node.prev = node

        # merge the node into the root list
        self.root = self._merge_circular_doubly_linked_lists(self.root, node)

        if node.parent.marked:
            self._cascading_cut(node.parent)
        else:
            node.parent.marked = True

        node.parent = None


@dataclass(slots=True)
class NodeL(AbstractNode[Key, Value, "NodeL[Key, Value]"]):
    degree: int = 0
    marked: bool = False
    parent: Optional[NodeL[Key, Value]] = field(default=None, init=False, repr=False)
    children: list[NodeL[Key, Value]] = field(default_factory=list)

    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        raise NotImplementedError

    def iter_children(self) -> Iterator[NodeL[Key, Value]]:
        yield from self.children


@dataclass(slots=True, init=False)
class FibonacciHeapArray(Heap[Key, Value, NodeL[Key, Value]]):
    trees: list[NodeL[Key, Value]]
    size: int

    def __init__(self, items: list[tuple[Key, Value]] | None = None) -> None:
        self.trees = []
        self.size = 0

        for key, value in items or []:
            self.enqueue(key, value)

    def find_min(self) -> tuple[Key, Value]:
        if not self.trees:
            raise IndexError("Empty heap")
        min_node = self.trees[-1]
        return min_node.key, min_node.value

    def enqueue(self, key: Key, value: Value) -> NodeL[Key, Value]:
        node = NodeL[Key, Value](key, value)
        self.trees = self._merge(self.trees, [node])
        self.size += 1
        return node

    def extract_min(self) -> tuple[Key, Value]:
        if not self.trees:
            raise IndexError("Empty heap")

        self.size -= 1

        min_node = self.trees.pop()

        # clear the parent field for all the minimum node's children
        # since they are about to become roots
        for child in min_node.children:
            child.parent = None

        # merge the children of the minimum node with the root list
        self.trees = self._merge(self.trees, min_node.children)

        if self.trees is not None:
            # consolidate the root list by joining trees of equal degree
            # (by creating a list of root nodes with distinct degrees)
            # Next, we need to coalesce all the roots so that there is only one
            # tree of each degree. To track trees of each size, we allocate an
            # ArrayList where the entry at position `i` is either None or the
            # unique tree of degree `i`.
            tree_table: deque[Optional[NodeL[Key, Value]]] = deque()

            # We need to traverse the entire list, but since we're going to be
            # messing around with it, we have to be careful not to break our
            # traversal order mid-stream. One major challenge is how to detect
            # whether we're visiting the same node twice. To do this, we'll
            # spend a bit of overhead adding all the nodes to a list, and
            # then will visit each element of this list in order.

            # To add everything, we'll iterate across the elements until we
            # find the first element twice. We check this by looping while the
            # list is empty or while the current element isn't the first element
            # of that list.
            to_visit: deque[NodeL[Key, Value]] = deque(self.trees)

            # Traverse this list and perform the appropriate union steps.
            for curr in to_visit:
                # Keep merging until a match arises.
                while True:
                    # Ensure that the list is long enough to hold an element of this degree.
                    while curr.degree >= len(tree_table):
                        tree_table.append(None)

                    # If nothing's here, we can record that this tree has this size
                    # and are done processing.
                    if tree_table[curr.degree] is None:
                        tree_table[curr.degree] = curr
                        break

                    # Otherwise, merge with what's there.
                    other = tree_table[curr.degree]
                    if other is None:
                        raise RuntimeError

                    # Clear the slot
                    tree_table[curr.degree] = None

                    # Determine which of the two trees has the smaller root, storing
                    # the two trees accordingly. In the event of a tie, ensure
                    # minimum and maximum and assigned different trees.
                    minimum = min(curr, other, key=attrgetter("key"))
                    maximum = max(other, curr, key=attrgetter("key"))
                    assert minimum and maximum

                    # Break max out of the root list, then merge it into min's child list.
                    self.trees.remove(maximum)

                    # TODO: optimize to O(1)
                    insort(minimum.children, maximum, key=attrgetter("key"))

                    # Re-parent maximum appropriately.
                    maximum.parent = minimum

                    # Clear maximum's mark, since it can now lose another child.
                    maximum.marked = False

                    # Increase minimum's degree; it now has another child.
                    minimum.degree += 1

                    # Continue merging this tree.
                    curr = minimum
        return min_node.key, min_node.value

    def __contains__(self, __x: object) -> bool:
        nodes = self.trees[:]
        while nodes:
            node = nodes.pop()
            if node is None:
                continue
            if node.key == __x:
                return True
            nodes.extend(node.children)
        return False

    def __len__(self) -> int:
        return self.size

    @staticmethod
    def _merge(
        a_list: list[NodeL[Key, Value]], other: list[NodeL[Key, Value]]
    ) -> list[NodeL[Key, Value]]:
        a_list.extend(other)
        a_list.sort(key=attrgetter("key"), reverse=True)
        return a_list

    def _cascading_cut(self, node: NodeL[Key, Value]) -> None:
        assert node.marked

        node.marked = False
        # Base case: If the node has no parent, we're done.
        if node.parent is None:
            return None

        # if the node has siblings, splice it out
        node.parent.children.remove(node)

        # decrement the degree of the parent, since we just removed a child
        node.parent.degree -= 1

        # merge the node into the root list
        # TODO: optimize this because we are just inserting one node
        insort(self.trees, node, key=attrgetter("key"))

        if node.parent.marked:
            self._cascading_cut(node.parent)
        else:
            node.parent.marked = True

        node.parent = None
