"""A class for checking a single equation."""
import sympy as sp
from sympy.combinatorics import SymmetricGroup, Permutation, PermutationGroup
from itertools import permutations, combinations
from warnings import warn


class SingleEqChecker():
    """A family of functions for finding subsets of a given set
    that satisfy a given equation.


    Parameters
    ----------
    var_count: int (positive)
        The number of variables used
    symbols_col:  Iterable[sympy.core.symbol.Symbol]
        The collection of symbols needed.  The user is responsible for ensuring
        that enough symbols for the equation are given, and that the symbols
        have all appropriate assumptions in-built.
    eq: sympy.core.relational.Eq
        The equation used.  Must use the symbols in symbols_col, and must not
        use more than var_count many symbols.
    inputs: Iterable[sympy.core.number.Number (or interpretable as such)]
        The collection of inputs from which we must find a solution.
        Repeats are allowed here.
        Note that the internal mechanisms immediately recast this as a tuple.
    """

    def __init__(self, var_count, symbols_col, eq, inputs):
        '''Initialize the data.'''
        self.var_count = var_count
        self.symbols_col = symbols_col
        self.eq = eq
        self.inputs = tuple(inputs)
        self.input_count = len(self.inputs)
        # for reporting our results to the subset-counting commands,
        # repeats would be destructive, so we track the indices
        self.input_indices = [j for j in range(self.input_count)]
        # containers for the various results
        self.basic_solutions = []
        self.nums = [(j, 0) for j in range(var_count)]
        self.denoms = [(j, 1) for j in range(var_count)]
        self.results = [(j, sp.Rational(0, 1)) for j in range(var_count)]
        self.single_layer_results = []
        self.single_layer = 0

    def _given_list_checker(self, short_list):
        '''Given a subset of the inputs,
        see if we can find a sub-subset satisfying the equation.

        Parameters
        ------------
        short_list: Iterable[sympy.core.number.Number (or castable as such)]
            The collection of inputs from which we must find a solution.
            Repeats are allowed here.
        '''
        if len(short_list) < self.var_count:
            raise ValueError(f"Tuple must be of length {self.var_count}!")
        for permy in permutations(short_list, self.var_count):
            temp_dict = {
                self.symbols_col[j]: permy[j] for j in range(self.var_count)
            }
            if self.eq.subs(temp_dict):
                return True
        return False

    def single_eq_tester_direct(self, midsize_len,
                                is_saved=False, reporting_type='ind',
                                status_updates=False, group_size=100):
        '''Check all subsets of the inputs of size midsize_len
        to see how many of them are solutions,
        by directly checking the equations.

        Parameters
        ------------
        midsize_len: int (positive)
            The size of subsets we wish to check.
        is_saved: bool, optional
            If False, we do not record which subsets are satisfying.
            If True, we do record which subsets are satisfying.
            Note that running another command will erase the results,
            so save them first!
        reporting_type: string  ('ind'=default, 'val'), optional
            No effect unless is_saved = True.
            If reporting_type is equal to 'ind', we save the collections
            of indices.
            If reporting_type is equal to 'val', we save the values themselves.
            Default is 'ind', because my subset-counting commands
            will break on repeated values.
        status_updates: bool, optional
            If set to True, will give status updates to the command line
            at the intervals specified by group_size.
        group_size: int (positive), optional
            No effect unless status_updates=True.
            Sets the interval at which status updates are given.
        '''
        if midsize_len > self.input_count or midsize_len < self.var_count:
            raise ValueError("Subset must be smaller than full set.")
        if reporting_type not in ('ind', 'val'):
            warn('Invalid Reporting type, will not save data.')
        # nC is the sympy function that counts combinations
        our_denom = sp.functions.combinatorial.numbers.nC(
            self.input_count, midsize_len
        )
        our_num = 0
        count = 0
        num_groups = 0
        self.single_layer = midsize_len
        self.single_layer_results = []
        for selection in combinations(self.input_indices, midsize_len):
            vals_selection = [self.inputs[j] for j in selection]
            if self._given_list_checker(vals_selection):
                our_num += 1
                if is_saved:
                    if reporting_type == 'ind':
                        self.single_layer_results.append(selection)
                    elif reporting_type == 'val':
                        self.single_layer_results.append(vals_selection)
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        self.nums.append((midsize_len, our_num))
        self.denoms.append((midsize_len, our_denom))
        result = sp.Rational(our_num, our_denom)
        self.results.append((midsize_len, result))
        return result

    def basic_solutions_calculator(self, status_updates=False,
                                   group_size=100):
        """Stores (indices of) basic solution sets.

        Parameters
        ----------
        status_updates: bool, optional
            If set to True, will give status updates to the command line
            at the intervals specified by group_size.
        group_size: int (positive), optional
            No effect unless status_updates=True.
            Sets the interval at which status updates are given.
        '''"""
        self.single_eq_tester_direct(self.var_count,
                                     True, 'ind',
                                     status_updates, group_size)
        for comb in self.single_layer_results:
            self.basic_solutions.append(set(comb))
        self.basic_solutions = tuple(self.basic_solutions)
        return self.basic_solutions

    def _given_list_checker_from_basic(self, short_list):
        '''Given a subset of the inputs,
        see if we can find a solving sub-subset
        by checking against the basic solutions.

        Parameters
        ------------
        short_list: Iterable[sympy.core.number.Number (or castable as such)]
            The collection of inputs from which we must find a solution.
            Repeats are allowed here.
        '''
        if len(short_list) < self.var_count:
            raise ValueError(f"Tuple must be of length >= {self.var_count}!")
        temp_set = set(short_list)
        for sol_set in self.basic_solutions:
            if sol_set <= temp_set:
                return True
        return False

    def single_eq_tester_from_basic(self, midsize_len,
                                    is_saved=False, reporting_type='ind',
                                    status_updates=False, group_size=100):
        '''Check all subsets of the inputs of size midsize_len
        to see how many of them are solutions,
        by checking against the basic solutions.

        Parameters
        ------------
        midsize_len: int (positive)
            The size of subsets we wish to check.
        is_saved: bool, optional
            If False, we do not record which subsets are satisfying.
            If True, we do record which subsets are satisfying.
            Note that running another command will erase the results,
            so save them first!
        reporting_type: string  ('ind'=default, 'val'), optional
            No effect unless is_saved = True.
            If reporting_type is equal to 'ind', we save the collections
            of indices.
            If reporting_type is equal to 'val', we save the values themselves.
            Default is 'ind', because my subset-counting commands
            will break on the repeats.
        status_updates: bool, optional
            If set to True, will give status updates to the command line
            at the intervals specified by group_size.
        group_size: int (positive), optional
            No effect unless status_updates=True.
            Sets the interval at which status updates are given.
        '''
        if midsize_len > self.input_count or midsize_len < self.var_count:
            raise ValueError("Subset must be smaller than full set.")
        # if no baseline, cannot proceed, use standard method.
        if not self.basic_solutions:
            warn('Basic solutions not stored, so must '
                 + 'revert to standard method.')
            return self.single_eq_tester_direct(midsize_len,
                                                is_saved, reporting_type,
                                                status_updates, group_size)
        our_denom = sp.functions.combinatorial.numbers.nC(
            self.input_count, midsize_len
        )
        our_num = 0
        count = 0
        num_groups = 0
        self.single_layer = midsize_len
        self.single_layer_results = []
        # we search from inds since the basic solutions are stored in indices
        for selection in combinations(self.input_indices, midsize_len):
            if self._given_list_checker_from_basic(selection):
                our_num += 1
                if is_saved:
                    if reporting_type == 'ind':
                        self.single_layer_results.append(selection)
                    elif reporting_type == 'val':
                        self.single_layer_results.append(
                            [self.inputs[j] for j in
                             selection]
                        )
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {group_size}')
                    count = 0
        self.nums.append((midsize_len, our_num))
        self.denoms.append((midsize_len, our_denom))
        result = sp.Rational(our_num, our_denom)
        self.results.append((midsize_len, result))
        return result


