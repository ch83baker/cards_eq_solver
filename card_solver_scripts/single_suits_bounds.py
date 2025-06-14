'''Calculate the lower-bound probabilities for the groupings of terms.'''
from sympy import Rational, prod
from sympy.functions.combinatorial.numbers import nC
from itertools import permutations
from pathlib import Path

# first, find the probability of choosing s spades,
# c clubs, d diamonds, and h hearts
# in a selection of selection_size cards


def types_probs(counts, selection_size):
    if len(counts) != 4:
        raise ValueError('Not the right number of suits!')
    elif sum(counts) != selection_size:
        raise ValueError('Not the right number of cards!')
    return Rational(
        prod([nC(13, j) for j in counts]), nC(52, selection_size)
    )


# upload the solution probabilities for single-suit equations,
# starting with single-equation


subset_1suit_1eq_probs = {
    'short': [0 for j in range(14)],
    'long': [0 for j in range(14)]
}
for short_long_choice in {'short', 'long'}:
    in_path = Path(f'./results/single_{short_long_choice}.txt')
    with open(in_path, 'r') as reader:
        lines = reader.readlines()
    if lines[0] != 'single\n' or lines[1] != short_long_choice + '\n':
        raise ValueError('The file I read in has the wrong header!')
    lines = lines[2:]
    str_lists = []
    for line in lines:
        str_lists.append(line.replace('\n', '').split(', '))
    for j in range(14):
        subset_1suit_1eq_probs[short_long_choice][j] = Rational(
            int(str_lists[j][2]), int(str_lists[j][3])
        )

# now for 1-suit, 2 equations

subset_1suit_2eq_probs = {
    'short_short': [0 for j in range(14)],
    'short_long': [0 for j in range(14)],
    'long_long': [0 for j in range(14)]
}

for short_long_mix in ('short_short', 'short_long', 'long_long'):
    # I happened to run the non-'alt' version for all cases
    # If you are running this code, feel free to try both alt and non-alt
    # versions.
    in_path = Path(f'./results/single_2eq_{short_long_mix}.txt')
    with open(in_path, 'r+') as reader:
        lines = reader.readlines()
    if lines[0] != 'single\n' or lines[1] != short_long_mix + '\n':
        raise ValueError('Read-in file has wrong header!')
    lines = lines[2:]
    str_lists = []
    for line in lines:
        str_lists.append(line.replace('\n', '').split(', '))
    for j in range(14):
        subset_1suit_2eq_probs[short_long_mix][j] = Rational(
            int(str_lists[j][2]), int(str_lists[j][3])
        )

# 1 suit, 3 equations
subset_1suit_3eq_probs = {
    'long_short_short': [0 for j in range(14)],
    'long_long_short': [0 for j in range(14)]
}

for short_long_mix in ('long_short_short', 'long_long_short'):
    # I happened to run the non-'alt' version for all cases
    # If you are running this code, feel free to try both alt and non-alt
    # versions.
    in_path = Path(f'./results/single_3eq_{short_long_mix}.txt')
    with open(in_path, 'r+') as reader:
        lines = reader.readlines()
    if lines[0] != 'single\n' or lines[1] != short_long_mix + '\n':
        raise ValueError('Read-in file has wrong header!')
    lines = lines[2:]
    str_lists = []
    for line in lines:
        str_lists.append(line.replace('\n', '').split(', '))
    for j in range(14):
        subset_1suit_3eq_probs[short_long_mix][j] = Rational(
            int(str_lists[j][2]), int(str_lists[j][3])
        )

