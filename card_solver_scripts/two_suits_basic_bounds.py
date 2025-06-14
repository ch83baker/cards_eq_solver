'''Calculate the lower-bound probabilities for the groupings of terms.'''
from sympy import Rational
from sympy.functions.combinatorial.numbers import nC
from pathlib import Path


# first, find the probability of choosing j cards from one two-suit collection
# and (18-j) cards from the opposite two-suit collection

type_probs = [Rational(nC(26, j) * nC(26, 18-j),
                       nC(52, 18)) for j in range(19)]

# sanity check
if sum(type_probs) != 1:
    raise ValueError('Sum of probabilities of suits must equal 1!')

# now upload the given subset probabilities for the two-deck type.
grouping = 'opp'
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


# For each choice of j elts in suit-pair A and (18-j) elts in suit-pair B,
# there are three easy ways to get a solution:
# 1.  Each collection gets assigned a short-long pair.
# 2.  Collection A handles both short equations; Collection B, both long eqns.
# 3.  Collection B handles both short eqns; Collection A, both long eqns.
# These cases are not quite disjoint (a full suit can handle 3/4 equations),
# so I just take the maximum probabilities.

calc_type = 'compact'
if calc_type == 'compact':
    cond_probs = []
    for j in range(19):
        cond_probs.append(max((
            subset_2eq_probs['long_short'][j]
            * subset_2eq_probs['long_short'][18-j],
            subset_2eq_probs['short_short'][j]
            * subset_2eq_probs['long_long'][18-j],
            subset_2eq_probs['long_long'][j]
            * subset_2eq_probs['short_short'][18-j]
        )))
elif calc_type == 'verbose':
    # extra debug printing
    cond_probs_one = [subset_2eq_probs['long_short'][j]
                      * subset_2eq_probs['long_short'][18-j]
                      for j in range(19)]
    cond_probs_two = [subset_2eq_probs['short_short'][j]
                      * subset_2eq_probs['long_long'][18-j]
                      for j in range(19)]
    cond_probs_three = cond_probs_two[::-1]

    print('Type One Probabilities')
    for j in range(19):
        print((j, cond_probs_one[j]))

    print('Type Two Probabilities')
    for j in range(19):
        print((j, cond_probs_two[j]))

    cond_probs = [0 for j in range(19)]
    for j in range(19):
        cond_probs[j] = max(
            cond_probs_one[j], cond_probs_two[j],
            cond_probs_three[j]
        )
else:
    raise ValueError('Bad calculation type!')

probs_list = [type_probs[j] * cond_probs[j] for j in range(19)]

prob_est = sum(probs_list)

print(prob_est)

# for a Rational object, the numerator is attribute p
# and the denominator is attribute q
# moreover, these are returned as Python ints,
# so the ratio is a float, not a sympy.Rational object
prob_est_as_float_percent = prob_est.p/prob_est.q*100

print(f'As percentage: {prob_est_as_float_percent:.3f}%')
