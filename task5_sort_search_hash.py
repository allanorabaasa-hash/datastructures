"""
BCS 2105 Data Structures and Algorithms - Group Coursework
Task 5: Sorting, Searching and Hashing
"""

import random
import time

from campus_data import BUILDINGS


# ---------------------------------------------------------------- Task 5(a)
def insertion_sort(values, trace=None):
    """Stable, in place. Best O(n) (already sorted), average and worst O(n^2)."""
    array = list(values)
    for i in range(1, len(array)):
        key = array[i]
        j = i - 1
        shifts = 0
        while j >= 0 and array[j] > key:
            array[j + 1] = array[j]              # shift the larger item right
            j -= 1
            shifts += 1
        array[j + 1] = key
        if trace is not None:
            trace.append((i, key, shifts, list(array)))
    return array


def merge_sort(values, trace=None):
    """Stable. O(n log n) in every case, O(n) extra space."""
    array = list(values)

    def merge(low, middle, high):
        left, right = array[low:middle + 1], array[middle + 1:high + 1]
        i = j = 0
        k = low
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                array[k] = left[i]
                i += 1
            else:
                array[k] = right[j]
                j += 1
            k += 1
        while i < len(left):
            array[k] = left[i]
            i += 1
            k += 1
        while j < len(right):
            array[k] = right[j]
            j += 1
            k += 1
        if trace is not None:
            trace.append((left, right, list(array[low:high + 1]), list(array)))

    def sort(low, high):
        if low < high:
            middle = (low + high) // 2
            sort(low, middle)
            sort(middle + 1, high)
            merge(low, middle, high)

    sort(0, len(array) - 1)
    return array


# ---------------------------------------------------------------- Task 5(b)
def quick_sort(values):
    """Quicksort with a random pivot (Lomuto partition), sorting a copy in place."""
    array = list(values)

    def sort(low, high):
        while low < high:
            pivot_index = random.randint(low, high)
            array[pivot_index], array[high] = array[high], array[pivot_index]
            pivot = array[high]
            boundary = low - 1
            for k in range(low, high):
                if array[k] <= pivot:
                    boundary += 1
                    array[boundary], array[k] = array[k], array[boundary]
            array[boundary + 1], array[high] = array[high], array[boundary + 1]
            split = boundary + 1
            if split - low < high - split:       # recurse on the smaller side first
                sort(low, split - 1)
                low = split + 1
            else:
                sort(split + 1, high)
                high = split - 1

    sort(0, len(array) - 1)
    return array


def timing_comparison(n=10000):
    """Time both sorts on n random room records (keyed by room code)."""
    random.seed(2105)
    records = [("RM-%05d" % random.randint(0, 99999), "Room %d" % k) for k in range(n)]
    results = {}
    for name, function in (("merge sort", merge_sort), ("quicksort", quick_sort)):
        start = time.perf_counter()
        output = function(records)
        results[name] = time.perf_counter() - start
        assert output == sorted(records)
    return results


