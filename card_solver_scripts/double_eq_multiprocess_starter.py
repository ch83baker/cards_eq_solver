'''Find all (indices of) basic solution sets for the desired cases.
Written as a script, not a class, to enable multiprocessing.'''
from sympy import symbols, Eq, Rational
from sympy.combinatorics import SymmetricGroup, Permutation, PermutationGroup
from sympy.functions.combinatorial.numbers import nC
from itertools import combinations
import concurrent.futures
from pathlib import Path
import csv
import time

'''Put all options at the top for convenience,
with cross-references as needed.'''
# deck_type options: 'single', 'sample', 'like_sample', 'full_sample',
# 'opp', 'three', 'full'
deck_type = 'single'  # see line 41
# short_long_mix options: 'short_short', 'short_long', 'long_short',
# 'long_long'
# in practice, long_short has slightly better performance than short_long
short_long_mix = 'short_short'  # see line 74
# is_timing options: True, False
is_timing = True  # see line 232

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
two_black_suits_longer_sample = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
                                 6, 6, 7, 7, 8, 8, 9, 9, 10, 10]
four_suits_sample = [-5, -5, -4, -4, -3, -3, -2, -2, -1, -1,
                     1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

'''deck_type relevant here.'''
my_deck = None
if deck_type == 'single':
    my_deck = black_suit
elif deck_type == 'sample':
    my_deck = two_black_suits_sample
elif deck_type == 'like_sample':
    my_deck = two_black_suits_longer_sample
elif deck_type == 'full_sample':
    my_deck = four_suits_sample
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


# set equations and minimal permutations
slots = symbols('x:8')
short_eq_start = Eq(slots[0] + slots[1], slots[2])
short_eq_after_short = Eq(slots[3] + slots[4], slots[5])
short_eq_after_long = Eq(slots[4] + slots[5], slots[6])
long_eq_start = Eq(slots[0] + slots[1] + slots[2], slots[3])
long_eq_after_short = Eq(slots[3] + slots[4] + slots[5], slots[6])
long_eq_after_long = Eq(slots[4] + slots[5] + slots[6], slots[7])

'''short_long_mix choice relevant here.'''
my_n = 0
my_first_eq = None
my_second_eq = None
my_right_coset_reps = None
if short_long_mix == 'short_short':
    my_n = 6
    my_first_eq = short_eq_start
    my_second_eq = short_eq_after_short
    S6 = SymmetricGroup(6)
    # symmetries of first equation
    p1 = Permutation([1, 0, 2, 3, 4, 5])
    # symmetries of second equation
    p2 = Permutation([0, 1, 2, 4, 3, 5])
    # symmetry of trading equations
    p3 = Permutation([3, 4, 5, 0, 1, 2])
    eqs_stabilizer = PermutationGroup(p1, p2, p3)
    my_right_coset_reps = S6.coset_transversal(eqs_stabilizer)
elif short_long_mix == 'short_long':
    my_n = 7
    my_first_eq = short_eq_start  # or long_eq_start with . . .
    my_second_eq = long_eq_after_short  # short_eq_after_long
    S7 = SymmetricGroup(7)
    # symmetries of short equation
    q1 = Permutation([1, 0, 2, 3, 4, 5, 6])
    # symmetries of long equation -- can use dihedral group for S3
    q2_1 = Permutation([0, 1, 2, 4, 5, 3, 6])
    q2_2 = Permutation([0, 1, 2, 4, 3, 5, 6])
    eqs_stabilizer = PermutationGroup(q1, q2_1, q2_2)
    my_right_coset_reps = S7.coset_transversal(eqs_stabilizer)
elif short_long_mix == 'long_short':
    # yes, this is just short_long reordered
    # I am curious if there is a performance difference
    my_n = 7
    my_first_eq = long_eq_start
    my_second_eq = short_eq_after_long
    S7 = SymmetricGroup(7)
    # symmetries of long_equation
    q1_1 = Permutation([1, 2, 0, 3, 4, 5, 6])
    q1_2 = Permutation([1, 0, 2, 3, 4, 5, 6])
    # symmetries of short equation
    q2 = Permutation([0, 1, 2, 3, 5, 4, 6])
    eqs_stabilizer = PermutationGroup(q1_1, q1_2, q2)
    my_right_coset_reps = S7.coset_transversal(eqs_stabilizer)
elif short_long_mix == 'long_long':
    my_n = 8
    my_first_eq = long_eq_start
    my_second_eq = long_eq_after_long
    S8 = SymmetricGroup(8)
    # symmetries of first long equation
    r1_1 = Permutation([1, 2, 0, 3, 4, 5, 6, 7])
    r1_2 = Permutation([1, 0, 2, 3, 4, 5, 6, 7])
    # symmetries of second long equation
    r2_1 = Permutation([0, 1, 2, 3, 5, 6, 4, 7])
    r2_2 = Permutation([0, 1, 2, 3, 5, 4, 6, 7])
    # symmetry of two like equations
    r3 = Permutation([4, 5, 6, 7, 0, 1, 2, 3])
    eqs_stabilizer = PermutationGroup(r1_1, r1_2,
                                      r2_1, r2_2,
                                      r3)
    my_right_coset_reps = S8.coset_transversal(eqs_stabilizer)
else:
    raise ValueError('Bad specification of equations.')

# initialize results listings:  too few cards are 0
basic_solutions = []


# original code
# retained for reference only
def given_list_checker(inds_selection):
    """
    Check if the given list has a selection that can be rearranged
    to solve the equation.

    Parameters
    -------------
    inds_selection: Iterable[int]
       The selection of indices of cards from which we attempt
       to find a solution.
    """
    if len(inds_selection) < my_n:
        raise ValueError("Tuple must be of length >= number of slots.!")
    vals_selection = [my_deck[j] for j in inds_selection]
    for combo in combinations(vals_selection, my_n):
        for permy in my_right_coset_reps:
            temp_dict = {
                slots[j]: permy(combo)[j] for j in range(my_n)
            }
            if my_first_eq.subs(temp_dict):
                if my_second_eq.subs(temp_dict):
                    return inds_selection  # truthy!
    return False


# since we only use it for minimum-size sets in 'starter',
# we rework to remove the redundant combination
def given_list_checker_min_size_only(inds_selection):
    """
    Check if the given list has a selection that can be rearranged
    to solve the equation.

    Parameters
    -------------
    inds_selection: Iterable[int]
        The selection of indices required to solve the problem.
    """
    if len(inds_selection) != my_n:
        raise ValueError("Tuple must be of length == number of variables.!")
    vals_selection = [my_deck[j] for j in inds_selection]
    for permy in my_right_coset_reps:
        temp_dict = {
            slots[j]: permy(vals_selection)[j] for j in range(my_n)
        }
        if my_first_eq.subs(temp_dict):
            if my_second_eq.subs(temp_dict):
                return inds_selection  # truthy!
    return False


def basic_solutions_calculator():
    '''Find all basic solutions, using multiprocessing.'''
    base_denom = nC(deck_size, my_n)
    base_num = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(
            given_list_checker_min_size_only,  # or given_list_checker
            combinations(my_inds, my_n),
            chunksize=base_denom//10
        ):
            if result:
                base_num += 1
                basic_solutions.append(set(result))
    return Rational(base_num, base_denom)  # ratio good subsets to all subsets


def basic_solutions_calculator_without_multiprocessing():
    '''Find all basic solutions, without using multiprocessing.'''
    base_denom = nC(deck_size, my_n)
    base_num = 0
    status_updates = True
    count = 0
    num_groups = 0
    status_group_size = max(base_denom//100, 100)
    for combo in combinations(my_inds, my_n):
        if given_list_checker(combo):
            base_num += 1
            basic_solutions.append(set(combo))
            if status_updates:
                count += 1
                if count >= status_group_size:
                    count += 1
                    print(f"Finished {num_groups} groups"
                          + f' of size {status_group_size}')
                    count = 0
    return Rational(base_num, base_denom)  # ratio good subsets to all subsets


'''is_timing relevant here.'''
if __name__ == '__main__':
    if is_timing:
        st = time.time()
    else:
        st = 0
    basic_solutions_calculator()
    if is_timing:
        et = time.time()
    else:
        et = 0
    elapsed = (et - st) / 60
    if elapsed > 0.1:
        print(f'Time elasped: {elapsed:.3f} minutes.')
    path = Path(f'../results/{deck_type}_2eq_{short_long_mix}_baseline.csv')
    path.touch()
    with open(path, 'w+', newline='') as basic_solutions_printout:
        base_writer = csv.writer(basic_solutions_printout, delimiter=',')
        base_writer.writerow(deck_type)
        base_writer.writerow(short_long_mix)
        for a_subset in basic_solutions:
            base_writer.writerow(a_subset)
