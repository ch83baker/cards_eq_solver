from sympy import Rational
from sympy.functions.combinatorial.numbers import nC
# from copy import copy


def encode_bin_tuple_to_int(my_tuple, num_terms):
    """Encode characteristic tuple as a string for compactness.

    Parameters:
    -----------
    my_tuple: Iterable
        The 0-1 tuple encoding membership in the subset
    num_terms: int (positive)
        the number of terms in your set of items
    """
    if len(my_tuple) != num_terms:
        raise ValueError(f"Not a {num_terms}-length tuple!")
    sum = 0
    for j in range(num_terms):
        if my_tuple[j]:
            sum += 2**j
    return sum


def decode_int_to_bin_tuple(code_int, num_terms):
    """Decode integer as a characteristic tuple.

    Parameters:
    -----------
    code_int: int
        The int whose binary representation encodes the subset.
    num_terms: int (positive)
        the number of terms in your set of items
    """
    if code_int < 0 or code_int >= 2**num_terms:
        raise ValueError("Outside range.")
    output_list = []
    for j in range(num_terms):
        output_list.append(code_int % 2)
        code_int = code_int // 2
    return tuple(output_list)


def encode_members_as_bin_tuple(short_list, items):
    """Encode a sequence (the list of items in a subset)
    as a characteristic tuple.

    Parameters:
    -----------
    short_list: Iterable
       The set of items in the subset of choice.
    items: Iterable
       the iterable giving you the items.
    """
    num_terms = len(items)
    output = [0 for j in range(num_terms)]
    for j in short_list:
        for pair in enumerate(items):
            if pair[1] == j:
                output[pair[0]] = 1
    return tuple(output)


def decode_bin_tuple_as_members(long_list, items):
    """Decode binary tuple as the sequence of elements
    it represents.

    Parameters:
    -----------
    long_list: Iterable
        The 0-1 tuple encoding membership in the subset
    items: Iterable
       the iterable giving you the set's items.
    """
    num_terms = len(items)
    if len(long_list) != num_terms:
        raise ValueError("Not the right length of list.")
    output = []
    for pair in enumerate(long_list):
        if pair[1]:
            output.append(items[pair[0]])
    return tuple(output)


