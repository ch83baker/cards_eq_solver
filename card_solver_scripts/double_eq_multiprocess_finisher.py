'''Assuming double_eq_multiprocess_starter has run,
find the counts of solving sets for all instance sizes,
using multiprocessing.'''
from sympy import Rational
from sympy.functions.combinatorial.numbers import nC
from itertools import combinations
import concurrent.futures
from pathlib import Path
import csv
from time import time

'''Put all options at the top for convenience,
with cross-references as needed.'''
# deck_type options: 'single', 'sample', 'like_sample', 'full_sample',
# 'opp', 'three', 'full'
deck_type = 'opp'  # see line 39
# short_long_mix options: 'short_short', 'short_long', 'long_short',
# 'long_long'
short_long_mix = 'short_long'  # see line 62
# is_timing options: True, False
is_timing = True  # see line 212

# Initialize deck
black_suit = [j for j in range(1, 14)]
red_suit = [-j for j in range(1, 14)]
two_black_suits = black_suit + black_suit
two_black_suits.sort()
two_opp_suits = red_suit + black_suit
two_opp_suits.sort()
full_deck = red_suit + red_suit + black_suit + black_suit
full_deck.sort()
two_black_suits_sample = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
two_black_suits_longer_sample = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
                                 6, 6, 7, 7, 8, 8, 9, 9, 10, 10]
four_suits_sample = [-5, -5, -4, -4, -3, -3, -2, -2, -1, -1,
                     1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

'''deck_type relevant here'''
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
elif deck_type == 'full':
    my_deck = full_deck
else:
    raise ValueError("Invalid deck type.")
deck_size = len(my_deck)
my_inds = [j for j in range(deck_size)]


# set number of variables
# equations looked at only in 'starter'
'''short_long_mix relevant here.'''
my_n = 0
if short_long_mix == 'short_short':
    my_n = 6
elif short_long_mix == 'short_long' or short_long_mix == 'long_short':
    my_n = 7
elif short_long_mix == 'long_long':
    my_n = 8
else:
    raise ValueError('Bad specification of equations.')

# initialize results listings:  too few cards are 0
my_nums = [(j, 0) for j in range(my_n)]
my_denoms = [(j, 1) for j in range(my_n)]
my_results = [(j, Rational(0, 1)) for j in range(my_n)]
basic_solutions = []
last_layer = deck_size  # can adjust manually if desired

# load basic_solutions
temp_list = []
in_path = Path(f'../results/{deck_type}_2eq_{short_long_mix}_baseline.csv')
with open(in_path, 'r+', newline='') as pass_along:
    basic_solutions_reader = csv.reader(pass_along)
    for row in basic_solutions_reader:
        temp_list.append(row)
claimed_deck_type = ''.join(j for j in temp_list[0])
claimed_eq_type = ''.join(j for j in temp_list[1])
temp_list = temp_list[2:]
if claimed_deck_type != deck_type or claimed_eq_type != short_long_mix:
    raise ValueError('Reading the Wrong file.\n'
                     + f'desired: {deck_type}, {short_long_mix} \n'
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
                chunksize=max(current_denom//10, 1)
            ):
                if result:
                    current_num += 1
    my_nums.append((cardinality, current_num))
    my_denoms.append((cardinality, current_denom))
    my_results.append((cardinality,
                       Rational(current_num, current_denom)))
    return Rational(current_num, current_denom)


def subsets_counter_no_multiprocess(cardinality=my_n+1):
    '''Count how many subsets of a given cardinality satisfy the property,
    without multiprocessing
    Parameters:
    cardinality: int (positive)
        The size of subsets to consider'''
    current_denom = nC(deck_size, cardinality)
    current_num = 0
    # This option changes whether updates printed to standard output.
    status_updates = False
    # check if already done!  If so, no need for more searches.
    # definitely assumes an upward-closed property
    already_done = False
    for result in my_results:
        if result[0] < cardinality and result[1] == 1:
            already_done = True
    if already_done:
        print(f'{cardinality} comes for free!')  # debug code
        current_num = current_denom
    elif no_solutions_flag:
        current_num = 0
    else:
        count = 0
        num_groups = 0
        status_group_size = current_denom//100
        for combo in combinations(my_inds, cardinality):
            if given_list_checker_basic_solutions(combo):
                current_num += 1
                if status_updates:
                    count += 1
                    if count >= status_group_size:
                        num_groups += 1
                        print(f"Finished {num_groups} groups"
                              + f' of size {status_group_size}')
                        count = 0
    my_nums.append((cardinality, current_num))
    my_denoms.append((cardinality, current_denom))
    my_results.append((cardinality,
                       Rational(current_num, current_denom)))
    return Rational(current_num, current_denom)


'''is_timing relevant here.'''
if __name__ == '__main__':
    time_running_total = 0
    for j in range(my_n + 1, last_layer + 1):
        print(j)
        if is_timing:
            st = time()
        else:
            st = 0
        subsets_counter(j)
        if is_timing:
            et = time()
        else:
            et = 0
        duration = (et - st)/60
        time_running_total += duration
        if duration > 0.1:
            print(f'Time elasped for level {j}: {duration:.3f} minutes.')
    if is_timing:
        print(f'Total time elapsed: {time_running_total:.3f} minutes.')
    out_path = Path(f'../results/{deck_type}_2eq_{short_long_mix}.txt')
    out_path.touch()
    with open(out_path, 'w+') as results_printer:
        print(deck_type, file=results_printer)
        print(short_long_mix, file=results_printer)
        for j in range(len(my_nums)):
            print(f'{my_results[j][0]:>2}, {my_results[j][1]}, '
                  + f'{my_nums[j][1]}, {my_denoms[j][1]}',
                  file=results_printer)
