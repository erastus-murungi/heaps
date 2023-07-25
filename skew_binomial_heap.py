from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from operator import attrgetter
from typing import Optional, Iterator

from binomial_heap import BinomialHeapAbstract as BinomialHeap
from binomial_heap import NodeAbstract as BinomialNode
from core import Key, Value


def is_sorted(lst):
    return all(a >= b for a, b in zip(lst, lst[1:]))


@dataclass(slots=True)
class Node(BinomialNode[Key, Value, "Node[Key, Value]"]):
    order: int = 0

    def link(self, other: Node[Key, Value]) -> Node[Key, Value]:
        root = super(Node, self).link(other)
        root.order += 1
        return root

    def skew_link(
        self, other: Node[Key, Value], singleton: Optional[Node[Key, Value]]
    ) -> Node[Key, Value]:
        assert self.order == other.order
        if singleton is not None:
            if singleton.key < self.key and singleton.key < other.key:
                # type A skew link
                singleton.child = self
                self.sibling = other
                singleton.order = self.order + 1
                return singleton
            else:
                # type B skew link
                root = self.link(other)
                singleton.sibling = root.child
                root.child = singleton
                return root
        else:
            # simple link
            return self.link(other)


@dataclass(slots=True, init=False)
class SkewBinomialHeap(BinomialHeap[Key, Value, Node[Key, Value]]):
    forest: list[Node[Key, Value]]  # type: ignore
    size: int

    def _insert_singleton(self, node: Node[Key, Value]) -> None:
        if len(self.forest) >= 2 and self.forest[-2].order == self.forest[-1].order:
            first, second = self.forest.pop(), self.forest.pop()
            self.forest.append(first.skew_link(second, node))
        else:
            self.forest.append(node)

    @staticmethod
    def _merge_by_order(
        roots: list[Node[Key, Value]], other: list[Node[Key, Value]]
    ) -> Iterator[tuple[Optional[Node[Key, Value]], Optional[Node[Key, Value]]]]:
        order = 0
        i, j = len(roots) - 1, len(other) - 1
        if roots and other:
            max_order = max(roots[0].order, other[0].order)
            while order <= max_order:
                if (i >= 0 and roots[i].order == order) and (
                    j >= 0 and other[j].order == order
                ):
                    yield roots[i], other[j]
                    i -= 1
                    j -= 1
                elif i >= 0 and roots[i].order == order:
                    yield roots[i], None
                    i -= 1
                elif j >= 0 and other[j].order == order:
                    yield None, other[j]
                    j -= 1
                else:
                    yield None, None
                order += 1
                if i < 0 and j < 0:
                    break
        elif roots:
            max_order = roots[0].order
            while i >= 0 and order <= max_order:
                if roots[i].order == order:
                    yield roots[i], None
                    i -= 1
                else:
                    yield None, None
                order += 1
        elif other:
            max_order = other[0].order
            while j >= 0 and order <= max_order:
                if other[j].order == order:
                    yield None, other[j]
                    j -= 1
                else:
                    yield None, None
                order += 1

    @staticmethod
    def _normalize(*forests: list[Node[Key, Value]]) -> None:
        for forest in forests:
            while len(forest) >= 2 and forest[-2].order == forest[-1].order:
                first, second = forest.pop(), forest.pop()
                forest.append(first.link(second))

    @staticmethod
    def _extract_singletons(*forests: list[Node[Key, Value]]) -> list[Node[Key, Value]]:
        singletons = []
        for forest in forests:
            while forest and forest[-1].order == 0:
                singletons.append(forest.pop())
        return singletons

    def _get_min_node_index(self) -> int:
        if self.forest:
            min_node_index = 0
            for i in range(1, len(self.forest)):
                if self.forest[i].key < self.forest[min_node_index].key:
                    min_node_index = i
            return min_node_index
        raise IndexError("Heap is empty.")

    def _insert_singletons(self, singletons: list[Node[Key, Value]]) -> None:
        for singleton in singletons:
            self._insert_singleton(singleton)

    def extract_min(self) -> tuple[Key, Value]:
        if self.forest:
            min_node_index = self._get_min_node_index()
            min_node = self.forest[min_node_index]
            # fracture the packet
            fractures: list[Node[Key, Value]] = min_node.fracture_node()
            self.forest.pop(min_node_index)

            # ensure that the fractures are in monotonically increasing order
            fractures.sort(key=attrgetter("order"), reverse=True)

            singletons = self._extract_singletons(self.forest, fractures)
            self._normalize(self.forest, fractures)

            result: list[Node[Key, Value]] = []
            carry: Node[Key, Value] | None = None

            for top, low in self._merge_by_order(self.forest, fractures):
                t, carry = self._one_bit_full_adder(top, low, carry)
                if t is not None:
                    result.append(t)

            # Finally, if the carry is set, append it to the result.
            if carry is not None:
                result.append(carry)
            result.reverse()
            self.forest = result
            self._insert_singletons(singletons)
            self.size -= 1
            return min_node.key, min_node.value
        raise IndexError("Heap is empty.")

    def enqueue(self, key: Key, value: Value) -> Node[Key, Value]:
        node = Node(key, value)
        self._insert_singleton(node)
        self.size += 1
        return node

    def __len__(self) -> int:
        return self.size

    def pretty_str(self) -> str:
        indent = ""
        return "".join(
            chain.from_iterable(
                tree.yield_line(indent, f"T{index}")
                for index, tree in enumerate(self.forest)
                if tree is not None
            )
        )

    def validate(self):
        assert is_sorted([tree.order for tree in self.forest])
        # no forest have the same rank except for at most one pair
        if len(self.forest) <= 1:
            return
        if len(self) > 2:
            assert (
                len(set(tree.order for tree in self.forest[:-2])) == len(self.forest) - 2
            )

    def _node(self, key: Key, value: Value) -> Node[Key, Value]:
        return Node(key, value)