class SingleEqCheckerWithCosets(SingleEqChecker):
    """A family of functions for testing subsets of a given set for solving
    an equation, using a reduced set of permutations coming from symmetries
    of the variables in the equation.

    The user is responsible for identifying:
    1.  Whether or not their equation has symmetric variables.
    2.  The kernel of the permutation-group action on the variables list.
    3.  The appropriate representatives of the (right) cosets of the kernel
        in the appropriate symmetry group (as created by, for example,
        Sn.coset_transversal(K), where Sn is the (permutation) symmetric group
        and K is the kernel.)

    If you are uncertain about how to encode your case, please use the original
    SingleEqChecker class.

    Examples of this setup are shown in the subclass
    SingleEqCheckerCommonCases below.

    Parameters
    ----------
    var_count: int (positive)
        The number of variables used
    symbols_col:  Iterable[sympy.core.symbol.Symbol]
        The collection of symbols needed.  The user is responsible for ensuring
        that enough symbols for the equation are given, and that the symbols
        have all appropriate assumptions in-built.
    eq: sympy.core.relational.Eq
        The equation used.  Must use the symbols in symbols_col, and must not
        use more than var_count many symbols.
    r_coset_reps: Iterable[sympy.combinatorics.permutations.Permutation]
        The list of representatives of each right coset of the kernel
        of the permutation-group action on the variables.
    inputs: Iterable[sympy.core.number.Number (or interpretable as such)]
        The collection of inputs from which we must find a solution.
        Repeats are allowed here.
        Note that the internal mechanisms immediately recast this as a tuple.
    """

    def __init__(self, var_count, symbols_col, eq,
                 r_coset_reps, inputs):
        """Initialize the function."""
        super().__init__(
            var_count, symbols_col, eq, inputs
        )
        self.r_coset_reps = r_coset_reps

    def _given_list_checker(self, short_list):
        '''Given a subset of the inputs,
           see if we can find a sub-subset satisfying the equation.

        Parameters
        ------------
        short_list: Iterable[sympy.core.number.Number (or castable as such)]
            The collection of inputs from which we must find a solution.
            Repeats are allowed here.
        '''
        if len(short_list) < self.var_count:
            raise ValueError(f"Tuple must be of length {self.var_count}!")
        for combo in combinations(short_list, self.var_count):
            for perm in self.r_coset_reps:
                temp_dict = {
                    self.symbols_col[j]: perm(combo)[j]
                    for j in range(self.var_count)
                }
                if self.eq.subs(temp_dict):
                    return True
        return False


