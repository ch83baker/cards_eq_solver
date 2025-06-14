"""Give a (multi)subset graph and search for upward-closed properties."""
num_terms = 5
enum_list = tuple([j for j in range(5)])
items_list = ('a', 'b', 'c', 'd', 'e')
dup_items_list = ('a', 'b', 'c', 'a', 'b')


def encode_bin_list_to_int(my_tuple):
    if len(my_tuple) != num_terms:
        raise ValueError(f"Not a {num_terms}-length tuple!")
    sum = 0
    for j in range(num_terms):
        if my_tuple[j]:
            sum += 2**j
    return sum


def decode_int_to_bin_list(code_int):
    if code_int < 0 or code_int >= 2**num_terms:
        raise ValueError("Outside range.")
    output_list = []
    for j in range(num_terms):
        output_list.append(code_int % 2)
        code_int = code_int // 2
    return tuple(output_list)


def encode_list_as_bin_list(short_list):
    output = [0 for j in range(num_terms)]
    for j in short_list:
        for pair in enumerate(items_list):
            if pair[1] == j:
                output[pair[0]] = 1
    return tuple(output)


def decode_bin_list_as_list(long_list):
    if len(long_list) != num_terms:
        raise ValueError("Not the right length of list.")
    output = []
    for pair in enumerate(long_list):
        if pair[1]:
            output.append(items_list[pair[0]])
    return tuple(output)
