# cards_eq_solver

Tools to give partial solutions to JDH's problem on Math.SE, "Is this math game always winnable?"

## What is this?

This code was written in an attempt to give a partial solution to the Math.Stack Exchange question, 
[Question 4023506](https://math.stackexchange.com/questions/4023546/is-this-math-game-always-winnable).
The code gives various tools to use various sub-decks to solve 1, 2, or (to a very limited extent) 3 of the equations,
as well as some general code for solving 1-2 equations more generally.  


## Requirements:

All the code is in Python 3, and makes heavy use of the Symbolic Python (`sympy`) package.  Currently, there is no
executable file for those who do not have a current Python installation.  

Note that a lot of the tools use a lot of time and/or space on a year-old, 32 GB RAM computer;
we make no guarantees of ability to run the more complicated routines on old systems with any reasonable amount
of resources, especially the ones whose results we have not advertised.  Moreover, given our simplistic multiprocessing setup,
if you split your work across several cores, it is more-or-less impossible to get progress updates in the current setup.

## How to install:

Download from GitHub as normal, then from the relevant folder (and in a virtual environment),
run the usual local-installation code,

    python -m pip install -e folder/

or 

    python -m pip install -e .

(replacing 'python' with 'py' on Windows systems as appropriate).  
You should also be able to run individual scripts from a command-line or interactive interface in the usual way.

## Brief notes on strategy:

The Python `sympy` package (in particular, the `symbols` and `Eq` constructors) make it easy to set up the equations, and the
`itertools` package makes it easy to loop through permutations and combinations of the sets of acceptable values.
That said, `sympy` can be slow.  Hence, we divided the task into three parts:

1.  Find the basic solutions using the symbolic methods.
2.  Find supersets of solving sets in one of two ways:
    - For each superset, query the satisfactory subsets, saying, "Are you my subset?" repeatedly.
    Reasonably quick, but variable speed depending on the size and quantity of solutions.
    - Model the subgraph of subsets of the existing set (with edges governed by inclusion between sets of neighboring sizes).
    More stable speed, but a huge space-drain.
3.  Estimate the probabilities we wanted, again using symbolic methods for exact arithmetic.

## What you get:

* Solvers for solving 1 or 2 arbitrary equations with symbolic inputs from any (multi)set of inputs, `SingleEqChecker` (in `SingleEq.py`) and `DoubleEqChecker` (in `DoubleEq.py`).
(The generalization is clear to code, but if there are at least 20 elements in a set,
it would take a great deal of time to finish.)

* Some general classes for creating (various slices of) the graph of subsets of a given set (where edges are given by inclusion), and
propogating up various upward-closed properties of said subsets, given an initial list of satisfactory subsets.  (Used here because supersets of a solution set are solution sets.)  See `my_subset_graph_new_py` and `my_subset_graph_again.py`.
**Warning:** A 26-element set's full graph of subsets made a 32 GB RAM system choke, and even the trimmed version (one cardinality
size at a time) takes 14-20 GB of RAM plus an unknown amount of virtual memory.  This enables some speedup on the problems, but at the
cost of a lot of space.  Once the basic solutions are determined, it may well be superior to switch to C++ or somesuch for this part
of the problem.

* Some multiprocessing hacks to speed up the special cases helpful for the problem at hand, with a limited amount of configuration
options available at the beginning of each script.  Cannot be run in interactive mode, and requires a multi-core CPU to actually
access multiprocessing.  See: `single_eq_multiprocess_starter.py` and `single_eq_multiprocess_finisher.py`, and the analogues for `double` and `triple`.  (See also `double_eq_finisher_alt.py` for the alternative strategy of modeling subgraphs.)
**Advice on the current limits of computation:**
    * For single-equation problems, using one or two suits (13-26 cards) is no issue.  For three suits (39 cards) and a small `a + b = c` problem,
    the basic solutions are not too hard, but this had to be done *without* multiprocessing, as my simplistic approach has too much overhead.  Hence, it took 1-2 days on a single core to get only out to 10-element subsets.
    * For double-equation problems, using one suit is easy, and two suits is just about at the edge of acceptable computation time
    outside a supercomputer, taking about a week to handle all cases.
    * For three-equation problems, single-suit solutions took just under an hour, but by scaling the problem size, two-suit solutions would take weeks to months with the current setup.

* Some quick scripts to add together all the probabilities in the lower-bounding technique I use in my answer.  Again using sympy.  See `single_suits_bounds.py`, `two_suits_basic_bounds.py`, and to a lesser extent `two_suits_bounds.py`.  

* In addition to the `results` folder for your results, a `sample_results` folder to store my results, for comparison.  Only .csv and .txt files are used.  

## Questions?

Please contact me at @ch83baker with any questions.