class SingleEqCheckerCommonCases(SingleEqCheckerWithCosets):
    """A family of common cases for single-equation setups, both
    as convenience for myself and an illustration on how to set up the
    permutation groups.

    Parameters
    ----------
    eq_type: string ('short', 'long', 'very long', 'mixed ops')
        The type of equation.
        'short' means x0 + x1 = x2
        'long' means x0 + x1 + x2 = x3
        'very long' means x0 + x1 + x2 + x3 + x4 = x5
        'mixed ops' means x0 + x1 = x2 * x3
    inputs: Iterable[sympy.core.number.Number (or interpretable as such)]
        The collection of inputs from which we must find a solution.
        Repeats are allowed here.
        Note that the internal mechanisms immediately recast this as a tuple.
    """

    def __init__(self, eq_type, inputs):
        if eq_type == 'short':  # i.e., x0 + x1 = x2
            var_count = 3
            symbols_col = sp.symbols('x:3')
            eq = sp.Eq(symbols_col[0] + symbols_col[1], symbols_col[2])
            S3 = SymmetricGroup(3)
            # permutation of flipping the first two symbols,
            # generated by the transposition of the first two terms
            # remember that sympy starts indexing from 0
            p1 = Permutation([1, 0, 2])
            K = PermutationGroup(p1)
            r_coset_reps = S3.coset_transversal(K)
        elif eq_type == 'long':  # i.e., x0 + x1 + x2 = x3
            var_count = 4
            symbols_col = sp.symbols('x:4')
            eq = sp.Eq(symbols_col[0] + symbols_col[1] + symbols_col[2],
                       symbols_col[3])
            S4 = SymmetricGroup(4)
            # can freely permute the first three variables, x0-2.
            # We generate from a transposition and a rotation
            # on those first three variables.
            p1 = Permutation([1, 0, 2, 3])
            p2 = Permutation([1, 2, 0, 3])
            K = PermutationGroup(p1, p2)
            r_coset_reps = S4.coset_transversal(K)
        elif eq_type == 'very long':  # i.e., $\sum_{k = 0}^4 x_k = x_5$
            var_count = 6
            symbols_col = sp.symbols('x:6')
            eq = sp.Eq(symbols_col[0] + symbols_col[1] + symbols_col[2]
                       + symbols_col[3] + symbols_col[4],
                       symbols_col[5])
            S6 = SymmetricGroup(6)
            # We generate from a transposition of the first two variables
            # and a cycle on the first 5 variables, leaving x5 alone.
            p1 = Permutation([1, 0, 2, 3, 4, 5])
            p2 = Permutation([1, 2, 3, 4, 0, 5])
            K = PermutationGroup(p1, p2)
            r_coset_reps = S6.coset_transversal(K)
        elif eq_type == 'mixed ops':  # i.e., x_0 + x_1 = x_2 * x_3
            var_count = 4
            symbols_col = sp.symbols('x:4')
            eq = sp.Eq(symbols_col[0] + symbols_col[1],
                       symbols_col[2] * symbols_col[3])
            S4 = SymmetricGroup(4)
            # left-side symmetry
            p1 = Permutation([1, 0, 2, 3])
            # right-side symmetry
            p2 = Permutation([0, 1, 3, 2])
            K = PermutationGroup(p1, p2)
            r_coset_reps = S4.coset_transversal(K)
        else:
            raise ValueError(
                f'Equation type {eq_type} is not on our list of valid types:\n'
                + '("short", "long", "very long", "mixed ops")'
            )
        super().__init__(var_count, symbols_col, eq, r_coset_reps, inputs)
