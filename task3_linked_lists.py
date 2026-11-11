"""
BCS 2105 Data Structures and Algorithms - Group Coursework
Task 3: Linked Lists and Variants

"""


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


# ---------------------------------------------------------------- Task 3(a)
class SinglyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def insert_at_head(self, data):
        """O(1): the new node points at the old head."""
        node = Node(data)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self.size += 1

    def insert_at_tail(self, data):
        """O(1) because a tail pointer is kept."""
        node = Node(data)
        if self.head is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def delete(self, value):
        """Remove the first node holding value. O(n). Returns True if removed."""
        previous, current = None, self.head
        while current is not None and current.data != value:
            previous, current = current, current.next
        if current is None:
            return False
        if previous is None:
            self.head = current.next
        else:
            previous.next = current.next
        if current is self.tail:
            self.tail = previous
        self.size -= 1
        return True

    def traverse(self):
        """Visit every node from head to tail. O(n). Returns the data as a list."""
        result, current = [], self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __str__(self):
        return " -> ".join(self.traverse() + ["None"])


# ---------------------------------------------------------------- Task 3(c)
def has_cycle(head):
    
    slow = fast = head
    steps = 0
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        steps += 1
        if slow is fast:
            return True, steps
    return False, steps


def find_cycle_start(head):
    """Second phase of Floyd's algorithm: locate the node where the cycle begins."""
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow
    return None


# ---------------------------------------------------------------- Task 3(e)
class CircularLinkedList:
    """The last node points back to the first, so the route never ends."""

    def __init__(self):
        self.tail = None             # tail.next is the first stop
        self.size = 0

    def append(self, data):
        node = Node(data)
        if self.tail is None:
            node.next = node
        else:
            node.next = self.tail.next
            self.tail.next = node
        self.tail = node
        self.size += 1

    def find(self, value):
        if self.tail is None:
            return None
        current = self.tail.next
        for _ in range(self.size):
            if current.data == value:
                return current
            current = current.next
        return None

    def traverse_from(self, start, laps=1):
        """One or more full laps of the route beginning at any stop."""
        node = self.find(start)
        if node is None:
            raise ValueError("unknown stop: %s" % start)
        route = []
        for _ in range(self.size * laps):
            route.append(node.data)
            node = node.next
        route.append(node.data)      # back where the lap started
        return route

    def next_stop(self, stop):
        node = self.find(stop)
        return None if node is None else node.next.data


SHUTTLE_STOPS = ["Main Gate", "Hostel 1", "Hostel 2", "Hostel 3", "Town Centre"]


def demo():
    print("Task 3(a): singly linked list of shuttle stops")
    stops = SinglyLinkedList()
    for stop in ["Hostel 1", "Hostel 2", "Hostel 3"]:
        stops.insert_at_tail(stop)
    print("  3 x insert_at_tail :", stops)
    stops.insert_at_head("Main Gate")
    print("  insert_at_head     :", stops)
    stops.insert_at_tail("Town Centre")
    print("  insert_at_tail     :", stops)
    stops.delete("Hostel 2")
    print("  delete('Hostel 2') :", stops)
    print("  delete('Chapel')   :", stops.delete("Chapel"), "(not in the list, nothing removed)")
    print("  traverse()         :", stops.traverse(), "| size =", stops.size)
    print()

    print("Task 3(c): Floyd's cycle detection")
    acyclic = SinglyLinkedList()
    for stop in SHUTTLE_STOPS:
        acyclic.insert_at_tail(stop)
    found, steps = has_cycle(acyclic.head)
    print("  acyclic:", acyclic)
    print("  has_cycle ->", found, "after", steps, "steps (fast pointer reached the end)")

    cyclic = SinglyLinkedList()
    for stop in SHUTTLE_STOPS:
        cyclic.insert_at_tail(stop)
    cyclic.tail.next = cyclic.head.next          # Town Centre -> Hostel 1
    found, steps = has_cycle(cyclic.head)
    print("  cyclic : Main Gate -> Hostel 1 -> Hostel 2 -> Hostel 3 -> Town Centre -> (Hostel 1 again)")
    print("  has_cycle ->", found, "after", steps, "steps; the cycle starts at", find_cycle_start(cyclic.head).data)
    print()

    print("Task 3(e): circular linked list for the continuous shuttle route")
    route = CircularLinkedList()
    for stop in SHUTTLE_STOPS:
        route.append(stop)
    print("  one full lap starting from Main Gate, from Hostel 2 and from Town Centre:")
    for start in ("Main Gate", "Hostel 2", "Town Centre"):
        print("    " + " -> ".join(route.traverse_from(start)))
    print("  next stop after Town Centre :", route.next_stop("Town Centre"))
    print()


if __name__ == "__main__":
    demo()
