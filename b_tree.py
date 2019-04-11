
class Node:
    """
    B-Tree node data structure.
    """

    def __init__(self, keys, children):
        """
        Generates a b-tree node containing the given keys
        and children.

        Note: This procedure assumes that, if provided,
        keys and children have the proper structure.
        """
        self.keys = keys 
        self.children = children 
        self.str_pos = None


    def num_keys(self):
        """
        Returns the number of key stored in self.
        """
        return len(self.keys)


    def num_children(self):
        """
        Returns the number of children in self.
        """
        return len(self.children)


    def is_leaf(self):
        """
        Checks whether self is a leaf.
        """
        return self.num_children() == 0


    def search(self, key):
        """
        Returns the index of the key preceding key in self.
        If all keys in self are smaller than key, then the
        returned index equals the number of keys in self.
        """
        left = 0 
        right = self.num_keys()
        while right > left:
            mid = (left + right)//2
            if self.keys[mid] >= key:
                right = mid
            else:
                left = mid + 1
        return left


    def linear_search(self, key):
        """
        Returns the index of the key preceding key in self.
        If all keys in self are smaller than key, then the
        returned index equals the number of keys in self.
        """
        index = 0
        while index < self.num_keys() and self.keys[index] < key:
            index += 1
        return index


    def contains_key_at(self, key, index):
        """
        Checks whether index is the index of key in self.
        """
        return index < self.num_keys() and self.keys[index] == key


    def deep_min(self):
        """
        Returns the smallest key in self's sub-tree.
        """
        node = self
        while not node.is_leaf():
            node = node.children[0]
        return node.keys[0] if node.keys else None


    def deep_max(self):
        """
        Returns the largest key in self's sub-tree.
        """
        node = self
        while not node.is_leaf():
            node = node.children[-1]
        return node.keys[-1] if node.keys else None


    def locate_predecessor(self, key):
        """
        Returns the index of the key potentially
        preceding key in self. If no predecessor
        exists, then -1 is returned.
        """
        index = self.search(key)
        return index-1


    def predecessor(self, key):
        """
        Returns the key preceding key in self.
        If no predecessor exists, then  None is
        returned.
        """
        index = self.locate_predecessor(key)
        return self.keys[index] if index >= 0 else None


    def deep_predecessor(self, index):
        """
        Returns the key, in self's sub-tree, that
        precedes the index-th key in self.

        Note: Assumes that self is not a leaf.
        """
        return self.children[index].deep_max()


    def locate_successor(self, key):
        """
        Returns the index of the key potentially
        succeeding key in self. If no successor 
        exists, then the number of keys in self is
        returned.
        """
        index = 0
        while index < self.num_keys() and self.keys[index] <= key:
            index += 1
        return index


    def successor(self, key):
        """
        Returns the key succeeding key in self.
        If no successor exists, then  None is
        returned.
        """
        index = self.locate_successor(key)
        self.keys[index] if index < self.num_keys() else None


    def deep_successor(self, index):
        """
        Returns the key, in self's sub-tree, that
        succeeds the index-th key in self.

        Note: Assumes that self is not a leaf.
        """
        return self.children[index+1].deep_min()
        

    def insert(self, key):
        """
        Inserts key in self.
        """
        index = self.search(key)
        self.keys.insert(index, key)


    def delete(self, key):
        """
        Deletes key from self.
        """
        index = self.search(key)
        if self.contains_key_at(key, index):
            del self.keys[index]


    def split_child(self, index):
        """
        Splits self's index-th child.

        Splitting divides that child into three parts:
            - The median key.

            - A new left node containing:
                    - The keys located at the left of the median key
                    - The left children of those keys together with
                      the left child of the median key.

            - A new right node containing:
                    - The keys located at the right of the median key in child
                    - the right child of the median key together with the
                      right children of the rest of those keys

        Then makes those nodes the left and right children of the median key
        and inserts the median key into self.
        """
        child = self.children[index]
        median = (child.num_keys())//2
        median_key = child.keys[median]

        left  = Node(child.keys[:median], child.children[:median + 1])
        right = Node(child.keys[median + 1:], child.children[median + 1:])

        self.keys.insert(index, median_key)
        self.children[index:index+1] = [left, right]


    def merge_children(self, index):
        """
        Merges self's index-th keyi and its left
        and right children into a single node.
        """
        median_key = self.keys[index]
        left, right = self.children[index : index+2]

        left.keys.append(median_key)
        left.keys.extend(right.keys)

        if not right.is_leaf():
            left.children.extend(right.children)

        del self.keys[index]
        del self.children[index+1]

        merged = left

        if self.num_keys() == 0:
            self.keys = left.keys
            self.children = left.children
            merged = self

        return merged 


    def grow_child(self, index, min_num_keys):
        """
        Returns self's index-th child after increasing its number of
        keys by either:

            - Transferring a key from a direct sibling that contains
              more than min_num_keys keys or,

            - Merging with a sibling that contains at most min_num_keys
            keys.
        """
        child = self.children[index]
        left_sibling = (index > 0) and self.children[index-1]
        right_sibling = (index < self.num_keys()) and self.children[index+1]

        if left_sibling and left_sibling.num_keys() > min_num_keys:
            self.transfer_key_clockwise(index-1)

        elif right_sibling and right_sibling.num_keys() > min_num_keys:
            self.transfer_key_counter_clockwise(index)

        else:
            shared_key_index = (index - 1) if left_sibling else index
            child = self.merge_children(shared_key_index)

        return child 


    def transfer_key_clockwise(self, index):
        """
        Let child be self's index-th child and let sibling be child's left sibling.
        This method transfers the largest key of sibling to self, replacing its
        index-th key. Then the replaced key and the rightmost child of sibling are
        transferred to child.
        """
        left, right = self.children[index : index+2]
        right.keys.insert(0, self.keys[index])

        if left.children:
            right.children.insert(0, left.children[-1])
            del left.children[-1]

        self.keys[index] = left.keys[-1]
        del left.keys[-1]


    def transfer_key_counter_clockwise(self, index):
        """
        Let child be self's index-th child and let sibling be the right sibling of
        child. This method transfers the smallest key of sibling to self, replacing
        its index-th key. Then the replaced key and the leftmost child of sibling
        are transferred to child.
        """
        left, right = self.children[index : index+2]
        left.keys.append(self.keys[index])

        if not right.is_leaf():
            left.children.append(right.children[0])
            del right.children[0]

        self.keys[index] = right.keys[0]
        del right.keys[0]


    def __str__(self):
        """
        Returns a string representing self.
        """
        T = Btree(2)
        T.root = Node(self.keys, [Node(child.keys, []) for child in self.children])
        return str(T)


    def __repr__(self):
        """
        Represents self.
        """
        return str(self) 



