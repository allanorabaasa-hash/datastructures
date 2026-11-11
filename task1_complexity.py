"""
BCS 2105 Data Structures and Algorithms 
Task 1: Algorithm Analysis and Complexity
"""

import sys

BUILDINGS = [
    "Main Gate", "Administration Block", "Main Library", "Library Annex",
    "Lecture Theatre 1", "Lecture Theatre 2", "Science Block", "ICT Laboratory Block",
    "Cafeteria", "Hostel 1", "Hostel 2", "Sports Complex",
]


# ---------------------------------------------------------------- Task 1(a)
def access_by_index(items, index):
    """One address calculation, whatever the size of the list: O(1)."""
    return items[index]


def linear_search_by_name(items, name):
    """Scan from the left. Returns (position, number_of_comparisons)."""
    comparisons = 0
    for position, item in enumerate(items):
        comparisons += 1
        if item == name:
            return position, comparisons
    return -1, comparisons


def part_a():
    print("Task 1(a): operation counts on the list of 12 buildings")
    print("  Access by index 7       ->", access_by_index(BUILDINGS, 7), "(1 step)")

    copy = list(BUILDINGS)
    copy.append("New Building")              # insertion at the end: amortised O(1)
    print("  Append at the end       -> list now has", len(copy), "items (0 items shifted)")
    copy.insert(0, "Another Building")       # insertion at the front: O(n) shifts
    print("  Insert at position 0    ->", len(copy) - 1, "items shifted one place right")

    for name in ("Main Gate", "Cafeteria", "Sports Complex", "Chapel"):
        position, comparisons = linear_search_by_name(BUILDINGS, name)
        result = "found at index %d" % position if position >= 0 else "not found"
        print("  Linear search %-16s -> %-18s after %2d comparisons" % (repr(name), result, comparisons))
    print()


# ---------------------------------------------------------------- Task 1(c)
def count_equal_pairs(A):
    """The pseudocode of Task 1(c). Returns (count, comparisons_made)."""
    n = len(A)
    count = 0
    comparisons = 0
    for i in range(n):
        for j in range(n):
            comparisons += 1
            if A[i] == A[j]:
                count += 1
    return count, comparisons


def part_c():
    print("Task 1(c): nested loop, worst case is an array of identical values")
    print("  %6s %14s %12s %10s" % ("n", "comparisons", "n squared", "count"))
    for n in (1, 2, 4, 8, 16, 32, 64):
        count, comparisons = count_equal_pairs([7] * n)
        print("  %6d %14d %12d %10d" % (n, comparisons, n * n, count))
    print("  Doubling n multiplies the work by 4, which is the signature of O(n^2).")
    print()


# ---------------------------------------------------------------- Task 1(e)
class DynamicArray:
    """A growable array that doubles its capacity when it is full.

    It counts every element write so that the amortised cost can be measured.
    """

    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.slots = [None] * self.capacity
        self.copies = 0          # elements moved during all resizes so far
        self.writes = 0          # elements written by append itself

    def append(self, value):
        """Returns the actual cost of this append (1 write + any copies)."""
        cost = 0
        if self.size == self.capacity:
            new_slots = [None] * (2 * self.capacity)
            for k in range(self.size):
                new_slots[k] = self.slots[k]
            self.copies += self.size
            cost += self.size
            self.slots = new_slots
            self.capacity *= 2
        self.slots[self.size] = value
        self.size += 1
        self.writes += 1
        return cost + 1


def part_e():
    print("Task 1(e): amortised cost of append in a doubling dynamic array")
    array = DynamicArray()
    print("  %4s %-22s %9s %6s %10s %12s" % ("i", "building appended", "capacity", "cost", "total", "total / i"))
    total = 0
    for i, name in enumerate(BUILDINGS, start=1):
        cost = array.append(name)
        total += cost
        print("  %4d %-22s %9d %6d %10d %12.2f" % (i, name, array.capacity, cost, total, total / i))
    print("  Total cost of 12 appends = %d, which is below the bound 3n = %d." % (total, 3 * len(BUILDINGS)))

    print("  Larger runs (total cost / n never reaches 3):")
    for n in (100, 1000, 10000, 100000):
        array = DynamicArray()
        total = sum(array.append(k) for k in range(n))
        print("    n = %6d   total cost = %7d   cost per append = %.3f" % (n, total, total / n))

    print("  Python's built-in list also grows geometrically (bytes allocated as items are appended):")
    items, last = [], None
    for k in range(18):
        size = sys.getsizeof(items)
        if size != last:
            print("    length %2d -> %3d bytes" % (len(items), size))
            last = size
        items.append(k)
    print()


if __name__ == "__main__":
    part_e()
