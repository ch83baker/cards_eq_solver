from sympy import Rational
from sympy.functions.combinatorial.numbers import nC


def encode_seq_as_bin_tuple(short_list, items):
    """Encode a list of [distinct] elements as a
    characteristic function.

    Parameters:
    -----------
    short_list: Iterable
       The set of items in the subset of choice.
    items: Iterable
       The list of all the elements of the set.
    """
    num_terms = len(items)
    output = [0 for j in range(num_terms)]
    for j in short_list:
        for pair in enumerate(items):
            if pair[1] == j:
                output[pair[0]] = 1
    return tuple(output)


def encode_bin_tuple_as_str(my_tuple, num_terms):
    """Encode characteristic tuple as a string for compactness.

    Parameters:
    -----------
    my_tuple: Iterable
        The 0-1 tuple encoding membership in the subset
    num_terms: int (positive)
        the number of terms in your set of items
    """
    if len(my_tuple) != num_terms:
        raise ValueError('Length of tuple incorrect.')
    return ''.join([str(j) for j in my_tuple])


def encode_seq_to_str(short_list, items):
    """Do both of the prior functions in one step.

    Parameters:
    -----------
    short_list: Iterable
       The set of items in the subset of choice.
    items: Iterable
       the iterable giving you the items.
    """
    num_terms = len(items)
    output_list = [0 for j in range(num_terms)]
    for j in short_list:
        for pair in enumerate(items):
            if pair[1] == j:
                output_list[pair[0]] = 1
    return ''.join([str(j) for j in output_list])


def encode_str_to_int(my_str, num_terms):
    """Return an integer [for indexing] corresponding
    to the characteristic list.

    Parameters:
    -----------
    my_str: string
        The bit-string encoding membership in the subset
    num_terms: int (positive)
        the number of terms in your set of items
    """
    if len(my_str) != num_terms:
        raise ValueError('Length of string incorrect.')
    return int(my_str, 2)


def decode_int_to_str(code_int, num_terms):
    """Return the binary string corresponding to the
    code-integer.

    Parameters:
    -----------
    code_int: int
        The int whose binary representation encodes the subset.
    num_terms: int (positive)
        the number of terms in your set of items
    """
    return f'{code_int:0{num_terms}b}'


def decode_str_to_bin_tuple(my_str, num_terms):
    """Return 0-1 binary string to 0-1 binary tuple.

    Parameters:
    -----------
    my_str: string
        The bit-string encoding membership in the subset
    num_terms: int (positive)
        the number of terms in your set of items
    """
    if len(my_str) != num_terms:
        raise ValueError('Length of tuple incorrect.')
    return tuple([int(j) for j in my_str])


def decode_bin_tuple_as_seq(my_tuple, items):
    """Decode binary tuple as the sequence of elements
    it represents.

    Parameters:
    -----------
    my_tuple: Iterable
        The 0-1 tuple encoding membership in the subset
    items: Iterable
       the iterable giving you the items.
    """
    num_terms = len(items)
    if len(my_tuple) != num_terms:
        raise ValueError("Not the right length of list.")
    output = []
    for pair in enumerate(my_tuple):
        if pair[1]:
            output.append(items[pair[0]])
    return tuple(output)


def decode_str_to_seq(my_str, items):
    """Do both of the previous functions in the same step.

    Parameters:
    -----------
    my_str: string
        The bit-string encoding membership in the subset
    items: Iterable
        the iterable giving you the items.
    """
    num_terms = len(items)
    if len(my_str) != num_terms:
        raise ValueError("Not the right length of list.")
    output = []
    for pair in enumerate(my_str):
        if pair[1] == '1':
            output.append(items[int(pair[0])])
    return tuple(output)


def dict_constructor_again(bin_str, prop=False):
    '''Given the binary string encoding a subset,
    make the dictionary for storage.

    Parameters
    -----------
    bin_str: string
       The 0-1 string encoding the subset
    prop: bool
       The indicator of whether or not the subset has the property.
    '''
    num_terms = len(bin_str)
    num_elts = bin_str.count('1')
    parents = []
    temp_tuple = decode_str_to_bin_tuple(bin_str, num_terms)
    for numbered_pair in enumerate(temp_tuple):
        if not numbered_pair[1]:  # missing term
            temp_list = list(temp_tuple)
            temp_list[numbered_pair[0]] = 1
            parents.append(encode_str_to_int(
                encode_bin_tuple_as_str(temp_list, num_terms),
                num_terms)
                )
    return {
            "bin_str": bin_str,
            "num_elts": num_elts,
            "parents": parents,
            "property": prop
    }


class BinSubsetGraphSparseAgain():
    """
    Get minimally-labeled subset system, with only 1-2 layers at a time to
    avoid overloading space.  Use binary strings for storage to save space.

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
            my_str = decode_int_to_str(j, self.n)
            num_elts = my_str.count('1')
            # build only current layer and connections
            if num_elts == start_layer:
                self.subset_list.append(dict_constructor_again(
                    my_str, False
                    ))
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
            my_ind = encode_str_to_int(
                encode_seq_to_str(valid, self.items),
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
                            self.subset_list[parent] = dict_constructor_again(
                                decode_int_to_str(parent, self.n),
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
            my_str = decode_int_to_str(j, self.n)
            num_terms = my_str.count('1')
            # build only current layer and connections
            if num_terms == cur_layer:
                self.subset_list.append(dict_constructor_again(my_str, False))
            else:  # still need a (falsy) entry to keep the counting straight
                self.subset_list.append(False)
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
