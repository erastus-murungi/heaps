import pytest
from hypothesis import given
from hypothesis.strategies import integers, lists

from binary_heap import (
    BinaryHeap,
    BinaryHeapTree,
    BinaryHeapTreeP,
)


@pytest.mark.parametrize("heap_class", [BinaryHeap, BinaryHeapTreeP, BinaryHeapTree])
@given(lists(integers()))
def test_sorted(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]
