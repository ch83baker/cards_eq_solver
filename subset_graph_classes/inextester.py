from itertools import combinations
from sympy.functions.combinatorial.numbers import nC

default_terms = [j for j in range(10)]
default_subsets = [
    (0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 2, 5),
    (0, 3, 4), (0, 3, 5), (0, 4, 6), (0, 4, 7),
    (0, 5, 6), (0, 5, 7), (0, 6, 8), (0, 6, 9),
    (0, 7, 8), (0, 7, 9), (1, 2, 4), (1, 2, 5),
    (1, 3, 4), (1, 3, 5), (1, 4, 6), (1, 4, 7),
    (1, 5, 6), (1, 5, 7), (1, 6, 8), (1, 6, 9),
    (1, 7, 8), (1, 7, 9), (2, 3, 6), (2, 3, 7),
    (2, 4, 8), (2, 4, 9), (2, 5, 8), (2, 5, 9),
    (3, 4, 8), (3, 4, 9), (3, 5, 8), (3, 5, 9)
]


class OverlapsCounter():
    """Counts overlaps in acceptable sets.  Multisets not allowed."""

    def __init__(self, terms=default_terms, subsets_list=default_subsets):
        self.num_terms = len(terms)
        self.terms = set(terms)
        if len(self.terms) != self.num_terms:
            raise ValueError("Given set contains repeats!")
        # make sure first subset is good
        self.subset_size = len(subsets_list[0])
        test_set = set(subsets_list[0])
        if len(test_set) != self.subset_size:
            raise ValueError(f"Subset {self.subsets[0]} contains repeats.")
        self.subsets = []
        for subset in subsets_list:
            subset = set(subset)
            if len(subset) != self.subset_size:
                raise ValueError(
                    f"Subset {subset} contains repeats!"
                )
            if not subset <= self.terms:
                raise ValueError(
                    f"Subset {subset} is not in set:\n"
                    + f"{self.terms}"
                )
            self.subsets.append(subset)
        self.subsets = tuple(self.subsets)

    def count_overlap_size(self, small_size=1):
        if small_size < 1 or small_size > self.subset_size:
            raise ValueError(
                f"Invalid overlap size {small_size} detected.\n"
                + f"Maximum size is {self.subset_size}."
            )
        overlap_counts = []
        for subsubset in combinations(self.terms, small_size):
            subsubset_as_set = set(subsubset)
            count = 0
            for subset in self.subsets:
                if subsubset_as_set <= subset:
                    count += 1
            # if m uses of a subsubset, m-choose-two pairs
            overlap_counts.append((subsubset, count, nC(count, 2)))
        total_count = 0
        for pair in overlap_counts:
            total_count += pair[2]
        return (total_count, overlap_counts)
