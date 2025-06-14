"""Take a file coming from my results and pretty-print in LaTeX"""
from sympy import Rational
from pathlib import Path


def local_file_printer(filename_in):
    in_path = Path(filename_in)
    with open(in_path, 'r+') as reader:
        lines = reader.readlines()
    deck_type = lines[0].replace('\n', '')
    equation_mix = lines[1].replace('\n', '').replace('_', '-')
    lines = lines[2:]
    str_lists = []
    for line in lines:
        str_lists.append(line.replace('\n', '').split(', '))
    out_path = Path(f'./results/{deck_type}_{equation_mix}_latex.tex')
    out_path.touch()
    with open(out_path, 'w') as writer:
        print(deck_type, file=writer)
        print(equation_mix, file=writer)
        print('\\[', file=writer)
        print('\\begin{array}{c | c}', file=writer)
        print('|T| & P (equation mix) \\\\\\hline', file=writer)
        for out_str in str_lists:
            my_num = Rational(int(out_str[2])/int(out_str[3]))
            my_pct_float = my_num.p/my_num.q*100
            print_str = f'{out_str[0]} & \\frac{{{out_str[2]}}}'\
                + f'{{{out_str[3]}}} = {my_pct_float:.5f}\\%\\\\'
            print(print_str, file=writer)
        print('\\end{array}', file=writer)
        print('\\]', file=writer)


def print_multiple_results(deck_type, deck_count, filenames_list):
    num_files = len(filenames_list)
    results_megalist = [[] for j in range(num_files)]
    equation_mixes = []
    for index, filename_in in enumerate(filenames_list):
        in_path = Path(filename_in)
        with open(in_path, 'r+') as reader:
            lines = reader.readlines()
        if deck_type != lines[0].replace('\n', ''):
            raise ValueError("Incorrect deck type!")
        equation_mixes.append(lines[1].replace('\n', '').replace('_', '-'))
        lines = lines[2:]
        str_lists = []
        for line in lines:
            str_lists.append(line.replace('\n', '').split(', '))
        results_megalist[index] = str_lists

    out_path = Path(f'./results/{deck_type}_all_results_latex.tex')
    out_path.touch()
    with open(out_path, 'w') as writer:
        print(deck_type, file=writer)
        print('\\[', file=writer)
        print('\\begin{array}{c' + ''.join(['| c' for j in range(num_files)])
              + '}', file=writer)
        print('|T|' + ''.join([f' & P(\\text{{{eq_set}}})'
                               for eq_set in equation_mixes])
              + ' \\\\\\hline', file=writer)
        for k in range(deck_count + 1):
            print_str = f'{k}'
            for j in range(num_files):
                my_str_list = results_megalist[j][k]
                my_num = Rational(int(my_str_list[2])/int(my_str_list[3]))
                my_pct_float = my_num.p/my_num.q*100
                if my_num == 0 or my_num == 1:
                    print_str += f' & {my_num}'
                else:
                    print_str += f' & \\frac{{{my_str_list[2]}}}'\
                        + f'{{{my_str_list[3]}}} = {my_pct_float:.5f}\\%'
            print_str += '\\\\'
            print(print_str, file=writer)
        print('\\end{array}', file=writer)
        print('\\]', file=writer)
