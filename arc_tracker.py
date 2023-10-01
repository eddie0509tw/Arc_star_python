import numpy as np

class EventTracker:
    def __init__(self, dconn=5, delta_t_max=0.1, rho_thresh=5):
        self.dconn = dconn
        self.delta_t_max = delta_t_max
        self.rho_thresh = rho_thresh
        self.graph = {}  # Initialize the graph as an empty dictionary

    def add_corner_event(self, event):
        t, x, y = event

        # Find neighboring vertices within dconn pixels and delta_t_max time difference
        Vneigh = self.find_neighboring_vertices(event)

        # Split vertices into leaf and non-leaf nodes
        Vleaf, Vnotleaf = self.split_leaf_and_notleaf_vertices(Vneigh)

        if Vleaf:
            # Find the closest and newest vertex in Vleaf
            vparent = self.find_closest_and_newest_vertex(Vleaf)
        elif Vnotleaf:
            # Find the closest and newest vertex in Vnotleaf
            vparent = self.find_closest_and_newest_vertex(Vnotleaf)
        else:
            # No active vertices in the neighborhood, create a new tree
            self.graph[t] = [event]
            return

        # Establish data association and grow the tree
        self.establish_data_association(vparent, event)

    def find_neighboring_vertices(self, event):
        t, x, y = event
        Vneigh = []

        for v in self.graph.values():
            for vertex in v:
                tt, xx, yy = vertex
                # Check proximity in space and time
                if (
                    abs(x - xx) <= self.dconn
                    and abs(y - yy) <= self.dconn
                    and abs(t - tt) <= self.delta_t_max
                ):
                    Vneigh.append(vertex)

        return Vneigh

    def split_leaf_and_notleaf_vertices(self, Vneigh):
        Vleaf = []
        Vnotleaf = []

        for vertex in Vneigh:
            t, x, y = vertex
            if self.is_leaf_vertex(vertex):
                Vleaf.append(vertex)
            else:
                Vnotleaf.append(vertex)

        return Vleaf, Vnotleaf

    def is_leaf_vertex(self, vertex):
        t, x, y = vertex

        for v in self.graph.values():
            for v_event in v:
                tt, xx, yy = v_event
                # Check if vertex is older than any other vertex in the tree
                if t > tt:
                    return False

        return True

    def find_closest_and_newest_vertex(self, vertices):
        min_distance = float("inf")
        closest_vertex = None

        for vertex in vertices:
            t, x, y = vertex
            distance = x ** 2 + y ** 2  # Euclidean distance in image plane
            if distance < min_distance or (distance == min_distance and t > closest_vertex[0]):
                min_distance = distance
                closest_vertex = vertex

        return closest_vertex

    def establish_data_association(self, vparent, event):
        t_parent, x_parent, y_parent = vparent
        t_event, x_event, y_event = event

        # Find the tree to which vparent belongs
        parent_tree = None
        for key, value in self.graph.items():
            if vparent in value:
                parent_tree = key
                break

        # Add the event to the tree
        if parent_tree is not None:
            self.graph[parent_tree].append(event)
        else:
            self.graph[t_event] = [event]

    def deactivate_vertices(self, tree):
        max_depth = self.compute_max_depth(tree)

        for vertex in self.graph[tree]:
            t, x, y = vertex
            depth = self.compute_depth(tree, vertex)
            if max_depth - depth > self.rho_thresh:
                self.graph[tree].remove(vertex)

    def compute_max_depth(self, tree):
        max_depth = 0
        for vertex in self.graph[tree]:
            depth = self.compute_depth(tree, vertex)
            if depth > max_depth:
                max_depth = depth
        return max_depth

    def compute_depth(self, tree, vertex):
        t, x, y = vertex
        depth = 0
        for v in self.graph[tree]:
            tt, xx, yy = v
            if tt < t and abs(x - xx) <= self.dconn and abs(y - yy) <= self.dconn:
                depth += 1
        return depth

# Example usage:
tracker = EventTracker()
event1 = (0.1, 10, 20)
event2 = (0.2, 12, 22)
event3 = (0.3, 8, 18)

tracker.add_corner_event(event1)
tracker.add_corner_event(event2)
tracker.add_corner_event(event3)

print(tracker.graph)
