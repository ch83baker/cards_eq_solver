from my_subset_graph_again import encode_seq_to_str, encode_seq_as_bin_tuple, \
    encode_bin_tuple_as_str, encode_str_to_int, decode_int_to_str, \
    decode_str_to_seq, decode_str_to_bin_tuple, decode_bin_tuple_as_seq
from itertools import combinations

test_items_one = ('a', 'b', 'c', 'd', 'e')
num_items_one = 5
test_sample_one_one = ('a', 'c')
test_sample_one_two = ('b', 'c', 'd')


def test_seq_to_str_compatability():
    for j in range(0, 6):
        for combo in combinations(test_items_one, j):
            str_form_a = encode_seq_to_str(combo, test_items_one)
            str_form_b = encode_bin_tuple_as_str(
                encode_seq_as_bin_tuple(combo, test_items_one),
                num_items_one)
            if str_form_a != str_form_b:
                print("Trouble!")
                print(f"One-step: {str_form_a}")
                print(f"Two-step: {str_form_b}")
                return False
    return True


def test_seq_to_str_reversibility():
    for j in range(0, 6):
        for combo in combinations(test_items_one, j):
            str_form_a = encode_seq_to_str(combo, test_items_one)
            combo_reproduce = decode_str_to_seq(
                str_form_a, test_items_one
            )
            # unsure about types
            for k in range(j):
                if combo[k] != combo_reproduce[k]:
                    print("Trouble!")
                    print(f"Original: {combo}")
                    print(f'Result: {combo_reproduce}')
                    return False
    return True


def test_str_to_int_reversibility():
    for j in range(2**num_items_one):
        result = encode_str_to_int(
            decode_int_to_str(j, num_items_one), num_items_one)
        if result != j:
            print("Trouble!")
            print(f"Original: {j}, Result: {result}")
            return False
    return True


def test_str_to_seq_compatibility():
    for j in range(2**num_items_one):
        my_str = decode_int_to_str(j, num_items_one)
        my_direct = decode_str_to_seq(my_str, test_items_one)
        my_indirect = decode_bin_tuple_as_seq(
            decode_str_to_bin_tuple(my_str, num_items_one),
            test_items_one
        )
        if my_direct != my_indirect:
            print("Trouble!")
            print(f"One-step: {my_direct}")
            print(f"Two-step: {my_indirect}")
            return False
    return True


if __name__ == '__main__':
    print("Testing seq-to-str compatibility:")
    print(test_seq_to_str_compatability())
    print("Testing seq_to_str reversibility:")
    print(test_seq_to_str_reversibility())
    print("Testing int to str reversibility:")
    print(test_str_to_int_reversibility())
    print("Testing str-to-seq compatibility:")
    print(test_str_to_int_reversibility())
