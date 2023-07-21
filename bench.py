import statistics
from collections import defaultdict
from pprint import pprint
from random import randint
from timeit import timeit
import matplotlib.pyplot as plt

from binary_heap import BinaryHeap, BinaryHeapTree, BinaryHeapTreeP
from binomial_heap import BinomialHeap
from leftist_heap import LeftistHeap
from pairing_heap import PairingHeap
from skew_heap import SkewHeap
from fibonacci_heap import FibonacciHeap, FibonacciHeapArray


def run_sort(heap_class, keys):
    heap = heap_class([(k, None) for k in keys])  # type: ignore
    assert sorted(keys) == [key for key, _ in heap.sorted()]


ALL_CLASSES = [
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


def benchmark_many_consecutive_insertions() -> None:
    times = defaultdict(list)
    for n_insertions in range(1, 2000, 500):
        keys = [randint(-100_000_000, 100_000_000) for _ in range(n_insertions)]
        for constructor in ALL_CLASSES:
            times[constructor.__name__].append(
                timeit(
                    lambda: run_sort(constructor, keys),
                    number=2,
                ),
            )
    pprint(times)
    # fig, axs = plt.subplots(len(times), 1)
    # for ax, (labels, time_series) in zip(axs, times.items()):
    #     ax.plot(time_series)
    #     ax.set_title(labels)
    # plt.show()

    for label, time_series in times.items():
        plt.plot(time_series, label=label)
    plt.legend()
    plt.xlabel('Number of insertions')
    plt.ylabel('Time (s)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    benchmark_many_consecutive_insertions()
