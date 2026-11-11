"""
BCS 2105 Data Structures and Algorithms - Group Coursework
Task 2: Linear Data Structures - Stacks and Queues

"""


# ---------------------------------------------------------------- Task 2(a)

class NavigationStack:
    """Stack storing the last 10 buildings visited (LIFO)."""

    def __init__(self, capacity=10):
        self.capacity = capacity
        self.items = []              # top of stack = end of list

    def is_empty(self):
        return len(self.items) == 0

    def push(self, building):
        if len(self.items) == self.capacity:
            self.items.pop(0)        # remove oldest visit (bottom)
        self.items.append(building)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack underflow: no history")
        return self.items.pop()      # remove most recent visit

    def peek(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]        # view most recent, no removal

    def size(self):
        return len(self.items)


# Demonstration
history = NavigationStack()
for b in ["Library", "Admin Block", "Labs", "Block B"]:
    history.push(b)

print(history.peek())      # Block B
print(history.pop())       # Block B  (user presses "Back")
print(history.peek())      # Labs
print(history.is_empty())  # False

# ---------------------------------------------------------------- Task 2(b)
class ShuttleQueue:
    """FIFO queue of shuttles waiting at the main gate."""

    class _Node:
        def __init__(self, data):
            self.data = data
            self.next = None

    def __init__(self):
        self.head = None   # front
        self.tail = None   # rear
        self._size = 0

    def is_empty(self):
        return self.head is None

    def enqueue(self, shuttle):
        node = self._Node(shuttle)
        if self.is_empty():
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue underflow: no shuttles scheduled")
        data = self.head.data
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return data

    def front(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.head.data


# Demonstration
q = ShuttleQueue()
q.enqueue("Shuttle 1 - 08:00")
q.enqueue("Shuttle 2 - 08:15")
q.enqueue("Shuttle 3 - 08:30")

print(q.front())     # Shuttle 1 - 08:00
print(q.dequeue())   # Shuttle 1 - 08:00 departs
print(q.front())     # Shuttle 2 - 08:15