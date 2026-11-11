"""
BCS 2105 Data Structures and Algorithms - Group Coursework
Task 6: Graph Algorithms and the Integrated System

Campus Navigation and Resource Management System (working prototype).
"""

import sys

from campus_data import BUILDINGS, PATHWAYS, ROOMS, SHUTTLE_STOPS
from task2_stack_queue import NavigationHistory, Queue, Stack
from task3_linked_lists import CircularLinkedList
from task4_trees_heaps import BinarySearchTree, MinHeap, top_k_busiest
from task5_sort_search_hash import RoomHashTable, merge_sort

INFINITY = float("inf")


# ================================================================ Task 6(a)
class Graph:
 
    def __init__(self):
        self.adjacency = {}
        self.edge_count = 0

    def add_vertex(self, vertex):
        if vertex not in self.adjacency:
            self.adjacency[vertex] = []

    def add_edge(self, u, v, minutes):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adjacency[u].append((v, minutes))
        self.adjacency[v].append((u, minutes))   # undirected: store both directions
        self.edge_count += 1

    def vertices(self):
        return merge_sort(list(self.adjacency))

    def neighbours(self, vertex):
        """Neighbours in alphabetical order, so every traversal is repeatable."""
        return merge_sort(self.adjacency[vertex])

    def adjacency_matrix(self):
        """V x V matrix: entry [i][j] is the walking time, or 0 if there is no pathway."""
        order = self.vertices()
        position = {vertex: index for index, vertex in enumerate(order)}
        matrix = [[0] * len(order) for _ in order]
        for u in order:
            for v, minutes in self.adjacency[u]:
                matrix[position[u]][position[v]] = minutes
        return order, matrix

    # ============================================================ Task 6(b)
    def depth_first_search(self, start):
        """Iterative DFS using the Task 2 stack. O(V + E)."""
        visited, order = set(), []
        stack = Stack()
        stack.push(start)
        while not stack.is_empty():
            vertex = stack.pop()
            if vertex in visited:
                continue
            visited.add(vertex)
            order.append(vertex)
            # push in reverse so that the alphabetically first neighbour is explored first
            for neighbour, _ in reversed(self.neighbours(vertex)):
                if neighbour not in visited:
                    stack.push(neighbour)
        return order

    def breadth_first_search(self, start):
        """BFS using the Task 2 queue. O(V + E). Visits buildings level by level."""
        visited, order = {start}, []
        queue = Queue()
        queue.enqueue(start)
        while not queue.is_empty():
            vertex = queue.dequeue()
            order.append(vertex)
            for neighbour, _ in self.neighbours(vertex):
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.enqueue(neighbour)
        return order

    def dijkstra(self, source, target=None, trace=None):
        """Shortest walking times from source, using the Task 4 min-heap.

        Returns (distance, previous). If target is given the search stops as
        soon as the target is settled. O((V + E) log V) time, O(V) space.
        trace collects (settled_vertex, its_distance, list_of_improved_neighbours).
        """
        distance = {vertex: INFINITY for vertex in self.adjacency}
        previous = {vertex: None for vertex in self.adjacency}
        distance[source] = 0
        settled = set()
        heap = MinHeap()
        heap.push((0, source))
        while not heap.is_empty():
            minutes, vertex = heap.pop()
            if vertex in settled:
                continue                         # an out-of-date heap entry
            settled.add(vertex)
            improved = []
            if vertex != target:
                for neighbour, weight in self.neighbours(vertex):
                    candidate = minutes + weight
                    if neighbour not in settled and candidate < distance[neighbour]:
                        distance[neighbour] = candidate          # relaxation
                        previous[neighbour] = vertex
                        heap.push((candidate, neighbour))
                        improved.append("%s=%d" % (neighbour, candidate))
            if trace is not None:
                trace.append((vertex, minutes, improved))
            if vertex == target:
                break
        return distance, previous

    def shortest_path(self, source, target, trace=None):
        """Returns (list_of_buildings_on_the_route, total_minutes) or (None, infinity)."""
        distance, previous = self.dijkstra(source, target, trace)
        if distance[target] == INFINITY:
            return None, INFINITY
        route = Stack()                          # walk back from the target, then reverse
        vertex = target
        while vertex is not None:
            route.push(vertex)
            vertex = previous[vertex]
        return route.items_top_first(), distance[target]

    def edge_weight(self, u, v):
        for neighbour, minutes in self.adjacency[u]:
            if neighbour == v:
                return minutes
        return None


