import sympy as sp
from sympy.combinatorics import Permutation, PermutationGroup, SymmetricGroup
from itertools import permutations, combinations
from warnings import warn


class DoubleEqChecker():
    """A family of functions for finding subsets of a given set
    that satisfy a given pair of equations.

    Parameters
    ----------
    var_count: int (positive)
        The number of variables used
    symbols_col:  Iterable[sympy.core.symbol.Symbol]
        The collection of symbols needed.  The user is responsible for ensuring
        that enough symbols for the equation are given, and that the symbols
        have all appropriate assumptions in-built.
    first_eq: sympy.core.relational.Eq
        The first equation.  Must use the symbols in symbols_col, and must not
        use more than var_count many symbols.
    second_eq: sympy.core.relational.Eq
        The second equation.  Must use the symbols in symbols_col, and must not
        use more than var_count many symbols.
    inputs: Iterable[sympy.core.number.Number (or interpretable as such)]
        The collection of inputs from which we must find a solution.
        Repeats are allowed here.
        Note that the internal mechanisms immediately recast this as a tuple.
    """

    def __init__(self, var_count, symbols_col, first_eq, second_eq,
                 inputs):
        """Initialize the function."""
        self.var_count = var_count
        self.symbols_col = symbols_col
        self.first_eq = first_eq
        self.second_eq = second_eq
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
        see if we can find a sub-subset satisfying the equations.'''
        if len(short_list) < self.var_count:
            raise ValueError(f"Tuple must be of length {self.var_count}!")
        for permy in permutations(short_list, self.var_count):
            temp_dict = {
                self.symbols_col[j]: permy[j] for j in range(self.var_count)
            }
            if self.first_eq.subs(temp_dict):
                if self.second_eq.subs(temp_dict):
                    return True
        return False

    def double_eq_tester_direct(self, midsize_len,
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
        if reporting_type not in ('ind', 'val'):
            warn('Invalid Reporting type, will not save data.')
        # nC is the sympy combinations-counting function
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
        """Stores (indices of) basic solution sets."""
        self.double_eq_tester_direct(self.var_count,
                                     True, 'ind',
                                     status_updates, group_size)
        for comb in self.single_layer_results:
            self.basic_solutions.append(set(comb))
        self.basic_solutions = tuple(self.basic_solutions)
        return self.basic_solutions

    def _given_list_checker_from_basic(self, short_list):
        '''Loop through the basic solutions to see if we have a super-set
        of a good solution.'''
        if len(short_list) < self.var_count:
            raise ValueError(f"Tuple must be of length >= {self.var_count}!")
        temp_set = set(short_list)
        for sol_set in self.basic_solutions:
            if sol_set <= temp_set:
                return True
        return False

    def double_eq_tester_from_basic(self, midsize_len,
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
        # if no basic solutions, cannot proceed, use standard method.
        if not self.basic_solutions:
            warn('Basic solutions not stored, so must '
                 + 'revert to standard method.')
            return self.double_eq_tester_direct(midsize_len,
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
        # we search from inds since the basic solutions are stored as indices
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


class DoubleEqCheckerWithCosets(DoubleEqChecker):
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

    def __init__(self, var_count, symbols_col, first_eq, second_eq,
                 r_coset_reps, inputs):
        """Initialize the function."""
        super().__init__(
            var_count, symbols_col, first_eq, second_eq, inputs
        )
        self.r_coset_reps = r_coset_reps

    def _given_list_checker(self, short_list):
        if len(short_list) < self.var_count:
            raise ValueError("Tuple must be of length n!")
        for combo in combinations(short_list, self.var_count):
            for perm in self.r_coset_reps:
                temp_dict = {
                    self.symbols_col[j]: perm(combo)[j]
                    for j in range(self.var_count)
                }
                if self.first_eq.subs(temp_dict):
                    if self.second_eq.subs(temp_dict):
                        return True
        return False


class DoubleEqCheckerCommonCases(DoubleEqCheckerWithCosets):
    """A family of common cases for double-equation setups, both
    as convenience for my common cases, and an illustration on how
    to set up the permutation groups.

    Parameters
    ----------
    eq_type: string ('short-short', 'long-short', 'long-long')
        The type of equation.
        'short-short' means 2 equations of the form x + y = z
        'long-short' means 1 equation of the form a + b + c = d,
        followed by one of the form x + y = z
        'long-long' means 2 equations of the form a + b + c = d.
    inputs: Iterable[sympy.core.number.Number (or interpretable as such)]
        The collection of inputs from which we must find a solution.
        Repeats are allowed here.
        Note that the internal mechanisms immediately recast this as a tuple.
    """
    def __init__(self, eq_type, inputs):
        """Initialize."""
        if eq_type == 'short-short':
            var_count = 6
            symbols_col = sp.symbols('x:6')
            first_eq = sp.Eq(symbols_col[0] + symbols_col[1], symbols_col[2])
            second_eq = sp.Eq(symbols_col[3] + symbols_col[4], symbols_col[5])
            S6 = SymmetricGroup(6)
            # symmetries of first equation
            p1 = Permutation([1, 0, 2, 3, 4, 5])
            # symmetries of second equation
            p2 = Permutation([0, 1, 2, 4, 3, 5])
            # symmetry of trading equations
            p3 = Permutation([3, 4, 5, 0, 1, 2])
            K = PermutationGroup(p1, p2, p3)
            r_coset_reps = S6.coset_transversal(K)
        elif eq_type == 'long-short':
            var_count = 7
            symbols_col = sp.symbols('x:7')
            first_eq = sp.Eq(symbols_col[0] + symbols_col[1] + symbols_col[2],
                             symbols_col[3])
            second_eq = sp.Eq(symbols_col[4] + symbols_col[5], symbols_col[6])
            S7 = SymmetricGroup(7)
            # symmetries of long_equation
            # can generate with 3-cycle and transposition
            q1_1 = Permutation([1, 2, 0, 3, 4, 5, 6])
            q1_2 = Permutation([1, 0, 2, 3, 4, 5, 6])
            # symmetries of short equation
            q2 = Permutation([0, 1, 2, 3, 5, 4, 6])
            K = PermutationGroup(q1_1, q1_2, q2)
            r_coset_reps = S7.coset_transversal(K)
        elif eq_type == 'long-long':
            var_count = 8
            symbols_col = sp.symbols('x:8')
            first_eq = sp.Eq(symbols_col[0] + symbols_col[1] + symbols_col[2],
                             symbols_col[3])
            second_eq = sp.Eq(symbols_col[4] + symbols_col[5] + symbols_col[6],
                              symbols_col[7])
            S8 = SymmetricGroup(8)
            # symmetries of first long equation
            r1_1 = Permutation([1, 2, 0, 3, 4, 5, 6, 7])
            r1_2 = Permutation([1, 0, 2, 3, 4, 5, 6, 7])
            # symmetries of second long equation
            r2_1 = Permutation([0, 1, 2, 3, 5, 6, 4, 7])
            r2_2 = Permutation([0, 1, 2, 3, 5, 4, 6, 7])
            # symmetry of two like equations
            r3 = Permutation([4, 5, 6, 7, 0, 1, 2, 3])
            K = PermutationGroup(r1_1, r1_2, r2_1, r2_2, r3)
            r_coset_reps = S8.coset_transversal(K)
        else:
            raise ValueError(
                f'Equation type {eq_type} is not on our list of valid types:\n'
                + '("short-short", "long-short", "long-long")'
            )
        super().__init__(var_count, symbols_col, first_eq, second_eq,
                         r_coset_reps, inputs)
