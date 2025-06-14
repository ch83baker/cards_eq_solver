'''Desired cases of SingleEq.py, put in a module to enable multiprocessing.'''
from sympy import IndexedBase, Eq, Rational
from sympy.combinatorics import SymmetricGroup, Permutation, PermutationGroup
from sympy.functions.combinatorial.numbers import nC
from itertools import combinations
import concurrent.futures
from pathlib import Path
import csv

'''All options set here, for convenience.
Will cross-reference with start of their relevance below.'''
# deck_type options: 'single', 'sample', 'like', 'opp', 'three', 'full'
deck_type = 'three'  # see line 30 and following
# short_or_long options: 'short', 'long'
short_or_long = 'long'  # see line 55 and following

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

'''deck_type choice relevant here.'''
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
slots = IndexedBase('x')
short_eq = Eq(slots[0] + slots[1], slots[2])
long_eq = Eq(slots[0] + slots[1] + slots[2], slots[3])


'''short_or_long choice relevant here'''
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


# initialize results listings:  too few cards are 0
my_nums = [(j, 0) for j in range(my_n)]
my_denoms = [(j, nC(my_n, j)) for j in range(my_n)]
my_results = [(j, Rational(0, 1)) for j in range(my_n)]
basic_solutions = []


def given_list_checker(inds_selection):
    """
    Check if the given list has a selection that can be rearranged
    to solve the equation.

    Parameters:
    -------------
    inds_selection: the indices of the cards chosen
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


def basic_solutions_calculator():
    '''Find all basic solutions, using multiprocessing.'''
    base_denom = nC(deck_size, my_n)
    base_num = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for result in executor.map(
            given_list_checker,
            combinations(my_inds, my_n),
            chunksize=base_denom//8
        ):
            if result:
                base_num += 1
                basic_solutions.append(set(result))
    my_nums.append((my_n, base_num))
    my_denoms.append((my_n, base_denom))
    my_results.append((my_n, Rational(base_num, base_denom)))
    return Rational(base_num, base_denom)


if __name__ == '__main__':
    basic_solutions_calculator()
    path = Path(f'../results/{deck_type}_{short_or_long}_baseline.csv')
    path.touch()
    with open(path, 'w+', newline='') as basic_solutions_printout:
        base_writer = csv.writer(basic_solutions_printout, delimiter=',')
        base_writer.writerow(deck_type)
        base_writer.writerow(short_or_long)
        for a_subset in basic_solutions:
            base_writer.writerow(a_subset)