def build_campus_graph():
    graph = Graph()
    for code, _, _ in BUILDINGS:
        graph.add_vertex(code)
    for u, v, minutes in PATHWAYS:
        graph.add_edge(u, v, minutes)
    return graph


# ================================================================ Task 6(c)
class CampusSystem:
    """Ties every data structure together behind one set of operations."""

    def __init__(self):
        self.graph = build_campus_graph()

        self.building_tree = BinarySearchTree()          # building code -> record
        for code, name, footfall in BUILDINGS:
            self.building_tree.insert(code, {"code": code, "name": name, "footfall": footfall})

        self.room_table = RoomHashTable(11)              # room code -> record  (hash table)
        self.room_tree = BinarySearchTree()              # room name -> record  (BST)
        for code, name, building in ROOMS:
            record = {"code": code, "name": name, "building": building}
            self.room_table.put(code, record)
            self.room_tree.insert(name.lower(), record)

        self.history = NavigationHistory(limit=10)       # stack
        self.shuttle_queue = Queue()                     # queue
        self.shuttle_route = CircularLinkedList()        # circular linked list
        for stop in SHUTTLE_STOPS:
            self.shuttle_route.append(stop)

    # -- helpers
    def building_name(self, code):
        record, _ = self.building_tree.search(code)
        return record["name"] if record else code

    def is_building(self, code):
        return self.building_tree.contains(code)

    def building_codes(self):
        return self.building_tree.inorder()

    # -- operations
    def find_route(self, source, target):
        route, minutes = self.graph.shortest_path(source, target)
        if route is not None:
            for code in route:
                self.history.push(code)                  # every building walked through
        return route, minutes

    def find_room_by_code(self, room_code):
        return self.room_table.get(room_code.upper())

    def find_room_by_name(self, room_name):
        return self.room_tree.search(room_name.strip().lower())

    def suggest_rooms(self, text):
        """Inorder walk of the room BST returning names that contain the text."""
        text = text.strip().lower()
        matches = []
        for name in self.room_tree.inorder():
            if text in name:
                record, _ = self.room_tree.search(name)
                matches.append(record)
        return matches

    def busiest(self, k):
        locations = [(footfall, code) for code, _, footfall in BUILDINGS]
        ranking, _ = top_k_busiest(locations, k)
        return ranking

    def schedule_shuttle(self, shuttle):
        self.shuttle_queue.enqueue(shuttle)

    def dispatch_shuttle(self):
        return None if self.shuttle_queue.is_empty() else self.shuttle_queue.dequeue()

    def go_back(self):
        """Pop the current building; the new top is where the user was before."""
        if self.history.is_empty():
            return None, None
        left = self.history.pop()
        now = None if self.history.is_empty() else self.history.peek()
        return left, now


# ================================================================ output helpers
def print_adjacency_list(system):
    print("Adjacency list (neighbour: minutes)")
    for vertex in system.graph.vertices():
        pairs = ", ".join("%s:%d" % pair for pair in system.graph.neighbours(vertex))
        print("  %-5s-> %s" % (vertex, pairs))
    print("  %d vertices, %d edges" % (len(system.graph.adjacency), system.graph.edge_count))


def print_adjacency_matrix(system):
    order, matrix = system.graph.adjacency_matrix()
    print("Adjacency matrix (walking time in minutes, 0 = no direct pathway)")
    print("       " + "".join("%5s" % vertex for vertex in order))
    for vertex, row in zip(order, matrix):
        print("  %-5s" % vertex + "".join("%5d" % value for value in row))


def print_route(system, source, target):
    route, minutes = system.find_route(source, target)
    if route is None:
        print("  No route exists between %s and %s." % (source, target))
        return
    print("  Shortest route from %s to %s:" % (system.building_name(source), system.building_name(target)))
    print("    " + " -> ".join(route))
    for u, v in zip(route, route[1:]):
        print("    %-22s to %-22s %2d min" % (system.building_name(u), system.building_name(v),
                                              system.graph.edge_weight(u, v)))
    print("    Total walking time: %d minutes" % minutes)


def print_room(system, record):
    print("    %s  %s  (%s, %s)" % (record["code"], record["name"], record["building"],
                                    system.building_name(record["building"])))