class B_Tree:
    """
    B-Tree data structure.
    """

    def __init__(self, degree):
        """
        Returns an empty b-tree with the given degree.
        Note: Assumes degree > 1.
        """
        self.root = Node([], [])
        self.min_num_keys = degree - 1 
        self.max_num_keys = 2*degree - 1

    
    def search(self, key):
        """
        Searches for the given key in the b-tree. Returns
        a location pair (node, index), if the given key is
        found, and None otherwise.
        """
        (node, index) = self.root, self.root.search(key)
        while not node.contains_key_at(key, index) and not node.is_leaf():
            node = node.children[index]
            index = node.search(key)

        return (node, index) if node.contains_key_at(key, index) else None


    def predecessor(self, key):
        """
        Returns the predecessor of key in the b-tree if
        a predecessor exists and None otherwise.
        """
        node = self.root
        predecessor = None
        while node:
            index = node.locate_predecessor(key)
            if index >= 0:
                predecessor = node.keys[index]
            node = node.children[index+1] if not node.is_leaf() else None
        return predecessor


    def successor(self, key):
        """
        Returns the successor of key in the b-tree if
        a successor exists and None otherwise.
        """
        node = self.root
        successor = None
        while node:
            index = node.locate_successor(key)
            if index < node.num_keys():
                successor = node.keys[index]
            node = node.children[index] if not node.is_leaf() else None
        return successor


    def insert(self, key):
        """
        Inserts key in the b-tree.
        """
        if self.root.num_keys() == self.max_num_keys:
            self.root = Node([], [self.root])
            self.root.split_child(0)

        node = self.root 
        while not node.is_leaf():
            index = node.search(key)

            child = node.children[index]
            if child.num_keys() == self.max_num_keys:
                node.split_child(index)

                if node.keys[index] < key:
                    index += 1

            node = node.children[index] 

        node.insert(key)


    def delete(self, key):
        """
        Deletes key from the b-tree.
        """
        node = self.root
        while not node.is_leaf():
            index = node.search(key)

            if node.contains_key_at(key, index):
                left, right = node.children[index : index+2]

                if left.num_keys() > self.min_num_keys:
                    node.keys[index] = node.deep_predecessor(index)
                    (node, key) = (left, node.keys[index])

                elif right.num_keys() > self.min_num_keys:
                    node.keys[index] = node.deep_successor(index) 
                    (node, key) = (right, node.keys[index])

                else:
                    node = node.merge_children(index)

            else:
                child = node.children[index]
                if child.num_keys() <= self.min_num_keys:
                   child = node.grow_child(index, self.min_num_keys)
                node = child
                    
        node.delete(key)


    def inorder(self):
        """
        Generates the keys of the b-tree in non-decreasing order.
        """
        queue = []
        node = self.root
        index = 0
        while node:

            if node.is_leaf():
                yield from node.keys

                if not queue:
                    node = None

                else:
                    node, index = queue.pop()
                    yield node.keys[index]
                    index = index + 1

            else:
                if index < node.num_keys():
                    queue.append((node, index))

                node = node.children[index]
                index = 0


    def breadth_first_search(self):
        """
        Generates the nodes of the b-tree in breath-first order.
        """
        queue = [self.root]
        while queue:
            node = queue.pop()
            yield node
            queue.extend(node.children)
    

    def depth_first_search(self):
        """
        Generates the nodes of the b-tree in depth-first order.
        """
        queue = [self.root]
        ordered = []
        while queue:
            node = queue.pop()
            ordered.append(node)
            queue.extend(node.children)
        
        while ordered:
            yield ordered.pop()


    def __str__(self):
        """
        Returns a string representing the b-tree.
        """
        levels = tuple(self.generate_levels())
        self.compute_representation_positions()
        levels_to_strings = self.represent_tree_levels(levels)
        branches = self.represent_tree_branches(levels)

        return "".join("".join((level, "\n\n", branch))
                        for (level, branch) in zip(levels_to_strings, branches))


    def generate_levels(self):
        """
        Generates the levels of the tree. Here, a level is a list containing 
        the nodes of the corresponding level in the tree.
        """
        level = (self.root,)
        while level:
            yield level
            level = tuple(child for node in level for child in node.children)


    def compute_representation_positions(self):
        """
        Consider a node in the tree and define the label of a node
        be the string representation of its list of keys. This
        method computes the start position of the label of every
        node in the tree and stores the result in an attribute
        node.repr_pos
        """
        offset = 3
        for node in self.depth_first_search():

            if node.is_leaf():
                node.str_pos = offset
                offset += len(str(node.keys)) + 2

            else:
                first_child_mid = node.children[ 0].str_pos + len(str(node.children[ 0].keys))//2
                last_child_mid  = node.children[-1].str_pos + len(str(node.children[-1].keys))//2
                node.str_pos = (first_child_mid + last_child_mid)//2 - len(str(node.keys))//2


    def represent_tree_levels(self, levels):
        """
        Generates the string representation of every level in the tree.
        """
        prev_node_end = 0 
        level_string = []
        for level in levels:
            prev_node_end = 0 
            level_string = []
            for node in level: 
                node_to_str = str(node.keys)
                space_between_nodes = node.str_pos - prev_node_end 
                level_string.extend((" "*space_between_nodes, node_to_str))
                prev_node_end = node.str_pos + len(node_to_str)

            yield "".join(level_string)


    def represent_tree_branches(self, levels):
        """
        Generates the string representation of the branches of every
        level in the tree.
        """
        for level in levels[:-1]:
            branch = []
            prev_child_mid = 0 
            for node in level:
                curr_child_mid = node.children[0].str_pos + len(str(node.children[0].keys))//2
                space_between_children = curr_child_mid - prev_child_mid 
                branch.extend((" "*space_between_children, "|"))
                prev_child_mid = curr_child_mid + 1
                for child in node.children[1:]:
                    curr_child_mid = child.str_pos + len(str(child.keys))//2
                    space_between_children = curr_child_mid - prev_child_mid 
                    branch.extend(("-"*space_between_children, "|"))
                    prev_child_mid = curr_child_mid + 1
            
            branch = "".join(branch)
            branch = "".join((branch, "\n", branch.replace("-", " "), "\n\n"))
            yield branch

        yield ""
                

    def __repr__(self):
        """
        Represents the b-tree.
        """
        return str(self)

