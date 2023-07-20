from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from heapq import heapify, heappop, heappush, heapreplace
from typing import Optional

from core import Heap, Key, Value, AbstractNode, HasNode, NodeType


class BinaryHeap(Heap[Key, Value]):
    items: list[tuple[Key, Value]]

    def __init__(self, items: Optional[list[tuple[Key, Value]]] = None) -> None:
        self.items = items if items else []
        heapify(self.items)

    def find_min(self) -> tuple[Key, Value]:
        return self.items[0]

    def push(self, key: Key, value: Value) -> None:
        heappush(self.items, (key, value))

    def pop(self) -> tuple[Key, Value]:
        return heappop(self.items)

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        return heapreplace(self.items, (key, value))

    def __contains__(self, __x: object) -> bool:
        return any(key == __x for key, _ in self.items)

    def __len__(self) -> int:
        return len(self.items)


class Node(AbstractNode[Key, Value, "Node[Key, Value]"]):
    left: Node[Key, Value] | None = None
    right: Node[Key, Value] | None = None


@dataclass(slots=True)
class NodeP(AbstractNode[Key, Value, "NodeP[Key, Value]"]):
    left: NodeP[Key, Value] | None = None
    right: NodeP[Key, Value] | None = None
    parent: NodeP[Key, Value] | None = None


class HeapTree(Heap[Key, Value], HasNode[Key, Value, NodeType], ABC):
    root: Optional[NodeType]
    size: int

    def __init__(self, items: Optional[list[tuple[Key, Value]]] = None) -> None:
        self.root = None
        self.size = 0
        for key, value in items or []:
            self.push(key, value)

    def find_min(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        return self.root.key, self.root.value

    def push(self, key: Key, value: Value) -> None:
        self._push_node(self._node(key, value))
        self.size += 1

    @abstractmethod
    def _push_node(self, node: NodeType):
        pass

    @abstractmethod
    def decrease_key(self, node: NodeType, new_key: Key) -> None:
        pass

    def __len__(self):
        return self.size


class BinaryHeapTreeAbstract(HeapTree[Key, Value], ABC):
    def __contains__(self, __x: object) -> bool:
        if self.root is None:
            return False
        else:
            nodes: list[NodeType] = [self.root]
            while nodes:
                current = nodes.pop()
                if current.key == __x:
                    return True
                if current.left is not None:
                    nodes.append(current.left)
                if current.right is not None:
                    nodes.append(current.right)
            return False

    @staticmethod
    def _bubble_down(node: NodeType) -> None:
        while (
            node.left is not None
            and node.key > node.left.key
            or node.right is not None
            and node.key > node.right.key
        ):
            if node.right is None or node.left.key < node.right.key:  # type: ignore
                node.swap_keys_and_values(node.left)  # type: ignore
                node = node.left  # type: ignore
            else:
                node.swap_keys_and_values(node.right)
                node = node.right

    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        if self.root is not None:
            root = self.root
            key_value = root.key, root.value
            root.key, root.value = key, value
            self._bubble_down(root)
            return key_value
        raise IndexError("Empty heap")

    def decrease_key(self, node: NodeType, new_key: Key) -> None:
        node.key = new_key
        self._bubble_down(node)


class BinaryHeapTree(BinaryHeapTreeAbstract[Key, Value, Node[Key, Value]]):
    def _get_leftmost_leaf_path(self) -> list[Node[Key, Value]]:
        assert self.root is not None
        current = self.root
        path = [current]
        while current.left is not None:
            current = current.left
            path.append(current)
        return path

    def _push_node(self, node: Node[Key, Value]):
        if self.root is None:
            self.root = node
        else:
            path = self._get_leftmost_leaf_path()
            current = path[-1]
            current.left = node
            while path:
                parent = path.pop()
                if parent.key > node.key:
                    node.swap_keys_and_values(parent)
                    node = parent
                else:
                    break

    def _remove_leaf_no_parent(self, path: list[Node[Key, Value]]):
        node = path.pop()
        if path:
            parent = path[-1]
            if parent.left is node:
                parent.left = None
            else:
                parent.right = None
        else:
            self.root = None

    def pop(self) -> tuple[Key, Value]:
        if self.root is not None:
            path = self._get_leftmost_leaf_path()
            leaf = path[-1]
            root = self.root
            key_value = root.key, root.value
            self._remove_leaf_no_parent(path)
            if leaf is not root:
                root.swap_keys_and_values(leaf)
                self._bubble_down(root)
            self.size -= 1
            return key_value
        raise IndexError("Empty heap")

    def _node(self, key: Key, value: Value) -> Node[Key, Value]:
        return Node(key, value)


class BinaryHeapTreeP(BinaryHeapTreeAbstract[Key, Value, NodeP[Key, Value]]):
    def _get_leftmost_leaf(self) -> NodeP[Key, Value]:
        assert self.root is not None
        current = self.root
        while current.left is not None:
            current = current.left
        return current

    @staticmethod
    def _bubble_up(node: NodeP[Key, Value]) -> None:
        while node.parent is not None and node.parent.key > node.key:
            node.swap_keys_and_values(node.parent)
            node = node.parent

    def _push_node(self, node: NodeP[Key, Value]):
        if self.root is None:
            self.root = node
        else:
            # Add the element to the bottom level of the heap at the leftmost open space.
            current = self._get_leftmost_leaf()
            current.left = node
            node.parent = current
            # bubble up
            self._bubble_up(node)

    def remove_leaf(self, leaf: NodeP[Key, Value]):
        if leaf.parent is not None:
            if leaf.parent.left == leaf:
                leaf.parent.left = None
            else:
                leaf.parent.right = None
        else:
            self.root = None

    def pop(self) -> tuple[Key, Value]:
        if self.root is not None:
            leaf = self._get_leftmost_leaf()
            root = self.root
            key_value = root.key, root.value
            self.remove_leaf(leaf)
            if leaf is not root:
                root.swap_keys_and_values(leaf)
                self._bubble_down(root)
            self.size -= 1
            return key_value
        raise KeyError("Empty heap")

    def _node(self, key: Key, value: Value) -> NodeP[Key, Value]:
        return NodeP(key, value)