def print_room_by_code(system, room_code):
    record, slot, probes = system.find_room_by_code(room_code)
    if record is None:
        print("  Hash table: no room with code %s (slot %d holds %d other key(s))." % (room_code.upper(), slot, probes))
    else:
        print("  Hash table: found in slot %d of %d after %d probe(s)" % (slot, system.room_table.size, probes))
        print_room(system, record)


def print_room_by_name(system, room_name):
    record, comparisons = system.find_room_by_name(room_name)
    if record is not None:
        print("  BST: found after %d key comparison(s)" % comparisons)
        print_room(system, record)
        return
    print("  BST: no room is called exactly '%s' (%d comparison(s))." % (room_name, comparisons))
    matches = system.suggest_rooms(room_name)
    if matches:
        print("  Rooms whose name contains '%s':" % room_name)
        for match in matches:
            print_room(system, match)


def print_busiest(system, k):
    print("  Top %d busiest locations (average daily footfall)" % k)
    for rank, (footfall, code) in enumerate(system.busiest(k), start=1):
        print("    %d. %-22s %-5s %5d" % (rank, system.building_name(code), code, footfall))


def print_history(system):
    if system.history.is_empty():
        print("  Navigation history is empty.")
        return
    print("  Navigation history, most recent first (%d of %d):" % (system.history.size(), system.history.limit))
    print("    " + " | ".join(system.history.items_top_first()))


def print_shuttle_queue(system):
    waiting = system.shuttle_queue.to_list()
    if not waiting:
        print("  Shuttle queue is empty.")
    else:
        print("  Shuttle queue, front first: " + " | ".join(waiting))


# ================================================================ Task 6(d)
def run_demo():
    system = CampusSystem()
    line = "-" * 72

    print("CAMPUS NAVIGATION AND RESOURCE MANAGEMENT SYSTEM - DEMONSTRATION")
    print(line)
    print_adjacency_list(system)
    print()
    print_adjacency_matrix(system)
    print(line)

    print("Depth-first search from the Main Gate:")
    print("  " + " -> ".join(system.graph.depth_first_search("GATE")))
    print("Breadth-first search from the Main Gate:")
    print("  " + " -> ".join(system.graph.breadth_first_search("GATE")))
    print(line)

    print("1. Shortest route (Dijkstra)")
    print_route(system, "GATE", "SPT")
    print_route(system, "LBX", "HST2")
    trace = []
    system.graph.shortest_path("GATE", "SPT", trace)
    print("  Dijkstra trace for GATE to SPT (vertex settled, distance, labels improved):")
    for step, (vertex, minutes, improved) in enumerate(trace, start=1):
        print("    %2d. %-5s %2d   %s" % (step, vertex, minutes, ", ".join(improved) or "-"))
    print(line)

    print("2. Room lookup")
    print(" Lookup by room code 'ICT-105' using the hash table:")
    print_room_by_code(system, "ICT-105")
    print(" Lookup by room name 'Computer Science Department Office' using the BST:")
    print_room_by_name(system, "Computer Science Department Office")
    print(" Lookup of a code that does not exist, 'LIB-999':")
    print_room_by_code(system, "LIB-999")
    print(" Lookup by part of a name, 'laboratory':")
    print_room_by_name(system, "laboratory")
    print("  (hash table: %d rooms in %d slots, load factor %.2f, longest chain %d; room BST height %d)"
          % (system.room_table.count, system.room_table.size, system.room_table.load_factor(),
             system.room_table.longest_chain(), system.room_tree.height()))
    print(line)

    print("3. Ranking of the busiest locations (min-heap)")
    print_busiest(system, 3)
    print(line)

    print("4. Navigation history (stack)")
    print_history(system)
    left, now = system.go_back()
    print("  Go back: left %s, now at %s" % (left, now))
    left, now = system.go_back()
    print("  Go back: left %s, now at %s" % (left, now))
    print_history(system)
    print(line)

    print("5. Shuttle schedule at the Main Gate (queue)")
    for shuttle in ["SH-01 07:00", "SH-02 07:20", "SH-03 07:40"]:
        system.schedule_shuttle(shuttle)
        print("  Scheduled:", shuttle)
    print_shuttle_queue(system)
    print("  Dispatched:", system.dispatch_shuttle())
    print("  Dispatched:", system.dispatch_shuttle())
    system.schedule_shuttle("SH-04 08:00")
    print("  Scheduled: SH-04 08:00")
    print_shuttle_queue(system)
    print("  Shuttle route for a passenger boarding at Hostel 2 (circular linked list):")
    print("    " + " -> ".join(system.shuttle_route.traverse_from("Hostel 2")))
    print(line)


