from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from typing import Container, Generic, Iterator, Optional, Protocol, Sized, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: Key) -> bool:
        pass

    def __le__(self, other: Key) -> bool:
        pass


Key = TypeVar("Key", bound=Comparable)
Value = TypeVar("Value")
NodeType = TypeVar("NodeType", bound="AbstractNode")


class PrettyStrMixin(ABC):
    @abstractmethod
    def pretty_str(self) -> str:
        pass


class PrettyLineYieldMixin(ABC):
    @abstractmethod
    def yield_line(self, indent: str, prefix: str) -> Iterator[str]:
        pass


@dataclass(slots=True)
class AbstractNode(
    Generic[Key, Value, NodeType], PrettyStrMixin, PrettyLineYieldMixin, ABC
):
    key: Key
    value: Value

    def swap_keys_and_values(self, other: AbstractNode) -> None:
        self.key, other.key = other.key, self.key
        self.value, other.value = other.value, self.value

    def pretty_str(self) -> str:
        return "".join(self.yield_line("", "R"))

    @abstractmethod
    def children(self) -> Iterator[NodeType]:
        pass


class HasNode(Generic[Key, Value, NodeType], ABC):
    @abstractmethod
    def _node(self, key: Key, value: Value) -> NodeType:
        pass


class HeapQueryTrait(Generic[Key, Value], ABC):
    @abstractmethod
    def find_min(self) -> tuple[Key, Value]:
        """
        Find the minimum key-value pair in the heap.

        Returns
        -------
        tuple[Key, Value]
            The minimum key-value pair in the heap.

        Raises
        ------
        IndexError
            If the heap is empty.
        """
        pass


T = TypeVar("T")


class HeapMutationTrait(Generic[Key, Value, T], ABC):
    @abstractmethod
    def enqueue(self, key: Key, value: Value) -> T:
        """
        Push a key-value pair into the heap.

        Parameters
        ----------
        key : Key
            The key of the pair.
        value : Value
            The value of the pair.
        """
        pass

    @abstractmethod
    def extract_min(self) -> tuple[Key, Value]:
        """
        Extract the minimum key-value pair in the heap.

        Returns
        -------
        tuple[Key, Value]
            The minimum key-value pair in the heap.

        Raises
        ------
        IndexError
            If the heap is empty.
        """
        pass


class Heap(
    HeapQueryTrait[Key, Value],
    HeapMutationTrait[Key, Value, T],
    Container[Key],
    Sized,
    ABC,
):
    def sorted(self) -> Iterator[tuple[Key, Value]]:
        while len(self) > 0:
            yield self.extract_min()


class HeapTree(
    Heap[Key, Value, NodeType], HasNode[Key, Value, NodeType], PrettyStrMixin
):
    def __init__(self, items: Optional[list[tuple[Key, Value]]] = None) -> None:
        self.root: Optional[NodeType] = None
        self.size: int = 0
        for key, value in items or []:
            self.enqueue(key, value)

    def find_min(self) -> tuple[Key, Value]:
        if self.root is None:
            raise IndexError("Empty heap")
        return self.root.key, self.root.value

    def enqueue(self, key: Key, value: Value) -> NodeType:
        node = self._node(key, value)
        self._push_node(node)
        self.size += 1
        return node

    def _push_node(self, node: NodeType) -> None:
        if self.root is None:
            self.root = node if self.root is None else self._push_node_non_empty(node)
        else:
            self.root = self._push_node_non_empty(node)

    @abstractmethod
    def _push_node_non_empty(self, node: NodeType) -> NodeType:
        ...

    def __len__(self):
        return self.size

    def pretty_str(self) -> str:
        if self.root is not None:
            return "".join(self.root.yield_line("", "R"))
        else:
            return "Nothing"

    def __contains__(self, __x: object) -> bool:
        if self.root is None:
            return False
        else:
            nodes: list[NodeType] = [self.root]
            while nodes:
                current = nodes.pop()
                if current.key == __x:
                    return True
                nodes.extend(current.children())
            return False


class SelfAdjustingHeap(HeapTree[Key, Value, NodeType], ABC):
    def _push_node_non_empty(self, node: NodeType) -> None:
        return self._merge(self.root, node)

    def extract_min(self) -> tuple[Key, Value]:
        if self.root is not None:
            key_value = self.root.key, self.root.value
            self.root = reduce(self._merge, self.root.children(), None)
            self.size -= 1
            return key_value
        raise IndexError("Empty heap")

    def _merge(
        self, heap1: Optional[NodeType], heap2: Optional[NodeType]
    ) -> Optional[NodeType]:
        pass
