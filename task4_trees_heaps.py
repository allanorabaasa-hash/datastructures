"""
BCS 2105 Data Structures and Algorithms - Group Coursework
Task 4: Trees and Heaps

Contents
  BinarySearchTree - insert, search, delete and the three depth-first traversals
  MinHeap          - array-based binary min-heap (push, pop, peek, replace_root)
  top_k_busiest    - keeps the k busiest locations in a min-heap of size k
  heap_sort        - in-place heap sort (max-heap) with a trace of every extraction

Run:  python task4_trees_heaps.py
"""

from campus_data import BUILDINGS


# ---------------------------------------------------------------- Task 4(a)-(c)
class TreeNode:
    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    """Keys in the left subtree are smaller and keys in the right subtree are larger.

    Building codes are strings, so they are compared alphabetically
    (for example "CAF" < "LIB" and "LEC1" < "LIB").
    """

    def __init__(self):
        self.root = None
        self.size = 0

    # -- insertion: O(h) where h is the height of the tree
    def insert(self, key, value=None):
        if self.root is None:
            self.root = TreeNode(key, value)
            self.size += 1
            return
        current = self.root
        while True:
            if key == current.key:
                current.value = value            # same key: update the record
                return
            if key < current.key:
                if current.left is None:
                    current.left = TreeNode(key, value)
                    break
                current = current.left
            else:
                if current.right is None:
                    current.right = TreeNode(key, value)
                    break
                current = current.right
        self.size += 1

    # -- search: O(h). Returns (value, number_of_key_comparisons)
    def search(self, key):
        current, comparisons = self.root, 0
        while current is not None:
            comparisons += 1
            if key == current.key:
                return current.value, comparisons
            current = current.left if key < current.key else current.right
        return None, comparisons

    def contains(self, key):
        current = self.root
        while current is not None:
            if key == current.key:
                return True
            current = current.left if key < current.key else current.right
        return False

    # -- traversals: O(n)
    def inorder(self):
        result = []

        def visit(node):
            if node is not None:
                visit(node.left)
                result.append(node.key)
                visit(node.right)

        visit(self.root)
        return result

    def preorder(self):
        result = []

        def visit(node):
            if node is not None:
                result.append(node.key)
                visit(node.left)
                visit(node.right)

        visit(self.root)
        return result

    def postorder(self):
        result = []

        def visit(node):
            if node is not None:
                visit(node.left)
                visit(node.right)
                result.append(node.key)

        visit(self.root)
        return result

    # -- deletion: O(h)
    def delete(self, key):
        """Remove key. Returns True if it was present."""
        if not self.contains(key):
            return False
        self.root = self._delete(self.root, key)
        self.size -= 1
        return True

    def _delete(self, node, key):
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:                # case 1 and 2: no child or one child
                return node.right
            if node.right is None:
                return node.left
            successor = node.right               # case 3: two children
            while successor.left is not None:    # smallest key of the right subtree
                successor = successor.left
            node.key, node.value = successor.key, successor.value
            node.right = self._delete(node.right, successor.key)
        return node

    def height(self):
        def measure(node):
            return -1 if node is None else 1 + max(measure(node.left), measure(node.right))

        return measure(self.root)

    def draw(self):
        """Text picture of the tree: one node per line, children indented under the parent."""
        lines = []

        def walk(node, prefix, tag, last):
            lines.append(prefix + ("" if tag == "" else ("└── " if last else "├── ") + tag) + node.key)
            children = [("L: ", node.left), ("R: ", node.right)]
            children = [(t, c) for t, c in children if c is not None]
            for index, (child_tag, child) in enumerate(children):
                extension = "" if tag == "" else ("    " if last else "│   ")
                walk(child, prefix + extension, child_tag, index == len(children) - 1)

        if self.root is not None:
            walk(self.root, "", "", True)
        return "\n".join(lines)


# ---------------------------------------------------------------- Task 4(d)
class MinHeap:
    """Binary min-heap stored in a list.

    For the item at index i: parent = (i - 1) // 2, left = 2i + 1, right = 2i + 2.
    The smallest item is always at index 0.
    """

    def __init__(self):
        self.items = []

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at an empty heap")
        return self.items[0]

    def push(self, item):
        """Add at the end and sift up. O(log n)."""
        self.items.append(item)
        self._sift_up(len(self.items) - 1)

    def pop(self):
        """Remove and return the smallest item. O(log n)."""
        if self.is_empty():
            raise IndexError("pop from an empty heap")
        smallest = self.items[0]
        last = self.items.pop()
        if self.items:
            self.items[0] = last
            self._sift_down(0)
        return smallest

    def replace_root(self, item):
        """Swap the smallest item for a new one and restore the heap. O(log n)."""
        smallest = self.items[0]
        self.items[0] = item
        self._sift_down(0)
        return smallest

    def _sift_up(self, index):
        while index > 0:
            parent = (index - 1) // 2
            if self.items[index] < self.items[parent]:
                self.items[index], self.items[parent] = self.items[parent], self.items[index]
                index = parent
            else:
                break

    def _sift_down(self, index):
        n = len(self.items)
        while True:
            left, right, smallest = 2 * index + 1, 2 * index + 2, index
            if left < n and self.items[left] < self.items[smallest]:
                smallest = left
            if right < n and self.items[right] < self.items[smallest]:
                smallest = right
            if smallest == index:
                break
            self.items[index], self.items[smallest] = self.items[smallest], self.items[index]
            index = smallest


