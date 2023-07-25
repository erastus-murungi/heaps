from __future__ import annotations

from dataclasses import dataclass
from itertools import chain, zip_longest
from operator import attrgetter
from typing import Optional, Iterator

from binomial_heap import Node as BinomialNode, BinomialHeap
from core import (
    Key,
    Value,
)


def is_sorted(lst):
    return all(a >= b for a, b in zip(lst, lst[1:]))


@dataclass(slots=True)
class Node(BinomialNode[Key, Value]):
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


def iter_with_rank(trees1: list[Node[Key, Value]], trees2: list[Node[Key, Value]]):
    order = 0
    index1, index2 = 0, 0
    if trees1 and trees2:
        max_order = max(trees1[0].order, trees2[0].order)
        trees1.reverse()
        trees2.reverse()
        while order <= max_order:
            if (index1 < len(trees1) and trees1[index1].order == order) and (
                index2 < len(trees2) and trees2[index2].order == order
            ):
                yield trees1[index1], trees2[index2]
                index1 += 1
                index2 += 1
            elif index1 < len(trees1) and trees1[index1].order == order:
                yield trees1[index1], None
                index1 += 1
            elif index2 < len(trees2) and trees2[index2].order == order:
                yield None, trees2[index2]
                index2 += 1
            else:
                yield None, None
            order += 1
            if index1 >= len(trees1) and index2 >= len(trees2):
                break
    elif trees1:
        max_order = trees1[0].order
        trees1.reverse()
        while index1 < len(trees1) and order <= max_order:
            if trees1[index1].order == order:
                yield trees1[index1], None
                index1 += 1
            else:
                yield None, None
            order += 1
    elif trees2:
        max_order = trees2[0].order
        trees2.reverse()
        while index2 < len(trees2) and order <= max_order:
            if trees2[index2].order == order:
                yield None, trees2[index2]
                index2 += 1
            else:
                yield None, None
            order += 1


@dataclass(slots=True, init=False)
class SkewBinomialHeap(BinomialHeap[Key, Value]):
    def _insert_singleton(self, node: Node[Key, Value]) -> None:
        if len(self.trees) >= 2 and self.trees[-2].order == self.trees[-1].order:
            first, second = self.trees.pop(), self.trees.pop()
            self.trees.append(first.skew_link(second, node))
        else:
            self.trees.append(node)

    def extract_min(self) -> tuple[Key, Value]:
        if not self.trees:
            raise IndexError("Heap is empty.")

        min_node = min(filter(None, self.trees), key=attrgetter("key"))
        min_node_index = self.trees.index(min_node)

        # fracture the packet
        fractures: list[Node[Key, Value]] = []
        current_child = min_node.child

        while current_child is not None:
            fractures.append(current_child)
            nxt_child = current_child.sibling
            current_child.sibling = None
            current_child = nxt_child

        self.trees.pop(min_node_index)

        # remove any trailing None values
        while self.trees and self.trees[-1] is None:
            raise ValueError("None value in root list")

        # ensure that the fractures are in monotonically increasing order
        fractures.reverse()
        fractures.sort(key=attrgetter("order"), reverse=True)
        list1 = self.trees
        list2 = fractures
        # normalize
        singletons1 = [tree for tree in list1 if tree.order == 0]
        list1 = [tree for tree in list1 if tree.order != 0]
        while len(list1) >= 2 and list1[-2].order == list1[-1].order:
            first, second = list1.pop(), list1.pop()
            list1.append(first.link(second))

        # normalize
        singletons2 = [tree for tree in list2 if tree.order == 0]
        list2 = [tree for tree in list2 if tree.order != 0]
        while len(list2) >= 2 and list2[-2].order == list2[-1].order:
            first, second = list2.pop(), list2.pop()
            list2.append(first.link(second))

        assert len(set(map(attrgetter("order"), list1))) == len(list1)
        assert len(set(map(attrgetter("order"), list2))) == len(list2)

        assert is_sorted([tree.order for tree in list1])
        assert is_sorted([tree.order for tree in list2])

        result: list[Node[Key, Value]] = []
        carry: Node[Key, Value] | None = None

        for top, low in iter_with_rank(list1, list2):
            # print(top, low, carry)
            t, carry = SkewBinomialHeap._one_bit_full_adder(top, low, carry)
            if t is not None:
                result.append(t)

        # Finally, if the carry is set, append it to the result.
        if carry is not None:
            result.append(carry)
        result.reverse()
        self.trees = result
        for s in singletons1:
            self._insert_singleton(s)
        for s in singletons2:
            self._insert_singleton(s)
        self.size -= 1
        # print(heap.pretty_str())
        return min_node.key, min_node.value

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
                for index, tree in enumerate(self.trees)
            )
        )

    def validate(self):
        assert is_sorted([tree.order for tree in self.trees])
        # no trees have the same rank except for at most one pair
        if len(self.trees) <= 1:
            return
        if len(self) > 2:
            assert (
                len(set(tree.order for tree in self.trees[:-2])) == len(self.trees) - 2
            )


if __name__ == "__main__":
    from random import randint, seed
    from math import log2

    seed(0)
    for _ in range(10000):
        keys = [randint(0, 1000000) for _ in range(100)]
        #     print(len(keys))
        # print(keys)
        heap = SkewBinomialHeap([(key, key) for key in keys])
        # print(heap.pretty_str())
        # print(heap.find_min())
        assert heap.find_min()[0] == min(keys)
        assert sorted(keys) == [key for key, _ in heap.sorted()]
        # print(log2(len(keys)), len(heap.trees))
        # print([tree.order for tree in heap.trees])
        heap.validate()