# ================================================================ interactive menu
MENU = """
==================== CAMPUS NAVIGATION SYSTEM ====================
 1. Shortest route between two buildings      (graph, Dijkstra)
 2. Find a room by room code                  (hash table)
 3. Find a room by name                       (binary search tree)
 4. Show building details                     (binary search tree)
 5. Rank the busiest locations                (min-heap)
 6. Shuttle: schedule a shuttle               (queue)
 7. Shuttle: dispatch the next shuttle        (queue)
 8. Shuttle: show the queue and the route     (queue, circular list)
 9. Navigation history / go back              (stack)
10. Explore the campus with DFS and BFS       (graph)
11. Show adjacency list and adjacency matrix  (graph)
 0. Exit
=================================================================="""


def ask(prompt):
    """input() that also echoes the answer when the input is piped from a file."""
    answer = input(prompt).strip()
    if not sys.stdin.isatty():
        print(answer)
    return answer


def ask_building(system, prompt):
    while True:
        code = ask(prompt).upper()
        if system.is_building(code):
            return code
        print("  Unknown code. Valid codes: " + ", ".join(system.building_codes()))


def run_menu():
    system = CampusSystem()
    while True:
        print(MENU)
        try:
            choice = ask("Choose an option: ")
        except EOFError:
            break

        if choice == "1":
            print("  Buildings: " + ", ".join(system.building_codes()))
            source = ask_building(system, "  From (building code): ")
            target = ask_building(system, "  To (building code): ")
            print_route(system, source, target)
        elif choice == "2":
            print_room_by_code(system, ask("  Room code (for example ICT-105): "))
        elif choice == "3":
            print_room_by_name(system, ask("  Room name (for example Dining Hall): "))
        elif choice == "4":
            code = ask_building(system, "  Building code: ")
            record, comparisons = system.building_tree.search(code)
            print("  %s  %s, average daily footfall %d (BST: %d comparison(s))"
                  % (record["code"], record["name"], record["footfall"], comparisons))
            links = ", ".join("%s %d min" % (v, w) for v, w in system.graph.neighbours(code))
            print("  Direct pathways: " + links)
        elif choice == "5":
            answer = ask("  How many locations (1-%d)? " % len(BUILDINGS))
            if answer.isdigit() and 1 <= int(answer) <= len(BUILDINGS):
                print_busiest(system, int(answer))
            else:
                print("  Please enter a whole number between 1 and %d." % len(BUILDINGS))
        elif choice == "6":
            shuttle = ask("  Shuttle id and departure time (for example SH-01 07:00): ")
            if shuttle:
                system.schedule_shuttle(shuttle)
                print("  Added to the rear of the queue.")
                print_shuttle_queue(system)
            else:
                print("  Nothing entered.")
        elif choice == "7":
            shuttle = system.dispatch_shuttle()
            print("  No shuttle is waiting." if shuttle is None else "  Dispatched: " + shuttle)
            print_shuttle_queue(system)
        elif choice == "8":
            print_shuttle_queue(system)
            if not system.shuttle_queue.is_empty():
                print("  Next to leave: " + system.shuttle_queue.front())
            print("  Route: " + " -> ".join(system.shuttle_route.traverse_from(SHUTTLE_STOPS[0])))
        elif choice == "9":
            print_history(system)
            if not system.history.is_empty() and ask("  Go back one step (y/n)? ").lower() == "y":
                left, now = system.go_back()
                print("  Left %s. %s" % (left, "History is now empty." if now is None else "Now at " + now + "."))
        elif choice == "10":
            start = ask_building(system, "  Start building code: ")
            print("  DFS: " + " -> ".join(system.graph.depth_first_search(start)))
            print("  BFS: " + " -> ".join(system.graph.breadth_first_search(start)))
        elif choice == "11":
            print_adjacency_list(system)
            print()
            print_adjacency_matrix(system)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("  Invalid option. Enter a number from the menu.")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_menu()