def top_k_busiest(locations, k, trace=None):
    """Return the k busiest locations, busiest first.

    locations is a list of (footfall, code). A min-heap of size k is kept: its
    root is the quietest of the k best seen so far, so a new location only has
    to beat the root to get in. Time O(n log k), space O(k).
    Also returns the heap array as it stood before the final extraction.
    """
    heap = MinHeap()
    for entry in locations:
        if heap.size() < k:
            heap.push(entry)
            action = "push"
        elif entry > heap.peek():
            removed = heap.replace_root(entry)
            action = "replaces root %s" % removed[1]
        else:
            action = "rejected (not above root %d)" % heap.peek()[0]
        if trace is not None:
            trace.append((entry, action, [footfall for footfall, _ in heap.items]))
    heap_array = list(heap.items)
    ranking = []
    while not heap.is_empty():
        ranking.append(heap.pop())
    ranking.reverse()                            # ascending pops -> busiest first
    return ranking, heap_array


# ---------------------------------------------------------------- Task 4(e)
def _sift_down_max(array, index, size):
    while True:
        left, right, largest = 2 * index + 1, 2 * index + 2, index
        if left < size and array[left] > array[largest]:
            largest = left
        if right < size and array[right] > array[largest]:
            largest = right
        if largest == index:
            return
        array[index], array[largest] = array[largest], array[index]
        index = largest


def heap_sort(values, trace=None):
    """Sort into ascending order. O(n log n) time, O(1) extra space.

    Phase 1 builds a max-heap bottom-up. Phase 2 repeatedly swaps the maximum
    (index 0) with the last item of the heap, shrinks the heap by one and sifts
    the new root down. trace collects (label, array_copy, heap_size).
    """
    array = list(values)
    n = len(array)
    for index in range(n // 2 - 1, -1, -1):
        _sift_down_max(array, index, n)
        if trace is not None:
            trace.append(("heapify at index %d" % index, list(array), n))
    for end in range(n - 1, 0, -1):
        extracted = array[0]
        array[0], array[end] = array[end], array[0]
        _sift_down_max(array, 0, end)
        if trace is not None:
            trace.append(("extract %d" % extracted, list(array), end))
    return array


# ---------------------------------------------------------------- demonstration
def build_building_bst():
    tree = BinarySearchTree()
    for code, name, footfall in BUILDINGS:
        tree.insert(code, {"code": code, "name": name, "footfall": footfall})
    return tree


def demo():
    print("Task 4(a): BST of campus buildings keyed by building code")
    tree = build_building_bst()
    print("  insertion order:", [code for code, _, _ in BUILDINGS])
    print("  nodes =", tree.size, "| height =", tree.height())
    print(tree.draw())
    print()

    print("Task 4(b): traversals")
    print("  inorder  :", " ".join(tree.inorder()))
    print("  preorder :", " ".join(tree.preorder()))
    print("  postorder:", " ".join(tree.postorder()))
    print()

    print("Task 4(c): delete CAF (a node with two children)")
    tree.delete("CAF")
    print(tree.draw())
    print("  inorder after deletion:", " ".join(tree.inorder()))
    print()

    print("Task 4(d): min-heap of the top 8 busiest locations")
    trace = []
    locations = [(footfall, code) for code, _, footfall in BUILDINGS]
    ranking, heap_array = top_k_busiest(locations, 8, trace)
    for (footfall, code), action, snapshot in trace:
        print("  %-5s %5d  %-30s heap = %s" % (code, footfall, action, snapshot))
    print("  final heap array:", heap_array)
    print("  ranking (busiest first):", ranking)
    print()

    print("Task 4(e): heap sort of [45, 12, 78, 33, 22, 90, 56]")
    trace = []
    result = heap_sort([45, 12, 78, 33, 22, 90, 56], trace)
    for label, array, heap_size in trace:
        print("  %-20s heap part %-30s sorted part %s" % (label, array[:heap_size], array[heap_size:]))
    print("  sorted:", result)
    print()


if __name__ == "__main__":
    demo()
