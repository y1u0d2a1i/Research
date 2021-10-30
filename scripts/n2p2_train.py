import copy

from n2p2 import n2p2_training

obj = n2p2_training.n2p2TrainingFlow('/home/y1u0d2/Program/n2p2/two-body')

pair_min = 3
pair_max = 20

r_cut_min = 5
r_cut_max = 15

r_cut = r_cut_min
num_pairs = pair_min

while r_cut <= r_cut_max:
    while num_pairs <= pair_max:
        cp_obj = copy.copy(obj)
        cp_obj.set_up(f'nnp-train_{r_cut}_{num_pairs}')
        cp_obj.set_up_sf(r_cut, num_pairs, f'nnp-train_{r_cut}_{num_pairs}')
        cp_obj.run_n2p2()
        num_pairs += num_pairs
    r_cut += r_cut




