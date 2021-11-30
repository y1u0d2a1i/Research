import copy

from n2p2.n2p2_training import n2p2TrainingFlow

# [r_cut, num_pairs]
params = [
    [5, 3],
    [5, 6],
    [5, 9],
    [5, 5],
    [5, 10],
    [5, 15],
    [10, 5],
    [10, 10],
    [10, 15],
    [15, 5],
    [15, 10],
    [15, 15],
]
obj = n2p2TrainingFlow('/home/y1u0d2/Program/n2p2/two-body')
for param in params:
    r_cut = param[0]
    num_pairs = param[1]
    cp_obj = copy.copy(obj)
    cp_obj.set_up(f'nnp-train_{r_cut}_{num_pairs}')
    cp_obj.set_up_sf(r_cut, num_pairs, f'nnp-train_{r_cut}_{num_pairs}')
    cp_obj.run_n2p2(f'nnp-train_{r_cut}_{num_pairs}')




