"""Give a (multi)subset graph and search for upward-closed properties."""
import sympy as sp
from itertools import combinations


class DAGNode:
    """Create a simple node as appropriate for a DAG"""

    def __init__(self, value, layer, *children):
        """Initialize."""
        self.value = value
        self.layer = layer
        self.children = children
        self.property = False

    def set_property_direct(self, val):
        """Set a property by fiat."""
        self.property = val

    def property_from_children(self):
        """Upward-close the property."""
        for child in self.children:
            if child.property:
                self.property = True

    def __str__(self):
        """Serialise the tree recursively as parent -> (children)."""
        childstring = ", ".join(map(str, self.children))
        return f"{self.value!s} -> ({childstring})"


class MultiSubsetGraph:
    """Given an iterable, give its subset graph."""

    def __init__(self, my_list, debug_mode=False):
        self.tuple = tuple(my_list)
        # layer 0
        empty_node = DAGNode('EmptySet', 0, None)
        self.nodes = [[empty_node,], ]
        # layer 1
        temp_list = []
        for j in my_list:
            temp_list.append(DAGNode((j,), 1, empty_node))
        temp_tuple = tuple(temp_list)
        self.nodes.append(temp_tuple)
        # higher layers
        for j in range(2, len(my_list) + 1):
            if debug_mode:
                print(j)
            temp_list = []
            for combo in combinations(my_list, j):
                new_children_list = []
                for sub_combo in combinations(combo, j - 1):
                    for possible_child in self.nodes[j - 1]:
                        if possible_child.value == sub_combo:
                            new_children_list.append(possible_child)
                            break  # this shortcut may not work for multisets
                temp_list.append(DAGNode(combo, j, *new_children_list))
            temp_tuple = tuple(temp_list)
            self.nodes.append(temp_tuple)

    def count_property_by_layer(self, layer):
        our_denom = sp.functions.combinatorial.numbers.nC(
            len(self.tuple), layer
        )
        our_num = 0
        for node in self.nodes[layer]:
            if node.property:
                our_num += 1
        return (our_num, our_denom, sp.Rational(our_num, our_denom))

    def fill_in_property(
            self, valids, is_layer_promise=False, layer_promise=1
            ):
        """Fill in the property, starter, then upwards closing."""
        if is_layer_promise:
            for node in self.nodes[layer_promise]:
                if any(node.value == valid for valid in valids):
                    node.set_property_direct(True)
            for j in range(layer_promise + 1, len(self.tuple) + 1):
                for node in self.nodes[j]:
                    node.property_from_children()
        else:
            for j in range(1, len(self.tuple)):
                for node in self.nodes[j]:
                    if any(node.value == valid for valid in valids):
                        node.set_property_direct(True)
            # take a second pass to update
            for j in range(1, len(self.tuple) + 1):
                for node in self.nodes[j]:
                    node.property_from_children()
