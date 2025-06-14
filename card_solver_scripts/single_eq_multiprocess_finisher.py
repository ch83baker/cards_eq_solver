'''Assuming single_eq_multiprocess_starter has run,
find the counts of solving sets for all instance sizes.'''
from sympy import symbols, Eq, Rational
from sympy.combinatorics import SymmetricGroup, Permutation, PermutationGroup
from sympy.functions.combinatorial.numbers import nC
from itertools import combinations
import concurrent.futures
from time import time
from pathlib import Path
import csv

'''All options listed here for convenience.
Docstrings will note where they come back into play.'''
# deck_type options: 'single', 'sample', 'like', 'opp', 'three', 'full'
deck_type = 'single'  # see line 34 and following
# short_or_long options: 'short', 'long'
short_or_long = 'long'  # see line 58 and following
# is_timing options: True, False
is_timing = True  # see line 241 and following

# Initialize deck
black_suit = [j for j in range(1, 14)]
red_suit = [-j for j in range(1, 14)]
two_black_suits = black_suit + black_suit
two_black_suits.sort()
two_opp_suits = red_suit + black_suit
two_opp_suits.sort()
three_suits = black_suit + black_suit + red_suit
three_suits.sort()
full_deck = red_suit + red_suit + black_suit + black_suit
full_deck.sort()
two_black_suits_sample = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

'''deck_type choice enters into play here.'''
my_deck = None
if deck_type == 'single':
    my_deck = black_suit
elif deck_type == 'sample':
    my_deck = two_black_suits_sample
elif deck_type == 'like':
    my_deck = two_black_suits
elif deck_type == 'opp':
    my_deck = two_opp_suits
elif deck_type == 'three':
    my_deck = three_suits
elif deck_type == 'full':
    my_deck = full_deck
else:
    raise ValueError("Invalid deck type.")
deck_size = len(my_deck)
my_inds = [j for j in range(deck_size)]

# initialize equation and limited set of permutations
slots = symbols('x:4')
short_eq = Eq(slots[0] + slots[1], slots[2])
long_eq = Eq(slots[0] + slots[1] + slots[2], slots[3])

'''short_or_long choice relevant here.'''
my_n = 0
my_eq = None
my_right_coset_reps = None
if short_or_long == 'short':
    my_n = 3
    my_eq = short_eq
    S3 = SymmetricGroup(3)
    p1 = Permutation([1, 0, 2])
    the_stabilizer = PermutationGroup(p1)
    my_right_coset_reps = S3.coset_transversal(the_stabilizer)
elif short_or_long == 'long':
    my_n = 4
    my_eq = long_eq
    S4 = SymmetricGroup(4)
    # Dihedral group on triangle equivalent to S3
    q1_1 = Permutation([1, 0, 2, 3])
    q1_2 = Permutation([1, 2, 0, 3])
    the_stabilizer = PermutationGroup(q1_1, q1_2)
    my_right_coset_reps = S4.coset_transversal(the_stabilizer)
else:
    raise ValueError('Invalid equation choice.')

# initialize results listings:  too few cards are 0 probability
my_nums = [(j, 0) for j in range(my_n)]
my_denoms = [(j, 1) for j in range(my_n)]
my_results = [(j, Rational(0, 1)) for j in range(my_n)]
basic_solutions = []

# load basic_solutions
temp_list = []
in_path = Path(f'../results/{deck_type}_{short_or_long}_baseline.csv')
with open(in_path, 'r+', newline='') as pass_along:
    basic_solutions_reader = csv.reader(pass_along)
    for row in basic_solutions_reader:
        temp_list.append(row)
claimed_deck_type = ''.join(j for j in temp_list[0])
claimed_eq_type = ''.join(j for j in temp_list[1])
temp_list = temp_list[2:]
if claimed_deck_type != deck_type or claimed_eq_type != short_or_long:
    raise ValueError('Reading the Wrong file.\n'
                     + f'desired: {deck_type}, {short_or_long}\n'
                     + f'read:{claimed_deck_type}, {claimed_eq_type}')
else:
    for text_list in temp_list:  # must convert back to int
        basic_solutions.append(set([int(j) for j in text_list]))
# What if no solutions?
no_solutions_flag = False
if not basic_solutions:
    no_solutions_flag = True
# go ahead and add the basic_solutions level
base_denom = nC(deck_size, my_n)
if basic_solutions:
    my_nums.append((my_n, len(basic_solutions)))
    my_denoms.append((my_n, base_denom))
    my_results.append((my_n, Rational(len(basic_solutions), base_denom)))
else:
    my_nums.append((my_n, 0))
    my_denoms.append((my_n, base_denom))
    my_results.append((my_n, Rational(0, base_denom)))