class BinSubsetGraph():
    """
    Get minimally-labeled subset system.
    That said, considering a set of > 20 elements is likely to
    cause memory errors!

    Parameters
    ------------
    my_list: Iterable
        The list constaining all items in your set.  No repeats allowed.
    status_updates: bool
        Determine whether standard output gives status updates
    group_size: int (positive)
        Only active if status_updates is True
        Determines the interval at which status updates given.
    """

    def __init__(self, my_list, status_updates=False, group_size=10**4):
        self.items = tuple(my_list)
        self.n = len(my_list)
        count = 0
        num_groups = 0
        self.subset_list = []
        for j in range(2**self.n):
            self.subset_list.append({
                "bin_list": decode_int_to_bin_tuple(j, self.n),
                "num_elts": 0,
                "parents": [],
                "property": False
            })
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Started {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        # initialize num_elts, parents
        count = 0
        num_groups = 0
        for j in range(2**self.n - 1):  # last term is full set, no parents
            my_bin_tuple = self.subset_list[j]["bin_list"]
            self.subset_list[j]["num_elts"] = my_bin_tuple.count(1)
            for numbered_pair in enumerate(my_bin_tuple):
                if not numbered_pair[1]:  # i.e., 0 there
                    temp_list = list(self.subset_list[j]["bin_list"])
                    temp_list[numbered_pair[0]] = 1
                    self.subset_list[j]["parents"].append(
                        encode_bin_tuple_to_int(temp_list, self.n)
                    )
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        # last term  has no parents, but still must update counter.
        self.subset_list[2**self.n - 1]["num_elts"] = self.n

    def count_property_by_layer(self, layer):
        '''Count the number of subsets in a given layer
        with the desired upward-closed property.

        Parameters
        -----------
        layer: int (nonnegative)
            the cardinality of subsets you wish to consider.
        '''
        our_denom = nC(len(self.items), layer)
        our_num = 0
        for j in range(2**self.n):
            if self.subset_list[j]["num_elts"] == layer:
                if self.subset_list[j]["property"]:
                    our_num += 1
        return (our_num, our_denom, Rational(our_num, our_denom))

    def fill_in_property(self, valids):
        '''Fill in (all) known subsets with a given upward-closed property.

        Parameters
        -------------
        valids: Iterable[tuple]
            The iterable whose tuples list the members of the subsets
            with the desired property.
        '''
        for valid in valids:
            self.subset_list[encode_bin_tuple_to_int(
                encode_members_as_bin_tuple(valid, self.items),
                self.n
            )]["property"] = True
        # bubble up, starting with fewest elements
        # currently using n passes, but still ensuring that
        # each term only bubbles up once
        for k in range(self.n):
            for j in range(2**self.n):
                if self.subset_list[j]["num_elts"] == k:
                    if self.subset_list[j]["property"]:
                        for parent in self.subset_list[j]["parents"]:
                            self.subset_list[parent]["property"] = True

    def clear_property(self):
        '''
        Retain the set, but clear all property data out.
        '''
        for j in range(2**self.n):
            self.subset_list[j]["property"] = False


class BinSubsetGraphExtras(BinSubsetGraph):
    """Get subset graph with explicit extras added (for testing).
    Uncertain if this method can handle a 20-element set!

    Parameters
    ------------
    my_list: Iterable
        The list constaining all items in your set.  No repeats allowed.
    status_updates: bool
        Determine whether standard output gives status updates
    group_size: int (positive)
        Only active if status_updates is True
        Determines the interval at which status updates given.
    """

    def __init__(self, my_list, status_updates=False, group_size=10**4):
        super().__init__(my_list, status_updates, group_size)
        count = 0
        num_groups = 0
        for j in range(2**self.n):
            self.subset_list[j]["index"] = j
            self.subset_list[j]["members"] = decode_bin_tuple_as_members(
                decode_int_to_bin_tuple(j, self.n), self.items
            )
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print("Finished extras for "
                          + f"{num_groups} groups"
                          + f' of size {group_size}')
                    count = 0


class BinSubsetGraphCpct():
    """
    Get minimally-labeled subset system, internals as flat list.
    Initial attempt to curtail size, sadly ineffective.

    Parameters
    ------------
    my_list: Iterable
        The list constaining all items in your set.  No repeats allowed.
    status_updates: bool
        Determine whether standard output gives status updates
    group_size: int (positive)
        Only active if status_updates is True
        Determines the interval at which status updates given.
    """

    def __init__(self, my_list, status_updates=False, group_size=10**4):
        self.items = tuple(my_list)
        self.n = len(my_list)
        count = 0
        num_groups = 0
        self.subset_list = []
        for j in range(2**self.n):
            # append list [bin_tuple, num_elts, parents, property]
            self.subset_list.append(
                [decode_int_to_bin_tuple(j, self.n), 0, [], False]
            )
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Started {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        # initialize num_elts, parents
        count = 0
        num_groups = 0
        for j in range(2**self.n - 1):  # last term is full set, no parents
            my_bin_tuple = self.subset_list[j][0]
            self.subset_list[j][1] = my_bin_tuple.count(1)
            for numbered_pair in enumerate(my_bin_tuple):
                if not numbered_pair[1]:  # i.e., 0 there
                    temp_list = list(self.subset_list[j][0])
                    temp_list[numbered_pair[0]] = 1
                    self.subset_list[j][2].append(
                        encode_bin_tuple_to_int(temp_list, self.n)
                    )
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        # last term  has no parents, but still must update counter.
        self.subset_list[2**self.n - 1][1] = self.n

    def fill_in_property(self, valids):
        '''Fill in (all) known subsets with a given upward-closed property.

        Parameters
        -------------
        valids: Iterable[tuple]
            The iterable whose tuples list the members of the subsets
            with the desired property.
        '''
        for valid in valids:
            self.subset_list[encode_bin_tuple_to_int(
                encode_members_as_bin_tuple(valid, self.items),
                self.n
            )][3] = True
        # bubble up, starting with fewest elements
        # currently using n passes, but still ensuring that
        # each term only bubbles up once
        for k in range(self.n):
            for j in range(2**self.n):
                if self.subset_list[j][1] == k:
                    if self.subset_list[j][3]:
                        for parent in self.subset_list[j][2]:
                            self.subset_list[parent][3] = True

    def clear_property(self):
        '''
        Retain the set, but clear all property data out.
        '''
        for j in range(2**self.n):
            self.subset_list[j][3] = False

    def count_property_by_layer(self, layer):
        '''Count the number of subsets in a given layer
        with the desired upward-closed property.

        Parameters
        -----------
        layer: int (nonnegative)
            the cardinality of subsets you wish to consider.
        '''
        our_denom = nC(len(self.items), layer)
        our_num = 0
        for j in range(2**self.n):
            if self.subset_list[j]["num_elts"] == layer:
                if self.subset_list[j]["property"]:
                    our_num += 1
        return (our_num, our_denom, Rational(our_num, our_denom))


def dict_constructor(the_bin_tuple, prop=False):
    '''Given a bin_tuple representing a subset
    and its membership in the property,
    create the dictionary item to be stored
    in the table.

    Parameters
    -----------
    the_bin_tuple: Iterable[int]
       The 0-1 tuple encoding the subset.
    prop: bool
       The indicator of whether or not the subset has the property.
    '''
    num_terms = len(the_bin_tuple)
    num_elts = the_bin_tuple.count(1)
    parents = []
    for numbered_pair in enumerate(the_bin_tuple):
        if not numbered_pair[1]:  # missing term
            temp_list = list(the_bin_tuple)
            temp_list[numbered_pair[0]] = 1
            parents.append(encode_bin_tuple_to_int(temp_list,
                                                   num_terms))
    return {
            "bin_list": the_bin_tuple,
            "num_elts": num_elts,
            "parents": parents,
            "property": prop
    }


class BinSubsetGraphSparse():
    """
    Get minimally-labeled subset system, with only 1-2 layers at a time to
    avoid overloading space.  Redundant num_terms system for debugging.

    Parameters
    ------------
    my_list: Iterable
        The list constaining all items in your set.  No repeats allowed.
    start_layer: int (nonnegative)
        The layer at which we begin studying the subset graph.
        Cannot exceed len(my_list)
    status_updates: bool
        Determine whether standard output gives status updates
    group_size: int (positive)
        Only active if status_updates is True
        Determines the interval at which status updates given.
    """

    def __init__(self, my_list, start_layer=0, status_updates=False,
                 group_size=10**4):
        self.items = tuple(my_list)
        self.n = len(my_list)
        self.current_layer = start_layer
        count = 0
        num_groups = 0
        self.subset_list = []
        for j in range(2**self.n):
            my_bin_tuple = decode_int_to_bin_tuple(j, self.n)
            num_terms = my_bin_tuple.count(1)
            # build only current and next layer and connections
            if num_terms == start_layer:
                self.subset_list.append(dict_constructor(my_bin_tuple, False))
            else:  # still need a (falsy) entry to keep the counting straight
                self.subset_list.append(False)
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0

    def count_property_at_current_layer(self):
        '''Count the number of subsets in the current layer
        with the desired upward-closed property.'''
        our_denom = nC(len(self.items), self.current_layer)
        our_num = 0
        for j in range(2**self.n):
            if self.subset_list[j]:  # otherwise, skip
                if self.subset_list[j]["num_elts"] == self.current_layer:
                    if self.subset_list[j]["property"]:
                        our_num += 1
        return (our_num, our_denom, Rational(our_num, our_denom))

    def fill_in_property_at_current_layer(self, valids):
        '''Fill in the property with valid elements at the current layer.
        The user is responsible for ensuring that they are at the right
        cardinality for the subsets.

        Parameters
        -------------
        valids: Iterable[tuple]
            The iterable whose tuples list the members of the subsets
            of the current cardinality with the desired property.
        '''
        for valid in valids:
            my_ind = encode_bin_tuple_to_int(
                encode_members_as_bin_tuple(valid, self.items),
                self.n
            )
            try:
                self.subset_list[my_ind]["property"] = True
            except TypeError as e:
                my_string = f'Entry {valid},\n'
                + f'indexed by {my_ind}, is not instantiated!'
                print(my_string)
                raise e
        return True

    def raise_layer_with_properties(self, status_updates=False,
                                    group_size=10**4):
        '''Assuming an upward-closed property,
        increase the subset-size by one, filling in the property
        as relevant.

        Parameters
        -------------
        status_updates: bool
            Determine whether standard output gives status updates
        group_size: int (positive)
            Only active if status_updates is True
            Determines the interval at which status updates given.
        '''
        if self.current_layer == self.n:
            raise ValueError("No more layers to go!")
        # update current_layer at end of process
        # add new terms
        count = 0
        num_groups = 0
        for j in range(2**self.n):
            if self.subset_list[j]:  # if nothing there, nothing to do
                if self.subset_list[j]["num_elts"] == self.current_layer:
                    # Aside: this is the only time that num_elts matters.
                    # otherwise, will need to make a temp list to not
                    # delete new terms.
                    for parent in self.subset_list[j]["parents"]:
                        # if someone else created it already,
                        # only need to update a positive property
                        if self.subset_list[parent]:
                            if self.subset_list[j]["property"]:
                                self.subset_list[parent]["property"] = True
                        else:  # create element
                            self.subset_list[parent] = dict_constructor(
                                decode_int_to_bin_tuple(parent, self.n),
                                self.subset_list[j]["property"]
                            )
                    # delete current-layer term when done with updating its
                    # parents
                    self.subset_list[j] = False
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0

        self.current_layer += 1
        print(f"We are now considering {self.current_layer}-element subsets.")

    def clear_property_and_reset_layer(self, cur_layer, status_updates=False,
                                       group_size=10**4):
        '''Keep the set the same, but clear all data and restart anew.

        Note: the original writer did not use or test this function much;
        use at your own risk.

        Parameters
        -------------
        cur_layer: int (nonnegative)
           The new starting cardinality for subsets to be considered.
        status_updates: bool
            Determine whether standard output gives status updates
        group_size: int (positive)
            Only active if status_updates is True
            Determines the interval at which status updates given.
        '''
        self.current_layer = cur_layer
        count = 0
        num_groups = 0
        for j in range(2**self.n):
            my_bin_tuple = decode_int_to_bin_tuple(j, self.n)
            num_terms = my_bin_tuple.count(1)
            # build only current and next layer and connections
            if num_terms == cur_layer:
                self.subset_list.append(dict_constructor(my_bin_tuple, False))
            else:  # still need a (falsy) entry to keep the counting straight
                self.subset_list.append(False)
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
