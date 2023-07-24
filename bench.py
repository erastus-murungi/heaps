from collections import defaultdict
from pprint import pprint
from random import randint
from timeit import timeit

import matplotlib.pyplot as plt  # type: ignore
from matplotlib import rcParams  # type: ignore

from binary_heap import BinaryHeap, BinaryHeapTree, BinaryHeapTreeP
from binomial_heap import BinomialHeap
from fibonacci_heap import FibonacciHeap, FibonacciHeapArray
from leftist_heap import LeftistHeap
from pairing_heap import PairingHeap
from skew_heap import SkewHeap

rcParams.update({"font.size": 8})


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

    for label, time_series in times.items():
        plt.plot(time_series, label=label)
    plt.legend()
    plt.xlabel("Number of insertions")
    plt.ylabel("Time (s)")
    plt.grid(True)
    plt.show()


def benchmark_many_consecutive_insertions_bars() -> None:
    times = []
    insertions_range = list(range(1, 2000, 500))
    for n_insertions in insertions_range:
        keys = [randint(-100_000_000, 100_000_000) for _ in range(n_insertions)]
        y_time = []
        for constructor in ALL_CLASSES:
            y_time.append(
                timeit(
                    lambda: run_sort(constructor, keys),
                    number=2,
                ),
            )
        times.append(y_time)
    labels = [constructor.__name__ for constructor in ALL_CLASSES]
    y_pos = list(range(len(labels)))
    fig, axs = plt.subplots(len(times), 1)
    for ax, time_series, n_insertions in zip(axs, times, insertions_range):
        ax.bar(y_pos, time_series)
        ax.set_xticks(y_pos, labels)
        ax.set_title(f"{n_insertions} insertions")
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    benchmark_many_consecutive_insertions_bars()