# ---------------------------------------------------------------- Task 5(c)
def binary_search(sorted_items, target):
    """Returns (index or -1, number_of_probes). O(log n) time, O(1) space."""
    low, high, probes = 0, len(sorted_items) - 1, 0
    while low <= high:
        middle = (low + high) // 2
        probes += 1
        if sorted_items[middle] == target:
            return middle, probes
        if sorted_items[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1, probes


# ---------------------------------------------------------------- Task 5(d)
class LinearProbingHashTable:
    """Open addressing: on a collision try the next slot, wrapping round the table."""

    def __init__(self, size=11):
        self.size = size
        self.slots = [None] * size

    def hash(self, key):
        return key % self.size                   # division method

    def insert(self, key):
        """Returns (slot_used, probes, list_of_slots_examined)."""
        home = self.hash(key)
        examined = []
        for i in range(self.size):
            index = (home + i) % self.size
            examined.append(index)
            if self.slots[index] is None:
                self.slots[index] = key
                return index, i + 1, examined
        raise OverflowError("hash table is full")

    def search(self, key):
        """Returns (slot or -1, probes)."""
        home = self.hash(key)
        for i in range(self.size):
            index = (home + i) % self.size
            if self.slots[index] is None:
                return -1, i + 1
            if self.slots[index] == key:
                return index, i + 1
        return -1, self.size


# ---------------------------------------------------------------- Task 5(e)
class ChainingHashTable:
    """Separate chaining: every slot holds a list (chain) of the keys that hash there."""

    def __init__(self, size=11):
        self.size = size
        self.slots = [[] for _ in range(size)]

    def hash(self, key):
        return key % self.size

    def insert(self, key):
        """Appends to the chain. Returns (slot, position_in_chain)."""
        index = self.hash(key)
        self.slots[index].append(key)
        return index, len(self.slots[index])

    def search(self, key):
        """Returns (slot or -1, probes) where probes = keys examined in the chain."""
        index = self.hash(key)
        for position, stored in enumerate(self.slots[index], start=1):
            if stored == key:
                return index, position
        return -1, len(self.slots[index])


# ---------------------------------------------------------------- Task 5(f)
class DoubleHashingTable:
    """Open addressing where the step size comes from a second hash function."""

    def __init__(self, size=11, prime=7):
        self.size = size
        self.prime = prime
        self.slots = [None] * size

    def hash1(self, key):
        return key % self.size

    def hash2(self, key):
        return self.prime - (key % self.prime)   # always between 1 and prime

    def insert(self, key):
        home, step = self.hash1(key), self.hash2(key)
        examined = []
        for i in range(self.size):
            index = (home + i * step) % self.size
            examined.append(index)
            if self.slots[index] is None:
                self.slots[index] = key
                return index, i + 1, examined
        raise OverflowError("hash table is full")


# ---------------------------------------------------------------- used by Task 6
class RoomHashTable:
    def __init__(self, size=11):
        self.size = size
        self.slots = [[] for _ in range(size)]
        self.count = 0

    def _string_to_int(self, key):
        number = 0
        for character in key:
            number = number * 31 + ord(character)
        return number

    def hash(self, key):
        return self._string_to_int(key) % self.size

    def put(self, key, value):
        chain = self.slots[self.hash(key)]
        for position, (stored_key, _) in enumerate(chain):
            if stored_key == key:
                chain[position] = (key, value)
                return
        chain.append((key, value))
        self.count += 1
        if self.count / self.size > 0.75:
            self._resize()

    def get(self, key):
        """Returns (value or None, slot, probes)."""
        index = self.hash(key)
        for position, (stored_key, value) in enumerate(self.slots[index], start=1):
            if stored_key == key:
                return value, index, position
        return None, index, len(self.slots[index])

    def _resize(self):
        old_entries = [entry for chain in self.slots for entry in chain]
        self.size = self.size * 2 + 1
        self.slots = [[] for _ in range(self.size)]
        self.count = 0
        for key, value in old_entries:
            self.put(key, value)

    def load_factor(self):
        return self.count / self.size

    def longest_chain(self):
        return max(len(chain) for chain in self.slots)


# ---------------------------------------------------------------- demonstration
KEYS = [22, 41, 53, 46, 30, 13, 1, 67]


def demo():
    data = [12, 11, 13, 5, 6]

    print("Task 5(a): insertion sort on", data)
    trace = []
    insertion_sort(data, trace)
    for i, key, shifts, array in trace:
        print("  pass %d: key = %2d, %d shift(s) -> %s" % (i, key, shifts, array))
    print()

    print("Task 5(a): merge sort on", data)
    trace = []
    merge_sort(data, trace)
    for number, (left, right, merged, array) in enumerate(trace, start=1):
        print("  merge %d: %-9s + %-9s = %-18s array -> %s" % (number, left, right, merged, array))
    print()

    print("Task 5(b): time to sort 10,000 room records (one run on this machine)")
    for name, seconds in timing_comparison().items():
        print("  %-10s %.1f ms" % (name, seconds * 1000))
    print()

    print("Task 5(c): binary search on the sorted building codes")
    codes = merge_sort([code for code, _, _ in BUILDINGS])
    print("  sorted list:", codes)
    for target in ("ICT", "GATE", "SPT", "CHP"):
        index, probes = binary_search(codes, target)
        outcome = "found at index %d" % index if index >= 0 else "not found"
        print("  search %-5s -> %-17s (%d probes)" % (target, outcome, probes))
    print()

    print("Task 5(d): h(k) = k mod 11 with linear probing")
    linear = LinearProbingHashTable(11)
    linear_total = 0
    for key in KEYS:
        slot, probes, examined = linear.insert(key)
        linear_total += probes
        print("  insert %2d: h = %2d, slots tried %-14s -> slot %2d (%d probe%s)"
              % (key, linear.hash(key), examined, slot, probes, "" if probes == 1 else "s"))
    print("  final table:", linear.slots)
    print("  total probes =", linear_total, "| average =", linear_total / len(KEYS))
    print()

    print("Task 5(e): the same keys with separate chaining")
    chained = ChainingHashTable(11)
    for key in KEYS:
        chained.insert(key)
    for index, chain in enumerate(chained.slots):
        print("  slot %2d: %s" % (index, " -> ".join(str(k) for k in chain) if chain else "empty"))
    chain_total = sum(chained.search(key)[1] for key in KEYS)
    linear_search_total = sum(linear.search(key)[1] for key in KEYS)
    print("  probes to find each key  :", {key: chained.search(key)[1] for key in KEYS})
    print("  successful search, total : chaining %d, linear probing %d" % (chain_total, linear_search_total))
    print("  successful search, mean  : chaining %.3f, linear probing %.3f"
          % (chain_total / len(KEYS), linear_search_total / len(KEYS)))
    absent = list(range(11))                    # one unsuccessful search per home slot
    linear_miss = sum(linear.search(1000 * 11 + home)[1] for home in absent)
    chain_miss = sum(max(1, len(chain)) for chain in chained.slots)
    print("  unsuccessful search, mean over the 11 home slots: chaining %.3f, linear probing %.3f"
          % (chain_miss / 11, linear_miss / 11))
    print()

    print("Task 5(f): the same keys with double hashing, h2(k) = 7 - (k mod 7)")
    double = DoubleHashingTable(11, 7)
    double_total = 0
    for key in KEYS:
        slot, probes, examined = double.insert(key)
        double_total += probes
        print("  insert %2d: h1 = %2d, h2 = %d, slots tried %-10s -> slot %2d"
              % (key, double.hash1(key), double.hash2(key), examined, slot))
    print("  final table:", double.slots)
    print("  total probes =", double_total, "(linear probing needed %d)" % linear_total)
    print()


if __name__ == "__main__":
    demo()