# now we may continue with the main loop
# if 0-13 cards, obviously impossible.
results = [(j, 0, 1, Rational(0, 1), '0.00000%') for j in range(14)]
for selection_size in range(14, 53):
    cond_probs_given_suit_counts = [
        [
            [[0 for d in range(14)] for h in range(14)]
            for c in range(14)
        ] for s in range(14)
    ]
    probs_of_suit_counts = [
        [
            [[0 for d in range(14)] for h in range(14)]
            for c in range(14)
        ] for s in range(14)
    ]
    total_probs = [
        [
            [[0 for d in range(14)] for h in range(14)]
            for c in range(14)
        ] for s in range(14)
    ]
    for s in range(14):
        cap_chd = min(13, selection_size-s)
        for c in range(cap_chd + 1):
            cap_hd = min(13, selection_size-s-c)
            for h in range(cap_hd + 1):
                d = selection_size - s - c - h
                if d <= 13 and d >= 0:
                    my_quartet = (s, c, h, d)
                    probs_of_suit_counts[s][c][h][d]\
                        = types_probs(my_quartet, selection_size)
                    running_max_prob = 0
                    # take maximum of all 1 suit solves 3 equations,
                    # 1 suit solves remaining equations
                    # and two suits each solving two equations
                    for permy in permutations(my_quartet, 2):
                        permy_max = max(
                            subset_1suit_3eq_probs['long_long_short'][permy[0]]
                            * subset_1suit_1eq_probs['short'][permy[1]],
                            subset_1suit_3eq_probs['long_short_short'][permy[0]]
                            * subset_1suit_1eq_probs['long'][permy[1]],
                            subset_1suit_2eq_probs['long_long'][permy[0]]
                            * subset_1suit_2eq_probs['short_short'][permy[1]],
                            subset_1suit_2eq_probs['short_long'][permy[0]]
                            * subset_1suit_2eq_probs['short_long'][permy[1]]
                        )
                        running_max_prob = max(running_max_prob, permy_max)
                    # maximum over all solutions of form:
                    # suit 1 handles two equation
                    # suits 2 & 3 handle one equation each
                    for permy in permutations(my_quartet, 3):
                        permy_max = max(
                            subset_1suit_2eq_probs['long_long'][permy[0]]
                            * subset_1suit_1eq_probs['short'][permy[1]]
                            * subset_1suit_1eq_probs['short'][permy[2]],
                            subset_1suit_2eq_probs['short_long'][permy[0]]
                            * subset_1suit_1eq_probs['long'][permy[1]]
                            * subset_1suit_1eq_probs['short'][permy[2]],
                            subset_1suit_2eq_probs['short_short'][permy[0]]
                            * subset_1suit_1eq_probs['long'][permy[1]]
                            * subset_1suit_1eq_probs['long'][permy[2]],
                        )
                        running_max_prob = max(running_max_prob, permy_max)
                    # maximum over all ways to split each suit to an equation
                    for permy in permutations(my_quartet, 4):
                        permy_prob = subset_1suit_1eq_probs['long'][permy[0]]\
                                     * subset_1suit_1eq_probs['long'][permy[1]]\
                                     * subset_1suit_1eq_probs['short'][permy[2]]\
                                     * subset_1suit_1eq_probs['short'][permy[3]]
                        running_max_prob = max(running_max_prob, permy_prob)
                    cond_probs_given_suit_counts[s][c][h][d] = running_max_prob
                    total_probs[s][c][h][d] = probs_of_suit_counts[s][c][h][d]\
                        * cond_probs_given_suit_counts[s][c][h][d]

    running_total_prob = 0
    for s in range(14):
        for c in range(14):
            for h in range(14):
                for d in range(14):
                    running_total_prob += total_probs[s][c][h][d]
    prob_as_float_percent = running_total_prob.p/running_total_prob.q*100
    results.append((
        selection_size,
        running_total_prob.p,
        running_total_prob.q,
        running_total_prob,
        f'{prob_as_float_percent:.5f}%'
    ))

out_path = Path('./results/probabilities_single_suit.txt')
out_path.touch()
with open(out_path, 'w') as results_printer:
    print('Results for solving each equation single suit'
          + ' lower bounds on probabilities',
          file=results_printer)
    for result in results:
        print(f'{result[0]}, {result[1]}, {result[2]}, ' + result[4],
              file=results_printer)
