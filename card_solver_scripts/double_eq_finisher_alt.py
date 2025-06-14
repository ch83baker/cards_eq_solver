'''Assuming double_eq_multiprocess_starter has run,
find the counts of solving sets for all instance sizes,
using the subsets tree.'''
from sympy import Rational
from sympy.functions.combinatorial.numbers import nC
from pathlib import Path
import csv
from my_subset_graph_new import BinSubsetGraphSparse
from my_subset_graph_again import BinSubsetGraphSparseAgain
from time import time

'''Put all options at the top for convenience,
with cross-references as needed.'''
# deck_type options: 'single', 'sample', 'like_sample', 'full_sample',
# 'opp', 'three', 'full'
deck_type = 'opp'  # see line 40
# short_long_mix options: 'short_short', 'short_long', 'long_short',
# 'long_long'
short_long_mix = 'short_long'  # see line 64
# is_timing options: True, False
is_timing = True  # see line 114
# version options: 'Original', 'Again'
version = 'Again'  # see line 114

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
in_path = Path(f'./results/{deck_type}_2eq_{short_long_mix}_baseline.csv')
with open(in_path, 'r+', newline='') as pass_along:
    basic_solutions_reader = csv.reader(pass_along)
    for row in basic_solutions_reader:
        temp_list.append(row)
claimed_deck_type = ''.join(j for j in temp_list[0])
claimed_eq_type = ''.join(j for j in temp_list[1])
temp_list = temp_list[2:]
if claimed_deck_type != deck_type or claimed_eq_type != short_long_mix:
    raise ValueError('Reading the Wrong file.\n'
                     + f'current: {deck_type}, {short_long_mix}'
                     + f'new:{claimed_deck_type}, {claimed_eq_type}')
else:
    for text_list in temp_list:  # must convert back to int tuple
        basic_solutions.append(tuple([int(j) for j in text_list]))
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

'''is_timing, version relevant here.'''
if __name__ == '__main__':
    time_running_total = 0
    print("Setting up...")
    if is_timing:
        st = time()
    else:
        st = 0
    if version == 'Original':
        my_subsets_graph = BinSubsetGraphSparse(my_inds, my_n)
        my_subsets_graph.fill_in_property_at_current_layer(basic_solutions)
    elif version == 'Again':
        my_subsets_graph = BinSubsetGraphSparseAgain(my_inds, my_n)
        my_subsets_graph.fill_in_property_at_current_layer(basic_solutions)
    else:
        raise ValueError("Invalid version of sparse graph.")
    if is_timing:
        et = time()
    else:
        et = 0
    duration = (et - st)/60
    time_running_total += duration
    if duration > 0:
        print(f'Time elasped for setup: {duration:.3f} minutes.')
    for j in range(my_n + 1, last_layer + 1):
        print(j)
        if is_timing:
            st = time()
        else:
            st = 0
        if version == 'Original':
            my_subsets_graph.raise_layer_with_properties()
            cur_num, cur_denom, cur_frac = \
                my_subsets_graph.count_property_at_current_layer()
        elif version == "Again":
            my_subsets_graph.raise_layer_with_properties()
            cur_num, cur_denom, cur_frac = \
                my_subsets_graph.count_property_at_current_layer()
        else:
            raise ValueError("Invalid version of sparse graph.")
        my_nums.append((j, cur_num))
        my_denoms.append((j, cur_denom))
        my_results.append((j, cur_frac))
        if is_timing:
            et = time()
        else:
            et = 0
        duration = (et - st)/60
        time_running_total += duration
        if duration > 0:
            print(f'Time elasped for level {j}: {duration:.3f} minutes.')
    if is_timing:
        print(f'Total time elapsed: {time_running_total:.3f} minutes.')
    out_path = Path(f'./results/{deck_type}_2eq_{short_long_mix}_alt.txt')
    out_path.touch()
    with open(out_path, 'w+') as results_printer:
        print(deck_type, file=results_printer)
        print(short_long_mix, file=results_printer)
        for j in range(len(my_nums)):
            print(f'{my_results[j][0]:>2}, {my_results[j][1]}, '
                  + f'{my_nums[j][1]}, {my_denoms[j][1]}',
                  file=results_printer)
