from __future__ import annotations
from typing import Optional, Protocol, TypeVar, Generic, Container, Sized, Iterator
from abc import ABC, abstractmethod


class Comparable(Protocol):
    def __lt__(self, other: Key) -> bool:
        pass


Key = TypeVar("Key", bound=Comparable)
Value = TypeVar("Value")


class HeapQueryTrait(Generic[Key, Value], ABC):
    @abstractmethod
    def find_min(self) -> Optional[tuple[Key, Value]]:
        """
        Find the minimum key-value pair in the heap.

        Returns
        -------
        Optional[tuple[Key, Value]]
            The minimum key-value pair in the heap.
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
    def replace(self, key: Key, value: Value) -> Optional[tuple[Key, Value]]:
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
        Optional[tuple[Key, Value]]
            The minimum key-value pair in the heap.
        """
        pass


class Heap(
    HeapQueryTrait[Key, Value],
    HeapMutationTrait[Key, Value],
    Container[Key],
    Sized,
    ABC,
):
    def sorted(self) -> Iterator[tuple[Key, Value]]:
        while len(self) > 0:
            yield self.pop()