def given_list_checker(inds_selection):
    """
    Check if the given list has a selection that can be rearranged
    to solve the equation.

    Parameters:
    -------------
    inds_selection: Iterable[int]
        the indices of the cards chosen
    """
    if len(inds_selection) < my_n:
        raise ValueError("Tuple must be of length >= number of slots.!")
    vals_selection = [my_deck[j] for j in inds_selection]
    for combo in combinations(vals_selection, my_n):
        for permy in my_right_coset_reps:
            temp_dict = {
                slots[j]: permy(combo)[j] for j in range(my_n)
            }
            if my_eq.subs(temp_dict):
                return inds_selection  # truthy!
    return False


def given_list_checker_basic_solutions(inds_selection):
    """
    Check if the given list has a selection that can be rearranged
    to solve the equation, by checking against the
    known solutions.

    Parameters:
    -------------
    inds_selection: Iterable[int]
        the indices of the cards chosen
    """
    if not basic_solutions:
        raise ValueError("basic_solutions is not propagating to processes!")
    temp_set = set(inds_selection)
    if len(temp_set) != len(inds_selection):
        raise ValueError(f"Duplicates in {inds_selection}")
    for sol_set in basic_solutions:
        if sol_set <= temp_set:
            return inds_selection  # truthy!
    return False


def subsets_counter(cardinality=my_n+1):
    '''Count how many subsets of a given cardinality satisfy the property.

    Parameters:
    cardinality: int (positive)
        The size of subsets to consider'''
    current_denom = nC(deck_size, cardinality)
    current_num = 0
    # check if already done!  If so, no need for more searches.
    # definitely assumes an upward-closed property
    already_done = False
    for result in my_results:
        if result[0] < cardinality and result[1] == 1:
            already_done = True
    if already_done:
        print(f'{cardinality} comes for free!')  # debug code
        current_num = current_denom
    elif no_solutions_flag:  # nothing to do!:
        current_num = 0
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for result in executor.map(
                given_list_checker_basic_solutions,
                combinations(my_inds, cardinality),
                chunksize=max(current_denom//8, 1)
            ):
                if result:
                    current_num += 1
    my_nums.append((cardinality, current_num))
    my_denoms.append((cardinality, current_denom))
    my_results.append((cardinality,
                       Rational(current_num, current_denom)))
    return Rational(current_num, current_denom)


def subsets_counter_no_multiprocess(cardinality=my_n+1):
    '''Count how many subsets of a given cardinality satisfy the property.

    Parameters:
    cardinality: int (positive)
        The size of subsets to consider'''
    current_denom = nC(deck_size, cardinality)
    current_num = 0
    # This option changes whether updates printed to standard output.
    status_updates = True
    count = 0
    num_groups = 0
    group_size = max(current_denom//50, 1000)
    # check if already done!  If so, no need for more searches.
    # definitely assumes an upward-closed property
    already_done = False
    for result in my_results:
        if result[0] < cardinality and result[1] == 1:
            already_done = True
    if already_done:
        print(f'{cardinality} comes for free!')  # debug code
        current_num = current_denom
    elif no_solutions_flag:  # nothing to do!:
        current_num = 0
    else:
        for combo in combinations(my_inds, cardinality):
            if given_list_checker_basic_solutions(combo):
                current_num += 1
            if status_updates:
                count += 1
                if count >= group_size:
                    num_groups += 1
                    print(f"Completed {num_groups} groups"
                          + f'of size {group_size}')
                    count = 0
    my_nums.append((cardinality, current_num))
    my_denoms.append((cardinality, current_denom))
    my_results.append((cardinality,
                       Rational(current_num, current_denom)))
    return Rational(current_num, current_denom)


'''is_timing takes on importance here.'''
if __name__ == '__main__':
    time_running_total = 0
    for j in range(my_n + 1, deck_size+1):
        print(j)
        if is_timing:
            st = time()
        else:
            st = 0
        # in practice, for 3-4 suits, the memory overhead
        # prevents worthwhile multiprocessing.
        if deck_size > 26:
            subsets_counter_no_multiprocess(j)
        else:
            subsets_counter(j)
        if is_timing:
            et = time()
        else:
            et = 0
        duration = (et - st)/60
        time_running_total += duration
        if duration >= 0.1:
            print(f'Time elasped for level {j}: {duration:.3f} minutes.')
    if is_timing:
        print(f'Total time elapsed: {time_running_total:.3f} minutes.')
    out_path = Path(f'../results/{deck_type}_{short_or_long}.txt')
    out_path.touch()
    with open(out_path, 'w+') as results_printer:
        print(deck_type, file=results_printer)
        print(short_or_long, file=results_printer)
        for j in range(len(my_nums)):
            print(f'{my_results[j][0]:>2}, {my_results[j][1]}, '
                  + f'{my_nums[j][1]}, {my_denoms[j][1]}',
                  file=results_printer)
