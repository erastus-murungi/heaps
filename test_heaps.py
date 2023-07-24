from random import randint

import pytest
from hypothesis import given
from hypothesis.strategies import integers, lists

from binary_heap import BinaryHeap, BinaryHeapTree, BinaryHeapTreeP
from binomial_heap import BinomialHeap
from fibonacci_heap import FibonacciHeap, FibonacciHeapArray
from leftist_heap import LeftistHeap
from pairing_heap import PairingHeap
from skew_heap import SkewHeap


@pytest.mark.parametrize(
    "heap_class",
    [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ],
)
@given(lists(integers()))
def test_sorted(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]


def test_sorted_legacy():
    heap_classes = [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ]
    keys = [randint(-100_000_000, 100_000_000) for _ in range(1_000)]
    for heap_class in heap_classes:
        heap = heap_class([(k, None) for k in keys])
        assert sorted(keys) == [key for key, _ in heap.sorted()]


@pytest.mark.parametrize(
    "heap_class",
    [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ],
)
@given(lists(integers(), min_size=1))
def test_min(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    keys.sort(reverse=True)
    while keys:
        assert keys[-1] == heap.find_min()[0]
        heap.extract_min()
        keys.pop()


@pytest.mark.parametrize(
    "heap_class",
    [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ],
)
def test_empty_heap_find_min_raises(heap_class):
    heap = heap_class()
    with pytest.raises(IndexError):
        heap.find_min()


@pytest.mark.parametrize(
    "heap_class",
    [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ],
)
@given(lists(integers()))
def test_contains(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])
    for key in keys:
        assert key in heap


@pytest.mark.parametrize(
    "heap_class",
    [
        BinaryHeap,
        BinaryHeapTreeP,
        BinaryHeapTree,
        PairingHeap,
        SkewHeap,
        LeftistHeap,
        BinomialHeap,
        FibonacciHeap,
        FibonacciHeapArray,
    ],
)
@given(lists(integers()))
def test_not_contains(heap_class, keys):
    heap = heap_class()
    for key in keys:
        assert key not in heap
