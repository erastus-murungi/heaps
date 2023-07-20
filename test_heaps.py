import pytest
from hypothesis import given
from hypothesis.strategies import integers, lists

from binary_heap import BinaryHeap, BinaryHeapTree, BinaryHeapTreeP
from leftist_heap import LeftistHeap
from pairing_heap import PairingHeap
from skew_heap import SkewHeap


@pytest.mark.parametrize(
    "heap_class",
    [BinaryHeap, BinaryHeapTreeP, BinaryHeapTree, PairingHeap, SkewHeap, LeftistHeap],
)
@given(lists(integers()))
def test_sorted(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]


@pytest.mark.parametrize(
    "heap_class",
    [BinaryHeap, BinaryHeapTreeP, BinaryHeapTree, PairingHeap, SkewHeap, LeftistHeap],
)
@given(lists(integers(), min_size=1))
def test_min(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    keys.sort(reverse=True)
    while keys:
        assert keys[-1] == heap.find_min()[0]
        heap.pop()
        keys.pop()


@pytest.mark.parametrize(
    "heap_class",
    [BinaryHeap, BinaryHeapTreeP, BinaryHeapTree, PairingHeap, SkewHeap, LeftistHeap],
)
def test_empty_heap_find_min_raises(heap_class):
    heap = heap_class()
    with pytest.raises(IndexError):
        heap.find_min()
