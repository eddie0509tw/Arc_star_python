import numpy as np
class Vertex:
    def __init__(self, event):
        self.event = event
        self.depth = 0
        self.treeid = None
        self.parent = None
        self.is_active = True
        self.children = []

    def deactivate(self):
        self.is_active = False
    

class EventTree:
    def __init__(self,id,root):
        self.id = id
        self.max_depth = 0
        self.max_depth_child = root
        self.last_t = root.event[0]
        self.root = root

    def add_child(self, child,p):
        child.parent = p
        child.depth = p.depth + 1
        if child.depth > self.max_depth:
            self.max_depth = child.depth
            self.max_depth_child = child
        if self.last_t < child.event[0]:
            self.last_t = child.event[0]
        child.treeid = self.id
        p.children.append(child)
        return
    
class EventTracker:
    def __init__(self, dconn=5, delta_t_max=0.1, rho_thresh=5, time_thresh = 0.2):
        self.dconn = dconn
        self.delta_t_max = delta_t_max
        self.rho_thresh = rho_thresh
        self.time_thresh = time_thresh
        self.treenum = 0
        self.graph = {}  # Initialize the graph as an empty dictionary
        self.vneigh = []

    def add_corner_event(self,event):
        v = Vertex(event)
        self.post_process_tree(v)
        # Find neighboring vertices within dconn pixels and delta_t_max time difference
        self.vneigh = []
        self.find_neighboring_vertices(v)
        self.deactivate_vertices()

        # Split vertices into leaf and non-leaf nodes
        Vleaf, Vnotleaf = self.split_leaf_and_notleaf_vertices()

        if len(Vleaf):
            # Find the closest and newest vertex in Vleaf
            vparent = self.find_closest_and_newest_vertex(Vleaf,v)
        elif len(Vnotleaf):
            # Find the closest and newest vertex in Vnotleaf
            vparent = self.find_closest_and_newest_vertex(Vnotleaf,v)
        else:
            # No active vertices in the neighborhood, create a new tree
            tree = EventTree(self.treenum,v)
            v.treeid = self.treenum
            self.treenum += 1
            self.graph[tree.id] = tree
            return

        # Establish data association and grow the tree
        self.establish_data_association(vparent, v)

    def find_neighboring_vertices(self, new_vertex):
        # key will be the id of the tree
        for key,tree in self.graph.items():
            p = tree.root
            if (len(p.children) == 0) and self.is_valid_neighboor(p,new_vertex):
                self.vneigh.append(p)
            else:
                self.traverse_and_append_neighboor(p,new_vertex)
            
        return

    def is_valid_neighboor(self,vertex,new_vertex):
        tt, xx, yy = vertex.event[0], vertex.event[1], vertex.event[2]
        t, x, y = new_vertex.event[0], new_vertex.event[1], new_vertex.event[2]
        if (abs(x - xx) <= self.dconn and 
            abs(y - yy) <= self.dconn and 
            abs(t - tt) <= self.delta_t_max):
            return True
        return False
    
    def traverse_and_append_neighboor(self,root,new_vertex):
        
        if(len(root.children)):
            for child in root.children:
                self.traverse_and_append_neighboor(child,new_vertex)
                # Check proximity in space and time
                if self.is_valid_neighboor(child,new_vertex):

                    self.vneigh.append(child)
            return
        else:
            return
        
    def split_leaf_and_notleaf_vertices(self):
        Vleaf = []
        Vnotleaf = []

        for vertex in self.vneigh:
            if self.is_leaf_vertex(vertex):
                Vleaf.append(vertex)
            else:
                Vnotleaf.append(vertex)

        return Vleaf, Vnotleaf
    
    def is_leaf_vertex(self, vertex):
        if len(vertex.children):
            return False
        return True
                
    def find_closest_and_newest_vertex(self, vertices,new_vertex):
        min_distance = float("inf")
        closest_t = 0
        new_e = new_vertex.event
        closest_vertex = None

        for vertex in vertices:
            e = vertex.event
            distance = (e[1] - new_e[1]) ** 2 + (e[2] - new_e[2]) ** 2
            if distance < min_distance or ((distance == min_distance) and (e[0] > closest_t)):
                closest_t = e[0]
                min_distance = distance
                closest_vertex = vertex

        return closest_vertex
    
    def establish_data_association(self, vparent, new_vertex):
        # Find the tree to which vparent belongs
        parent_tree = self.graph[vparent.treeid]
        parent_tree.add_child(new_vertex,vparent)
        return
    
    def deactivate_vertices(self):
        for vertex in self.vneigh:
            self.traverse_and_deactivate(vertex)
        return
    
    def traverse_and_deactivate(self,root):
        # deactivate all the children of vertex in neighborhood if their depth exceed the rho_thresh
        if(len(root.children)):
            for child in root.children:
                self.traverse_and_deactivate(child)
                if child.is_active:
                    curr_tree = self.graph[child.treeid]
                    if child.depth < (curr_tree.max_depth - self.rho_thresh):
                        child.deactivate()
            return
        else:
            return

    def post_process_tree(self, new_vertex):
        # delete the tree if the last event is older than time_thresh
        new_t = new_vertex.event[0]
        del_list = []
        for key,tree in self.graph.items():
            if (abs(tree.last_t - new_t) > self.time_thresh):
                del_list.append(key)
                continue
        for key in del_list:
            del self.graph[key]
        return
            
    def pick_branch(self):
        # select the active branch with the highest depth
        curr_branch = []
        for key,tree in self.graph.items():
            curr_leaf = tree.max_depth_child
            while curr_leaf:
                if curr_leaf.is_active:
                    curr_branch.append(curr_leaf.event)
                else:
                    break
                curr_leaf = curr_leaf.parent
        if len(curr_branch):
            curr_branch = np.array(curr_branch)
        else:
            curr_branch = np.zeros((0,4))
        return curr_branch

            
# Example usage:
if __name__ == '__main__':
    tracker = EventTracker()
    event1 = np.array([0.1, 10, 20,1])
    event2 = np.array([0.2, 12, 22,0])
    event3 = np.array([0.3, 8, 18,1])
    event4 = np.array([0.39, 11, 16,0])
    event5 = np.array([0.6, 20, 5,1])
    event6 = np.array([0.7, 40, 5,0])
    event7 = np.array([0.13, 11, 21,1])
    event8 = np.array([0.14, 13, 23,1])
    event9 = np.array([0.167, 15, 27,1])
    event10 = np.array([0.8, 100, 20,0])
    event11 = np.array([0.9, 120, 10,0])

    tracker.add_corner_event(event1)
    tracker.add_corner_event(event7)
    tracker.add_corner_event(event8)
    tracker.add_corner_event(event9)
    tracker.add_corner_event(event2)
    tracker.add_corner_event(event3)
    tracker.add_corner_event(event4)
    tracker.add_corner_event(event5)
    tracker.add_corner_event(event6)
    tracker.add_corner_event(event10)
    tracker.add_corner_event(event11)

    for key,tree in tracker.graph.items():
     print(tree.max_depth)
    
    active_branch = tracker.pick_branch()
    print(active_branch)
    print(np.zeros((0,4)))

