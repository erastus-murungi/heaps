from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Container, Generic, Iterator, Protocol, Sized, TypeVar


class Comparable(Protocol):
    def __lt__(self, other: Key) -> bool:
        pass


Key = TypeVar("Key", bound=Comparable)
Value = TypeVar("Value")


NodeType = TypeVar("NodeType", bound="AbstractNode")


@dataclass(slots=True)
class AbstractNode(Generic[Key, Value, NodeType]):
    key: Key
    value: Value
    left: NodeType | None = None
    right: NodeType | None = None

    def swap_keys_and_values(self, other: AbstractNode) -> None:
        self.key, other.key = other.key, self.key
        self.value, other.value = other.value, self.value


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


class HeapMutationTrait(Generic[Key, Value], ABC):
    @abstractmethod
    def push(self, key: Key, value: Value) -> None:
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
    def pop(self) -> tuple[Key, Value]:
        """
        Pop the minimum key-value pair in the heap.

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

    @abstractmethod
    def replace(self, key: Key, value: Value) -> tuple[Key, Value]:
        """
        Pop the minimum key-value pair in the heap and push a new key-value pair
        into the heap.

        Parameters
        ----------
        key : Key
            The key of the pair.
        value : Value
            The value of the pair.

        Returns
        -------
        tuple[Key, Value]
            The minimum key-value pair in the heap.
        """
        pass


class HasNode(Generic[NodeType], ABC):
    @abstractmethod
    def _node(self, key: Key, value: Value) -> NodeType:
        pass


class Heap(
    HeapQueryTrait[Key, Value],
    HeapMutationTrait[Key, Value],
    HasNode[NodeType],
    Container[Key],
    Sized,
    ABC,
):
    def sorted(self) -> Iterator[tuple[Key, Value]]:
        while len(self) > 0:
            yield self.pop()
