'''Calculate the lower-bound probabilities for the groupings of terms.'''
from sympy import Rational
from sympy.functions.combinatorial.numbers import nC
from pathlib import Path

# now upload the given subset probabilities for the two-deck type.
grouping = 'like'
subset_2eq_probs = {
    'short_short': [0 for j in range(27)],
    'long_short': [0 for j in range(27)],
    'long_long': [0 for j in range(27)]
}

for short_long_mix in ('short_short', 'long_short', 'long_long'):
    # I happened to run the 'alt' version for all cases
    # If you are running this code, feel free to try both alt and non-alt
    # versions.
    in_path = Path(f'../results/{grouping}_2eq_{short_long_mix}_alt.txt')
    with open(in_path, 'r+') as reader:
        lines = reader.readlines()
    if lines[0] != grouping + '\n' or lines[1] != short_long_mix + '\n':
        raise ValueError('Read-in file has wrong header!')
    lines = lines[2:]
    str_lists = []
    for line in lines:
        str_lists.append(line.replace('\n', '').split(', '))
    for j in range(27):
        subset_2eq_probs[short_long_mix][j] = Rational(
            int(str_lists[j][2]), int(str_lists[j][3])
        )

results = [(j, 0, 1, Rational(0, 1), '0.00000%') for j in range(14)]
# herein, a = |cards in suit-pair A| and b = |cards in suit-pair B|
for selection_size in range(14, 53):
    cond_probs_given_suit_pair_counts = [
        [0 for b in range(27)] for a in range(27)
    ]
    probs_of_suit_pair_counts = [
        [0 for b in range(27)] for a in range(27)
    ]
    total_probs = [
        [0 for b in range(27)] for a in range(27)
    ]

    # For each choice of j elts in suit-pair A
    # and (selection_size-j) elts in suit-pair B,
    # there are three easy ways to get a solution:
    # 1.  Each collection gets assigned a short-long pair.
    # 2.  Collection A handles both short equations;
    #     Collection B, both long eqns.
    # 3.  Collection B handles both short eqns;
    #     Collection A, both long eqns.
    # These cases are not quite disjoint,
    # so I just take the maximum probabilities.
    for a in range(27):
        b = selection_size - a
        if b >= 0 and b <= 26:
            probs_of_suit_pair_counts[a][b] = Rational(
                nC(26, a) * nC(26, b), nC(52, selection_size)
            )
            cond_probs_given_suit_pair_counts[a][b] = max(
                subset_2eq_probs['long_short'][a]
                * subset_2eq_probs['long_short'][b],
                subset_2eq_probs['short_short'][a]
                * subset_2eq_probs['long_long'][b],
                subset_2eq_probs['long_long'][a]
                * subset_2eq_probs['short_short'][b]
            )
            total_probs[a][b] = probs_of_suit_pair_counts[a][b]\
                * cond_probs_given_suit_pair_counts[a][b]

    running_total_prob = 0
    for a in range(27):
        for b in range(27):
            running_total_prob += total_probs[a][b]
    prob_as_float_percent = running_total_prob.p/running_total_prob.q*100
    results.append((
        selection_size,
        running_total_prob.p,
        running_total_prob.q,
        running_total_prob,
        f'{prob_as_float_percent:.5f}%'
    ))

# print human-readable table
out_path = Path(f'../results/probabilities_two_suits_{grouping}_colors.txt')
out_path.touch()
with open(out_path, 'w') as results_printer:
    print(f'Two-{grouping}-suit'
          + ' lower bounds on probabilities',
          file=results_printer)
    for result in results:
        print(f'{result[0]}, {result[1]}, {result[2]}, ' + result[4],
              file=results_printer)
