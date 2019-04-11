from b_tree import *
from random import randint, shuffle, sample

class B_Tree_Tester:


    def __init__(self, t, num_ops):
        self.T = B_Tree(t)
        self.num_ops = num_ops
#       self.random_tree()
#       print(self.T)
        self.perform_tests()


    def perform_tests(self):
        key_range = 10*self.num_ops
        universe = set(range(-key_range, key_range + 1))
        keys = [randint(-key_range, key_range + 1) for _ in range(self.num_ops)]
        existent = set(keys)
        nonexistent = list(sample(universe.difference(existent), self.num_ops))
        sorted_keys = sorted(existent)

        if not self.test_insert(keys):
            return False

        if not self.test_search(existent, nonexistent):
            return False

        if not self.test_predecessor(sorted_keys):
            return False

        if not self.test_successor(sorted_keys):
            return False

        if not self.test_delete(keys, nonexistent):
            return False


    def test_search(self, existent, nonexistent):
        print("Testing existent searches...")
        for key in existent:
            out, check = self.search(key)

            if not check:
                return False

            if out == None:
                print("\tExistent key not found")
                return False

            else:
                node, index = out
                if node.keys[index] != key:
                    print("\tIncorrect key found")
                    return False

        print("\tCorrect\n")

        print("Testing non-existent searches...")
        for key in nonexistent:
            out, check = self.search(key)

            if not check:
                return False

            elif out != None:
                print("\tNon-existent key found")
                return False

        print("\tCorrect\n")
        return True


    def test_predecessor(self, sorted_keys):
        print("Testing predecessor...")
        valid_predecessor = self.compute_predecessor(sorted_keys)
        for key in sorted_keys:
            predecessor, check = self.predecessor(key)
            if not check:
                return False

            if predecessor != valid_predecessor[key]:
                return False

        predecessor, check = self.predecessor(float('-inf'))
        if not check:
            return False

        if predecessor != None:
            print("\tIncorrect predecessor for -infinity")
            return False

        predecessor, check = self.predecessor(float('inf'))
        if not check:
            return False

        if predecessor != sorted_keys[-1]:
            print("\tIncorrect predecessor for infinity")
            return False

        print("\tCorrect\n")
        return True
    

    def compute_predecessor(self, sorted_keys):
        predecessor = dict()
        predecessor[sorted_keys[0]] = None
        for (prev, curr) in zip(sorted_keys, sorted_keys[1:]):
            predecessor[curr] = prev
        return predecessor


    def test_successor(self, sorted_keys):
        print("Testing successor...")
        valid_successor = self.compute_successor(sorted_keys)
        for key in sorted_keys:
            successor, check = self.successor(key)
            if not check:
                return False

            if successor != valid_successor[key]:
                print("\tIncorrect successor")
                return False

        successor, check = self.successor(float('-inf'))
        if not check:
            return False

        if successor != sorted_keys[0]:
            print("\tIncorrect successor for -infinity")
            return False

        successor, check = self.successor(float('inf'))
        if not check:
            return False

        if successor != None:
            print("\tIncorrect successor for infinity")
            return False

        print("\tCorrect\n")
        return True


    def compute_successor(self, sorted_keys):
        successor = dict()
        for (curr, next) in zip(sorted_keys, sorted_keys[1:]):
            successor[curr] = next 
        successor[sorted_keys[-1]] = None
        return successor


    def test_insert(self, keys):
        print("Testing Insertion...")
        for key in keys:
            if not self.insert(key):
                return False

        print("\tCorrect\n")
        return True

    
    def test_delete(self, keys, nonexistent):
        print("Testing non-existent deletions....")
        shuffle(keys)
        shuffle(nonexistent)

        valid_num_keys = 0
        valid_count = dict()
        for key in keys:
            valid_num_keys += 1
            valid_count[key] = valid_count.get(key, 0) + 1

        for key in nonexistent:
            if not self.delete(key):
                return False

            num_keys = 0
            for key in keys:
                num_keys += 1

            if  valid_num_keys != num_keys:
                print("\tNon-existent key deleted")

        print("\tCorrect\n")

        print("Testing existent deletions....")
        for key in keys:
            if not self.delete(key):
                return False

            valid_num_keys -= 1
            valid_count[key] -= 1

            count = dict()
            num_keys = 0
            for k in self.T.inorder():
                num_keys += 1
                count[k] = count.get(k, 0) + 1

            if valid_num_keys != num_keys:
                print("\tIncorrect number of keys deleted")
                return False

            if valid_count[key] != count.get(key, 0):
                print("\tIncorrect key deleted")
                return False

        print("\tCorrect\n")
        return True


    def search(self, k):
        out = self.T.search(k)
        return (out, self.check())


    def predecessor(self, k):
        out = self.T.predecessor(k)
        return (out, self.check)


    def successor(self, k):
        out = self.T.successor(k)
        return (out, self.check)


    def insert(self, k):
        self.T.insert(k)
        return self.check()
        

    def delete(self, k):
        self.T.delete(k)
        return self.check()


    def split_child(self, node, index):
        node.split_child(index)
        return self.check()


    def check(self):
        is_valid = True

        if not self.check_root():
            print("The root violates the representation invariant")
            is_valid = False

        queue = self.T.root.children and self.T.root.children[:]

        while queue:
            node = queue.pop()

            if not self.check_node(node):
                is_valid = False

            if node.children:
                queue.extend(node.children)

        if not self.all_leaves_at_same_depth():
            print("Not all leaves are at the same depth")
            is_valid = False

        return is_valid 
    

    def check_root(self):
        root = self.T.root
        is_valid = True

        if not self.valid_num_keys(root):
            print("Invalid number of keys")
            is_valid = False

        if not self.num_keys_below_upper_bound(root):
            print("The root has more than 2t-1 keys")
            is_valid = False

        if not self.keys_sorted_in_ascending_order(root):
            print("Root keys are not sorted in ascending order")
            is_valid = False

        if root.children:

            if not self.valid_num_keys_num_children_relation(root):
                print("Number of keys != number of children - 1")
                is_valid = False

            if not self.num_children_below_upper_bound(root):
                print("The root has more than 2t children")
                is_valid = False

            if not self.valid_key_children_ordering(root):
                print("Invalid key-children ordering")
                is_valid = False

        if not is_valid:
            self.show_state(root)

        return is_valid


    def check_node(self, node):
        is_valid = True

        if not self.valid_num_keys(node):
            print("Invalid number of keys")
            is_valid = False

        if not self.num_keys_over_lower_bound(node):
            print("The node has less than t-1 keys")
            is_valid = False

        if not self.num_keys_below_upper_bound(node):
            print("The node has more than 2t-1 keys")
            is_valid = False

        if not self.keys_sorted_in_ascending_order(node):
            print("Node keys are not sorted in ascending order")
            is_valid = False

        if node.children:

            if not self.valid_num_keys_num_children_relation(node):
                print("Number of keys != number of children - 1")
                is_valid = False

            if not self.num_children_over_lower_bound(node):
                print("The node has less than t children")
                is_valid = False

            if not self.num_children_below_upper_bound(node):
                print("The node has more than 2t children")
                is_valid = False

            if not self.valid_key_children_ordering(node):
                print("Invalid key-children ordering")
                is_valid = False

        if not is_valid:
            self.show_state(node)

        return is_valid


    def valid_num_keys(self, node):
        return node.num_keys() == len(node.keys)


    def num_keys_over_lower_bound(self, node):
        return node.num_keys() >= self.T.min_num_keys
    

    def num_keys_below_upper_bound(self, node):
        return node.num_keys() <= self.T.max_num_keys


    def keys_sorted_in_ascending_order(self, node):
        return all(node.keys[i-1] <= node.keys[i] for i in range(1, node.num_keys()))


    def valid_num_keys_num_children_relation(self, node):
        return node.num_keys() == node.num_children() - 1


    def num_children_over_lower_bound(self, node):
        return node.num_children() >= self.T.min_num_keys + 1


    def num_children_below_upper_bound(self, node):
        return node.num_children() <= self.T.max_num_keys + 1


    def valid_key_children_ordering(self, node):
        return all( key >= max(child.keys) for (key, child) in zip(node.keys, node.children)) \
               and  ( node.keys[-1] <= min(node.children[-1].keys) )


    def all_leaves_at_same_depth(self):

        tree_depth = self.get_tree_depth()
        queue = [(self.T.root, 0)]
        
        while queue:
            (node, node_depth) = queue.pop()

            if node.children:
                child_depth = node_depth + 1
                queue.extend((child, child_depth) for child in node.children)

            elif node_depth != tree_depth:
                return False

        return True


    def get_tree_depth(self):
        depth, node = 0, self.T.root
        while node.children:
            depth += 1
            node = node.children[0]
        return depth 


    def show_state(self, node):
        print("num_keys: {}".format(node.num_keys()))
        print("len(keys): {}".format(len(node.keys)))
        print("keys: {}".format(node.keys))
        print("num children: {}".format(node.num_children()))
        print("children: {}".format([child.keys for child in node.children]))
        if node.children:
            for i in range(node.num_keys()):
                print ("key:   {}".format(node.keys[i]))
                print ("left:  {}".format((i < node.num_children()) and node.children[i].keys))
                print ("right: {}".format((i+1 < node.num_children()) and node.children[i+1].keys))


    def random_tree(self):
        key_range = 10*self.num_ops
        for i in range(num_ops):
            self.insert(randint(-key_range, key_range))


    def __str__(self):
        return str(self.T)


    def __repr__(self):
        return repr(self.T)

