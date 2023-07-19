from min_heap import BinaryMinHeapArray
from random import randint
import pytest
from core import Heap
from typing import Type


@pytest.mark.parametrize("heap_class", [BinaryMinHeapArray])
def test_sorted(heap_class: Type[Heap]):
    n_keys = 10000
    keys = list({randint(0, 100000) for _ in range(n_keys)})
    heap = heap_class([(k, None) for k in keys]) # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]
